---
name: openHiTLS-bugAnalysis
description: Analyze whether openHiTLS has issues similar to those found in OpenSSL CODE_CHANGE commits. Reads the OpenSSL commit review at output/openssl_commit_review.md, cross-references the openHiTLS source at output/openhitls, and produces an HTML report in output/ via the generate-html skill. Use when the user wants a cross-project bug-impact analysis between OpenSSL and openHiTLS.
---

# openHiTLS Bug Analysis Skill

## Role

You are a senior cryptographic library maintainer and security researcher.
You are fluent in both the OpenSSL 3.5 codebase and the openHiTLS codebase.

Your task is to determine, for every OpenSSL commit marked `CODE_CHANGE` in the
review report, whether the openHiTLS source tree contains the **same**, a
**similar**, or a **related** defect. The goal is proactive bug discovery: use
the OpenSSL fix as a lead, then hunt for the analogous problem in openHiTLS.

The final result MUST be saved as a single HTML file in `output/` using the
`generate-html` skill.

---

# Inputs

All paths are relative to the repository root (current working directory).

| Input | Path | Description |
|---|---|---|
| OpenSSL commit review | `output/openssl_commit_review.md` | Pre-existing analysis report; only `CODE_CHANGE` entries are in scope. |
| openHiTLS source tree | `output/openhitls/` | Local checkout of openHiTLS used as the search target. |
| OpenSSL source tree | `./` (cwd) | The OpenSSL 3.5 repository itself, used to read the actual commit diffs. |
| Code structure reference | `CODE_STRUCTURE.md` (in this skill's directory) | Pre-built OpenSSL ↔ openHiTLS directory mapping, file listings, naming conventions, and feature gaps. Read this in Step 4 instead of re-exploring the codebase. |

No user-provided arguments are required. If the user provides a subset of
commit hashes, restrict the analysis to those hashes (still must be
`CODE_CHANGE` in the report).

---

# Step 1: Prepare output directory

```bash
mkdir -p output
```

---

# Step 2: Read the OpenSSL commit review report

Read `output/openssl_commit_review.md` in full (in chunks if large). Collect
every commit entry whose `分类` field is exactly `CODE_CHANGE`. For each,
extract:

- Hash (short, e.g. `d8dbadb7bd`)
- Subject (the heading line after `### <HASH> `)
- 作者 / 日期
- 影响等级 (NONE / LOW / MEDIUM / HIGH)
- 变更类型 (e.g. INPUT_VALIDATION, CRYPTO_BEHAVIOR, RETURN_VALUE, ...)
- 变更文件 (the code block listing changed files)
- 摘要
- 外部行为判定
- 证据 (file:line references — these are the primary leads for openHiTLS search)

Ignore DOC_ONLY, TEST_ONLY, APPS_ONLY, BUILD_ONLY commits entirely. They are
out of scope and must NOT appear in the final report.

If no `CODE_CHANGE` commits are found, write a minimal HTML report stating
"无 CODE_CHANGE 提交可供分析" and stop.

---

# Step 3: For each CODE_CHANGE commit, gather the OpenSSL fix context

For each in-scope commit, run (inside the OpenSSL repo, cwd):

```bash
git show --stat --summary <HASH>
git show --name-only --pretty=format: <HASH>
git show --unified=80 --no-ext-diff <HASH>
```

When the report's 证据 references specific file:line, also read the
**before** state for contrast:

```bash
git show <HASH>^:<FILE>
git show <HASH>:<FILE>
```

Build a concise mental model of:

1. **The defect**: what was wrong before the fix (the exact faulty logic,
   missing check, wrong return value, etc.).
2. **The fix**: what the commit changed (the added check, corrected branch,
   new error path, etc.).
3. **The trigger**: input/condition that exposes the defect (from 建议测试
   or 证据 in the report).
4. **The affected symbols**: function names, macro names, struct fields
   touched by the diff — these are the search keys for openHiTLS.

---

# Step 4: Locate the equivalent code in openHiTLS

## 4.0 Read the pre-built structure reference

Before searching, read the pre-built code structure reference file that lives
alongside this SKILL:

```text
C:\Users\huawei\.config\opencode\skills\openHiTLS-bugAnalysis\CODE_STRUCTURE.md
```

(Read it via the Read tool with that absolute path.)

This file contains:

1. **A full OpenSSL ↔ openHiTLS directory mapping table** (Section 1) — use
   this as the primary lookup: given an OpenSSL path from a commit diff, find
   the corresponding openHiTLS directory instantly without re-exploring.
2. **Detailed OpenSSL structure** (Section 2) — file-level listings for
   `crypto/`, `ssl/`, `providers/`, `include/openssl/`.
3. **Detailed openHiTLS structure** (Section 3) — file-level listings for
   `crypto/eal/`, `crypto/provider/`, `bsl/`, `pki/`, `tls/`, `include/`.
4. **Naming convention table** (Section 4) — how OpenSSL symbols map to
   openHiTLS symbols (prefix changes, file naming patterns).
5. **Feature gap table** (Section 5) — OpenSSL features that openHiTLS likely
   does NOT implement (QUIC, OCSP, ENGINE, CT, CMP, etc.), to accelerate
   `NOT_APPLICABLE` judgments.

Use the structure reference to jump directly to the candidate openHiTLS
directory for each commit, instead of exploring the tree from scratch.

## 4.1 Search strategy

For each commit, search openHiTLS by **symbol name** first (most reliable),
then by **string literals** (error messages, reason-code names), then by
**file/directory** mapping from the structure reference:

1. **Path mapping** — look up the OpenSSL changed file(s) in Section 1 of
   `CODE_STRUCTURE.md` to get the candidate openHiTLS directory. Read the
   listed files in that directory to locate the analogous function.
2. **Symbol search** — use Grep for the key function names from the OpenSSL
   diff (e.g. `evp_cipher_asn1_to_param_ex`, `OCSP_check_validity`). openHiTLS
   often keeps C symbol names identical or nearly so. If the exact symbol is
   not found, consult Section 4 of `CODE_STRUCTURE.md` for prefix
   transformations (e.g. `EVP_`→`CRYPT_`/`EAL`, `X509_`→`HITLS_X509_`,
   `SSL_`→`HITLS_`).
3. **String search** — grep for distinctive error strings, OID strings, or
   reason-code macro names from the OpenSSL diff.
4. **Call-site search** — if the openHiTLS function name differs, search for
   the *caller* (the OpenSSL caller symbol is more likely preserved) and
   trace down to the callee.

If after all four searches no equivalent code path exists in openHiTLS,
classify the commit as `NOT_APPLICABLE` with a one-line reason (e.g. "openHiTLS
未实现 OCSP 新鲜度检查"). Consult Section 5 of `CODE_STRUCTURE.md` to confirm
whether the feature is a known gap before finalizing.

---

# Step 5: Analyze whether openHiTLS has a similar issue

For each commit where an equivalent openHiTLS code path was found, perform a
focused comparison. Answer these questions:

1. **Does openHiTLS contain the same faulty logic?**
   - Is the same check missing?
   - Is the same wrong branch taken?
   - Is the same return value produced under the same trigger condition?
2. **Is the defect reachable in openHiTLS?**
   - Is the vulnerable function called from a live code path (not dead code)?
   - Are there upstream checks in openHiTLS that would block the trigger
     before reaching the faulty function? (If so, the impact is reduced but
     the latent bug may still exist.)
3. **Are there openHiTLS-specific differences?**
   - Different input validation upstream that changes the trigger surface.
   - Different error handling that masks or exposes the bug.
   - Different algorithm support that makes the bug unreachable.

## Finding classification

Assign exactly one classification per commit:

| Classification | Label (Chinese) | Meaning |
|---|---|---|
| `HAS_SIMILAR_ISSUE` | 存在类似问题 | openHiTLS contains the same or an equivalent defect, reachable on a live code path. **Highest priority.** |
| `PARTIAL_MATCH` | 部分类似 | openHiTLS has a related but not identical issue (e.g. same area, different trigger, or the bug is partially mitigated by an upstream check). |
| `NO_SIMILAR_ISSUE` | 不存在类似问题 | The equivalent code path exists in openHiTLS but is already correct / already has the check / is not vulnerable. |
| `NOT_APPLICABLE` | 无法对应 | openHiTLS does not implement the feature or code path at all. |

## Impact assessment

For each `HAS_SIMILAR_ISSUE` or `PARTIAL_MATCH` finding, assign a severity:

- **严重 (CRITICAL)**: reachable on a common/default code path, can cause
  memory safety issue, auth bypass, or silent data corruption.
- **高 (HIGH)**: reachable but requires specific input; security-relevant
  (validation bypass, wrong cert acceptance, etc.).
- **中 (MEDIUM)**: reachable in non-default/edge cases; correctness or
  hardening issue.
- **低 (LOW)**: latent bug, heavily mitigated, or hard to trigger.

---

# Step 6: Record evidence

For every commit, record concrete evidence in the analysis. For
`HAS_SIMILAR_ISSUE` / `PARTIAL_MATCH`, this MUST include:

- The openHiTLS file path and line number(s) of the suspected code (use
  `file:line` format, e.g. `crypto/eal/src/eal_cipher.c:197`).
- A short code excerpt (3-10 lines) showing the suspected logic.
- The trigger condition that would expose it.
- The OpenSSL fix reference (commit hash + the key changed line).

For `NO_SIMILAR_ISSUE`, cite the openHiTLS file:line that already has the
correct check.

For `NOT_APPLICABLE`, state which feature/symbol was searched and not found.

---

# Step 7: Generate the HTML report

Load the `generate-html` skill and follow its template exactly.

```text
skill: generate-html
```

Save the final HTML to:

```text
output/openhitls_bug_analysis.html
```

## HTML structure

### Title (h1)

```text
openHiTLS 类似问题分析报告
```

### Meta section

```html
<div class="meta">
  生成日期：TODAY<br>
  数据来源：output/openssl_commit_review.md（仅 CODE_CHANGE 提交）<br>
  openHiTLS 源码：output/openhitls/
</div>
```

Replace `TODAY` with the current date in `YYYY-MM-DD` format.

### Overview section (h2: "概览")

A `summary-box` div with a table:

| 字段 | 值 |
|---|---|
| 分析的 OpenSSL 提交数 | N（CODE_CHANGE 总数） |
| 存在类似问题 | a（红色） |
| 部分类似 | b（黄色） |
| 不存在类似问题 | c（绿色） |
| 无法对应 | d（灰色） |
| 严重 / 高 / 中 / 低 | s / h / m / l |

### Statistics overview (h2: "统计总览")

A stat-grid (use the extra CSS from the backport skill — see Step 8 below):

```html
<div class="stat-grid">
  <div class="stat-card total"><div class="num">N</div><div class="label">CODE_CHANGE 提交</div></div>
  <div class="stat-card danger"><div class="num">a</div><div class="label">存在类似问题</div></div>
  <div class="stat-card warn"><div class="num">b</div><div class="label">部分类似</div></div>
  <div class="stat-card done"><div class="num">c</div><div class="label">不存在类似问题</div></div>
  <div class="stat-card skip"><div class="num">d</div><div class="label">无法对应</div></div>
</div>
```

Also include a table showing the severity distribution of the
`HAS_SIMILAR_ISSUE` + `PARTIAL_MATCH` findings.

### Per-commit analysis (h2: "逐提交分析")

For **each** CODE_CHANGE commit, produce an `<h3>` subsection (with an
`id` attribute). Wrap each in a `<div class="section">` card.

Each commit card contains:

1. A header line with the OpenSSL commit hash (hyperlinked to GitHub) and
   subject:

   ```html
   <h3 id="commit-<HASH>"><a href="https://github.com/openssl/openssl/commit/<HASH>"><code><HASH></code></a> <SUBJECT></h3>
   ```

2. A meta table:

   | 字段 | 值 |
   |---|---|
   | OpenSSL 影响等级 | MEDIUM |
   | OpenSSL 变更类型 | INPUT_VALIDATION |
   | openHiTLS 判定 | 存在类似问题 |
   | openHiTLS 严重程度 | 高 |
   | 对应 openHiTLS 文件 | `crypto/eal/src/eal_cipher.c:197` |

   Use tag classes for the 判定 field:
   - 存在类似问题: `<span class="tag tag-danger">存在类似问题</span>`
   - 部分类似: `<span class="tag tag-warn">部分类似</span>`
   - 不存在类似问题: `<span class="tag tag-done">不存在类似问题</span>`
   - 无法对应: `<span class="tag tag-skip">无法对应</span>`

3. **OpenSSL 缺陷描述** — a `<p>` summarizing the original defect.

4. **openHiTLS 代码分析** — a `<p>` plus a `<pre><code>` block showing the
   suspected openHiTLS code excerpt with file:line caption.

5. **触发条件** — a `<p>` describing how the bug would be triggered in
   openHiTLS (or "N/A — 无法对应" for NOT_APPLICABLE).

6. **修复建议** — a `<p>` with a concrete fix recommendation for
   `HAS_SIMILAR_ISSUE` / `PARTIAL_MATCH`; for `NO_SIMILAR_ISSUE`, state
   "openHiTLS 已正确处理，无需修复"; for `NOT_APPLICABLE`, state "openHiTLS
   未实现该功能，无需修复".

Sort the per-commit subsections by classification priority:

```text
HAS_SIMILAR_ISSUE (severity CRITICAL → HIGH → MEDIUM → LOW)
  → PARTIAL_MATCH (severity CRITICAL → HIGH → MEDIUM → LOW)
  → NO_SIMILAR_ISSUE
  → NOT_APPLICABLE
```

Within the same priority/severity, sort by OpenSSL commit hash ascending.

### Risk summary (h2: "风险摘要")

A `section` div containing:

1. A table of all `HAS_SIMILAR_ISSUE` findings:

   | Hash | Subject | openHiTLS 文件 | 严重程度 | 风险概述 |
   |---|---|---|---|---|

   Every Hash cell MUST hyperlink to GitHub:
   `<a href="https://github.com/openssl/openssl/commit/HASH"><code>HASH</code></a>`

2. A table of all `PARTIAL_MATCH` findings (same columns).

3. If both tables are empty, write: `未发现需要在 openHiTLS 中修复的问题。`

### Conclusion (h2: "结论")

A `summary-box` div with 2-4 sentences summarizing:
- How many CODE_CHANGE commits were analyzed.
- How many led to actionable findings in openHiTLS.
- The single highest-priority item to fix (if any).
- A note on coverage limitations (e.g. "openHiTLS 未实现的功能未纳入分析")。

### Footer

```html
<div class="footer">
  openHiTLS 类似问题分析报告 | 生成日期：TODAY | 基于 OpenSSL CODE_CHANGE 提交
</div>
```

---

# Step 8: Extra CSS

Add the following CSS rules AFTER the existing `generate-html` template styles
(inside the same `<style>` block):

```css
.tag-danger { background: #3d1515; color: #f85149; }
.tag-warn { background: #3d2e00; color: #d29922; }
.tag-done { background: #1a3a2a; color: #3fb950; }
.tag-skip { background: #2a2a2a; color: #8b949e; }
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
.stat-card.total .num { color: var(--heading); }
.stat-card.danger .num { color: var(--danger); }
.stat-card.warn .num { color: var(--warn); }
.stat-card.done .num { color: var(--accent2); }
.stat-card.skip .num { color: var(--muted); }
pre {
  background: #1c2128;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.8rem 1rem;
  overflow-x: auto;
  margin: 0.6rem 0 1rem;
  font-size: 0.85rem;
  line-height: 1.5;
}
pre code {
  background: none;
  padding: 0;
  color: var(--text);
}
```

---

# Step 9: Commit hash hyperlinks

**CRITICAL**: Every OpenSSL commit hash that appears anywhere in the report
(tables, headings, prose) MUST be a hyperlink to GitHub:

```html
<a href="https://github.com/openssl/openssl/commit/<HASH>"><code><HASH></code></a>
```

Use the short hash as both the link text and URL suffix.

---

# Step 10: Final response

After saving the HTML file, respond only with:

```markdown
openHiTLS 类似问题分析报告已生成。

文件：output/openhitls_bug_analysis.html

统计：
- 分析的 CODE_CHANGE 提交：N
- 存在类似问题：a
- 部分类似：b
- 不存在类似问题：c
- 无法对应：d
```

Do not paste the full HTML content into chat unless the user asks for it.

---

# Strict rules

```text
1. Only analyze commits whose 分类 is exactly CODE_CHANGE in
   output/openssl_commit_review.md. All other categories (DOC_ONLY,
   TEST_ONLY, APPS_ONLY, BUILD_ONLY) MUST be excluded from the report
   entirely.

2. The openHiTLS source tree is at output/openhitls/. The OpenSSL source
   tree is the current working directory. Do not confuse the two when
   citing file paths.

3. For every CODE_CHANGE commit, you MUST attempt to locate the equivalent
   code in openHiTLS before classifying it as NOT_APPLICABLE. FIRST read the
   pre-built CODE_STRUCTURE.md (in this skill's directory) to get the
   candidate openHiTLS directory from the mapping table, then use path
   mapping → symbol search → string search → call-site search. Record which
   searches were performed.

4. Every HAS_SIMILAR_ISSUE and PARTIAL_MATCH finding MUST cite at least one
   openHiTLS file:line and include a code excerpt. Findings without concrete
   openHiTLS evidence are invalid.

5. Every commit hash in the HTML MUST be a hyperlink to
   https://github.com/openssl/openssl/commit/<HASH>.

6. Use the generate-html skill's template exactly. Only add the extra CSS
   classes listed in Step 8. Do not invent additional styles.

7. The HTML document language MUST be zh-CN (Chinese). All section headings,
   descriptions, and analysis text MUST be in Chinese. Code excerpts and
   file paths remain in their original language.

8. The output file MUST be saved to output/openhitls_bug_analysis.html.
   No other output files are user-facing.

9. Sort per-commit subsections by classification priority:
   HAS_SIMILAR_ISSUE → PARTIAL_MATCH → NO_SIMILAR_ISSUE → NOT_APPLICABLE,
   then by severity (CRITICAL → HIGH → MEDIUM → LOW), then by hash ascending.

10. The severity assessment (严重/高/中/低) applies only to HAS_SIMILAR_ISSUE
    and PARTIAL_MATCH. For NO_SIMILAR_ISSUE and NOT_APPLICABLE, leave
    severity blank or write "—".

11. Do not modify the openHiTLS source tree. This skill is read-only
    analysis. Do not apply fixes.

12. Do not modify the OpenSSL source tree or the commit review report.

13. The final chat response MUST be short and MUST NOT include the full HTML.

14. If the user provides a subset of commit hashes, restrict the analysis to
    those hashes, but still exclude any that are not CODE_CHANGE in the
    report. Inform the user of any excluded hashes in the final response.

15. When openHiTLS does not implement a feature (NOT_APPLICABLE), state
    explicitly which symbol/path was searched and not found, so the finding
    is auditable.
```
