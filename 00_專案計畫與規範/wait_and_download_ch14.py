# -*- coding: utf-8 -*-
"""
自動輪詢並下載第 14 章 Google NotebookLM 雙軌繁體中文影音資源
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

NOTEBOOK_ID = "4a8b0145-f20d-41f8-a94a-022fc220f854"
VIDEO_ID = "a36c702a-3dec-4d39-bd57-cef2f4e4ae80"
AUDIO_ID = "0db8a195-9118-43c3-85e1-368276bc1df1"

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
TARGET_DIR = BASE_DIR / "05_日治時期的統治轉型與抗爭"
TARGET_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_OUT = TARGET_DIR / "第14章_現代化骨架與殖民之刃_雙人對談.m4a"
AUDIO_COPY = TARGET_DIR / "ch14_podcast_deepdive.m4a"
VIDEO_OUT = TARGET_DIR / "第14章_現代化骨架與殖民之刃_說明影片.mp4"

print(f"開始監控第 14 章 NotebookLM [{NOTEBOOK_ID}] 影音生成進度...", flush=True)

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
            status_map = {item["id"]: item["status"] for item in data}
            v_st = status_map.get(VIDEO_ID, "unknown")
            a_st = status_map.get(AUDIO_ID, "unknown")
            print(f"[{attempt+1}/{max_attempts}] 狀態：音訊={a_st}, 影片={v_st}", flush=True)
            
            # 檢查音訊
            if a_st == "completed" and not audio_done:
                print(f"[AUDIO] 音訊已生成完畢，正在下載至：{AUDIO_OUT}...", flush=True)
                dl = subprocess.run(
                    ["nlm", "download", "audio", NOTEBOOK_ID, "--id", AUDIO_ID, "-o", str(AUDIO_OUT), "--no-progress"],
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
            if v_st == "completed" and not video_done:
                print(f"[VIDEO] 影片已生成完畢，正在下載至：{VIDEO_OUT}...", flush=True)
                dl = subprocess.run(
                    ["nlm", "download", "video", NOTEBOOK_ID, "--id", VIDEO_ID, "-o", str(VIDEO_OUT), "--no-progress"],
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
                print("\n[SUCCESS] 第 14 章 雙軌繁體中文影音資源全數下載成功！", flush=True)
                break

    except Exception as e:
        print(f"[ERR] 輪詢異常: {e}", flush=True)

    time.sleep(15)

if not (audio_done and video_done):
    print("\n[WARN] 超時退出，部分影音尚未完成。", flush=True)
