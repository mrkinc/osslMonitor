# OpenSSL 与 openHiTLS 代码结构对照参考

> 本文件由 `openHiTLS-bugAnalysis` SKILL 按需读取，避免每次运行都重新探索代码仓结构。
> 仓库快照日期：2026-08-29。如任一仓库结构发生重大变化，需重新生成本文件。

---

## 1. 顶层布局对照

| 功能领域 | OpenSSL 路径（cwd 仓库根） | openHiTLS 路径（`output/openhitls/`） |
|---|---|---|
| 加密算法原语 | `crypto/<alg>/` | `crypto/<alg>/` |
| EVP 抽象层 | `crypto/evp/` | `crypto/eal/src/`（`eal_*.c`） |
| EVP 初始化 | `crypto/init.c` 等 | `crypto/ealinit/` |
| Provider 机制 | `providers/` | `crypto/provider/`（`src/default/`, `src/mgr/`, `src/cmvp/`） |
| ASN.1 编解码 | `crypto/asn1/` | `bsl/asn1/src/`（`bsl_asn1.c`）+ `codecs/src/` |
| 对象/OID | `crypto/objects/` | `bsl/obj/src/`（`bsl_obj.c`, `bsl_cid_op.c`） |
| 错误处理 | `crypto/err/` | `bsl/err/src/`（`err.c`, `avl.c`） |
| BIO | `crypto/bio/` | `bsl/`（分散：`base64/`, `buffer/`, `print/`, `sal/`, `uio/` 等） |
| Base64 | `crypto/bio/` 内 | `bsl/base64/` |
| Buffer | `crypto/buffer/` | `bsl/buffer/` |
| 配置解析 | `crypto/conf/` | `bsl/conf/src/`（`bsl_conf.c`, `bsl_conf_def.c`） |
| PEM | `crypto/pem/` | `bsl/pem/src/`（`bsl_pem.c`） |
| 日志 | `crypto/trace.c` 等 | `bsl/log/` |
| 链表 | `crypto/stack/`, `lhash/` | `bsl/list/` |
| UI | `crypto/ui/` | `bsl/ui/` |
| 参数 | `crypto/params.c` 等 | `bsl/params/` |
| TLV | — | `bsl/tlv/` |
| HASH | `crypto/` 各 hash | `bsl/hash/` |
| 版本 | `crypto/cversion.c` | `bsl/version/` |
| 初始化入口 | `crypto/init.c` | `bsl/init/` |
| X.509 证书 | `crypto/x509/` | `pki/x509_cert/`（`hitls_x509_cert.c`） |
| X.509 公共/扩展 | `crypto/x509/`（v3_*.c） | `pki/x509_common/`（`hitls_x509_common.c`, `hitls_x509_ext.c`, `hitls_x509_attrs.c`, `hitls_x509_ctrl.c`, `hitls_x509_util.c`） |
| X.509 校验/Store | `crypto/x509/`（`x509_vfy.c`, `x509_lu.c`, `x509_vpm.c`） | `pki/x509_verify/`（`hitls_x509_verify.c`, `hitls_x509_store.c`） |
| CRL | `crypto/x509/`（`x_crl.c`, `t_crl.c`） | `pki/x509_crl/` |
| CSR | `crypto/x509/`（`x_req.c`, `t_req.c`） | `pki/x509_csr/` |
| OCSP | `crypto/ocsp/`（`ocsp_cl.c`, `ocsp_vfy.c`, `ocsp_lib.c` ...） | **无独立目录**，按符号搜索 `pki/x509_verify/`、`bsl/obj/`；多见于不存在 |
| CMS | `crypto/cms/`（`cms_*.c`） | `pki/cms/src/`（`hitls_cms_common.c`, `hitls_cms_signdata.c`, `hitls_cms_pqc.c`, `hitls_cms_util.c`） |
| PKCS#7 | `crypto/pkcs7/` | 并入 `pki/cms/` |
| PKCS#12 | `crypto/pkcs12/` | `pki/pkcs12/` |
| 打印 | `crypto/x509/t_*.c` | `pki/print/` |
| RAND | `crypto/rand/` | `crypto/drbg/`（DRBG）+ `crypto/entropy/`（熵源）+ `crypto/eal/src/eal_rand*.c` |
| KDF | `crypto/kdf/`（仅 `kdf_err.c`，实现在 `providers/implementations/kdfs/`） | `crypto/kdf/`, `crypto/hkdf/`, `crypto/pbkdf2/`, `crypto/scrypt/` |
| HMAC | `crypto/hmac/` | `crypto/hmac/` |
| CMAC/GMAC | `crypto/cmac/`, `crypto/gmac`（无） | `crypto/cmac/`, `crypto/gmac/` |
| HPKE | `crypto/hpke/` | `crypto/hpke/` |
| TLS 协议栈 | `ssl/` | `tls/` |
| TLS 状态机 | `ssl/statem/` | `tls/handshake/`（`common/`, `recv/`, `send/`, `parse/`, `pack/`, `reass/`, `cookie/`, `sm/`） |
| TLS 记录层 | `ssl/record/` | `tls/record/src/`（`rec_*.c`, `record.c`） |
| TLS 证书 | `ssl/ssl_cert.c` | `tls/cert/`（`cert_adapt/`, `hitls_x509_adapt/`） |
| TLS 配置 | `ssl/ssl_conf.c`, `ssl/t1_lib.c` | `tls/config/src/`（`config_*.c`, `cipher_suite.c`） |
| TLS 会话 | `ssl/ssl_sess.c` | 搜索 `tls/`（`hitls_session.h` 在 `include/tls/`） |
| TLS 密码套件 | `ssl/ssl_ciph.c` | `tls/config/src/cipher_suite.c` |
| TLS 方法 | `ssl/methods.c`, `ssl/ssl_lib.c` | `tls/`（搜索 `hitls.h`） |
| TLS 加密 | `ssl/t1_enc.c`, `ssl/tls13_enc.c` | `tls/crypt/` |
| TLS 应用数据 | `ssl/`（`ssl_lib.c`） | `tls/app/` |
| TLS 警报 | `ssl/d1_msg.c` 等 | `tls/alert/` |
| ChangeCipherSpec | `ssl/` | `tls/ccs/` |
| TLS 特性 | `ssl/ssl_utst.c` 等 | `tls/feature/` |
| TLS CM | — | `tls/cm/` |
| QUIC | `ssl/quic/`（49 文件）, `ssl/rio/` | **基本未实现**，搜索 `tls/`；多数判定 `NOT_APPLICABLE` |
| DTLS | `ssl/d1_*.c` | `tls/`（`hs_dtls_timer.c`, `rec_*` 中含 DTLS） |
| 公共头文件 | `include/openssl/` | 按模块分散：`include/crypto/`, `include/pki/`, `include/tls/`, `include/bsl/`, `include/auth/` |
| 内部头文件 | `include/internal/` | 各模块 `*/include/` 或 `*/src/*_local.h` |
| Provider 实现 | `providers/implementations/` | 直接在各 `crypto/<alg>/`；默认 provider 注册在 `crypto/provider/src/default/crypt_default_*.c` |
| ENGINE | `engines/`, `crypto/engine/` | 无（`NOT_APPLICABLE`） |
| 应用/CLI | `apps/` | `apps/` |
| 测试 | `test/` | `testcode/` |
| 构建 | `Configure`, `Configurations/`, `build.info` | `CMakeLists.txt`（各模块）+ 顶层 `CMakeLists.txt` |
| 文档 | `doc/` | `docs/` |

