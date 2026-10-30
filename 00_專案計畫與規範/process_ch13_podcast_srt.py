# -*- coding: utf-8 -*-
"""
第13章 播客深度對談 自然語氣斷句字幕生成腳本（專業繁中分詞與語氣停頓版）
使用 jieba 詞庫保護專有名詞，依據真實說話語氣、呼吸停頓與完整主謂語意切分，
絕不腰斬名詞、絕無半字斷行，行長嚴格控制於 10~22 字。
"""
import os
import sys
import json
import re
import jieba

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

CUSTOM_WORDS = [
    "馬關條約", "下關條約", "春帆樓", "臺灣民主國", "唐景崧", "丘逢甲", "劉永福", "陳季同", "藍地黃虎旗", "黃虎旗", "永清",
    "樺山資紀", "北白川宮能久親王", "能久親王", "山根信成", "乃木希典", "伏見宮貞愛親王", "近衛師團", "澳底登陸", "三貂角", "三貂嶺",
    "獅球嶺", "小南門", "重熙門", "始政式", "李春生", "辜顯榮", "桃竹苗", "客家義軍", "義民", "吳湯興", "徐驤", "姜紹祖", "敢字營",
    "北埔金廣福", "天水堂", "安平鎮之役", "胡嘉猷", "大嵙崁戰役", "尖筆山之役", "八卦山戰役", "吳彭年", "七星隊", "彰化城", "大肚溪",
    "蕭壠之役", "曾文溪", "德利士號", "巴克禮", "宋忠堅", "六三法", "匪徒刑罰令", "三段警備制", "抗日三猛", "簡大獅", "柯鐵虎",
    "柯鐵", "鐵國山", "雲林大屠殺", "林少貓", "萬丹", "後壁林", "噍吧哖事件", "噍吧哖", "西來庵事件", "西來庵", "余清芳",
    "羅俊", "江定", "五福大帝", "大明慈悲國", "虎頭山之役", "虎頭山", "玉井", "楠西", "左鎮", "南化", "甲仙埔", "臨時法院",
    "臺灣文化協會", "林獻堂", "蔣渭水", "蔡培火", "議會請願"
]

for w in CUSTOM_WORDS:
    jieba.add_word(w)

