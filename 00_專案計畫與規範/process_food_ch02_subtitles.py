# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 02 章《大航海的蔗香與鹿皮》影視級字幕製作與校對腳本
遵循影視級字幕 SOP：
1. 說明短片：單行 8~16 字（平均 12~14 字），自然意群，轉折詞換行
2. Podcast 對談：保護對話輪替（Speaker Turns），每行以單次呼吸語意群（8~18 字）為本，嚴禁機械截斷
3. 注入大航海、荷治與臺灣風土名詞庫，0 錯字破句
"""
import sys
import json
import re
import time
from pathlib import Path
from faster_whisper import WhisperModel

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

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
    (r"台灣", "臺灣"),

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

def correct_text(text: str) -> str:
    t = text.strip()
    for pat, rep in CORRECTIONS:
        t = re.sub(pat, rep, t)
    return t

def transcribe_and_dump_json(model, audio_path: Path, output_json: Path):
    print(f"🎙️ 正在轉錄音訊：{audio_path.name}")
    t0 = time.time()
    segments, info = model.transcribe(
        str(audio_path),
        language="zh",
        initial_prompt=PROMPT_TEXT,
        word_timestamps=True,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=450)
    )
    data = []
    for seg in segments:
        words_data = [{'word': w.word, 'start': w.start, 'end': w.end} for w in seg.words] if seg.words else []
        data.append({
            'start': seg.start,
            'end': seg.end,
            'text': seg.text,
            'words': words_data
        })
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 轉錄完成！共提取 {len(data)} 個片段，耗時 {time.time()-t0:.1f} 秒")
    return data

def process_segments_to_srt(segments: list, output_srt: Path, is_podcast: bool = False):
    subtitles = []
    i = 0
    while i < len(segments):
        cur = segments[i]
        c_text = correct_text(cur["text"])
        c_start = cur["start"]
        c_end = cur["end"]

        c_text = c_text.replace("?", "？").replace("!", "！").replace(",", "，")
        c_text = re.sub(r'，{2,}', '，', c_text)
        c_text = re.sub(r'^[，、。；]\s*', '', c_text)
        c_text = re.sub(r'[，、；]\s*$', '', c_text)

        if i < len(segments) - 1:
            nxt = segments[i + 1]
            n_text = correct_text(nxt["text"])
            pause = nxt["start"] - c_end
            comb_text = c_text + n_text

            clean_comb = re.sub(r'[^\w\u4e00-\u9fa5]', '', comb_text)
            clean_cur = re.sub(r'[^\w\u4e00-\u9fa5]', '', c_text)
            clean_nxt = re.sub(r'[^\w\u4e00-\u9fa5]', '', n_text)

            is_transition = any(clean_nxt.startswith(w) for w in ["好", "接著", "然後", "也就是說", "這表示什麼", "對", "嗯", "哇", "沒錯", "真的"])
            has_strong_punct = any(p in c_text for p in ['？', '?', '！', '!', '。'])

            max_len = 20 if is_podcast else 18
            if not is_transition and not has_strong_punct:
                if (len(clean_cur) < 7 and pause < 0.5 and len(clean_comb) <= max_len) or \
                   (len(clean_comb) <= max_len and pause < 0.2):
                    c_text = c_text + "，" + n_text if not any(c_text.endswith(p) for p in ['，', '。', '？', '！', '、']) else c_text + n_text
                    c_end = nxt["end"]
                    i += 1

        c_text = re.sub(r'[，、；]\s*$', '', c_text)
        c_text = correct_text(c_text)

        if len(re.sub(r'[^\w\u4e00-\u9fa5]', '', c_text)) > 0:
            subtitles.append((c_start, c_end, c_text))
        i += 1

    with open(output_srt, "w", encoding="utf-8") as f:
        for idx, (st, et, txt) in enumerate(subtitles, start=1):
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(st)} --> {format_timestamp(et)}\n")
            f.write(f"{txt}\n\n")

    lengths = [len(re.sub(r'[^\w\u4e00-\u9fa5]', '', txt)) for _, _, txt in subtitles]
    print(f"📄 已生成標準字幕：{output_srt.name}")
    print(f"📊 總字幕行數：{len(subtitles)} 行 (最短: {min(lengths)}, 平均: {sum(lengths)/len(lengths):.1f}, 最長: {max(lengths)} 字)")

if __name__ == "__main__":
    print("🚀 字幕處理工具模組載入完成。")
