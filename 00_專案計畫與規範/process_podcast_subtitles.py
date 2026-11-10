# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第01章 播客深度對談 字幕自然語意與錯別字精修器
依據人類自然說話之語音節奏、呼吸停頓、對話輪替（Speaker Turns）與完整語詞進行自然斷句
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
RAW_JSON = CH01_DIR / "raw_segments_podcast.json"

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
    (r"大[笨奔分]坑文化[城層]?", "大坌坑文化層"),
    (r"大[笨奔分]坑", "大坌坑"),
    (r"成第1603年", "陳第1603年"),
    (r"沉地", "陳第"),
    (r"成第", "陳第"),
    (r"陳弟", "陳第"),
    (r"東方記", "東番記"),
    (r"東番記", "《東番記》"),
    (r"玉永河", "郁永河"),
    (r"喻永和", "郁永河"),
    (r"御永和", "郁永河"),
    (r"[碧疲]海[基紀記]由", "《裨海紀遊》"),
    (r"裨海紀遊", "《裨海紀遊》"),
    (r"《+《裨海紀遊》+》", "《裨海紀遊》"),
    (r"《+《東番記》+》", "《東番記》"),
    (r"伊能[家嘉][局鋸記]", "伊能嘉矩"),
    (r"臺灣踏[茶查]日記", "《臺灣踏查日記》"),
    (r"《+《臺灣踏查日記》+》", "《臺灣踏查日記》"),
    (r"佐山[勇融]吉", "佐山融吉"),
    (r"[番蕃]族調查報告書", "《蕃族調查報告書》"),
    (r"碑南遺址", "卑南遺址"),

    # 族群與社會制度
    (r"南島[羽語]族", "南島語族"),
    (r"南島[鮮民]民", "南島先民"),
    (r"鮮民", "先民"),
    (r"鮮明", "先民"),
    (r"先代歷史", "現代歷史"),
    (r"排班族", "排灣族"),
    (r"臺灣族人", "排灣族人"),
    (r"盧凱族", "魯凱族"),
    (r"太牙[魚語]", "泰雅語"),
    (r"雙[忍人]連杯", "雙人連杯"),
    (r"雙人聯杯", "雙人連杯"),
    (r"兼併兼", "肩並肩"),
    (r"立法中樞", "曆法中樞"),
    (r"歲時祭儀", "歲時祭儀"),
    (r"碎石技[藝儀]", "歲時祭儀"),
    (r"一[碎穗]一[碎穗][的地]?", "一穗一穗地"),
    (r"神聖碎拔", "神聖穗拔"),
    (r"小米林", "小米靈"),
    (r"依次割碗", "一次割完"),
    (r"還沒成熟的碎", "還沒成熟的穗"),
    (r"社會契約的[地締]結", "社會契約的締結"),
    (r"Pajakala", "Patjara"),
    (r"Pajara", "Patjara"),
    (r"巴哈拉", "Patjara"),
    (r"生命規定", "嚴格規定"),
    (r"嚴固的史前環境", "嚴酷的史前環境"),
    (r"肢體同步[律率]", "肢體同步率"),
    (r"一體成心", "一體成形"),
    (r"柔和交織", "揉和交織"),
    (r"[一遺][望忘]神聖的小米酒", "一碗神聖的小米酒"),
    (r"延冬", "嚴冬"),
    (r"新時期時代", "新石器時代"),
    (r"刻板影響", "刻板印象"),
    (r"定居巨多", "定居聚落"),
    (r"部落影史", "部落飲食"),
    (r"從靈", "叢林"),

    # 食材、農業與植物學
    (r"Lavue", "Lavu"),
    (r"中不火", "種不活"),
    (r"A RANG", "Arang"),
    (r"a rang", "Arang"),
    (r"以速為重", "以粟為重"),
    (r"葉鹽碎石潑地上", "頁岩碎石坡地上"),
    (r"鹽縫裡面", "岩縫裡面"),
    (r"微枯其微", "微乎其微"),
    (r"吉拿[腹富]", "吉拿富"),
    (r"西那富", "吉拿富"),
    (r"[甲假]酸[薑漿]葉?", "假酸漿葉"),
    (r"假酸漿葉?液黏質", "假酸漿葉黏質"),
    (r"假酸漿葉液", "假酸漿葉"),
    (r"假酸漿液", "假酸漿葉"),
    (r"粘[值質]", "黏質"),
    (r"多醣粘[值質]", "多醣黏質"),
    (r"高溫吹蒸", "高溫炊蒸"),
    (r"天然味藥保膜", "天然胃藥保護膜"),
    (r"天然胃藥保膜", "天然胃藥保護膜"),
    (r"神農常百草", "神農嘗百草"),
    (r"林園灌木叢", "林緣灌木叢"),
    (r"紫草[殼科]的植物", "紫草科的植物"),
    (r"野生大山[竹豬]", "野生大山豬"),
    (r"大山竹", "大山豬"),
    (r"生豬肉", "山豬肉"),
    (r"新山味", "腥羶味"),
    (r"馬告珊瑚礁", "馬告山胡椒"),
    (r"珊瑚礁", "山胡椒"),
    (r"刺[蟲蔥]", "刺蔥"),
    (r"食[茱朱]萸", "食茱萸"),
    (r"鳥不[踏踏]", "鳥不踏"),
    (r"土[肉月]桂", "土肉桂"),
    (r"香[絲斯]木", "相思木"),
    (r"香[絲斯]樹", "相思樹"),
    (r"九[雄芎]木?", "九芎木"),
    (r"常味道", "腸胃道"),
    (r"味醬器", "胃脹氣"),
    (r"胃醬器", "胃脹氣"),
    (r"石[板版]屋", "石板屋"),
    (r"石[板版]烤肉", "石板烤肉"),
    (r"自米板鹽", "緻密板岩"),
    (r"鎖住肉質", "鎖住肉汁"),
    (r"天然酥肥雞煎鑄鐵鍋", "天然舒肥機兼鑄鐵鍋"),
    (r"火[堂燙糖腸]", "火塘"),
    (r"冷[燻熏]", "冷燻"),
    (r"煙[燻熏]", "煙燻"),
    (r"架上冷燻", "架上冷燻"),
    (r"渣[濫朗]", "Djalan"),
    (r"懸於土上", "懸於火上"),
    (r"雞酒至黑", "積久至黑"),
    (r"薄樹", "柏樹"),
    (r"多指木材", "多脂木材"),
    (r"蔓火", "慢火"),
    (r"蔓燻", "慢燻"),
    (r"[玉愈癒]創木[粉酚芬]", "癒創木酚"),
    (r"甲[粉酚]", "甲酚"),
    (r"檸檬[泉醛]", "檸檬醛"),
    (r"檸檬[稀烯]", "檸檬烯"),
    (r"異具防腐劑", "抑菌防腐劑"),
    (r"屈寒", "袪寒"),
    (r"點肉穿上", "給肉穿上"),
    (r"天然酒[渠麴]", "天然酒麴"),
    (r"酒[麴渠]", "酒麴"),
    (r"大葉甜香草", "大葉田香草"),
    (r"口[嚼嚼]酒", "口嚼酒"),
    (r"雅熱帶", "亞熱帶"),
    (r"在豪邁[地的]", "再豪邁地"),
    (r"舒舒服服的", "舒舒服服地"),
    (r"深深不息[的地]?", "生生不息地"),
    (r"靜靜的等待", "靜靜地等待"),
    (r"買彩卷", "買彩券"),
    (r"你常常看", "你想想看"),
    (r"獵人確保的部落", "獵人確保了部落"),
    (r"這要上說", "資料上說"),
    (r"痾，鐵類揮發油", "萜類揮發油"),
    (r"鐵類揮發油", "萜類揮發油"),
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
    if not RAW_JSON.exists():
        print(f"等待轉錄完成... 找不到 {RAW_JSON.name}")
        return

    with open(RAW_JSON, "r", encoding="utf-8") as f:
        segments = json.load(f)

    print(f"Total raw segments: {len(segments)}")

    subtitles = []
    i = 0
    while i < len(segments):
        cur = segments[i]
        c_text = correct_text(cur["text"])
        c_start = cur["start"]
        c_end = cur["end"]

        # 整理當前文字
        c_text = c_text.replace("?", "？").replace("!", "！").replace(",", "，")
        c_text = re.sub(r'，{2,}', '，', c_text)
        c_text = re.sub(r'^[，、。；]\s*', '', c_text)
        c_text = re.sub(r'[，、；]\s*$', '', c_text)

        # 嘗試與下一 segment 合併（依據說話呼吸與語意單元）
        if i < len(segments) - 1:
            nxt = segments[i + 1]
            n_text = correct_text(nxt["text"])
            pause = nxt["start"] - c_end
            comb_text = c_text + n_text

            clean_comb = re.sub(r'[^\w\u4e00-\u9fa5]', '', comb_text)
            clean_cur = re.sub(r'[^\w\u4e00-\u9fa5]', '', c_text)
            clean_nxt = re.sub(r'[^\w\u4e00-\u9fa5]', '', n_text)

            # 對話輪替標記：若下一句是獨立發語詞（對、嗯、哇、沒錯、真的），且 pause > 0.3s，不跨輪替合併
            is_turn_token = any(clean_nxt.startswith(w) for w in ["對", "嗯", "哇", "沒錯", "真的", "確實", "好的", "不過"])
            has_strong_punct = any(p in c_text for p in ['？', '?', '！', '!'])

            # 合併條件：
            # 1. 不是不同說話者輪替
            # 2. 當前句子太短（< 7 字），停頓小（< 0.5s），合併後 <= 22 字
            # 3. 或兩句極度緊密（pause < 0.2s），合併後 <= 18 字
            if not is_turn_token and not has_strong_punct:
                if (len(clean_cur) < 7 and pause < 0.5 and len(clean_comb) <= 22) or \
                   (len(clean_comb) <= 18 and pause < 0.2):
                    c_text = c_text + "，" + n_text if not any(c_text.endswith(p) for p in ['，', '。', '？', '！', '、']) else c_text + n_text
                    c_end = nxt["end"]
                    i += 1  # 消耗下一句

        # 處理結尾多餘標點
        c_text = re.sub(r'[，、；]\s*$', '', c_text)
        c_text = correct_text(c_text)

        # 如果文字不為空則加入
        if len(re.sub(r'[^\w\u4e00-\u9fa5]', '', c_text)) > 0:
            subtitles.append((c_start, c_end, c_text))
        i += 1

    out_srt = CH01_DIR / "第01章_粟米野豬與香料火種_雙人對談.srt"
    with open(out_srt, "w", encoding="utf-8") as f:
        for idx, (st, et, txt) in enumerate(subtitles, start=1):
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(st)} --> {format_timestamp(et)}\n")
            f.write(f"{txt}\n\n")

    lengths = [len(re.sub(r'[^\w\u4e00-\u9fa5]', '', txt)) for _, _, txt in subtitles]
    print(f"✅ 完成播客對談字幕生成：{out_srt.name}")
    print(f"📊 總字幕行數：{len(subtitles)} 行 (最短: {min(lengths)}, 平均: {sum(lengths)/len(lengths):.1f}, 最長: {max(lengths)} 字)")

    print("\n--- 前 25 行字幕預覽 ---")
    for idx, (st, et, txt) in enumerate(subtitles[:25], start=1):
        print(f"{idx:02d} [{format_timestamp(st)} --> {format_timestamp(et)}] {txt}")

if __name__ == "__main__":
    main()
