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
CH11_DIR = BASE_DIR / "舌尖上的臺灣" / "04_大江大海與眷村融合"
VID_FILE = CH11_DIR / "第11章_那一碗鄉愁的紅湯_說明影片.mp4"
POD_FILE = CH11_DIR / "第11章_那一碗鄉愁的紅湯_雙人對談.m4a"

RAW_VID_JSON = CH11_DIR / "whisper_raw_video.json"
RAW_POD_JSON = CH11_DIR / "whisper_raw_podcast.json"

def transcribe_file(model, media_path, out_json_path, label):
    print(f"\n🎙️ 開始轉錄 {label}：{media_path.name}")
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
    print(f"偵測語言: {info.language} (信心度: {info.language_probability:.2f})")
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
            print(f"  [{seg.start:6.2f}s -> {seg.end:6.2f}s] {seg.text}")

    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(seg_list, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - t0
    print(f"✅ {label} 轉錄完成！共 {len(seg_list)} 句，耗時 {elapsed:.1f} 秒，存至 {out_json_path.name}")

def main():
    if not VID_FILE.exists():
        print(f"❌ 視訊檔案不存在：{VID_FILE}")
        sys.exit(1)
    if not POD_FILE.exists():
        print(f"❌ 音訊檔案不存在：{POD_FILE}")
        sys.exit(1)

    print("🧠 載入 Faster-Whisper (medium 模型, cpu_threads=8, int8)...")
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)

    transcribe_file(model, VID_FILE, RAW_VID_JSON, "說明影片")
    transcribe_file(model, POD_FILE, RAW_POD_JSON, "播客對談")
    print("\n🎉 全部轉錄任務圓滿完成！")

if __name__ == "__main__":
    main()
