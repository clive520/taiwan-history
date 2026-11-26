# -*- coding: utf-8 -*-
"""
《島嶼鐵道物語》第 08 章 YouTube 雙軌排程自動上架發布腳本
- 說明短片排程：2026-12-05 17:30
- 播客長片排程：2026-12-05 19:30
- 官方清單：島嶼鐵道物語
- 自動更新 js/data-railway.js 與 島嶼鐵道物語/js/data.js
"""
import os
import sys
import re
import subprocess
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

PYTHON_EXE = r"C:\Users\admin\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
UPLOADER_SCRIPT = BASE_DIR / "00_專案計畫與規範" / "youtube_api_uploader.py"
RAIL_DIR = BASE_DIR / "島嶼鐵道物語" / "02_高山森林與產業支線"
THUMB_DIR = BASE_DIR / "assets" / "images" / "rail_ch08"

def run_cmd(cmd):
    print(f"\n[EXEC] {' '.join(cmd)}", flush=True)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', bufsize=1)
    full_output = []
    for line in iter(p.stdout.readline, ''):
        print(line, end='', flush=True)
        full_output.append(line)
    p.stdout.close()
    ret = p.wait()
    return ret, ''.join(full_output)

def update_databases(v1_id, v2_id):
    db_paths = [
        BASE_DIR / "js" / "data-railway.js",
        BASE_DIR / "島嶼鐵道物語" / "js" / "data.js"
    ]
    
    for db_path in db_paths:
        if not db_path.exists():
            continue
        c = db_path.read_text(encoding='utf-8')
        pattern = r'("id":\s*"rail_ch08",[\s\S]*?"status":\s*)"planned"'
        replacement = rf'\1"published",\n    "youtube": "{v1_id}",\n    "podcastYoutube": "{v2_id}",\n    "audioFile": "第08章_樟腦巨木與濁水溪的迴音_雙人對談.m4a"'
        c_new = re.sub(pattern, replacement, c)
        db_path.write_text(c_new, encoding='utf-8')
        print(f"✅ 已更新資料庫: {db_path.name} (rail_ch08 published, v1={v1_id}, v2={v2_id})")

def main():
    v1_file = RAIL_DIR / "第08章_樟腦巨木與濁水溪的迴音_說明影片.mp4"
    v1_title = "【島嶼鐵道物語 EP08】樟腦、巨木與濁水溪的迴音：集集支線、日月潭水電與車埕木業傳奇（4K說明短片）"
    v1_desc = BASE_DIR / "rail_ch08_desc.txt"
    v1_thumb = THUMB_DIR / "rail_ch08_youtube_thumbnail.jpg"
    v1_srt = RAIL_DIR / "第08章_樟腦巨木與濁水溪的迴音_說明影片.srt"
    
    v2_file = RAIL_DIR / "第08章_樟腦巨木與濁水溪的迴音_播客深度對談.mp4"
    v2_title = "【深度播客】電力心臟、神木池與震後重生：集集支線百年拓墾與 921 純檜木驛站奇蹟（雙人深度對談）"
    v2_desc = BASE_DIR / "rail_ch08_podcast_desc.txt"
    v2_thumb = THUMB_DIR / "rail_ch08_podcast_thumbnail.jpg"
    v2_srt = RAIL_DIR / "第08章_樟腦巨木與濁水溪的迴音_雙人對談.srt"
    
    tags = "臺灣歷史,島嶼鐵道物語,集集支線,集集車站,車埕,日月潭水力發電,大觀發電廠,武界引水隧道,濁水溪,振昌木業,孫海,貯木池,綠色隧道,921大地震,解體重組,ProjectIronVeins,臺灣鐵道史,播客,Podcast"
    playlist_name = "島嶼鐵道物語"

    if not v1_file.exists():
        print(f"❌ 說明短片不存在：{v1_file}")
        sys.exit(1)
    if not v2_file.exists():
        print(f"❌ 播客影片不存在：{v2_file}")
        sys.exit(1)

    print("🚀 開始執行第 08 章《樟腦、巨木與濁水溪的迴音》YouTube 雙軌排程上傳...")

    cmd_v1 = [
        PYTHON_EXE, str(UPLOADER_SCRIPT),
        "--video", str(v1_file),
        "--title", v1_title,
        "--desc-file", str(v1_desc),
        "--tags", tags,
        "--schedule", "2026-12-05 17:30",
        "--playlist", playlist_name,
        "--thumbnail", str(v1_thumb),
        "--srt", str(v1_srt)
    ]
    ret1, out1 = run_cmd(cmd_v1)
    if ret1 != 0:
        print("❌ 說明短片上傳失敗！")
        sys.exit(1)
    m1 = re.search(r"Video ID:\s*([a-zA-Z0-9_-]{11})", out1)
    v1_id = m1.group(1) if m1 else ""
    print(f"\n🎉 說明短片上傳成功！Video ID: {v1_id}")

    cmd_v2 = [
        PYTHON_EXE, str(UPLOADER_SCRIPT),
        "--video", str(v2_file),
        "--title", v2_title,
        "--desc-file", str(v2_desc),
        "--tags", tags,
        "--schedule", "2026-12-05 19:30",
        "--playlist", playlist_name,
        "--thumbnail", str(v2_thumb),
        "--srt", str(v2_srt)
    ]
    ret2, out2 = run_cmd(cmd_v2)
    if ret2 != 0:
        print("❌ 播客長片上傳失敗！")
        sys.exit(1)
    m2 = re.search(r"Video ID:\s*([a-zA-Z0-9_-]{11})", out2)
    v2_id = m2.group(1) if m2 else ""
    print(f"\n🎉 播客長片上傳成功！Video ID: {v2_id}")

    if v1_id and v2_id:
        print("\n📦 同步更新前端資料庫與中繼資料...")
        update_databases(v1_id, v2_id)
        print(f"\n🏆《島嶼鐵道物語》第 08 章已全規格發布排程完工！(v1={v1_id}, v2={v2_id})")
    else:
        print("⚠️ 無法擷取 Video ID，請手動確認資料庫更新。")

if __name__ == "__main__":
    main()
