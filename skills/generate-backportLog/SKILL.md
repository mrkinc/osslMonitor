---
name: generate-backportHtml
description: Generate an HTML backport summary report. The user provides a list of backported commit hashes, the skill reads the full commit analysis from output/openssl_commit_review.md, classifies backported vs not-backported commits, and produces a dark-themed HTML report with sidebar navigation. Commit hashes in tables are hyperlinked to GitHub.
---

# Generate Backport Log Skill

## Role

You are a senior OpenSSL maintainer producing a backport summary report.

The user provides a list of commit hashes that have been backported. You must read the full commit analysis from `output/openssl_commit_review.md`, classify every commit as backported or not-backported, and generate a polished HTML report using the `generate-html` skill.

---

# Inputs

The user provides:

```text
<BACKPORTED_COMMIT_HASH_LIST>
```

A space-separated or newline-separated list of short commit hashes that have been backported.

The user may also provide:

- **回合范围信息** (optional): upstream branch name, date range, backport type. If not provided, infer from `output/openssl_commit_review.md` or ask the user.

The commit analysis report is at:

```text
output/openssl_commit_review.md
```

---

# Step 1: Read the commit analysis report

Read `output/openssl_commit_review.md` in full. Extract every commit entry with:

- Hash (short, e.g. `80c15faaf7`)
- Subject (first line of the section heading)
- 分类 (category): DOC_ONLY, TEST_ONLY, APPS_ONLY, BUILD_ONLY, CODE_CHANGE
- 影响级别 (impact level): NONE, LOW, MEDIUM, HIGH
- 变更类型 (change type): e.g. INPUT_VALIDATION, CRYPTO_BEHAVIOR, TLS_SSL_BEHAVIOR, etc.
- 变更文件 (changed files)
- 摘要 (summary)
- 日期 (date), if available

If the file is large, read it in chunks. You MUST read every commit entry.

---

# Step 2: Classify commits

Build two sets:

## Backported set

All commits whose hash appears in the user-provided list.

## Not-backported set

All commits from the analysis report whose hash does NOT appear in the user-provided list.

### Not-backported sub-categories

For the not-backported set, classify each commit into exactly one of:

```text
1. DOC_ONLY     — 分类 is DOC_ONLY
2. APPS_ONLY    — 分类 is APPS_ONLY
3. QUIC_ONLY    — ALL changed files are under QUIC-related paths:
                  ssl/quic/, ssl/rio/, test/radix/quic*, test/quic*,
                  test/helpers/quic*, include/internal/quic_*
4. OTHER        — everything else (CODE_CHANGE, TEST_ONLY, BUILD_ONLY that
                  are not QUIC_ONLY)
```

For the OTHER category, further sub-sort by impact level:

```text
HIGH → MEDIUM → LOW → NONE → BUILD_ONLY
```

Within each impact level, sort by hash for consistency.

---

# Step 3: Prepare output directory

Ensure the output directory exists:

```bash
mkdir -p output
```

---

# Step 4: Generate the HTML report

Load the `generate-html` skill:

```text
skill: generate-html
```

Follow the `generate-html` template exactly. Fill in the content as described below.

## Commit hash hyperlinks

**CRITICAL**: Every commit hash that appears in a `<td>` cell MUST be a hyperlink to GitHub:

```html
<a href="https://github.com/openssl/openssl/commit/HASH">HASH</a>
```

Where `HASH` is the short hash (e.g. `80c15faaf7`). The link text should show the short hash in a `<code>` element for visual consistency:

```html
<a href="https://github.com/openssl/openssl/commit/80c15faaf7"><code>80c15faaf7</code></a>
```

This applies to ALL tables in the report (backported, not-backported, risk sections, etc.).

## HTML structure

### Title (h1)

```text
OpenSSL Commit 回合总结报告
```

### Meta section

```html
<div class="meta">
  生成日期：TODAY
</div>
```

### Backport scope section (h2: "概览")

A `section` card containing a table with the backport scope information:

| Field | Value |
|---|---|
| 上游分支 | e.g. OpenSSL 3.5 |
| 回合类型 | e.g. Bugfix Commit |
| 时间范围 | e.g. 2026-06-04 ~ 2026-08-07 |
| 哈希范围 | e.g. `e9dfa37740e6` ~ `3d9ddf4b9c` |
| 总提交数 | N |
| 已回合 | M (green) |
| 未回合 | K (yellow) |

If the user does not provide scope info, extract the hash range from the report header and ask the user for the date range and branch name.

### Statistics overview (h2: "统计总览")

A grid of stat cards showing:

```html
<div class="stat-grid">
  <div class="stat-card total"><div class="num">132</div><div class="label">总提交数</div></div>
  <div class="stat-card done"><div class="num">50</div><div class="label">已回合</div></div>
  <div class="stat-card skip"><div class="num">19</div><div class="label">仅文档</div></div>
  <div class="stat-card skip"><div class="num">2</div><div class="label">仅应用</div></div>
  <div class="stat-card quic"><div class="num">11</div><div class="label">仅QUIC</div></div>
  <div class="stat-card other"><div class="num">50</div><div class="label">其他未回合</div></div>
</div>
```

The stat-grid and stat-card CSS classes are defined below in the "Extra CSS" section.

