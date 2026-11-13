# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 06 章 影音處理、GitHub Releases 上傳與 FFmpeg 合成自動化腳本
"""
import sys
import os
import json
import time
import subprocess
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH06_DIR = BASE_DIR / "舌尖上的臺灣" / "02_唐山渡海與閩粵交融"
THUMB_DIR = BASE_DIR / "assets" / "images" / "food_ch06"

PODCAST_AUDIO = CH06_DIR / "food_ch06_podcast_deepdive.m4a"
PODCAST_THUMB = THUMB_DIR / "food_ch06_podcast_thumbnail.jpg"
PODCAST_VIDEO = CH06_DIR / "第06章_廟埕香火與米食變奏_播客深度對談.mp4"
EXPLAINER_VIDEO = CH06_DIR / "第06章_廟埕香火與米食變奏_說明影片.mp4"

def synthesize_podcast_video():
    if not PODCAST_AUDIO.exists():
        print(f"❌ 找不到音訊檔案：{PODCAST_AUDIO}")
        return False
    if not PODCAST_THUMB.exists():
        print(f"❌ 找不到縮圖檔案：{PODCAST_THUMB}")
        return False
        
    print(f"\n🎬 開始使用 FFmpeg 合成播客高畫質 1080p 影片：{PODCAST_VIDEO.name}...")
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(PODCAST_THUMB),
        "-i", str(PODCAST_AUDIO),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(PODCAST_VIDEO)
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", bufsize=1)
    for line in iter(p.stdout.readline, ''):
        if "time=" in line:
            print(f"\r⏳ 合成進度: {line.strip()}", end="", flush=True)
    p.stdout.close()
    ret = p.wait()
    print()
    if ret == 0 and PODCAST_VIDEO.exists():
        print(f"✅ 播客影片合成完成！檔案大小：{PODCAST_VIDEO.stat().st_size / (1024*1024):.2f} MB")
        return True
    else:
        print("❌ FFmpeg 合成失敗！")
        return False

def upload_to_github_release():
    if not PODCAST_AUDIO.exists():
        print(f"❌ 找不到音訊檔案：{PODCAST_AUDIO}")
        return False
    print(f"\n📦 正在上傳音訊至 GitHub Releases v1.0.0：{PODCAST_AUDIO.name}...")
    cmd = [
        "gh", "release", "upload", "v1.0.0",
        str(PODCAST_AUDIO),
        "--clobber",
        "-R", "clive520/taiwan-history"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✅ GitHub Releases 上傳成功！")
        print(f"🔗 音訊網址: https://github.com/clive520/taiwan-history/releases/download/v1.0.0/{PODCAST_AUDIO.name}")
        return True
    else:
        print(f"❌ GitHub Releases 上傳失敗：{res.stderr}")
        return False

if __name__ == "__main__":
    upload_to_github_release()
    synthesize_podcast_video()
