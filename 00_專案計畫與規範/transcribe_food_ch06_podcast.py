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
CH06_DIR = BASE_DIR / "舌尖上的臺灣" / "02_唐山渡海與閩粵交融"
POD_FILE = CH06_DIR / "food_ch06_podcast_deepdive.m4a"
RAW_POD_JSON = CH06_DIR / "whisper_raw_podcast.json"

print(f"🚀 初始化 Faster-Whisper (medium 模型)...")
try:
    model = WhisperModel("medium", device="cuda", compute_type="float16")
    print("⚡ 使用 CUDA GPU 加速 (float16)")
except Exception as e:
    print(f"⚠️ CUDA 初始化失敗 ({e})，切換為 CPU 模式 (int8)")
    model = WhisperModel("medium", device="cpu", compute_type="int8")

print(f"\n🎙️ 開始轉錄播客長片：{POD_FILE.name}")
t0 = time.time()
segments, info = model.transcribe(
    str(POD_FILE),
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
    if count % 30 == 0 or count <= 3:
        print(f"[{seg.start:06.2f}s -> {seg.end:06.2f}s] {seg.text.strip()}")

with open(RAW_POD_JSON, "w", encoding="utf-8") as f:
    json.dump({"duration": info.duration, "segments": seg_list}, f, ensure_ascii=False, indent=2)

cost = time.time() - t0
print(f"✅ 播客轉錄完成！共 {len(seg_list)} 句，耗時 {cost:.1f} 秒。已寫入：{RAW_POD_JSON.name}")
