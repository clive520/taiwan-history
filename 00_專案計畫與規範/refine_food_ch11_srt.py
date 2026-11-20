# -*- coding: utf-8 -*-
import json
import re
import sys
import os
from pathlib import Path

# 專用歷史與美食在地名詞精準校正字典（100% 繁體中文與專業術語）
TYPO_REPLACEMENTS = {
    # 豆瓣醬與釀造
    "豆瓣酱": "豆瓣醬",
    "辣豆瓣酱": "辣豆瓣醬",
    "岡山豆瓣": "岡山豆瓣醬",
    "崗山": "岡山",
    "岡山": "岡山",
    "劉明德": "劉明德",
    "明德豆瓣醬": "明德豆瓣醬",
    "郫縣": "郫縣",
    "皮縣": "郫縣",
    "碑縣": "郫縣",
    "郫縣豆瓣": "郫縣豆瓣醬",
    "蠶豆": "蠶豆",
    "黄豆": "黃豆",
    "黃豆": "黃豆",
    "日曬發酵": "日曬發酵",
    "發酵": "發酵",
    "發酵酸菜": "發酵酸菜",
    "酸菜": "酸菜",
    
    # 牛肉與烹飪工藝
    "牛肉面": "牛肉麵",
    "牛肉麵": "牛肉麵",
    "紅燒牛肉麵": "紅燒牛肉麵",
    "清燉牛肉麵": "清燉牛肉麵",
    "川味牛肉麵": "川味牛肉麵",
    "小碗牛肉": "小碗牛肉",
    "小碗紅湯牛肉": "小碗紅湯牛肉",
    "牛腱": "牛腱",
    "牛腱子": "牛腱子",
    "腱子肉": "腱子肉",
    "腱子心": "腱子心",
    "牛筋": "牛筋",
    "牛腩": "牛腩",
    "膠原蛋白": "膠原蛋白",
    "明膠": "明膠",
    "美拉德反應": "美拉德反應",
    "梅納反應": "梅納反應",
    "焦糖化": "焦糖化",
    "水解": "水解",
    
    # 歷史人物、地名與眷村
    "梁實秋": "梁實秋",
    "雅舍談吃": "《雅舍談吃》",
    "《《雅舍談吃》》": "《雅舍談吃》",
    "寶慶路": "寶慶路",
    "桃源街": "桃源街",
    "桃園街": "桃源街",
    "防空洞": "防空洞",
    "眷村": "眷村",
    "眷村菜": "眷村菜",
    "空軍眷村": "空軍眷村",
    "空軍機校": "空軍機校",
    "大江大海": "大江大海",
    "美援": "美援",
    "美援麵粉": "美援麵粉",
    "敬牛": "敬牛",
    "不食牛": "不食牛肉",
    "不食牛肉": "不食牛肉",
    "耕牛": "耕牛",
    "牛魂碑": "牛魂碑",
    "國際牛肉麵節": "國際牛肉麵節"
}

PUNCTUATION_FIXES = {
    ",": "，",
    "?": "？",
    "!": "！",
    ":": "：",
    ";": "；"
}

def clean_and_replace_text(text):
    for k, v in PUNCTUATION_FIXES.items():
        text = text.replace(k, v)
    for wrong, right in TYPO_REPLACEMENTS.items():
        text = text.replace(wrong, right)
    return text.strip()

def format_timestamp(seconds):
    millis = int(round(seconds * 1000))
    hours = millis // (3600 * 1000)
    millis %= (3600 * 1000)
    minutes = millis // (60 * 1000)
    millis %= (60 * 1000)
    secs = millis // 1000
    millis %= 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def segment_sentence_by_breath(text):
    """
    依自然呼吸律、語意與標點切分段落
    - 對話語氣詞（對吧？、真的！、沒錯、對對對等）獨立成行
    - 不硬截斷名詞與短語，每行控制在 12~18 字以內
    """
    delimiters = r'([。！？!?])'
    tokens = re.split(delimiters, text)
    sentences = []
    for i in range(0, len(tokens) - 1, 2):
        s = (tokens[i] + tokens[i+1]).strip()
        if s:
            sentences.append(s)
    if len(tokens) % 2 == 1 and tokens[-1].strip():
        sentences.append(tokens[-1].strip())
        
    final_lines = []
    
    INTERJECTIONS = [
        "對吧？", "真的！", "沒錯！", "沒錯，", "沒錯", "對對對！", "對對對，", "對啊！", "對啊，",
        "確實！", "確實，", "哈哈！", "是啊！", "沒問題！", "哇！", "你知道嗎？"
    ]
    
    for s in sentences:
        comma_parts = re.split(r'([，,、])', s)
        current_chunk = ""
        
        parts = []
        for j in range(0, len(comma_parts) - 1, 2):
            p = (comma_parts[j] + comma_parts[j+1]).strip()
            if p:
                parts.append(p)
        if len(comma_parts) % 2 == 1 and comma_parts[-1].strip():
            parts.append(comma_parts[-1].strip())
            
        for p in parts:
            p_clean = p.strip()
            if not p_clean:
                continue
                
            if p_clean in INTERJECTIONS:
                if current_chunk:
                    final_lines.append(current_chunk)
                    current_chunk = ""
                final_lines.append(p_clean)
                continue
                
            if len(current_chunk) + len(p_clean) <= 18:
                current_chunk += p_clean
            else:
                if current_chunk:
                    final_lines.append(current_chunk)
                current_chunk = p_clean
                
        if current_chunk:
            final_lines.append(current_chunk)
            
    return final_lines

def build_srt_from_whisper_json(whisper_json_path, output_srt_path):
    with open(whisper_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if isinstance(data, dict):
        segments = data.get("segments", [])
    elif isinstance(data, list):
        segments = data
    else:
        segments = []
        
    srt_entries = []
    idx = 1
    for seg in segments:
        seg_start = seg["start"]
        seg_end = seg["end"]
        raw_text = clean_and_replace_text(seg["text"])
        
        if not raw_text:
            continue
            
        lines = segment_sentence_by_breath(raw_text)
        if not lines:
            continue
            
        total_len = sum(len(l) for l in lines)
        duration = seg_end - seg_start
        cur_t = seg_start
        
        for l in lines:
            l_dur = duration * (len(l) / total_len) if total_len > 0 else duration
            t_start = cur_t
            t_end = cur_t + l_dur
            cur_t = t_end
            
            srt_entries.append((idx, t_start, t_end, l))
            idx += 1
            
    with open(output_srt_path, 'w', encoding='utf-8') as f:
        for index, start, end, line in srt_entries:
            f.write(f"{index}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            f.write(f"{line}\n\n")
            
    print(f"Generated {len(srt_entries)} subtitle lines in {output_srt_path}")
    return len(srt_entries)

def main():
    base_dir = Path(r"d:\Antigravity\科技歷史\臺灣史")
    ch11_dir = base_dir / "舌尖上的臺灣" / "04_大江大海與眷村融合"
    
    vid_json = ch11_dir / "whisper_raw_video.json"
    pod_json = ch11_dir / "whisper_raw_podcast.json"
    
    vid_srt = ch11_dir / "第11章_那一碗鄉愁的紅湯_說明影片.srt"
    pod_srt = ch11_dir / "第11章_那一碗鄉愁的紅湯_雙人對談.srt"
    
    if vid_json.exists():
        build_srt_from_whisper_json(vid_json, vid_srt)
    if pod_json.exists():
        build_srt_from_whisper_json(pod_json, pod_srt)

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        build_srt_from_whisper_json(sys.argv[1], sys.argv[2])
    else:
        main()
