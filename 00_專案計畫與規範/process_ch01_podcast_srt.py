# -*- coding: utf-8 -*-
"""
第01章 Podcast 自然語氣斷句字幕生成與自動上傳腳本
讀取 whisper_words_ch01_podcast.json，依語氣呼吸與語意停頓切分，校正專有名詞，
輸出標準 SRT 並自動上傳至 YouTube 影片 9Ep4670kORM。
"""
import os
import sys
import json
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# 歷史與專有名詞同音修正對照表
TERM_CORRECTIONS = [
    (r"左正仁", "左鎮人"),
    (r"左正", "左鎮"),
    (r"林朝鮮", "林朝棨"),
    (r"林朝起", "林朝棨"),
    (r"林朝[氣氣]", "林朝棨"),
    (r"潮陰洞", "潮音洞"),
    (r"朝陰洞", "潮音洞"),
    (r"朝音洞", "潮音洞"),
    (r"即時吹響", "擊石脆響"),
    (r"死前先驅", "史前先驅"),
    (r"死前文明", "史前文明"),
    (r"星火", "薪火"),
    (r"生命全員", "生命泉源"),
    (r"大放暗", "大翻案"),
    (r"菜鳥溪", "菜寮溪"),
    (r"採集者", "採集者"),
    (r"海雷洞", "海雷洞"),
    (r"乾欄式", "干欄式"),
    (r"懷河", "淮河"),
    (r"古靈齒象", "古菱齒象"),
    (r"古菱尺象", "古菱齒象"),
    (r"劍齒像", "劍齒象"),
    (r"早坂中國吸", "早坂中國犀"),
    (r"早坂中國溪", "早坂中國犀"),
    (r"鹿間石夫", "鹿間時夫"),
    (r"佐倉說", "佐倉朔"),
    (r"碳14", "碳十四"),
    (r"砍砸契", "砍砸器"),
    (r"刮削契", "刮削器"),
    (r"骨角契", "骨角器"),
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

def build_srt_from_whisper(json_path: str, output_srt: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    segments = data.get("segments", [])
    print(f"[*] 讀取到 {len(segments)} 個辨識段落，準備進行自然語氣斷句...")
    
    srt_lines = []
    line_index = 1
    
    for seg in segments:
        words = seg.get("words", [])
        if not words:
            # 回退到段落文本
            raw_text = seg.get("text", "").strip()
            if not raw_text:
                continue
            fixed = clean_and_fix_term(raw_text)
            srt_lines.append((line_index, seg["start"], seg["end"], fixed))
            line_index += 1
            continue
        
        # 詞級自然切分：依據停頓 (>=0.3s) 或標點符號，行長 10~20 字
        current_chunk = []
        current_text = ""
        current_start = None
        
        for i, w in enumerate(words):
            word_str = w["word"].strip()
            if not word_str:
                continue
            
            if current_start is None:
                current_start = w["start"]
            
            clean_word = re.sub(r"[,.?!;:，。？！；：、~'\" \(\)\[\]【】《》「」『』—]", "", word_str)
            current_chunk.append(w)
            current_text += clean_word
            
            # 檢查斷句條件
            is_last = (i == len(words) - 1)
            pause = 0.0
            if not is_last:
                pause = words[i+1]["start"] - w["end"]
            
            has_punc = bool(re.search(r"[,.?!;:，。？！；：、~]", word_str))
            
            should_break = False
            if is_last:
                should_break = True
            elif pause >= 0.28 and len(current_text) >= 6:
                should_break = True
            elif has_punc and len(current_text) >= 10:
                should_break = True
            elif len(current_text) >= 18:
                should_break = True
            
            if should_break and current_chunk:
                fixed_text = clean_and_fix_term(current_text)
                end_time = current_chunk[-1]["end"]
                if fixed_text.strip():
                    srt_lines.append((line_index, current_start, end_time, fixed_text))
                    line_index += 1
                current_chunk = []
                current_text = ""
                current_start = None
    
    # 輸出 SRT 檔案
    with open(output_srt, "w", encoding="utf-8") as out:
        for idx, s, e, text in srt_lines:
            # 確保時長合理
            if e <= s:
                e = s + 1.0
            s_str = format_timestamp(s)
            e_str = format_timestamp(e)
            out.write(f"{idx}\n{s_str} --> {e_str}\n{text}\n\n")
            
    print(f"[✓] 成功產出高品質自然斷句 SRT：{output_srt}（共 {len(srt_lines)} 條字幕）")
    return output_srt

if __name__ == "__main__":
    json_path = "01_史前文明與南島之源/whisper_words_ch01_podcast.json"
    output_srt = "01_史前文明與南島之源/第01章_黑潮上的遠古足跡_雙人對談.srt"
    
    if not os.path.exists(json_path):
        print(f"❌ 找不到轉錄結果：{json_path}，請等待轉錄完成。")
        sys.exit(1)
        
    build_srt_from_whisper(json_path, output_srt)
    
    # 自動上傳至 YouTube
    print("\n🚀 正在自動上傳至 YouTube Podcast 影片 (9Ep4670kORM)...")
    from upload_new_subtitles import update_subtitles
    update_subtitles("9Ep4670kORM", output_srt)
