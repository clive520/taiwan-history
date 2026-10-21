# -*- coding: utf-8 -*-
"""
第10章 雙人對談音訊 轉錄腳本
使用 faster-whisper (CPU int8, 8 threads)
注入 Chapter 10 臺灣史專用詞庫，產出詞級時間戳 JSON
"""
import sys
import os
import json
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from pathlib import Path
from faster_whisper import WhisperModel

def run():
    base_dir = Path(__file__).resolve().parent.parent
    input_media = str(base_dir / "04_清領時代的拓墾烽火與變革/第10章_唐山過臺灣的黑水溝血淚_雙人對談.m4a")
    output_json = str(base_dir / "04_清領時代的拓墾烽火與變革/whisper_words_ch10_podcast.json")
    
    prompt = (
        "臺灣史, 唐山過臺灣, 黑水溝, 六死三留一回頭, 渡臺禁令, 渡臺三禁, 照單審查, 嚴禁攜眷, 粵東客民, "
        "裨海紀遊, 郁永河, 臺海使槎錄, 黃叔璥, 東征集, 藍鼎元, 諸羅縣志, 周鍾瑄, "
        "羅漢腳, 放生, 灌水, 種芋頭, 壓艙底, 落漈, 牽水藏, "
        "墾首, 墾號, 墾照, 田底權, 田面權, 一田二主, 大租戶, 小租戶, 現耕佃農, 施侯大租, 靖海侯施琅, "
        "八堡圳, 施厝圳, 施世榜, 施長齡, 林先生, 石笱導水法, 竹篾筍籠, 濁水溪, 鼻仔頭, 二水, 彰化平原, 林先生廟, "
        "瑠公圳, 郭錫瑠, 瑠公, 郭元芬, 新店溪, 碧潭, 青潭口, 開硿, 木筧, 景美溪, 大加蚋堡, 大安, 艋舺, 錫口, "
        "有應公, 萬善爺, 百姓公, 義塚, 普渡祭典"
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
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })
        full_text.append(segment.text)
        
        if segment.words:
            for w in segment.words:
                words_list.append({
                    "word": w.word,
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 3)
                })
        else:
            words_list.append({
                "word": segment.text,
                "start": round(segment.start, 3),
                "end": round(segment.end, 3),
                "probability": 1.0
            })
            
        if seg_count % 10 == 0:
            print(f"  [進度] 已處理 {seg_count} 段，目前時間點：{segment.end:.1f}s", flush=True)
            
    cost_t = time.time() - start_t
    print(f"[*] 轉錄完成！總計段落數：{seg_count}，提取詞數：{len(words_list)}，耗時：{cost_t:.1f} 秒", flush=True)
    
    result = {
        "metadata": {
            "media": input_media,
            "duration": info.duration,
            "language": info.language,
            "model": model_size,
            "words_count": len(words_list),
            "segments_count": len(segment_list),
            "transcribed_at": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "full_text": "".join(full_text),
        "segments": segment_list,
        "words": words_list
    }
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        
    print(f"[OK] 詞級時間戳 JSON 已成功寫入：{output_json}", flush=True)

if __name__ == "__main__":
    run()
