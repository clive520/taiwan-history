# -*- coding: utf-8 -*-
import json
import re
import sys
import os
from pathlib import Path

# 專用歷史與美食在地名詞精準校正字典（100% 繁體中文與專業術語）
TYPO_REPLACEMENTS = {
    # 辦桌與總鋪師體系
    "总铺师": "總鋪師",
    "總鋪師": "總鋪師",
    "总舖师": "總鋪師",
    "辦桌": "辦桌",
    "办桌": "辦桌",
    "伴桌": "辦桌",
    "伴奏團隊": "辦桌團隊",
    "伴奏": "辦桌",
    "風街": "封街",
    "封街搭棚": "封街搭棚",
    "內門": "內門",
    "内门": "內門",
    "羅漢門": "羅漢門",
    "罗汉门": "羅漢門",
    "宋江陣": "宋江陣",
    "宋江阵": "宋江陣",
    "水腳": "水腳",
    "水脚": "水腳",
    "水餃在支撐": "水腳在支撐",
    "都是水餃": "都是水腳",
    "水餃的辛苦": "水腳的辛苦",
    "水餃的角色": "水腳的角色",
    "頭手": "頭手",
    "头手": "頭手",
    "二手": "二手",
    "灶頭": "灶頭",
    "砧板": "砧板",
    "洗切": "洗切",
    "打包": "打包",
    "菜尾": "菜尾",
    "菜尾湯": "菜尾湯",
    "菜尾汤": "菜尾湯",
    "古早味": "古早味",
    "古早未": "古早味",
    
    # 經典辦桌大菜
    "大封肉": "大封肉",
    "一品大封肉": "一品大封肉",
    "紅蟳米糕": "紅蟳米糕",
    "红蟳米糕": "紅蟳米糕",
    "紅蟳": "紅蟳",
    "红蟳": "紅蟳",
    "米糕": "米糕",
    "扁魚白菜滷": "扁魚白菜滷",
    "扁鱼白菜卤": "扁魚白菜滷",
    "白菜滷": "白菜滷",
    "白菜卤": "白菜滷",
    "扁魚": "扁魚",
    "扁鱼": "扁魚",
    "開陽": "開陽",
    "香菇": "香菇",
    "五福拼盤": "五福拼盤",
    "五福拼盘": "五福拼盤",
    "烏魚子": "烏魚子",
    "烏魚子拼盤": "烏魚子拼盤",
    "鳳梨蝦球": "鳳梨蝦球",
    "凤梨虾球": "鳳梨蝦球",
    "清蒸海上鮮": "清蒸海上鮮",
    "筍乾": "筍乾",
    "酸筍": "酸筍",
    "酸筍絲": "酸筍絲",
    
    # 夜市宵夜與小吃
    "蚵仔煎": "蚵仔煎",
    "蚵仔": "蚵仔",
    "蚵仔麵線": "蚵仔麵線",
    "鹽酥雞": "鹽酥雞",
    "盐酥鸡": "鹽酥雞",
    "咸酥鸡": "鹽酥雞",
    "九層塔": "九層塔",
    "九层塔": "九層塔",
    "地瓜粉": "地瓜粉",
    "太白粉": "太白粉",
    "樹薯粉": "樹薯粉",
    "番薯粉": "番薯粉",
    "茼蒿": "茼蒿",
    "甜辣醬": "甜辣醬",
    "醬油膏": "醬油膏",
    "味噌": "味噌",
    "夜市": "夜市",
    "宵夜": "宵夜",
    "消夜": "宵夜",
    "建成圓環": "建成圓環",
    "建成圆环": "建成圓環",
    "寧夏夜市": "寧夏夜市",
    "宁夏夜市": "寧夏夜市",
    "基隆廟口": "基隆廟口",
    "基隆庙口": "基隆廟口",
    "逢甲夜市": "逢甲夜市",
    "六合夜市": "六合夜市",
    "士林夜市": "士林夜市",
    "大排檔": "大排檔",
    "大排档": "大排檔",
    
    # 歷史政策、工業化與人物
    "客廳即工廠": "客廳即工廠",
    "客厅即工厂": "客廳即工廠",
    "謝東閔": "謝東閔",
    "谢东闵": "謝東閔",
    "加工出口區": "加工出口區",
    "加工出口区": "加工出口區",
    "楠梓加工出口區": "楠梓加工出口區",
    "高雄加工出口區": "高雄加工出口區",
    "三班倒": "三班倒",
    "大夜班": "大夜班",
    "黑手": "黑手",
    "女工": "女工",
    "外銷代工": "外銷代工",
    "中小企業": "中小企業",
    "米其林": "米其林",
    "必比登": "必比登",
    "必比登推介": "必比登推介",
    "焦桐": "焦桐",
    "林文月": "林文月",
    "黃婉玲": "黃婉玲",
    
    # 分子烹飪與食品科學硬核名詞
    "膠原蛋白": "膠原蛋白",
    "胶原蛋白": "膠原蛋白",
    "I型膠原蛋白": "I型膠原蛋白",
    "明膠": "明膠",
    "明胶": "明膠",
    "明膠化": "明膠化",
    "熱變性": "熱變性",
    "三螺旋結構": "三螺旋結構",
    "肌苷酸": "肌苷酸",
    "肌苷酸二鈉": "肌苷酸二鈉",
    "IMP": "IMP",
    "麩胺酸": "麩胺酸",
    "麩胺酸鈉": "麩胺酸鈉",
    "MSG": "MSG",
    "鮮味相乘": "鮮味相乘",
    "鮮味協同": "鮮味協同",
    "丁香酚": "丁香酚",
    "酯化反應": "酯化反應",
    "酯化": "酯化",
    "美拉德反應": "美拉德反應",
    "焦糖化反應": "焦糖化反應",
    "直鏈澱粉": "直鏈澱粉",
    "支鏈澱粉": "支鏈澱粉",
    "糊化": "糊化",
    "玻璃化轉變": "玻璃化轉變",
    "乳酸": "乳酸",
    "乙酸": "乙酸",
    "嘌呤核苷酸": "嘌呤核苷酸",
    "瓢瓴核桿酸": "嘌呤核苷酸",
    "核桿酸": "核苷酸",
    "唐揚雞": "唐揚雞",
    "唐洋雞": "唐揚雞",
    "台灣": "臺灣",
    "台湾": "臺灣",
    
    # 口語與通用校正
    "對吧？": "對吧？",
    "沒錯！": "沒錯！",
    "真的！": "真的！"
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
    ch13_dir = base_dir / "舌尖上的臺灣" / "04_大江大海與眷村融合"
    
    vid_json = ch13_dir / "whisper_raw_video.json"
    pod_json = ch13_dir / "whisper_raw_podcast.json"
    
    vid_srt = ch13_dir / "第13章_黑夜裡的流動盛宴_說明影片.srt"
    pod_srt = ch13_dir / "第13章_黑夜裡的流動盛宴_雙人對談.srt"
    
    if vid_json.exists():
        build_srt_from_whisper_json(vid_json, vid_srt)
    if pod_json.exists():
        build_srt_from_whisper_json(pod_json, pod_srt)

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        build_srt_from_whisper_json(sys.argv[1], sys.argv[2])
    else:
        main()