---

## 2. OpenSSL 详细结构（仓库根 = cwd）

### 2.1 `crypto/` 关键子目录与文件

| 子目录/文件 | 内容 |
|---|---|
| `evp/` | EVP 抽象层：`evp_lib.c`（cipher 参数 ASN1）、`evp_enc.c`、`evp_pkey.c`、`p_lib.c`、`p_sign.c`/`p_verify.c`、`encode.c`、`evp_fetch.c`、`mac_lib.c`、`kdf_lib.c`、`kem.c`、`signature.c`、`keymgmt_*`、`pmeth_*`、`e_*.c`（传统 cipher 实现）、`m_sigver.c`、`p5_crpt*.c` |
| `asn1/` | ASN.1：`a_int.c`、`a_object.c`、`a_time.c`（`a_gentm.c`/`a_utctm.c`）、`a_bitstr.c`、`a_strex.c`、`tasn_dec.c`/`tasn_enc.c`/`tasn_new.c`、`asn1_parse.c`、`ameth_lib.c`、`evp_asn1.c`、`bio_asn1.c`、`bio_ndef.c`、`p5_pbe*.c`、`x_*.c` |
| `x509/` | X.509：`x_x509.c`、`x_crl.c`、`x_req.c`、`x_pubkey.c`、`x509_vfy.c`（验证）、`x509_lu.c`（查找）、`x509_cmp.c`、`x509_vpm.c`（验证参数）、`x509_ext.c`、`x509_set.c`、`by_dir.c`/`by_file.c`/`by_store.c`、`v3_*.c`（扩展：SAN、AKID、SKID、策略、约束等）、`t_x509.c`/`t_crl.c`/`t_req.c`、`pcy_*.c`（策略树） |
| `ocsp/` | OCSP：`ocsp_cl.c`（客户端/`OCSP_check_validity`）、`ocsp_vfy.c`（验证）、`ocsp_lib.c`、`ocsp_ext.c`、`ocsp_srv.c`、`ocsp_asn.c`、`ocsp_http.c`、`v3_ocsp.c` |
| `cms/` | CMS：`cms_env.c`、`cms_enc.c`（解密）、`cms_sd.c`（签名）、`cms_pwri.c`（PWRI-KEK）、`cms_kari.c`（密钥协商）、`cms_lib.c`、`cms_att.c`、`cms_smime.c`、`cms_ess.c`、`cms_dh.c`/`cms_ec.c`/`cms_rsa.c` |
| `pkcs7/` | `pk7_doit.c`、`pk7_smime.c`、`pk7_mime.c`、`pk7_lib.c` |
| `pkcs12/` | `p12_kiss.c`、`p12_crt.c`、`p12_decr.c`、`p12_mutl.c`、`p12_sbag.c`、`p12_key.c` |
| `rand/` | `rand_lib.c`、`rand_meth.c`、`rand_pool.c`、`rand_uniform.c` |
| `kdf/` | 仅 `kdf_err.c`；实现位于 `providers/implementations/kdfs/` |
| `hmac/` | HMAC 实现 |
| `modes/` | `gcm128.c`、`ccm128.c`、`cbc128.c`、`ctr128.c`、`xts128.c`、`ofb128.c` 等 |
| `ec/` | EC：`ec_lib.c`、`ec_key.c`、`ec_mult.c`、`ec_curve.c`、`ecdsa_ossl.c`、`ecdh_ossl.c`、`eck_prn.c` |
| `rsa/` | `rsa_ossl.c`、`rsa_sign.c`、`rsa_pk1.c`、`rsa_oaep.c`、`rsa_pss.c`、`rsa_crpt.c`、`rsa_gen.c`、`rsa_x931.c` |
| `dh/` | `dh_gen.c`、`dh_check.c`、`dh_key.c`、`dh_rfc5114.c` |
| `dsa/` | `dsa_ossl.c`、`dsa_key.c`、`dsa_sign.c` |
| `store/` | `store_lib.c`、`store_meth.c`、`store_register.c`、`store_result.c` |
| `objects/` | `obj_dat.c`、`obj_lib.c`、`o_names.c` |
| `err/` | `err.c`、`err_all.c`、`err_blocks.c`、`err_prn.c` |
| `bio/` | `bio_lib.c`、`bio_meth.c`、`bss_*.c`、`bf_buff.c`、`bf_lbuf.c`、`b64_*.c` |
| `conf/` | `conf_lib.c`、`conf_mod.c`、`conf_sap.c`、`conf_def.c` |
| `pem/` | `pem_lib.c`、`pem_sign.c`、`pem_seal.c`、`pem_pkey.c`、`pem_x509.c` |
| `aes/`, `aria/`, `camellia/`, `chacha/`, `des/`, `sm4/` | 对称密码 |
| `sha/`, `md5/`, `sm3/`, `blake2/` | 哈希 |
| `ml_kem/`, `ml_dsa/`, `slh_dsa/` | 后量子算法 |
| `sm2/` | SM2 |
| `encode_decode/` | `decode_der.c`、`encode_der.c`、`decoder_pkey.c`、`encoder_pkey.c` |
| `property/` | `property.c`、`defn_cache.c`、`query.c`、`parse.c` |
| `comp/` | 压缩 |
| `http/` | HTTP 客户端 |
| `ts/` | 时间戳 |
| `ct/` | Certificate Transparency |
| `cmp/`, `crmf/`, `ess/` | CMP/CRMF/ESS |
| `async/`, `thread/` | 异步/线程 |
| `ui/` | 用户交互 |
| `dso/`, `engine/` | 动态加载/引擎 |

