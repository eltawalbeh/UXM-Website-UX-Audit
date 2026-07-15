# UXM Website Audit — Checkpoint Library v1

> Source base: `ExpertReviewCheckpoints.xls` (247 historical expert-review checks) + 25 UXM modern coverage checks.

## Library at a glance

- **272 total checkpoints:** 247 source-mapped checks and 25 UXM modern checks.
- Use **Core** by default; add **Conditional** checks only when their applicability rule is true; add **Specialist** checks only when scope requires deeper expertise.
- Audit states: `Pass`, `Partial`, `Issue`, `Not applicable`, `Not verified`.
- Scoring: Pass = 1, Partial = 0.5, Issue = 0. Not applicable and Not verified are excluded from the score denominator.
- A Critical or High finding is always shown in the roadmap regardless of numerical score.

## Applicability rules

| Rule | Apply when |
|---|---|
| `all_websites` | The experience or page is in audit scope. |
| `ecommerce` | The site includes product, payment, subscription, booking, delivery, or other financial commitment flows. |
| `search` | Site search is a meaningful discovery mechanism. |
| `account` | Sign-in, registration, session handling, password recovery, or account management exists. |
| `form` | The journey includes data entry, application, lead capture, checkout, or other form submission. |
| `complex_content` | The site has a sizable content catalogue, hierarchy, or filtering need. |
| `motion_media` | The experience uses animation, autoplaying media, carousels, or time limits. |
| `consent` | The site requests cookie, tracking, marketing, or comparable consent. |
| `multilingual` | The site publishes more than one language or locale. |
| `third_party_integration` | A scoped journey relies on an external payment, map, chat, video, calendar, booking, or identity service. |

## Section index

- **Homepage & First Impression** — 20 checks (14 core, 6 conditional, 0 specialist)
- **Task Completion & Conversion** — 44 checks (26 core, 16 conditional, 2 specialist)
- **Navigation & Information Architecture** — 30 checks (22 core, 8 conditional, 0 specialist)
- **Forms & Data Entry** — 25 checks (0 core, 25 conditional, 0 specialist)
- **Trust, Credibility & Transparency** — 14 checks (11 core, 3 conditional, 0 specialist)
- **Content & Microcopy** — 25 checks (22 core, 3 conditional, 0 specialist)
- **Interface & Visual Design** — 40 checks (34 core, 3 conditional, 3 specialist)
- **Search & Discovery** — 21 checks (0 core, 20 conditional, 1 specialist)
- **Feedback, Recovery & Error Tolerance** — 37 checks (23 core, 13 conditional, 1 specialist)
- **Accessibility** — 5 checks (4 core, 1 conditional, 0 specialist)
- **Mobile & Responsive** — 4 checks (3 core, 1 conditional, 0 specialist)
- **Performance & Perceived Performance** — 3 checks (2 core, 1 conditional, 0 specialist)
- **Privacy & Consent** — 2 checks (0 core, 2 conditional, 0 specialist)
- **Technical Reliability** — 2 checks (1 core, 1 conditional, 0 specialist)

## Checkpoints

### Homepage & First Impression

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `HP-01` | core | all_websites | The items on the home page are clearly focused on users’ key tasks (“featuritis” has been avoided) |
| `HP-02` | conditional | search, form | The home page contains a search input box |
| `HP-03` | conditional | ecommerce | Product categories are provided and clearly visible on the homepage |
| `HP-04` | core | all_websites | Useful content is presented on the home page or within one click of the home page |
| `HP-05` | core | all_websites | The home page shows good examples of real site content |
| `HP-06` | core | all_websites | Links on the home page begin with the most important keyword (e.g. "Sun holidays" not "Holidays in the sun") |
| `HP-07` | core | all_websites | There is a short list of items recently featured on the homepage, supplemented with a link to archival content |
| `HP-08` | conditional | form | Navigation areas on the home page are not over-formatted and users will not mistake them for adverts |
| `HP-09` | core | all_websites | The value proposition is clearly stated on the home page (e.g. with a tagline or welcome blurb) |
| `HP-10` | core | all_websites | The home page contains meaningful graphics, not clip art or pictures of models |
| `HP-11` | conditional | form | Navigation choices are ordered in the most logical or task-oriented manner (with the less important corporate information at the bottom) |
| `HP-12` | conditional | search | The title of the home page will provide good visibility in search engines like Google |
| `HP-13` | conditional | form | All corporate information is grouped in one distinct area (e.g. "About Us") |
| `HP-14` | core | all_websites | Users will understand the value proposition |
| `HP-15` | core | all_websites | By just looking at the home page, the first time user will understand where to start |
| `HP-16` | core | all_websites | The home page shows all the major options |
| `HP-17` | core | all_websites | The home page of the site has a memorable URL |
| `HP-18` | core | all_websites | The home page is professionally designed and will create a positive first impression |
| `HP-19` | core | all_websites | The design of the home page will encourage people to explore the site |
| `HP-20` | core | all_websites | The home page looks like a home page; pages lower in the site will not be confused with it |

