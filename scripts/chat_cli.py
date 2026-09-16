"""Interactive HTTP client sharing the authenticated application path."""

import argparse
import json
from pathlib import Path
import uuid
import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--token-file", default=".runtime/demo-tokens.json")
    parser.add_argument("--identity", default="alice")
    args = parser.parse_args()
    conv = None
    last = None
    print("SupportFlow：/new 新会话，/retry 重试原请求，/quit 退出。")
    with httpx.Client(timeout=200) as client:
        while True:
            try:
                message = input("你：").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if message == "/quit":
                break
            if message == "/new":
                conv = None
                last = None
                print("已切换新会话。")
                continue
            if not message:
                continue
            if message == "/retry":
                if last is None:
                    print("没有可重试的请求。")
                    continue
            else:
                last = {
                    "message": message,
                    "conv_id": conv,
                    "request_id": uuid.uuid4().hex,
                }
            try:
                token = json.loads(Path(args.token_file).read_text(encoding="utf-8"))[
                    args.identity
                ]
                r = client.post(
                    args.url.rstrip("/") + "/chat",
                    json=last,
                    headers={"Authorization": "Bearer " + token},
                )
                r.raise_for_status()
                body = r.json()
                conv = body["conv_id"]
                print("客服：" + body["response"])
                print(
                    "Agent:",
                    ",".join(body["agents"]),
                    "工具:",
                    ",".join(body["tools_used"]),
                    "状态:",
                    body["status"],
                )
            except Exception as exc:
                print(
                    "请求失败：", type(exc).__name__, "；可用 /retry 保持原幂等键重试。"
                )


if __name__ == "__main__":
    main()
