---
name: generate-html
description: Use when generating HTML documents. Produces a dark-themed, sidebar-navigated page with the GitHub-dark style. Use ONLY when the user asks to create or generate an HTML file or page.
---

# generate-html

Generate a single-file HTML document with the dark theme and left sidebar navigation.

## When to use

When the user asks to create, generate, or write an HTML file/page/report.

## Rules

1. **Single file** — all CSS and JS are inline; no external dependencies.
2. **Left sidebar** — always present, auto-generated from `h2` and `h3` headings.
3. **Scroll highlight** — the sidebar highlights the current section as the user scrolls.
4. **Heading IDs** — every `h2` and `h3` must have an `id` attribute for anchor links.
5. **`html lang="zh-CN"`** — default to Chinese; change only if the user specifies otherwise.
6. **Content first** — the user provides the content; you apply the template structure and style.

## Complete template

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITLE}}</title>
<style>
  :root {
    --bg: #0d1117;
    --card: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --heading: #f0f6fc;
    --accent: #58a6ff;
    --accent2: #3fb950;
    --warn: #d29922;
    --danger: #f85149;
    --muted: #8b949e;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, "Noto Sans SC", "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.75;
    padding: 0;
  }
  .layout {
    display: flex;
    min-height: 100vh;
  }
  .sidebar {
    width: 260px;
    min-width: 260px;
    background: var(--card);
    border-right: 1px solid var(--border);
    padding: 1.5rem 0;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    flex-shrink: 0;
  }
  .sidebar-title {
    color: var(--heading);
    font-size: 0.9rem;
    font-weight: 700;
    padding: 0 1.2rem 0.8rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.6rem;
    letter-spacing: 0.05em;
  }
  .sidebar ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  .sidebar li { margin: 0; }
  .sidebar a {
    display: block;
    padding: 0.4rem 1.2rem;
    color: var(--muted);
    text-decoration: none;
    font-size: 0.85rem;
    line-height: 1.6;
    transition: all 0.15s;
    border-left: 3px solid transparent;
  }
  .sidebar a:hover {
    color: var(--accent);
    background: rgba(88,166,255,0.06);
    border-left-color: var(--accent);
  }
  .sidebar .nav-h2 > a {
    color: var(--text);
    font-weight: 600;
    font-size: 0.88rem;
    padding-top: 0.6rem;
    padding-bottom: 0.4rem;
  }
  .sidebar .nav-h3 > a {
    padding-left: 2rem;
    font-size: 0.82rem;
  }
  .main {
    flex: 1;
    min-width: 0;
    padding: 2rem 2rem 2rem 2.5rem;
    display: flex;
    justify-content: center;
    position: relative;
  }
  .back-home {
    position: absolute;
    top: 1rem;
    right: 1.5rem;
    color: var(--muted);
    text-decoration: none;
    font-size: 0.85rem;
    padding: 0.3rem 0.8rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    transition: all 0.15s;
  }
  .back-home:hover {
    color: var(--accent);
    border-color: var(--accent);
  }
  .container {
    max-width: 860px;
    width: 100%;
  }
  h1 {
    color: var(--heading);
    font-size: 1.75rem;
    border-bottom: 2px solid var(--accent);
    padding-bottom: 0.6rem;
    margin-bottom: 1.2rem;
  }
  h2 {
    color: var(--accent);
    font-size: 1.3rem;
    margin-top: 2rem;
    margin-bottom: 0.8rem;
    padding-left: 0.5rem;
    border-left: 3px solid var(--accent);
  }
  h3 {
    color: var(--warn);
    font-size: 1.05rem;
    margin-top: 1.2rem;
    margin-bottom: 0.5rem;
  }
  p { margin-bottom: 0.8rem; }
  .meta {
    color: var(--muted);
    font-size: 0.85rem;
    margin-bottom: 1.5rem;
  }
  .meta a { color: var(--accent); text-decoration: none; }
  .meta a:hover { text-decoration: underline; }
  .summary-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
  }
  .summary-box p { margin-bottom: 0.5rem; }
  .summary-box p:last-child { margin-bottom: 0; }
  .section {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  ul, ol {
    padding-left: 1.5rem;
    margin-bottom: 0.8rem;
  }
  li { margin-bottom: 0.4rem; }
  .tag {
    display: inline-block;
    font-size: 0.75rem;
    padding: 0.15rem 0.5rem;
    border-radius: 12px;
    margin-right: 0.4rem;
    font-weight: 600;
  }
  .tag-impact { background: #1f3a5f; color: #58a6ff; }
  .tag-action { background: #1a3a2a; color: #3fb950; }
  .tag-warn { background: #3d2e00; color: #d29922; }
  code {
    background: #1c2128;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-size: 0.9em;
    color: var(--accent);
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.8rem 0;
    font-size: 0.92rem;
  }
  th, td {
    border: 1px solid var(--border);
    padding: 0.5rem 0.8rem;
    text-align: left;
  }
  th { background: #1c2128; color: var(--heading); }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  .highlight { color: var(--warn); font-weight: 600; }
  .footer {
    text-align: center;
    color: var(--muted);
    font-size: 0.8rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
  }
</style>
</head>
<body>
<div class="layout">
  <nav class="sidebar">
    <div class="sidebar-title">目录</div>
    <ul>
      {{NAV_ITEMS}}
    </ul>
  </nav>
  <div class="main">
  <a class="back-home" href="/">&#x2190; 回到首页</a>
  <div class="container">

{{CONTENT}}

  </div>
  </div>
</div>
<script>
  (function() {
    var links = document.querySelectorAll('.sidebar a');
    var sections = [];
    links.forEach(function(link) {
      var id = link.getAttribute('href').slice(1);
      var el = document.getElementById(id);
      if (el) sections.push({ el: el, link: link });
    });
    function onScroll() {
      var scrollY = window.scrollY + 120;
      var current = null;
      sections.forEach(function(s) {
        if (s.el.offsetTop <= scrollY) current = s;
      });
      links.forEach(function(l) { l.style.color = ''; l.style.borderLeftColor = 'transparent'; });
      if (current) {
        current.link.style.color = 'var(--accent)';
        current.link.style.borderLeftColor = 'var(--accent)';
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  })();
</script>
</body>
</html>
```

## Template placeholders

| Placeholder | Description |
|---|---|
| `{{TITLE}}` | The `<title>` text. |
| `{{NAV_ITEMS}}` | Sidebar navigation items. Each `h2` becomes `<li class="nav-h2"><a href="#id">text</a></li>`, each `h3` becomes `<li class="nav-h3"><a href="#id">text</a></li>`. |
| `{{CONTENT}}` | The main body content. Every `h2` and `h3` must carry an `id` attribute matching the corresponding nav link. |

## Workflow

1. Receive the user's content or topic.
2. Structure the content into `h1` (title), `h2` (major sections), `h3` (subsections).
3. Assign a kebab-case `id` to every `h2` and `h3` (e.g. `id="version-upgrade"`).
4. Build the `{{NAV_ITEMS}}` list from the headings, using `nav-h2` for h2 entries and `nav-h3` for h3 entries.
5. Wrap h2 sections in `<div class="section">` cards; use `<div class="summary-box">` for introductory summaries.
6. Use `.tag-impact`, `.tag-action`, `.tag-warn` for inline labels; `.highlight` for emphasis; `.meta` for source/date info; `.footer` for page footer.
7. Fill the template and write the file.
8. Do NOT add any CSS classes or styles beyond those defined in the template above. If the user requests extra styles, add them after the existing rules.
