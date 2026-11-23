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
CH15_DIR = BASE_DIR / "舌尖上的臺灣" / "05_島嶼綻放與世界舞台"
POD_FILE = CH15_DIR / "第15章_當代風土的米其林交響_雙人對談.m4a"
RAW_POD_JSON = CH15_DIR / "whisper_raw_podcast.json"

def main():
    if not POD_FILE.exists():
        print(f"❌ 音訊檔案不存在：{POD_FILE}")
        sys.exit(1)

    print("🧠 載入 Faster-Whisper (medium 模型, cpu_threads=8, int8)...")
    t0 = time.time()
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)

    print(f"🎙️ 開始轉錄播客對談：{POD_FILE.name}")
    segments, info = model.transcribe(
        str(POD_FILE),
        beam_size=5,
        language="zh",
        condition_on_previous_text=False,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=400)
    )
    print(f"偵測語言: {info.language} (信心度: {info.language_probability:.2f})")
    print(f"媒體總長: {info.duration:.2f} 秒 ({info.duration/60:.2f} 分鐘)")

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
            print(f"  [{seg.start:6.2f}s -> {seg.end:6.2f}s] {seg.text}")

    with open(RAW_POD_JSON, "w", encoding="utf-8") as f:
        json.dump(seg_list, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - t0
    print(f"\n✅ 播客對談轉錄完成！共 {len(seg_list)} 句，耗時 {elapsed:.1f} 秒，存至 {RAW_POD_JSON.name}")

if __name__ == "__main__":
    main()