### 2.2 `ssl/` 详细

| 文件/子目录 | 内容 |
|---|---|
| `ssl_lib.c` | SSL_CTX/SSL 主体、`SSL_new`/`SSL_CTX_new`、选项 |
| `ssl_conf.c` | SSL 配置 |
| `ssl_sess.c` | 会话 |
| `ssl_ciph.c` | 密码套件选择 |
| `ssl_cert.c` | 证书链 |
| `t1_lib.c` | TLS 扩展主体 |
| `t1_enc.c`, `tls13_enc.c` | 密钥派生/加解密 |
| `methods.c` | TLS/DTLS 方法 |
| `d1_lib.c`, `d1_msg.c`, `d1_srtp.c` | DTLS |
| `ssl_asn1.c` | 会话 ASN1 |
| `ssl_cert_comp.c` | 证书压缩 |
| `statem/` | 状态机：`statem.c`、`statem_clnt.c`、`statem_srvr.c`、`statem_lib.c`、`statem_dtls.c`、`extensions.c`/`extensions_clnt.c`/`extensions_srvr.c`/`extensions_cust.c` |
| `record/` | 记录层 |
| `quic/` | QUIC（49 文件） |
| `rio/` | QUIC I/O |

### 2.3 `providers/` 详细

| 路径 | 内容 |
|---|---|
| `defltprov.c`, `legacyprov.c`, `baseprov.c`, `nullprov.c` | provider 注册 |
| `implementations/ciphers/` | cipher provider 实现 |
| `implementations/digests/` | digest provider 实现 |
| `implementations/kdfs/` | KDF 实现（含 HKDF、PBKDF2、scrypt 等） |
| `implementations/macs/` | MAC |
| `implementations/keymgmt/` | KEYMGMT |
| `implementations/signature/` | 签名 |
| `implementations/asymciphers/` | 非对称加解密 |
| `implementations/kem/` | KEM |
| `implementations/exchange/` | 密钥交换 |
| `implementations/rands/` | 随机 provider |
| `implementations/encode_decode/` | 编解码 provider |
| `implementations/storemgmt/`, `skeymgmt/` | store/skeymgmt |
| `common/` | provider 公共代码 |