### Task Completion & Conversion

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `TO-01` | conditional | form | The site is free from irrelevant, unnecessary and distracting information |
| `TO-02` | core | all_websites | Excessive use of scripts, applets, movies, audio files, graphics and images has been avoided |
| `TO-03` | conditional | account | The site avoids unnecessary registration |
| `TO-04` | conditional | ecommerce | The critical path (e.g. purchase, subscription) is clear, with no distractions on route |
| `TO-05` | conditional | form | Information is presented in a simple, natural and logical order |
| `TO-06` | core | all_websites | The number of screens required per task has been minimised |
| `TO-07` | core | all_websites | The site requires minimal scrolling and clicking |
| `TO-08` | core | all_websites | The site correctly anticipates and prompts for the user’s probable next activity |
| `TO-09` | core | all_websites | When graphs are shown, users have access to the actual data (e.g. numeric annotation on bar charts) |
| `TO-10` | core | all_websites | Activities allocated to the user or the computer take full advantage of the strengths of each (look for actions that can be done automatically by the site, e.g. postcode lookup) |
| `TO-11` | core | all_websites | Users can complete common tasks quickly |
| `TO-12` | conditional | ecommerce | Items can be compared easily when this is necessary for the task (e.g. product comparisons) |
| `TO-13` | core | all_websites | The task sequence parallels the user’s work processes |
| `TO-14` | core | all_websites | The site makes the user’s work easier and quicker than without the system |
| `TO-15` | core | all_websites | The most important and frequently used topics, features and functions are close to the centre of the page, not in the far left or right margins |
| `TO-16` | conditional | form | The user does not need to enter the same information more than once |
| `TO-17` | core | all_websites | Important, frequently needed topics and tasks are close to the 'surface' of the web site |
| `TO-18` | conditional | ecommerce | Typing (e.g. during purchase) is kept to an absolute minimum, with accelerators (“one-click”) for return users |
| `TO-19` | core | all_websites | The path for any given task is a reasonable length (2-5 clicks) |
| `TO-20` | core | all_websites | When there are multiple steps in a task, the site displays all the steps that need to be completed and provides feedback on the user’s current position in the workflow |
| `TO-21` | conditional | ecommerce | Price is always clearly displayed next to any product |
| `TO-22` | conditional | form | The site's privacy policy is easy to find, especially on pages that ask for personal information, and the policy is simple and clear |
| `TO-23` | conditional | form | Users of the site do not need to remember information from place to place |
| `TO-24` | core | all_websites | The use of metaphors is easily understandable by the typical user |
| `TO-25` | conditional | form | Data formats follow appropriate cultural conventions (e.g. miles for UK) |
| `TO-26` | core | all_websites | Details of the software's internal workings are not exposed to the user |
| `TO-27` | core | all_websites | The site caters for users with little prior experience of the web |
| `TO-28` | core | all_websites | The site makes it easy for users to explore the site and try out different options before committing themselves |
| `TO-29` | core | all_websites | A typical first-time visitor can do the most common tasks without assistance |
| `TO-30` | core | all_websites | When they return to the site, users will remember how to carry out the key tasks |
| `TO-31` | core | all_websites | The functionality of novel device controls is obvious |
| `TO-32` | conditional | ecommerce | On the basket page, there is a highly visible ‘Proceed to checkout’ button at the top and bottom of the page |
| `TO-33` | conditional | ecommerce | Important calls to action, like ‘Add to basket’, are highly visible |
| `TO-34` | conditional | form | Action buttons (such as “Submit”) are always invoked by the user, not automatically invoked by the system when the last field is completed |
| `TO-35` | core | all_websites | Command and action items are presented as buttons (not, for example, as hypertext links) |
| `TO-36` | core | all_websites | If the user is half-way through a transaction and quits, the user can later return to the site and continue from where he left off |
| `TO-37` | conditional | form, complex_content | When a page presents a lot of information, the user can sort and filter the information |
| `TO-38` | core | all_websites | If there is an image on a button or icon, it is relevant to the task |
| `TO-39` | conditional | account | The site prompts the user before automatically logging off the user, and the time out is appropriate |
| `TO-40` | core | all_websites | Unwanted features (e.g. Flash animations) can be stopped or skipped |
| `TO-41` | core | all_websites | The site is robust and all the key features work (i.e. there are no javascript exceptions, CGI errors or broken links) |
| `TO-42` | core | all_websites | The site supports novice and expert users by providing different levels of explanation (e.g. in help and error messages) |
| `TO-43` | specialist | ecommerce, account | The site allows users to rename objects and actions in the interface (e.g. naming delivery addresses or accounts) |
| `TO-44` | specialist | account | The site allows the user to customise operational time parameters (e.g. time until automatic logout) |

