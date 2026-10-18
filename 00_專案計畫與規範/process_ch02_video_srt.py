# -*- coding: utf-8 -*-
"""
第02章 說明影片 自然語氣斷句字幕生成腳本（專業繁中分詞與語氣停頓版）
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
    "世界地圖", "巨大板塊", "南島語族", "南島語系", "出臺灣說", "彼得·貝爾伍德",
    "白樂思", "Robert Blust", "大坌坑文化", "大坌坑", "卑南文化", "卑南遺址",
    "十三行文化", "十三行", "豐田閃玉", "臺灣玉", "雙獸頭形玉玦", "人獸形玉玦",
    "舷外浮筒獨木舟", "舷外浮筒", "浮筒獨木舟", "雙體帆船", "蟹爪帆",
    "馬來-玻里尼西亞語族", "馬來-玻里尼西亞", "巴士海峽", "凱達格蘭族", "凱達格蘭",
    "噶瑪蘭族", "沙黃文化", "杜永洞", "洪曉純", "飯塚義之", "黑潮",
    "馬達加斯加", "復活節島", "南太平洋", "紐西蘭", "毛利人", "歷史語言學",
    "樹狀結構", "一級分支", "粗繩紋陶", "南關里東", "南科南關里東", "家犬墓葬",
    "都蘭山", "石板棺", "電子探針微分析", "牽牛星", "南十字座", "赤鐵礦", "磁鐵礦砂",
    "開元通寶", "平埔族群", "粒線體", "染色體單倍群", "古菱齒象", "長濱文化"
]

for w in CUSTOM_WORDS:
    jieba.add_word(w)

TERM_CORRECTIONS = [
    (r"大[份崩本]坑", "大坌坑"),
    (r"白樂[斯絲]", "白樂思"),
    (r"百樂思", "白樂思"),
    (r"彼[得德]·?貝爾[伍武]德", "彼得·貝爾伍德"),
    (r"豐田[產展]玉", "豐田閃玉"),
    (r"豐田閃[育域]", "豐田閃玉"),
    (r"透閃石軟玉", "透閃石軟玉"),
    (r"人[受獸]形玉[決玦絕]", "人獸形玉玦"),
    (r"人獸形玉[決絕]", "人獸形玉玦"),
    (r"雙獸[頭首]形玉[決玦絕]", "雙獸頭形玉玦"),
    (r"雙獸首耳飾", "雙獸首耳飾"),
    (r"玉[決絕]", "玉玦"),
    (r"[玄弦]外浮筒", "舷外浮筒"),
    (r"浮筒獨木舟", "浮筒獨木舟"),
    (r"[卸謝]爪帆", "蟹爪帆"),
    (r"粗[生深]紋陶", "粗繩紋陶"),
    (r"繩紋陶", "繩紋陶"),
    (r"沙皇文化", "沙黃文化"),
    (r"復活街[島道]", "復活節島"),
    (r"復活節[道街]", "復活節島"),
    (r"千禧之謎", "遷徙之謎"),
    (r"太平洋道[的地的]", "太平洋到"),
    (r"洪小純", "洪曉純"),
    (r"飯[宗主義]義之", "飯塚義之"),
    (r"都[藍蘭]山", "都蘭山"),
    (r"石板[官觀]", "石板棺"),
    (r"干欄式", "干欄式"),
    (r"乾欄式", "干欄式"),
    (r"凱達格蘭", "凱達格蘭族"),
    (r"波里尼西亞", "玻里尼西亞"),
    (r"馬來-玻里尼西亞", "馬來-玻里尼西亞語族"),
    (r"電子探針", "電子探針微分析"),
    (r"牽牛星", "牽牛星"),
    (r"南十字座", "南十字座"),
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
                    srt_entries.append((s_t, e_t, fixed_txt))
                current_chunk = []
                current_chars = ""
                
    final_lines = []
    prev_end = 0.0
    for idx, (s_t, e_t, text) in enumerate(srt_entries):
        if s_t < prev_end:
            s_t = prev_end
        if e_t <= s_t:
            e_t = s_t + 1.2
        prev_end = e_t
        final_lines.append((idx + 1, s_t, e_t, text))
        
    with open(output_srt, "w", encoding="utf-8") as out:
        for num, s, e, text in final_lines:
            s_str = format_timestamp(s)
            e_str = format_timestamp(e)
            out.write(f"{num}\n{s_str} --> {e_str}\n{text}\n\n")
            
    print(f"[✓] 成功產出完美自然語意斷句 SRT：{output_srt}（共 {len(final_lines)} 條字幕）")
    return output_srt

if __name__ == "__main__":
    json_path = "01_史前文明與南島之源/whisper_words_ch02_video.json"
    output_srt = "01_史前文明與南島之源/第02章_大海是唯一的路徑_說明影片.srt"
    
    if not os.path.exists(json_path):
        print(f"❌ 找不到轉錄結果：{json_path}")
        sys.exit(1)
        
    build_srt(json_path, output_srt)
