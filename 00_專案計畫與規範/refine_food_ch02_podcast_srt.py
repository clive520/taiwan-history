# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 02 章 播客深度對談 影視級字幕自然斷句重構與精修器
依據影視級字幕 SOP：
1. 消除機械字數斷句，重構自然呼吸意群（8~18字/行）
2. 保護對話輪替（Speaker Turns）與問答起承轉合
3. 注入 50+ 大航海、荷治與風土專有名詞校正庫，0 錯字破句
"""
import sys
import os
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
SRT_PATH = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味" / "第02章_大航海的蔗香與鹿皮_雙人對談.srt"

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

def clean_text(text: str) -> str:
    t = text.strip()
    for pat, rep in CORRECTIONS:
        t = re.sub(pat, rep, t)
    t = re.sub(r'[，。！？、；：\s]+$', '', t)
    t = re.sub(r'^[，。！？、；：\s]+', '', t)
    t = t.replace('”', '').replace('"', '').replace("'", '').replace('（', '')
    t = t.replace('）', '').replace('(', '').replace(')', '').replace('—', '')
    t = t.replace('…', '').replace('～', '').replace('~', '')
    return t

def refine_srt(input_path: Path):
    content = input_path.read_text(encoding='utf-8')
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
                
    print(f"📖 讀入原始字幕區塊數：{len(entries)}")
    
    # 建立連續音訊流，並在自然語意邊界切分
    # 策略：
    # 1. 串接相鄰區塊，若相鄰區塊停頓 > 600ms 或含句末標點（。！？），視為語意句中斷
    # 2. 將長句依標點、語氣助詞、轉折詞（8~18字）切分為廣播級字幕行
    
    # 首先將文字與時間進行時間戳平滑對齊
    # 每個原始區塊提供時間錨點
    char_timeline = []
    for entry in entries:
        txt = entry['text']
        cleaned = clean_text(txt)
        if not cleaned:
            continue
        duration = max(100, entry['end'] - entry['start'])
        ms_per_char = duration / len(cleaned)
        for idx, char in enumerate(cleaned):
            c_start = int(entry['start'] + idx * ms_per_char)
            c_end = int(entry['start'] + (idx + 1) * ms_per_char)
            char_timeline.append({
                'char': char,
                'start': c_start,
                'end': c_end
            })
            
    # 現在將字元組裝成意群
    # 轉折與語助詞清單
    BREAK_MARKERS = [
        "沒錯", "對", "嗯", "哇", "好的", "好", "其實", "也就是說", "這表示什麼", 
        "但神奇的是", "但是", "然而", "接著", "然後", "所以", "因為", "你知道",
        "如果你", "我們", "一邊是", "另外一邊", "聽起來", "說到", "那不然是"
    ]
    
    subtitles = []
    cur_chars = []
    
    i = 0
    while i < len(char_timeline):
        cur_chars.append(char_timeline[i])
        cur_text = "".join([c['char'] for c in cur_chars])
        
        need_split = False
        
        # 檢查下一個字元/詞彙是否是強中斷點
        if i < len(char_timeline) - 1:
            pause = char_timeline[i+1]['start'] - char_timeline[i]['end']
            
            # 停頓超過 500ms 且目前字數 >= 7
            if pause >= 500 and len(cur_text) >= 7:
                need_split = True
                
            # 標點符號後切分
            if char_timeline[i]['char'] in ['。', '！', '？', '；']:
                need_split = True
            elif char_timeline[i]['char'] in ['，', '、'] and len(cur_text) >= 9:
                need_split = True
                
            # 檢查後續文字是否開頭為轉折詞
            remaining_text = "".join([c['char'] for c in char_timeline[i+1:i+8]])
            for bm in BREAK_MARKERS:
                if remaining_text.startswith(bm) and len(cur_text) >= 8:
                    need_split = True
                    break
        else:
            need_split = True
            
        # 字數超過 18 字強制尋找最近的標點或自然點切分
        if len(cur_text) >= 18:
            need_split = True
            
        if need_split:
            final_text = clean_text("".join([c['char'] for c in cur_chars]))
            if len(final_text) > 0:
                st = cur_chars[0]['start']
                et = cur_chars[-1]['end']
                if et <= st:
                    et = st + 500
                subtitles.append((st, et, final_text))
            cur_chars = []
            
        i += 1
        
    if cur_chars:
        final_text = clean_text("".join([c['char'] for c in cur_chars]))
        if len(final_text) > 0:
            st = cur_chars[0]['start']
            et = cur_chars[-1]['end']
            if et <= st:
                et = st + 500
            subtitles.append((st, et, final_text))
            
    # 二次合併：若有行字數過短 (< 6 字) 且與下行間隔很小 (< 250ms)，進行流暢合併
    merged_subtitles = []
    idx = 0
    while idx < len(subtitles):
        st, et, txt = subtitles[idx]
        if idx < len(subtitles) - 1:
            nst, net, ntxt = subtitles[idx + 1]
            pause = nst - et
            if len(txt) <= 5 and pause < 300 and (len(txt) + len(ntxt) <= 18):
                # 合併
                txt = txt + "，" + ntxt if not any(txt.endswith(p) for p in ['，', '。', '！', '？']) else txt + ntxt
                et = net
                idx += 1
        merged_subtitles.append((st, et, clean_text(txt)))
        idx += 1
        
    # 寫回 SRT
    with open(input_path, 'w', encoding='utf-8') as f:
        for num, (st, et, txt) in enumerate(merged_subtitles, start=1):
            f.write(f"{num}\n")
            f.write(f"{format_timestamp(st)} --> {format_timestamp(et)}\n")
            f.write(f"{txt}\n\n")
            
    lengths = [len(txt) for _, _, txt in merged_subtitles]
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    print(f"🎉 播客字幕精修重構完畢！")
    print(f"📄 產出檔案：{input_path.name}")
    print(f"📊 總字幕行數：{len(merged_subtitles)} 行 (最短: {min(lengths)}, 平均: {avg_len:.1f}, 最長: {max(lengths)} 字)")

if __name__ == "__main__":
    refine_srt(SRT_PATH)
