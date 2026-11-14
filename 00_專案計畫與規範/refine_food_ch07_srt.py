# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 07 章 繁體中文版 影視級字幕精修處理器
1. 先查錯別字與同音字：針對明鄭陳永華、瓦溜淋泥法、糖郊李勝興、五條港水仙宮、
   范伯倫《有閒階級論》炫耀性消費、阿舍菜、生炒鱔魚意麵、焦糖化、梅納反應、
   琥珀糖膜、半流體溶膠、T1R2/T1R3 甜味受體、味覺掩蔽、鮮味乘數（IMP/GMP/Glu）、
   白糖粿、椪糖玻璃化轉變等 100+ 歷史與食品科學術語進行全方位精修校正。
2. 依據人類說話語音、語詞與呼吸律斷句：0 破字破詞，獨立保留對話交談語氣詞（「對吧？」、「真的！」、「沒錯」、「天啊」等）。
3. 輸出：
   - 第07章_甘甜的舌尖密碼_說明影片.srt
   - 第07章_甘甜的舌尖密碼_雙人對談.srt
"""
import sys
import os
import json
import re
from pathlib import Path
import opencc

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH07_DIR = BASE_DIR / "舌尖上的臺灣" / "02_唐山渡海與閩粵交融"

RAW_VID_JSON = CH07_DIR / "whisper_raw_video.json"
RAW_POD_JSON = CH07_DIR / "whisper_raw_podcast.json"

VID_SRT = CH07_DIR / "第07章_甘甜的舌尖密碼_說明影片.srt"
POD_SRT = CH07_DIR / "第07章_甘甜的舌尖密碼_雙人對談.srt"

cc = opencc.OpenCC('s2twp')

# 完整精修替換對照表（按長度由長至短、精確規則優先）
CORRECTIONS = [
    # 歷史人物與典籍
    (r"陳永華", "陳永華"),
    (r"成永華", "陳永華"),
    (r"沈光文", "沈光文"),
    (r"季麒光", "季麒光"),
    (r"周鍾瑄", "周鍾瑄"),
    (r"范咸", "范咸"),
    (r"高拱乾", "高拱乾"),
    (r"片岡巖", "片岡巖"),
    (r"片剛巖", "片岡巖"),
    (r"片岡岩", "片岡巖"),
    (r"東寧王國", "東寧王國"),
    (r"東寧王朝", "東寧王朝"),
    (r"明正時期", "明鄭時期"),
    (r"明正", "明鄭"),
    (r"臺灣輿地跋尾", "《臺灣輿地跋尾》"),
    (r"臺灣雜記", "《臺灣雜記》"),
    (r"臺灣府志", "《臺灣府志》"),
    (r"諸羅縣志", "《諸羅縣志》"),
    (r"臺灣風俗誌", "《臺灣風俗誌》"),
    (r"有閒階級論", "《有閒階級論》"),
    (r"有限階級論", "《有閒階級論》"),
    (r"有錢階級論", "《有閒階級論》"),
    (r"托斯丹·范伯倫", "托斯丹·范伯倫"),
    (r"范伯倫", "范伯倫"),
    (r"凡伯倫", "范伯倫"),
    (r"梵伯倫", "范伯倫"),
    (r"炫耀性消費", "炫耀性消費"),
    (r"炫耀行消費", "炫耀性消費"),
    (r"阿舍菜", "阿舍菜"),
    (r"阿舍", "阿舍"),
    (r"阿社", "阿舍"),
    (r"阿涉", "阿舍"),

    # 製糖科技與貿易組織
    (r"瓦溜淋泥法", "瓦溜淋泥法"),
    (r"瓦溜", "瓦溜"),
    (r"瓦六", "瓦溜"),
    (r"瓦流", "瓦溜"),
    (r"淋泥法", "淋泥法"),
    (r"糖郊李勝興", "糖郊李勝興"),
    (r"李勝興", "李勝興"),
    (r"糖郊", "糖郊"),
    (r"唐郊", "糖郊"),
    (r"三郊之首", "三郊之首"),
    (r"三郊", "三郊"),
    (r"北郊蘇萬利", "北郊蘇萬利"),
    (r"南郊金永順", "南郊金永順"),
    (r"五條港", "五條港"),
    (r"水仙宮", "水仙宮"),
    (r"石精臼", "石精臼"),
    (r"石金臼", "石精臼"),
    (r"十精臼", "石精臼"),
    (r"赤崁樓", "赤崁樓"),
    (r"赤崁", "赤崁"),
    (r"白糖", "白糖"),
    (r"黑糖", "黑糖"),
    (r"紅糖", "紅糖"),
    (r"霜糖", "霜糖"),
    (r"二砂糖", "二砂糖"),
    (r"特砂", "特砂"),
    (r"蔗糖", "蔗糖"),

    # 地道名菜與烹飪術語
    (r"炒鱔魚意麵", "炒鱔魚意麵"),
    (r"生炒鱔魚意麵", "生炒鱔魚意麵"),
    (r"生炒鱔魚", "生炒鱔魚"),
    (r"炒鱔魚", "炒鱔魚"),
    (r"鱔魚意麵", "鱔魚意麵"),
    (r"鱔魚", "鱔魚"),
    (r"善魚", "鱔魚"),
    (r"善魚意麵", "鱔魚意麵"),
    (r"香菇肉羹", "香菇肉羹"),
    (r"浮水魚羹", "浮水魚羹"),
    (r"浮水虱目魚羹", "浮水虱目魚羹"),
    (r"虱目魚", "虱目魚"),
    (r"滷肉飯", "滷肉飯"),
    (r"肉燥飯", "肉燥飯"),
    (r"肉燥", "肉燥"),
    (r"白糖粿", "白糖粿"),
    (r"白糖果", "白糖粿"),
    (r"白糖貴", "白糖粿"),
    (r"白糖糕", "白糖粿"),
    (r"椪糖", "椪糖"),
    (r"膨糖", "椪糖"),
    (r"蹦糖", "椪糖"),
    (r"生鐵大鑊", "生鐵大鑊"),
    (r"生鐵鑊氣", "生鐵鑊氣"),
    (r"生鐵大鍋", "生鐵大鑊"),
    (r"大鑊", "大鑊"),
    (r"鑊氣", "鑊氣"),
    (r"獲氣", "鑊氣"),
    (r"火氣", "鑊氣"),
    (r"快速爐", "快速爐"),
    (r"黑豆蔭油", "黑豆蔭油"),
    (r"蔭油", "蔭油"),
    (r"烏醋", "烏醋"),
    (r"五印醋", "五印醋"),

    # 食品化學與分子生物學
    (r"焦糖化反應", "焦糖化反應"),
    (r"焦糖化", "焦糖化"),
    (r"梅納反應", "梅納反應"),
    (r"美拉德反應", "梅納反應"),
    (r"美納反應", "梅納反應"),
    (r"非還原糖", "非還原糖"),
    (r"還原糖", "還原糖"),
    (r"三甲胺", "三甲胺"),
    (r"琥珀糖膜", "琥珀糖膜"),
    (r"糖膜", "糖膜"),
    (r"番薯粉糊化", "番薯粉糊化"),
    (r"番薯粉勾芡", "番薯粉勾芡"),
    (r"勾芡", "勾芡"),
    (r"半流體溶膠", "半流體溶膠"),
    (r"溶膠流變學", "溶膠流變學"),
    (r"流變學", "流變學"),
    (r"T1R2/T1R3", "T1R2/T1R3"),
    (r"T1R2", "T1R2"),
    (r"T1R3", "T1R3"),
    (r"甜味受體", "甜味受體"),
    (r"味覺掩蔽", "味覺掩蔽"),
    (r"掩蔽效應", "掩蔽效應"),
    (r"鮮味乘數效應", "鮮味乘數效應"),
    (r"鮮味乘數", "鮮味乘數"),
    (r"肌苷酸", "肌苷酸"),
    (r"鳥苷酸", "鳥苷酸"),
    (r"麩胺酸", "麩胺酸"),
    (r"谷氨酸", "麩胺酸"),
    (r"麩胺酸鈉", "麩胺酸鈉"),
    (r"碳酸氫鈉熱分解", "碳酸氫鈉熱分解"),
    (r"碳酸氫鈉", "碳酸氫鈉"),
    (r"重曹", "碳酸氫鈉"),
    (r"玻璃化轉變", "玻璃化轉變"),
    (r"玻璃化溫度", "玻璃化溫度"),
    (r"玻璃態", "玻璃態"),
]

def clean_text(text):
    """全量繁體轉化與歷史/科技專用術語替換"""
    t = cc.convert(text)
    for pat, rep in CORRECTIONS:
        t = re.sub(pat, rep, t)
    return t

def format_timestamp(seconds):
    """將秒數轉為 SRT 標準時間戳 00:00:00,000"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

