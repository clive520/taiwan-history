# -*- coding: utf-8 -*-
import sys
import json
import re
from pathlib import Path
import jieba

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
RAW_JSON = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味" / "第02章_說明影片_raw_words.json"
OUT_SRT = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味" / "第02章_大航海的蔗香與鹿皮_說明影片.srt"

CUSTOM_WORDS = [
    "熱蘭遮城", "普羅民遮", "大員", "臺江內海", "荷蘭東印度公司", "VOC", "甘治士", "揆一", "尤羅伯",
    "西拉雅族", "新港社", "蕭壠社", "麻豆社", "目加溜灣社", "贌社制度", "贌商", "王田制度", "水牛",
    "臺灣梅花鹿", "梅花鹿", "生鹿皮", "鹿肉乾", "hertenvleesch", "陣羽織", "長崎出島", "出島", "長崎",
    "糖廍", "糖車", "石磨", "雙石磨", "熟石灰", "澄清反應", "五聯鼎", "孔明鼎", "瓦溜", "淋泥法",
    "白糖", "赤砂糖", "黑砂糖", "烏糖", "糖蜜", "荷蘭豆", "檨仔", "土芒果", "情人果", "蓮霧",
    "番荔枝", "釋迦", "番石榴", "芭樂", "柑仔蜜", "番椒", "哥倫布大交換", "臺南甜", "最高處", "壓製好",
    "終生難忘", "極端衝突", "赤崁平原", "1638年", "秋天", "畫面喔", "臺南安平", "刺鼻", "散發著",
    "血水", "蒼蠅", "野性羶味", "日夜都在", "化不開", "焦糖甜香", "世界舞台", "重量級", "一手史料",
    "大員長官", "《熱蘭遮城日記》", "《臺灣略記》", "《被遺誤的臺灣》", "《裨海紀遊》", "郁永河", "回憶錄",
    "全球化輸送帶", "味覺基因", "巨大蝴蝶效應", "物理面貌", "截然不同", "親眼觀察", "生物化學工程",
    "大洗牌", "炒鱔魚", "滷肉飯", "時空旅行", "15萬張", "几乎絕跡", "幾乎絕跡", "制度"
]
for w in CUSTOM_WORDS:
    jieba.add_word(w)

CORRECTIONS = [
    (r"台([灣北市南中東中東南東東南])", r"臺\1"),
    (r"[臺台]灣", "臺灣"),
    (r"熱蘭[遮折周週]城?", "熱蘭遮城"),
    (r"普羅[民明]遮", "普羅民遮"),
    (r"赤[崁崁嵌]樓?", "赤崁"),
    (r"大[員圓園元]", "大員"),
    (r"臺江內海", "臺江內海"),
    (r"甘[治志之][士仕氏]", "甘治士"),
    (r"揆[一一]|奎伊|魁一", "揆一"),
    (r"臺灣[略劣烈][記跡]", "《臺灣略記》"),
    (r"熱蘭遮城日記", "《熱蘭遮城日記》"),
    (r"糖[廍部廓埔]", "糖廍"),
    (r"[生熟]?[露路鹿]皮", "生鹿皮"),
    (r"雪水", "血水"),
    (r"野性[山羶羶]味", "野性羶味"),
]

def format_timestamp(seconds: float) -> str:
    total_ms = int(round(seconds * 1000))
    hours = total_ms // 3600000
    rem = total_ms % 3600000
    minutes = rem // 60000
    rem = rem % 60000
    secs = rem // 1000
    ms = rem % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

def clean_text(t: str) -> str:
    for pat, rep in CORRECTIONS:
        t = re.sub(pat, rep, t)
    t = t.replace('?', '？').replace('!', '！').replace(',', '，')
    t = re.sub(r'^[，。！？、；：\s]+', '', t)
    t = re.sub(r'[，。！？、；：\s]+$', '', t)
    return t

def split_long_text_by_jieba(text: str, max_len=15):
    words = list(jieba.cut(text))
    lines = []
    cur = []
    for w in words:
        if sum(len(x) for x in cur) + len(w) > max_len and len(cur) > 0:
            lines.append("".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append("".join(cur))
    return lines

def run():
    with open(RAW_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    segments = data['segments']
    subtitles = []
    
    for seg in segments:
        text = seg['text'].strip()
        cleaned = clean_text(text)
        if not cleaned:
            continue
            
        if len(cleaned) <= 16:
            subtitles.append((seg['start'], seg['end'], cleaned))
        else:
            parts = re.split(r'([ ？!！，,])', text)
            chunks = []
            cur_c = ""
            for p in parts:
                if p in [' ', '？', '!', '！', '，', ',']:
                    cur_c += p
                    if len(cur_c.strip()) >= 6:
                        chunks.append(cur_c.strip())
                        cur_c = ""
                else:
                    cur_c += p
            if cur_c.strip():
                chunks.append(cur_c.strip())
                
            refined_chunks = []
            for c in chunks:
                c_clean = clean_text(c)
                if len(c_clean) > 16:
                    sub_lines = split_long_text_by_jieba(c_clean, max_len=14)
                    refined_chunks.extend(sub_lines)
                else:
                    refined_chunks.append(c_clean)
                    
            total_len = sum(len(c) for c in refined_chunks)
            dur = seg['end'] - seg['start']
            cur_st = seg['start']
            for c in refined_chunks:
                c_clean = clean_text(c)
                if not c_clean:
                    continue
                c_dur = dur * (len(c_clean) / total_len)
                cur_et = cur_st + c_dur
                subtitles.append((cur_st, cur_et, c_clean))
                cur_st = cur_et
                
    # 平滑合併短行 (< 6 字)
    merged = []
    i = 0
    while i < len(subtitles):
        st, et, txt = subtitles[i]
        if i < len(subtitles) - 1:
            nst, net, ntxt = subtitles[i+1]
            pause = nst - et
            # 如果目前行很短且合併後 <= 16 字
            if len(txt) <= 5 and pause < 0.35 and (len(txt) + len(ntxt) <= 16):
                txt = txt + " " + ntxt
                et = net
                i += 1
            # 或者下行很短且合併後 <= 16 字
            elif len(ntxt) <= 5 and pause < 0.35 and (len(txt) + len(ntxt) <= 16):
                txt = txt + " " + ntxt
                et = net
                i += 1
        merged.append((st, et, clean_text(txt)))
        i += 1
        
    with open(OUT_SRT, 'w', encoding='utf-8') as f:
        for idx, (st, et, txt) in enumerate(merged, 1):
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(st)} --> {format_timestamp(et)}\n")
            f.write(f"{txt}\n\n")
            
    lengths = [len(txt) for _, _, txt in merged]
    print(f"🎉 說明短片影視級字幕生成完成！")
    print(f"📄 輸出檔案：{OUT_SRT.name}")
    print(f"📊 總字幕行數：{len(merged)} 行 (最短: {min(lengths)}, 平均: {sum(lengths)/len(lengths):.1f}, 最長: {max(lengths)} 字)")

if __name__ == "__main__":
    run()
