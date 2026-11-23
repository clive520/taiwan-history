# -*- coding: utf-8 -*-
import json
import re
import sys
import os
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 專用歷史與新臺菜、米其林專有名詞精準校正字典（100% 繁體中文與專業術語）
TYPO_REPLACEMENTS = {
    # 主廚與人物
    "江振誠": "江振誠",
    "何順凱": "何順凱",
    "黃德興": "黃德興",
    "何奕佳": "何奕佳",
    "陳嵐舒": "陳嵐舒",
    "林明健": "林明健",
    "André Chiang": "André Chiang",
    "Kai Ho": "Kai Ho",
    
    # 餐廳與地標
    "態芮": "態芮",
    "太芮": "態芮",
    "Taïrroir": "Taïrroir",
    "Tairroir": "Taïrroir",
    "RAW": "RAW",
    "山海樓": "山海樓",
    "蓬萊閣": "蓬萊閣",
    "江山樓": "江山樓",
    "請客樓": "請客樓",
    "樂群三路": "樂群三路",
    "大直": "大直",
    "華西街": "華西街",
    "小王煮瓜": "小王煮瓜",
    "黑金滷肉飯": "黑金滷肉飯",
    "瓜仔肉": "瓜仔肉",
    "崁仔頂": "崁仔頂",
    
    # 米其林體系
    "米其林指南": "米其林指南",
    "米其林三星": "米其林三星",
    "米其林二星": "米其林二星",
    "米其林一星": "米其林一星",
    "米其林綠星": "米其林綠星",
    "必比登推介": "必比登推介",
    "必比登": "必比登",
    "八角哲學": "八角哲學",
    "Octaphilosophy": "Octaphilosophy",
    "Fine Dining": "Fine Dining",
    "Haute Cuisine": "Haute Cuisine",
    "當代臺灣料理": "當代臺灣料理",
    "新臺菜": "新臺菜",
    "新台菜": "新臺菜",
    
    # 經典名菜與菜餚
    "金銀燒豬": "金銀燒豬",
    "肚包雞": "肚包雞",
    "布袋雞": "肚包雞",
    "掛爐燒雞": "掛爐燒雞",
    "迷思": "「迷思」",
    "泥解": "「泥解」",
    "金沙芋泥": "金沙芋泥",
    "茶葉蛋": "茶葉蛋",
    "鹹豆漿": "鹹豆漿",
    "大甲芋頭": "大甲芋頭",
    "檳榔心芋": "檳榔心芋",
    "油蔥酥": "油蔥酥",
    "紅蔥頭": "紅蔥頭",
    "三杯雞": "三杯雞",
    "燒番麥": "燒番麥",
    "烤玉米": "烤玉米",
    "野生愛玉": "野生愛玉",
    "愛玉子": "愛玉子",
    
    # 原生風土香料與植物學
    "馬告": "馬告",
    "山胡椒": "山胡椒",
    "Makauy": "Makauy",
    "刺蔥": "刺蔥",
    "食茱萸": "食茱萸",
    "Tana": "Tana",
    "破布子": "破布子",
    "甘露破布子": "甘露破布子",
    "樹子": "樹子",
    "臺灣紅藜": "臺灣紅藜",
    "紅藜": "紅藜",
    "Djulis": "Djulis",
    "刺莧": "刺莧",
    "野莧菜": "野莧菜",
    "樹豆": "樹豆",
    "苦茶油": "苦茶油",
    "黑蒜頭": "黑蒜頭",
    
    # 分子化學與烹飪科學
    "檸檬醛": "檸檬醛",
    "橙花醛": "橙花醛",
    "香葉醛": "香葉醛",
    "檸檬烯": "檸檬烯",
    "沉香醇": "沉香醇",
    "大葉花椒醇": "大葉花椒醇",
    "月桂烯": "月桂烯",
    "石竹烯": "石竹烯",
    "萜烯": "萜烯",
    "游離麩胺酸": "游離麩胺酸",
    "麩胺酸": "麩胺酸",
    "多醣體": "多醣體",
    "單寧": "單寧",
    "低溫油萃": "低溫油萃",
    "低溫慢煮": "低溫慢煮",
    "舒肥": "低溫慢煮",
    "真空低溫烹調": "真空低溫烹調",
    "美拉德反應": "梅納反應",
    "梅納反應": "梅納反應",
    "鑊氣": "鑊氣",
    "風土": "風土",
    "Terroir": "Terroir",
    "二十四節氣": "二十四節氣"
}

