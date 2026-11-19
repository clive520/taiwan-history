# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 10 章 Podcast 影片重傳與舊排程影片替換腳本
- 影片：第10章_山嵐間的東方美人_播客深度對談.mp4 (已嵌入 16:9 無變形大師級油畫背景)
- 上傳並排程至 2026-11-22 19:30
- 掛載新封面與精修繁體中文雙人對談字幕
- 加入播放清單「舌尖上的臺灣」
- 刪除舊的排程影片 (ID: rlhbgn4T1z8)
- 自動更新全專案資料庫與文稿中的 Video ID
"""
import os
import sys
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
FOOD_DIR = BASE_DIR / "舌尖上的臺灣" / "03_帝國之眼與東洋滋味"
THUMB_DIR = BASE_DIR / "assets" / "images" / "food_ch10"

OLD_VIDEO_ID = "rlhbgn4T1z8"
VIDEO_FILE = FOOD_DIR / "第10章_山嵐間的東方美人_播客深度對談.mp4"
TITLE = "【深度播客】蜜香、茶金與維多利亞女王：從客庄膨風茶、陶德李春生洋行狂潮到一斤換數棟房的傳奇"
DESC_FILE = FOOD_DIR / "food_ch10_podcast_desc.txt"
THUMB_FILE = THUMB_DIR / "food_ch10_podcast_thumbnail.jpg"
SRT_FILE = FOOD_DIR / "第10章_山嵐間的東方美人_雙人對談.srt"
TAGS = "臺灣歷史,舌尖上的臺灣,東方美人茶,膨風茶,白毫烏龍,小綠葉蟬,客家茶文化,北埔茶金,大稻埕洋行,約翰陶德,李春生,FormosaOolong,臺灣茶史,維多利亞女王,茉莉酸,茶金"
SCHEDULE = "2026-11-22 19:30"
PLAYLIST = "舌尖上的臺灣"

sys.path.insert(0, str(BASE_DIR / "00_專案計畫與規範"))
from youtube_api_uploader import get_authenticated_service, upload_video

def update_references(new_id):
    print(f"\n📝 正在更新專案資料庫與專論文稿中的 Podcast Video ID ({OLD_VIDEO_ID} -> {new_id})...")
    # 1. 更新 food_ch10_youtube_ids.txt
    id_file = BASE_DIR / "00_專案計畫與規範" / "food_ch10_youtube_ids.txt"
    if id_file.exists():
        lines = id_file.read_text(encoding="utf-8").splitlines()
        if len(lines) >= 2:
            lines[1] = new_id
            id_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            id_file.write_text(f"IQJ-ciAwa-c\n{new_id}\n", encoding="utf-8")
        print("✅ 已更新 food_ch10_youtube_ids.txt")

    # 2. 更新 js/data-food.js 與 舌尖上的臺灣/js/data.js
    for db_path in [BASE_DIR / "js" / "data-food.js", BASE_DIR / "舌尖上的臺灣" / "js" / "data.js"]:
        if db_path.exists():
            c = db_path.read_text(encoding="utf-8")
            c = c.replace(OLD_VIDEO_ID, new_id)
            db_path.write_text(c, encoding="utf-8")
            print(f"✅ 已更新資料庫: {db_path.name}")

    # 3. 更新專題長文
    doc_path = FOOD_DIR / "第10章_山嵐間的東方美人_大稻埕洋行新竹苗栗客庄膨風茶與征服世界的烏龍傳奇.md"
    if doc_path.exists():
        t = doc_path.read_text(encoding="utf-8")
        t = t.replace(OLD_VIDEO_ID, new_id)
        doc_path.write_text(t, encoding="utf-8")
        print("✅ 已更新專題長文導讀模組")

def main():
    print("🚀 開始執行第 10 章 Podcast 影片重傳流程...")
    youtube = get_authenticated_service()
    if not youtube:
        print("❌ 無法取得 YouTube API 驗證客戶端")
        sys.exit(1)

    desc_text = DESC_FILE.read_text(encoding="utf-8") if DESC_FILE.exists() else ""

    print(f"\n📤 正在上傳內含新背景圖的 Podcast 影片：{VIDEO_FILE.name}...")
    new_video_id = upload_video(
        youtube=youtube,
        video_file=str(VIDEO_FILE),
        title=TITLE,
        description=desc_text,
        tags=TAGS,
        schedule_str=SCHEDULE,
        thumbnail_file=str(THUMB_FILE),
        srt_file=str(SRT_FILE),
        playlist_name=PLAYLIST
    )

    if not new_video_id:
        print("❌ 影片上傳失敗！")
        sys.exit(1)

    print(f"\n🎉 新 Podcast 影片上傳成功！新 Video ID: {new_video_id}")

    # 刪除舊排程影片
    try:
        print(f"\n🗑️ 正在刪除舊排程影片 (ID: {OLD_VIDEO_ID})...")
        youtube.videos().delete(id=OLD_VIDEO_ID).execute()
        print(f"✅ 已成功刪除舊排程影片：{OLD_VIDEO_ID}")
    except Exception as e:
        print(f"⚠️ 刪除舊影片時發生狀況（可能已不在線上或權限受限）：{e}")

    # 更新專案內所有參照
    update_references(new_video_id)

    print("\n" + "=" * 60)
    print(f"✨ 第 10 章 Podcast 影片替換全數完成！")
    print(f"👉 新影片連結：https://youtu.be/{new_video_id}")
    print("=" * 60)

if __name__ == "__main__":
    main()
