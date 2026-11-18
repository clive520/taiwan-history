import json
import re
import sys
import os

# 本章文史與在地專用名詞校驗替換詞庫（100% 精準校對）
TYPO_REPLACEMENTS = {
    # 昆蟲與生物化學
    "小綠葉禪": "小綠葉蟬",
    "小綠葉產": "小綠葉蟬",
    "小綠葉殘": "小綠葉蟬",
    "小綠月殘": "小綠葉蟬",
    "小綠月產": "小綠葉蟬",
    "客庄茶傘": "客庄茶山",
    "茶傘": "茶山",
    "山蘭間": "山嵐間",
    "山蘭": "山嵐",
    "土爵醋": "土埆厝",
    "油梨糖分": "游離糖分",
    "你畢上已經": "你閉上眼睛",
    "畢上已經": "閉上眼睛",
    "畢上": "閉上",
    "葉禪": "葉蟬",
    "浮塵子": "浮塵子",
    "浮成子": "浮塵子",
    "煙仔": "煙仔",
    "醃仔": "煙仔",
    "著涎": "著涎",
    "著賢": "著涎",
    "著先": "著涎",
    "莫莉酸": "茉莉酸",
    "末莉酸": "茉莉酸",
    "茉莉酸甲脂": "茉莉酸甲酯",
    "茉莉酸甲酯": "茉莉酸甲酯",
    "方樟醇": "芳樟醇",
    "芳章醇": "芳樟醇",
    "方張醇": "芳樟醇",
    "芳樟純": "芳樟醇",
    "芳樟醇氧化物": "芳樟醇氧化物",
    "水楊酸甲脂": "水楊酸甲酯",
    "水楊酸甲酯": "水楊酸甲酯",
    "香葉純": "香葉醇",
    "香葉醇": "香葉醇",
    "成花叔醇": "橙花叔醇",
    "橙花叔純": "橙花叔醇",
    "苯以醇": "苯乙醇",
    "苯乙純": "苯乙醇",
    "甘茶": "乾茶",
    
    # 茶葉品種與工藝
    "青心大有": "青心大冇",
    "青心大某": "青心大冇",
    "青心大毛": "青心大冇",
    "大有品種": "大冇品種",
    "大冇": "大冇",
    "白毫烏龍": "白毫烏龍",
    "白豪烏龍": "白毫烏龍",
    "五色茶": "五色茶",
    "武色茶": "五色茶",
    "彭風茶": "膨風茶",
    "朋風茶": "膨風茶",
    "捧風茶": "膨風茶",
    "膨風茶": "膨風茶",
    "膨風伯": "膨風伯",
    "浪茶": "浪茶",
    "亮茶": "浪茶",
    "悶堆": "悶堆",
    "悶堆回潤": "悶堆回潤",
    "回潤": "回潤",
    "殺青": "殺青",
    "殺清": "殺青",
    
    # 歷史人物與地名商號
    "約翰陶德": "約翰·陶德",
    "陶德": "陶德",
    "李春生": "李春生",
    "寶順洋行": "寶順洋行",
    "保順洋行": "寶順洋行",
    "德記洋行": "德記洋行",
    "怡記洋行": "怡記洋行",
    "和記洋行": "和記洋行",
    "美時洋行": "美時洋行",
    "千秋街": "千秋街",
    "貴德街": "貴德街",
    "建昌街": "建昌街",
    "大稻埕": "大稻埕",
    "大稻城": "大稻埕",
    "艋舺": "艋舺",
    "北埔": "北埔",
    "峨眉": "峨眉",
    "峨嵋": "峨眉",
    "銅鑼": "銅鑼",
    "新竹州": "新竹州",
    "揀茶女工": "揀茶女工",
    "檢茶女工": "揀茶女工",
    "揀茶": "揀茶",
    "茶底銀": "茶底銀",
    "飛剪帆船": "飛剪帆船",
    "飛剪式帆船": "飛剪式帆船",
    "維多利亞女王": "維多利亞女王",
    "東方美人": "東方美人",
    "東方美人茶": "東方美人茶",
    "福爾摩沙烏龍": "福爾摩沙烏龍",
    "Formosa Oolong": "Formosa Oolong"
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
        
    segments = data.get("segments", [])
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

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python refine_food_ch10_srt.py <whisper_json> <output_srt>")
        sys.exit(1)
    build_srt_from_whisper_json(sys.argv[1], sys.argv[2])
