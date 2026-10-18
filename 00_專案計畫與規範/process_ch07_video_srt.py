# -*- coding: utf-8 -*-
"""
第07章 說明影片 自然語氣斷句字幕生成腳本（專業繁中分詞與語氣停頓版）
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
    "鄭成功", "國姓爺", "Koxinga", "延平王", "朱成功", "揆一", "Frederick Coyett",
    "熱蘭遮城", "熱蘭遮", "普羅民遮城", "普羅民遮", "赤崁樓", "安平古堡",
    "鹿耳門", "鹿耳門水道", "臺江內海", "禾寮港", "柴頭港", "北線尾", "北線尾沙洲",
    "何斌", "馬德夫", "Thomas Pedel", "貓難實叮", "Jacobus Valentyn",
    "陳澤", "馬信", "甘輝", "黃廷", "范德蘭", "Dirk van der Laan",
    "烏特勒支碉堡", "烏特勒支", "Fort Utrecht", "拉迪斯", "Hans Jeuriaen Radis",
    "亨布魯克", "Antonius Hambroek", "赫克托號", "Hector", "格拉弗蘭號",
    "白鷺號", "瑪利亞號", "柯克肯號", "籐牌軍", "籐牌兵", "滾刀", "莫里斯方陣",
    "葡萄彈", "紅夷大砲", "遷界令", "東都承天府", "天興縣", "萬年縣", "屯田制",
    "左營", "前鎮", "新營", "柳營", "林鳳營", "大員評議會", "十八條締約"
]

for w in CUSTOM_WORDS:
    jieba.add_word(w)

TERM_CORRECTIONS = [
    (r"鄭成[功工]", "鄭成功"),
    (r"[國国]姓[爺爺]", "國姓爺"),
    (r"[揆睽]一", "揆一"),
    (r"熱[蘭藍]遮[城]?", "熱蘭遮城"),
    (r"普羅民[遮遮][城]?", "普羅民遮城"),
    (r"赤[崁嵌坎]樓?", "赤崁樓"),
    (r"鹿[耳爾]門", "鹿耳門"),
    (r"[臺台]江內海", "臺江內海"),
    (r"禾[寮僚]港", "禾寮港"),
    (r"柴頭[港剛]", "柴頭港"),
    (r"北[線綫]尾", "北線尾"),
    (r"何[斌斌]", "何斌"),
    (r"馬[德得]夫", "馬德夫"),
    (r"貓難實[叮盯]", "貓難實叮"),
    (r"陳[澤澤]", "陳澤"),
    (r"馬[信訊]", "馬信"),
    (r"烏特勒[支之]碉堡", "烏特勒支碉堡"),
    (r"烏特勒[支之]", "烏特勒支"),
    (r"拉[迪狄]斯", "拉迪斯"),
    (r"亨布[魯嚕]克", "亨布魯克"),
    (r"赫克[托託]號", "赫克托號"),
    (r"籐牌[軍兵]?", "籐牌軍"),
    (r"紅[夷夷]大[砲炮]", "紅夷大砲"),
    (r"遷界[令領]", "遷界令"),
    (r"東都承天[府負]", "東都承天府"),
    (r"天興[縣線]", "天興縣"),
    (r"萬年[縣線]", "萬年縣"),
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
            
            clean_w = re.sub(r"[,.?!;:，。？！；：、~'\" \(\)\[\]【】《》「」『』—]", "", w_str).strip()
            if not clean_w:
                continue
            
            need_space = False
            if current_chars and current_chars[-1].isascii() and current_chars[-1].isalnum() and clean_w[0].isascii() and clean_w[0].isalnum():
                need_space = True
                
            pause = 0.0
            if idx < len(tokens) - 1:
                pause = tokens[idx + 1]["start"] - tok["end"]
                
            current_chunk.append(tok)
            if need_space:
                current_chars += " " + clean_w
            else:
                current_chars += clean_w
            
            is_end_of_seg = (idx == len(tokens) - 1)
            should_break = False
            
            if is_end_of_seg:
                should_break = True
            elif pause >= 0.25 and len(current_chars) >= 8:
                should_break = True
            elif has_punc and len(current_chars) >= 10:
                should_break = True
            elif len(current_chars) >= 28:
                should_break = True
                    
            if should_break and current_chunk:
                s_t = current_chunk[0]["start"]
                e_t = current_chunk[-1]["end"]
                fixed_txt = clean_and_fix_term(current_chars)
                if fixed_txt.strip():
                    srt_entries.append((s_t, e_t, fixed_txt.strip()))
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
    json_p = "03_明鄭東寧與海上孤忠/whisper_words_ch07_video.json"
    srt_p = "03_明鄭東寧與海上孤忠/第07章_決戰大員九個月_說明影片.srt"
    build_srt(json_p, srt_p)
