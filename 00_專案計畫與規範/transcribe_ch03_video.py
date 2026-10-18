# -*- coding: utf-8 -*-
"""
第03章 說明影片 音訊轉錄腳本
使用 faster-whisper (CPU int8, 8 threads)
注入 Chapter 03 臺灣史專用詞庫，產出詞級時間戳 JSON
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
    input_media = "01_史前文明與南島之源/第03章_部落聯盟與土地精靈_說明影片.mp4"
    output_json = "01_史前文明與南島之源/whisper_words_ch03_video.json"
    
    prompt = (
        "臺灣史, 史前文明, 原住民族, 大肚王國, Middag, 甘馬轄阿興, 甘馬轄馬洛, Camachat, 華達旺, Quataong, "
        "拍瀑拉族, 巴布薩族, 巴宰族, 洪雅族, 大肚社, 沙轆社, 牛罵社, 彼得文伯恩, Pieter Boon, "
        "熱蘭遮城日誌, 臺海使槎錄, 黃叔璥, 劉國軒, 排灣族, 魯凱族, 石板屋, 百步蛇, 五年祭, "
        "阿美族, 卑南族, 太巴塱, 年齡階級, Kapah, 青年會所, Sfi, 豐年祭, 大獵祭, "
        "泰雅族, 太魯閣族, Gaga, 祖訓, 文面, 彩虹橋, 布農族, 鄒族, 八部合音, Pasibutbut, 小米祭曆, Dihanin"
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
    
    print(f"[*] 影片總長度：{info.duration:.1f} 秒 (~{info.duration/60:.1f} 分鐘)")
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
        
        if seg_count % 15 == 0:
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
