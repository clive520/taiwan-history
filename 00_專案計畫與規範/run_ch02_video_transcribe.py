# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 02 章 說明影片 語音轉錄與影視級自然語意 SRT 生成腳本
"""
import sys
import os
import json
import time
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

from faster_whisper import WhisperModel

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH02_DIR = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味"

PROMPT_TEXT = (
    "熱蘭遮城, 普羅民遮, 大員, 臺江內海, 荷蘭東印度公司, VOC, 甘治士, 揆一, 尤羅伯, "
    "西拉雅族, 新港社, 蕭壠社, 麻豆社, 目加溜灣社, 贌社制度, 贌商, 王田制度, 水牛, "
    "臺灣梅花鹿, 鹿皮, 鹿肉乾, hertenvleesch, 陣羽織, 出島, 長崎, 糖廍, 糖車, 石磨, "
    "熟石灰, 澄清反應, 孔明鼎, 瓦溜, 淋泥法, 白糖, 赤砂糖, 烏糖, 糖蜜, 荷蘭豆, 檨仔, "
    "土芒果, 情人果, 蓮霧, 番荔枝, 釋迦, 番石榴, 芭樂, 番茄, 柑仔蜜, 番椒, 臺南甜, 哥倫布大交換"
)

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

def format_timestamp(seconds: float) -> str:
    total_ms = int(round(seconds * 1000))
    hours = total_ms // 3600000
    rem = total_ms % 3600000
    minutes = rem // 60000
    rem = rem % 60000
    secs = rem // 1000
    ms = rem % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

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

def transcribe_video():
    vid_file = CH02_DIR / "第02章_大航海的蔗香與鹿皮_說明影片.mp4"
    json_file = CH02_DIR / "第02章_說明影片_raw_words.json"
    srt_file = CH02_DIR / "第02章_大航海的蔗香與鹿皮_說明影片.srt"
    
    print("🚀 初始化 Faster-Whisper (medium, int8, cpu_threads=8)...")
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)
    
    print(f"🎙️ 開始轉錄說明影片：{vid_file.name}")
    t0 = time.time()
    segments, info = model.transcribe(
        str(vid_file),
        language="zh",
        initial_prompt=PROMPT_TEXT,
        word_timestamps=True,
        beam_size=1,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=450)
    )
    
    words_data = []
    seg_list = []
    for seg in segments:
        seg_list.append({
            'start': seg.start,
            'end': seg.end,
            'text': seg.text
        })
        if seg.words:
            for w in seg.words:
                words_data.append({
                    'word': w.word,
                    'start': w.start,
                    'end': w.end
                })
                
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({'segments': seg_list, 'words': words_data}, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 轉錄完成！共獲取 {len(words_data)} 個詞彙標籤，耗時 {time.time()-t0:.1f} 秒")
    
    # 自然語意斷句（說明短片特化：8~16字，平均12~14字）
    subtitles = []
    cur_words = []
    
    for i, w in enumerate(words_data):
        cur_words.append(w)
        cur_text = clean_text("".join([x['word'] for x in cur_words]))
        
        need_split = False
        
        # 1. 停頓切分
        if i < len(words_data) - 1:
            pause = words_data[i+1]['start'] - w['end']
            if pause >= 0.5 and len(cur_text) >= 8:
                need_split = True
        else:
            need_split = True
            
        # 2. 標點切分
        if any(p in w['word'] for p in ['。', '！', '？', '；', '\n']) and len(cur_text) >= 6:
            need_split = True
        elif any(p in w['word'] for p in ['，', '、']) and len(cur_text) >= 10:
            need_split = True
            
        # 3. 長度上限（保護字詞完整）
        if len(cur_text) >= 16:
            need_split = True
            
        if need_split and len(cur_text) > 0:
            st = cur_words[0]['start']
            et = cur_words[-1]['end']
            if et <= st:
                et = st + 0.5
            subtitles.append((st, et, cur_text))
            cur_words = []
            
    if cur_words:
        cur_text = clean_text("".join([x['word'] for x in cur_words]))
        if len(cur_text) > 0:
            st = cur_words[0]['start']
            et = cur_words[-1]['end']
            if et <= st:
                et = st + 0.5
            subtitles.append((st, et, cur_text))
            
    with open(srt_file, 'w', encoding='utf-8') as f:
        for idx, (st, et, txt) in enumerate(subtitles, start=1):
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(st)} --> {format_timestamp(et)}\n")
            f.write(f"{txt}\n\n")
            
    lengths = [len(txt) for _, _, txt in subtitles]
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    print(f"📄 已生成廣播級字幕：{srt_file.name}")
    print(f"📊 總字幕行數：{len(subtitles)} 行 (最短: {min(lengths)}, 平均: {avg_len:.1f}, 最長: {max(lengths)} 字)")

if __name__ == "__main__":
    transcribe_video()
