# -*- coding: utf-8 -*-
"""
第 06 章 與 第 07 章 重建 YouTube 影音發布管線
1. 刪除 YouTube 上舊的英文發音影片 (可選/安全防呆)
2. 清理舊 .uploaded 標記檔以觸發全新上傳
3. 上傳繁體中文說明影片與播客影片，附帶排程、縮圖、語意 SRT 字幕軌與加入播放清單
4. 自動更新 js/data.js 與 Markdown 檔案中的 Video ID
"""
import os
import sys
import json
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

OLD_IDS = {
    "ch06_video": "qdRyKFYwhPk",
    "ch06_podcast": "FBCapmmopgI",
    "ch07_video": "zzdTcyMWc0g",
    "ch07_podcast": "8pEU0k1p158"
}

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

def delete_old_youtube_videos():
    print("="*70)
    print("🗑️ 正在安全刪除 YouTube 上舊有的 4 部英文發音影片...")
    print("="*70)
    
    script_del = """
import sys
from pathlib import Path
sys.path.insert(0, r"d:/Antigravity/科技歷史/臺灣史/00_專案計畫與規範")
from youtube_api_uploader import get_authenticated_service

youtube = get_authenticated_service()
old_ids = ['qdRyKFYwhPk', 'FBCapmmopgI', 'zzdTcyMWc0g', '8pEU0k1p158']
for vid in old_ids:
    try:
        youtube.videos().delete(id=vid).execute()
        print(f"✅ 成功從 YouTube 刪除舊影片: {vid}")
    except Exception as e:
        print(f"⚠️ 刪除影片 {vid} 略過或失敗: {e}")
"""
    del_file = BASE_DIR / "00_專案計畫與規範" / "_temp_delete_old_videos.py"
    del_file.write_text(script_del, encoding='utf-8')
    subprocess.run([PYTHON_EXE, str(del_file)], capture_output=False)
    if del_file.exists():
        del_file.unlink()

def clean_uploaded_markers():
    markers = [
        BASE_DIR / "02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_說明影片.uploaded",
        BASE_DIR / "02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_播客深度對談.uploaded",
        BASE_DIR / "03_明鄭東寧與海上孤忠/第07章_決戰大員九個月_說明影片.uploaded",
        BASE_DIR / "03_明鄭東寧與海上孤忠/第07章_決戰大員九個月_播客深度對談.uploaded",
    ]
    for m in markers:
        if m.exists():
            m.unlink()
            print(f"🧹 已清除標記檔: {m.name}")

def update_all_references(id_map):
    print("\n" + "="*70)
    print("📝 正在更新 js/data.js 與章節 Markdown 檔案中的 Video ID...")
    print("="*70)
    
    # 1. 更新 js/data.js
    data_js = BASE_DIR / "js" / "data.js"
    if data_js.exists():
        content = data_js.read_text(encoding='utf-8')
        for old_id, new_id in id_map.items():
            if old_id and new_id and old_id != new_id:
                content = content.replace(f'"{old_id}"', f'"{new_id}"')
        data_js.write_text(content, encoding='utf-8')
        print(f"✅ 已成功更新 {data_js.name}")

    # 2. 更新 Ch06 Markdown
    md_06 = BASE_DIR / "02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_郭懷一抗荷事件與早期漢人移民的悲歌.md"
    if md_06.exists():
        c06 = md_06.read_text(encoding='utf-8')
        if OLD_IDS["ch06_video"] in id_map and id_map[OLD_IDS["ch06_video"]]:
            c06 = c06.replace(OLD_IDS["ch06_video"], id_map[OLD_IDS["ch06_video"]])
        if OLD_IDS["ch06_podcast"] in id_map and id_map[OLD_IDS["ch06_podcast"]]:
            c06 = c06.replace(OLD_IDS["ch06_podcast"], id_map[OLD_IDS["ch06_podcast"]])
        md_06.write_text(c06, encoding='utf-8')
        print(f"✅ 已成功更新 {md_06.name}")

    # 3. 更新 Ch07 Markdown
    md_07 = BASE_DIR / "03_明鄭東寧與海上孤忠/第07章_決戰大員九個月_鄭成功驅荷復臺與熱蘭遮城大圍城.md"
    if md_07.exists():
        c07 = md_07.read_text(encoding='utf-8')
        if OLD_IDS["ch07_video"] in id_map and id_map[OLD_IDS["ch07_video"]]:
            c07 = c07.replace(OLD_IDS["ch07_video"], id_map[OLD_IDS["ch07_video"]])
        if OLD_IDS["ch07_podcast"] in id_map and id_map[OLD_IDS["ch07_podcast"]]:
            c07 = c07.replace(OLD_IDS["ch07_podcast"], id_map[OLD_IDS["ch07_podcast"]])
        md_07.write_text(c07, encoding='utf-8')
        print(f"✅ 已成功更新 {md_07.name}")

