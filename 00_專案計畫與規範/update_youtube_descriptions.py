# -*- coding: utf-8 -*-
"""
更新《舌尖上的臺灣》第 01 章與第 02 章（共 4 支影片）YouTube 影片說明欄連結
補上專題長文網頁連結、飲食風土專頁連結與文庫總門戶連結
"""
import sys
import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
TOKEN_PATH = BASE_DIR / "00_專案計畫與規範" / "youtube_token.json"
CH01_DIR = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味"

VIDEOS = [
    {
        "id": "tT9wePxt0ZY",
        "name": "第 01 章 說明短片",
        "desc_file": CH01_DIR / "food_ch01_desc.txt"
    },
    {
        "id": "r7MVQa5En9A",
        "name": "第 01 章 播客長片",
        "desc_file": CH01_DIR / "food_ch01_podcast_desc.txt"
    },
    {
        "id": "anxoGeGVLz4",
        "name": "第 02 章 說明短片",
        "desc_file": CH01_DIR / "food_ch02_desc.txt"
    },
    {
        "id": "zEvu1lJY54Q",
        "name": "第 02 章 播客長片",
        "desc_file": CH01_DIR / "food_ch02_podcast_desc.txt"
    }
]

def update_descriptions():
    if not TOKEN_PATH.exists():
        print(f"❌ 找不到 Token 檔案：{TOKEN_PATH}")
        sys.exit(1)
        
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    youtube = build("youtube", "v3", credentials=creds)
    
    print("🚀 開始向 YouTube API 更新 4 支影片之說明欄（注入專題網頁連結）...\n")
    
    for v in VIDEOS:
        vid = v["id"]
        vname = v["name"]
        desc_path = v["desc_file"]
        
        if not desc_path.exists():
            print(f"❌ 找不到說明欄檔案：{desc_path}")
            continue
            
        new_desc = desc_path.read_text(encoding="utf-8").strip()
        
        # 1. 取得既有影片資訊
        res = youtube.videos().list(part="snippet", id=vid).execute()
        items = res.get("items", [])
        if not items:
            print(f"⚠️ 找不到 YouTube 影片：{vid} ({vname})")
            continue
            
        snippet = items[0]["snippet"]
        old_desc = snippet.get("description", "")
        
        # 2. 更新 description
        snippet["description"] = new_desc
        
        # 3. 呼叫 update API
        update_res = youtube.videos().update(
            part="snippet",
            body={
                "id": vid,
                "snippet": snippet
            }
        ).execute()
        
        print(f"✅ 【{vname}】更新成功！")
        print(f"   - 影片 ID: {vid} (https://youtu.be/{vid})")
        print(f"   - 標題: {snippet.get('title')}")
        print("   - 包含的網址連結：")
        for line in new_desc.splitlines():
            if "http" in line:
                print(f"     {line.strip()}")
        print("-" * 60)

    print("\n🎉 4 支影片說明欄網頁連結全部更新完成！")

if __name__ == "__main__":
    update_descriptions()
