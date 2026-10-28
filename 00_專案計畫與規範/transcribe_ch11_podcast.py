# -*- coding: utf-8 -*-
"""
第11章 雙人對談播客 音訊轉錄腳本
使用 faster-whisper (CPU int8, 8 threads)
注入 Chapter 11 臺灣史專用詞庫，產出詞級時間戳 JSON
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
    input_media = str(base_dir / "04_清領時代的拓墾烽火與變革/第11章_三年一反五年一亂_雙人對談.m4a")
    output_json = str(base_dir / "04_清領時代的拓墾烽火與變革/whisper_words_ch11_podcast.json")
    
    prompt = (
        "臺灣史, 清領時代, 官逼民反, 三年一反五年一亂, 班兵制度, 綠營標營, 輪戍制, 流官制, 羅漢腳, 渡臺禁令, "
        "朱一貴, 鴨母王, 鴨母寮, 內門, 大岡山, 中興王, 永和, 王珍, 杜君英, 檳榔林, 施世驃, 藍廷珍, 藍鼎元, 平臺紀略, 東征集, 貓兒干, "
        "林爽文, 天地會, 洪門, 嚴煙, 大里杙, 順天, 莊大田, 鳳山縣, 諸羅城, 柴大紀, 董啟埏, 諸羅縣志, "
        "福康安, 海蘭察, 巴圖魯, 欽定平定臺灣紀略, 嘉義, 嘉義縣, 嘉義公園, 贔屓馱碑, 十全武功, 老衢崎, 集集埔, 小半天, "
        "分類械鬥, 漳泉械鬥, 閩粵械鬥, 頂下郊拚, 艋舺, 大稻埕, 三邑人, 同安人, 祖師廟, 龍山寺, 開漳聖王, 三山國王, 保生大帝, 廣澤尊王, "
        "以漢制漢, 義民, 義民爺, 褒忠, 新埔褒忠義民廟, 林先坤, 六堆, 六堆忠義亭, 李直三, 黑色義民旗, 挑擔奉飯, 桑梓認同"
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
