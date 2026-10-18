# -*- coding: utf-8 -*-
"""
更新 YouTube 影片字幕工具
檢查並替換指定影片的繁體中文字幕軌道
"""
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def update_subtitles(video_id: str, srt_path: str):
    token_file = Path("00_專案計畫與規範/youtube_token.json")
    if not token_file.exists():
        token_file = Path("youtube_token.json")
    
    with open(token_file, "r", encoding="utf-8") as f:
        token_data = json.load(f)
    
    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    youtube = build("youtube", "v3", credentials=creds)
    
    srt_file = Path(srt_path).resolve()
    if not srt_file.exists():
        print(f"❌ 找不到字幕檔：{srt_file}")
        return False
        
    print(f"🎬 目標影片 ID: {video_id}")
    print(f"📝 準備上傳字幕檔：{srt_file.name}")
    
    # 1. 查詢既有字幕軌道
    res = youtube.captions().list(part="snippet", videoId=video_id).execute()
    existing_items = res.get("items", [])
    print(f"📋 目前既有字幕軌道數：{len(existing_items)}")
    
    for item in existing_items:
        c_id = item["id"]
        c_lang = item["snippet"]["language"]
        c_name = item["snippet"]["name"]
        print(f"   - 現有字幕 [ID: {c_id}] 語言: {c_lang}, 名稱: {c_name}")
        # 如果已有繁中字幕軌道，先刪除再上傳新的以確保格式純淨
        if c_lang in ["zh-TW", "zh", "zh-Hant"] or "繁體" in c_name:
            print(f"   🗑️ 正在刪除舊有字幕軌道 [{c_id}]...")
            youtube.captions().delete(id=c_id).execute()
            print(f"   ✅ 已成功刪除舊字幕軌道！")

    # 2. 上傳全新高品質繁中字幕
    print(f"\n🚀 正在向 YouTube API 上傳全新語氣自然斷句字幕軌...")
    caption_body = {
        "snippet": {
            "videoId": video_id,
            "language": "zh-TW",
            "name": "繁體中文（語氣自然斷句校準版）",
            "isDraft": False
        }
    }
    
    media = MediaFileUpload(
        str(srt_file),
        mimetype="application/x-subrip",
        resumable=True
    )
    
    insert_req = youtube.captions().insert(
        part="snippet",
        body=caption_body,
        media_body=media
    )
    
    new_caption = insert_req.execute()
    print(f"🎉 字幕上傳成功！全新字幕軌 ID：{new_caption['id']}")
    print(f"   語言: {new_caption['snippet']['language']}")
    print(f"   軌道名稱: {new_caption['snippet']['name']}")
    return True

if __name__ == "__main__":
    video_id = "5fKIcNMT_jI"
    srt_file = "01_史前文明與南島之源/第01章_黑潮上的遠古足跡_說明影片.srt"
    update_subtitles(video_id, srt_file)
