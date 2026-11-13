# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 04 章 雙軌 YouTube 影片外掛繁體中文字幕更新腳本
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
CH04_DIR = BASE_DIR / "舌尖上的臺灣" / "02_唐山渡海與閩粵交融"

TOKEN_PATHS = [
    BASE_DIR / "youtube_token.json",
    BASE_DIR / "舌尖上的臺灣" / "youtube_token.json",
    BASE_DIR / "00_專案計畫與規範" / "youtube_token.json",
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

def update_captions_for_video(youtube, video_id: str, srt_path: Path, track_name: str = "繁體中文（自然呼吸律與無錯字精修）"):
    print(f"\n==================================================")
    print(f"🎬 正在為影片 [{video_id}] 更新字幕...")
    print(f"📄 字幕檔案：{srt_path.name}")
    
    if not srt_path.exists():
        raise FileNotFoundError(f"找不到字幕檔案：{srt_path}")
        
    # 1. 查詢既有字幕清單並安全刪除
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
    
    # 1. 說明短片 (NMVgUgVNX_w)
    vid_srt = CH04_DIR / "第04章_一碗肉臊的百年身世_說明影片.srt"
    update_captions_for_video(youtube, "NMVgUgVNX_w", vid_srt, "繁體中文（影視級呼吸律）")
    
    # 2. 播客長片 (HQGjT51NLxg)
    pod_srt = CH04_DIR / "第04章_一碗肉臊的百年身世_雙人對談.srt"
    update_captions_for_video(youtube, "HQGjT51NLxg", pod_srt, "繁體中文（對話呼吸意群）")
    print("✨ 第 04 章雙軌 YouTube 字幕已全部更新同步上線！")
