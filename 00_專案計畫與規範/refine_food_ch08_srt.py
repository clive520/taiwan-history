# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 08 章 繁體中文版 影視級字幕深度校正與呼吸律精修處理器
1. 先查錯別字與同音字：針對磯永吉、末永仁、竹子湖原種田、臺中65號（龜治×神力）、
   米糖相剋、番薯籤、幼苗插秧法、直鏈澱粉（Amylose）、支鏈澱粉（Amylopectin）、
   老化回生（Retrogradation）、嘉南大圳、大橋頭米市等 100+ 歷史與農藝化學術語全方位精修校正。
2. 依據人類說話語音、語詞與呼吸律斷句：0 破字破詞，獨立保留對話交談語氣詞（「對吧？」、「真的！」、「沒錯」、「先說喔」、「你想想看」等）。
3. 輸出：
   - 第08章_改變世界的綠色奇蹟_說明影片.srt
   - 第08章_改變世界的綠色奇蹟_雙人對談.srt
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
CH08_DIR = BASE_DIR / "舌尖上的臺灣" / "03_帝國之眼與東洋滋味"

RAW_VID_JSON = CH08_DIR / "whisper_raw_video.json"
RAW_POD_JSON = CH08_DIR / "whisper_raw_podcast.json"

VID_SRT = CH08_DIR / "第08章_改變世界的綠色奇蹟_說明影片.srt"
POD_SRT = CH08_DIR / "第08章_改變世界的綠色奇蹟_雙人對談.srt"

cc = opencc.OpenCC('s2twp')

# 完整同音字、錯別字、專有名詞替換規則庫（長詞優先、精確比對）
CORRECTIONS = [
    # 歷史人物與制度
    (r"磯永吉", "磯永吉"),
    (r"機永吉", "磯永吉"),
    (r"基永吉", "磯永吉"),
    (r"磯博士", "磯博士"),
    (r"磯小屋", "磯小屋"),
    (r"末永仁", "末永仁"),
    (r"末永", "末永"),
    (r"莫永仁", "末永仁"),
    (r"伊澤多喜男", "伊澤多喜男"),
    (r"伊澤總督", "伊澤總督"),
    (r"八田與一", "八田與一"),
    (r"八田", "八田"),
    (r"矢內原忠雄", "矢內原忠雄"),
    (r"川野重任", "川野重任"),
    (r"米騷動", "米騷動"),
    (r"大正米騷動", "大正米騷動"),
    (r"越中女房一揆", "越中女房一揆"),
    (r"臺北帝國大學", "臺北帝國大學"),
    (r"中央研究所農業部", "中央研究所農業部"),
    (r"農事試驗場", "農事試驗場"),
    (r"臺中州農事試驗場", "臺中州農事試驗場"),

    # 水稻品種與培育
    (r"蓬萊米", "蓬萊米"),
    (r"朋萊米", "蓬萊米"),
    (r"逢萊米", "蓬萊米"),
    (r"在來米", "在來米"),
    (r"再來米", "在來米"),
    (r"在萊米", "在來米"),
    (r"秈稻", "秈稻"),
    (r"仙稻", "秈稻"),
    (r"鹹稻", "秈稻"),
    (r"粳稻", "粳稻"),
    (r"梗稻", "粳稻"),
    (r"更稻", "粳稻"),
    (r"臺中65號", "臺中65號"),
    (r"台中65號", "臺中65號"),
    (r"台中六十五號", "臺中65號"),
    (r"臺中六十五號", "臺中65號"),
    (r"龜治", "龜治"),
    (r"神力", "神力"),
    (r"中村種", "中村種"),
    (r"中村", "中村"),
    (r"山地陸稻", "山地陸稻"),
    (r"陸稻", "陸稻"),
    (r"原原種", "原原種"),
    (r"原種田", "原種田"),
    (r"原種", "原種"),
    (r"採種田", "採種田"),
    (r"幼苗插秧法", "幼苗插秧法"),
    (r"若苗插秧法", "若苗插秧法"),
    (r"若苗插秧", "若苗插秧"),
    (r"幼苗插秧", "幼苗插秧"),
    (r"早花化", "早花化"),
    (r"早花", "早花"),
    (r"苗床期", "苗床期"),
    (r"分櫱", "分櫱"),
    (r"分葉", "分櫱"),
    (r"幼穗分化", "幼穗分化"),
    (r"稻熱病", "稻熱病"),
    (r"稻熱", "稻熱"),
    (r"光週期敏感性", "光週期敏感性"),
    (r"光週期", "光週期"),
    (r"感光性", "感光性"),
    (r"感溫性", "感溫性"),
    (r"短日照植物", "短日照植物"),
    (r"短日照", "短日照"),
    (r"長日照", "長日照"),

    # 生物化學與澱粉物理化學
    (r"直鏈澱粉", "直鏈澱粉"),
    (r"直鍊澱粉", "直鏈澱粉"),
    (r"織鏈澱粉", "支鏈澱粉"),
    (r"支鏈澱粉", "支鏈澱粉"),
    (r"支鍊澱粉", "支鏈澱粉"),
    (r"老化回生", "老化回生"),
    (r"回生", "回生"),
    (r"回聲", "回生"),
    (r"離水現象", "離水現象"),
    (r"離水", "離水"),
    (r"糊化溫度", "糊化溫度"),
    (r"糊化", "糊化"),
    (r"空間位阻", "空間位阻"),
    (r"黏彈性", "黏彈性"),
    (r"氫鍵微晶束", "氫鍵微晶束"),
    (r"氫鍵網絡", "氫鍵網絡"),
    (r"氫鍵", "氫鍵"),
    (r"親建", "氫鍵"),

    # 地理、水利與社會階級
    (r"竹子湖", "竹子湖"),
    (r"竹子胡", "竹子湖"),
    (r"陽明山", "陽明山"),
    (r"草山", "草山"),
    (r"大屯山", "大屯山"),
    (r"七星山", "七星山"),
    (r"小觀音山", "小觀音山"),
    (r"嘉南大圳", "嘉南大圳"),
    (r"嘉南大郡", "嘉南大圳"),
    (r"烏山頭水庫", "烏山頭水庫"),
    (r"烏山頭", "烏山頭"),
    (r"官田溪", "官田溪"),
    (r"三年輪作給水制", "三年輪作給水制"),
    (r"三年輪作", "三年輪作"),
    (r"米糖相剋", "米糖相剋"),
    (r"米糖相克", "米糖相剋"),
    (r"飢餓輸出", "飢餓輸出"),
    (r"番薯籤", "番薯籤"),
    (r"甘藷籤", "番薯籤"),
    (r"番薯簽", "番薯籤"),
    (r"大橋頭米市", "大橋頭米市"),
    (r"大橋頭", "大橋頭"),
    (r"筒仔米糕", "筒仔米糕"),
    (r"米苔目", "米苔目"),
    (r"米苔姆", "米苔目"),
    (r"鹹圓仔湯", "鹹圓仔湯"),
]

