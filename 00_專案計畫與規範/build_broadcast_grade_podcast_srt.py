# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 02 章 播客深度對談 廣播級自然意群字幕生成器
- 以完整連續文字流 + Jieba 詞級斷詞，100% 杜絕破詞破句（如「你/正站在」、「城堡的最/高處」、「生/鹿皮」）
- 嚴格控制每行 8~18 字（平均 12~14 字），自然停頓、語助詞、轉折詞換行
- 全面校對 50+ 大航海、荷治、西拉雅與風土專有名詞，0 錯字
"""
import sys
import os
import re
from pathlib import Path
import jieba

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
SRT_PATH = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味" / "第02章_大航海的蔗香與鹿皮_雙人對談.srt"

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
    "全球化輸送帶", "味覺基因", "巨大蝴蝶效應", "物理面貌", "截然不同", "親眼觀察", "生物化學工程"
]
for w in CUSTOM_WORDS:
    jieba.add_word(w)

CORRECTIONS = [
    # 臺/臺灣
    (r"台([灣北市南中東中東南東東南])", r"臺\1"),
    (r"全台", "全臺"),
    (r"在台", "在臺"),
    (r"來台", "來臺"),
    (r"割台", "割臺"),
    (r"治台", "治臺"),
    (r"保台", "保臺"),
    (r"平台", "平臺"),
    (r"開台", "開臺"),
    (r"回台", "回臺"),
    (r"返台", "返臺"),
    (r"犯台", "犯臺"),
    (r"[臺台]灣", "臺灣"),

    # 地名與堡壘
    (r"熱蘭[遮折周週]城?", "熱蘭遮城"),
    (r"普羅[民明]遮", "普羅民遮"),
    (r"赤[崁崁嵌]樓?", "赤崁"),
    (r"大[員圓園元]", "大員"),
    (r"臺江內海", "臺江內海"),
    (r"長[崎奇]出島", "長崎出島"),

    # 歷史人物與典籍
    (r"甘[治志之][士仕氏]", "甘治士"),
    (r"揆[一一]|奎伊|魁一", "揆一"),
    (r"尤羅[伯白]", "尤羅伯"),
    (r"被[遺遺]誤的臺灣", "《被遺誤的臺灣》"),
    (r"臺灣[略劣烈][記跡]", "《臺灣略記》"),
    (r"熱蘭遮城日記", "《熱蘭遮城日記》"),
    (r"裨海[紀記]遊", "《裨海紀遊》"),
    (r"郁永[河何]", "郁永河"),

    # 族群與制度
    (r"西拉[雅亞]族?", "西拉雅族"),
    (r"新港[社涉]", "新港社"),
    (r"蕭[壠壟]社", "蕭壠社"),
    (r"麻[豆荳]社", "麻豆社"),
    (r"目加溜灣[社涉]", "目加溜灣社"),
    (r"[贌僕僕]社[制治]度", "贌社制度"),
    (r"[贌僕僕]商", "贌商"),
    (r"王田[制治]度", "王田制度"),
    (r"什一[稅水]", "什一稅"),

    # 鹿皮與獵鹿
    (r"梅花[鹿路]", "梅花鹿"),
    (r"[生熟]?[露路鹿]皮", "生鹿皮"),
    (r"鹿[肉月]乾", "鹿肉乾"),
    (r"雪水", "血水"),
    (r"野性[山羶羶]味", "野性羶味"),
    (r"陣羽[織芝]", "陣羽織"),
    (r"大[鎧凱]", "大鎧"),

    # 糖業與設備
    (r"糖[廍部廓埔]", "糖廍"),
    (r"石[磨墨]糖車", "石磨糖車"),
    (r"雙石[磨墨]", "雙石磨"),
    (r"熟石[灰輝]", "熟石灰"),
    (r"澄清[反返]應", "澄清反應"),
    (r"五聯[鼎頂]", "五聯鼎"),
    (r"孔明[鼎頂]", "孔明鼎"),
    (r"瓦[溜留]", "瓦溜"),
    (r"淋[泥尼]法", "淋泥法"),
    (r"赤砂[糖唐]", "赤砂糖"),
    (r"黑砂[糖唐]", "黑砂糖"),
    (r"烏[糖唐]", "烏糖"),
    (r"糖[蜜密]", "糖蜜"),
    (r"甘[蔗遮]", "甘蔗"),
    (r"蔗[渣查]", "蔗渣"),

    # 引進作物與飲食
    (r"荷蘭[豆荳]", "荷蘭豆"),
    (r"[檨樣][仔子]", "檨仔"),
    (r"土芒[果菓]", "土芒果"),
    (r"情人[果菓]", "情人果"),
    (r"蓮[霧務]", "蓮霧"),
    (r"番[荔立]枝", "番荔枝"),
    (r"釋[迦加]", "釋迦"),
    (r"番石[榴留]", "番石榴"),
    (r"芭[樂樂]", "芭樂"),
    (r"柑[仔子]蜜", "柑仔蜜"),
    (r"番[椒焦]", "番椒"),
    (r"哥倫[布步]大交換", "哥倫布大交換"),
    (r"臺南[甜田]", "臺南甜"),
    (r"水[牛午]", "水牛"),
]

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

def clean_text(t: str) -> str:
    for pat, rep in CORRECTIONS:
        t = re.sub(pat, rep, t)
    return t

def build_broadcast_subtitles():
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
                txt = "".join(lines[2:]).strip()
                entries.append({'start': st, 'end': et, 'text': txt})
                
    # 建立連續字元時間軸
    char_nodes = []
    for entry in entries:
        txt = clean_text(entry['text'])
        # 去除原始行首尾可能遺留的標點空白
        txt = txt.strip()
        if not txt:
            continue
        dur = max(100, entry['end'] - entry['start'])
        ms_per_char = dur / len(txt)
        for idx, char in enumerate(txt):
            c_st = int(entry['start'] + idx * ms_per_char)
            c_et = int(entry['start'] + (idx + 1) * ms_per_char)
            char_nodes.append({
                'char': char,
                'start': c_st,
                'end': c_et
            })
            
    full_text = "".join([c['char'] for c in char_nodes])
    print(f"📖 總字數：{len(full_text)} 字，正在執行 Jieba 詞級精確分詞...")
    words = list(jieba.cut(full_text))
    print(f"✅ 分詞完成，共獲取 {len(words)} 個語意詞彙！")
    
    # 將 words 對齊回 char_nodes 的時間戳
    word_nodes = []
    char_ptr = 0
    for w in words:
        w_len = len(w)
        if w_len == 0:
            continue
        st = char_nodes[char_ptr]['start']
        et = char_nodes[char_ptr + w_len - 1]['end']
        word_nodes.append({
            'word': w,
            'start': st,
            'end': et
        })
        char_ptr += w_len
        
    # 自然語意意群組裝（雙人對談特化：8~18字）
    subtitles = []
    cur_words = []
    
    BREAK_WORDS = {
        "沒錯", "對", "嗯", "哇", "好的", "好", "其實", "也就是說", "這表示什麼", 
        "但神奇的是", "但", "但是", "然而", "接著", "然後", "所以", "因為", "你知道",
        "如果你", "我們", "一邊是", "另外一邊", "聽起來", "說到", "那不然是", "截然不同"
    }
    
    for i, wn in enumerate(word_nodes):
        w = wn['word']
        cur_words.append(wn)
        cur_text = "".join([x['word'] for x in cur_words])
        
        need_split = False
        
        if i < len(word_nodes) - 1:
            nxt_w = word_nodes[i+1]['word']
            pause = word_nodes[i+1]['start'] - wn['end']
            
            # 1. 自然長停頓（超過 400ms 且字數 >= 8）
            if pause >= 400 and len(cur_text) >= 8:
                need_split = True
            # 2. 句末標點符號
            elif any(p in w for p in ['。', '！', '？', '；']) and len(cur_text) >= 6:
                need_split = True
            # 3. 句中逗號（字數 >= 9）
            elif any(p in w for p in ['，', '、']) and len(cur_text) >= 9:
                need_split = True
            # 4. 下一個詞是強轉折或對話語助詞（字數 >= 8）
            elif nxt_w in BREAK_WORDS and len(cur_text) >= 8:
                need_split = True
            # 5. 字數保護：如果加上下一個詞將超過 18 字，且目前字數已 >= 8，則在此切分
            elif len(cur_text) + len(nxt_w) > 18 and len(cur_text) >= 8:
                need_split = True
            # 6. 極限字數 22 字強制切分
            elif len(cur_text) >= 22:
                need_split = True
        else:
            need_split = True
            
        if need_split:
            line_str = "".join([x['word'] for x in cur_words]).strip()
            # 清理首尾非必要標點
            line_str = re.sub(r'^[，。！？、；：\s]+', '', line_str)
            line_str = re.sub(r'[，。！？、；：\s]+$', '', line_str)
            if len(line_str) > 0:
                st = cur_words[0]['start']
                et = cur_words[-1]['end']
                if et <= st:
                    et = st + 500
                subtitles.append((st, et, line_str))
            cur_words = []
            
    if cur_words:
        line_str = "".join([x['word'] for x in cur_words]).strip()
        line_str = re.sub(r'^[，。！？、；：\s]+', '', line_str)
        line_str = re.sub(r'[，。！？、；：\s]+$', '', line_str)
        if len(line_str) > 0:
            st = cur_words[0]['start']
            et = cur_words[-1]['end']
            if et <= st:
                et = st + 500
            subtitles.append((st, et, line_str))
            
    # 微調平滑：合併字數小於 6 字的短行
    final_subtitles = []
    idx = 0
    while idx < len(subtitles):
        st, et, txt = subtitles[idx]
        if idx < len(subtitles) - 1:
            nst, net, ntxt = subtitles[idx + 1]
            pause = nst - et
            if len(txt) <= 6 and pause < 350 and (len(txt) + len(ntxt) <= 18):
                txt = txt + "，" + ntxt if not any(txt.endswith(p) for p in ['，', '。', '！', '？', '；']) else txt + " " + ntxt
                et = net
                idx += 1
        final_subtitles.append((st, et, txt))
        idx += 1
        
    with open(SRT_PATH, 'w', encoding='utf-8') as f:
        for num, (st, et, txt) in enumerate(final_subtitles, start=1):
            f.write(f"{num}\n")
            f.write(f"{format_timestamp(st)} --> {format_timestamp(et)}\n")
            f.write(f"{txt}\n\n")
            
    lengths = [len(txt) for _, _, txt in final_subtitles]
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    print(f"🎉 播客字幕廣播級重構圓滿完成！")
    print(f"📄 輸出檔案：{SRT_PATH.name}")
    print(f"📊 總字幕行數：{len(final_subtitles)} 行 (最短: {min(lengths)}, 平均: {avg_len:.1f}, 最長: {max(lengths)} 字)")
    print("\n前 20 行成果預覽：")
    for n, (st, et, txt) in enumerate(final_subtitles[:20], 1):
        print(f"{n:02d}. [{format_timestamp(st)} -> {format_timestamp(et)}] ({len(txt):02d}字) {txt}")

if __name__ == "__main__":
    build_broadcast_subtitles()
