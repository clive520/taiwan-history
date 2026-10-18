#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動輪詢並下載第 06 章 Google NotebookLM 雙軌影音資源
"""
import subprocess
import json
import time
from pathlib import Path

NOTEBOOK_ID = "c5354897-5c84-4a22-81e7-bc4ee2d0585b"
AUDIO_OUT = Path("02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_雙人對談.m4a")
VIDEO_OUT = Path("02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_說明影片.mp4")

print(f"開始監控 NotebookLM [{NOTEBOOK_ID}] 影音生成進度...")

audio_done = False
video_done = False

max_attempts = 60  # 最多等待 20 分鐘
for attempt in range(max_attempts):
    try:
        res = subprocess.run(
            ["nlm", "studio", "status", NOTEBOOK_ID],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if res.returncode == 0:
            data = json.loads(res.stdout)
            status_map = {item["type"]: item["status"] for item in data}
            print(f"[{attempt+1}/{max_attempts}] 狀態：音訊={status_map.get('audio', '無')}, 影片={status_map.get('video', '無')}")
            
            # 檢查音訊
            if status_map.get("audio") == "completed" and not audio_done:
                print(f"🎵 音訊已生成完畢，正在下載至：{AUDIO_OUT}...")
                dl = subprocess.run(
                    ["nlm", "download", "audio", NOTEBOOK_ID, "-o", str(AUDIO_OUT)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                if dl.returncode == 0 and AUDIO_OUT.exists():
                    print(f"✅ 音訊下載成功！檔案大小: {AUDIO_OUT.stat().st_size / (1024*1024):.2f} MB")
                    audio_done = True
                else:
                    print(f"⚠️ 音訊下載重試中：{dl.stderr}")

            # 檢查影片
            if status_map.get("video") == "completed" and not video_done:
                print(f"🎬 影片已生成完畢，正在下載至：{VIDEO_OUT}...")
                dl = subprocess.run(
                    ["nlm", "download", "video", NOTEBOOK_ID, "-o", str(VIDEO_OUT)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                if dl.returncode == 0 and VIDEO_OUT.exists():
                    print(f"✅ 影片下載成功！檔案大小: {VIDEO_OUT.stat().st_size / (1024*1024):.2f} MB")
                    video_done = True
                else:
                    print(f"⚠️ 影片下載重試中：{dl.stderr}")

            if audio_done and video_done:
                print("\n🎉 雙軌影音資源全數生成並下載完畢！")
                break
    except Exception as e:
        print(f"輪詢異常：{e}")

    time.sleep(20)

if not (audio_done and video_done):
    print(f"\n⚠️ 等待超時或未完全完成：audio_done={audio_done}, video_done={video_done}")