### Navigation & Information Architecture

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `NAV-01` | core | all_websites | There is a convenient and obvious way to move between related pages and sections and it is easy to return to the home page |
| `NAV-02` | conditional | form | The information that users are most likely to need is easy to navigate to from most pages |
| `NAV-03` | core | all_websites | Navigation choices are ordered in the most logical or task-oriented manner |
| `NAV-04` | core | all_websites | The navigation system is broad and shallow (many items on a menu) rather than deep (many menu levels) |
| `NAV-05` | core | all_websites | The site structure is simple, with a clear conceptual model and no unnecessary levels |
| `NAV-06` | core | all_websites | The major sections of the site are available from every page (persistent navigation) and there are no dead ends |
| `NAV-07` | core | all_websites | Navigation tabs are located at the top of the page, and look like clickable versions of real-world tabs |
| `NAV-08` | conditional | complex_content | There is a site map that provides an overview of the site's content |
| `NAV-09` | conditional | complex_content | The site map is linked to from every page |
| `NAV-10` | conditional | complex_content | The site map provides a concise overview of the site, not a rehash of the main navigation or a list of every single topic |
| `NAV-11` | core | all_websites | Good navigational feedback is provided (e.g. showing where you are in the site) |
| `NAV-12` | conditional | form | Category labels accurately describe the information in the category |
| `NAV-13` | core | all_websites | Links and navigation labels contain the "trigger words" that users will look for to achieve their goal |
| `NAV-14` | core | all_websites | Terminology and conventions (such as link colours) are (approximately) consistent with general web usage |
| `NAV-15` | core | all_websites | Links look the same in the different sections of the site |
| `NAV-16` | conditional | ecommerce | Product pages contain links to similar and complementary products to support cross-selling |
| `NAV-17` | core | all_websites | The terms used for navigation items and hypertext links are unambiguous and jargon-free |
| `NAV-18` | conditional | ecommerce, complex_content | Users can sort and filter catalogue pages (e.g. by listing in price order, or showing 'most popular') |
| `NAV-19` | core | all_websites | There is a visible change when the mouse points at something clickable (excluding cursor changes) |
| `NAV-20` | core | all_websites | Important content can be accessed from more than one link (different users may require different link labels) |
| `NAV-21` | core | all_websites | Navigation-only pages (such as the home page) can be viewed without scrolling |
| `NAV-22` | core | all_websites | Hypertext links that invoke actions (e.g downloads, new windows) are clearly distinguished from hypertext links that load another page |
| `NAV-23` | core | all_websites | The site allows the user to control the pace and sequence of the interaction |
| `NAV-24` | core | all_websites | There are clearly marked exits on every page allowing the user to bale out of the current task without having to go through an extended dialog |
| `NAV-25` | core | all_websites | The site does not disable the browser's “Back” button and the "Back" button appears on the browser toolbar on every page |
| `NAV-26` | core | all_websites | Clicking the back button always takes the user back to the page the user came from |
| `NAV-27` | conditional | ecommerce | A link to both the basket and checkout is clearly visible on every page |
| `NAV-28` | core | all_websites | If the site spawns new windows, these will not confuse the user (e.g. they are dialog-box sized and can be easily closed) |
| `NAV-29` | core | all_websites | Menu instructions, prompts and messages appear on the same place on each screen |
| `NAV-30` | core | all_websites | Users can recover from deep links, expired sessions, and unavailable pages without losing their task context |

