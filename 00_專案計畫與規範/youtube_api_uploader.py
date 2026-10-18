#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
臺灣史專案 - 官方 YouTube Data API v3 自動化排程與發布管線
功能：
1. 支援 Google Cloud OAuth 2.0 桌面授權（讀取 client_secrets.json，自動儲存並同步 youtube_token.json）
2. 智慧 Token 刷新與過期重授權機制
3. 斷點續傳（Resumable Upload）上傳大型高畫質 MP4 影片（分類 27: 教育）
4. 智慧時間轉換：將臺灣時間 (UTC+8) 自動轉為 YouTube API 要求之 UTC ISO-8601 (以 Z 結尾)
5. 排程發布自動搭配 privacyStatus: private 嚴格防呆
6. 自動上傳繁體中文外掛字幕（.srt）
7. 自動上傳自訂高清封面縮圖（.jpg / .png）
8. 自動檢索或建立「台灣史」專屬播放清單並加入影片
9. 防重複上傳機制（產生同名 .uploaded 標記檔）
"""

import os
import sys
import argparse
import datetime
import re
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# 必備 OAuth 2.0 權限範圍（與 music_suno 完全一致，不依賴敏感的 youtubepartner）
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

CANDIDATE_SECRET_PATHS = [
    Path("client_secrets.json"),
    Path("client_secret.json"),
    Path(__file__).parent / "client_secrets.json",
    Path(__file__).parent.parent / "client_secrets.json",
    Path(r"G:\共用雲端硬碟\志賢個人資料\Antigravity\music_suno\client_secrets.json"),
]

CANDIDATE_TOKEN_PATHS = [
    Path("youtube_token.json"),
    Path(__file__).parent / "youtube_token.json",
    Path(__file__).parent.parent / "youtube_token.json",
    Path(r"G:\共用雲端硬碟\志賢個人資料\Antigravity\music_suno\youtube_token.json"),
]

def find_file(candidate_list, description="檔案"):
    for p in candidate_list:
        try:
            if p.exists():
                return p.resolve()
        except Exception:
            pass
    return None

def parse_schedule_to_utc_iso(schedule_str: str) -> str:
    """
    將使用者輸入的時間（如 '2026-10-26 17:30', '2026-10-26T17:30:00+08:00'）
    自動轉換為 YouTube API 要求之 UTC ISO-8601 格式：YYYY-MM-DDTHH:MM:SS.000Z
    """
    schedule_str = schedule_str.strip()
    # 如果已經是 UTC 格式 (以 Z 結尾)
    if schedule_str.endswith("Z"):
        return schedule_str

    dt = None
    # 支援幾種常見格式
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
    ]

    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(schedule_str, fmt)
            break
        except ValueError:
            continue

    if not dt:
        # 正則嘗試解析
        m = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})[ T](\d{1,2}):(\d{1,2})", schedule_str)
        if m:
            y, mo, d, h, mi = map(int, m.groups())
            dt = datetime.datetime(y, mo, d, h, mi)
        else:
            raise ValueError(f"無法解析排程時間格式：{schedule_str}。請使用 YYYY-MM-DD HH:MM 格式。")

    # 若無時區資訊，預設為臺灣時區 UTC+8
    if dt.tzinfo is None:
        tz_cst = datetime.timezone(datetime.timedelta(hours=8))
        dt = dt.replace(tzinfo=tz_cst)

    # 轉為 UTC
    dt_utc = dt.astimezone(datetime.timezone.utc)
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def get_authenticated_service(client_secrets_file=None, token_file=None):
    """取得 YouTube API 授權客戶端"""
    # 1. 定位 client_secrets.json
    secret_path = None
    if client_secrets_file and Path(client_secrets_file).exists():
        secret_path = Path(client_secrets_file).resolve()
    else:
        secret_path = find_file(CANDIDATE_SECRET_PATHS, "OAuth 用戶端 ID 憑證")

    # 2. 定位或準備 youtube_token.json
    tok_path = None
    if token_file and Path(token_file).exists():
        tok_path = Path(token_file).resolve()
    else:
        tok_path = find_file(CANDIDATE_TOKEN_PATHS, "Token 檔")
        if not tok_path:
            tok_path = Path(__file__).parent / "youtube_token.json"

    creds = None
    if tok_path and tok_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(tok_path), SCOPES)
        except Exception as e:
            print(f"⚠️ 讀取現有 Token 失敗：{e}，準備重新進行授權。")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 正在向 Google 伺服器刷新授權 Token...")
                creds.refresh(Request())
                print("✅ Token 刷新成功！")
            except Exception as e:
                print(f"⚠️ Token 刷新失敗（{e}），需重新取得授權。")
                creds = None

        if not creds:
            if not secret_path or not secret_path.exists():
                raise FileNotFoundError(
                    f"❌ 找不到 Google Cloud OAuth 憑證 (client_secrets.json)！\n"
                    f"請確認檔案位於專案目錄或共用雲端硬碟中。"
                )
            print(f"\n🔑 使用憑證檔案：{secret_path}")
            print("🌐 正在啟動 Google OAuth 2.0 本地授權流程...")
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                str(secret_path), SCOPES
            )
            # 優先嘗試 8080，若被佔用則由系統隨機分配 port=0
            try:
                creds = flow.run_local_server(port=8080, prompt="consent")
            except Exception:
                creds = flow.run_local_server(port=0, prompt="consent")

        # 儲存 Token 到本地以及共用雲端硬碟 (若可用)
        token_json_data = creds.to_json()
        target_token_paths = [
            tok_path,
            Path(__file__).parent / "youtube_token.json",
            Path(__file__).parent.parent / "youtube_token.json",
            Path(r"G:\共用雲端硬碟\志賢個人資料\Antigravity\music_suno\youtube_token.json"),
        ]
        for save_p in target_token_paths:
            try:
                save_p.parent.mkdir(parents=True, exist_ok=True)
                with open(save_p, "w", encoding="utf-8") as f:
                    f.write(token_json_data)
                print(f"💾 Token 已同步保存至：{save_p}")
            except Exception:
                pass

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def find_or_create_playlist(youtube, playlist_title):
    """查詢既有播放清單，若不存在則自動新建"""
    print(f"🔍 正在查詢頻道播放清單 [{playlist_title}]...")
    try:
        request = youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50
        )
        response = request.execute()
        for item in response.get("items", []):
            if item["snippet"]["title"].strip() == playlist_title.strip():
                playlist_id = item["id"]
                print(f"✅ 找到既有播放清單：{playlist_title} (ID: {playlist_id})")
                return playlist_id
    except Exception as e:
        print(f"⚠️ 查詢播放清單時發生非致命錯誤：{e}")

    print(f"➕ 正在建立全新播放清單：[{playlist_title}]...")
    create_request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": playlist_title,
                "description": "臺灣歷史專題數位文庫系列影音全集（含深度導讀與外掛字幕）"
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    )
    res = create_request.execute()
    playlist_id = res["id"]
    print(f"✅ 成功建立播放清單 ID：{playlist_id}")
    return playlist_id

def add_video_to_playlist(youtube, video_id, playlist_id, playlist_title=""):
    """將影片加入播放清單"""
    print(f"📌 正在將影片加入播放清單 [{playlist_title}] (ID: {playlist_id})...")
    try:
        youtube.playlistItems().insert(
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
        ).execute()
        print(f"✅ 成功將影片加入播放清單！")
    except Exception as e:
        print(f"⚠️ 加入播放清單失敗或影片已存在於清單：{e}")

def upload_video(youtube, video_file, title, description, tags=None, schedule_str=None, thumbnail_file=None, srt_file=None, playlist_name=None):
    """執行完整影片上傳、排程、縮圖、字幕與清單歸類流程"""
    video_path = Path(video_file).resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"找不到影片檔案：{video_path}")

    # 檢查防重複標記檔
    marker_path = video_path.with_suffix(".uploaded")
    if marker_path.exists():
        with open(marker_path, "r", encoding="utf-8") as f:
            existing_id = f.read().strip()
        print(f"⏩ 偵測到標記檔 [{marker_path.name}]，該影片已於先前成功上傳！")
        print(f"🔗 既有 YouTube 網址：https://youtu.be/{existing_id}")
        return existing_id

    # 嚴格控制標題長度 <= 95 字元
    safe_title = title.strip()
    if len(safe_title) > 95:
        safe_title = safe_title[:95]

    if tags is None:
        tags = ["臺灣史", "台灣史", "歷史科普", "數位文庫", "NotebookLM"]

    # 處理排程與公開狀態
    status_body = {
        "selfDeclaredMadeForKids": False
    }
    if schedule_str:
        utc_iso = parse_schedule_to_utc_iso(schedule_str)
        status_body["privacyStatus"] = "private"  # API 限制：排程時必須設為 private
        status_body["publishAt"] = utc_iso
        print(f"⏰ 排程公開時間：{schedule_str} (UTC 傳送值: {utc_iso})")
    else:
        status_body["privacyStatus"] = "public"
        print("📢 發布狀態：直接公開 (Public)")

    body = {
        "snippet": {
            "title": safe_title,
            "description": description,
            "tags": tags,
            "categoryId": "27",  # 27 = Education 教育
            "defaultLanguage": "zh-TW",
            "defaultAudioLanguage": "zh-TW"
        },
        "status": status_body
    }

    print(f"\n🚀 開始上傳影片：{video_path.name}")
    print(f"📝 影片標題：{safe_title}")
    print(f"📦 檔案大小：{video_path.stat().st_size / (1024*1024):.2f} MB")

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    print("📤 正在進行 Resumable 斷點續傳...")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"   上傳進度：{int(status.progress() * 100)}%...")

    video_id = response["id"]
    video_url = f"https://youtu.be/{video_id}"
    print(f"\n🎉 影片上傳成功！")
    print(f"🆔 Video ID: {video_id}")
    print(f"🔗 影片網址: {video_url}")

    # 寫入 .uploaded 防重複標記
    with open(marker_path, "w", encoding="utf-8") as f:
        f.write(video_id)
    print(f"📄 已建立防重複標記檔：{marker_path.name}")

    # 1. 上傳封面縮圖
    if thumbnail_file and Path(thumbnail_file).exists():
        thumb_p = Path(thumbnail_file).resolve()
        try:
            print(f"🖼️ 正在上傳封面縮圖：{thumb_p.name}...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumb_p))
            ).execute()
            print("✅ 封面縮圖設定成功！")
        except Exception as e:
            print(f"⚠️ 封面縮圖上傳失敗：{e}")

    # 2. 上傳外掛繁中字幕 (.srt)
    if srt_file and Path(srt_file).exists():
        srt_p = Path(srt_file).resolve()
        try:
            print(f"📝 正在上傳繁體中文字幕：{srt_p.name}...")
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
                media_body=MediaFileUpload(str(srt_p), mimetype="application/x-subrip")
            ).execute()
            print("✅ 繁體中文字幕上傳成功！")
        except Exception as e:
            print(f"⚠️ 字幕上傳失敗：{e}")

    # 3. 加入播放清單
    if playlist_name:
        try:
            playlist_id = find_or_create_playlist(youtube, playlist_name)
            add_video_to_playlist(youtube, video_id, playlist_id, playlist_name)
        except Exception as e:
            print(f"⚠️ 播放清單處理失敗：{e}")

    return video_id

def main():
    parser = argparse.ArgumentParser(description="YouTube Data API v3 官方上傳工具 (臺灣史專用)")
    parser.add_argument("--video", required=True, help="影片 MP4 檔案路徑")
    parser.add_argument("--title", required=True, help="影片標題")
    parser.add_argument("--desc-file", help="說明欄文字檔路徑")
    parser.add_argument("--desc", help="說明文字直接傳入")
    parser.add_argument("--srt", help="外掛字幕 SRT 檔案路徑")
    parser.add_argument("--thumbnail", help="封面縮圖 JPG/PNG 檔案路徑")
    parser.add_argument("--playlist", default="台灣史", help="播放清單名稱")
    parser.add_argument("--schedule", help="排程發布時間 (例如: '2026-10-26 17:30' 或 '2026-10-26T17:30:00+08:00')")
    parser.add_argument("--tags", default="臺灣史,台灣史,歷史科普,長濱文化,八仙洞,舊石器時代,左鎮人,黑潮", help="標籤逗號分隔")
    parser.add_argument("--secrets", help="指定 client_secrets.json 路徑")
    parser.add_argument("--token", help="指定 youtube_token.json 路徑")

    args = parser.parse_args()

    desc_content = ""
    if args.desc_file and Path(args.desc_file).exists():
        with open(args.desc_file, "r", encoding="utf-8") as f:
            desc_content = f.read()
    elif args.desc:
        desc_content = args.desc

    tags_list = [t.strip() for t in args.tags.split(",") if t.strip()]

    # 初始化服務
    youtube = get_authenticated_service(args.secrets, args.token)

    # 執行上傳
    video_id = upload_video(
        youtube=youtube,
        video_file=args.video,
        title=args.title,
        description=desc_content,
        tags=tags_list,
        schedule_str=args.schedule,
        thumbnail_file=args.thumbnail,
        srt_file=args.srt,
        playlist_name=args.playlist
    )

    print("\n" + "="*60)
    print("🎯 YouTube 自動化排程發布全流程完成！")
    print(f"🎬 影片 ID: {video_id}")
    print(f"🔗 影片預覽/觀看連結: https://youtu.be/{video_id}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
