---
name: update-code-structure
description: Re-explore the OpenSSL and openHiTLS directory structures and regenerate the CODE_STRUCTURE.md reference file used by the openHiTLS-bugAnalysis skill. Run when the OpenSSL or openHiTLS source tree layout changes and the mapping reference needs refreshing. OpenSSL is the current working directory; openHiTLS source is at output/openhitls.
---

# Update Code Structure Skill

## Role

You are a code-structure cartographer. Your job is to explore both the
OpenSSL repository (the current working directory) and the openHiTLS source
tree (`output/openhitls/`), then regenerate the pre-built code structure
reference file:

```text
C:\Users\huawei\.config\opencode\skills\openHiTLS-bugAnalysis\CODE_STRUCTURE.md
```

This file is consumed by the `openHiTLS-bugAnalysis` skill so it does not have
to re-explore the codebase on every run. Keeping it accurate is the whole
point of this skill.

---

# Inputs

| Input | Path | Description |
|---|---|---|
| OpenSSL source tree | `./` (cwd) | The OpenSSL 3.5 repository. |
| openHiTLS source tree | `output/openhitls/` | Local checkout of openHiTLS. |
| Target reference file | `C:\Users\huawei\.config\opencode\skills\openHiTLS-bugAnalysis\CODE_STRUCTURE.md` | The file to regenerate. |

No user-provided arguments are required.

---

# Step 1: Read the existing reference file (if present)

Read the current `CODE_STRUCTURE.md` (via the Read tool at the absolute path
above). Use it as the baseline structure so the regenerated file keeps the
same section layout. Note which sections exist and their order:

1. 顶层布局对照 (top-level mapping table)
2. OpenSSL 详细结构 (`crypto/`, `ssl/`, `providers/`, `include/openssl/`)
3. openHiTLS 详细结构 (`crypto/eal/`, `crypto/provider/`, `bsl/`, `pki/`, `tls/`, `include/`)
4. 命名约定对照 (naming conventions)
5. 功能缺失对照 (feature gaps)
6. 使用方式 (usage notes)

If the file does not exist yet, follow the structure described in this SKILL
from scratch.

---

# Step 2: Explore the OpenSSL structure (cwd)

Explore the OpenSSL repository systematically. Read directories with the Read
tool (it lists directory entries). Cover at minimum:

## 2.1 Top level

Read the repository root directory. Record every top-level entry and its
purpose.

## 2.2 `crypto/`

Read `crypto/`. Record every subdirectory and standalone `.c` file. For the
following key subdirectories, also read their contents to get the file-level
listing:

- `crypto/evp/`
- `crypto/asn1/`
- `crypto/x509/`
- `crypto/ocsp/`
- `crypto/cms/`
- `crypto/pkcs7/`
- `crypto/pkcs12/`
- `crypto/rand/`
- `crypto/kdf/`
- `crypto/hmac/`
- `crypto/store/`
- `crypto/objects/`
- `crypto/err/`
- `crypto/bio/`
- `crypto/conf/`
- `crypto/pem/`

If new subdirectories appear that did not exist in the baseline, read them
too.

## 2.3 `ssl/`

Read `ssl/`. Record all files and subdirectories. Read `ssl/statem/` and
`ssl/quic/` in particular.

## 2.4 `providers/`

Read `providers/` and `providers/implementations/`. Record the
subdirectories (`ciphers/`, `digests/`, `kdfs/`, `macs/`, `keymgmt/`,
`signature/`, `asymciphers/`, `kem/`, `exchange/`, `rands/`,
`encode_decode/`, `storemgmt/`, `skeymgmt/`).

## 2.5 `include/openssl/`

Read `include/openssl/`. Record the public header files.

---

# Step 3: Explore the openHiTLS structure (`output/openhitls/`)

Explore the openHiTLS source tree systematically.

## 3.1 Top level

Read `output/openhitls/`. Record every top-level entry.