### Forms & Data Entry

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `FORM-01` | conditional | form | Fields in data entry screens contain default values when appropriate and show the structure of the data and the field length |
| `FORM-02` | conditional | form | When a task involves source documents (such as a paper form), the interface is compatible with the characteristics of the source document |
| `FORM-03` | conditional | form | The site automatically enters field formatting data (e.g. currency symbols, commas for 1000s, trailing or leading spaces). Users do not need to enter characters like £ or %. |
| `FORM-04` | conditional | form | Field labels on forms clearly explain what entries are desired |
| `FORM-05` | conditional | form | Text boxes on forms are the right length for the expected answer |
| `FORM-06` | conditional | form | There is a clear distinction between “required” and “optional” fields on forms |
| `FORM-07` | conditional | account, form | The same form is used for both logging in and registering (i.e. it's like Amazon) |
| `FORM-08` | conditional | form | Forms pre-warn the user if external information is needed for completion (e.g. a passport number) |
| `FORM-09` | conditional | form | Questions on forms are grouped logically, and each group has a heading |
| `FORM-10` | conditional | form | Fields on forms contain hints, examples or model answers to demonstrate the expected input |
| `FORM-11` | conditional | form | When field labels on forms take the form of questions, the questions are stated in clear, simple language |
| `FORM-12` | conditional | form | Pull-down menus, radio buttons and check boxes are used in preference to text entry fields on forms (i.e. text entry fields are not overused) |
| `FORM-13` | conditional | form | With data entry screens, the cursor is placed where the input is needed |
| `FORM-14` | conditional | form | Data formats are clearly indicated for input (e.g. dates) and output (e.g. units of values). |
| `FORM-15` | conditional | form | Users can complete simple tasks by entering just essential information (with the system supplying the non-essential information by default) |
| `FORM-16` | conditional | form | Forms allow users to stay with a single interaction method for as long as possible (i.e. users do not need to make numerous shifts from keyboard to mouse to keyboard). |
| `FORM-17` | conditional | form | The user can change default values in form fields |
| `FORM-18` | conditional | form | Text entry fields indicate the amount and the format of data that needs to be entered |
| `FORM-19` | conditional | form | Forms are validated before the form is submitted |
| `FORM-20` | conditional | form | With data entry screens, the site carries out field-level checking and form-level checking at the appropriate time |
| `FORM-21` | conditional | form | The site makes it easy to correct errors (e.g. when a form is incomplete, positioning the cursor at the location where correction is required) |
| `FORM-22` | conditional | form | There is consistency between data entry and data display |
| `FORM-23` | conditional | form | Labels are close to the data entry fields (e.g. labels are right justified) |
| `FORM-24` | conditional | form | Form errors are announced, explained beside the relevant field, and do not remove valid entered data |
| `FORM-25` | conditional | account | Authentication and account recovery provide clear, safe paths for first-time and returning users |

### Trust, Credibility & Transparency

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `TRUST-01` | core | all_websites | The content is up-to-date, authoritative and trustworthy |
| `TRUST-02` | conditional | form | The site contains third-party support (e.g. citations, testimonials) to verify the accuracy of information. |
| `TRUST-03` | core | all_websites | It is clear that there is a real organisation behind the site (e.g. there is a physical address or a photo of the office) |
| `TRUST-04` | core | all_websites | The company comprises acknowledged experts (look for credentials) |
| `TRUST-05` | core | all_websites | The site avoids advertisements, especially pop-ups. |
| `TRUST-06` | conditional | ecommerce | Delivery costs are highlighted at the very beginning of checkout |
| `TRUST-07` | core | all_websites | The site avoids marketing waffle |
| `TRUST-08` | core | all_websites | Each page is clearly branded so that the user knows he is still in the same site |
| `TRUST-09` | core | all_websites | It is easy to contact someone for assistance and a reply is received quickly |
| `TRUST-10` | core | all_websites | The content is fresh: it is updated frequently and the site includes recent content |
| `TRUST-11` | core | all_websites | The site is free of typographic errors and spelling mistakes |
| `TRUST-12` | core | all_websites | The visual design complements the brand and any offline marketing messages |
| `TRUST-13` | core | all_websites | There are real people behind the organisation and they are honest and trustworthy (look for bios) |
| `TRUST-14` | conditional | ecommerce | Prices, fees, taxes, delivery terms, renewal terms, and commitments are disclosed before commitment |

### Content & Microcopy

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `CONTENT-01` | core | all_websites | The site has compelling and unique content |
| `CONTENT-02` | core | all_websites | Text is concise, with no needless instructions or welcome notes |
| `CONTENT-03` | core | all_websites | Each content page begins with conclsuions or implications and the text is written with an inverted pyramid style |
| `CONTENT-04` | core | all_websites | Pages use bulleted and numbered lists in preference to narrative text |
| `CONTENT-05` | core | all_websites | Lists are prefaced with a concise introduction (e.g. a word or phrase), helping users appreciate how the items are related to one another |
| `CONTENT-06` | core | all_websites | The most important items in a list are placed at the top |
| `CONTENT-07` | conditional | form | Information is organised hierarchically, from the general to the specific, and the organisation is clear and logical |
| `CONTENT-08` | core | all_websites | Content has been specifically created for the web (web pages do not comprise repurposed material from print publications such as brochures) |
| `CONTENT-09` | conditional | ecommerce | Product pages contain the detail necessary to make a purchase, and users can zoom in on product images |
| `CONTENT-10` | core | all_websites | Hypertext has been appropriately used to structure content |
| `CONTENT-11` | core | all_websites | Sentences are written in the active voice |
| `CONTENT-12` | core | all_websites | Pages are quick to scan, with ample headings and sub-headings and short paragraphs |
| `CONTENT-13` | core | all_websites | The site uses maps, diagrams, graphs, flow charts and other visuals in preference to wordy blocks of text |
| `CONTENT-14` | core | all_websites | Each page is clearly labelled with a descriptive and useful title that makes sense as a bookmark |
| `CONTENT-15` | core | all_websites | Links and link titles are descriptive and predictive, and there are no “Click here!” links |
| `CONTENT-16` | core | all_websites | The site avoids cute, clever, or cryptic headings |
| `CONTENT-17` | core | all_websites | Link names match the title of destination pages, so users will know when they have reached the intended page |
| `CONTENT-18` | core | all_websites | Button labels and link labels start with action words |
| `CONTENT-19` | core | all_websites | Headings and sub-headings are short, straightforward and descriptive |
| `CONTENT-20` | core | all_websites | The words, phrases and concepts used will be familiar to the typical user |
| `CONTENT-21` | core | all_websites | Numbered lists start at "1" not at "0" |
| `CONTENT-22` | core | all_websites | Acronyms and abbreviations are defined when first used |
| `CONTENT-23` | core | all_websites | Text links are long enough to be understood, but short enough to minimise wrapping (especially when used as a navigation list) |
| `CONTENT-24` | core | all_websites | Content identifies the audience, outcome, and next step before supporting detail |
| `CONTENT-25` | conditional | multilingual | Arabic and English content, where both are offered, are equally complete and contextually appropriate |

### Interface & Visual Design

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `VIS-01` | core | all_websites | The screen density is appropriate for the target users and their tasks |
| `VIS-02` | core | all_websites | The layout helps focus attention on what to do next |
| `VIS-03` | conditional | form | On all pages, the most important information (such as frequently used topics, features and functions) is presented on the first screenful of information (“above the fold”) |
| `VIS-04` | core | all_websites | The site can be used without scrolling horizontally |
| `VIS-05` | core | all_websites | Things that are clickable (like buttons) are obviously pressable |
| `VIS-06` | core | all_websites | Items that aren't clickable do not have characteristics that suggest that they are |
| `VIS-07` | core | all_websites | The functionality of buttons and controls is obvious from their labels or from their design |
| `VIS-08` | core | all_websites | Clickable images include redundant text labels (i.e. there is no 'mystery meat' navigation) |
| `VIS-09` | core | all_websites | Hypertext links are easy to identify without needing to 'minesweep' (e.g. underlined) |
| `VIS-10` | core | all_websites | Fonts are used consistently |
| `VIS-11` | core | all_websites | The relationship between controls and their actions is obvious |
| `VIS-12` | core | all_websites | Icons and graphics are standard and/or intuitive (concrete and familiar) |
| `VIS-13` | core | all_websites | There is a clear visual "starting point" to every page |
| `VIS-14` | core | all_websites | Each page on the site shares a consistent layout |
| `VIS-15` | specialist | form | Pages on the site are formatted for printing, or there is a printer-friendly version |
| `VIS-16` | core | all_websites | Buttons and links show that they have been clicked |
| `VIS-17` | core | all_websites | GUI components (like radio buttons and check boxes) are used appropriately |
| `VIS-18` | core | all_websites | Fonts are readable |
| `VIS-19` | core | all_websites | The site avoids italicised text and uses underlining only for hypertext links |
| `VIS-20` | conditional | form | There is a good balance between information density and use of white space |
| `VIS-21` | core | all_websites | The site is pleasant to look at |
| `VIS-22` | core | all_websites | Pages are free of "scroll stoppers" (headings or page elements that create the illusion that users have reached the top or bottom of a page when they have not) |
| `VIS-23` | core | all_websites | The site avoids extensive use of upper case text |
| `VIS-24` | core | all_websites | The site has a consistent, clearly recognisable look and feel that will engage users |
| `VIS-25` | specialist | all_websites | Saturated blue is avoided for fine detail (e.g. text, thin lines and symbols) |
| `VIS-26` | core | all_websites | Colour is used to structure and group items on the page |
| `VIS-27` | core | all_websites | Graphics will not be confused with banner ads |
| `VIS-28` | core | all_websites | Emboldening is used to emphasise important topic categories |
| `VIS-29` | core | all_websites | On content pages, line lengths are neither too short (<50 characters per line) nor too long (>100 characters per line) when viewed in a standard browser width window |
| `VIS-30` | core | all_websites | Pages have been designed to an underlying grid, with items and widgets aligned both horizontally and vertically |
| `VIS-31` | core | all_websites | Meaningful labels, effective background colours and appropriate use of borders and white space help users identify a set of items as a discrete functional block |
| `VIS-32` | core | all_websites | The colours work well together and complicated backgrounds are avoided |
| `VIS-33` | conditional | form | Individual pages are free of clutter and irrelevant information |
| `VIS-34` | core | all_websites | Standard elements (such as page titles, site navigation, page navigation, privacy policy etc.) are easy to locate |
| `VIS-35` | core | all_websites | The organisation's logo is placed in the same location on every page, and clicking the logo returns the user to the most logical page (e.g. the home page) |
| `VIS-36` | core | all_websites | Attention-attracting features (such as animation, bold colours and size differentials) are used sparingly and only where relevant |
| `VIS-37` | core | all_websites | Icons are visually and conceptually distinct yet still harmonious (clearly part of the same family) |
| `VIS-38` | specialist | form | Related information and functions are clustered together, and each group can be scanned in a single fixation (5-deg, about 4.4cm diam circle on screen) |
| `VIS-39` | core | all_websites | Interactive states are distinguishable across hover, focus, pressed, disabled, loading, and error states |
| `VIS-40` | core | all_websites | The design system maintains consistency across responsive templates and core journeys |

### Search & Discovery

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `SEARCH-01` | conditional | search | The default search is intuitive to configure (no Boolean operators) |
| `SEARCH-02` | conditional | search | The search results page shows the user what was searched for and it is easy to edit and resubmit the search |
| `SEARCH-03` | conditional | search | Search results are clear, useful and ranked by relevance |
| `SEARCH-04` | conditional | search | The search results page makes it clear how many results were retrieved, and the number of results per page can be configured by the user |
| `SEARCH-05` | conditional | search, form | If no results are returned, the system offers ideas or options for improving the query based on identifiable problems with the user's input |
| `SEARCH-06` | conditional | search | The search engine handles empty queries gracefully |
| `SEARCH-07` | conditional | search | The most common queries (as reflected in the site log) produce useful results |
| `SEARCH-08` | conditional | search | The search engine includes templates, examples or hints on how to use it effectively |
| `SEARCH-09` | conditional | search | The site includes a more powerful search interface available to help users refine their searches (preferably named "revise search" or "refine search", not "advanced search) |
| `SEARCH-10` | conditional | search | The search results page does not show duplicate results (either perceived duplicates or actual duplicates) |
| `SEARCH-11` | conditional | search | The search box is long enough to handle common query lengths |
| `SEARCH-12` | conditional | search | Searches cover the entire web site, not a portion of it |
| `SEARCH-13` | conditional | search | If the site allows users to set up a complex search, these searches can be saved and executed on a regular basis (so users can keep up-to-date with dynamic content) |
| `SEARCH-14` | conditional | search | The search interface is located where users will expect to find it (top right of page) |
| `SEARCH-15` | conditional | search | The search box and its controls are clearly labelled (multiple search boxes can be confusing) |
| `SEARCH-16` | conditional | search | The site supports people who want to browse and people who want to search |
| `SEARCH-17` | conditional | search | The scope of the search is made explicit on the search results page and users can restrict the scope (if relevant to the task) |
| `SEARCH-18` | conditional | search, form | The search results page displays useful meta-information, such as the size of the document, the date that the document was created and the file type (Word, pdf etc.) |
| `SEARCH-19` | conditional | search | The search engine provides automatic spell checking and looks for plurals and synonyms |
| `SEARCH-20` | specialist | search | The search engine provides an option for similarity search (“more like this”) |
| `SEARCH-21` | conditional | search | Search results support spelling tolerance, language variants, and intent-relevant empty states |

### Feedback, Recovery & Error Tolerance

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `HELP-01` | core | all_websites | The FAQ or on-line help provides step-by-step instructions to help users carry out the most important tasks |
| `HELP-02` | conditional | form | It is easy to get help in the right form and at the right time |
| `HELP-03` | core | all_websites | Prompts are brief and unambiguous |
| `HELP-04` | conditional | form | The user does not need to consult user manuals or other external information to use the site |
| `HELP-05` | conditional | search | The site uses a customised 404 page, which includes tips on how to find the missing page and links to “Home” and Search |
| `HELP-06` | conditional | ecommerce | The site provides good feedback (e.g. progress indicators or messages) when needed (e.g. during checkout) |
| `HELP-07` | conditional | ecommerce | Users are given help in choosing products |
| `HELP-08` | core | all_websites | User confirmation is required before carrying out potentially “dangerous” actions (e.g. deleting something) |
| `HELP-09` | core | all_websites | Confirmation pages are clear |
| `HELP-10` | core | all_websites | Error messages contain clear instructions on what to do next |
| `HELP-11` | conditional | ecommerce | Immediately prior to commiting to the purchase, the site shows the user a clear summary page and this will not be confused with a purchase confirmation page |
| `HELP-12` | core | all_websites | When the user needs to choose between different options (such as in a dialog box), the options are obvious |
| `HELP-13` | conditional | form | The site keeps users informed about unavoidable delays in the site’s response time (e.g. when authorising a credit card transaction) |
| `HELP-14` | core | all_websites | Error messages are written in a non-derisory tone and do not blame the user for the error |
| `HELP-15` | core | all_websites | Pages load quickly (5 seconds or less) |
| `HELP-16` | conditional | form | The site provides immediate feedback on user input or actions |
| `HELP-17` | conditional | form, complex_content | The user is warned about large, slow-loading pages (e.g. “Please wait…”), and the most important information appears first |
| `HELP-18` | conditional | form | Where tooltips are used, they provide useful additional help and do not simply duplicate text in the icon, link or field label |
| `HELP-19` | core | all_websites | When giving instructions, pages tell users what to do rather than what to avoid doing |
| `HELP-20` | core | all_websites | The site shows users how to do common tasks where appropriate (e.g. with demonstrations of the site's functionality) |
| `HELP-21` | core | all_websites | The site provides feedback (e.g. “Did you know?”) that helps the user learn how to use the site |
| `HELP-22` | core | all_websites | The site provides context sensitive help |
| `HELP-23` | core | all_websites | Help is clear and direct and simply expressed in plain English, free from jargon and buzzwords |
| `HELP-24` | core | all_websites | The site provides clear feedback when a task has been completed successfully |
| `HELP-25` | conditional | form | Important instructions remain on the screen while needed, and there are no hasty time outs requiring the user to write down information |
| `HELP-26` | specialist | all_websites | Fitts' Law is followed (the distance between controls and the size of the controls is appropriate, with size proportional to distance) |
| `HELP-27` | core | all_websites | There is sufficient space between targets to prevent the user from hitting multiple or incorrect targets |
| `HELP-28` | core | all_websites | There is a line space of at least 2 pixels between clickable items |
| `HELP-29` | conditional | form | The site makes it obvious when and where an error has occurred (e.g. when a form is incomplete, highlighting the missing fields) |
| `HELP-30` | core | all_websites | The site uses appropriate selection methods (e.g. pull-down menus) as an alternative to typing |
| `HELP-31` | core | all_websites | The site does a good job of preventing the user from making errors |
| `HELP-32` | conditional | form | The site prompts the user before correcting erroneous input (e.g. Google's “Did you mean…”) |
| `HELP-33` | core | all_websites | The site ensures that work is not lost (either by the user or site error) |
| `HELP-34` | core | all_websites | Error messages are written in plain language with sufficient explanation of the problem |
| `HELP-35` | core | all_websites | When relevant, the user can defer fixing errors until later in the task |
| `HELP-36` | core | all_websites | The site can provide more detail about error messages if required |
| `HELP-37` | core | all_websites | It is easy to “undo” (or “cancel”) and “redo” actions |

### Accessibility

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `A11Y-01` | core | all_websites | Text contrast meets WCAG AA on all core task states |
| `A11Y-02` | core | all_websites | Keyboard users can reach, operate, and visibly focus every core control |
| `A11Y-03` | core | all_websites | Semantic page structure and form labels support assistive technology |
| `A11Y-04` | core | all_websites | Core journeys remain usable at 200% zoom and narrow reflow widths |
| `A11Y-05` | conditional | motion_media | Motion, autoplaying media, and time-based behavior can be paused or reduced |

### Mobile & Responsive

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `MOB-01` | core | all_websites | The primary navigation is understandable and operable on small screens |
| `MOB-02` | core | all_websites | Primary calls to action remain visible and usable without accidental taps on mobile |
| `MOB-03` | core | all_websites | Content, media, and tables reflow without clipping or horizontal page scrolling |
| `MOB-04` | conditional | form | Mobile input types, autofill, and virtual keyboard behavior reduce input effort |

### Performance & Perceived Performance

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `PERF-01` | core | all_websites | Users receive an immediate visible response after a primary action |
| `PERF-02` | core | all_websites | Critical content and primary actions become usable before non-essential assets |
| `PERF-03` | conditional | form, account, ecommerce | Long-running tasks communicate progress and preserve user input |

### Privacy & Consent

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `PRIV-01` | conditional | consent | Consent choices are clear, equal in prominence, and reversible where relevant |
| `PRIV-02` | conditional | form, account | Privacy, data use, and retention explanations are contextual to the data requested |

### Technical Reliability

| ID | Level | Applies when | Checkpoint |
|---|---|---|---|
| `BUG-01` | core | all_websites | Core journeys complete without console errors, broken links, failed resources, or unexpected dead ends |
| `BUG-02` | conditional | third_party_integration | Third-party embeds and integrations communicate failure safely and provide a recovery path |

## Auditor rules

1. Do not assess a conditional checkpoint until you have confirmed it is applicable to the scoped website or journey.
2. Create a client-facing finding for every material Issue. If an Issue remains internal-only, record why.
3. Every published finding needs evidence, an impact statement, a direct recommendation, and at least one linked checkpoint unless it is a documented specialist finding.
4. Preserve `sourceMapping` when editing or splitting a source-derived checkpoint; it protects traceability to the original workbook.
5. Treat the library as a starting framework. Add proven UXM improvements through versioned library updates, not one-off silent edits.