### 2.4 `include/openssl/` 公共头（节选）

`aes.h`、`asn1.h.in`、`bio.h.in`、`bn.h`、`buffer.h`、`cms.h.in`、`crypto.h.in`、`decoder.h`、`dh.h`、`dsa.h`、`ec.h`、`ecdh.h`、`ecdsa.h`、`encoder.h`、`err.h`、`evp.h`（核心）、`hmac.h`、`kdf.h`、`mac.h`、`objects.h`、`ocsp.h`、`pem.h`、`pkcs7.h`、`pkcs12.h`、`rand.h`、`rsa.h`、`ssl.h`、`store.h`、`x509.h`、`x509v3.h` 等。`*err.h` 为错误码定义。

---

## 3. openHiTLS 详细结构（`output/openhitls/`）

### 3.1 顶层

```
apps/        - CLI 工具
auth/        - 认证相关
bsl/         - 基础支撑库（对应 OpenSSL crypto 的 BIO/err/obj/pem/conf/asn1/base64/buffer 等）
codecs/      - 编解码（DER 解码：decode.c, decode_chain.c）
config/      - 平台配置
crypto/      - 加密算法原语 + EAL + provider
docs/        - 文档
include/     - 公共头（按模块：auth/ bsl/ crypto/ pki/ tls/）
pki/         - PKI（X.509、CMS、PKCS12、打印）
tls/         - TLS 协议栈
testcode/    - 测试
```