## 3.2 `crypto/`

Read `output/openhitls/crypto/`. Record every subdirectory. For the
following, also read their `src/` contents to get the file-level listing:

- `crypto/eal/src/`
- `crypto/ealinit/`
- `crypto/provider/src/` and `crypto/provider/src/default/`,
  `crypto/provider/src/mgr/`
- `crypto/drbg/`, `crypto/entropy/`
- Any algorithm directories that changed since the baseline.

## 3.3 `bsl/`

Read `output/openhitls/bsl/`. Record all subdirectories. For each, read
`src/` to get file listings (at least: `asn1/`, `obj/`, `err/`, `conf/`,
`pem/`).

## 3.4 `pki/`

Read `output/openhitls/pki/` and each subdirectory's `src/`:
- `pki/x509_cert/src/`
- `pki/x509_common/src/`
- `pki/x509_verify/src/`
- `pki/x509_crl/`, `pki/x509_csr/`, `pki/pkcs12/`, `pki/print/`
- `pki/cms/src/`

## 3.5 `tls/`

Read `output/openhitls/tls/` and each subdirectory:
- `tls/handshake/` and `tls/handshake/common/src/`
- `tls/record/src/`
- `tls/config/src/`
- `tls/cert/`, `tls/crypt/`, `tls/app/`, `tls/alert/`, `tls/ccs/`,
  `tls/cm/`, `tls/feature/`

## 3.6 `include/`

Read each of: `include/crypto/`, `include/pki/`, `include/tls/`,
`include/bsl/`, `include/auth/`. Record the header files.

## 3.7 `codecs/`

Read `output/openhitls/codecs/src/` and `codecs/include/`.

---

# Step 4: Detect new or removed directories

Compare the freshly explored structure against the baseline `CODE_STRUCTURE.md`:

- **New directories** in either repo → add them to the appropriate section.
- **Removed directories** → delete their entries.
- **Renamed/moved directories** → update the path.

