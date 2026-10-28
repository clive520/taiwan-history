# -*- coding: utf-8 -*-
"""
YouTube Data API v3 專屬一次性 OAuth 授權更新腳本
確保單一 State、正確儲存 Token 到所有專案路徑
"""
import sys
from pathlib import Path
import google_auth_oauthlib.flow

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

base_dir = Path("D:/Antigravity/科技歷史/臺灣史/00_專案計畫與規範")
secret_path = base_dir / "client_secrets.json"
tok_path = base_dir / "youtube_token.json"
auth_txt = base_dir / "youtube_auth_url.txt"

print(f"🔑 使用憑證檔案：{secret_path}", flush=True)

class UrlSaverPrompt:
    def format(self, **kwargs):
        url = kwargs.get("url", "")
        try:
            auth_txt.write_text(url, encoding="utf-8")
        except Exception:
            pass
        return (
            f"\n{'='*70}\n"
            f"👉 請在瀏覽器中開啟專屬授權連結：\n{url}\n"
            f"{'='*70}\n"
            f"🌐 正在監聽本地 Port 8080 等待授權回傳...\n"
        )

flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    str(secret_path), SCOPES
)

# 由 run_local_server 統一生成單一 URL 並開啟瀏覽器
creds = flow.run_local_server(
    port=8080,
    prompt="consent",
    access_type="offline",
    authorization_prompt_message=UrlSaverPrompt(),
    open_browser=True
)

token_json_data = creds.to_json()
target_token_paths = [
    tok_path,
    tok_path.parent.parent / "youtube_token.json",
    Path(r"G:\共用雲端硬碟\志賢個人資料\Antigravity\music_suno\youtube_token.json"),
]

for save_p in target_token_paths:
    try:
        save_p.parent.mkdir(parents=True, exist_ok=True)
        with open(save_p, "w", encoding="utf-8") as f:
            f.write(token_json_data)
        print(f"💾 Token 已成功保存至：{save_p}", flush=True)
    except Exception as e:
        print(f"⚠️ 保存至 {save_p} 失敗：{e}", flush=True)

print("🎉 YouTube OAuth 授權已全面更新並就緒！", flush=True)
