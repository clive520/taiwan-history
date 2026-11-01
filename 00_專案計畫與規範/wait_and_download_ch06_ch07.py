# -*- coding: utf-8 -*-
"""
自動輪詢並下載第 06 章與第 07 章繁體中文影音資源
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

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")

CH06_DIR = BASE_DIR / "02_大航海時代與荷西競逐"
CH07_DIR = BASE_DIR / "03_明鄭東寧與海上孤忠"

CH06_NOTEBOOK = "c5354897-5c84-4a22-81e7-bc4ee2d0585b"
CH07_NOTEBOOK = "c3127091-0bff-4fea-be05-93089cfaeeb1"

CH06_VIDEO_ID = "1b09332c-8cc7-4c6d-b390-6b51a7a6b484"
CH06_AUDIO_ID = "4535eef4-9481-4d94-8097-8adbbc40a5cc"

CH07_VIDEO_ID = "b626151f-3ce0-49a3-bae2-7dbb319ae0d1"
CH07_AUDIO_ID = "a78cb819-e6ff-4c9c-9ea2-e848b56bd8ac"

CH06_VIDEO_OUT = CH06_DIR / "第06章_血濺赤崁與大鹿港_說明影片.mp4"
CH06_AUDIO_OUT = CH06_DIR / "第06章_血濺赤崁與大鹿港_雙人對談.m4a"
CH06_AUDIO_COPY = CH06_DIR / "ch06_podcast_deepdive.m4a"

CH07_VIDEO_OUT = CH07_DIR / "第07章_決戰大員九個月_說明影片.mp4"
CH07_AUDIO_OUT = CH07_DIR / "第07章_決戰大員九個月_雙人對談.m4a"
CH07_AUDIO_COPY = CH07_DIR / "ch07_podcast_deepdive.m4a"

status_flags = {
    "ch06_video": False,
    "ch06_audio": False,
    "ch07_video": False,
    "ch07_audio": False
}

def check_status(notebook_id):
    try:
        res = subprocess.run(
            ["nlm", "studio", "status", notebook_id],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if res.returncode == 0:
            return json.loads(res.stdout)
    except Exception as e:
        print(f"[ERR] check_status error: {e}", flush=True)
    return []

print("開始監控第 06 章與第 07 章 NotebookLM 繁體中文影音生成進度...", flush=True)

max_attempts = 150  # 最多等待約 35 分鐘
for attempt in range(max_attempts):
    # 檢查 Ch06
    data_06 = check_status(CH06_NOTEBOOK)
    map_06 = {item["id"]: item["status"] for item in data_06}
    
    # 檢查 Ch07
    data_07 = check_status(CH07_NOTEBOOK)
    map_07 = {item["id"]: item["status"] for item in data_07}
    
    c6_v_st = map_06.get(CH06_VIDEO_ID, "unknown")
    c6_a_st = map_06.get(CH06_AUDIO_ID, "unknown")
    c7_v_st = map_07.get(CH07_VIDEO_ID, "unknown")
    c7_a_st = map_07.get(CH07_AUDIO_ID, "unknown")
    
    print(f"[{attempt+1}/{max_attempts}] 狀態 -> "
          f"Ch06影片:{c6_v_st}, Ch06音訊:{c6_a_st} | "
          f"Ch07影片:{c7_v_st}, Ch07音訊:{c7_a_st}", flush=True)
    
    # 下載 Ch06 影片
    if c6_v_st == "completed" and not status_flags["ch06_video"]:
        print(f"\n[CH06] 說明影片已完成，開始下載至: {CH06_VIDEO_OUT}...", flush=True)
        dl = subprocess.run(
            ["nlm", "download", "video", CH06_NOTEBOOK, "--id", CH06_VIDEO_ID, "-o", str(CH06_VIDEO_OUT), "--no-progress"],
            capture_output=True, text=True, encoding="utf-8"
        )
        if dl.returncode == 0 and CH06_VIDEO_OUT.exists() and CH06_VIDEO_OUT.stat().st_size > 100000:
            print(f"✅ Ch06 說明影片下載成功！大小: {CH06_VIDEO_OUT.stat().st_size / (1024*1024):.2f} MB", flush=True)
            status_flags["ch06_video"] = True
        else:
            print(f"[WARN] Ch06 說明影片下載失敗重試: {dl.stderr}", flush=True)

    # 下載 Ch06 音訊
    if c6_a_st == "completed" and not status_flags["ch06_audio"]:
        print(f"\n[CH06] 播客音訊已完成，開始下載至: {CH06_AUDIO_OUT}...", flush=True)
        dl = subprocess.run(
            ["nlm", "download", "audio", CH06_NOTEBOOK, "--id", CH06_AUDIO_ID, "-o", str(CH06_AUDIO_OUT), "--no-progress"],
            capture_output=True, text=True, encoding="utf-8"
        )
        if dl.returncode == 0 and CH06_AUDIO_OUT.exists() and CH06_AUDIO_OUT.stat().st_size > 100000:
            print(f"✅ Ch06 播客音訊下載成功！大小: {CH06_AUDIO_OUT.stat().st_size / (1024*1024):.2f} MB", flush=True)
            shutil.copyfile(CH06_AUDIO_OUT, CH06_AUDIO_COPY)
            print(f"✅ Ch06 副本已同步存為: {CH06_AUDIO_COPY}", flush=True)
            status_flags["ch06_audio"] = True
        else:
            print(f"[WARN] Ch06 播客音訊下載失敗重試: {dl.stderr}", flush=True)

    # 下載 Ch07 影片
    if c7_v_st == "completed" and not status_flags["ch07_video"]:
        print(f"\n[CH07] 說明影片已完成，開始下載至: {CH07_VIDEO_OUT}...", flush=True)
        dl = subprocess.run(
            ["nlm", "download", "video", CH07_NOTEBOOK, "--id", CH07_VIDEO_ID, "-o", str(CH07_VIDEO_OUT), "--no-progress"],
            capture_output=True, text=True, encoding="utf-8"
        )
        if dl.returncode == 0 and CH07_VIDEO_OUT.exists() and CH07_VIDEO_OUT.stat().st_size > 100000:
            print(f"✅ Ch07 說明影片下載成功！大小: {CH07_VIDEO_OUT.stat().st_size / (1024*1024):.2f} MB", flush=True)
            status_flags["ch07_video"] = True
        else:
            print(f"[WARN] Ch07 說明影片下載失敗重試: {dl.stderr}", flush=True)

    # 下載 Ch07 音訊
    if c7_a_st == "completed" and not status_flags["ch07_audio"]:
        print(f"\n[CH07] 播客音訊已完成，開始下載至: {CH07_AUDIO_OUT}...", flush=True)
        dl = subprocess.run(
            ["nlm", "download", "audio", CH07_NOTEBOOK, "--id", CH07_AUDIO_ID, "-o", str(CH07_AUDIO_OUT), "--no-progress"],
            capture_output=True, text=True, encoding="utf-8"
        )
        if dl.returncode == 0 and CH07_AUDIO_OUT.exists() and CH07_AUDIO_OUT.stat().st_size > 100000:
            print(f"✅ Ch07 播客音訊下載成功！大小: {CH07_AUDIO_OUT.stat().st_size / (1024*1024):.2f} MB", flush=True)
            shutil.copyfile(CH07_AUDIO_OUT, CH07_AUDIO_COPY)
            print(f"✅ Ch07 副本已同步存為: {CH07_AUDIO_COPY}", flush=True)
            status_flags["ch07_audio"] = True
        else:
            print(f"[WARN] Ch07 播客音訊下載失敗重試: {dl.stderr}", flush=True)

    if all(status_flags.values()):
        print("\n🎉🎉🎉 第 06 章與第 07 章四項繁體中文影音資源全數生成並下載完畢！", flush=True)
        break

    time.sleep(15)

if not all(status_flags.values()):
    print("\n[WARN] 輪詢結束，部分影音尚未完成: ", status_flags, flush=True)