### 3.2 `crypto/` 子目录

**算法原语**（多含 `include/` + `src/`）：

| 子目录 | 对应 OpenSSL |
|---|---|
| `aes/` | `crypto/aes/` |
| `blake2/` | `crypto/blake2/` |
| `bn/` | `crypto/bn/` |
| `chacha20/` | `crypto/chacha/` |
| `cmac/` | `crypto/cmac/` |
| `curve25519/` | `crypto/ec/`（curve25519 部分） |
| `dh/` | `crypto/dh/` |
| `drbg/` | `crypto/rand/`（DRBG 部分） |
| `dsa/` | `crypto/dsa/` |
| `eal/` | `crypto/evp/`（见下） |
| `ealinit/` | EVP 初始化入口 |
| `ecc/`, `ecdh/`, `ecdsa/`, `sm2/` | `crypto/ec/`（拆分） |
| `elgamal/` | — |
| `entropy/` | 熵源（对应 OpenSSL rand/entropy） |
| `frodokem/`, `mceliece/`, `mlkem/`, `mldsa/`, `hybridkem/` | 后量子 |
| `gmac/` | GMAC |
| `hbs/` | HBS（哈希基签名） |
| `hkdf/`, `kdf/`, `pbkdf2/`, `scrypt/` | KDF |
| `hmac/` | `crypto/hmac/` |
| `hpke/` | `crypto/hpke/` |
| `md5/`, `sha1/`, `sha2/`, `sha3/`, `sm3/`, `siphash/` | 哈希 |
| `modes/` | `crypto/modes/` |
| `paillier/` | — |
| `provider/` | `providers/`（见下） |
| `rsa/` | `crypto/rsa/` |
| `sm4/`, `sm9/` | 国密 |
| `util/` | 工具 |
| `codecsdata/`, `codecskey/`, `composite/` | 编解码数据/复合 |
| `include/` | `crypto` 内部头 |

### 3.3 `crypto/eal/src/` —— EVP 抽象层（对应 OpenSSL `crypto/evp/`）

| 文件 | 对应 OpenSSL 文件 | 关注符号 |
|---|---|---|
| `eal_cipher.c` | `evp_enc.c`, `e_aes.c` 等 | cipher 加解密 |
| `eal_cipher_method.c` | cipher method 注册 | |
| `eal_md.c` | `digest.c`, `m_*.c` | digest |
| `eal_md_method.c` | | |
| `eal_mac.c` | `mac_lib.c` | MAC |
| `eal_kdf.c` | `kdf_lib.c` | KDF |
| `eal_pkey_sign.c` | `p_sign.c`, `p_verify.c` | 签名/验签 |
| `eal_pkey_crypt.c` | `p_dec.c`, `p_enc.c`, `p_lib.c` | 非对称加解密 |
| `eal_pkey_gen.c` | `pkey_gen` | 密钥生成 |
| `eal_pkey_kem.c` | `kem.c` | KEM |
| `eal_pkey_params.c` | | 密钥参数 |
| `eal_pkey_computesharekey.c` | | 密钥协商 |
| `eal_pkey_method.c` | `pmeth_*` | 算法方法 |
| `eal_keymgmt_util.c` | `keymgmt_*` | KEYMGMT |
| `eal_rand.c` | `rand_lib.c` | 随机 |
| `eal_rand_method.c` | `rand_meth.c` | |
| `eal_entropy.c`, `eal_entropyPool.c`, `eal_entropy_ecf.c` | 熵池 | |
| `eal_common.c` | `evp_lib.c` 公共 | 通用工具 |

