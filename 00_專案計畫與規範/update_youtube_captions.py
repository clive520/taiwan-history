# -*- coding: utf-8 -*-
"""
更新 YouTube 影片外掛繁體中文字幕腳本
功能：
1. 讀取既有 YouTube OAuth Token
2. 查詢指定影片既有的字幕軌並安全清除舊版
3. 上傳最新精修之繁體中文字幕（.srt）
"""
import sys
import os
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
TOKEN_PATHS = [
    BASE_DIR / "舌尖上的臺灣" / "youtube_token.json",
    BASE_DIR / "youtube_token.json",
    Path(r"G:\共用雲端硬碟\志賢個人資料\Antigravity\music_suno\youtube_token.json")
]

def get_youtube_client():
    token_file = None
    for p in TOKEN_PATHS:
        if p.exists():
            token_file = p
            break
            
    if not token_file:
        raise FileNotFoundError("找不到 youtube_token.json！")
        
    creds = Credentials.from_authorized_user_file(str(token_file))
    if creds.expired and creds.refresh_token:
        print("🔄 Token 已過期，正在自動刷新...")
        creds.refresh(Request())
        with open(token_file, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
            
    return build("youtube", "v3", credentials=creds)

def update_captions_for_video(youtube, video_id: str, srt_path: Path, track_name: str = "繁體中文（自然語意精準校對）"):
    print(f"\n==================================================")
    print(f"🎬 正在為影片 [{video_id}] 更新字幕...")
    print(f"📄 字幕檔案：{srt_path.name}")
    
    if not srt_path.exists():
        raise FileNotFoundError(f"找不到字幕檔案：{srt_path}")
        
    # 1. 查詢既有字幕清單
    try:
        captions_res = youtube.captions().list(part="snippet", videoId=video_id).execute()
        existing_items = captions_res.get("items", [])
        print(f"🔍 找到 {len(existing_items)} 個既有字幕軌：")
        for item in existing_items:
            cap_id = item["id"]
            lang = item["snippet"].get("language", "")
            name = item["snippet"].get("name", "")
            print(f"   🗑️ 正在刪除舊字幕軌：ID={cap_id}, 語言={lang}, 名稱={name}")
            try:
                youtube.captions().delete(id=cap_id).execute()
                print("      ✅ 刪除成功！")
            except Exception as e:
                print(f"      ⚠️ 刪除失敗（非致命）：{e}")
    except Exception as e:
        print(f"⚠️ 查詢既有字幕時發生錯誤：{e}")
        
    # 2. 上傳新字幕軌
    caption_body = {
        "snippet": {
            "videoId": video_id,
            "language": "zh-TW",
            "name": track_name,
            "isDraft": False
        }
    }
    media = MediaFileUpload(str(srt_path), mimetype="application/x-subrip")
    insert_req = youtube.captions().insert(
        part="snippet",
        body=caption_body,
        media_body=media
    )
    res = insert_req.execute()
    new_id = res.get("id")
    print(f"🎉 成功上傳新字幕軌！ID: {new_id}")
    print(f"🔗 影片預覽：https://youtu.be/{video_id}")
    print("==================================================\n")

if __name__ == "__main__":
    youtube = get_youtube_client()
    
    CH01_DIR = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味"
    
    # 1. 說明影片
    v1_id = "tT9wePxt0ZY"
    v1_srt = CH01_DIR / "第01章_粟米野豬與香料火種_說明影片.srt"
    if v1_srt.exists():
        update_captions_for_video(youtube, v1_id, v1_srt, "繁體中文（精準校對）")
        
    # 2. 播客影片
    v2_id = "r7MVQa5En9A"
    v2_srt = CH01_DIR / "第01章_粟米野豬與香料火種_雙人對談.srt"
    if v2_srt.exists():
        update_captions_for_video(youtube, v2_id, v2_srt, "繁體中文（自然語意對話）")