INTERJECTIONS = [
    "對吧？", "對吧", "對啊！", "對啊", "沒錯！", "沒錯", "確實！", "確實",
    "真的！", "真的", "哇！", "哇", "天啊！", "天啊", "太不可思議了！", "太厲害了！"
]

def refine_segments(segments):
    """依據呼吸律與交談語氣詞進行微細意群重組"""
    refined = []
    for seg in segments:
        text = clean_text(seg["text"].strip())
        start = seg["start"]
        end = seg["end"]
        words = seg.get("words", [])
        
        # 移除首尾多餘標點
        text = re.sub(r'^[，、；：\s]+', '', text)
        text = re.sub(r'[，、；：\s]+$', '', text)
        
        if not text:
            continue
            
        # 若單句過長（超過 25 字元），且包含停頓點或連接詞，進行細緻拆分
        if len(text) > 24 and words and len(words) > 4:
            # 依詞彙時間戳拆分
            current_chunk = []
            chunk_start = words[0]["start"]
            
            for idx, w in enumerate(words):
                w_text = clean_text(w["word"])
                current_chunk.append(w_text)
                cur_str = "".join(current_chunk)
                
                # 判斷是否為斷句點：包含標點或語氣詞或長度達標
                is_break = False
                if any(p in w_text for p in ["，", "。", "！", "？", "；", "、"]):
                    is_break = True
                elif len(cur_str) >= 16 and idx < len(words) - 2:
                    # 尋找自然的連接詞斷句
                    next_w = clean_text(words[idx+1]["word"])
                    if any(conj in next_w for conj in ["因為", "所以", "但是", "而且", "換句話說", "其實", "這也就是", "我們可以看到"]):
                        is_break = True
                        
                if is_break and len(cur_str) >= 8:
                    sub_text = re.sub(r'[，、；：\s]+$', '', cur_str)
                    if sub_text:
                        refined.append({
                            "start": chunk_start,
                            "end": w["end"],
                            "text": sub_text
                        })
                    current_chunk = []
                    if idx + 1 < len(words):
                        chunk_start = words[idx+1]["start"]
                        
            if current_chunk:
                cur_str = "".join(current_chunk)
                sub_text = re.sub(r'[，、；：\s]+$', '', cur_str)
                if sub_text:
                    refined.append({
                        "start": chunk_start,
                        "end": words[-1]["end"],
                        "text": sub_text
                    })
        else:
            # 短句或中等長度句子，直接檢查開頭語氣詞
            split_done = False
            for inter in INTERJECTIONS:
                if text.startswith(inter) and len(text) > len(inter) + 4:
                    # 分離語氣詞
                    inter_len = len(inter)
                    inter_text = inter
                    rest_text = text[inter_len:].lstrip('，, ！？')
                    
                    # 語氣詞時間約 0.6 ~ 0.8 秒
                    split_t = min(start + 0.8, start + (end - start) * 0.25)
                    refined.append({
                        "start": start,
                        "end": split_t,
                        "text": inter_text
                    })
                    refined.append({
                        "start": split_t,
                        "end": end,
                        "text": rest_text
                    })
                    split_done = True
                    break
            if not split_done:
                refined.append({
                    "start": start,
                    "end": end,
                    "text": text
                })
                
    return refined

