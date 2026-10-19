#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動輪詢並下載第 09 章 Google NotebookLM 雙軌影音資源
"""
import subprocess
import json
import time
import sys
from pathlib import Path

NOTEBOOK_ID = "384ad7a6-8b75-43c6-be97-4407e005ffc1"
AUDIO_OUT = Path("03_明鄭東寧與海上孤忠/第09章_澎湖海戰與帝國落幕_雙人對談.m4a")
VIDEO_OUT = Path("03_明鄭東寧與海上孤忠/第09章_澎湖海戰與帝國落幕_說明影片.mp4")

print(f"開始監控 NotebookLM [{NOTEBOOK_ID}] 影音生成進度...", flush=True)

audio_done = False
video_done = False

max_attempts = 120  # 最多等待約 30 分鐘
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
            print(f"[{attempt+1}/{max_attempts}] 狀態：音訊={status_map.get('audio', '無')}, 影片={status_map.get('video', '無')}", flush=True)
            
            # 檢查音訊
            if status_map.get("audio") == "completed" and not audio_done:
                print(f"[AUDIO] 音訊已生成完畢，正在下載至：{AUDIO_OUT}...", flush=True)
                dl = subprocess.run(
                    ["nlm", "download", "audio", NOTEBOOK_ID, "-o", str(AUDIO_OUT)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                if dl.returncode == 0 and AUDIO_OUT.exists():
                    print(f"[OK] 音訊下載成功！檔案大小: {AUDIO_OUT.stat().st_size / (1024*1024):.2f} MB", flush=True)
                    audio_done = True
                else:
                    print(f"[WARN] 音訊下載重試中：{dl.stderr}", flush=True)

            # 檢查影片
            if status_map.get("video") == "completed" and not video_done:
                print(f"[VIDEO] 影片已生成完畢，正在下載至：{VIDEO_OUT}...", flush=True)
                dl = subprocess.run(
                    ["nlm", "download", "video", NOTEBOOK_ID, "-o", str(VIDEO_OUT)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                if dl.returncode == 0 and VIDEO_OUT.exists():
                    print(f"[OK] 影片下載成功！檔案大小: {VIDEO_OUT.stat().st_size / (1024*1024):.2f} MB", flush=True)
                    video_done = True
                else:
                    print(f"[WARN] 影片下載重試中：{dl.stderr}", flush=True)

            if audio_done and video_done:
                print(">>> 雙軌影音（音訊＋影片）全數下載完成！<<<", flush=True)
                break

    except Exception as e:
        print(f"檢查異常: {e}", flush=True)

    time.sleep(15)

if not (audio_done and video_done):
    print("等待超時或部分未完成，請稍後手動檢查狀態！", flush=True)
    sys.exit(1)
