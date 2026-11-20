# -*- coding: utf-8 -*-
"""
使用 FFmpeg 將高品質 1080p 絕美無變形背景圖與雙人對談音訊合成為 YouTube 播客專用 MP4 影片
"""
import subprocess
import sys
import os
from pathlib import Path

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH12_DIR = BASE_DIR / "舌尖上的臺灣" / "04_大江大海與眷村融合"
BG_IMG = BASE_DIR / "assets" / "images" / "food_ch12" / "food_ch12_podcast_bg.jpg"
AUDIO_FILE = CH12_DIR / "第12章_晨光裡的麵粉香_雙人對談.m4a"
OUTPUT_MP4 = CH12_DIR / "第12章_晨光裡的麵粉香_播客深度對談.mp4"

def main():
    if not BG_IMG.exists():
        print(f"❌ 背景底圖不存在：{BG_IMG}")
        sys.exit(1)
    if not AUDIO_FILE.exists():
        print(f"❌ 音訊檔案不存在：{AUDIO_FILE}")
        sys.exit(1)

    print(f"🎬 開始合成 1080p 播客影片...")
    print(f"  - 背景圖 (1920x1080 嚴格等比無拉伸): {BG_IMG.name}")
    print(f"  - 音訊源: {AUDIO_FILE.name}")
    print(f"  - 輸出目標: {OUTPUT_MP4.name}")

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(BG_IMG),
        "-i", str(AUDIO_FILE),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(OUTPUT_MP4)
    ]

    ret = subprocess.run(cmd)
    if ret.returncode == 0 and OUTPUT_MP4.exists() and OUTPUT_MP4.stat().st_size > 100000:
        print(f"✅ 播客影片合成成功！檔案大小: {OUTPUT_MP4.stat().st_size // (1024*1024)} MB")
    else:
        print("❌ 播客影片合成失敗！")
        sys.exit(ret.returncode)

if __name__ == "__main__":
    main()
