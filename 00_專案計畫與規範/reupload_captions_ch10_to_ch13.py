# -*- coding: utf-8 -*-
"""
臺灣史 第10章 至 第13章 8 部 YouTube 影片外掛字幕軌重新發布工具
將舊字幕軌替換為最新依照「文字意義」與「自然說話習慣」重新切分的高品質繁中字幕
"""
import os
import sys
import io
import time
from pathlib import Path
from googleapiclient.http import MediaFileUpload

# 確保輸出支援 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 載入現有 YouTube 授權模組
sys.path.append(str(Path(__file__).resolve().parent))
import youtube_api_uploader

def update_video_caption(youtube, video_id, srt_file_path, video_label):
    srt_p = Path(srt_file_path).resolve()
    if not srt_p.exists():
        print(f"❌ [找不到字幕檔] {srt_p}")
        return False
        
    print(f"\n" + "-"*60)
    print(f"🎬 正在更新 [{video_label}] 的字幕軌...")
    print(f"🆔 YouTube Video ID: {video_id} (https://youtu.be/{video_id})")
    print(f"📄 新字幕檔案：{srt_p.name} ({srt_p.stat().st_size} bytes)")
    
    # 1. 查詢既有字幕軌
    try:
        caps_resp = youtube.captions().list(part="snippet", videoId=video_id).execute()
        existing_items = caps_resp.get("items", [])
        
        # 刪除舊的繁中字幕軌（避免重複）
        for item in existing_items:
            cap_id = item["id"]
            lang = item["snippet"].get("language", "")
            name = item["snippet"].get("name", "")
            print(f"🔍 發現既有字幕軌：[ID: {cap_id}] 語言: {lang}, 名稱: {name}")
            try:
                youtube.captions().delete(id=cap_id).execute()
                print(f"   🗑️ 已成功刪除舊字幕軌：{cap_id}")
                time.sleep(1)
            except Exception as de:
                print(f"   ⚠️ 刪除舊字幕軌失敗（{de}），嘗試直接新增。")
                
    except Exception as e:
        print(f"⚠️ 查詢既有字幕失敗：{e}")

    # 2. 上傳全新語意切分繁中字幕
    try:
        caption_body = {
            "snippet": {
                "videoId": video_id,
                "language": "zh-TW",
                "name": "繁體中文（精準語意校對）",
                "isDraft": False
            }
        }
        media = MediaFileUpload(str(srt_p), mimetype="application/x-subrip")
        result = youtube.captions().insert(
            part="snippet",
            body=caption_body,
            media_body=media
        ).execute()
        new_cap_id = result.get("id", "OK")
        print(f"✅ [成功上傳] 新繁體中文字幕軌已套用！字幕軌 ID: {new_cap_id}")
        return True
    except Exception as e:
        print(f"❌ [上傳失敗] {e}")
        return False

def main():
    base_dir = Path("d:/Antigravity/科技歷史/臺灣史")
    
    # 第 10 章至第 13 章共 8 支影片
    caption_tasks = [
        # 第 13 章
        {
            "video_id": "w_w9qd8zOLw",
            "srt": base_dir / "05_日治時期的統治轉型與抗爭/第13章_乙未悲歌與武裝抗日_說明影片.srt",
            "label": "第13章 說明影片 (乙未悲歌與武裝抗日)"
        },
        {
            "video_id": "hPKl9JEMu7w",
            "srt": base_dir / "05_日治時期的統治轉型與抗爭/第13章_乙未悲歌與武裝抗日_雙人對談.srt",
            "label": "第13章 播客影片 (乙未悲歌與武裝抗日)"
        },
        # 第 12 章
        {
            "video_id": "rMa854Dcga0",
            "srt": base_dir / "04_清領時代的拓墾烽火與變革/第12章_開港通商與現代化急先鋒_說明影片.srt",
            "label": "第12章 說明影片 (開港通商與現代化急先鋒)"
        },
        {
            "video_id": "0p5jfL8fNmo",
            "srt": base_dir / "04_清領時代的拓墾烽火與變革/第12章_開港通商與現代化急先鋒_雙人對談.srt",
            "label": "第12章 播客影片 (開港通商與現代化急先鋒)"
        },
        # 第 11 章
        {
            "video_id": "eQgzt1vCRws",
            "srt": base_dir / "04_清領時代的拓墾烽火與變革/第11章_三年一反五年一亂_說明影片.srt",
            "label": "第11章 說明影片 (三年一反五年一亂)"
        },
        {
            "video_id": "agIBuot_bTI",
            "srt": base_dir / "04_清領時代的拓墾烽火與變革/第11章_三年一反五年一亂_雙人對談.srt",
            "label": "第11章 播客影片 (三年一反五年一亂)"
        },
        # 第 10 章
        {
            "video_id": "Rd45_RsE5DU",
            "srt": base_dir / "04_清領時代的拓墾烽火與變革/第10章_唐山過臺灣的黑水溝血淚_說明影片.srt",
            "label": "第10章 說明影片 (唐山過臺灣的黑水溝血淚)"
        },
        {
            "video_id": "VPPLQWHw1Bc",
            "srt": base_dir / "04_清領時代的拓墾烽火與變革/第10章_唐山過臺灣的黑水溝血淚_雙人對談.srt",
            "label": "第10章 播客影片 (唐山過臺灣的黑水溝血淚)"
        },
    ]

    print("\n" + "="*70)
    print("🚀 正在連線 YouTube Data API v3 執行第 10~13 章字幕軌全量更新...")
    print("="*70)
    
    youtube = youtube_api_uploader.get_authenticated_service()
    
    success_count = 0
    for task in caption_tasks:
        ok = update_video_caption(youtube, task["video_id"], task["srt"], task["label"])
        if ok:
            success_count += 1
        time.sleep(2)  # 避免 API 瞬間速率限制
        
    print("\n" + "="*70)
    print(f"🎯 全部更新作業完成！成功更新：{success_count} / {len(caption_tasks)} 部影片字幕軌！")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