### 3.4 `crypto/provider/` —— Provider 机制

| 路径 | 对应 OpenSSL |
|---|---|
| `src/default/crypt_default_provider.c` | `defltprov.c` |
| `src/default/crypt_default_cipher.c` | cipher provider 注册 |
| `src/default/crypt_default_md.c` | digest 注册 |
| `src/default/crypt_default_mac.c` | MAC 注册 |
| `src/default/crypt_default_kdf.c` | KDF 注册 |
| `src/default/crypt_default_sign.c` | 签名注册 |
| `src/default/crypt_default_kem.c` | KEM 注册 |
| `src/default/crypt_default_keymgmt.c` | KEYMGMT 注册 |
| `src/default/crypt_default_keyexch.c` | 密钥交换注册 |
| `src/default/crypt_default_pkeycipher.c` | 非对称加解密注册 |
| `src/default/crypt_default_rand.c` | 随机注册 |
| `src/default/crypt_default_decode.c` | 解码注册 |
| `src/mgr/crypt_provider*.c` | provider 管理核心 |
| `src/cmvp/` | CMVP 合规 |

### 3.5 `bsl/` —— 基础支撑库

| 子目录 | 对应 OpenSSL | 关键文件 |
|---|---|---|
| `asn1/` | `crypto/asn1/` | `bsl_asn1.c` |
| `base64/` | `crypto/bio/b64_*.c` | |
| `buffer/` | `crypto/buffer/` | |
| `conf/` | `crypto/conf/` | `bsl_conf.c`, `bsl_conf_def.c` |
| `err/` | `crypto/err/` | `err.c`, `avl.c` |
| `hash/` | 通用哈希 | |
| `init/` | `crypto/init.c` | |
| `list/` | `crypto/stack/`, `lhash/` | |
| `log/` | `crypto/trace.c` | |
| `obj/` | `crypto/objects/` | `bsl_obj.c`, `bsl_cid_op.c` |
| `params/` | `crypto/params.c` | |
| `pem/` | `crypto/pem/` | `bsl_pem.c` |
| `print/` | `crypto/bio/b_print.c` 等 | |
| `sal/` | OS 抽象层 | |
| `tlv/` | TLV 解析 | |
| `ui/` | `crypto/ui/` | |
| `uio/` | BIO 风格 I/O | |
| `version/` | `crypto/cversion.c` | |

### 3.6 `pki/` —— PKI

| 子目录 | 对应 OpenSSL | 关键文件 |
|---|---|---|
| `x509_cert/` | `crypto/x509/`（x_x509.c, x509_set.c） | `hitls_x509_cert.c` |
| `x509_common/` | `crypto/x509/`（v3_*.c, x509_att.c, x509_cmp.c） | `hitls_x509_common.c`, `hitls_x509_ext.c`, `hitls_x509_attrs.c`, `hitls_x509_ctrl.c`, `hitls_x509_util.c` |
| `x509_verify/` | `crypto/x509/`（x509_vfy.c, x509_lu.c, x509_vpm.c, by_dir/file/store.c） | `hitls_x509_verify.c`, `hitls_x509_store.c` |
| `x509_crl/` | `crypto/x509/`（x_crl.c, t_crl.c） | |
| `x509_csr/` | `crypto/x509/`（x_req.c, t_req.c） | |
| `cms/` | `crypto/cms/` | `hitls_cms_common.c`, `hitls_cms_signdata.c`, `hitls_cms_pqc.c`, `hitls_cms_util.c` |
| `pkcs12/` | `crypto/pkcs12/` | |
| `print/` | `crypto/x509/t_*.c` | |

