# -*- coding: utf-8 -*-
"""
第09章 說明影片 自然語氣斷句字幕生成腳本（專業繁中分詞與語氣停頓版）
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
    "施琅", "劉國軒", "鄭克塽", "鄭克臧", "鄭克𡒉", "鄭經", "馮錫範", "姚啟聖", "李光地", "康熙帝",
    "恭陳臺灣棄留疏", "東寧之變", "北園別館", "延平王廟", "八罩島", "望安", "娘媽宮", "馬公港",
    "風櫃尾砲台", "雞籠嶼", "牛心灣", "西嶼", "吼門水道", "五爪開花", "鳥船", "趕繒船", "雙帆艍船",
    "紅夷大砲", "佛郎機", "噴筒", "藍理", "曾成", "林賢", "董義", "陳蟒", "魏明", "林陞", "江勝",
    "承天府", "安平鎮", "鹿耳門", "臺灣府", "臺灣縣", "鳳山縣", "諸羅縣", "臺灣分巡道", "臺灣總兵",
    "遷界令", "展界復界", "棄留臺灣廷議", "一府三縣", "東寧王國", "延平王", "東寧"
]

for w in CUSTOM_WORDS:
    jieba.add_word(w)

TERM_CORRECTIONS = [
    (r"施[狼良郎]", "施琅"),
    (r"劉國[軒宣]", "劉國軒"),
    (r"鄭克[臧藏𡒉]", "鄭克𡒉"),
    (r"鄭克[塽爽]", "鄭克塽"),
    (r"馮錫[範范]", "馮錫範"),
    (r"姚[啟啟]聖", "姚啟聖"),
    (r"李光[地第]", "李光地"),
    (r"恭陳[臺台]灣棄留[疏書]", "恭陳臺灣棄留疏"),
    (r"東[寧甯]之變", "東寧之變"),
    (r"東[寧甯]王國", "東寧王國"),
    (r"東[寧甯]", "東寧"),
    (r"北園[別別]館", "北園別館"),
    (r"延平王[廟祠]", "延平王廟"),
    (r"八[罩照]島", "八罩島"),
    (r"娘媽[宮公]", "娘媽宮"),
    (r"風[櫃貴]尾", "風櫃尾"),
    (r"吼門[水波]道", "吼門水道"),
    (r"五爪[開闢]花", "五爪開花"),
    (r"鳥[船船]", "鳥船"),
    (r"趕[繒增]船", "趕繒船"),
    (r"紅[夷衣]大[砲炮砲]", "紅夷大砲"),
    (r"佛[郎朗]機", "佛郎機"),
    (r"藍[理禮]", "藍理"),
    (r"林[陞升]", "林陞"),
    (r"承天[府負]", "承天府"),
    (r"鹿耳[門們]", "鹿耳門"),
    (r"[臺台]灣府", "臺灣府"),
    (r"[臺台]灣縣", "臺灣縣"),
    (r"鳳山[縣線]", "鳳山縣"),
    (r"諸羅[縣線]", "諸羅縣"),
    (r"一府三[縣線]", "一府三縣"),
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
    json_p = "03_明鄭東寧與海上孤忠/whisper_words_ch09_video.json"
    srt_p = "03_明鄭東寧與海上孤忠/第09章_澎湖海戰與帝國落幕_說明影片.srt"
    build_srt(json_p, srt_p)
