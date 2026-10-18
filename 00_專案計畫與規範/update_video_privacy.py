# -*- coding: utf-8 -*-
"""
YouTube 影片隱私與公開狀態快速更新工具
支援將排程私人影片即時轉換為 公開 (public) 或 不公開 (unlisted)
"""
import sys
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def update_privacy(video_id: str, new_privacy: str = "public"):
    token_file = Path(__file__).parent / "youtube_token.json"
    if not token_file.exists():
        token_file = Path(r"d:\Antigravity\科技歷史\臺灣史\youtube_token.json")
    
    with open(token_file, "r", encoding="utf-8") as f:
        token_data = json.load(f)
    
    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    youtube = build("youtube", "v3", credentials=creds)
    
    # 讀取目前狀態
    res = youtube.videos().list(part="status,snippet", id=video_id).execute()
    if not res.get("items"):
        print(f"❌ 找不到影片 ID: {video_id}")
        return False
        
    item = res["items"][0]
    title = item["snippet"]["title"]
    print(f"📺 影片: {title} (ID: {video_id})")
    print(f"   原狀態: {item['status'].get('privacyStatus')} (排程: {item['status'].get('publishAt')})")
    
    status_body = {
        "privacyStatus": new_privacy,
        "selfDeclaredMadeForKids": False,
        "embeddable": True
    }
    
    update_res = youtube.videos().update(
        part="status",
        body={
            "id": video_id,
            "status": status_body
        }
    ).execute()
    
    print(f"✅ 成功將影片狀態更新為：{update_res['status']['privacyStatus']}！")
    print(f"🔗 播放網址：https://youtu.be/{video_id}\n")
    return True

if __name__ == "__main__":
    privacy = sys.argv[1] if len(sys.argv) > 1 else "public"
    targets = ["5fKIcNMT_jI", "9Ep4670kORM"]
    for vid in targets:
        update_privacy(vid, privacy)
