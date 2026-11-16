import json
import re
import sys
import os

# 本章文史與在地專用名詞校驗替換詞庫（100% 精準校對）
TYPO_REPLACEMENTS = {
    # 總體與感官旅程
    "極其憂悵": "極其悠長",
    "憂悵": "悠長",
    "響車雲霄": "響徹雲霄",
    "響車": "響徹",
    "英國關係": "因果關係",
    "氣笛": "汽笛",
    "氣滴": "汽笛",
    "火車氣笛": "火車汽笛",
    "火車氣滴": "火車汽笛",
    "總冠鐵路": "縱貫鐵路",
    "縱冠鐵路": "縱貫鐵路",
    "重冠鐵路": "縱貫鐵路",
    "中冠鐵路": "縱貫鐵路",
    "長谷川緊介": "長谷川謹介",
    "長谷川警界": "長谷川謹介",
    "載人親王": "載仁親王",
    "再人親王": "載仁親王",
    "在任親王": "載仁親王",
    "湖心亭": "湖心亭",
    "時刻錶": "時刻表",
    "雅熱帶": "亞熱帶",
    "牙熱帶": "亞熱帶",
    "台北西來壤網": "臺北熙來攘往",
    "熙來壤網": "熙來攘往",
    "還沒完內": "還沒完呢",
    "那身1908年": "那聲1908年",
    
    # 經木與物性科學
    "金木合": "經木盒",
    "金木盒": "經木盒",
    "金木": "經木",
    "精木": "經木",
    "經目": "經木",
    "驚木": "經木",
    "金目": "經木",
    "京木": "經木",
    "薄木片核": "薄木片盒",
    "小木河": "小木盒",
    "圍孔的食物纖維": "微孔的植物纖維",
    "圍孔": "微孔",
    "壞木或山木": "檜木或杉木",
    "壞木": "檜木",
    "山木": "杉木",
    "壞木蟲跟丹寧酸": "檜木醇跟單寧酸",
    "壞木蟲": "檜木醇",
    "丹寧酸": "單寧酸",
    "單林酸": "單寧酸",
    "芬多精": "芬多精",
    "管胞": "管胞",
    
    # 便當與菜色
    "日知丸便當": "日之丸便當",
    "日智丸便當": "日之丸便當",
    "日誌丸便當": "日之丸便當",
    "日知丸": "日之丸",
    "日智丸": "日之丸",
    "玉子燒": "玉子燒",
    "金平牛蒡": "金平牛蒡",
    "奈良漬": "奈良漬",
    "台鐵便當": "臺鐵便當",
    "鐵路便當": "鐵路便當",
    "一邊": "驛弁",
    "意邊": "驛弁",
    "翼弁": "驛弁",
    "排骨便當": "排骨便當",
    "菜圃": "菜脯",
    "蔡脯": "菜脯",
    "酸菜": "酸菜",
    
    # 飯店與建築
    "鐵道飯店": "鐵道飯店",
    "鐵道旅館": "鐵道飯店",
    "帝國飯店": "帝國飯店",
    "奧的斯": "奧的斯",
    "奧迪斯": "奧的斯",
    "生降機": "昇降機",
    "升降機": "昇降機",
    "都鐸式": "都鐸式",
    "邁森": "邁森",
    "麥森": "邁森",
    "雙倍牛澄清湯": "雙倍牛澄清湯",
    "澄清湯": "澄清湯",
    "康索美": "Consommé",
    "金燉牛排": "精燉牛排",
    
    # 喫茶店與摩登生活
    "玻麗路": "波麗路",
    "玻璃路": "波麗路",
    "柏麗路": "波麗路",
    "波麗露": "波麗路",
    "博麗路": "波麗路",
    "廖水來": "廖水來",
    "廖水藍": "廖水來",
    "莫里斯拉威爾": "莫里斯·拉威爾",
    "拉威爾": "拉威爾",
    "山水亭": "山水亭",
    "山水庭": "山水亭",
    "王井泉": "王井泉",
    "王井權": "王井泉",
    "天馬茶房": "天馬茶房",
    "詹天馬": "詹天馬",
    "女給": "女給",
    "女節": "女給",
    "女階": "女給",
    "大正浪漫": "大正浪漫",
    "昭和摩登": "昭和摩登",
    "喫茶店": "喫茶店",
    "吃茶店": "喫茶店",
    "七茶店": "喫茶店",
    "氣茶店": "喫茶店",
    
    # 啤酒與發酵科技
    "高砂賣酒朱惠社": "高砂麥酒株式會社",
    "高砂賣酒": "高砂麥酒",
    "高砂麥酒": "高砂麥酒",
    "高殺麥酒": "高砂麥酒",
    "高沙麥酒": "高砂麥酒",
    "高沙買酒": "高砂麥酒",
    "朱惠社": "株式會社",
    "德國安亞洲機": "德國氨壓縮機",
    "安亞洲機": "氨壓縮機",
    "氨壓縮機": "氨壓縮機",
    "氨壓縮": "氨壓縮",
    "安壓縮": "氨壓縮",
    "生啤酒": "生啤酒",
    "生皮酒": "生啤酒",
    "建國啤酒廠": "建國啤酒廠",
    "拉格": "拉格",
    "底層發酵": "底層發酵",
    "啤酒館": "啤酒館",
    "Beer Hall": "Beer Hall",
    "可樂餅": "可樂餅",
    "炸可樂餅": "炸可樂餅",
    
    # 乳品與甜品
    "森永製菓": "森永製菓",
    "明治製菓": "明治製菓",
    "森永": "森永",
    "明治": "明治",
    "加糖煉乳": "加糖煉乳",
    "保久乳": "保久乳",
    "冰果室": "冰菓室",
    "香蕉油": "香蕉油"
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
        print("Usage: python refine_food_ch09_srt.py <whisper_json> <output_srt>")
        sys.exit(1)
    build_srt_from_whisper_json(sys.argv[1], sys.argv[2])
