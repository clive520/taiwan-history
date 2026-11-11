# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 02 章 說明影片 語音轉錄與影視級自然語意 SRT 生成腳本
主題：大航海的蔗香與鹿皮——荷西東印度公司、糖業拓墾與熱帶果物登陸
規範：遵循《影視級字幕製作標準作業程序_SOP.md》
- 說明短片特化斷句策略：單行 8~16 字（平均 12~14 字），自然意群，轉折詞換行
- 0 錯字破句、臺/臺灣標準繁體
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

COMMON_CORRECTIONS = [
    (r"蜻蜓", "清廷"),
    (r"清景", "清廷"),
    (r"輕艇", "清廷"),
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
]

FOOD_CH02_CORRECTIONS = COMMON_CORRECTIONS + [
    # 地名與堡壘
    (r"熱蘭[遮折]城", "熱蘭遮城"),
    (r"普羅[民明]遮", "普羅民遮"),
    (r"赤[崁崁嵌]樓?", "赤崁"),
    (r"大[員圓園]", "大員"),
    (r"臺江內海", "臺江內海"),
    (r"長[崎奇]出島", "長崎出島"),

    # 歷史人物與典籍
    (r"甘治[士仕]", "甘治士"),
    (r"揆[一一]", "揆一"),
    (r"尤羅[伯白]", "尤羅伯"),
    (r"被[遺遺]誤的臺灣", "《被遺誤的臺灣》"),
    (r"臺灣[略記]記", "《臺灣略記》"),
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
    (r"鹿[皮披]", "鹿皮"),
    (r"鹿[肉月]乾", "鹿肉乾"),
    (r"陣羽[織芝]", "陣羽織"),
    (r"大[鎧凱]", "大鎧"),

    # 糖業與設備
    (r"糖[廍部廓]", "糖廍"),
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
    for pat, rep in FOOD_CH02_CORRECTIONS:
        t = re.sub(pat, rep, t)
    t = re.sub(r'[，。！？、；：\s]+$', '', t)
    t = re.sub(r'^[，。！？、；：\s]+', '', t)
    t = t.replace('”', '').replace('"', '').replace("'", '').replace('（', '')
    t = t.replace('）', '').replace('(', '').replace(')', '').replace('—', '')
    t = t.replace('…', '').replace('～', '').replace('~', '')
    return t

def split_natural_sentences_explainer(words, min_chars=6, max_chars=18, max_pause=0.55):
    """
    說明片特化：字數較緊湊（6~18字，平均12~14字），語意清晰
    """
    subtitles = []
    cur_words = []
    
    for i, w in enumerate(words):
        cur_words.append(w)
        cur_text = clean_text("".join([x.word for x in cur_words]))
        
        need_split = False
        
        # 1. 停頓過長
        if i < len(words) - 1:
            pause = words[i+1].start - w.end
            if pause >= max_pause and len(cur_text) >= min_chars:
                need_split = True
        else:
            need_split = True
            
        # 2. 字數達到上限
        if len(cur_text) >= max_chars:
            need_split = True
            
        # 3. 原始文本含明確停頓標點
        if any(p in w.word for p in ['。', '！', '？', '；', '\n']) and len(cur_text) >= min_chars:
            need_split = True

        if need_split and len(cur_text) > 0:
            start_time = cur_words[0].start
            end_time = cur_words[-1].end
            if end_time <= start_time:
                end_time = start_time + 0.5
            subtitles.append((start_time, end_time, cur_text))
            cur_words = []
            
    if cur_words:
        cur_text = clean_text("".join([x.word for x in cur_words]))
        if len(cur_text) > 0:
            start_time = cur_words[0].start
            end_time = cur_words[-1].end
            if end_time <= start_time:
                end_time = start_time + 0.5
            subtitles.append((start_time, end_time, cur_text))
            
    return subtitles

def write_srt(subtitles, srt_path: Path):
    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, (st, et, txt) in enumerate(subtitles, start=1):
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(st)} --> {format_timestamp(et)}\n")
            f.write(f"{txt}\n\n")

def transcribe_and_make_srt(model, audio_path: Path, output_srt: Path, prompt_text=""):
    print(f"\n==================================================")
    print(f"🎙️ 正在處理說明影片音訊：{audio_path.name}")
    print(f"📦 檔案大小：{audio_path.stat().st_size / (1024*1024):.2f} MB")
    
    t0 = time.time()
    segments, info = model.transcribe(
        str(audio_path),
        language="zh",
        word_timestamps=True,
        initial_prompt=prompt_text,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=450)
    )
    
    all_words = []
    print("⏳ 正在轉錄語音片段...")
    for seg in segments:
        if seg.words:
            all_words.extend(seg.words)
            
    print(f"✅ 轉錄完成！共獲取 {len(all_words)} 個詞彙標籤，耗時 {time.time()-t0:.1f} 秒")
    
    # 說明片自然語意斷句
    subs = split_natural_sentences_explainer(all_words, min_chars=6, max_chars=18, max_pause=0.55)
    write_srt(subs, output_srt)
    
    lengths = [len(txt) for _, _, txt in subs]
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    print(f"📄 已生成廣播級字幕：{output_srt.name}")
    print(f"📊 總字幕行數：{len(subs)} 行 (最短: {min(lengths) if lengths else 0}, 平均: {avg_len:.1f}, 最長: {max(lengths) if lengths else 0} 字)")
    print("==================================================\n")

if __name__ == "__main__":
    prompt = (
        "熱蘭遮城, 普羅民遮, 大員, 臺江內海, 荷蘭東印度公司, VOC, 甘治士, 揆一, 尤羅伯, "
        "西拉雅族, 新港社, 蕭壠社, 麻豆社, 目加溜灣社, 贌社制度, 贌商, 王田制度, 水牛, "
        "臺灣梅花鹿, 鹿皮, 鹿肉乾, hertenvleesch, 陣羽織, 出島, 長崎, 糖廍, 糖車, 石磨, "
        "熟石灰, 澄清反應, 孔明鼎, 瓦溜, 淋泥法, 白糖, 赤砂糖, 烏糖, 糖蜜, 荷蘭豆, 檨仔, "
        "土芒果, 情人果, 蓮霧, 番荔枝, 釋迦, 番石榴, 芭樂, 番茄, 柑仔蜜, 番椒, 臺南甜, 哥倫布大交換"
    )
    
    print("🚀 初始化 Faster-Whisper (medium, int8, cpu_threads=8)...")
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)
    
    # 處理說明影片
    vid_file = CH02_DIR / "第02章_大航海的蔗香與鹿皮_說明影片.mp4"
    vid_srt = CH02_DIR / "第02章_大航海的蔗香與鹿皮_說明影片.srt"
    if vid_file.exists():
        transcribe_and_make_srt(model, vid_file, vid_srt, prompt)
    else:
        print(f"❌ 找不到影片檔案：{vid_file}")
