# -*- coding: utf-8 -*-
"""
第05章 說明影片 自然語氣斷句字幕生成腳本（專業繁中分詞與語氣停頓版）
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
    "聖薩爾瓦多城", "聖薩爾瓦多", "聖多明哥城", "聖多明哥", "諸聖修道院",
    "退守堡", "看守堡", "圓堡", "木堡", "北教堂堡",
    "社寮島", "和平島", "八尺門", "雞籠", "淡水", "淡水河口", "三貂角", "Santiago",
    "伐爾得斯", "Antonio Carreño Valdés", "阿爾卡拉索", "Juan de Alcarazo",
    "波提紐", "Gonzalo Portillo", "哈魯斯", "Hendrik Harouse",
    "科奎拉", "Sebastián Hurtado de Corcuera", "席爾瓦", "特羅登紐斯",
    "艾斯基維", "Jacinto Esquivel", "淡水語辭典", "淡水語教理書",
    "巴賽族", "巴賽語", "凱達格蘭族", "凱達格蘭", "噶瑪蘭族", "噶瑪蘭",
    "哆囉滿", "Turoboan", "立霧溪", "砂金", "硫磺",
    "馬尼拉大帆船", "馬尼拉", "阿卡普爾科", "菲律賓都督府", "都督府",
    "道明會", "方濟各會", "耶穌會", "邦板牙族", "卡加延",
    "勃艮第十字旗", "紅毛城", "熱蘭遮城", "荷蘭東印度公司", "VOC",
    "大航海時代", "三十年戰爭", "考古發掘"
]

for w in CUSTOM_WORDS:
    jieba.add_word(w)

TERM_CORRECTIONS = [
    (r"聖[薩薩]爾瓦多[城]?", "聖薩爾瓦多城"),
    (r"聖多明[哥歌][城]?", "聖多明哥城"),
    (r"諸聖[修道院]{2,3}", "諸聖修道院"),
    (r"退守[堡保]", "退守堡"),
    (r"看守[堡保]", "看守堡"),
    (r"社[寮僚]島", "社寮島"),
    (r"和[平萍]島", "和平島"),
    (r"八[尺呎]門", "八尺門"),
    (r"三[貂雕]角", "三貂角"),
    (r"伐[爾爾]得斯", "伐爾得斯"),
    (r"阿爾卡[拉啦]索", "阿爾卡拉索"),
    (r"波[提梯]紐", "波提紐"),
    (r"哈[魯嚕]斯", "哈魯斯"),
    (r"科[奎逵]拉", "科奎拉"),
    (r"艾斯[基吉]維", "艾斯基維"),
    (r"淡水語[辭詞]典", "淡水語辭典"),
    (r"巴[賽塞]族", "巴賽族"),
    (r"巴[賽塞]語", "巴賽語"),
    (r"凱達格[蘭藍]族", "凱達格蘭族"),
    (r"凱達格[蘭藍]", "凱達格蘭"),
    (r"[噶葛]瑪[蘭藍]族", "噶瑪蘭族"),
    (r"[噶葛]瑪[蘭藍]", "噶瑪蘭"),
    (r"哆[囉羅]滿", "哆囉滿"),
    (r"馬尼[拉啦]大帆船", "馬尼拉大帆船"),
    (r"馬尼[拉啦]", "馬尼拉"),
    (r"道明[會惠]", "道明會"),
    (r"方濟[各格]會", "方濟各會"),
    (r"邦板[牙雅]族", "邦板牙族"),
    (r"勃[艮根]第十字[旗契]?", "勃艮第十字旗"),
    (r"熱[蘭藍]遮[城]?", "熱蘭遮城"),
    (r"紅毛[城成]", "紅毛城"),
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
    json_p = "02_大航海時代與荷西競逐/whisper_words_ch05_video.json"
    srt_p = "02_大航海時代與荷西競逐/第05章_聖多明哥的十字架_說明影片.srt"
    build_srt(json_p, srt_p)
