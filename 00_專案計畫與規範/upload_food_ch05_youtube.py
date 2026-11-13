# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 05 章 YouTube 雙軌排程自動上架發布腳本
- 說明短片排程：2026-11-17 17:30
- 播客長片排程：2026-11-17 19:30
- 官方清單：舌尖上的臺灣 (PLAFdajbNY8qg)
- 自動更新 js/data-food.js、舌尖上的臺灣/js/data.js 與專題長文導讀模組
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
FOOD_DIR = BASE_DIR / "舌尖上的臺灣" / "02_唐山渡海與閩粵交融"
THUMB_DIR = BASE_DIR / "assets" / "images" / "food_ch05"

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
    audio_release_url = "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/food_ch05_podcast_deepdive.m4a"
    
    # 1. 更新 js/data-food.js 與 舌尖上的臺灣/js/data.js
    db_paths = [
        BASE_DIR / "js" / "data-food.js",
        BASE_DIR / "舌尖上的臺灣" / "js" / "data.js"
    ]
    
    for db_path in db_paths:
        if not db_path.exists():
            continue
        c = db_path.read_text(encoding='utf-8')
        c_norm = c.replace("\r\n", "\n")
        
        target_pattern = r'(\{\s*"id":\s*"ch05",[\s\S]*?"status":\s*)"planned"([\s\S]*?"file":\s*"第05章_水牛禁忌與清晨的甘甜_臺南溫體牛肉湯的破戒身世與屠宰冷鏈微革命\.md",)'
        
        replacement = (
            r'\1"published",\n'
            f'    "bannerImage": "assets/images/food_ch05/food_ch05_hero_banner.jpg",\n'
            f'    "youtube": "{v1_id}",\n'
            f'    "podcastYoutube": "{v2_id}",\n'
            f'    "audioFile": "{audio_release_url}",\n'
            r'\2'
        )
        
        if re.search(target_pattern, c_norm):
            c_new = re.sub(target_pattern, replacement, c_norm)
            db_path.write_text(c_new, encoding='utf-8')
            print(f"✅ 已成功更新 {db_path.relative_to(BASE_DIR)}！")
        else:
            print(f"[WARN] 未能在 {db_path.name} 找到 ch05 正則匹配位置，嘗試替代模式...")
            # 寬鬆替換
            p2 = r'("id":\s*"ch05"[\s\S]*?"status":\s*)"planned"'
            if re.search(p2, c_norm):
                c_new = re.sub(p2, r'\1"published"', c_norm)
                # 插入欄位
                insert_fields = (
                    f'\n    "bannerImage": "assets/images/food_ch05/food_ch05_hero_banner.jpg",\n'
                    f'    "youtube": "{v1_id}",\n'
                    f'    "podcastYoutube": "{v2_id}",\n'
                    f'    "audioFile": "{audio_release_url}",'
                )
                c_new = re.sub(r'("id":\s*"ch05"[\s\S]*?"status":\s*"published",)', r'\1' + insert_fields, c_new)
                db_path.write_text(c_new, encoding='utf-8')
                print(f"✅ 寬鬆匹配成功更新 {db_path.name}！")

    # 2. 更新 Markdown 導讀影音超連結
    md_file = FOOD_DIR / "第05章_水牛禁忌與清晨的甘甜_臺南溫體牛肉湯的破戒身世與屠宰冷鏈微革命.md"
    if md_file.exists():
        md_c = md_file.read_text(encoding='utf-8')
        md_c = md_c.replace("https://youtu.be/pending_food_ch05_video", f"https://youtu.be/{v1_id}")
        md_c = md_c.replace("https://youtu.be/pending_food_ch05_podcast", f"https://youtu.be/{v2_id}")
        md_file.write_text(md_c, encoding='utf-8')
        print(f"✅ 已成功更新專題長文導讀模組 Video ID：{md_file.name}！")

