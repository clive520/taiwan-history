#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
from pathlib import Path
sys.path.append('00_專案計畫與規範')
from youtube_api_uploader import get_authenticated_service
from googleapiclient.http import MediaFileUpload

yt = get_authenticated_service()

tasks = [
    # Ch01
    ('5fKIcNMT_jI', 'assets/images/ch01/ch01_youtube_thumbnail.jpg', '【臺灣史 EP01 說明影片】'),
    ('9Ep4670kORM', 'assets/images/ch01/ch01_podcast_thumbnail.jpg', '【臺灣史 PODCAST EP01】'),
    # Ch02
    ('7UHNACoGMps', 'assets/images/ch02/ch02_youtube_thumbnail.jpg', '【臺灣史 EP02 說明影片】'),
    ('nCPvm8Wm3bc', 'assets/images/ch02/ch02_podcast_thumbnail.jpg', '【臺灣史 PODCAST EP02】'),
    # Ch03
    ('zUdGDyUpf9g', 'assets/images/ch03/ch03_youtube_thumbnail.jpg', '【臺灣史 EP03 說明影片】'),
    ('C3thxaXg7Fc', 'assets/images/ch03/ch03_podcast_thumbnail.jpg', '【臺灣史 PODCAST EP03】'),
    # Ch04
    ('F9PmvVUY7no', 'assets/images/ch04/ch04_youtube_thumbnail.jpg', '【臺灣史 EP04 說明影片】'),
    ('-NUWwkAHEPA', 'assets/images/ch04/ch04_podcast_thumbnail.jpg', '【臺灣史 PODCAST EP04】'),
    # Ch05
    ('1xV__Smr_Xs', 'assets/images/ch05/ch05_youtube_thumbnail.jpg', '【臺灣史 EP05 說明影片】'),
    ('5R-t3fwEDws', 'assets/images/ch05/ch05_podcast_thumbnail.jpg', '【臺灣史 PODCAST EP05】'),
]

print(f"Starting thumbnail replacement for {len(tasks)} videos on YouTube...")
success_count = 0

for vid, thumb_path, desc in tasks:
    p = Path(thumb_path)
    if not p.exists():
        print(f"❌ 檔案不存在：{thumb_path}")
        continue
    try:
        print(f"🚀 正在替換 {desc} (ID: {vid}) 的封面縮圖...")
        res = yt.thumbnails().set(
            videoId=vid,
            media_body=MediaFileUpload(str(p), mimetype='image/jpeg')
        ).execute()
        print(f"   ✅ 替換成功！")
        success_count += 1
        time.sleep(1)
    except Exception as e:
        print(f"   ❌ 替換失敗 (ID: {vid})：{e}")

print(f"\n🎉 全部處理完成！成功替換 {success_count}/{len(tasks)} 部影片封面圖片！")