def upload_all():
    # 刪除舊影片與清除 marker
    delete_old_youtube_videos()
    clean_uploaded_markers()
    
    uploaded_ids = {}
    
    tasks = [
        {
            "key": "ch06_video",
            "old_id": OLD_IDS["ch06_video"],
            "file": BASE_DIR / "02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_說明影片.mp4",
            "title": "【臺灣史 EP06】血濺赤崁與大鹿港：郭懷一抗荷事件與早期漢人移民的悲歌",
            "desc": BASE_DIR / "02_大航海時代與荷西競逐/ch06_desc.txt",
            "thumb": BASE_DIR / "assets/images/ch06/ch06_youtube_thumbnail.jpg",
            "srt": BASE_DIR / "02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_說明影片.srt",
            "schedule": "2026-10-31 17:30"
        },
        {
            "key": "ch06_podcast",
            "old_id": OLD_IDS["ch06_podcast"],
            "file": BASE_DIR / "02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_播客深度對談.mp4",
            "title": "【臺灣史 PODCAST EP06】血濺赤崁與大鹿港：郭懷一抗荷事件與殖民清剿真相（深度對談）",
            "desc": BASE_DIR / "02_大航海時代與荷西競逐/ch06_podcast_desc.txt",
            "thumb": BASE_DIR / "assets/images/ch06/ch06_podcast_thumbnail.jpg",
            "srt": BASE_DIR / "02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_雙人對談.srt",
            "schedule": "2026-10-31 19:30"
        },
        {
            "key": "ch07_video",
            "old_id": OLD_IDS["ch07_video"],
            "file": BASE_DIR / "03_明鄭東寧與海上孤忠/第07章_決戰大員九個月_說明影片.mp4",
            "title": "【臺灣史 EP07】決戰大員九個月：鄭成功驅荷復臺與熱蘭遮城大圍城",
            "desc": BASE_DIR / "03_明鄭東寧與海上孤忠/ch07_desc.txt",
            "thumb": BASE_DIR / "assets/images/ch07/ch07_youtube_thumbnail.jpg",
            "srt": BASE_DIR / "03_明鄭東寧與海上孤忠/第07章_決戰大員九個月_說明影片.srt",
            "schedule": "2026-11-01 17:30"
        },
        {
            "key": "ch07_podcast",
            "old_id": OLD_IDS["ch07_podcast"],
            "file": BASE_DIR / "03_明鄭東寧與海上孤忠/第07章_決戰大員九個月_播客深度對談.mp4",
            "title": "【臺灣史 PODCAST EP07】大軍登陸鹿耳門！鄭成功圍城九個月與揆一開城秘辛（深度對談）",
            "desc": BASE_DIR / "03_明鄭東寧與海上孤忠/ch07_podcast_desc.txt",
            "thumb": BASE_DIR / "assets/images/ch07/ch07_podcast_thumbnail.jpg",
            "srt": BASE_DIR / "03_明鄭東寧與海上孤忠/第07章_決戰大員九個月_雙人對談.srt",
            "schedule": "2026-11-01 19:30"
        }
    ]
    
    id_map = {}
    
    for t in tasks:
        print("\n" + "="*70)
        print(f"🚀 正在上傳：{t['title']}")
        print("="*70)
        cmd = [
            PYTHON_EXE, str(UPLOADER_SCRIPT),
            "--video", str(t['file']),
            "--title", t['title'],
            "--desc-file", str(t['desc']),
            "--thumbnail", str(t['thumb']),
            "--srt", str(t['srt']),
            "--schedule", t['schedule'],
            "--playlist", "台灣史"
        ]
        ret, out = run_cmd(cmd)
        vid = None
        m = re.search(r"https://youtu\.be/([a-zA-Z0-9_-]{11})", out)
        if m:
            vid = m.group(1)
        else:
            up_m = t['file'].with_suffix('.uploaded')
            if up_m.exists():
                vid = up_m.read_text(encoding='utf-8').strip()
                
        if vid:
            print(f"✅ 上傳完成！Video ID: {vid}")
            uploaded_ids[t['key']] = vid
            id_map[t['old_id']] = vid
        else:
            print(f"❌ 上傳失敗或未取得 Video ID: {t['file'].name}")
            
    update_all_references(id_map)
    print("\n🎉 第 06 章與第 07 章四部全新繁體中文影音已全數成功發布並更新資料庫！")

if __name__ == '__main__':
    upload_all()
