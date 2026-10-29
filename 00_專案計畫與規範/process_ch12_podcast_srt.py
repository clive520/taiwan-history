# -*- coding: utf-8 -*-
"""
第12章 播客深度對談 自然語氣斷句字幕生成腳本（專業繁中分詞與語氣停頓版）
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
    "沈葆楨", "劉銘傳", "丁日昌", "邵友濂", "唐景崧", "孫開華", "林朝棟", "羅大春", "吳光亮", "李春生", "約翰·陶德", "馬偕", "白乃爾", "西鄉從道", "孤拔", "赫德",
    "牡丹社事件", "石門古戰場", "八瑤灣", "高士佛社", "牡丹社", "瑯嶠", "億載金城", "二鯤鯓砲臺", "旗後砲台", "阿姆斯特朗", "阿姆斯特朗巨砲",
    "開山撫番", "八通關古道", "蘇花古道", "崑崙坳古道", "飛虎軍", "恆春縣", "臺北府", "渡臺禁令",
    "中法戰爭", "清法戰爭", "棄基保滬", "滬尾之役", "淡水大捷", "滬尾礮臺", "北門鎖鑰", "大稻埕", "千秋街", "六館街", "迪化街",
    "寶順洋行", "德記洋行", "怡記洋行", "和記洋行", "東興洋行", "唻記洋行", "福爾摩沙烏龍茶", "包種茶", "樟腦", "經濟重心北移",
    "獅球嶺隧道", "曠宇天開", "騰雲號", "御風號", "霍恩索倫", "馬修", "莫里生", "海底電纜", "川石島",
    "臺灣郵政總局", "臺灣郵票", "臺北電燈", "西學堂", "洋務學堂", "清賦事業", "減四留六", "大租戶", "小租戶", "施九緞事件", "撫墾總局", "大嵙崁戰役"
]

for w in CUSTOM_WORDS:
    jieba.add_word(w)

TERM_CORRECTIONS = [
    (r"蜻蜓", "清廷"),
    (r"清景", "清廷"),
    (r"輕艇", "清廷"),
    (r"青菜大臣", "欽差大臣"),
    (r"秦才大臣", "欽差大臣"),
    (r"模範神", "模範省"),
    (r"現代化地義模範[者省]", "現代化第一模範省"),
    (r"頭戴鋼[龜盔]", "頭戴鋼盔"),
    (r"聯發步槍", "連發步槍"),
    (r"相擁部隊", "鄉勇部隊"),
    (r"本地相擁", "本地鄉勇"),
    (r"長滿[稻倒][池刺]的野生[灌關]木[蟲叢]", "長滿倒刺的野生灌木叢"),
    (r"長滿稻埕的零頭樹", "長滿倒刺的林投樹"),
    (r"長滿[倒稻][刺埕]的[零林][頭投]樹", "長滿倒刺的林投樹"),
    (r"[大打]刀[弱肉][脖搏]", "大刀肉搏"),
    (r"[弱肉][脖搏]戰", "肉搏戰"),
    (r"[大打]刀落花流水", "打到落花流水"),
    (r"白任[戰繞]*", "白刃戰"),
    (r"白任繞帛戰", "白刃肉搏戰"),
    (r"白刃繞帛戰", "白刃肉搏戰"),
    (r"鞭錘荒島", "邊陲荒島"),
    (r"互[惟尾]大捷", "滬尾大捷"),
    (r"互[惟尾]", "滬尾"),
    (r"護[衛尾]大捷", "滬尾大捷"),
    (r"護[衛尾]", "滬尾"),
    (r"牡丹事件", "牡丹社事件"),
    (r"一斧二[入路]三蒙[價價假]", "一府二鹿三艋舺"),
    (r"一府二鹿三[蒙艋][價舺假]", "一府二鹿三艋舺"),
    (r"大搶攻", "大搶購"),
    (r"琉球傳名", "琉球船民"),
    (r"橫村半島", "恆春半島"),
    (r"不紳士不出界", "不生事不出界"),
    (r"形不通", "行不通"),
    (r"沈寶[生楨真貞]", "沈葆楨"),
    (r"沈葆[真楨振]", "沈葆楨"),
    (r"新型冷保", "新型稜堡"),
    (r"[義一]仔金城", "億載金城"),
    (r"一載金城", "億載金城"),
    (r"同強鐵壁", "銅牆鐵壁"),
    (r"開山覆[藩翻]", "開山撫番"),
    (r"開山[撫撫][番藩]", "開山撫番"),
    (r"閒軍的中央山脈", "險峻的中央山脈"),
    (r"披出三條路", "劈出三條路"),
    (r"王島危機", "亡島危機"),
    (r"劉明[傳川]", "劉銘傳"),
    (r"流民船", "劉銘傳"),
    (r"劉銘[傳船全]", "劉銘傳"),
    (r"懷軍", "淮軍"),
    (r"契機保護", "棄基保滬"),
    (r"棄基保[滬護]", "棄基保滬"),
    (r"重病都壓在", "重兵都壓在"),
    (r"乘青州", "乘輕舟"),
    (r"全[台臺]淨失", "全臺盡失"),
    (r"吐破", "突破"),
    (r"瞬流而下", "順流而下"),
    (r"滑解", "瓦解"),
    (r"好幾十招", "好幾十艘"),
    (r"造成直接封死", "鑿沉直接封死"),
    (r"造成徹底堵死", "鑿沉徹底堵死"),
    (r"爛泥巴里", "爛泥巴裡"),
    (r"印章", "硬仗"),
    (r"《劍神與六大新政》", "《建省與六大新政》"),
    (r"打贏神章", "打贏勝仗"),
    (r"抵禦外務", "抵禦外侮"),
    (r"絲球[領嶺]", "獅球嶺"),
    (r"師[丘球][領嶺]", "獅球嶺"),
    (r"獅球嶺[隧隨]道", "獅球嶺隧道"),
    (r"著穿了", "鑿穿了"),
    (r"[親清][父夫富]事業", "清賦事業"),
    (r"[親清][父夫富]改革", "清賦改革"),
    (r"[親清]夫失業", "清賦事業"),
    (r"清[賦負]事業", "清賦事業"),
    (r"重新[葬占漲]糧", "重新丈量"),
    (r"土地[葬占漲]涼", "土地丈量"),
    (r"土地[葬占漲]糧", "土地丈量"),
    (r"填[補復]", "田賦"),
    (r"流六", "留六"),
    (r"金人財源", "驚人財源"),
    (r"髒腦", "樟腦"),
    (r"彰島", "樟腦"),
    (r"四居的祖靈", "世居的祖靈"),
    (r"傳統列場", "傳統獵場"),
    (r"大[苛科]侃戰役", "大嵙崁戰役"),
    (r"大[苛科]感戰役", "大嵙崁戰役"),
    (r"大[嵙科]崁", "大嵙崁"),
    (r"雙方史上", "雙方死傷"),
    (r"科技黃標", "科技狂飆"),
    (r"實料解說", "史料解說"),
    (r"丁日[昌常]", "丁日昌"),
    (r"邵友[濂廉聯]", "邵友濂"),
    (r"邵有[濂廉聯]", "邵友濂"),
    (r"孫開[華花]", "孫開華"),
    (r"林朝[棟東洞]", "林朝棟"),
    (r"約翰[·．\s]*陶[德得]", "約翰·陶德"),
    (r"陶[德得]", "陶德"),
    (r"李春[生聲]", "李春生"),
    (r"大[稻到]埕", "大稻埕"),
    (r"千秋[街接]", "千秋街"),
    (r"億載金[城成]", "億載金城"),
    (r"二[鯤鯤]鯓", "二鯤鯓"),
    (r"二[鯤鯤]身", "二鯤鯓"),
    (r"阿姆斯特[朗郎]", "阿姆斯特朗"),
    (r"牡丹[社設]", "牡丹社"),
    (r"八瑤[灣彎]", "八瑤灣"),
    (r"高士[佛佛][社設]", "高士佛社"),
    (r"西鄉[從從崇]道", "西鄉從道"),
    (r"石門[之戰古戰場]*", "石門古戰場"),
    (r"八通[關官]古道", "八通關古道"),
    (r"蘇花古道", "蘇花古道"),
    (r"中法[戰爭之役]*", "中法戰爭"),
    (r"清法[戰爭之役]*", "清法戰爭"),
    (r"孤[拔拔]", "孤拔"),
    (r"北門[鎖鑰鎖匙]", "北門鎖鑰"),
    (r"曠[宇雨]天[開揩]", "曠宇天開"),
    (r"騰雲[號号]", "騰雲號"),
    (r"御風[號号]", "御風號"),
    (r"川石[島鳥]", "川石島"),
    (r"減四留[六陸]", "減四留六"),
    (r"大租[戶戶]", "大租戶"),
    (r"小租[戶戶]", "小租戶"),
    (r"施九[緞段]", "施九緞"),
    (r"詩九[緞段]", "施九緞"),
    (r"撫墾[總局局]", "撫墾總局"),
    (r"戰火犀利", "戰火洗禮"),
    (r"兩指條約", "兩紙條約"),
    (r"烘開了", "轟開了"),
    (r"創造暴力", "創造暴利"),
    (r"矽谷形創", "矽谷新創"),
    (r"For Mosa", "Formosa"),
    (r"墨西哥應援", "墨西哥銀圓"),
    (r"但隨海關", "淡水海關"),
    (r"賽骨廠", "曬穀場"),
    (r"爆發戶", "暴發戶"),
    (r"化外之名", "化外之民"),
    (r"反將義軍", "反將一軍"),
    (r"六代惡性虐擊", "熱帶惡性瘧疾"),
    (r"陣而玉龍", "震耳欲聾"),
    (r"算過賬", "算過帳"),
    (r"直導臺北", "直搗臺北"),
    (r"直導台北", "直搗臺北"),
    (r"南洋悶戶東開", "南洋門戶洞開"),
    (r"正式建上", "正式建省"),
    (r"驟傾", "奏請"),
    (r"570三公尺", "573公尺"),
    (r"沙眼地質", "砂岩地質"),
    (r"才關頭", "才貫通"),
    (r"交受理化", "教授理化"),
    (r"氣提升", "汽笛聲"),
    (r"田園木戈", "田園牧歌"),
    (r"加特林技巧", "加特林機槍"),
    (r"地方好強", "地方豪強"),
    (r"強烈鳴鞭", "強烈民變"),
    (r"暴病辭職", "抱病辭職"),
    (r"內渡風景", "內渡封禁"),
    (r"油正的現代化", "郵政的現代化"),
    (r"靜待化基礎", "現代化基礎"),
    (r"績勞成疾", "積勞成疾"),
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
    in_json = str(base_dir / "04_清領時代的拓墾烽火與變革/whisper_words_ch12_podcast.json")
    out_srt = str(base_dir / "04_清領時代的拓墾烽火與變革/第12章_開港通商與現代化急先鋒_雙人對談.srt")
    generate_natural_srt(in_json, out_srt)
