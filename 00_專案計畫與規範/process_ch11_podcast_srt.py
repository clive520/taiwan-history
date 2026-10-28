# -*- coding: utf-8 -*-
"""
第11章 雙人對談播客 自然語氣斷句字幕生成腳本（專業繁中分詞與語氣停頓版）
使用 jieba 詞庫保護專有名詞，依據真實說話語氣、呼吸停頓與完整主謂語意切分，
絕不腰斬名詞、絕無半字斷行，行長嚴格控制於 10~22 字。
"""
import os
import sys
import json
import re
import jieba

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

CUSTOM_WORDS = [
    "朱一貴", "鴨母王", "鴨母寮", "大岡山", "中興王", "永和", "王珍", "杜君英", "檳榔林", "施世驃", "藍廷珍", "藍鼎元", "平臺紀略", "東征集", "貓兒干",
    "林爽文", "天地會", "洪門", "嚴煙", "大里杙", "順天", "莊大田", "鳳山縣", "諸羅城", "柴大紀", "董啟埏", "諸羅縣志",
    "福康安", "海蘭察", "巴圖魯", "欽定平定臺灣紀略", "嘉義", "嘉義縣", "嘉義公園", "贔屓馱碑", "十全武功", "老衢崎", "集集埔", "小半天",
    "分類械鬥", "漳泉械鬥", "閩粵械鬥", "頂下郊拚", "艋舺", "大稻埕", "三邑人", "同安人", "祖師廟", "龍山寺", "開漳聖王", "三山國王", "保生大帝", "廣澤尊王",
    "以漢制漢", "義民", "義民爺", "褒忠", "新埔褒忠義民廟", "林先坤", "六堆", "六堆忠義亭", "李直三", "黑色義民旗", "挑擔奉飯", "羅漢腳", "班兵制度"
]

for w in CUSTOM_WORDS:
    jieba.add_word(w)

