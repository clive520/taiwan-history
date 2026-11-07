# -*- coding: utf-8 -*-
"""
第 18 章 NLM 影音產出狀態輪詢、自動下載、播客影片合成與 GitHub Releases 託管
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
CH_DIR = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇"

VIDEO_OUT = CH_DIR / "第18章_矽島崛起與世界舞台_說明影片.mp4"
AUDIO_OUT = CH_DIR / "第18章_矽島崛起與世界舞台_雙人對談.m4a"
AUDIO_RELEASE = CH_DIR / "ch18_podcast_deepdive.m4a"
PODCAST_VIDEO_OUT = CH_DIR / "第18章_矽島崛起與世界舞台_播客深度對談.mp4"

NOTEBOOK_ID = "5323a966-58e1-4aea-8ae1-257174e629ea"
VIDEO_ID = "bddb65fe-64a8-4dd5-b101-8a11be80897f"
AUDIO_ID = "0f15963d-eab3-4f23-a226-cefd385f239f"

print("="*70)
print("🚀 開始第 18 章影音狀態監控與下載管線...")
print("="*70)

video_downloaded = False
audio_downloaded = False

start_time = time.time()
max_wait = 1800  # 最多等待 30 分鐘

while time.time() - start_time < max_wait:
    res = subprocess.run(["nlm", "studio", "status", NOTEBOOK_ID, "--json"], capture_output=True, text=True, encoding="utf-8")
    try:
        items = json.loads(res.stdout)
    except Exception as e:
        print(f"⚠️ 解析 status JSON 失敗: {e}")
        time.sleep(15)
        continue

    v_status = None
    a_status = None
    for item in items:
        iid = item.get("id") or item.get("artifact_id")
        itype = item.get("type")
        istatus = item.get("status")
        if iid == VIDEO_ID or itype == "video":
            v_status = istatus
        if iid == AUDIO_ID or itype == "audio":
            a_status = istatus

    elapsed = int(time.time() - start_time)
    print(f"[{elapsed}s] 說明影片狀態: {v_status} | 播客音訊狀態: {a_status}")

    # 下載影片
    if not video_downloaded and v_status == "completed":
        print(f"[*] 說明影片已完成！開始下載至 {VIDEO_OUT.name}...")
        dl_cmd = ["nlm", "download", "video", NOTEBOOK_ID, "-o", str(VIDEO_OUT), "--id", VIDEO_ID, "--no-progress"]
        dl_res = subprocess.run(dl_cmd, capture_output=True, text=True, encoding="utf-8")
        if VIDEO_OUT.exists() and VIDEO_OUT.stat().st_size > 1000000:
            print(f"✅ 說明影片下載成功！大小: {VIDEO_OUT.stat().st_size / (1024*1024):.2f} MB")
            video_downloaded = True
        else:
            print(f"⚠️ 下載影片警告: {dl_res.stdout} {dl_res.stderr}")

    # 下載音訊
    if not audio_downloaded and a_status == "completed":
        print(f"[*] 播客音訊已完成！開始下載至 {AUDIO_OUT.name}...")
        dl_cmd = ["nlm", "download", "audio", NOTEBOOK_ID, "-o", str(AUDIO_OUT), "--id", AUDIO_ID, "--no-progress"]
        dl_res = subprocess.run(dl_cmd, capture_output=True, text=True, encoding="utf-8")
        if AUDIO_OUT.exists() and AUDIO_OUT.stat().st_size > 500000:
            print(f"✅ 播客音訊下載成功！大小: {AUDIO_OUT.stat().st_size / (1024*1024):.2f} MB")
            audio_downloaded = True
            
            # 複製為 release 檔名
            shutil.copy2(AUDIO_OUT, AUDIO_RELEASE)
            print(f"✅ 已同步為：{AUDIO_RELEASE.name}")
            
            # 上傳至 GitHub Releases v1.0.0
            print("[*] 正在上傳音訊至 GitHub Releases v1.0.0...")
            gh_cmd = ["gh", "release", "upload", "v1.0.0", str(AUDIO_RELEASE), "--clobber", "-R", "clive520/taiwan-history"]
            gh_res = subprocess.run(gh_cmd, capture_output=True, text=True, encoding="utf-8")
            if gh_res.returncode == 0:
                print(f"🎉 成功上傳音訊至 GitHub Release: {AUDIO_RELEASE.name}！")
            else:
                print(f"⚠️ GitHub Release 上傳警告: {gh_res.stderr}")
                
            # 合成 1080p 播客深度對談影片
            print("[*] 正在合成 1080p 播客深度對談影片...")
            syn_cmd = ["python", str(BASE_DIR / "00_專案計畫與規範/synthesize_ch18_podcast_video.py")]
            subprocess.run(syn_cmd, check=True)

    if video_downloaded and audio_downloaded:
        print("\n🎉 第 18 章雙軌媒體資源已全部就緒！")
        break

    time.sleep(20)

if not (video_downloaded and audio_downloaded):
    print("❌ 超時或未完全完成！")
    sys.exit(1)