### 3.7 `tls/` —— TLS 协议栈（对应 OpenSSL `ssl/`）

| 子目录 | 对应 OpenSSL | 关键文件 |
|---|---|---|
| `handshake/` | `ssl/statem/` | 状态机 |
| `handshake/common/src/` | `statem_lib.c`, `statem.c` | `hs_common.c`, `hs_cert.c`, `hs_kx.c`, `hs_verify.c`, `tls13key.c`, `transcript_hash.c`, `hs_dtls_timer.c` |
| `handshake/recv/`, `send/`, `parse/`, `pack/`, `reass/`, `cookie/`, `sm/` | `statem_clnt.c`, `statem_srvr.c`, `extensions_*` | 收发/解析/打包/重组 |
| `record/` | `ssl/record/` | `rec_*.c`（`rec_conn.c`, `rec_read.c`, `rec_write.c`, `rec_crypto.c`, `rec_crypto_aead.c`, `rec_crypto_cbc.c`, `rec_alert.c`, `rec_anti_replay.c`, `rec_retransmit.c`, `record.c`） |
| `cert/` | `ssl/ssl_cert.c` | `cert_adapt/`, `hitls_x509_adapt/` |
| `config/` | `ssl/ssl_conf.c`, `ssl/t1_lib.c`, `ssl_ciph.c` | `config.c`, `config_tls.c`, `config_tls13.c`, `config_dtls.c`, `config_cert.c`, `config_check.c`, `config_default.c`, `config_group.c`, `config_sign.c`, `config_feature.c`, `cipher_suite.c` |
| `crypt/` | `ssl/t1_enc.c`, `ssl/tls13_enc.c` | 密钥派生/记录加密 |
| `app/` | `ssl/ssl_lib.c`（应用数据） | 应用层 |
| `alert/` | `ssl/d1_msg.c` 等 | 警报 |
| `ccs/` | `ssl/`（CCS） | ChangeCipherSpec |
| `cm/` | — | 连接管理 |
| `feature/` | `ssl/ssl_utst.c` | 特性 |
| `include/` | TLS 内部头 | |

### 3.8 公共头 `include/`

| 子目录 | 对应 OpenSSL | 内容 |
|---|---|---|
| `crypto/` | `include/openssl/`（crypto 部分） | `crypt_eal_cipher.h`, `crypt_eal_md.h`, `crypt_eal_mac.h`, `crypt_eal_kdf.h`, `crypt_eal_pkey.h`, `crypt_eal_rand.h`, `crypt_eal_entropy.h`, `crypt_eal_hpke.h`, `crypt_eal_init.h`, `crypt_eal_provider.h`, `crypt_eal_codecs.h`, `crypt_eal_cmvp.h`, `crypt_algid.h`, `crypt_errno.h`, `crypt_params_key.h`, `crypt_types.h`, `crypt_eal_implprovider.h` |
| `pki/` | `include/openssl/x509.h`, `cms.h`, `pkcs12.h` 等 | `hitls_pki_cert.h`, `hitls_pki_cms.h`, `hitls_pki_crl.h`, `hitls_pki_csr.h`, `hitls_pki_pkcs12.h`, `hitls_pki_x509.h`, `hitls_pki_params.h`, `hitls_pki_types.h`, `hitls_pki_utils.h`, `hitls_pki_errno.h` |
| `tls/` | `include/openssl/ssl.h` 等 | `hitls.h`（主头）, `hitls_type.h`, `hitls_config.h`, `hitls_cert.h`, `hitls_session.h`, `hitls_alpn.h`, `hitls_sni.h`, `hitls_security.h`, `hitls_error.h`, `hitls_psk.h`, `hitls_cookie.h`, `hitls_dtls_cid.h`, `hitls_quic_tls.h`, `hitls_cert_init.h`, `hitls_cert_type.h`, `hitls_crypt_init.h`, `hitls_crypt_type.h`, `hitls_debug.h`, `hitls_custom_extensions.h` |
| `bsl/` | `include/openssl/`（基础） | `bsl_types.h`, `bsl_obj.h`, `bsl_err.h`, `bsl_errno.h`, `bsl_asn1.h`, `bsl_base64.h`, `bsl_init.h`, `bsl_params.h`, `bsl_sal.h`, `bsl_log.h`, `bsl_list.h`, `bsl_ui.h`, `bsl_uio.h`, `bsl_version.h` |
| `auth/` | — | 认证相关 |