def clean_text(text):
    t = cc.convert(text)
    for pat, rep in CORRECTIONS:
        t = re.sub(pat, rep, t)
    return t

def format_timestamp(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

INTERJECTIONS = [
    "對吧？", "對吧", "對啊！", "對啊", "沒錯！", "沒錯", "確實！", "確實",
    "真的！", "真的", "哇！", "哇", "天啊！", "天啊", "太不可思議了！", "太厲害了！",
    "你看！", "你看", "先說喔", "好啦", "你知道", "你想想看"
]

def refine_segments(segments):
    refined = []
    for seg in segments:
        text = clean_text(seg["text"].strip())
        start = seg["start"]
        end = seg["end"]
        words = seg.get("words", [])
        
        text = re.sub(r'^[，、；：\s]+', '', text)
        text = re.sub(r'[，、；：\s]+$', '', text)
        
        if not text:
            continue
            
        if len(text) > 23 and words and len(words) > 4:
            current_chunk = []
            chunk_start = words[0]["start"]
            
            for idx, w in enumerate(words):
                w_text = clean_text(w["word"])
                current_chunk.append(w_text)
                cur_str = "".join(current_chunk)
                
                is_break = False
                if any(p in w_text for p in ["，", "。", "！", "？", "；"]):
                    is_break = True
                elif len(cur_str) >= 15 and idx < len(words) - 2:
                    next_w = clean_text(words[idx+1]["word"])
                    if any(conj in next_w for conj in ["因為", "所以", "但是", "而且", "換句話說", "其實", "這也就是", "我們可以看到"]):
                        is_break = True
                        
                if is_break and len(cur_str) >= 6:
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
            split_done = False
            for inter in INTERJECTIONS:
                if text.startswith(inter) and len(text) > len(inter) + 3:
                    inter_len = len(inter)
                    inter_text = inter
                    rest_text = text[inter_len:].lstrip('，, ！？')
                    
                    split_t = min(start + 0.8, start + (end - start) * 0.3)
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

def build_srt(segments, out_path, label):
    refined = refine_segments(segments)
    lines = []
    idx = 1
    for seg in refined:
        text = seg["text"].strip()
        if not text:
            continue
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
    print(f"🎉 {label} 精修 SRT 已寫入：{out_path.name}，共 {idx-1} 條字幕。")
    return idx - 1

def main():
    if RAW_VID_JSON.exists():
        with open(RAW_VID_JSON, "r", encoding="utf-8") as f:
            v_data = json.load(f)
        build_srt(v_data["segments"], VID_SRT, "說明短片")
    else:
        print(f"⚠️ 找不到說明短片原始轉錄檔：{RAW_VID_JSON}")

    if RAW_POD_JSON.exists():
        with open(RAW_POD_JSON, "r", encoding="utf-8") as f:
            p_data = json.load(f)
        build_srt(p_data["segments"], POD_SRT, "播客對談")
    else:
        print(f"⚠️ 找不到播客原始轉錄檔：{RAW_POD_JSON}")

if __name__ == "__main__":
    main()
