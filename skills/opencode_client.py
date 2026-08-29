#!/usr/bin/env python3
"""
通过 opencode server 的 HTTP API 调用指定 provider/model 进行对话。

前置：
  1. 全局/项目 opencode.json 已配置好 provider（当前已配 HWai 火山网关）
  2. 启动 server:  opencode serve --port 4096
  3. 依赖:  pip install requests

用法示例：
  # 交互式（默认 provider=HWai model=glm-5.2）
  python opencode_client.py
  # 指定模型
  python opencode_client.py --provider HWai --model deepseek-v4-pro
  # 一次性提问
  python opencode_client.py --prompt "用一句话解释什么是快排"
  # server 设了密码时
  python opencode_client.py --password secret
"""
import argparse
import sys

import requests


class OpencodeClient:
    def __init__(self, base_url="http://localhost:4096", username="opencode", password=None):
        self.base = base_url.rstrip("/")
        self.auth = (username, password) if password else None

    def health(self):
        r = requests.get(f"{self.base}/global/health", auth=self.auth, timeout=10)
        r.raise_for_status()
        return r.json()

    def create_session(self, title="py-client"):
        r = requests.post(
            f"{self.base}/session",
            json={"title": title} if title else {},
            auth=self.auth,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def send_message(self, session_id, text, provider_id, model_id, timeout=300):
        body = {
            "model": {"providerID": provider_id, "modelID": model_id},
            "parts": [{"type": "text", "text": text}],
        }
        r = requests.post(
            f"{self.base}/session/{session_id}/message",
            json=body,
            auth=self.auth,
            timeout=timeout,
        )
        r.raise_for_status()
        return r.json()

    def run_command(self, session_id, command, arguments="", provider_id=None, model_id=None, timeout=600):
        """执行 skill / slash command。command 为 skill 名，如 generate-html。"""
        body = {"command": command, "arguments": arguments}
        if provider_id and model_id:
            body["model"] = {"providerID": provider_id, "modelID": model_id}
        r = requests.post(
            f"{self.base}/session/{session_id}/command",
            json=body,
            auth=self.auth,
            timeout=timeout,
        )
        r.raise_for_status()
        return r.json()

    def list_commands(self):
        r = requests.get(f"{self.base}/command", auth=self.auth, timeout=10)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def extract_text(resp):
        texts = [p.get("text", "") for p in resp.get("parts", []) if p.get("type") == "text"]
        return "\n".join(texts).strip()


def main():
    ap = argparse.ArgumentParser(description="opencode server HTTP client")
    ap.add_argument("--url", default="http://localhost:4096", help="server base url")
    ap.add_argument("--provider", default="HWai", help="provider id (见 opencode.json)")
    ap.add_argument("--model", default="glm-5.2", help="model id (见 opencode.json)")
    ap.add_argument("--prompt", help="一次性提问；省略则进入交互模式")
    ap.add_argument("--skill", help="显式执行某 skill（如 generate-html），配合 --args 传参")
    ap.add_argument("--args", default="", help="传给 skill 的参数")
    ap.add_argument("--list-commands", action="store_true", help="列出所有可用 skill/command")
    ap.add_argument("--password", help="OPENCODE_SERVER_PASSWORD（设了密码时填）")
    ap.add_argument("--timeout", type=int, default=300, help="单次请求超时秒数")
    args = ap.parse_args()

    client = OpencodeClient(args.url, password=args.password)

    try:
        h = client.health()
    except Exception as e:
        print(f"[error] 无法连接 {args.url}: {e}", file=sys.stderr)
        print("请先启动:  opencode serve --port 4096", file=sys.stderr)
        sys.exit(1)
    print(f"[ok] server v{h.get('version')} @ {args.url}")

    if args.list_commands:
        cmds = client.list_commands()
        print(f"可用 skill/command（共 {len(cmds)} 个）:")
        for c in cmds:
            print(f"  {c['name']:<28} {c.get('description','')}")
        return

    session = client.create_session()
    sid = session["id"]
    print(f"[ok] session={sid}  provider={args.provider}  model={args.model}\n")

    if args.skill:
        resp = client.run_command(sid, args.skill, args.args, args.provider, args.model, args.timeout)
        print(OpencodeClient.extract_text(resp))
        return

    if args.prompt:
        resp = client.send_message(sid, args.prompt, args.provider, args.model, args.timeout)
        print(OpencodeClient.extract_text(resp))
        return

    print("交互模式：输入消息回车发送，:q 退出，:new 新建会话\n")
    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user:
            continue
        if user == ":q":
            break
        if user == ":new":
            session = client.create_session()
            sid = session["id"]
            print(f"[ok] 新会话 {sid}\n")
            continue
        resp = client.send_message(sid, user, args.provider, args.model, args.timeout)
        print(f"ai> {OpencodeClient.extract_text(resp)}\n")

    print("bye.")


if __name__ == "__main__":
    main()