def build_srt(segments, out_path):
    refined = refine_segments(segments)
    lines = []
    idx = 1
    for seg in refined:
        text = seg["text"].strip()
        if not text:
            continue
        # 移除結尾逗號，保留問號與驚嘆號
        if text.endswith("，") or text.endswith("、"):
            text = text[:-1]
        
        t_start = format_timestamp(seg["start"])
        t_end = format_timestamp(seg["end"])
        
        lines.append(f"{idx}")
        lines.append(f"{t_start} --> {t_end}")
        lines.append(text)
        lines.append("")
        idx += 1
        
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"🎉 精修 SRT 已寫入：{out_path.name}，共 {idx-1} 條字幕。")

def main():
    if RAW_VID_JSON.exists():
        with open(RAW_VID_JSON, "r", encoding="utf-8") as f:
            v_data = json.load(f)
        build_srt(v_data["segments"], VID_SRT)
    else:
        print(f"⚠️ 找不到說明短片原始轉錄檔：{RAW_VID_JSON}")

    if RAW_POD_JSON.exists():
        with open(RAW_POD_JSON, "r", encoding="utf-8") as f:
            p_data = json.load(f)
        build_srt(p_data["segments"], POD_SRT)
    else:
        print(f"⚠️ 找不到播客原始轉錄檔：{RAW_POD_JSON}")

if __name__ == "__main__":
    main()
