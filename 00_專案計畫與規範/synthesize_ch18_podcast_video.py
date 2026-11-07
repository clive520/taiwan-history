# -*- coding: utf-8 -*-
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

base_dir = Path("D:/Antigravity/科技歷史/臺灣史")
cover_img = base_dir / "assets/images/ch18/ch18_hero_banner.jpg"
audio_file = base_dir / "06_戰後重構民主浪潮與矽島傳奇/ch18_podcast_deepdive.m4a"
video_out = base_dir / "06_戰後重構民主浪潮與矽島傳奇/第18章_矽島崛起與世界舞台_播客深度對談.mp4"

if not audio_file.exists():
    print(f"[ERR] 找不到音訊檔案：{audio_file}")
    sys.exit(1)
if not cover_img.exists():
    print(f"[ERR] 找不到封面檔案：{cover_img}")
    sys.exit(1)

print(f"[*] 開始合成 1080p 播客影片：{video_out.name}...", flush=True)
cmd = [
    "ffmpeg", "-loop", "1",
    "-i", str(cover_img),
    "-i", str(audio_file),
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "stillimage",
    "-c:a", "aac",
    "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-shortest",
    str(video_out),
    "-y"
]

res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
if res.returncode == 0 and video_out.exists() and video_out.stat().st_size > 1000000:
    print(f"✅ 1080p 播客影片合成成功！大小：{video_out.stat().st_size / (1024*1024):.2f} MB")
else:
    print(f"[ERR] 合成失敗：{res.stderr}")
    sys.exit(1)
