# -*- coding: utf-8 -*-
import json
import re
import sys
import os
from pathlib import Path

# 專用歷史與美食在地名詞精準校正字典（100% 繁體中文與專業術語）
TYPO_REPLACEMENTS = {
    # 豆漿與早點店號
    "永和豆浆": "永和豆漿",
    "永和豆漿": "永和豆漿",
    "世界豆浆大王": "世界豆漿大王",
    "世界豆漿大王": "世界豆漿大王",
    "阜杭豆浆": "阜杭豆漿",
    "阜杭豆漿": "阜杭豆漿",
    "阜航": "阜杭",
    "華山市場": "華山市場",
    "华山市场": "華山市場",
    "中正橋": "中正橋",
    "中正桥": "中正橋",
    "李齊榮": "李齊榮",
    "李齐荣": "李齊榮",
    
    # 麵食與豆製品工藝
    "燒餅": "燒餅",
    "烧饼": "燒餅",
    "厚燒餅": "厚燒餅",
    "薄燒餅": "薄燒餅",
    "油條": "油條",
    "油条": "油條",
    "豆漿": "豆漿",
    "豆浆": "豆漿",
    "鹹豆漿": "鹹豆漿",
    "咸豆浆": "鹹豆漿",
    "甜豆漿": "甜豆漿",
    "清漿": "清漿",
    "清浆": "清漿",
    "水餃": "水餃",
    "水饺": "水餃",
    "餃子": "餃子",
    "水餃子": "水餃",
    "韭菜水餃": "韭菜水餃",
    "點水三回": "點水三回",
    "點水": "點水",
    "蔥油餅": "蔥油餅",
    "葱油饼": "蔥油餅",
    "烙餅": "烙餅",
    "烙饼": "烙餅",
    "單餅": "單餅",
    "燙麵": "燙麵",
    "烫面": "燙麵",
    
    # 科學與原料術語
    "等電點": "等電點",
    "等电点": "等電點",
    "大豆球蛋白": "大豆球蛋白",
    "大豆求蛋白": "大豆球蛋白",
    "凝乳": "凝乳",
    "油酥": "油酥",
    "麵筋": "麵筋",
    "面筋": "麵筋",
    "水麵": "水麵",
    "水面油酥": "水麵油酥",
    "麥穀蛋白": "麥穀蛋白",
    "醇溶蛋白": "醇溶蛋白",
    "二硫鍵": "二硫鍵",
    "碳酸氫鈉": "碳酸氫鈉",
    "碳酸氫銨": "碳酸氫銨",
    "明礬": "明礬",
    "美拉德反應": "美拉德反應",
    "焦糖化反應": "焦糖化反應",
    "靜重": "淨重",
    "淨重22公斤": "淨重22公斤",
    "地緣爭執": "地緣政治",
    "傳統石鋪": "傳統食譜",
    
    # 歷史政策與人物
    "中美合作": "中美合作",
    "美援": "美援",
    "美援麵粉": "美援麵粉",
    "美援面粉": "美援麵粉",
    "公法480號": "公法480號",
    "公法 480 號": "公法 480 號",
    "PL 480": "PL 480",
    "PL480": "PL 480",
    "糧食和平計畫": "糧食和平計畫",
    "以麵代米": "以麵代米",
    "以面代米": "以麵代米",
    "農復會": "農復會",
    "农复会": "農復會",
    "JCRR": "JCRR",
    "李國鼎": "李國鼎",
    "李国鼎": "李國鼎",
    "沈宗瀚": "沈宗瀚",
    "臺灣麵食推廣委員會": "臺灣麵食推廣委員會",
    "中華穀類食品工業技術研究所": "中華穀類食品工業技術研究所",
    "米其林": "米其林",
    "必比登": "必比登",
    "必比登推介": "必比登推介",
    
    # 文學名家與著作
    "梁實秋": "梁實秋",
    "梁实秋": "梁實秋",
    "雅舍談吃": "《雅舍談吃》",
    "《《雅舍談吃》》": "《雅舍談吃》",
    "林海音": "林海音",
    "城南舊事": "《城南舊事》",
    "《《城南舊事》》": "《城南舊事》",
    "逯耀東": "逯耀東",
    "肚大能容": "《肚大能容》",
    "《《肚大能容》》": "《肚大能容》"
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
    ch12_dir = base_dir / "舌尖上的臺灣" / "04_大江大海與眷村融合"
    
    vid_json = ch12_dir / "whisper_raw_video.json"
    pod_json = ch12_dir / "whisper_raw_podcast.json"
    
    vid_srt = ch12_dir / "第12章_晨光裡的麵粉香_說明影片.srt"
    pod_srt = ch12_dir / "第12章_晨光裡的麵粉香_雙人對談.srt"
    
    if vid_json.exists():
        build_srt_from_whisper_json(vid_json, vid_srt)
    if pod_json.exists():
        build_srt_from_whisper_json(pod_json, pod_srt)

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        build_srt_from_whisper_json(sys.argv[1], sys.argv[2])
    else:
        main()
