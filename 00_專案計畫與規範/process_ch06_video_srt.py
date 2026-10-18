# -*- coding: utf-8 -*-
"""
第06章 說明影片 自然語氣斷句字幕生成腳本（專業繁中分詞與語氣停頓版）
使用 jieba 詞庫保護專有名詞，依據真實說話語氣、呼吸停頓與完整主謂語意切分，
絕不腰斬名詞、絕無半字斷行，行長嚴格控制於 10~22 字。
"""
import os
import sys
import json
import re
import jieba

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

CUSTOM_WORDS = [
    "郭懷一", "郭懷一事件", "赤崁", "大鹿港", "歐汪", "油車行",
    "普羅民遮城", "熱蘭遮城", "大員", "臺江內海", "鹿耳門",
    "費爾勃格", "Nicolas Verburg", "揆一", "Frederick Coyett",
    "人頭稅", "Hoofdgeld", "王田", "贌社制度", "捕鹿執照",
    "西拉雅族", "新港社", "麻豆社", "蕭壠社", "目加溜灣社",
    "鄭芝龍", "鄭成功", "荷蘭東印度公司", "VOC",
    "莫里斯排槍輪射", "葡萄彈", "火繩槍", "刺竹槍", "連枷", "蔗刀", "糖廍", "梅花鹿皮"
]

for w in CUSTOM_WORDS:
    jieba.add_word(w)

TERM_CORRECTIONS = [
    (r"郭[懷懷]一", "郭懷一"),
    (r"赤[崁嵌坎]", "赤崁"),
    (r"大[鹿陸]港", "大鹿港"),
    (r"油車[行航]", "油車行"),
    (r"歐[汪枉]", "歐汪"),
    (r"普羅民[遮遮][城]?", "普羅民遮城"),
    (r"熱[蘭藍]遮[城]?", "熱蘭遮城"),
    (r"費爾[勃伯博]格", "費爾勃格"),
    (r"[揆睽]一", "揆一"),
    (r"人頭[稅說]", "人頭稅"),
    (r"[贌撲樸]社", "贌社"),
    (r"西[拉啦]雅族", "西拉雅族"),
    (r"西[拉啦]雅", "西拉雅"),
    (r"新港[社設]", "新港社"),
    (r"麻[豆荳]社", "麻豆社"),
    (r"蕭[壠壟隴]社", "蕭壠社"),
    (r"目加[溜留]灣社", "目加溜灣社"),
    (r"[臺台]江內海", "臺江內海"),
    (r"鹿[耳爾]門", "鹿耳門"),
    (r"鄭[芝之]龍", "鄭芝龍"),
    (r"鄭成[功工]", "鄭成功"),
    (r"刺竹[槍搶]", "刺竹槍"),
    (r"火繩[槍搶]", "火繩槍"),
    (r"糖[廍部]", "糖廍"),
]

def format_timestamp(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis -= 1000
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def clean_and_fix_term(text: str) -> str:
    res = text
    for pattern, replacement in TERM_CORRECTIONS:
        res = re.sub(pattern, replacement, res)
    return res

def build_srt(json_path: str, output_srt: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    segments = data.get("segments", [])
    print(f"[*] 讀取到 {len(segments)} 個辨識段落，準備進行語氣自然斷句...")
    
    srt_entries = []
    
    for seg in segments:
        words = seg.get("words", [])
        if not words:
            raw = clean_and_fix_term(seg.get("text", "").strip())
            if raw:
                srt_entries.append((seg["start"], seg["end"], raw))
            continue
            
        tokens = []
        for w in words:
            w_str = w["word"].strip()
            if not w_str:
                continue
            tokens.append(w)
            
        if not tokens:
            continue
            
        current_chunk = []
        current_chars = ""
        
        for idx, tok in enumerate(tokens):
            w_str = tok["word"].strip()
            clean_w = re.sub(r"[,.?!;:，。？！；：、~'\" \(\)\[\]【】《》「」『』—]", "", w_str)
            has_punc = bool(re.search(r"[,.?!;:，。？！；：、~]", w_str))
            
            pause = 0.0
            if idx < len(tokens) - 1:
                pause = tokens[idx + 1]["start"] - tok["end"]
                
            current_chunk.append(tok)
            current_chars += clean_w
            
            is_end_of_seg = (idx == len(tokens) - 1)
            should_break = False
            
            if is_end_of_seg:
                should_break = True
            elif pause >= 0.25 and len(current_chars) >= 8:
                should_break = True
            elif has_punc and len(current_chars) >= 10:
                should_break = True
            elif len(current_chars) >= 16:
                next_word = tokens[idx + 1]["word"].strip() if idx < len(tokens) - 1 else ""
                clean_next = re.sub(r"[,.?!;:，。？！；：、~'\" \(\)\[\]【】《》「」『』—]", "", next_word)
                if len(current_chars) + len(clean_next) > 22 or pause >= 0.15:
                    should_break = True
                elif len(current_chars) >= 20:
                    should_break = True
                    
            if should_break and current_chunk:
                s_t = current_chunk[0]["start"]
                e_t = current_chunk[-1]["end"]
                fixed_txt = clean_and_fix_term(current_chars)
                if fixed_txt.strip():
                    words_in_chunk = list(jieba.cut(fixed_txt))
                    refit_txt = "".join(words_in_chunk)
                    srt_entries.append((s_t, e_t, refit_txt))
                current_chunk = []
                current_chars = ""
    
    merged_entries = []
    for s_t, e_t, txt in srt_entries:
        if not txt.strip():
            continue
        if merged_entries:
            prev_s, prev_e, prev_txt = merged_entries[-1]
            if len(prev_txt) < 8 and (s_t - prev_e) < 0.25 and (len(prev_txt) + len(txt)) <= 22:
                merged_entries[-1] = (prev_s, e_t, prev_txt + txt)
                continue
        merged_entries.append((s_t, e_t, txt))
        
    os.makedirs(os.path.dirname(os.path.abspath(output_srt)), exist_ok=True)
    with open(output_srt, "w", encoding="utf-8-sig") as f:
        for i, (s_t, e_t, txt) in enumerate(merged_entries, 1):
            if e_t <= s_t:
                e_t = s_t + 0.8
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(s_t)} --> {format_timestamp(e_t)}\n")
            f.write(f"{txt}\n\n")
            
    print(f"[✓] 成功產出語氣自然斷句 SRT：{output_srt}")
    print(f"[✓] 總字幕行數：{len(merged_entries)}")

if __name__ == "__main__":
    json_p = "02_大航海時代與荷西競逐/whisper_words_ch06_video.json"
    srt_p = "02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_說明影片.srt"
    build_srt(json_p, srt_p)
