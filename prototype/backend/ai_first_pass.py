"""Bounded, public-only discovery for productized preliminary UX audit candidates."""
from __future__ import annotations

import html
import ipaddress
import json
import os
import re
import socket
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urldefrag, urlparse, urlunparse
from urllib.request import Request, build_opener, HTTPRedirectHandler

from backend.audit_copilot import _extract_draft

MAX_PAGES = 12
MAX_HTML_BYTES = 750_000
BLOCKED_ROUTE_WORDS = ("login", "log-in", "signin", "sign-in", "signup", "sign-up", "register", "account", "profile", "password", "checkout", "cart", "payment", "pay", "transaction", "apply", "submit", "appointment")
PRODUCT_TYPES = {
    "government_civic": "Government / civic service", "ecommerce": "E-commerce", "saas_digital_product": "SaaS / digital product",
    "corporate_marketing": "Corporate / marketing website", "content_publisher": "Content / publisher", "custom": "Custom",
}
BUNDLES = {
    "full_website": ("Full website", 160), "selected_pages": ("Selected pages", 72),
    "general_health_check": ("General health check", 48), "contact_experience": ("Contact experience", 42),
}
REQUIRED_CANDIDATE_FIELDS = ("id", "pageUrl", "pageName", "journey", "checkpointId", "reviewState", "duplicateRisk", "title", "observation", "impact", "recommendation", "suggestedSeverity", "confidence", "reasons", "evidenceRefs", "evidenceGaps")


def safe_public_url(value: object) -> str:
    if not isinstance(value, str) or not value.strip(): raise ValueError("A public http(s) URL is required")
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password: raise ValueError("Only public http(s) URLs without credentials are allowed")
    host = parsed.hostname.lower().rstrip(".")
    if host == "localhost" or host.endswith(".localhost"): raise ValueError("Only public http(s) URLs are allowed")
    try:
        if not ipaddress.ip_address(host).is_global: raise ValueError("Only public http(s) URLs are allowed")
    except ValueError as error:
        if "Only public" in str(error): raise
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", "", parsed.query, ""))


def scope_request(data: dict, target_url: str) -> dict:
    product_type, bundle = data.get("productType"), data.get("bundle")
    if product_type not in PRODUCT_TYPES: raise ValueError("A valid product type is required before First Pass")
    if bundle not in BUNDLES: raise ValueError("A valid scope bundle is required before First Pass")
    selected = data.get("selectedPages", [])
    if isinstance(selected, str): selected = [line.strip() for line in selected.splitlines() if line.strip()]
    if not isinstance(selected, list) or not all(isinstance(item, str) for item in selected): raise ValueError("Selected pages must be a list of public URLs or paths")
    origin = urlparse(target_url).hostname
    resolved = []
    for item in selected:
        url = safe_public_url(urljoin(target_url, item))
        if urlparse(url).hostname != origin: raise ValueError("Selected pages must be on the same public origin as the website URL")
        if url not in resolved: resolved.append(url)
    if bundle == "selected_pages" and not resolved: raise ValueError("Selected pages requires one or more same-origin public pages")
    return {"productType": product_type, "productTypeLabel": PRODUCT_TYPES[product_type], "bundle": bundle, "bundleLabel": BUNDLES[bundle][0], "checkpointCount": BUNDLES[bundle][1], "selectedPages": resolved}


def _host_is_public(host: str) -> bool:
    try: addresses = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror: return False
    return bool(addresses) and all(ipaddress.ip_address(item[4][0]).is_global for item in addresses)


def _blocked_route(url: str) -> bool: return any(word in urlparse(url).path.lower() for word in BLOCKED_ROUTE_WORDS)
def _contact_route(url: str) -> bool: return any(word in urlparse(url).path.lower() for word in ("contact", "support", "help", "location", "branch", "privacy"))


class _PageParser(HTMLParser):
    def __init__(self): super().__init__(); self.title=""; self._in_title=False; self.text=[]; self.links=[]
    def handle_starttag(self, tag, attrs):
        attributes=dict(attrs); self._in_title = tag == "title" or self._in_title
        if tag == "a" and attributes.get("href"): self.links.append(attributes["href"])
    def handle_endtag(self, tag):
        if tag == "title": self._in_title=False
    def handle_data(self, data):
        if self._in_title: self.title += data
        self.text.append(data)