Also include a table showing the impact distribution of backported commits (HIGH/MEDIUM/LOW/NONE counts).

### Backported commits (h2: "已回合提交")

A `section` div with a table:

| # | Hash | Subject | Category | Impact |
|---|---|---|---|---|
| 1 | `<a href="..."><code>HASH</code></a>` | Subject | tag | tag |

Sort by impact level descending (HIGH → MEDIUM → LOW → NONE), then by hash.

Use tag classes:

- HIGH: `<span class="tag tag-danger">HIGH</span>`
- MEDIUM: `<span class="tag tag-warn">MEDIUM</span>`
- LOW: `<span class="tag tag-impact">LOW</span>`
- NONE: `<span class="tag tag-action">NONE</span>`
- Category tags: `<span class="tag tag-danger">CODE_CHANGE</span>`, `<span class="tag tag-test">TEST_ONLY</span>`, etc.

### Not-backported commits (h2: "未回合提交")

A `summary-box` div with total counts.

#### DOC_ONLY (h3: "仅文档修改 (DOC_ONLY)")

A `section` div with a table:

| # | Hash | Subject |
|---|---|---|
| 1 | `<a href="..."><code>HASH</code></a>` | Subject |

#### APPS_ONLY (h3: "仅应用修改 (APPS_ONLY)")

Same format as DOC_ONLY.

#### QUIC_ONLY (h3: "仅QUIC修改")

A `section` div with a table:

| # | Hash | Subject | Category | Impact |
|---|---|---|---|---|

#### OTHER (h3: "其他未回合提交")

A `section` div, sub-divided by impact level (h3 for each):

- "高影响 (HIGH)"
- "中影响 (MEDIUM)"
- "低影响 (LOW)"
- "无影响 (NONE)"
- "仅构建 (BUILD_ONLY)"

Each sub-section has a table:

| # | Hash | Subject | Category | Change Type |
|---|---|---|---|---|

### Risk section (h2: "风险提示")

A `section` div highlighting:

1. Not-backported HIGH impact commits with risk descriptions
2. Not-backported MEDIUM impact commits with risk descriptions

Tables with columns: Hash, Subject, Risk Overview.

### Footer

```html
<div class="footer">
  OpenSSL Commit 回合总结报告 | 生成日期：TODAY | 审查范围：START_HASH ~ END_HASH
</div>
```

---

# Step 5: Extra CSS

Add the following CSS rules AFTER the existing `generate-html` template styles (inside the same `<style>` block):

```css
.tag-danger { background: #3d1515; color: #f85149; }
.tag-doc { background: #2d1f4e; color: #b392f0; }
.tag-app { background: #1f3a2a; color: #56d364; }
.tag-quic { background: #1a3040; color: #39d2c0; }
.tag-test { background: #2a2a2a; color: #8b949e; }
.tag-build { background: #2a2a2a; color: #8b949e; }
.tag-done { background: #1a3a2a; color: #3fb950; }
.tag-skip { background: #3d2e00; color: #d29922; }
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}
.stat-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
}
.stat-card .num {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.2;
}
.stat-card .label {
  font-size: 0.8rem;
  color: var(--muted);
  margin-top: 0.3rem;
}
.stat-card.done .num { color: var(--accent2); }
.stat-card.skip .num { color: var(--warn); }
.stat-card.quic .num { color: #39d2c0; }
.stat-card.other .num { color: var(--accent); }
.stat-card.total .num { color: var(--heading); }
```

---

# Step 6: Save the HTML file

Save the generated HTML file to:

```text
output/backport_report.html
```

---

# Step 7: Final response

After finishing, respond only with:

```markdown
回合总结报告已生成。

文件：output/backport_report.html

统计：
- 总提交数：N
- 已回合：M
- 未回合：K（DOC_ONLY: d, APPS_ONLY: a, QUIC_ONLY: q, 其他: o）
```

Do not paste the full HTML content into chat unless the user asks for it.

---

# Strict rules

```text
1. Read output/openssl_commit_review.md COMPLETELY. Every commit entry must be
   classified. Do not skip any commits.

2. The user provides the list of backported commit hashes. All other commits
   from the analysis report are considered not-backported.

3. QUIC_ONLY classification: a commit is QUIC_ONLY if ALL of its changed files
   are under QUIC-related paths (ssl/quic/, ssl/rio/, test/radix/quic*,
   test/quic*, test/helpers/quic*, include/internal/quic_*). If ANY changed
   file is outside these paths, the commit is NOT QUIC_ONLY.

4. EVERY commit hash in EVERY table cell MUST be a hyperlink to GitHub:
   <a href="https://github.com/openssl/openssl/commit/HASH"><code>HASH</code></a>

5. Use the generate-html skill's template exactly. Only add the extra CSS
   classes listed in Step 5.

6. The HTML document language MUST be zh-CN (Chinese).

7. The output file MUST be saved to output/backport_report.html.

8. If the user does not provide scope info (branch, date range, backport type),
   ask the user before generating the report.

9. Sort backported commits by impact level descending (HIGH → MEDIUM → LOW → NONE).

10. Sort not-backported commits by hash within each sub-category for consistency.

11. Do NOT add any CSS classes or styles beyond those defined in the generate-html
    template and the extra CSS in Step 5.

12. All content (section headings, descriptions, risk summaries) MUST be written
    in Chinese.
```