def clean_and_correct_text(text):
    # 簡轉繁常見漏網詞
    simplified_to_traditional = {
        "台湾": "臺灣", "台北": "臺北", "台中": "臺中", "台南": "臺南", "台東": "臺東",
        "米其林": "米其林", "主厨": "主廚", "餐厅": "餐廳", "风土": "風土",
        "八角哲学": "八角哲學", "咸豆浆": "鹹豆漿", "茶叶蛋": "茶葉蛋"
    }
    for s, t in simplified_to_traditional.items():
        text = text.replace(s, t)

    for wrong, right in TYPO_REPLACEMENTS.items():
        text = text.replace(wrong, right)
    
    # 移除多餘空白與語音破音符號
    text = re.sub(r'\s+', '', text)
    return text

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis -= 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def process_raw_json_to_srt(json_path, srt_path, max_len=24):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    srt_entries = []
    idx = 1

    for seg in data:
        raw_text = clean_and_correct_text(seg.get("text", ""))
        if not raw_text:
            continue
        
        start = seg["start"]
        end = seg["end"]
        duration = end - start

        # 如果句子長度合理，直接輸出
        if len(raw_text) <= max_len:
            srt_entries.append((idx, start, end, raw_text))
            idx += 1
        else:
            # 依據標點符號或語意進行自然拆句
            # 優先切分逗號、分號、頓號
            parts = re.split(r'([，,、；;。！!？?])', raw_text)
            chunks = []
            curr = ""
            for p in parts:
                if not p:
                    continue
                if p in "，,、；;。！!？?":
                    curr += p
                    if len(curr) >= 12:
                        chunks.append(curr)
                        curr = ""
                else:
                    if len(curr) + len(p) > max_len:
                        if curr:
                            chunks.append(curr)
                        curr = p
                    else:
                        curr += p
            if curr:
                chunks.append(curr)

            if not chunks:
                chunks = [raw_text]

            # 依據長度比例分配時間
            total_chars = sum(len(c) for c in chunks)
            c_start = start
            for c in chunks:
                c_dur = duration * (len(c) / total_chars)
                c_end = c_start + c_dur
                # 清除句首句末標點符號
                c_clean = c.strip("，,、；;。！!？?")
                if c_clean:
                    srt_entries.append((idx, c_start, c_end, c_clean))
                    idx += 1
                c_start = c_end

    # 寫入 SRT
    with open(srt_path, "w", encoding="utf-8") as f:
        for entry in srt_entries:
            i, s, e, txt = entry
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(s)} --> {format_timestamp(e)}\n")
            f.write(f"{txt}\n\n")

    print(f"✅ 生成影視級字幕：{srt_path.name}（共 {len(srt_entries)} 行）")

def main():
    BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
    CH15_DIR = BASE_DIR / "舌尖上的臺灣" / "05_島嶼綻放與世界舞台"
    
    raw_vid = CH15_DIR / "whisper_raw_video.json"
    raw_pod = CH15_DIR / "whisper_raw_podcast.json"
    
    out_vid_srt = CH15_DIR / "第15章_當代風土的米其林交響_說明影片.srt"
    out_pod_srt = CH15_DIR / "第15章_當代風土的米其林交響_雙人對談.srt"

    if raw_vid.exists():
        process_raw_json_to_srt(raw_vid, out_vid_srt, max_len=22)
    else:
        print(f"⚠️ 找不到 {raw_vid.name}")

    if raw_pod.exists():
        process_raw_json_to_srt(raw_pod, out_pod_srt, max_len=24)
    else:
        print(f"⚠️ 找不到 {raw_pod.name}")

if __name__ == "__main__":
    main()
