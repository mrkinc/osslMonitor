---
name: code-backport
description: Cherry-pick a user-provided list of commits (possibly unordered) into a backport fork, sorted chronologically oldest-first, using the analysis report from output/openssl_commit_review.md to determine category and skip rules.
---

# Code Backport Skill

## Role

You are a senior OpenSSL maintainer performing backport cherry-picks.

The user provides a list of commit hashes (possibly unordered). You must:

1. Read the existing analysis report at `output/openssl_commit_review.md` to determine each commit's category and metadata.
2. Sort the commits chronologically from oldest to newest.
3. Cherry-pick each eligible commit into the backport fork with a rewritten commit message.
4. Skip DOC_ONLY and APPS_ONLY commits.
5. Update the analysis report with the cherry-pick results.

---

# Inputs

The user provides:

```text
<COMMIT_HASH_LIST>
```

A space-separated or newline-separated list of short or full commit hashes. The list may be unordered.

The repository is assumed to be the current working directory.

The analysis report is at:

```text
output/openssl_commit_review.md
```

---

# Step 1: Resolve and sort commits

For each hash in the user-provided list, resolve it to the full commit hash and get its commit timestamp:

```bash
git log -1 --pretty=format:'%H %cI %s' <HASH>
```

Collect all results, then sort by timestamp ascending (oldest first). This is the cherry-pick order.

If any hash cannot be resolved, record it as a failed entry and skip it.

---

# Step 2: Read analysis report

Read `output/openssl_commit_review.md` and extract for each commit:

- `分类` (category): DOC_ONLY, TEST_ONLY, APPS_ONLY, BUILD_ONLY, or CODE_CHANGE
- `影响等级` (impact level): NONE, LOW, MEDIUM, or HIGH
- `变更类型` (change type)

Use this information to determine which commits to skip.

---

# Step 3: Prepare backport directory

Run from the repository root:

```bash
mkdir -p backport
```

If `backport/` already exists and contains a git repository, skip cloning and proceed.

---

# Step 4: Clone the user's fork

Clone the user's OpenSSL fork on the 3.5 branch into the `backport` directory if it does not already exist:

```bash
git clone -b openssl-3.5 https://github.com/mrkinc/openssl.git backport
```

If the branch name differs from `openssl-3.5`, ask the user for the correct branch name.

---

# Step 5: Configure upstream

Inside the cloned repository, add the official OpenSSL repository as `upstream`:

```bash
cd backport
git remote add upstream https://github.com/openssl/openssl.git
git fetch upstream
```

If `upstream` remote already exists, skip adding it but still fetch.

---

# Step 6: Cherry-pick commits

Iterate through the sorted commit list. For each commit:

## Skip rules

If the commit's category from the analysis report is:

```text
DOC_ONLY
APPS_ONLY
```

Skip it. Record it in the "Skipped" section of the results.

All other categories (TEST_ONLY, BUILD_ONLY, CODE_CHANGE) are eligible for cherry-pick.

## Commit message rewriting rules

The original commit message must be transformed as follows:

1. **First line**: Prepend `[Backport] ` to the original first line (subject).
2. **Insert after first line**: Add a blank line, then `Offering: HiSec-ICT TLS`, then a blank line, then `Reference: https://github.com/openssl/openssl/commit/<FULL_HASH>`, then a blank line.
3. **Rest of message**: Append the original commit message body (everything after the first line).

**Example transformation:**

Original:

```text
aes_wrap: fix buffer overflow in EVP_CipherInit_ex

The EVP_CipherInit_ex function...
```

Rewritten:

```text
[Backport] aes_wrap: fix buffer overflow in EVP_CipherInit_ex

Offering: HiSec-ICT TLS

Reference: https://github.com/openssl/openssl/commit/abc123def456...

The EVP_CipherInit_ex function...
```

## Cherry-pick command

Use the following approach for each eligible commit:

```bash
# Get the original commit message
ORIGINAL_MSG=$(git -C <UPSTREAM_REPO> log -1 --pretty=format:'%B' <FULL_COMMIT_HASH>)

# Extract first line and body
FIRST_LINE=$(echo "$ORIGINAL_MSG" | head -n 1)
BODY=$(echo "$ORIGINAL_MSG" | tail -n +2)

# Construct new message
NEW_MSG="[Backport] $FIRST_LINE

Offering: HiSec-ICT TLS

Reference: https://github.com/openssl/openssl/commit/<FULL_COMMIT_HASH>
$BODY"

# Cherry-pick with rewritten message
git cherry-pick --no-commit <FULL_COMMIT_HASH>
git commit -m "$NEW_MSG"
```

## Conflict handling

If a cherry-pick fails due to conflicts:

1. Record the failed commit hash and subject.
2. Run `git cherry-pick --abort`.
3. Continue with the next commit.
4. Add the failed commit to the "Failed Cherry-picks" section.

---

# Step 7: Update the analysis report

Append a new section to `output/openssl_commit_review.md` before the "最终结论" (Final Conclusion) section:

```markdown
## Backport Cherry-pick 结果

### 成功

| # | 哈希 | 主题 |
|---|---|---|
| 1 | ... | ... |

### 跳过 (DOC_ONLY / APPS_ONLY)

| # | 哈希 | 主题 | 分类 |
|---|---|---|---|
| 1 | ... | ... | ... |

### 失败 (冲突)

| # | 哈希 | 主题 | 原因 |
|---|---|---|---|
| 1 | ... | ... | ... |
```

If all cherry-picks succeeded, write `None.` under "失败 (冲突)".

If no commits were skipped, write `None.` under "跳过 (DOC_ONLY / APPS_ONLY)".

---

# Step 8: Final response

After finishing the backport, respond only with:

```markdown
Backport completed.

Results:

- Successful: <count>
- Skipped (DOC_ONLY / APPS_ONLY): <count>
- Failed (conflicts): <count>

Updated files:

- output/openssl_commit_review.md
- backport/ (cloned fork with cherry-picked commits)
```

Do not paste the full report into chat unless the user asks for it.

---

# Strict rules

```text
1. Commits provided by the user may be unordered. You MUST sort them chronologically
   (oldest first) before cherry-picking.

2. Read the analysis report at output/openssl_commit_review.md to determine each
   commit's category. Use this to decide skip eligibility.

3. DOC_ONLY and APPS_ONLY commits must NOT be cherry-picked. Record them as skipped.

4. All other categories (TEST_ONLY, BUILD_ONLY, CODE_CHANGE) are eligible for
   cherry-pick.

5. Cherry-pick commits in chronological order (oldest first).

6. If a cherry-pick fails, abort it, record the failure, and continue with the next
   commit.

7. The backport directory is backport/ relative to the repository root.

8. The user's fork remote is origin, the official repo remote is upstream.

9. The report section must be in chinese.

10. The cherry-pick results must be appended to the existing report, not replace it.

11. If the backport directory already exists with a git repo, reuse it. Do not re-clone.

12. If upstream remote already exists, do not re-add it. Just fetch.
```
