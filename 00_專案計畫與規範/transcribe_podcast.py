# -*- coding: utf-8 -*-
"""
第01章 Podcast 23分鐘音訊轉錄腳本
使用 faster-whisper (CPU int8, 8 threads)
注入臺灣史專用詞庫，產出詞級時間戳 JSON
"""
import sys
import os
import json
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from faster_whisper import WhisperModel

def run():
    input_media = "01_史前文明與南島之源/第01章_黑潮上的遠古足跡_雙人對談.m4a"
    output_json = "01_史前文明與南島之源/whisper_words_ch01_podcast.json"
    
    prompt = (
        "臺灣史, 史前文明, 長濱文化, 八仙洞, 潮音洞, 海雷洞, "
        "宋文薰, 林朝棨, 舊石器時代晚期, 末次冰盛期, 臺灣海峽陸橋, "
        "淮河古菱齒象, 劍齒象, 左鎮動物群, 菜寮溪, 郭德鈴, 何傳坤, "
        "鹿間時夫, 佐倉朔, 左鎮人, AMS碳十四定年, 加速器質譜儀, "
        "砍砸器, 石片器, 骨角器, 先陶文化, 黑潮暖流"
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
            print(f"   已處理至段落 {seg_count}（當前進度：{seg.end:.1f}s / {info.duration:.1f}s）...")
    
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
