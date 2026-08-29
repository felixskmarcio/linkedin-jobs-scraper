#!/usr/bin/env python3
"""
Inject LinkedIn cookies into a headless Chrome via CDP (logged-in mode).

⚠️ FIXED vs original version: cookies are injected AFTER any clearing —
the original called Network.clearBrowserCookies() after setCookie, wiping
everything that was just injected.

Requires:
    - Chrome running with: --remote-debugging-port=9222 --remote-allow-origins=*
    - pip install websocket-client
    - cookies JSON exported via Cookie-Editor (see docs/COOKIES.md)

Usage:
    python3 inject_cookies.py linkedin_cookies.json "https://www.linkedin.com/feed/"
"""
import json
import sys
import time
import urllib.request

import websocket

CDP_URL = "http://127.0.0.1:9222"

SAME_SITE_MAP = {"no_restriction": "None", "lax": "Lax", "strict": "Strict"}


def list_targets():
    with urllib.request.urlopen(f"{CDP_URL}/json/list", timeout=10) as r:
        return json.loads(r.read())


def send(ws, method, params=None, _id=[1]):
    msg = {"id": _id[0], "method": method, "params": params or {}}
    _id[0] += 1
    ws.send(json.dumps(msg))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg["id"]:
            return resp.get("result", {})


def cookie_params(c: dict) -> dict:
    params = {
        "name": c["name"],
        "value": c["value"],
        "domain": c.get("domain", ".linkedin.com"),
        "path": c.get("path", "/"),
        "secure": c.get("secure", True),
        "httpOnly": c.get("httpOnly", False),
    }
    ss = SAME_SITE_MAP.get(c.get("sameSite"), c.get("sameSite"))
    if ss in ("Lax", "Strict", "None"):
        params["sameSite"] = ss
    if c.get("expirationDate"):
        params["expires"] = int(c["expirationDate"])
    return params


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cookies_path = sys.argv[1]
    target_url = sys.argv[2] if len(sys.argv) > 2 else "https://www.linkedin.com/feed/"

    with open(cookies_path, encoding="utf-8") as f:
        cookies = json.load(f)
    print(f"Loaded {len(cookies)} cookies from {cookies_path}")

    pages = [t for t in list_targets() if t["type"] == "page"]
    if not pages:
        print("ERROR: no page target. Is Chrome running with --remote-debugging-port=9222?")
        return 1

    ws = websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=15)
    send(ws, "Network.enable")

    # Clear FIRST, then inject (order matters!)
    send(ws, "Network.clearBrowserCookies")
    ok, fail = 0, 0
    for c in cookies:
        r = send(ws, "Network.setCookie", cookie_params(c))
        if r.get("success"):
            ok += 1
        else:
            fail += 1
            print(f"  FAILED: {c['name']}")
    print(f"Injected: {ok} OK, {fail} failed")

    # Verify critical cookies persisted
    stored = send(ws, "Network.getCookies", {"urls": ["https://www.linkedin.com/"]}).get("cookies", [])
    names = {c["name"] for c in stored}
    for critical in ("li_at", "JSESSIONID"):
        print(f"  {critical}: {'✅ present' if critical in names else '❌ MISSING'}")

    send(ws, "Page.enable")
    send(ws, "Page.navigate", {"url": target_url})
    time.sleep(6)
    r = send(ws, "Runtime.evaluate", {
        "expression": "JSON.stringify({url: location.href, title: document.title})",
        "returnByValue": True,
    })
    state = json.loads(r["result"]["value"])
    print(f"After navigation -> {state['url']}")
    print(f"Title: {state['title']}")
    if "authwall" in state["url"] or "login" in state["url"] or "checkpoint" in state["url"]:
        print("⚠️  Redirected to auth/login — cookies rejected or expired. Re-export from your browser.")
    ws.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
