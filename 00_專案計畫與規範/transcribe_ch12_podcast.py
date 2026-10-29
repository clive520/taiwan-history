# -*- coding: utf-8 -*-
"""
第12章 雙人對談播客 音訊轉錄腳本
使用 faster-whisper (CPU int8, 8 threads)
注入 Chapter 12 臺灣史專用詞庫，產出詞級時間戳 JSON
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
    input_media = str(base_dir / "04_清領時代的拓墾烽火與變革/第12章_開港通商與現代化急先鋒_雙人對談.m4a")
    output_json = str(base_dir / "04_清領時代的拓墾烽火與變革/whisper_words_ch12_podcast.json")
    
    prompt = (
        "臺灣史, 開港通商, 天津條約, 北京條約, 淡水港, 滬尾, 安平港, 打狗港, 雞籠港, 五大洋行, 德記洋行, 寶順洋行, 怡記洋行, 和記洋行, 東興洋行, 唻記洋行, "
        "約翰·陶德, John Dodd, 李春生, 買辦, 臺灣三寶, 福爾摩沙烏龍茶, Formosa Oolong, 包種茶, 樟腦, 大稻埕, 千秋街, 六館街, 迪化街, 經濟重心北移, "
        "牡丹社事件, 八瑤灣, 宮古島, 高士佛社, 牡丹社, 排灣族, 阿祿古, 西鄉從道, 石門古戰場, 石門之戰, 沈葆楨, 億載金城, 二鯤鯓砲臺, 阿姆斯特朗巨砲, 白乃爾, 日意格, "
        "開山撫番, 八通關古道, 吳光亮, 飛虎軍, 蘇花古道, 羅大春, 崑崙坳古道, 張其光, 恆春縣, 臺北府, 渡臺禁令廢止, 開山禁令, "
        "中法戰爭, 清法戰爭, 孤拔, Amédée Courbet, 利士比, 劉銘傳, 淮軍, 銘軍, 棄基保滬, 滬尾之役, 淡水大捷, 孫開華, 章高元, 曹志忠, 林朝棟, 棟軍, 霧峰林家, "
        "沙崙海灘, 油車口, 林投樹叢, 觸發水雷, 沉石封江, 臺灣建省, 首任巡撫, 臺灣行省, 鐵路, 獅球嶺隧道, 曠宇天開, 騰雲號, 御風號, 霍恩索倫, 馬修, 莫里生, "
        "海底電纜, 川石島, 臺灣郵政總局, 臺灣郵票, 臺北電燈, 西學堂, 洋務學堂, 清賦事業, 減四留六, 大租戶, 小租戶, 施九緞事件, 撫墾總局, 大嵙崁戰役, 邵友濂"
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
            
        if seg_count % 20 == 0:
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
