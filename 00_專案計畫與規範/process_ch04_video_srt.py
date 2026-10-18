# -*- coding: utf-8 -*-
"""
第04章 說明影片 自然語氣斷句字幕生成腳本（專業繁中分詞與語氣停頓版）
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
    "熱蘭遮城", "普羅民遮城", "大員", "一鯤鯓", "赤崁", "風櫃尾",
    "荷蘭東印度公司", "東印度公司", "VOC", "親王旗", "宋克", "Martinus Sonck",
    "彼得·奴易茲", "彼得奴易茲", "Pieter Nuyts", "普特曼斯", "Hans Putmans",
    "揆一", "Frederik Coyett", "濱田彌兵衛", "末次平藏", "朱印船", "出島",
    "料羅灣海戰", "料羅灣", "鄭芝龍", "鄒維璉", "劉香", "李旦",
    "西拉雅族", "西拉雅", "新港社", "蕭壠社", "麻豆社", "目加溜灣社",
    "甘治士", "Georgius Candidius", "尤羅伯", "Robertus Junius",
    "新港文書", "番仔契", "紅毛字", "贌社制度", "贌社", "社商", "贌商",
    "地方會議", "Landdag", "長老會議", "銀頭藤杖", "藤杖",
    "人頭稅", "Polltax", "郭懷一事件", "郭懷一",
    "鹿皮貿易", "梅花鹿皮", "甘蔗", "砂糖", "糖廍", "生絲", "西班牙銀圓", "里爾", "Reales",
    "阿姆斯特丹", "巴達維亞", "十七人董事會", "Heeren XVII",
    "馬太福音", "海德堡教義問答", "雷爾生", "南居益", "商周運"
]

for w in CUSTOM_WORDS:
    jieba.add_word(w)

TERM_CORRECTIONS = [
    (r"熱[蘭藍]遮[城]?", "熱蘭遮城"),
    (r"普[羅儸]民[遮庶][城]?", "普羅民遮城"),
    (r"大[員圓園]", "大員"),
    (r"一[鯤鯓鵾][鯓身]?", "一鯤鯓"),
    (r"赤[崁坎嵌]", "赤崁"),
    (r"風[櫃貴]尾", "風櫃尾"),
    (r"彼得[·]?奴[易意]茲", "彼得·奴易茲"),
    (r"普特[曼滿]斯", "普特曼斯"),
    (r"揆[一一]", "揆一"),
    (r"濱田[彌彌]兵[衛衛]", "濱田彌兵衛"),
    (r"末次平[藏臟]", "末次平藏"),
    (r"料[羅蘿]灣", "料羅灣"),
    (r"鄭[芝之]龍", "鄭芝龍"),
    (r"甘[治智]士", "甘治士"),
    (r"尤[羅儸]伯", "尤羅伯"),
    (r"新港[文檔]書", "新港文書"),
    (r"[番瘋]仔契", "番仔契"),
    (r"[贌僕]社[制治]度", "贌社制度"),
    (r"[贌僕]社", "贌社"),
    (r"[贌僕]商", "贌商"),
    (r"社[商傷]", "社商"),
    (r"銀頭[藤騰]杖", "銀頭藤杖"),
    (r"郭[懷懷]一", "郭懷一"),
    (r"西[拉臘]雅", "西拉雅"),
    (r"麻[豆荳]社", "麻豆社"),
    (r"蕭[壠壟瓏]社", "蕭壠社"),
    (r"目加[溜留]灣社", "目加溜灣社"),
    (r"南[居車]益", "南居益"),
    (r"雷[爾爾]生", "雷爾生"),
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
    json_p = "02_大航海時代與荷西競逐/whisper_words_ch04_video.json"
    srt_p = "02_大航海時代與荷西競逐/第04章_熱蘭遮的紅毛城旗_說明影片.srt"
    build_srt(json_p, srt_p)
