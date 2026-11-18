# -*- coding: utf-8 -*-
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
CH10_DIR = BASE_DIR / "舌尖上的臺灣" / "03_帝國之眼與東洋滋味"
VID_FILE = CH10_DIR / "第10章_山嵐間的東方美人_說明影片.mp4"
RAW_VID_JSON = CH10_DIR / "whisper_raw_video.json"

print(f"🚀 初始化 Faster-Whisper (medium 模型, cpu_threads=8, int8)...")
model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)

print(f"🎙️ 開始轉錄說明短片：{VID_FILE.name}")
t0 = time.time()
segments, info = model.transcribe(
    str(VID_FILE),
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
    if count % 20 == 0 or count == 1:
        print(f"  [{count}] {seg.start:.2f}s -> {seg.end:.2f}s: {seg.text}")

with open(RAW_VID_JSON, "w", encoding="utf-8") as f:
    json.dump({
        "info": {
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration
        },
        "segments": seg_list
    }, f, ensure_ascii=False, indent=2)

print(f"✅ 說明短片轉錄完成！耗時 {time.time()-t0:.2f} 秒，共 {len(seg_list)} 個區間")
