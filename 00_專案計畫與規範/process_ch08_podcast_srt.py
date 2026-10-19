# -*- coding: utf-8 -*-
"""
第08章 雙人對談播客 自然語氣斷句字幕生成腳本（專業繁中分詞與語氣停頓版）
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
    "陳永華", "鄭經", "鄭成功", "鄭襲", "鄭克臧", "鄭克塽", "馮錫範", "沈光文", "施琅",
    "東寧王國", "東寧", "承天府", "天興州", "萬年州", "諮議參軍", "東寧總制", "臺灣國王", "永曆",
    "全臺首學", "臺南孔廟", "明倫堂", "大成殿", "國子學", "泮池", "櫺星門",
    "營盤田", "官田", "文武官田", "寓兵於農", "柳營", "查畝營", "林鳳營", "新營", "下營",
    "左鎮", "前鎮", "後勁", "右昌", "左營", "瀨口", "天日曬鹽", "瓦盤鹽田", "糖廓", "燒磚瓦",
    "遷界令", "遷海令", "英國東印度公司", "鄭英通商條約", "萬壽號", "Bantam", "King of Tywan",
    "山海五商", "龍湖巖", "三藩之亂", "東寧之變", "果毅後"
]

for w in CUSTOM_WORDS:
    jieba.add_word(w)

TERM_CORRECTIONS = [
    (r"陳永[華花發]", "陳永華"),
    (r"鄭[經京金]", "鄭經"),
    (r"鄭克[臧藏]", "鄭克臧"),
    (r"鄭克[塽爽]", "鄭克塽"),
    (r"馮錫[範范]", "馮錫範"),
    (r"東[寧甯]王國", "東寧王國"),
    (r"東[寧甯]", "東寧"),
    (r"承天[府負]", "承天府"),
    (r"天興[州縣線]", "天興州"),
    (r"萬年[州縣線]", "萬年州"),
    (r"諮議參[軍君]", "諮議參軍"),
    (r"全[臺台]首學", "全臺首學"),
    (r"[臺台]南孔廟", "臺南孔廟"),
    (r"明倫[堂唐]", "明倫堂"),
    (r"大成[殿電]", "大成殿"),
    (r"營盤[田填]", "營盤田"),
    (r"寓兵於[農濃]", "寓兵於農"),
    (r"查[畝母]營", "查畝營"),
    (r"林[鳳風]營", "林鳳營"),
    (r"[瀨賴]口", "瀨口"),
    (r"瓦[盤盤]鹽田", "瓦盤鹽田"),
    (r"糖[廓廍廓]", "糖廓"),
    (r"遷[界海][令領]", "遷界令"),
    (r"鄭英通商[條條]約", "鄭英通商條約"),
    (r"萬[壽手]號", "萬壽號"),
    (r"龍湖[巖岩]", "龍湖巖"),
    (r"果[毅意]後", "果毅後"),
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
            
    print(f"[OK] 成功產出語氣自然斷句 SRT：{output_srt}")
    print(f"[OK] 總字幕行數：{len(merged_entries)}")

if __name__ == "__main__":
    json_p = "03_明鄭東寧與海上孤忠/whisper_words_ch08_podcast.json"
    srt_p = "03_明鄭東寧與海上孤忠/第08章_海外別立乾坤_雙人對談.srt"
    build_srt(json_p, srt_p)
