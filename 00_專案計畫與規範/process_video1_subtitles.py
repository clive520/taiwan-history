# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第01章 說明影片 字幕自然語意與錯別字精修器
"""
import sys
import json
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH01_DIR = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味"
RAW_JSON = CH01_DIR / "raw_segments_video1.json"

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

    # 歷史人物與典籍
    (r"大[笨分]坑", "大坌坑"),
    (r"沉地", "陳第"),
    (r"陳弟", "陳第"),
    (r"東方記", "東番記"),
    (r"玉永河", "郁永河"),
    (r"喻永和", "郁永河"),
    (r"御永和", "郁永河"),
    (r"[碧疲]海[基紀記]油", "裨海紀遊"),
    (r"裨海[記遊]", "裨海紀遊"),
    (r"伊能[家嘉][局鋸記]", "伊能嘉矩"),
    (r"佐山[勇融]吉", "佐山融吉"),
    (r"[番蕃]族調查報告書", "蕃族調查報告書"),

    # 文化與人類學專有名詞
    (r"南島[羽語]族", "南島語族"),
    (r"鮮明", "先民"),  # 語音誤辨
    (r"先代歷史", "現代歷史"),
    (r"立法中樞", "曆法中樞"),
    (r"碎石技[藝儀]", "歲時祭儀"),
    (r"台灣語叫做阿軟", "族語叫做 Arang"),
    (r"社會契約的[地締]結", "社會契約的締結"),
    (r"Pajakala", "Patjara"),
    (r"巴哈拉", "Patjara"),
    (r"肢體同步[律率]", "肢體同步率"),
    (r"柔和交織", "揉和交織"),
    (r"[一遺][望忘]神聖的小米酒", "一碗神聖的小米酒"),
    (r"雙人聯杯", "雙人連杯"),
    (r"兼併兼", "肩並肩"),
    (r"延冬", "嚴冬"),
    (r"新時期時代", "新石器時代"),
    (r"刻板影響", "刻板印象"),

    # 植物學、食材與化學
    (r"吉[拿納南]富", "吉拿富"),
    (r"西那富", "吉拿富"),
    (r"假[酸宣][薑漿]", "假酸漿"),
    (r"月[桃挑]", "月桃"),
    (r"馬[告告]", "馬告"),
    (r"麻[告告]", "馬告"),
    (r"刺[蔥聰]", "刺蔥"),
    (r"石珠魚", "食茱萸"),
    (r"食[茱朱]萸", "食茱萸"),
    (r"鳥不[踏踏]", "鳥不踏"),
    (r"土[肉月]桂", "土肉桂"),
    (r"香[絲斯]木", "相思木"),
    (r"香[絲斯]樹", "相思樹"),
    (r"九[芎弓]木?", "九芎木"),
    (r"常味道", "腸胃道"),
    (r"石[板版]屋", "石板屋"),
    (r"石[板版]烤肉", "石板烤肉"),
    (r"火[堂燙糖]", "火塘"),
    (r"冷[燻熏]", "冷燻"),
    (r"煙[燻熏]", "煙燻"),
    (r"渣朗", "Djalan"),
    (r"[玉愈癒]創木[粉酚]", "癒創木酚"),
    (r"甲[粉酚]", "甲酚"),
    (r"檸檬[泉醛]", "檸檬醛"),
    (r"檸檬[稀烯]", "檸檬烯"),
    (r"異具防腐劑", "抑菌防腐劑"),
    (r"屈寒", "袪寒"),
    (r"點肉穿上", "給肉穿上"),
    (r"天然酒[渠麴]", "天然酒麴"),
    (r"酒[麴渠]", "酒麴"),
    (r"口[嚼嚼]酒", "口嚼酒"),
    (r"雅熱帶", "亞熱帶"),
    (r"在豪邁[地的]", "再豪邁地"),
    (r"舒舒服服的", "舒舒服服地"),
    (r"豪邁的灑上", "豪邁地灑上"),
    (r"慢慢的燒", "慢慢地燒"),
    (r"精準的把", "精準地把"),
    (r"公平的分給", "公平地分給"),
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

def main():
    with open(RAW_JSON, "r", encoding="utf-8") as f:
        segments = json.load(f)

    print(f"Total raw segments: {len(segments)}")

    # 智慧語意合併：
    # 若當前 segment 與下一 segment 語意相連、未發生長停頓（停頓 < 0.4s），
    # 且兩者合計字數在 8 ~ 22 字之間，則自然合併為同一句；
    # 若單句已有足夠長度（>= 8 字），或結尾為強停頓（句號、問號、感嘆號），則獨立成行。
    subtitles = []
    i = 0
    while i < len(segments):
        cur = segments[i]
        c_text = correct_text(cur["text"])
        c_start = cur["start"]
        c_end = cur["end"]

        # 嘗試與下一個 segment 合併
        if i < len(segments) - 1:
            nxt = segments[i + 1]
            n_text = correct_text(nxt["text"])
            pause = nxt["start"] - c_end
            comb_text = c_text + n_text

            is_transition = any(nxt["text"].strip().startswith(w) for w in ["好", "接著", "然後", "也就是說", "這表示什麼", "講完前面"])
            has_strong_punct = any(p in c_text for p in ['？', '?', '！', '!', '。'])

            if not is_transition and not has_strong_punct:
                # 判斷是否適合合併：
                # 1. pause 很短 (< 0.4s)
                # 2. 合併後純中文字數 <= 22 字
                # 3. 當前句子長度過短 (< 8 字)，需要與後續結合才符合聽覺語詞
                clean_comb = re.sub(r'[^\w\u4e00-\u9fa5]', '', comb_text)
                clean_cur = re.sub(r'[^\w\u4e00-\u9fa5]', '', c_text)
                
                if (len(clean_cur) < 8 and pause < 0.5 and len(clean_comb) <= 22) or \
                   (len(clean_comb) <= 18 and pause < 0.25):
                    c_text = c_text + "，" + n_text if not any(c_text.endswith(p) for p in ['，', '。', '？', '！', '、']) else c_text + n_text
                    c_end = nxt["end"]
                    i += 1  # 消耗下一句

        # 整理標點
        c_text = c_text.replace("?", "？").replace("!", "！").replace(",", "，")
        c_text = re.sub(r'，{2,}', '，', c_text)
        c_text = re.sub(r'^[，、。；]\s*', '', c_text)
        c_text = re.sub(r'[，、；]\s*$', '', c_text)

        # 處理句尾殘留的獨立感嘆字（如「，哇」、「，好」移至下一句）
        for ex in ["哇", "好"]:
            if c_text.endswith(f"，{ex}") or c_text.endswith(f" {ex}"):
                c_text = c_text[:-2].rstrip("， ")
                if i < len(segments):
                    segments[i]["text"] = f"{ex}，" + segments[i]["text"].lstrip("，、 ")
        
        # 再次過濾錯字
        c_text = correct_text(c_text)
        subtitles.append((c_start, c_end, c_text))
        i += 1

    # 輸出到新 SRT
    out_srt = CH01_DIR / "第01章_粟米野豬與香料火種_說明影片.srt"
    with open(out_srt, "w", encoding="utf-8") as f:
        for idx, (st, et, txt) in enumerate(subtitles, start=1):
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(st)} --> {format_timestamp(et)}\n")
            f.write(f"{txt}\n\n")

    lengths = [len(re.sub(r'[^\w\u4e00-\u9fa5]', '', txt)) for _, _, txt in subtitles]
    print(f"✅ 完成說明影片字幕生成：{out_srt.name}")
    print(f"📊 總字幕行數：{len(subtitles)} 行 (最短: {min(lengths)}, 平均: {sum(lengths)/len(lengths):.1f}, 最長: {max(lengths)} 字)")

    # 顯示前 25 行供檢查
    print("\n--- 前 25 行字幕預覽 ---")
    for idx, (st, et, txt) in enumerate(subtitles[:25], start=1):
        print(f"{idx:02d} [{format_timestamp(st)} --> {format_timestamp(et)}] {txt}")

if __name__ == "__main__":
    main()