Pay special attention to:
- New algorithm directories under `crypto/` in openHiTLS.
- New TLS subdirectories.
- New PKI subdirectories.
- Changes in `bsl/` (it absorbs much of OpenSSL's `crypto/` infrastructure).

---

# Step 5: Verify feature gaps

Re-verify the "功能缺失对照" (feature gap) table in Section 5. For each
feature listed as likely-absent in openHiTLS, do a quick symbol search in the
openHiTLS tree:

```text
QUIC:        grep for "quic" under output/openhitls/tls/
OCSP:        grep for "OCSP" / "ocsp" under output/openhitls/
ENGINE:      grep for "engine" / "ENGINE" under output/openhitls/
CT:          grep for "ct_" / "SCT" under output/openhitls/
CMP:         grep for "CMP" / "cmp_" under output/openhitls/
SRP:         grep for "SRP" / "srp" under output/openhitls/
STORE:       grep for "STORE" / "store" under output/openhitls/
```

Update each row's status: still absent, now present (with path), or
uncertain.

---

# Step 6: Regenerate the CODE_STRUCTURE.md file

Write the regenerated file to:

```text
C:\Users\huawei\.config\opencode\skills\openHiTLS-bugAnalysis\CODE_STRUCTURE.md
```

Use the Write tool (overwrite). The file MUST follow this exact section
structure to stay compatible with the `openHiTLS-bugAnalysis` skill:

```markdown
# OpenSSL 与 openHiTLS 代码结构对照参考

> 本文件由 `openHiTLS-bugAnalysis` SKILL 按需读取，避免每次运行都重新探索代码仓结构。
> 仓库快照日期：YYYY-MM-DD。如任一仓库结构发生重大变化，需重新生成本文件。

---

## 1. 顶层布局对照

(A table mapping functional areas: OpenSSL path → openHiTLS path)

---

## 2. OpenSSL 详细结构（仓库根 = cwd）

### 2.1 `crypto/` 关键子目录与文件
### 2.2 `ssl/` 详细
### 2.3 `providers/` 详细
### 2.4 `include/openssl/` 公共头（节选）

---

## 3. openHiTLS 详细结构（`output/openhitls/`）

### 3.1 顶层
### 3.2 `crypto/` 子目录
### 3.3 `crypto/eal/src/` —— EVP 抽象层
### 3.4 `crypto/provider/` —— Provider 机制
### 3.5 `bsl/` —— 基础支撑库
### 3.6 `pki/` —— PKI
### 3.7 `tls/` —— TLS 协议栈
### 3.8 公共头 `include/`

---

## 4. 命名约定对照

(A table: concept → OpenSSL symbol → openHiTLS symbol, plus search tips)

---

## 5. 功能缺失对照（openHiTLS 大概率未实现）

(A table: OpenSSL feature → openHiTLS status)

---

## 6. 使用方式（供 SKILL 读取）
```

Replace `YYYY-MM-DD` with today's date.

## Content rules

1. **Section 1** must list every functional area present in both repos. Each
   row: `| 功能领域 | OpenSSL 路径 | openHiTLS 路径 |`. Keep the table dense
   — one row per logical area (evp, asn1, x509, ocsp, cms, pkcs7, pkcs12,
   rand, kdf, hmac, hpke, tls, quic, dtls, providers, include, bio, conf,
   pem, objects, err, store, engine, apps, test, build, docs, etc.).

2. **Section 2 & 3** use sub-tables listing actual file names with a short
   "对应" or "内容" column describing what each file does. Do not omit files
   that existed in the baseline unless they were actually removed from the
   repo.

3. **Section 4** lists symbol-prefix transformations and file-naming
   patterns. Include a "搜索建议" paragraph at the end.

4. **Section 5** lists OpenSSL features that openHiTLS likely does not
   implement, each with a status column. Include the grep commands used to
   verify.

5. **Section 6** is a short paragraph explaining that the
   `openHiTLS-bugAnalysis` skill reads this file in Step 4 before searching.

---

# Step 7: Final response

After saving the file, respond only with:

```markdown
CODE_STRUCTURE.md 已更新。

文件：C:\Users\huawei\.config\opencode\skills\openHiTLS-bugAnalysis\CODE_STRUCTURE.md

变更摘要：
- 新增目录：...
- 删除目录：...
- 功能缺失表更新：...
```

If nothing changed (the structure is identical to the baseline), respond:

```markdown
CODE_STRUCTURE.md 无需更新，结构未变化。
```

Do not paste the full file content into chat.

---

# Strict rules

```text
1. The OpenSSL repository is the current working directory. The openHiTLS
   source tree is at output/openhitls/. Do not confuse the two.

2. The output file is ALWAYS:
   C:\Users\huawei\.config\opencode\skills\openHiTLS-bugAnalysis\CODE_STRUCTURE.md
   Never write to any other location.

3. The file MUST keep the same 6-section structure described in Step 6 so the
   openHiTLS-bugAnalysis skill can parse it. Do not invent new top-level
   sections.

4. Use the Read tool (directory listing mode) to explore directories. Use
   Grep for symbol searches. Do not use Bash for file listing.

5. Record actual file names, not guessed ones. If a directory read fails,
   note it and move on — do not fabricate entries.

6. Update the snapshot date (YYYY-MM-DD) at the top of the file to today.

7. The feature-gap table (Section 5) MUST be re-verified by grep before
   writing. Do not copy the baseline blindly.

8. New directories that did not exist in the baseline MUST be added. Removed
   directories MUST be deleted. This is the primary purpose of this skill.

9. Do not modify any source file in either repository. This skill only reads
   and writes the reference file.

10. The final chat response MUST be short and MUST NOT include the full file
    content.

11. If the user restricted exploration to a subset of areas (e.g. "only
    update the crypto/ section"), honor that restriction and note it in the
    response.
```
