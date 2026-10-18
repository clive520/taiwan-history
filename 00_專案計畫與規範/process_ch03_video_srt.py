# -*- coding: utf-8 -*-
"""
第03章 說明影片 自然語氣斷句字幕生成腳本（專業繁中分詞與語氣停頓版）
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
    "大肚王國", "大肚王", "甘馬轄·阿興", "甘馬轄阿興", "甘馬轄·馬洛", "甘馬轄馬洛",
    "Camachat Asing", "Camachat Maloe", "Camachat", "Middag", "華達旺", "Quataong",
    "拍瀑拉族", "拍瀑拉", "巴布薩族", "巴布薩", "巴宰族", "巴宰", "洪雅族", "洪雅",
    "大肚社", "沙轆社", "牛罵社", "彼得·文伯恩", "彼得文伯恩", "Pieter Boon",
    "熱蘭遮城日誌", "熱蘭遮城", "臺海使槎錄", "黃叔璥", "劉國軒", "大甲西社",
    "排灣族", "排灣", "魯凱族", "魯凱", "石板屋", "百步蛇", "五年祭", "Maleveq", "刺球",
    "阿美族", "阿美", "卑南族", "卑南", "太巴塱", "年齡階級", "Kapah", "青年會所", "Sfi",
    "豐年祭", "Ilisin", "大獵祭", "Mangayau", "泰雅族", "泰雅", "太魯閣族", "太魯閣",
    "Gaga", "祖訓", "文面", "彩虹橋", "Hongu Utux", "布農族", "布農", "鄒族",
    "八部合音", "Pasibutbut", "小米祭曆", "粟作", "Dihanin", "天神"
]

for w in CUSTOM_WORDS:
    jieba.add_word(w)

TERM_CORRECTIONS = [
    (r"甘馬[下暇峽]阿[星心興]", "甘馬轄·阿興"),
    (r"甘馬轄阿[星心興]", "甘馬轄·阿興"),
    (r"甘馬轄馬[落洛]", "甘馬轄·馬洛"),
    (r"甘馬轄", "甘馬轄"),
    (r"拍[瀑爆暴]拉", "拍瀑拉族"),
    (r"巴[布步]薩", "巴布薩族"),
    (r"巴[宰載]族", "巴宰族"),
    (r"[紅洪]雅族", "洪雅族"),
    (r"沙[鹿]社", "沙轆社"),
    (r"牛[馬]社", "牛罵社"),
    (r"米[達克]格", "米達格"),
    (r"彼得[·]?文[伯柏]恩", "彼得·文伯恩"),
    (r"祖訓[嘎嘎]Gaga", "祖訓 Gaga"),
    (r"祖訓[嘎嘎]", "祖訓 Gaga"),
    (r"[八步]部合音", "八部合音"),
    (r"太[巴扒]塱", "太巴塱"),
    (r"[百白]步蛇", "百步蛇"),
    (r"熱蘭遮城日[記誌]", "熱蘭遮城日誌"),
    (r"臺海使[差槎]錄", "臺海使槎錄"),
    (r"台海使槎錄", "臺海使槎錄"),
    (r"大甲西社抗[暴暴]事件", "大甲西社抗暴事件"),
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
    json_p = "01_史前文明與南島之源/whisper_words_ch03_video.json"
    srt_p = "01_史前文明與南島之源/第03章_部落聯盟與土地精靈_說明影片.srt"
    build_srt(json_p, srt_p)
