# -*- coding: utf-8 -*-
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

base_dir = Path("D:/Antigravity/科技歷史/臺灣史")

tasks = [
    {
        "name": "Ch06",
        "cover": base_dir / "assets/images/ch06/ch06_hero_banner.jpg",
        "audio": base_dir / "02_大航海時代與荷西競逐/ch06_podcast_deepdive.m4a",
        "output": base_dir / "02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_播客深度對談.mp4"
    },
    {
        "name": "Ch07",
        "cover": base_dir / "assets/images/ch07/ch07_hero_banner.jpg",
        "audio": base_dir / "03_明鄭東寧與海上孤忠/ch07_podcast_deepdive.m4a",
        "output": base_dir / "03_明鄭東寧與海上孤忠/第07章_決戰大員九個月_播客深度對談.mp4"
    }
]

for t in tasks:
    print(f"\n[*] 開始合成 {t['name']} 1080p 播客影片：{t['output'].name}...", flush=True)
    if not t['audio'].exists():
        print(f"[ERR] 找不到音訊檔案：{t['audio']}")
        continue
    if not t['cover'].exists():
        print(f"[ERR] 找不到封面檔案：{t['cover']}")
        continue
        
    cmd = [
        "ffmpeg", "-loop", "1",
        "-i", str(t['cover']),
        "-i", str(t['audio']),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(t['output']),
        "-y"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode == 0 and t['output'].exists() and t['output'].stat().st_size > 1000000:
        print(f"✅ {t['name']} 1080p 播客影片合成成功！大小：{t['output'].stat().st_size / (1024*1024):.2f} MB")
    else:
        print(f"[ERR] {t['name']} 合成失敗：{res.stderr}")

print("\n🎉 播客影片合成處理完畢！")
