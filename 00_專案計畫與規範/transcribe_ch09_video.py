# -*- coding: utf-8 -*-
"""
第09章 說明影片 音訊轉錄腳本
使用 faster-whisper (CPU int8, 8 threads)
注入 Chapter 09 臺灣史專用詞庫，產出詞級時間戳 JSON
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
    input_media = "03_明鄭東寧與海上孤忠/第09章_澎湖海戰與帝國落幕_說明影片.mp4"
    output_json = "03_明鄭東寧與海上孤忠/whisper_words_ch09_video.json"
    
    prompt = (
        "臺灣史, 澎湖海戰, 施琅, 劉國軒, 鄭克塽, 鄭克臧, 鄭克𡒉, 鄭經, 馮錫範, 姚啟聖, 李光地, 康熙帝, "
        "恭陳臺灣棄留疏, 東寧之變, 北園別館, 延平王廟, 八罩島, 望安, 娘媽宮, 馬公港, 風櫃尾砲台, "
        "雞籠嶼, 牛心灣, 西嶼, 吼門水道, 五爪開花, 鳥船, 趕繒船, 雙帆艍船, 紅夷大砲, 佛郎機, 噴筒, "
        "藍理, 曾成, 林賢, 董義, 陳蟒, 魏明, 林陞, 江勝, 承天府, 安平鎮, 鹿耳門, 臺灣府, 臺灣縣, "
        "鳳山縣, 諸羅縣, 臺灣分巡道, 臺灣總兵, 遷界令, 展界復界, 棄留臺灣廷議, 一府三縣"
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
    for segment in segments:
        seg_count += 1
        segment_list.append({
            "id": segment.id,
            "seek": segment.seek,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })
        full_text.append(segment.text)
        
        if segment.words:
            for w in segment.words:
                words_list.append({
                    "word": w.word,
                    "start": w.start,
                    "end": w.end,
                    "probability": w.probability
                })
        
        if seg_count % 10 == 0:
            print(f"[{segment.end:.1f}s / {info.duration:.1f}s] {segment.text}", flush=True)
            
    total_time = time.time() - start_t
    print(f"[OK] 轉錄完成！共 {len(words_list)} 個詞，耗時 {total_time:.1f} 秒", flush=True)
    
    result_data = {
        "media": input_media,
        "duration": info.duration,
        "language": info.language,
        "full_text": "".join(full_text),
        "segments": segment_list,
        "words": words_list
    }
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
        
    print(f"[OK] 詞級時間戳已儲存至：{output_json}", flush=True)

if __name__ == "__main__":
    run()