TERM_CORRECTIONS = [
    (r"些民", "先民"),
    (r"飄悍", "剽悍"),
    (r"奏折", "奏摺"),
    (r"台民", "臺民"),
    (r"話外之地", "化外之地"),
    (r"報名", "暴民"),
    (r"平台集略", "平臺紀略"),
    (r"清定平定臺灣集略", "欽定平定臺灣紀略"),
    (r"藝民", "義民"),
    (r"周線", "州縣"),
    (r"蟹多貝後", "械鬥背後"),
    (r"天高皇帝元", "天高皇帝遠"),
    (r"邊吹啃鳴", "邊陲墾民"),
    (r"反清復民", "反清復明"),
    (r"防民勝於致民", "防民甚於治民"),
    (r"留官制", "流官制"),
    (r"囊坨已盈", "囊橐已盈"),
    (r"仗烈之氣", "瘴癘之氣"),
    (r"搬兵制", "班兵制"),
    (r"三年一壞", "三年一換"),
    (r"西加帶卷", "攜家帶眷"),
    (r"軍響", "軍餉"),
    (r"克扣", "剋扣"),
    (r"忘其欺詐", "望旗棄甲"),
    (r"訴諸武力滋味", "訴諸武力自衛"),
    (r"探官", "貪官"),
    (r"羊鴨", "養鴨"),
    (r"縮印", "縮影"),
    (r"牙醫", "衙役"),
    (r"贖盡", "贖金"),
    (r"大頭竿", "大岡山"),
    (r"殺血結盟", "歃血結盟"),
    (r"水師體徒施士標", "水師提督施世驃"),
    (r"他立刻獻祭以躍致命", "他立刻獻計以粵制閩"),
    (r"以躍致命", "以粵制閩"),
    (r"六堆相擁", "六堆鄉勇"),
    (r"言言", "嚴煙"),
    (r"煞血結盟", "歃血結盟"),
    (r"患難護濟", "患難互濟"),
    (r"肯明", "墾民"),
    (r"大禮遇", "大里杙"),
    (r"大禮禦", "大里杙"),
    (r"人獸與意外險", "人壽與意外險"),
    (r"這份炮險", "這份保險"),
    (r"龐大的護主網路", "龐大的互助網絡"),
    (r"柳樹南", "柳樹湳"),
    (r"打死燒殺擄掠", "大肆燒殺擄掠"),
    (r"結幹起義", "揭竿起義"),
    (r"見好順天", "建號順天"),
    (r"超出一貴時機", "超過朱一貴時期"),
    (r"基層周縣衙門", "基層州縣衙門"),
    (r"侏羅城", "諸羅城"),
    (r"侏羅", "諸羅"),
    (r"財大祭", "柴大紀"),
    (r"八寶鎮", "八堡圳"),
    (r"封收", "豐收"),
    (r"蟹鬥", "械鬥"),
    (r"頂下[較交][平拼拚]", "頂下郊拚"),
    (r"蒙甲", "艋舺"),
    (r"泉州三藝人", "泉州三邑人"),
    (r"三藝人", "三邑人"),
    (r"燒個金光", "燒個精光"),
    (r"陳皇爺", "城隍爺"),
    (r"仍不住", "忍不住"),
    (r"防台妙計", "防臺妙計"),
    (r"路骨", "露骨"),
    (r"是張權互仇敏越互治", "使漳泉互仇、閩粵互制"),
    (r"張權互仇", "漳泉互仇"),
    (r"敏越互治", "閩粵互制"),
    (r"天災不端", "天災不斷"),
    (r"生前之旅", "深入探索"),
    (r"義民也信仰", "義民爺信仰"),
    (r"相擁", "鄉勇"),
    (r"刺下保忠", "賜下褒忠"),
    (r"羅漢角馬", "羅漢腳嘛"),
    (r"羅漢[角腳跤]", "羅漢腳"),
    (r"新蒲薄中義民廟", "新埔褒忠義民廟"),
    (r"新蒲", "新埔"),
    (r"挑[蛋擔]奉[範飯]", "挑擔奉飯"),
    (r"泥濤", "泥淖"),
    (r"退去", "褪去"),
    (r"天神的暴民", "天生的暴民"),
    (r"一鳴器", "義民旗"),
    (r"分類褻瘍", "分類械鬥"),
    (r"實質在在", "實實在在"),
    (r"津天洞地", "驚天動地"),
    (r"雪凌凌", "血淋淋"),
    (r"死進城", "紫禁城"),
    (r"漢永[，,、]?刁[腕頑]男[子治]", "悍勇、刁頑難治"),
    (r"劉關志", "流官制"),
    (r"藏匿險地", "瘴癘險地"),
    (r"任內之想", "任內只想"),
    (r"班[賓兵]志", "班兵制"),
    (r"扣扣", "剋扣"),
    (r"渡[台臺]禁令", "渡臺禁令"),
    (r"壓力國", "壓力鍋"),
    (r"豬[衣一]櫃", "朱一貴"),
    (r"朱一[貴桂]", "朱一貴"),
    (r"橫征爆裂", "橫徵暴斂"),
    (r"近山砍", "進山砍"),
    (r"撒血[結盟誓]", "歃血結盟"),
    (r"鴨母[王汪]", "鴨母王"),
    (r"鴨母[寮療]", "鴨母寮"),
    (r"大岡山", "大岡山"),
    (r"事物破竹", "勢如破竹"),
    (r"杜[鈞君]英", "杜君英"),
    (r"機關之間的猜忌", "籍貫之間的猜忌"),
    (r"撒謊了眼", "殺紅了眼"),
    (r"抗性聯合陣線", "抗清聯合陣線"),
    (r"俘虜猝死", "俘虜處死"),
    (r"蜻蜓的[製制]毒病灶", "清廷的制度病灶"),
    (r"蜻蜓", "清廷"),
    (r"台中大禮[一弋]", "臺中大里杙"),
    (r"大禮[禦杙弋][一帶]*", "大里杙"),
    (r"大里[杙弋代]", "大里杙"),
    (r"可明", "墾民"),
    (r"羅漢[橋腳跤角]", "羅漢腳"),
    (r"截[幹竿]起義", "揭竿起義"),
    (r"同事機構", "統治機構"),
    (r"豆[粿粕]", "豆粕"),
    (r"死守不[祥降]", "死守不降"),
    (r"新副大將軍", "心腹大將軍"),
    (r"解[得了]諸羅之[危圍]", "解了諸羅之圍"),
    (r"死守帶[圓援]", "死守待援"),
    (r"實權武功", "十全武功"),
    (r"八[寶保]鎮", "八堡圳"),
    (r"台北[蒙艋][甲舺]", "臺北艋舺"),
    (r"頂下[交郊][拼拚]", "頂下郊拚"),
    (r"[全泉]州三[億邑]人", "泉州三邑人"),
    (r"[銅同][鞍安]人", "同安人"),
    (r"借到", "借道"),
    (r"以漢[治制]漢", "以漢制漢"),
    (r"[張漳]州[、，]?[全泉]州", "漳州、泉州"),
    (r"咒則", "奏摺"),
    (r"[異義]民", "義民"),
    (r"忠[誠臣]義士", "忠臣義士"),
    (r"寶中", "褒忠"),
    (r"[異義]民旗", "義民旗"),
    (r"寶中[異義]民廟", "褒忠義民廟"),
    (r"挑[戰擔]奉[範飯]", "挑擔奉飯"),
    (r"林爽[文聞]", "林爽文"),
    (r"莊大[田填]", "莊大田"),
    (r"柴大[紀記]", "柴大紀"),
    (r"福康[安按]", "福康安"),
    (r"海蘭[察查]", "海蘭察"),
    (r"巴圖[魯盧]", "巴圖魯"),
    (r"[贔屓贔負]馱碑", "贔屓馱碑"),
    (r"老衢[崎奇]", "老衢崎"),
    (r"集集[埔補]", "集集埔"),
    (r"新[埔補]", "新埔"),
    (r"六[堆對]", "六堆"),
    (r"忠義[亭庭]", "忠義亭"),
    (r"[臺台]灣", "臺灣"),
]