def main():
    # 說明短片設定
    v1_file = FOOD_DIR / "第05章_水牛禁忌與清晨的甘甜_說明影片.mp4"
    v1_title = "【舌尖上的臺灣 EP05】水牛禁忌與清晨的甘甜！善化牛墟試牛四法、溫體牛Pre-rigor生化保水性與98°C生沖工藝"
    v1_desc = FOOD_DIR / "food_ch05_desc.txt"
    v1_thumb = THUMB_DIR / "food_ch05_youtube_thumbnail.jpg"
    v1_srt = FOOD_DIR / "第05章_水牛禁忌與清晨的甘甜_說明影片.srt"
    v1_schedule = "2026-11-17 17:30"
    
    print("\n" + "="*70)
    print("🚀 [1/2] 正在上傳第 05 章 說明影片...")
    print("="*70)
    cmd1 = [
        PYTHON_EXE, str(UPLOADER_SCRIPT),
        "--video", str(v1_file),
        "--title", v1_title,
        "--desc-file", str(v1_desc),
        "--thumbnail", str(v1_thumb),
        "--srt", str(v1_srt),
        "--schedule", v1_schedule,
        "--playlist", "舌尖上的臺灣"
    ]
    v1_uploaded = FOOD_DIR / "第05章_水牛禁忌與清晨的甘甜_說明影片.uploaded"
    if v1_uploaded.exists():
        v1_id = v1_uploaded.read_text(encoding='utf-8').strip()
        print(f"\n🎉 影片 1 已上傳過，讀取 Video ID: {v1_id}")
    else:
        ret1, out1 = run_cmd(cmd1)
        if ret1 != 0:
            print("[ERROR] 影片 1 上傳失敗！")
            return
            
        m1 = re.search(r"Video ID:\s*([a-zA-Z0-9_-]+)", out1, re.I) or re.search(r"影片 ID:\s*([a-zA-Z0-9_-]+)", out1)
        if not m1:
            print("[ERROR] 未能解析到 Video 1 ID！")
            return
        v1_id = m1.group(1)
        print(f"\n🎉 影片 1 上傳成功！Video ID: {v1_id}")
        v1_uploaded.write_text(v1_id, encoding='utf-8')

    # 播客深度對談設定
    v2_file = FOOD_DIR / "第05章_水牛禁忌與清晨的甘甜_播客深度對談.mp4"
    v2_title = "【舌尖上的臺灣 深度對談 EP05】水牛禁忌與清晨的甘甜：從敬牛不食、1960鐵牛退役潮到臺南溫體牛肉湯的生化分子革命"
    v2_desc = FOOD_DIR / "food_ch05_podcast_desc.txt"
    v2_thumb = THUMB_DIR / "food_ch05_podcast_thumbnail.jpg"
    v2_srt = FOOD_DIR / "第05章_水牛禁忌與清晨的甘甜_雙人對談.srt"
    v2_schedule = "2026-11-17 19:30"
    
    print("\n" + "="*70)
    print("🚀 [2/2] 正在上傳第 05 章 播客深度對談長片...")
    print("="*70)
    cmd2 = [
        PYTHON_EXE, str(UPLOADER_SCRIPT),
        "--video", str(v2_file),
        "--title", v2_title,
        "--desc-file", str(v2_desc),
        "--thumbnail", str(v2_thumb),
        "--srt", str(v2_srt),
        "--schedule", v2_schedule,
        "--playlist", "舌尖上的臺灣"
    ]
    v2_uploaded = FOOD_DIR / "第05章_水牛禁忌與清晨的甘甜_播客深度對談.uploaded"
    if v2_uploaded.exists():
        v2_id = v2_uploaded.read_text(encoding='utf-8').strip()
        print(f"\n🎉 影片 2 已上傳過，讀取 Video ID: {v2_id}")
    else:
        ret2, out2 = run_cmd(cmd2)
        if ret2 != 0:
            print("[ERROR] 影片 2 上傳失敗！")
            return
            
        m2 = re.search(r"Video ID:\s*([a-zA-Z0-9_-]+)", out2, re.I) or re.search(r"影片 ID:\s*([a-zA-Z0-9_-]+)", out2)
        if not m2:
            print("[ERROR] 未能解析到 Video 2 ID！")
            return
        v2_id = m2.group(1)
        print(f"\n🎉 影片 2 上傳成功！Video ID: {v2_id}")
        v2_uploaded.write_text(v2_id, encoding='utf-8')

    # 更新資料庫與長文導讀
    print("\n" + "="*70)
    print("📝 正在更新專案資料庫與長文導讀模組...")
    print("="*70)
    update_databases(v1_id, v2_id)
    print(f"\n✨ 第 05 章 雙軌排程發布與資料庫同步全部大功告成！")

if __name__ == "__main__":
    main()