---

## 4. 命名约定对照

| 概念 | OpenSSL | openHiTLS |
|---|---|---|
| 抽象层前缀 | `EVP_` | `EVP_`（保留）或 `CRYPT_`（EAL 内部） |
| 算法实现文件 | `e_aes.c`, `m_sha1.c` | `<alg>/src/`（如 `aes/src/`） |
| 错误码前缀 | `ERR_R_*`, `<lib>_R_*` | `BSL_ERR_*`, `CRYPT_ERRNO_*`, `HITLS_*` |
| 对象/OID | `OBJ_*`, `NID_*` | `BSL_CID_*`, `bsl_obj_*` |
| 公共头宏 | `OPENSSL_*` | `HITLS_*`, `BSL_*` |
| TLS API | `SSL_*`, `TLS_*` | `HITLS_*`（`hitls.h`） |
| X.509 API | `X509_*` | `HITLS_X509_*`（`hitls_pki_x509.h`） |
| CMS API | `CMS_*` | `HITLS_CMS_*`（`hitls_pki_cms.h`） |
| PKCS12 API | `PKCS12_*` | `HITLS_PKCS12_*` |
| 配置 | `CONF_*` | `BSL_CONF_*` |
| PEM | `PEM_*` | `BSL_PEM_*` |
| BIO | `BIO_*` | `BSL_UIO_*`（uio 层） |
| 文件前缀 | `evp_`, `x509_`, `ssl_` | `eal_`, `hitls_x509_`, `hitls_` |
| 内部头 | `*_local.h` | `*_local.h`（沿用） |

> **搜索建议**：先按 OpenSSL 符号名（函数/宏）grep openHiTLS；若未命中，尝试去掉/替换前缀（`EVP_`→`CRYPT_`/`EAL`，`X509_`→`HITLS_X509_`，`SSL_`→`HITLS_`），再按功能目录定位。

---

## 5. 功能缺失对照（openHiTLS 大概率未实现）

| OpenSSL 功能 | openHiTLS 状态 |
|---|---|
| QUIC（`ssl/quic/`） | 基本未实现 → 默认判 `NOT_APPLICABLE` |
| OCSP 完整客户端（`OCSP_check_validity` 等） | 未发现独立实现 → 按符号搜索确认 |
| ENGINE（`crypto/engine/`, `engines/`） | 未实现 → `NOT_APPLICABLE` |
| CT（Certificate Transparency） | 未发现 |
| CMP/CRMF/ESS | 未发现 |
| TS（时间戳） | 未发现 |
| HTTP 客户端（`crypto/http/`） | 未发现独立模块 |
| SRP | 未发现 |
| STORE（`crypto/store/`） | 未发现独立模块 |
| Provider 编解码独立模块（`providers/implementations/encode_decode/`） | 由 `codecs/` + `crypt_default_decode.c` 替代 |

> 遇到上述功能时，先按符号搜索确认（避免误判），确认缺失后记 `NOT_APPLICABLE` 并注明搜索过的符号。

---

## 6. 使用方式（供 SKILL 读取）

1. 本文件位于 `C:\Users\huawei\.config\opencode\skills\openHiTLS-bugAnalysis\CODE_STRUCTURE.md`。
2. SKILL 在 Step 4（定位 openHiTLS 对应代码）前读取本文件第 1 节对照表，直接得到候选目录。
3. 命中后用 Grep/Read 验证具体符号；若对照表无命中项，再回退到逐目录探索。
4. 第 5 节列出的大概率缺失功能，可加速 `NOT_APPLICABLE` 判定，但仍需一次符号搜索确认。
