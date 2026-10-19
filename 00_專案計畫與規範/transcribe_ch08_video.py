# -*- coding: utf-8 -*-
"""
第08章 說明影片 音訊轉錄腳本
使用 faster-whisper (CPU int8, 8 threads)
注入 Chapter 08 臺灣史專用詞庫，產出詞級時間戳 JSON
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
    input_media = "03_明鄭東寧與海上孤忠/第08章_海外別立乾坤_說明影片.mp4"
    output_json = "03_明鄭東寧與海上孤忠/whisper_words_ch08_video.json"
    
    prompt = (
        "臺灣史, 鄭經, 陳永華, 鄭成功, 鄭襲, 鄭克臧, 鄭克塽, 馮錫範, 沈光文, 施琅, "
        "東寧王國, 承天府, 天興州, 萬年州, 諮議參軍, 東寧總制, 臺灣國王, 永曆, "
        "全臺首學, 臺南孔廟, 明倫堂, 大成殿, 國子學, 泮池, 營盤田, 官田, 文武官田, "
        "寓兵於農, 柳營, 查畝營, 林鳳營, 新營, 下營, 左鎮, 前鎮, 後勁, 右昌, 左營, "
        "瀨口, 天日曬鹽, 瓦盤鹽田, 糖廓, 燒磚瓦, 遷界令, 遷海令, 英國東印度公司, "
        "鄭英通商條約, 萬壽號, Bantam, King of Tywan, 山海五商, 龍湖巖, 三藩之亂, 東寧之變, 果毅後"
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
    print(f"\n[OK] 轉錄完成！總耗時: {total_time:.1f} 秒 (約 {total_time/60:.1f} 分鐘)", flush=True)
    print(f"[OK] 總提取詞數: {len(words_list)}, 總句數: {len(segment_list)}", flush=True)
    
    result_data = {
        "media_file": input_media,
        "duration": info.duration,
        "language": info.language,
        "transcribe_time_sec": total_time,
        "full_text": "".join(full_text),
        "segments": segment_list,
        "words": words_list
    }
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
        
    print(f"[OK] 詞級時間戳 JSON 已儲存：{output_json}", flush=True)

if __name__ == "__main__":
    run()
