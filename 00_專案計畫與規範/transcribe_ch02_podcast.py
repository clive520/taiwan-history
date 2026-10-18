# -*- coding: utf-8 -*-
"""
第02章 Podcast 雙人對談音訊轉錄腳本
使用 faster-whisper (CPU int8, 8 threads)
注入 Chapter 02 臺灣史專用詞庫，產出詞級時間戳 JSON
"""
import sys
import os
import json
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from faster_whisper import WhisperModel

def run():
    input_media = "01_史前文明與南島之源/第02章_大海是唯一的路徑_雙人對談.m4a"
    output_json = "01_史前文明與南島之源/whisper_words_ch02_podcast.json"
    
    prompt = (
        "臺灣史, 南島語族, 出臺灣說, 彼得·貝爾伍德, Peter Bellwood, "
        "白樂思, Robert Blust, 大坌坑文化, 卑南文化, 十三行文化, "
        "豐田閃玉, 臺灣玉, 雙獸頭形玉玦, 人獸形玉玦, 舷外浮筒獨木舟, "
        "Outrigger canoe, 馬來-玻里尼西亞語族, 巴士海峽, 凱達格蘭族, "
        "沙黃文化, Sa Huynh, 杜永洞, 洪曉純, 飯塚義之, 黑潮"
    )
    
    model_size = "medium"
    print(f"[*] 正在初始化 Faster-Whisper ({model_size}, CPU int8, 8 threads)...")
    start_t = time.time()
    
    model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=8)
    
    print(f"[*] 開始轉錄：{input_media}")
    print(f"[*] 專用提示詞：{prompt}")
    
    segments, info = model.transcribe(
        input_media,
        language="zh",
        initial_prompt=prompt,
        word_timestamps=True,
        beam_size=5,
        vad_filter=True
    )
    
    print(f"[*] 音訊總長度：{info.duration:.1f} 秒 (~{info.duration/60:.1f} 分鐘)")
    print(f"[*] 辨識語言：{info.language}")
    
    words_list = []
    full_text = []
    segment_list = []
    
    seg_count = 0
    for seg in segments:
        seg_count += 1
        full_text.append(seg.text)
        seg_words = []
        if seg.words:
            for w in seg.words:
                w_obj = {
                    "word": w.word,
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 3)
                }
                words_list.append(w_obj)
                seg_words.append(w_obj)
        
        segment_list.append({
            "id": seg_count,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text,
            "words": seg_words
        })
        
        if seg_count % 25 == 0:
            print(f"   已處理至段落 {seg_count}（當前進度：{seg.end:.1f}s / {info.duration:.1f}s）...", flush=True)
    
    result = {
        "text": "".join(full_text),
        "language": info.language,
        "duration": info.duration,
        "segments": segment_list,
        "words": words_list
    }
    
    os.makedirs(os.path.dirname(os.path.abspath(output_json)), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    elapsed = time.time() - start_t
    print(f"\n[✓] 轉錄完成！總耗時: {elapsed:.1f} 秒")
    print(f"[✓] 輸出檔案: {output_json}")
    print(f"[✓] 總識別段落數: {len(segment_list)}，總單字數: {len(words_list)}")

if __name__ == "__main__":
    run()
