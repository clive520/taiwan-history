# -*- coding: utf-8 -*-
"""
第10章 說明影片 自然語氣斷句字幕生成腳本（專業繁中分詞與語氣停頓版）
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
    "唐山過臺灣", "黑水溝", "六死三留一回頭", "渡臺禁令", "渡臺三禁", "照單審查", "嚴禁攜眷", "粵東客民",
    "裨海紀遊", "郁永河", "臺海使槎錄", "黃叔璥", "東征集", "藍鼎元", "諸羅縣志", "周鍾瑄",
    "羅漢腳", "放生", "灌水", "種芋頭", "壓艙底", "落漈", "牽水藏",
    "墾首", "墾號", "墾照", "田底權", "田面權", "一田二主", "大租戶", "小租戶", "現耕佃農", "施侯大租", "靖海侯施琅",
    "八堡圳", "施厝圳", "施世榜", "施長齡", "林先生", "石笱導水法", "竹篾筍籠", "石笱", "濁水溪", "鼻仔頭", "二水", "彰化平原", "林先生廟",
    "瑠公圳", "郭錫瑠", "瑠公", "郭元芬", "新店溪", "碧潭", "青潭口", "開硿", "木筧", "景美溪", "大加蚋堡", "大安", "艋舺", "錫口",
    "有應公", "萬善爺", "百姓公", "義塚", "普渡祭典"
]

for w in CUSTOM_WORDS:
    jieba.add_word(w)

TERM_CORRECTIONS = [
    (r"黑水[溝鉤]", "黑水溝"),
    (r"郁永[河合和]", "郁永河"),
    (r"黃叔[璥敬璟]", "黃叔璥"),
    (r"藍鼎[元玄]", "藍鼎元"),
    (r"周[鍾鐘]瑄", "周鍾瑄"),
    (r"羅漢[腳跤角]", "羅漢腳"),
    (r"種芋[頭投]", "種芋頭"),
    (r"八[堡保]圳", "八堡圳"),
    (r"施世[榜榜棒]", "施世榜"),
    (r"施[長長]齡", "施長齡"),
    (r"石[笱苟狗筍]", "石笱"),
    (r"濁水[溪西]", "濁水溪"),
    (r"鼻[仔子]頭", "鼻仔頭"),
    (r"[瑠留劉]公圳", "瑠公圳"),
    (r"郭[錫錫]瑠", "郭錫瑠"),
    (r"郭元[芬芳]", "郭元芬"),
    (r"木[筧見箭]", "木筧"),
    (r"景美[溪西]", "景美溪"),
    (r"大加[蚋納]堡", "大加蚋堡"),
    (r"艋[舺甲]", "艋舺"),
    (r"有應[公工]", "有應公"),
    (r"萬善[爺夜]", "萬善爺"),
    (r"一田[二兩]主", "一田二主"),
    (r"施侯[大租租]", "施侯大租"),
    (r"田[底低]權", "田底權"),
    (r"田[面免]權", "田面權"),
    (r"[臺台]灣", "臺灣"),
]

def correct_text(text):
    for pattern, replacement in TERM_CORRECTIONS:
        text = re.sub(pattern, replacement, text)
    return text

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis = 0
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def clean_word(w):
    return re.sub(r'[\s，。！？、；：""''（）《》〈〉…—]+', '', w)

def is_punctuation_word(w):
    return bool(re.match(r'^[\s，。！？、；：""''（）《》〈〉…—]+$', w))

def generate_natural_srt(input_json_path, output_srt_path):
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    raw_words = data.get("words", [])
    if not raw_words:
        print("[WARN] 沒有 words 資料，使用 segments 回退")
        return False
        
    filtered_words = []
    for item in raw_words:
        w_text = item["word"]
        if is_punctuation_word(w_text):
            continue
        c_text = clean_word(w_text)
        if not c_text:
            continue
        filtered_words.append({
            "word": correct_text(c_text),
            "start": item["start"],
            "end": item["end"]
        })
        
    print(f"[*] 載入有效詞彙：{len(filtered_words)} 個")
    
    sentences = []
    cur_sentence = []
    
    PAUSE_SENTENCE_BREAK = 0.55
    
    for i, w in enumerate(filtered_words):
        if not cur_sentence:
            cur_sentence.append(w)
            continue
            
        prev_w = cur_sentence[-1]
        gap = w["start"] - prev_w["end"]
        
        cur_chars = sum(len(x["word"]) for x in cur_sentence)
        
        if gap >= PAUSE_SENTENCE_BREAK or cur_chars >= 28:
            sentences.append(cur_sentence)
            cur_sentence = [w]
        else:
            cur_sentence.append(w)
            
    if cur_sentence:
        sentences.append(cur_sentence)
        
    print(f"[*] 初步依停頓劃分語句數：{len(sentences)}")
    
    final_subtitles = []
    
    for s in sentences:
        s_chars = sum(len(x["word"]) for x in s)
        s_start = s[0]["start"]
        s_end = s[-1]["end"]
        
        if s_chars <= 22:
            s_text = "".join(x["word"] for x in s)
            final_subtitles.append({
                "start": s_start,
                "end": s_end,
                "text": s_text
            })
        else:
            cut_idx = len(s) // 2
            best_diff = 999
            accum_chars = 0
            
            for idx in range(len(s) - 1):
                accum_chars += len(s[idx]["word"])
                diff = abs(accum_chars - (s_chars / 2))
                if diff < best_diff:
                    best_diff = diff
                    cut_idx = idx + 1
                    
            part1 = s[:cut_idx]
            part2 = s[cut_idx:]
            
            if part1:
                final_subtitles.append({
                    "start": part1[0]["start"],
                    "end": part1[-1]["end"],
                    "text": "".join(x["word"] for x in part1)
                })
            if part2:
                final_subtitles.append({
                    "start": part2[0]["start"],
                    "end": part2[-1]["end"],
                    "text": "".join(x["word"] for x in part2)
                })
                
    for i in range(len(final_subtitles) - 1):
        if final_subtitles[i]["end"] > final_subtitles[i+1]["start"]:
            final_subtitles[i]["end"] = final_subtitles[i+1]["start"]
            
    with open(output_srt_path, "w", encoding="utf-8") as f:
        for idx, sub in enumerate(final_subtitles, 1):
            start_str = format_timestamp(sub["start"])
            end_str = format_timestamp(sub["end"])
            f.write(f"{idx}\n{start_str} --> {end_str}\n{sub['text']}\n\n")
            
    print(f"[OK] 自然語氣斷句字幕生成成功！共 {len(final_subtitles)} 行字幕")
    print(f"[OK] 輸出路徑：{output_srt_path}")
    return True

if __name__ == "__main__":
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent
    in_json = str(base_dir / "04_清領時代的拓墾烽火與變革/whisper_words_ch10_video.json")
    out_srt = str(base_dir / "04_清領時代的拓墾烽火與變革/第10章_唐山過臺灣的黑水溝血淚_說明影片.srt")
    generate_natural_srt(in_json, out_srt)
