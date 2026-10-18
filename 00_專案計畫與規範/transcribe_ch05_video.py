# -*- coding: utf-8 -*-
"""
第05章 說明影片 音訊轉錄腳本
使用 faster-whisper (CPU int8, 8 threads)
注入 Chapter 05 臺灣史專用詞庫，產出詞級時間戳 JSON
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
    input_media = "02_大航海時代與荷西競逐/第05章_聖多明哥的十字架_說明影片.mp4"
    output_json = "02_大航海時代與荷西競逐/whisper_words_ch05_video.json"
    
    prompt = (
        "臺灣史, 大航海時代, 西班牙帝國, 菲律賓都督府, 馬尼拉大帆船, 伐爾得斯, Antonio Carreño Valdés, "
        "阿爾卡拉索, Juan de Alcarazo, 波提紐, Gonzalo Portillo, 聖薩爾瓦多城, Fort San Salvador, "
        "退守堡, El Retiro, 看守堡, El Cubo, 和平島, 社寮島, 諸聖修道院, Todos los Santos, "
        "聖多明哥城, Fort San Domingo, 淡水紅毛城, 艾斯基維, Jacinto Esquivel, 淡水語辭典, 巴賽語, "
        "巴賽族, 凱達格蘭族, 噶瑪蘭族, 哆囉滿, Turoboan, 砂金, 三貂角, Santiago, 哈魯斯, Hendrik Harouse, "
        "荷蘭東印度公司, VOC, 硫磺貿易, 考古發掘"
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
        beam_size=1,
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
