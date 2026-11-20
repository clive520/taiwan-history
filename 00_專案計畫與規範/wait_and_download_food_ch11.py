# -*- coding: utf-8 -*-
"""
自動輪詢並下載《舌尖上的臺灣》第 11 章 NotebookLM 生成之說明短片與播客雙人對談
"""
import subprocess
import json
import time
import sys
import shutil
from pathlib import Path

NOTEBOOK_ID = "73a11068-cf22-4088-a743-96cbb9e95c71"
BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
TARGET_DIR = BASE_DIR / "舌尖上的臺灣" / "04_大江大海與眷村融合"
TARGET_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_OUT = TARGET_DIR / "第11章_那一碗鄉愁的紅湯_雙人對談.m4a"
AUDIO_COPY = TARGET_DIR / "food_ch11_podcast_deepdive.m4a"
VIDEO_OUT = TARGET_DIR / "第11章_那一碗鄉愁的紅湯_說明影片.mp4"

print(f"🚀 開始監控 NotebookLM [{NOTEBOOK_ID}] 影音生成進度...", flush=True)

audio_done = False
video_done = False

max_attempts = 150  # 最多等待約 35 分鐘
for attempt in range(max_attempts):
    try:
        res = subprocess.run(
            ["nlm", "studio", "status", NOTEBOOK_ID, "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if res.returncode == 0:
            data = json.loads(res.stdout)
            status_map = {item["type"]: item["status"] for item in data}
            print(f"[{attempt+1}/{max_attempts}] 狀態：音訊={status_map.get('audio', '??')}, 視訊={status_map.get('video', '??')}", flush=True)
            
            # 檢查音訊
            if not audio_done and status_map.get("audio") == "completed":
                print("🎉 音訊生成完成，正在下載...", flush=True)
                dl_res = subprocess.run(
                    ["nlm", "download", "audio", NOTEBOOK_ID, "-o", str(AUDIO_OUT), "--no-progress"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                if dl_res.returncode == 0 and AUDIO_OUT.exists() and AUDIO_OUT.stat().st_size > 100000:
                    shutil.copy2(AUDIO_OUT, AUDIO_COPY)
                    print(f"✅ 音訊已成功下載並備份至：{AUDIO_OUT.name} ({AUDIO_OUT.stat().st_size // 1024} KB)", flush=True)
                    audio_done = True
                else:
                    print(f"⚠️ 音訊下載失敗或檔案過小：{dl_res.stderr}", flush=True)

            # 檢查視訊
            if not video_done and status_map.get("video") == "completed":
                print("🎉 視訊生成完成，正在下載...", flush=True)
                dl_res = subprocess.run(
                    ["nlm", "download", "video", NOTEBOOK_ID, "-o", str(VIDEO_OUT), "--no-progress"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                if dl_res.returncode == 0 and VIDEO_OUT.exists() and VIDEO_OUT.stat().st_size > 100000:
                    print(f"✅ 視訊已成功下載至：{VIDEO_OUT.name} ({VIDEO_OUT.stat().st_size // 1024} KB)", flush=True)
                    video_done = True
                else:
                    print(f"⚠️ 視訊下載失敗或檔案過小：{dl_res.stderr}", flush=True)

            if audio_done and video_done:
                print("\n🔥 雙軌影音素材全數下載完成！", flush=True)
                break
                
    except Exception as e:
        print(f"監控錯誤: {e}", flush=True)
        
    time.sleep(15)

if not (audio_done and video_done):
    print("❌ 等待超時或部分任務未完成", flush=True)
    sys.exit(1)
