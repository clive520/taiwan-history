#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
臺灣史專案 - 官方 YouTube Data API v3 命令列自動上傳工具
功能：
1. 本地 OAuth 2.0 授權登入（使用者只需在瀏覽器中點擊允許一次，自動產生 token.json 供日後免手動登入）
2. 斷點續傳（Resumable Upload）上傳大型高畫質 MP4 影片
3. 自動設定標題、說明欄（含 GitHub Pages 專屬章節網址）、標籤、兒童保護設定
4. 自動設定公開排程時間（例如：2026-10-26T17:30:00+08:00）
5. 自動上傳繁體中文外掛字幕（.srt）
6. 自動上傳自訂高清封面縮圖（.jpg / .png）
7. 自動加入指定播放清單（例如：「台灣史」）
"""

import os
import sys
import argparse
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# 所需 YouTube API 權限範圍
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtubepartner"
]

def get_authenticated_service(client_secrets_file="client_secret.json", token_file="youtube_token.json"):
    """取得 YouTube API 驗證服務"""
    creds = None
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            print(f"⚠️ 讀取現有 Token 失敗：{e}，將重新授權。")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 正在刷新過期的授權 Token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secrets_file):
                print(f"\n❌ 錯誤：找不到 Google Cloud 憑證檔案 [{client_secrets_file}]")
                print("💡 請先至 Google Cloud Console 下載 OAuth 2.0 Client ID 憑證（Desktop 應用程式）")
                print(f"   並將檔案命名為 {client_secrets_file} 放置於專案根目錄。")
                sys.exit(1)
            print("\n🌐 即將開啟瀏覽器進行 Google / YouTube 授權...")
            print("👉 請在瀏覽器中登入您的 YouTube 頻道並點選「允許」。")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=8080, prompt="consent")
        
        # 儲存 Token
        with open(token_file, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print(f"✅ 授權成功！Token 已持久化儲存於：{token_file}")

    return build("youtube", "v3", credentials=creds)

def find_or_create_playlist(youtube, playlist_title):
    """查找或建立播放清單"""
    print(f"🔍 正在檢查播放清單 [{playlist_title}]...")
    request = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50
    )
    response = request.execute()
    for item in response.get("items", []):
        if item["snippet"]["title"] == playlist_title:
            print(f"✅ 找到既有播放清單：{playlist_title} (ID: {item['id']})")
            return item["id"]
    
    print(f"➕ 正在建立新播放清單：[{playlist_title}]...")
    create_request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": playlist_title,
                "description": "臺灣史專題寫作與數位文庫系列影音全集"
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    )
    res = create_request.execute()
    print(f"✅ 成功建立播放清單 ID：{res['id']}")
    return res["id"]

def add_video_to_playlist(youtube, video_id, playlist_id):
    """將影片加入播放清單"""
    print(f"📌 正在將影片加入播放清單 (ID: {playlist_id})...")
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    request.execute()
    print("✅ 成功加入播放清單！")

def upload_video(youtube, video_file, title, description, tags, schedule_iso=None, thumbnail_file=None, srt_file=None, playlist_name=None):
    """上傳影片主流程"""
    if not os.path.exists(video_file):
        print(f"❌ 找不到影片檔案：{video_file}")
        sys.exit(1)

    print(f"\n🚀 開始上傳影片：{os.path.basename(video_file)}")
    print(f"📌 標題：{title}")
    
    # 決定發布狀態與排程
    status_body = {
        "selfDeclaredMadeForKids": False
    }
    if schedule_iso:
        # YouTube 要求排程影片在排程生效前 privacyStatus 必須是 private
        status_body["privacyStatus"] = "private"
        status_body["publishAt"] = schedule_iso
        print(f"⏰ 已設定公開排程時間：{schedule_iso}")
    else:
        status_body["privacyStatus"] = "public"
        print("📢 發布狀態：直接公開")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "27", # Education (教育)
            "defaultLanguage": "zh-TW",
            "defaultAudioLanguage": "zh-TW"
        },
        "status": status_body
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    print("📤 正在進行傳輸上傳（支援斷點續傳）...")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"   已上傳 {int(status.progress() * 100)}%...")

    video_id = response["id"]
    video_url = f"https://youtu.be/{video_id}"
    print(f"\n🎉 影片上傳成功！")
    print(f"🔗 影片網址：{video_url}")

    # 1. 上傳封面縮圖
    if thumbnail_file and os.path.exists(thumbnail_file):
        try:
            print(f"🖼️ 正在上傳封面縮圖：{os.path.basename(thumbnail_file)}...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_file)
            ).execute()
            print("✅ 封面縮圖設定成功！")
        except Exception as e:
            print(f"⚠️ 封面縮圖上傳失敗：{e}")

    # 2. 上傳外掛字幕 (.srt)
    if srt_file and os.path.exists(srt_file):
        try:
            print(f"📝 正在上傳外掛字幕：{os.path.basename(srt_file)}...")
            caption_body = {
                "snippet": {
                    "videoId": video_id,
                    "language": "zh-TW",
                    "name": "繁體中文（精準校對）",
                    "isDraft": False
                }
            }
            youtube.captions().insert(
                part="snippet",
                body=caption_body,
                media_body=MediaFileUpload(srt_file, mimetype="application/x-subrip")
            ).execute()
            print("✅ 繁體中文字幕上傳成功！")
        except Exception as e:
            print(f"⚠️ 字幕上傳失敗：{e}")

    # 3. 加入播放清單
    if playlist_name:
        try:
            playlist_id = find_or_create_playlist(youtube, playlist_name)
            add_video_to_playlist(youtube, video_id, playlist_id)
        except Exception as e:
            print(f"⚠️ 加入播放清單失敗：{e}")

    return video_url

def main():
    parser = argparse.ArgumentParser(description="YouTube API 影片與字幕自動化上傳 CLI")
    parser.add_argument("--video", required=True, help="影片 MP4 檔案路徑")
    parser.add_argument("--title", required=True, help="影片標題")
    parser.add_argument("--desc-file", help="說明欄 Markdown 或文字檔案路徑")
    parser.add_argument("--desc", help="說明文字內容（直接傳入）")
    parser.add_argument("--srt", help="外掛字幕 SRT 檔案路徑")
    parser.add_argument("--thumbnail", help="封面縮圖 JPG/PNG 檔案路徑")
    parser.add_argument("--playlist", default="台灣史", help="播放清單名稱")
    parser.add_argument("--schedule", help="排程 ISO 格式時間 (如: 2026-10-26T17:30:00+08:00)")
    parser.add_argument("--tags", default="臺灣史,台灣史,歷史科普,長濱文化", help="逗號分隔的標籤字串")
    parser.add_argument("--secrets", default="client_secret.json", help="OAuth 憑證路徑")

    args = parser.parse_args()

    desc_content = ""
    if args.desc_file and os.path.exists(args.desc_file):
        with open(args.desc_file, "r", encoding="utf-8") as f:
            desc_content = f.read()
    elif args.desc:
        desc_content = args.desc

    tags_list = [t.strip() for t in args.tags.split(",") if t.strip()]

    # 執行授權與上傳
    youtube = get_authenticated_service(client_secrets_file=args.secrets)
    video_url = upload_video(
        youtube=youtube,
        video_file=args.video,
        title=args.title,
        description=desc_content,
        tags=tags_list,
        schedule_iso=args.schedule,
        thumbnail_file=args.thumbnail,
        srt_file=args.srt,
        playlist_name=args.playlist
    )

    print(f"\n=======================================================")
    print(f"🎯 全流程完成！影片已成功排程並收錄於清單。")
    print(f"🔗 影片連結：{video_url}")
    print(f"=======================================================\n")

if __name__ == "__main__":
    main()
