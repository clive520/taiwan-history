# -*- coding: utf-8 -*-
import json
import re
import sys
import os
from pathlib import Path

# 專用歷史與手搖飲專有名詞精準校正字典（100% 繁體中文與專業術語）
TYPO_REPLACEMENTS = {
    # 珍奶品牌、名店與人物
    "春水堂": "春水堂",
    "翰林茶館": "翰林茶館",
    "翰林": "翰林",
    "陽羨茶行": "陽羨茶行",
    "陽羨": "陽羨",
    "劉漢介": "劉漢介",
    "刘汉介": "劉漢介",
    "林秀慧": "林秀慧",
    "涂宗和": "涂宗和",
    "建國市場": "建國市場",
    "鸭母寮": "鴨母寮",
    "鴨母寮市場": "鴨母寮市場",
    "四維街": "四維街",
    "快可立": "快可立",
    "休閒小站": "休閒小站",
    "樂立杯": "樂立杯",
    "五十嵐": "五十嵐",
    "日出茶太": "日出茶太",
    "六角國際": "六角國際",
    "貢茶": "貢茶",
    "老虎堂": "老虎堂",
    "幸福堂": "幸福堂",
    "CoCo都可": "CoCo都可",
    "都可": "都可",
    
    # 飲品與原料品類
    "珍珠奶茶": "珍珠奶茶",
    "珍珠奶茶的": "珍珠奶茶的",
    "波霸奶茶": "波霸奶茶",
    "波霸": "波霸",
    "黑珍珠": "黑珍珠",
    "白珍珠": "白珍珠",
    "白玉珍珠": "白玉珍珠",
    "熊貓珍珠": "熊貓珍珠",
    "泡沫紅茶": "泡沫紅茶",
    "雪克杯": "雪克杯",
    "不鏽鋼雪克杯": "不鏽鋼雪克杯",
    "調酒器": "調酒器",
    "粉圓": "粉圓",
    "黑糖粉圓": "黑糖粉圓",
    "樹薯粉圓": "樹薯粉圓",
    "樹薯澱粉": "樹薯澱粉",
    "樹薯粉": "樹薯粉",
    "太白粉": "太白粉",
    "黑糖蜜": "黑糖蜜",
    "黑糖虎紋": "黑糖虎紋",
    
    # 機械與工程專利
    "益芳": "益芳",
    "益芳封口機": "益芳封口機",
    "自動封口機": "自動封口機",
    "封口機": "封口機",
    "葉益芳": "葉益芳",
    "熱壓封口": "熱壓封口",
    "封口薄膜": "封口薄膜",
    "熱熔": "熱熔",
    "粗吸管": "粗吸管",
    "斜口粗吸管": "斜口粗吸管",
    "斜口吸管": "斜口吸管",
    "平口吸管": "平口吸管",
    "瓶口吸管": "平口吸管",
    "應力集中": "應力集中",
    "聚丙烯": "聚丙烯",
    "PP杯": "PP杯",
    "雙相流": "雙相流",
    
    # 食品物理化學與流變學
    "支鏈澱粉": "支鏈澱粉",
    "直鏈澱粉": "直鏈澱粉",
    "樹薯澱粉": "樹薯澱粉",
    "素屬澱粉": "樹薯澱粉",
    "改性樹薯澱粉": "改性樹薯澱粉",
    "改性素屬澱粉": "改性樹薯澱粉",
    "耐凍的改性樹薯澱粉": "耐凍的改性樹薯澱粉",
    "耐動的改性素屬澱粉": "耐凍的改性樹薯澱粉",
    "第一步是沸水翻滾": "第一步是沸水翻滾",
    "第一部是廢水翻滾": "第一步是沸水翻滾",
    "沸水翻滾": "沸水翻滾",
    "廢水翻滾": "沸水翻滾",
    "沸水": "沸水",
    "糊化": "糊化",
    "糊化度": "糊化度",
    "老化回生": "老化回生",
    "回生": "回生",
    "脫水收縮": "脫水收縮",
    "儲能模量": "儲能模量",
    "彈性模量": "彈性模量",
    "滲透壓": "滲透壓",
    "微氣泡": "微氣泡",
    "兒茶素": "兒茶素",
    "茶多酚": "茶多酚",
    "美拉德反應": "美拉德反應",
    "焦糖化反應": "焦糖化反應",
    "焦糖化": "焦糖化",
    "熱收縮": "熱收縮",
    "冷水激冷": "冷水激冷",
    
    # 地名、國際流行語與國家
    "台灣": "臺灣",
    "台湾": "臺灣",
    "羅浮宮": "羅浮宮",
    "盧浮宮": "羅浮宮",
    "澀谷": "澀谷",
    "涉谷": "澀谷",
    "時代廣場": "時代廣場",
    "智慧財產法院": "智慧財產法院",
    "智財法院": "智慧財產法院",
    "文化資產": "文化資產",
    "Boba": "Boba",
    "タピる": "タピる",
    "タピオカ": "タピオカ"
}

def clean_and_replace_text(text):
    for wrong, right in TYPO_REPLACEMENTS.items():
        text = text.replace(wrong, right)
    text = re.sub(r'[\r\n]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def segment_sentence_by_breath(text):
    text = clean_and_replace_text(text)
    if not text:
        return []
        
    tokens = re.split(r'([。？！?!；;])', text)
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
    ch14_dir = base_dir / "舌尖上的臺灣" / "05_島嶼綻放與世界舞台"
    
    vid_json = ch14_dir / "whisper_raw_video.json"
    pod_json = ch14_dir / "whisper_raw_podcast.json"
    
    vid_srt = ch14_dir / "第14章_吸管裡的黑色奇蹟_說明影片.srt"
    pod_srt = ch14_dir / "第14章_吸管裡的黑色奇蹟_雙人對談.srt"
    
    if vid_json.exists():
        build_srt_from_whisper_json(vid_json, vid_srt)
    if pod_json.exists():
        build_srt_from_whisper_json(pod_json, pod_srt)

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        build_srt_from_whisper_json(sys.argv[1], sys.argv[2])
    else:
        main()
