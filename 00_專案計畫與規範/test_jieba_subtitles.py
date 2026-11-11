# -*- coding: utf-8 -*-
import sys
import re
from pathlib import Path
import jieba

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
SRT_PATH = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味" / "第02章_大航海的蔗香與鹿皮_雙人對談.srt"

CUSTOM_WORDS = [
    "熱蘭遮城", "普羅民遮", "大員", "臺江內海", "荷蘭東印度公司", "VOC", "甘治士", "揆一", "尤羅伯",
    "西拉雅族", "新港社", "蕭壠社", "麻豆社", "目加溜灣社", "贌社制度", "贌商", "王田制度", "水牛",
    "臺灣梅花鹿", "梅花鹿", "生鹿皮", "鹿肉乾", "陣羽織", "長崎出島", "糖廍", "糖車", "石磨",
    "雙石磨", "熟石灰", "澄清反應", "五聯鼎", "孔明鼎", "瓦溜", "淋泥法", "白糖", "赤砂糖", "黑砂糖",
    "烏糖", "糖蜜", "荷蘭豆", "檨仔", "土芒果", "情人果", "蓮霧", "番荔枝", "釋迦", "番石榴", "芭樂",
    "柑仔蜜", "番椒", "哥倫布大交換", "臺南甜", "最高處", "壓製好", "終生難忘", "極端衝突", "赤崁平原",
    "1638年", "秋天", "畫面喔", "臺南安平"
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
    (r"生化工程", "生物化學工程"),
]

def clean_text(t: str) -> str:
    for pat, rep in CORRECTIONS:
        t = re.sub(pat, rep, t)
    return t

def format_timestamp(ms: int) -> str:
    hours = ms // 3600000
    rem = ms % 3600000
    minutes = rem // 60000
    rem = rem % 60000
    secs = rem // 1000
    ms_rem = rem % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms_rem:03d}"

def parse_timestamp(ts: str) -> int:
    h, m, s = ts.strip().split(":")
    sec, ms = s.split(",")
    return int(h) * 3600000 + int(m) * 60000 + int(sec) * 1000 + int(ms)

def run():
    content = SRT_PATH.read_text(encoding='utf-8')
    blocks = content.strip().split("\n\n")
    
    entries = []
    for b in blocks:
        lines = b.strip().split("\n")
        if len(lines) >= 3:
            time_match = re.match(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", lines[1])
            if time_match:
                st = parse_timestamp(time_match.group(1))
                et = parse_timestamp(time_match.group(2))
                text = "".join(lines[2:]).strip()
                entries.append({'start': st, 'end': et, 'text': text})
                
    # 逐條分詞重組
    # 每個 entry 進行 jieba 分詞
    all_tokens = []
    for entry in entries:
        txt = clean_text(entry['text'])
        # 去除首尾標點
        txt = re.sub(r'^[，。！？、；：\s]+', '', txt)
        txt = re.sub(r'[，。！？、；：\s]+$', '', txt)
        if not txt:
            continue
        words = list(jieba.cut(txt))
        dur = max(200, entry['end'] - entry['start'])
        ms_per_char = dur / max(1, len(txt))
        
        cur_pos = entry['start']
        for w in words:
            w_len = len(w)
            w_dur = int(w_len * ms_per_char)
            all_tokens.append({
                'word': w,
                'start': cur_pos,
                'end': cur_pos + w_dur
            })
            cur_pos += w_dur
            
    # 現在將 tokens 組裝成自然流暢的行（8~18字）
    subtitles = []
    cur_line = []
    
    STRONG_BREAKS = ["對", "沒錯", "哇", "嗯", "好", "好的", "其實", "也就是說", "但神奇的是", "但", "然而", "接著", "然後"]
    
    for i, tok in enumerate(all_tokens):
        w = tok['word']
        cur_line.append(tok)
        cur_text = "".join([t['word'] for t in cur_line])
        
        need_split = False
        
        if i < len(all_tokens) - 1:
            nxt = all_tokens[i+1]['word']
            # 停頓超過 400ms
            if all_tokens[i+1]['start'] - tok['end'] >= 400 and len(cur_text) >= 8:
                need_split = True
            # 下一個詞是強轉折或對話標記
            elif nxt in STRONG_BREAKS and len(cur_text) >= 8:
                need_split = True
            # 目前詞是標點
            elif any(p in w for p in ['。', '！', '？', '；']) and len(cur_text) >= 6:
                need_split = True
            elif any(p in w for p in ['，', '、']) and len(cur_text) >= 9:
                need_split = True
            # 總字數達到 14~18 字且下個詞不是標點
            elif len(cur_text) >= 14 and nxt not in ['，', '、', '。', '！', '？', '；']:
                need_split = True
        else:
            need_split = True
            
        if need_split:
            # 清理該行首尾標點
            line_str = "".join([t['word'] for t in cur_line]).strip()
            line_str = re.sub(r'^[，。！？、；：\s]+', '', line_str)
            line_str = re.sub(r'[，。！？、；：\s]+$', '', line_str)
            if line_str:
                st = cur_line[0]['start']
                et = cur_line[-1]['end']
                if et <= st:
                    et = st + 500
                subtitles.append((st, et, line_str))
            cur_line = []
            
    print(f"🎉 產出 {len(subtitles)} 條分詞意群字幕！前 15 條示範：")
    for idx, (st, et, txt) in enumerate(subtitles[:15], 1):
        print(f"[{format_timestamp(st)} -> {format_timestamp(et)}] ({len(txt)}字) {txt}")

if __name__ == "__main__":
    run()
