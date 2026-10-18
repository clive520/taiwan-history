#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
臺灣史專案 - YouTube Data API 官方 OAuth 2.0 授權精靈 (獨立純淨版)
"""

import os
import sys
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials
import googleapiclient.discovery

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

CANDIDATE_SECRET_PATHS = [
    Path("client_secrets.json"),
    Path(__file__).parent / "client_secrets.json",
    Path(__file__).parent.parent / "client_secrets.json",
    Path(r"G:\共用雲端硬碟\志賢個人資料\Antigravity\music_suno\client_secrets.json"),
]

def find_file(candidate_list):
    for p in candidate_list:
        try:
            if p.exists():
                return p.resolve()
        except Exception:
            pass
    return None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    auth_code = None
    query_params = {}

    def log_message(self, format, *args):
        # 靜默日誌，避免干擾終端
        return

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        OAuthCallbackHandler.query_params = qs
        if "code" in qs:
            OAuthCallbackHandler.auth_code = qs["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>YouTube 授權成功</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #0f172a; color: #f8fafc; }
                    .card { background: #1e293b; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; max-width: 500px; border: 1px solid #334155; }
                    h1 { color: #38bdf8; margin-bottom: 12px; font-size: 24px; }
                    p { color: #94a3b8; line-height: 1.6; font-size: 16px; }
                    .badge { display: inline-block; background: #059669; color: white; padding: 6px 16px; border-radius: 9999px; font-weight: bold; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="card">
                    <div class="badge">✓ 授權成功</div>
                    <h1>YouTube 官方 API 授權完成！</h1>
                    <p>已成功取得 clive520@gmail.com 之 YouTube 上傳與管理憑證。<br>系統已將憑證安全儲存，您現在可以關閉此瀏覽器視窗。</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h1>授權未完成或拒絕存取</h1>".encode("utf-8"))

def main():
    print("=" * 70, flush=True)
    print("🎬 【臺灣史】YouTube 官方 API 授權精靈 (Google Cloud OAuth 2.0)", flush=True)
    print("=" * 70, flush=True)

    secret_file = find_file(CANDIDATE_SECRET_PATHS)
    if not secret_file:
        print("❌ 找不到 client_secrets.json！", flush=True)
        return

    print(f"📄 找到 OAuth 用戶端憑證：{secret_file}", flush=True)
    print("👉 目標 Google 帳號：clive520@gmail.com", flush=True)
    print("-" * 70, flush=True)

    # 嘗試綁定本地 Port (8080 -> 8081 -> 8082)
    server = None
    listen_port = 8080
    for p in [8080, 8081, 8082, 0]:
        try:
            server = HTTPServer(("localhost", p), OAuthCallbackHandler)
            listen_port = server.server_port
            break
        except Exception:
            continue

    if not server:
        print("❌ 無法啟動本地接收伺服器！", flush=True)
        return

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        str(secret_file), SCOPES
    )
    flow.redirect_uri = f"http://localhost:{listen_port}/"

    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    print("\n" + "=" * 70, flush=True)
    print("🔑 請點擊以下授權網址進行 Google 授權：", flush=True)
    print("=" * 70, flush=True)
    print(auth_url, flush=True)
    print("=" * 70 + "\n", flush=True)
    print(f"📡 本地監聽伺服器已就緒 (http://localhost:{listen_port}/)，等待瀏覽器授權回傳...", flush=True)

    # 嘗試開啟瀏覽器 (若桌面環境允許)
    try:
        import webbrowser
        webbrowser.open(auth_url)
    except Exception:
        pass

    # 等候直到捕獲授權碼
    while not OAuthCallbackHandler.auth_code:
        server.handle_request()
    server.server_close()

    code = OAuthCallbackHandler.auth_code
    if not code:
        print("❌ 未收到有效的授權碼！", flush=True)
        return

    print("📥 成功接收授權回傳，正在向 Google 伺服器交換 Token...", flush=True)
    flow.fetch_token(code=code)
    creds = flow.credentials
    token_json = creds.to_json()

    save_targets = [
        Path(__file__).parent / "youtube_token.json",
        Path(__file__).parent.parent / "youtube_token.json",
        Path(r"G:\共用雲端硬碟\志賢個人資料\Antigravity\music_suno\youtube_token.json")
    ]

    print("-" * 70, flush=True)
    for p in save_targets:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(token_json)
            print(f"💾 憑證成功寫入：{p}", flush=True)
        except Exception as e:
            print(f"⚠️ 寫入 {p} 失敗: {e}", flush=True)

    # 驗證取得的頻道名稱
    try:
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
        res = youtube.channels().list(part="snippet", mine=True).execute()
        if res.get("items"):
            channel_name = res["items"][0]["snippet"]["title"]
            print(f"\n🎉 驗證成功！已成功連線至 YouTube 頻道：【{channel_name}】", flush=True)
    except Exception as e:
        print(f"頻道名稱獲取提示: {e}", flush=True)

    print("\n" + "=" * 70, flush=True)
    print("✅ YouTube 官方 API 授權圓滿完成！後續上傳作業皆可全自動背景執行。", flush=True)
    print("=" * 70 + "\n", flush=True)

if __name__ == "__main__":
    main()
