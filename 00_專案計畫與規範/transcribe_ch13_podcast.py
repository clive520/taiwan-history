# -*- coding: utf-8 -*-
"""
第13章 雙人對談播客 音訊轉錄腳本
使用 faster-whisper (CPU int8, 8 threads)
注入 Chapter 13 臺灣史專用詞庫，產出詞級時間戳 JSON
"""
import sys
import os
import json
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

from pathlib import Path
from faster_whisper import WhisperModel

def run():
    base_dir = Path(__file__).resolve().parent.parent
    input_media = str(base_dir / "05_日治時期的統治轉型與抗爭/第13章_乙未悲歌與武裝抗日_雙人對談.m4a")
    output_json = str(base_dir / "05_日治時期的統治轉型與抗爭/whisper_words_ch13_podcast.json")
    
    prompt = (
        "臺灣史, 馬關條約, 乙未戰爭, 臺灣民主國, 唐景崧, 丘逢甲, 劉永福, 藍地黃虎旗, 永清, 樺山資紀, 北白川宮能久親王, 近衛師團, 澳底登陸, 李春生, 辜顯榮, "
        "桃竹苗客家義軍, 吳湯興, 徐驤, 姜紹祖, 敢字營, 北埔金廣福, 安平鎮之役, 大嵙崁戰役, 尖筆山之役, 八卦山戰役, 吳彭年, 七星隊, 彰化城, 蕭壠之役, 曾文溪, "
        "德利士號, 巴克禮, 宋忠堅, 六三法, 匪徒刑罰令, 抗日三猛, 簡大獅, 大屯山, 柯鐵虎, 鐵國山, 雲林大屠殺, 林少貓, 萬丹, 後壁林, 噍吧哖事件, 西來庵事件, "
        "余清芳, 羅俊, 江定, 五福大帝, 大明慈悲國, 虎頭山之役, 玉井, 楠西, 臨時法院, 臺灣文化協會, 林獻堂, 蔣渭水"
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
        seg_data = {
            "id": segment.id,
            "seek": segment.seek,
            "start": round(segment.start, 3),
            "end": round(segment.end, 3),
            "text": segment.text.strip(),
            "words": []
        }
        full_text.append(segment.text.strip())
        
        if segment.words:
            for w in segment.words:
                word_entry = {
                    "word": w.word,
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 4)
                }
                seg_data["words"].append(word_entry)
                words_list.append(word_entry)
        
        segment_list.append(seg_data)
        if seg_count % 20 == 0:
            print(f"  [進度] 已處理 {seg_count} 段，目前時間點：{segment.end:.1f}s", flush=True)
            
    total_time = time.time() - start_t
    print(f"[*] 轉錄完成！總計段落數：{len(segment_list)}，提取詞數：{len(words_list)}，耗時：{total_time:.1f} 秒", flush=True)
    
    result = {
        "metadata": {
            "media_file": os.path.basename(input_media),
            "duration": round(info.duration, 3),
            "language": info.language,
            "transcribe_time_seconds": round(total_time, 2),
            "word_count": len(words_list),
            "segment_count": len(segment_list)
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
