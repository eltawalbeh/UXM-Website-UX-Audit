import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('.', import.meta.url));
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8' };

export function createStaticServer() {
  return createServer(async (request, response) => {
    const url = new URL(request.url, 'http://localhost');
    const relative = url.pathname === '/' ? 'index.html' : url.pathname.replace(/^\//, '');
    const path = normalize(join(root, relative));
    if (!path.startsWith(root)) { response.writeHead(403); response.end('Forbidden'); return; }
    try {
      const body = await readFile(path);
      response.writeHead(200, { 'Content-Type': types[extname(path)] ?? 'application/octet-stream' });
      response.end(body);
    } catch {
      response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }); response.end('Not found');
    }
  });
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT || 4173);
  createStaticServer().listen(port, '127.0.0.1', () => console.log(`UXM Audit prototype running at http://127.0.0.1:${port}`));
}