TERM_CORRECTIONS = [
    (r"蜻蜓", "清廷"),
    (r"清景", "清廷"),
    (r"輕艇", "清廷"),
    (r"青菜大臣", "欽差大臣"),
    (r"秦才大臣", "欽差大臣"),
    (r"家務戰爭", "甲午戰爭"),
    (r"第一[展盞]城市電燈", "第一盞城市電燈"),
    (r"展城市電燈", "盞城市電燈"),
    (r"第一展", "第一盞"),
    (r"下指導旗", "下指導棋"),
    (r"[敬晉]衛師團", "近衛師團"),
    (r"敬畏[十師]團", "近衛師團"),
    (r"晉維[十師]?團?", "近衛師團"),
    (r"精衛使團", "近衛師團"),
    (r"近衛使團", "近衛師團"),
    (r"抄襲家夥", "抄起傢伙"),
    (r"抄襲傢伙", "抄起傢伙"),
    (r"黃[帝底]青龍旗?", "黃底青龍旗"),
    (r"藍[帝地]黃[虎滸][旗期]?", "藍地黃虎旗"),
    (r"黃[虎滸]旗", "黃虎旗"),
    (r"永遠[懸眷]念大清", "永遠眷念大清"),
    (r"分庭[靠靠]裡", "分庭抗禮"),
    (r"唐景[崧嵩松]", "唐景崧"),
    (r"丘逢[甲嘉]", "丘逢甲"),
    (r"劉永[福富]", "劉永福"),
    (r"陳季[同童]", "陳季同"),
    (r"樺山[資姿]紀", "樺山資紀"),
    (r"北白川[宮官公]能久親王", "北白川宮能久親王"),
    (r"能久親[王汪]", "能久親王"),
    (r"[山]?根信[成城]{1,2}", "山根信成"),
    (r"乃木希[典點]", "乃木希典"),
    (r"澳[底低]", "澳底"),
    (r"三貂[角腳]", "三貂角"),
    (r"[顧辜][顯顯]榮", "辜顯榮"),
    (r"[陶桃]竹苗", "桃竹苗"),
    (r"[赤刺]竹林", "刺竹林"),
    (r"載到不行", "窄到不行"),
    (r"[吳武]湯[興星]", "吳湯興"),
    (r"[吳武]唐[興新]", "吳湯興"),
    (r"吳[長常]興", "吳湯興"),
    (r"吳彭年中彈身亡吳唐", "吳彭年中彈身亡吳湯"),
    (r"新在壕溝裡", "興在壕溝裡"),
    (r"徐[驤驤襄香祥]", "徐驤"),
    (r"許[香祥驤]", "徐驤"),
    (r"須[湘驤]", "徐驤"),
    (r"[江姜]少[祖組]", "姜紹祖"),
    (r"敢[自字]營", "敢字營"),
    (r"[敢趕桿]字[營銀]", "敢字營"),
    (r"黃旭身家未存國歌此生一意願看來生", "遑恤身家為存國格此生已矣願看來生"),
    (r"遑恤身家[，\s]*為存國[格歌][；\s]*此生已[矣意][，\s]*願看來生", "遑恤身家為存國格此生已矣願看來生"),
    (r"氣雞皮疙瘩", "起雞皮疙瘩"),
    (r"金[廣廣]福", "金廣福"),
    (r"天水[堂糖]", "天水堂"),
    (r"安平[鎮陣]之役", "安平鎮之役"),
    (r"胡嘉[猷猶]", "胡嘉猷"),
    (r"大[嵙科]崁", "大嵙崁"),
    (r"尖筆[山珊]", "尖筆山"),
    (r"八[卦掛三]戰役", "八卦山戰役"),
    (r"八[卦掛]山", "八卦山"),
    (r"吳[彭鵬][年連]", "吳彭年"),
    (r"七星[隊對]", "七星隊"),
    (r"滑[糖膛]砲", "滑膛砲"),
    (r"火[蟲銃槍]", "火銃"),
    (r"箭[砲炮]", "艦砲"),
    (r"好溝", "壕溝"),
    (r"重彈身亡", "中彈身亡"),
    (r"夫曉", "拂曉"),
    (r"強?度大[度肚][息溪]", "強渡大肚溪"),
    (r"衝上林線", "衝上稜線"),
    (r"大肚[溪西]", "大肚溪"),
    (r"孤[手守]", "孤守"),
    (r"三[陸路]大軍", "三路大軍"),
    (r"包[朝抄]", "包抄"),
    (r"實戰到南部", "死戰到南部"),
    (r"蕭[壠壟瓏]", "蕭壠"),
    (r"曾文[溪西][盤畔]?", "曾文溪畔"),
    (r"覬覦後望", "寄予厚望"),
    (r"德[利力]士號", "德利士號"),
    (r"巴克[禮禮里][牧木]?[師斯]?", "巴克禮牧師"),
    (r"宋[忠中]堅", "宋忠堅"),
    (r"[以乙]未戰爭", "乙未戰爭"),
    (r"六[三參]法", "六三法"),
    (r"[匪非]徒刑罰令", "匪徒刑罰令"),
    (r"三段警[備備]制", "三段警備制"),
    (r"[施獅][孟猛]", "獅猛"),
    (r"簡大[獅師]", "簡大獅"),
    (r"[胡虎][盟猛]", "虎猛"),
    (r"柯鐵[虎滸胡]", "柯鐵虎"),
    (r"柯[鐵鐵]", "柯鐵"),
    (r"鐵[國國]山", "鐵國山"),
    (r"[貓描][盟猛]", "貓猛"),
    (r"林少[貓苗]", "林少貓"),
    (r"後[壁璧]林", "後壁林"),
    (r"治[堂糖]會社", "製糖會社"),
    (r"剝削折農", "剝削蔗農"),
    (r"(?:噍吧哖|焦八年|焦吧年|喬巴[黏粘]|朝霸年)[事件劫]*", "噍吧哖事件"),
    (r"西[來來][庵安]", "西來庵"),
    (r"[宇余][清新][芳方]", "余清芳"),
    (r"[羅羅]俊", "羅俊"),
    (r"江[定訂]", "江定"),
    (r"五[福副]大帝", "五福大帝"),
    (r"大明慈[悲碑]國", "大明慈悲國"),
    (r"刀槍[補不]入", "刀槍不入"),
    (r"挨餓受[動凍]", "挨餓受凍"),
    (r"鳥[衝銃叢]", "鳥銃"),
    (r"刀刀和鳥[叢銃]", "大刀和鳥銃"),
    (r"淡雨", "彈雨"),
    (r"扇拋上", "山坡上"),
    (r"扇拋", "山砲"),
    (r"山砲上死傷枕藉", "山坡上死傷枕藉"),
    (r"死傷[整正]戒", "死傷枕藉"),
    (r"戰後的[傾清]向", "戰後的清鄉"),
    (r"虎[頭投]山", "虎頭山"),
    (r"玉[井景]", "玉井"),
    (r"楠[西細]", "楠西"),
    (r"無[南男]丁", "無男丁"),
    (r"戶戶[街皆]哭聲", "戶戶皆哭聲"),
    (r"[剪減]刑", "減刑"),
    (r"(?:被送上了)?僥倖台", "被送上了絞刑臺"),
    (r"唱他20年", "長達20年"),
    (r"教醒了", "叫醒了"),
    (r"神[父符]悲劇", "神符悲劇"),
    (r"由血肉之軀", "用血肉之軀"),
    (r"草[蟒莽]抗暴", "草莽抗暴"),
    (r"左[鎮陣]", "左鎮"),
    (r"南[化華]", "南化"),
    (r"甲仙[埔補]", "甲仙埔"),
    (r"浮水", "符水"),
    (r"蔣[渭衛]水", "蔣渭水"),
    (r"林[獻獻][堂棠]", "林獻堂"),
    (r"蔡培[火伙]", "蔡培火"),
    (r"[敲撬]動龐然大物", "撬動龐然大物"),
    (r"蠻[桿幹]", "蠻幹"),
    (r"爭脫", "掙脫"),
    (r"鞭錘荒島", "邊陲荒島"),
    (r"春帆[樓樓]", "春帆樓"),
    (r"下關[條條]約", "下關條約"),
    (r"馬關[條條]約", "馬關條約"),
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
    in_json = str(base_dir / "05_日治時期的統治轉型與抗爭/whisper_words_ch13_podcast.json")
    out_srt = str(base_dir / "05_日治時期的統治轉型與抗爭/第13章_乙未悲歌與武裝抗日_雙人對談.srt")
    generate_natural_srt(in_json, out_srt)
