# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 07 章 雙軌音訊 Faster-Whisper 語音轉錄提取腳本
- 說明影片：第07章_甘甜的舌尖密碼_說明影片.mp4
- 播客對談：food_ch07_podcast_deepdive.m4a
使用 Faster-Whisper (medium 模型, cpu_threads=8, compute_type=int8)
"""
import sys
import os
import json
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

from faster_whisper import WhisperModel

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH07_DIR = BASE_DIR / "舌尖上的臺灣" / "02_唐山渡海與閩粵交融"

VID_FILE = CH07_DIR / "第07章_甘甜的舌尖密碼_說明影片.mp4"
POD_FILE = CH07_DIR / "food_ch07_podcast_deepdive.m4a"

RAW_VID_JSON = CH07_DIR / "whisper_raw_video.json"
RAW_POD_JSON = CH07_DIR / "whisper_raw_podcast.json"

def transcribe_file(model, media_path, out_json_path, label):
    print(f"\n" + "="*70)
    print(f"🎙️ 開始轉錄 {label}：{media_path.name}")
    print("="*70)
    t0 = time.time()
    
    segments, info = model.transcribe(
        str(media_path),
        beam_size=5,
        language="zh",
        condition_on_previous_text=False,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=400)
    )
    
    print(f"偵測語言: {info.language} (機率: {info.language_probability:.2f})")
    print(f"媒體總長: {info.duration:.2f} 秒")
    
    seg_list = []
    count = 0
    for seg in segments:
        count += 1
        seg_data = {
            "id": seg.id,
            "start": seg.start,
            "end": seg.end,
            "text": seg.text,
            "words": [{"word": w.word, "start": w.start, "end": w.end, "probability": w.probability} for w in (seg.words or [])]
        }
        seg_list.append(seg_data)
        if count % 25 == 0 or count == 1:
            print(f"[{seg.start:06.2f}s -> {seg.end:06.2f}s] {seg.text.strip()}")
            
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump({"duration": info.duration, "segments": seg_list}, f, ensure_ascii=False, indent=2)
        
    cost = time.time() - t0
    print(f"✅ {label} 轉錄完成！共 {len(seg_list)} 句，耗時 {cost:.1f} 秒。已寫入：{out_json_path.name}")

def main():
    print(f"🚀 初始化 Faster-Whisper (medium 模型, cpu_threads=8, int8)...")
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)

    if VID_FILE.exists():
        transcribe_file(model, VID_FILE, RAW_VID_JSON, "說明短片")
    else:
        print(f"❌ 找不到說明短片：{VID_FILE}")

    if POD_FILE.exists():
        transcribe_file(model, POD_FILE, RAW_POD_JSON, "播客長片")
    else:
        print(f"❌ 找不到播客音訊：{POD_FILE}")

if __name__ == "__main__":
    main()
