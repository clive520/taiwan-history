# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 04 章 說明影片 語音轉錄與影視級自然語意 SRT 生成腳本
"""
import sys
import os
import json
import time
import re
from pathlib import Path
import jieba

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

from faster_whisper import WhisperModel

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH04_DIR = BASE_DIR / "舌尖上的臺灣" / "02_唐山渡海與閩粵交融"
VID_FILE = CH04_DIR / "第04章_一碗肉臊的百年身世_說明影片.mp4"
OUT_SRT = CH04_DIR / "第04章_一碗肉臊的百年身世_說明影片.srt"

PROMPT_TEXT = (
    "肉臊, 肉臊飯, 滷肉飯, 爌肉飯, 黑豬肉, 臺灣黑豬, 紅蔥頭, 紅蔥酥, 油蔥酥, 黑豆蔭油, "
    "五條港, 府城, 羅漢腳, 諸羅縣志, 臺灣府志, 安平縣雜記, 周鍾瑄, 高拱乾, "
    "陶缸日曬, 固態發酵, 黑豆麴, 青仁黑豆, 帶皮五花, 手工切丁, 肌纖維, 肌間脂肪, "
    "膠原蛋白, 明膠, 水解, 三螺旋結構, 梅納反應, 有機硫化物, 谷氨酸, 黏唇口感"
)

CUSTOM_WORDS = [
    "肉臊", "肉臊飯", "滷肉飯", "爌肉飯", "黑豬肉", "臺灣黑豬", "紅蔥頭", "紅蔥酥", "油蔥酥",
    "黑豆蔭油", "蔭油", "黑豆醬油", "五條港", "府城", "羅漢腳", "諸羅縣志", "臺灣府志",
    "安平縣雜記", "周鍾瑄", "高拱乾", "陶缸", "陶缸日曬", "固態發酵", "黑豆麴", "青仁黑豆",
    "帶皮五花", "三層肉", "手工切丁", "肌纖維", "肌間脂肪", "膠原蛋白", "明膠", "水解",
    "三螺旋結構", "梅納反應", "有機硫化物", "谷氨酸", "天門冬氨酸", "黏唇口感", "大井頭",
    "水仙宮", "接官亭"
]
for w in CUSTOM_WORDS:
    jieba.add_word(w)

CORRECTIONS = [
    (r"蜻蜓", "清廷"),
    (r"清景", "清廷"),
    (r"輕艇", "清廷"),
    (r"台([灣北市南中東中東南東東南])", r"臺\1"),
    (r"全台", "全臺"),
    (r"在台", "在臺"),
    (r"來台", "來臺"),
    (r"[臺台]灣", "臺灣"),
    (r"肉[燥噪][飯反]", "肉臊飯"),
    (r"滷肉[飯反]", "滷肉飯"),
    (r"爌肉[飯反]", "爌肉飯"),
    (r"肉[燥噪]", "肉臊"),
    (r"黑[豬猪]肉", "黑豬肉"),
    (r"紅[蔥葱][頭投]?", "紅蔥頭"),
    (r"紅[蔥葱]酥", "紅蔥酥"),
    (r"黑豆[蔭蔭]油", "黑豆蔭油"),
    (r"陶[缸剛]", "陶缸"),
    (r"諸羅縣志", "《諸羅縣志》"),
    (r"臺灣府志", "《臺灣府志》"),
    (r"安平縣雜記", "《安平縣雜記》"),
    (r"梅[納納]反應", "梅納反應"),
    (r"膠原蛋白", "膠原蛋白"),
    (r"明膠", "明膠"),
]

def format_timestamp(seconds: float) -> str:
    total_ms = int(round(seconds * 1000))
    hours = total_ms // 3600000
    rem = total_ms % 3600000
    minutes = rem // 60000
    rem = rem % 60000
    secs = rem // 1000
    ms = rem % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

def clean_text(text: str) -> str:
    t = text.strip()
    for pat, rep in CORRECTIONS:
        t = re.sub(pat, rep, t)
    t = re.sub(r'[，。！？、；：\s]+$', '', t)
    t = re.sub(r'^[，。！？、；：\s]+', '', t)
    t = t.replace('”', '').replace('"', '').replace("'", '').replace('（', '')
    t = t.replace('）', '').replace('(', '').replace(')', '').replace('—', '')
    t = t.replace('…', '').replace('～', '').replace('~', '')
    return t

def split_natural_sentences(words, min_chars=6, max_chars=18, max_pause=0.55):
    subtitles = []
    cur_words = []
    
    for i, w in enumerate(words):
        cur_words.append(w)
        cur_text = clean_text("".join([x.word for x in cur_words]))
        
        need_split = False
        if i < len(words) - 1:
            pause = words[i+1].start - w.end
            if pause >= max_pause and len(cur_text) >= min_chars:
                need_split = True
        else:
            need_split = True

        if len(cur_text) >= max_chars:
            need_split = True
            
        if any(p in w.word for p in ['。', '！', '？', '；', '\n']) and len(cur_text) >= min_chars:
            need_split = True

        if need_split and len(cur_text) > 0:
            start_time = cur_words[0].start
            end_time = cur_words[-1].end
            if end_time <= start_time:
                end_time = start_time + 0.5
            subtitles.append((start_time, end_time, cur_text))
            cur_words = []
            
    if cur_words:
        cur_text = clean_text("".join([x.word for x in cur_words]))
        if len(cur_text) > 0:
            start_time = cur_words[0].start
            end_time = cur_words[-1].end
            if end_time <= start_time:
                end_time = start_time + 0.5
            subtitles.append((start_time, end_time, cur_text))
            
    return subtitles

def write_srt(subtitles, srt_path: Path):
    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, (st, et, txt) in enumerate(subtitles, start=1):
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(st)} --> {format_timestamp(et)}\n")
            f.write(f"{txt}\n\n")

def main():
    print("🚀 初始化 Faster-Whisper (medium, int8, cpu_threads=8)...")
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)
    
    print(f"\n🎙️ 正在處理說明影片：{VID_FILE.name}")
    t0 = time.time()
    segments, info = model.transcribe(
        str(VID_FILE),
        language="zh",
        word_timestamps=True,
        initial_prompt=PROMPT_TEXT,
        beam_size=5,
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=450)
    )
    
    print(f"[*] 音訊時長：{info.duration:.1f} 秒 (~{info.duration/60:.1f} 分鐘)")
    all_words = []
    for seg in segments:
        s_txt = seg.text.strip()
        print(f"  [{format_timestamp(seg.start)} -> {format_timestamp(seg.end)}] {s_txt}", flush=True)
        if seg.words:
            all_words.extend(seg.words)
            
    print(f"\n✅ 說明影片語音解碼完成！共獲取 {len(all_words)} 個詞彙標籤，耗時 {time.time()-t0:.1f} 秒")
    subs = split_natural_sentences(all_words, min_chars=6, max_chars=18, max_pause=0.55)
    write_srt(subs, OUT_SRT)
    print(f"📄 已生成說明影片字幕：{OUT_SRT.name}，共 {len(subs)} 行")

if __name__ == "__main__":
    main()
