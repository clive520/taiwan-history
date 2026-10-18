# -*- coding: utf-8 -*-
"""
第07章 播客深度對談 音訊轉錄腳本
使用 faster-whisper (CPU int8, 8 threads)
注入 Chapter 07 臺灣史專用詞庫，產出詞級時間戳 JSON
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
    input_media = "03_明鄭東寧與海上孤忠/第07章_決戰大員九個月_雙人對談.m4a"
    output_json = "03_明鄭東寧與海上孤忠/whisper_words_ch07_podcast.json"
    
    prompt = (
        "臺灣史, 鄭成功, 國姓爺, Koxinga, 延平王, 朱成功, 揆一, Frederick Coyett, "
        "荷蘭東印度公司, VOC, 熱蘭遮城, Fort Zeelandia, 普羅民遮城, Fort Provintia, "
        "赤崁樓, 安平古堡, 鹿耳門, 臺江內海, 禾寮港, 柴頭港, 北線尾, 何斌, 馬德夫, "
        "Thomas Pedel, 貓難實叮, Jacobus Valentyn, 陳澤, 馬信, 甘輝, 黃廷, 范德蘭, "
        "Dirk van der Laan, 烏特勒支碉堡, Fort Utrecht, 拉迪斯, Hans Jeuriaen Radis, "
        "亨布魯克, Antonius Hambroek, 赫克托號, Hector, 格拉弗蘭號, Graveland, "
        "白鷺號, Vink, 瑪利亞號, Maria, 柯克肯號, Koukerke, 籐牌軍, 滾刀, "
        "莫里斯方陣, 葡萄彈, 紅夷大砲, 遷界令, 東都承天府, 天興縣, 萬年縣, 屯田制, "
        "左營, 前鎮, 新營, 柳營, 林鳳營"
    )
    
    model_size = "medium"
    print(f"[*] 正在初始化 Faster-Whisper ({model_size}, CPU int8, 8 threads)...", flush=True)
    start_t = time.time()
    
    model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=8)
    
    print(f"[*] 開始轉錄：{input_media}", flush=True)
    print(f"[*] 專用提示詞：{prompt}", flush=True)
    
    segments, info = model.transcribe(
        input_media,
        language="zh",
        initial_prompt=prompt,
        word_timestamps=True,
        beam_size=1,
        vad_filter=True
    )
    
    print(f"[*] 音訊總長度：{info.duration:.1f} 秒 (~{info.duration/60:.1f} 分鐘)", flush=True)
    print(f"[*] 辨識語言：{info.language}", flush=True)
    
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
        
        if seg_count % 20 == 0:
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
    print(f"\n[✓] 轉錄完成！總耗時: {elapsed:.1f} 秒", flush=True)
    print(f"[✓] 輸出檔案: {output_json}", flush=True)
    print(f"[✓] 總識別段落數: {len(segment_list)}，總單字數: {len(words_list)}", flush=True)

if __name__ == "__main__":
    run()