def _fetch_public_page(url: str) -> dict:
    parsed=urlparse(url)
    if not _host_is_public(parsed.hostname): raise ValueError("Host does not resolve only to public addresses")
    request=Request(url, headers={"User-Agent":"UXM-Audit-Preliminary-Discovery/1.0", "Accept":"text/html,application/xhtml+xml"}, method="GET")
    with build_opener(HTTPRedirectHandler()).open(request, timeout=20) as response:
        final_url=safe_public_url(response.geturl())
        if urlparse(final_url).hostname != parsed.hostname: raise ValueError("Redirect left the requested public origin")
        if response.headers.get_content_type() not in {"text/html", "application/xhtml+xml"}: raise ValueError("Page is not HTML")
        body=response.read(MAX_HTML_BYTES+1)
        if len(body)>MAX_HTML_BYTES: raise ValueError("Page exceeds the safe discovery size limit")
        charset=response.headers.get_content_charset() or "utf-8"
    parser=_PageParser(); parser.feed(body.decode(charset, errors="replace"))
    return {"url":final_url, "title":re.sub(r"\s+"," ",parser.title).strip()[:200] or urlparse(final_url).path or "Untitled page", "textExcerpt":re.sub(r"\s+"," ",html.unescape(" ".join(parser.text))).strip()[:2500], "links":parser.links, "capturedAt":datetime.now(timezone.utc).isoformat(), "capture":{"kind":"text","url":final_url}}


def _scope_exclusions(bundle: str) -> list[str]:
    shared=["Public GET-only HTML review; no credentials, personal data, form submissions, transactions, or authentication.", "Login-only, account, payment, checkout, submission, and private flows are excluded / not verifiable."]
    if bundle == "general_health_check": return shared+["This is a homepage plus small public sample, not whole-site coverage; all other checkpoints are out of scope / not verified."]
    if bundle == "selected_pages": return shared+["Only the confirmed selected pages and named public journeys are in scope; all other pages are excluded / not verified."]
    if bundle == "contact_experience": return shared+["Only public contact, support, location, privacy, form clarity, and recovery entry points are in scope; no form is submitted."]
    return shared+["Sitemap/navigation discovery is bounded and template-grouped; inaccessible, blocked, and private areas are not verified."]


def explore_public_pages(start_url: str, request_scope: dict | None = None) -> dict:
    start_url=safe_public_url(start_url); request_scope=request_scope or {"bundle":"general_health_check", "selectedPages":[]}
    bundle=request_scope["bundle"]; origin=urlparse(start_url).hostname
    if bundle == "selected_pages": queue=list(request_scope["selectedPages"])
    else: queue=[start_url]
    seen=set(); visited=[]; skipped=[]
    limit = MAX_PAGES if bundle == "full_website" else (5 if bundle == "general_health_check" else 6)
    while queue and len(visited)<limit:
        current=queue.pop(0)
        if current in seen: continue
        seen.add(current)
        if _blocked_route(current): skipped.append({"url":current,"reason":"login, account, transaction, or submission route"}); continue
        if bundle == "contact_experience" and current != start_url and not _contact_route(current): skipped.append({"url":current,"reason":"outside contact/support bundle"}); continue
        try: page=_fetch_public_page(current)
        except (HTTPError,URLError,OSError,ValueError) as error: skipped.append({"url":current,"reason":f"not fetched safely: {error}"}); continue
        visited.append({key:page[key] for key in ("url","title","textExcerpt","capturedAt","capture")})
        if bundle != "selected_pages":
            for raw_link in page["links"]:
                next_url=urldefrag(urljoin(page["url"],raw_link)).url
                try: next_url=safe_public_url(next_url)
                except ValueError: skipped.append({"url":raw_link,"reason":"not a public http(s) link"}); continue
                if urlparse(next_url).hostname != origin: skipped.append({"url":next_url,"reason":"outside requested origin"})
                elif _blocked_route(next_url): skipped.append({"url":next_url,"reason":"login, account, transaction, or submission route"})
                elif next_url not in seen and next_url not in queue: queue.append(next_url)
    if not visited: return {"status":"unavailable","message":"Could not safely fetch any public HTML pages; no AI candidates were generated."}
    return {"status":"ready","scope":{"requestedUrl":start_url,"visited":visited,"skipped":skipped}}