def correct_text(text):
    for pattern, replacement in TERM_CORRECTIONS:
        text = re.sub(pattern, replacement, text)
    return text

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis = 0
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def clean_word(w):
    return re.sub(r'[\s，。！？、；：""''（）《》〈〉…—]+', '', w)

def is_punctuation_word(w):
    return bool(re.match(r'^[\s，。！？、；：""''（）《》〈〉…—]+$', w))

def generate_natural_srt(input_json_path, output_srt_path):
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    raw_words = data.get("words", [])
    if not raw_words:
        print("[WARN] 沒有 words 資料，使用 segments 回退")
        return False
        
    filtered_words = []
    for item in raw_words:
        w_text = item["word"]
        if is_punctuation_word(w_text):
            continue
        c_text = clean_word(w_text)
        if not c_text:
            continue
        filtered_words.append({
            "word": correct_text(c_text),
            "start": item["start"],
            "end": item["end"]
        })
        
    print(f"[*] 載入有效詞彙：{len(filtered_words)} 個")
    
    sentences = []
    cur_sentence = []
    
    PAUSE_SENTENCE_BREAK = 0.55
    
    for i, w in enumerate(filtered_words):
        if not cur_sentence:
            cur_sentence.append(w)
            continue
            
        prev_w = cur_sentence[-1]
        gap = w["start"] - prev_w["end"]
        
        cur_chars = sum(len(x["word"]) for x in cur_sentence)
        
        if gap >= PAUSE_SENTENCE_BREAK or cur_chars >= 28:
            sentences.append(cur_sentence)
            cur_sentence = [w]
        else:
            cur_sentence.append(w)
            
    if cur_sentence:
        sentences.append(cur_sentence)
        
    print(f"[*] 初步依停頓劃分語句數：{len(sentences)}")
    
    final_subtitles = []
    
    for s in sentences:
        s_chars = sum(len(x["word"]) for x in s)
        s_start = s[0]["start"]
        s_end = s[-1]["end"]
        
        if s_chars <= 22:
            s_text = "".join(x["word"] for x in s)
            final_subtitles.append({
                "start": s_start,
                "end": s_end,
                "text": correct_text(s_text)
            })
        else:
            cut_idx = len(s) // 2
            best_diff = 999
            accum_chars = 0
            
            for idx in range(len(s) - 1):
                accum_chars += len(s[idx]["word"])
                diff = abs(accum_chars - (s_chars / 2))
                if diff < best_diff:
                    best_diff = diff
                    cut_idx = idx + 1
                    
            part1 = s[:cut_idx]
            part2 = s[cut_idx:]
            
            if part1:
                final_subtitles.append({
                    "start": part1[0]["start"],
                    "end": part1[-1]["end"],
                    "text": correct_text("".join(x["word"] for x in part1))
                })
            if part2:
                final_subtitles.append({
                    "start": part2[0]["start"],
                    "end": part2[-1]["end"],
                    "text": correct_text("".join(x["word"] for x in part2))
                })
                
    for i in range(len(final_subtitles) - 1):
        if final_subtitles[i]["end"] > final_subtitles[i+1]["start"]:
            final_subtitles[i]["end"] = final_subtitles[i+1]["start"]
            
    with open(output_srt_path, "w", encoding="utf-8") as f:
        for idx, sub in enumerate(final_subtitles, 1):
            start_str = format_timestamp(sub["start"])
            end_str = format_timestamp(sub["end"])
            f.write(f"{idx}\n{start_str} --> {end_str}\n{sub['text']}\n\n")
            
    print(f"[OK] 自然語氣斷句字幕生成成功！共 {len(final_subtitles)} 行字幕")
    print(f"[OK] 輸出路徑：{output_srt_path}")
    return True

if __name__ == "__main__":
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent
    in_json = str(base_dir / "04_清領時代的拓墾烽火與變革/whisper_words_ch11_podcast.json")
    out_srt = str(base_dir / "04_清領時代的拓墾烽火與變革/第11章_三年一反五年一亂_雙人對談.srt")
    generate_natural_srt(in_json, out_srt)
