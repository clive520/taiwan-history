#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動輪詢並下載第 12 章 Google NotebookLM 雙軌影音資源
"""
import subprocess
import json
import time
import sys
import shutil
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

NOTEBOOK_ID = "ee220930-b26c-412d-8939-29b55f50a41f"
BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
TARGET_DIR = BASE_DIR / "04_清領時代的拓墾烽火與變革"
TARGET_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_OUT = TARGET_DIR / "第12章_開港通商與現代化急先鋒_雙人對談.m4a"
AUDIO_COPY = TARGET_DIR / "ch12_podcast_deepdive.m4a"
VIDEO_OUT = TARGET_DIR / "第12章_開港通商與現代化急先鋒_說明影片.mp4"

print(f"開始監控 NotebookLM [{NOTEBOOK_ID}] 影音生成進度...", flush=True)

audio_done = False
video_done = False

max_attempts = 150  # 最多等待約 35 分鐘
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
                    ["nlm", "download", "audio", NOTEBOOK_ID, "-o", str(AUDIO_OUT), "--no-progress"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                if dl.returncode == 0 and AUDIO_OUT.exists() and AUDIO_OUT.stat().st_size > 100000:
                    print(f"[OK] 音訊下載成功！大小: {AUDIO_OUT.stat().st_size / (1024*1024):.2f} MB", flush=True)
                    shutil.copyfile(AUDIO_OUT, AUDIO_COPY)
                    print(f"[OK] 副本已同步存為: {AUDIO_COPY}", flush=True)
                    audio_done = True
                else:
                    print(f"[WARN] 音訊下載重試中：{dl.stderr}", flush=True)

            # 檢查影片
            if status_map.get("video") == "completed" and not video_done:
                print(f"[VIDEO] 影片已生成完畢，正在下載至：{VIDEO_OUT}...", flush=True)
                dl = subprocess.run(
                    ["nlm", "download", "video", NOTEBOOK_ID, "-o", str(VIDEO_OUT), "--no-progress"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                if dl.returncode == 0 and VIDEO_OUT.exists() and VIDEO_OUT.stat().st_size > 100000:
                    print(f"[OK] 影片下載成功！大小: {VIDEO_OUT.stat().st_size / (1024*1024):.2f} MB", flush=True)
                    video_done = True
                else:
                    print(f"[WARN] 影片下載重試中：{dl.stderr}", flush=True)

            if audio_done and video_done:
                print("\n[SUCCESS] 第 12 章 雙軌影音資源全數下載成功！", flush=True)
                break

    except Exception as e:
        print(f"[ERR] 輪詢異常: {e}", flush=True)

    time.sleep(15)

if not (audio_done and video_done):
    print("\n[WARN] 超時退出，部分影音尚未完成。", flush=True)