def finalize_scope(exploration: dict, request_scope: dict) -> dict:
    scope={**exploration}
    included = request_scope["selectedPages"] if request_scope["bundle"] == "selected_pages" else [page["url"] for page in scope.get("visited", [])]
    scope.update({key:request_scope[key] for key in ("productType","productTypeLabel","bundle","bundleLabel","checkpointCount")}, includedUrls=included, includedJourneys=["Public discovery and information understanding"] if request_scope["bundle"] != "contact_experience" else ["Contact and support discovery"], exclusions=_scope_exclusions(request_scope["bundle"]), candidateRule="Candidate findings only: no score, report, published finding, or persisted audit data changes until human review and approval.")
    return scope


def build_first_pass_context(audit: dict, scope: dict) -> dict:
    return {"auditId":audit.get("id"),"auditScope":audit.get("scope",""),"requestedUrl":scope.get("requestedUrl"),"pages":scope.get("visited",[]),"scopeContract":{key:scope.get(key) for key in ("productType","productTypeLabel","bundle","bundleLabel","includedUrls","includedJourneys","checkpointCount","exclusions","candidateRule")},"existingFindings":[{"id":item.get("id"),"title":item.get("title","")} for item in audit.get("findings",[])]}


def _valid_candidates(candidates: object, scope: dict) -> bool:
    visited={page.get("url") for page in scope.get("visited",[])}; allowed_prefixes=("NAV-","FORM-","A11Y-","CONV-","CONT-","SUP-")
    return isinstance(candidates,list) and all(isinstance(item,dict) and all(field in item for field in REQUIRED_CANDIDATE_FIELDS) and item.get("suggestedSeverity") in {"critical","high","medium","low"} and item.get("confidence") in {"high","medium","low"} and item.get("reviewState") == "Awaiting review" and isinstance(item.get("reasons"),list) and isinstance(item.get("evidenceRefs"),list) and isinstance(item.get("evidenceGaps"),list) and item.get("pageUrl") in visited and set(item["evidenceRefs"]).issubset(visited) and str(item.get("checkpointId","")).startswith(allowed_prefixes) for item in candidates)


def configured_first_pass_drafter(context: dict) -> dict:
    endpoint=os.getenv("UXM_AI_ENDPOINT","").strip(); api_key=os.getenv("UXM_AI_API_KEY","").strip(); model=os.getenv("UXM_AI_MODEL","").strip()
    if not endpoint or not model: return {"status":"unavailable","message":"AI connection unavailable. Configure UXM_AI_ENDPOINT and UXM_AI_MODEL; no candidates were generated."}
    instructions="Generate only preliminary evidence-linked UX candidates using supplied public captures and scope contract. Return JSON {candidates:[...]}. Every candidate needs id (AIFP-NNN), pageUrl, pageName, journey, applicable checkpointId, evidenceRefs, observation, impact, recommendation, suggestedSeverity, confidence, evidenceGaps, duplicateRisk, reasons, and reviewState exactly Awaiting review. Do not invent evidence, submit forms, authenticate, or claim private coverage. Use only applicable checkpoints and URLs in the scope contract."
    payload={"model":model,"messages":[{"role":"system","content":instructions},{"role":"user","content":json.dumps(context,ensure_ascii=False)}],"response_format":{"type":"json_object"},"max_tokens":2200}; headers={"Content-Type":"application/json"}
    if api_key: headers["Authorization"]=f"Bearer {api_key}"
    try:
        with __import__("urllib.request",fromlist=["urlopen"]).urlopen(Request(endpoint,data=json.dumps(payload).encode("utf-8"),headers=headers,method="POST"),timeout=90) as response: body=json.load(response)
    except (HTTPError,URLError,TimeoutError,json.JSONDecodeError,OSError) as error: return {"status":"unavailable","message":f"AI connection unavailable ({error}); no candidates were generated."}
    candidates=(_extract_draft(body if isinstance(body,dict) else {}) or {}).get("candidates")
    if not _valid_candidates(candidates,{"visited":context.get("pages",[])}): return {"status":"unavailable","message":"The configured provider did not return evidence-linked, in-scope candidates; no candidates were generated."}
    return {"status":"ready","candidates":candidates}
