# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 04 章 完美版影視級字幕生成器
1. 嚴格檢查並校正所有錯別字、同音字、OpenCC 繁簡轉換瑕疵與專有名詞
2. 重建合乎人類呼吸與說話語氣的自然斷句（單行 8~16 字，0 破字破詞，獨立保留對話語氣詞）
"""
import sys
import os
import re
from pathlib import Path
import opencc

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH04_DIR = BASE_DIR / "舌尖上的臺灣" / "02_唐山渡海與閩粵交融"

VID_SRT = CH04_DIR / "第04章_一碗肉臊的百年身世_說明影片.srt"
POD_SRT = CH04_DIR / "第04章_一碗肉臊的百年身世_雙人對談.srt"

LOG_VID = Path(r"C:\Users\admin\.gemini\antigravity\brain\e6ad31e6-5e47-44d3-86ec-3061599c52d4\.system_generated\tasks\task-11619.log")
LOG_POD = Path(r"C:\Users\admin\.gemini\antigravity\brain\e6ad31e6-5e47-44d3-86ec-3061599c52d4\.system_generated\tasks\task-11578.log")

cc = opencc.OpenCC('s2twp')

# 專家級全域同音字與專有名詞替換表
EXPERT_CORRECTIONS = [
    # 料理與店名專名
    (r'肉[燥噪][飯反]', '肉臊飯'),
    (r'乳[肉酪][飯反]', '滷肉飯'),
    (r'滷肉[飯反]', '滷肉飯'),
    (r'肉燒[飯反]', '肉臊飯'),
    (r'肉鬆飯', '肉臊飯'),
    (r'肉燒', '肉臊'),
    (r'肉[燥噪]', '肉臊'),
    (r'[焢空炕]肉[飯反]', '爌肉飯'),
    (r'[焢空炕]肉', '爌肉'),
    (r'黑豆[蔭蔭印應]油', '黑豆蔭油'),
    (r'[蔭蔭印應]油', '蔭油'),
    (r'黑豆醬油', '黑豆醬油'),
    (r'輕人黑豆', '青仁黑豆'),
    (r'青仁黑豆', '青仁黑豆'),
    (r'[杜肚]小[岳月嶽]', '度小月'),
    (r'小[岳月嶽]期間', '小月期間'),
    (r'小[岳月嶽]', '小月'),
    (r'蛋在[麵面]', '擔仔麵'),
    (r'蛋仔[麵面]', '擔仔麵'),
    (r'擔仔[麵面]', '擔仔麵'),
    (r'蛋子賣[麵面]', '挑擔賣麵'),
    (r'挑[著着]挑擔賣[麵面]', '挑著擔子賣麵'),
    (r'挑[著着]蛋子', '挑著擔子'),
    (r'挑起扁[單擔]', '挑起扁擔'),
    (r'洪玉頭', '洪芋頭'),
    (r'食慕[餘魚][松鬆]', '虱目魚鬆'),
    (r'虱目[餘魚][松鬆]', '虱目魚鬆'),
    
    # 科學術語與生化機制
    (r'剪下力', '剪切力'),
    (r'機械剪下力', '機械剪切力'),
    (r'福[安溫]酸', '谷氨酸'),
    (r'浮[安溫]酸', '谷氨酸'),
    (r'谷[氨胺]酸', '谷氨酸'),
    (r'有禮案積算', '游離氨基酸'),
    (r'游離[氨胺]基酸', '游離氨基酸'),
    (r'[氨胺]基酸', '氨基酸'),
    (r'鶴變', '褐變'),
    (r'青[腱鍵]', '氫鍵'),
    (r'親[腱鍵]', '氫鍵'),
    (r'供價界', '共價鍵'),
    (r'共價[界鍵]', '共價鍵'),
    (r'可[容溶]性', '可溶性'),
    (r'[融溶]膠凝膠[項相]邊', '溶膠凝膠相變'),
    (r'[項相]邊', '相變'),
    (r'單[煉鏈]的明膠', '單鏈的明膠'),
    (r'螺圓', '螺旋'),
    (r'明膠微[低滴]', '明膠微滴'),
    (r'非[急極]性微[膠酵]束', '非極性微膠束'),
    (r'比奇類與差分類化合物', '吡嗪類與吡咯類化合物'),
    (r'堅果交[向香]', '堅果焦香'),
    (r'發[炎煙]點高達190度', '發煙點高達190度'),
    (r'發[炎煙]點', '發煙點'),
    (r'[基肌]間脂肪', '肌間脂肪'),
    (r'[溶熔]點', '熔點'),
    (r'水解[霉酶黴]', '水解酶'),
    (r'食品[圍微][觀觀]結構[修學]的核心', '食品微觀結構學的核心'),
    (r'梅[納納]反應', '梅納反應'),
    (r'膠原蛋白', '膠原蛋白'),
    (r'三螺旋結構', '三螺旋結構'),
    (r'三螺旋膠原蛋白', '三螺旋膠原蛋白'),
    (r'連線起來', '連接起來'),
    (r'劃過舌面', '滑過舌面'),
    (r'嘴唇微[膩抿]', '嘴唇微抿'),
    (r'[燒稍]涼的空氣', '稍涼的空氣'),
    (r'濃鬱', '濃郁'),
    
    # 歷史文獻、地名與成語口語
    (r'水星公司場', '水仙宮市場'),
    (r'水仙宮市場', '水仙宮市場'),
    (r'水仙宮', '水仙宮'),
    (r'像是那個《+諸羅縣志》+啦', '像是那個《諸羅縣志》啦'),
    (r'侏羅縣[治志]拉?', '《諸羅縣志》啦'),
    (r'諸羅縣[治志]', '《諸羅縣志》'),
    (r'重修台[灣湾][輔府][治志]', '《重修臺灣府志》'),
    (r'台[灣湾][輔府][治志]', '《臺灣府志》'),
    (r'台[灣湾]福祉', '《臺灣府志》'),
    (r'說文解字', '《說文解字》'),
    (r'臺灣方[製志]', '臺灣方志'),
    (r'官方[歷立]的禁宰石碑', '官方立的禁宰石碑'),
    (r'折損[因陰][得德]', '折損陰德'),
    (r'中[原元]普渡', '中元普渡'),
    (r'王爺建[教醮]', '王爺建醮'),
    (r'馬[腦瑙]光澤', '瑪瑙光澤'),
    (r'像馬[腦瑙]一樣', '像瑪瑙一樣'),
    (r'馬[腦瑙]', '瑪瑙'),
    (r'百年[生身][事世]', '百年身世'),
    (r'羅漢[角腳]', '羅漢腳'),
    (r'[鮮先]明', '先民'),
    (r'島嶼[鮮先]明', '島嶼先民'),
    (r'[資隻]身渡海', '隻身渡海'),
    (r'敗敗[丸完]', '拜拜完'),
    (r'[雅亞]熱帶氣候', '亞熱帶氣候'),
    (r'分子三[味位]液體', '分子三位一體'),
    (r'分子三[味位]一體', '分子三位一體'),
    (r'[這这]個[峰風][威味]方程式', '這個風味方程式'),
    (r'早期的[一移]民', '早期的移民'),
    (r'像木[蟹屑]一樣', '像木屑一樣'),
    (r'立體[集幾]合形狀', '立體幾何形狀'),
    (r'熱力學之[律旅]', '熱力學之旅'),
    (r'竹皮', '豬皮'),
    (r'三大地[獄域]流派', '三大地域流派'),
    (r'地[獄域]差異', '地域差異'),
    (r'地[獄域]流派', '地域流派'),
    (r'富商[四仕][生紳]', '富商仕紳'),
    (r'[同銅]班美食', '銅板美食'),
    (r'大口[拔扒]下', '大口扒下'),
    (r'做[出粗]活', '做粗活'),
    (r'[芥街]頭小吃', '街頭小吃'),
    (r'[應硬][任韌]的膠原蛋白', '硬韌的膠原蛋白'),
    (r'黏[醇唇][豐厚]+', '黏唇豐厚'),
    (r'黏[醇唇]感', '黏唇感'),
    (r'一[玩碗]把脂肪', '一碗把脂肪'),
    (r'[垂催]化劑', '催化劑'),
    (r'10度有保表', '濕度又爆表'),
    (r'[建見]方的肉[夾丁角]', '見方的肉丁'),
    (r'皮\s*[汁脂]\s*肉', '皮、脂、肉'),
    (r'什麼魔法[司時]客', '什麼魔法時刻'),
    (r'當結果肉臊', '當這鍋肉臊'),
    (r'雲[加嘉]南沿海是[危微][險鹹]的沙[子質]土壤', '雲嘉南沿海是微鹹的沙質土壤'),
    (r'白[化話][紋文]', '白話文'),
    (r'解除[風封][陰印]', '解除封印'),
    (r'爆銷了', '報銷了'),
    (r'[圍微]孔陶[鋼缸]', '微孔陶缸'),
    (r'[鋼缸]內溫度', '缸內溫度'),
    (r'[獨毒][立辣]太陽', '毒辣太陽'),
    (r'[喜洗]好[曲麴]的黑豆', '洗好麴的黑豆'),
    (r'大[變辯][整證]', '大辯證'),
    (r'吃[除粗]飽的', '吃粗飽的'),
    (r'[西細][脆碎]狀', '細碎狀'),
    (r'勞動重[症鎮]', '勞動重鎮'),
    (r'[不步]?14小時', '24小時'),
    (r'[這這]片便宜', '這碗便宜'),
    (r'深度探探', '深度探討'),
    (r'抗[蒸熱]氣候', '抗熱氣候'),
    (r'源自[實史]料', '源自史料'),
    (r'sou這個字', '「臊」這個字'),
    (r'[屎豕]膏臭[眼也]', '豕膏臭也'),
    (r'高溫多[餘雨]', '高溫多雨'),
    (r'嘴巴[里裡]', '嘴巴裡'),
    (r'像氣候妥協', '向氣候妥協'),
    (r'甚至早期富商仕紳那種精緻點心文化的印象', '深受早期富商仕紳那種精緻點心文化的影響'),
    (r'正是走入市民的美[學食]殿堂', '正式走入市民的美食殿堂'),
    
    # 消除 OpenCC 繁簡轉換過度 artifacts
    (r'為瞭解決', '為了解決'),
    (r'為瞭', '為了'),
    (r'發明瞭', '發明了'),
    (r'證明瞭', '證明了'),
    (r'裡麵', '裡面'),
    (r'儲存技術', '保存技術'),
    (r'儲存問題', '保存問題'),
    
    # 臺灣習慣正體字
    (r'台([灣北市南中東中東南東東南])', r'臺\1'),
    (r'全台', '全臺'),
    (r'在台', '在臺'),
    (r'來台', '來臺'),
    (r'[臺台]灣', '臺灣'),
]

def clean_text(text: str) -> str:
    t = cc.convert(text)
    for pat, rep in EXPERT_CORRECTIONS:
        t = re.sub(pat, rep, t)
    # 清除多餘英文逗號與連續空白
    t = t.replace(', ', '，').replace(',', '，')
    t = t.replace('? ', '？').replace('?', '？')
    t = t.replace('! ', '！').replace('!', '！')
    # 去除首尾標點
    t = re.sub(r'^[，。！？、；：\s]+', '', t)
    t = re.sub(r'[，。；、\s]+$', '', t)
    return t.strip()

def time_to_sec(ts):
    h, m, s_ms = ts.split(":")
    s, ms = s_ms.split(",")
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0

def sec_to_time(sec):
    td = max(0.0, sec)
    hrs = int(td // 3600)
    mins = int((td % 3600) // 60)
    secs = int(td % 60)
    millis = int(round((td - int(td)) * 1000))
    if millis >= 1000: millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def load_segments_from_log(log_path: Path):
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    pattern = re.compile(r'^\s*\[(\d{2}:\d{2}:\d{2},\d{3})\s*->\s*(\d{2}:\d{2}:\d{2},\d{3})\]\s*(.*)$', re.MULTILINE)
    matches = pattern.findall(content)
    segments = []
    for st, et, raw in matches:
        txt = clean_text(raw)
        if txt:
            segments.append({
                'start': time_to_sec(st),
                'end': time_to_sec(et),
                'text': txt
            })
    return segments

# 手動指定之特定長句自然意群斷句表 (完全貼合口語說話氣息)
SPECIFIC_SPLITS = [
    # 說明片長句斷句
    ("膠原蛋白那種堅韌的三螺旋結構就會完全解開", ["膠原蛋白那種堅韌的三螺旋結構", "就會完全解開"]),
    ("我們快速回顧一下它在社會經濟上的崛起過程", ["我們快速回顧一下", "它在社會經濟上的崛起過程"]),
    ("臺南的漁民為了在沒辦法出海的淡季討生活", ["臺南的漁民為了", "在沒辦法出海的淡季討生活"]),
    ("這碗銅板美食不但端上了總統就職的國宴餐桌", ["這碗銅板美食", "不但端上了總統就職的國宴餐桌"]),
    ("更在2018年拿下了米其林指南的星級認證", ["更在2018年", "拿下了米其林指南的星級認證"]),
    ("它裡面其實裝滿了我們300年的生存適應", ["它裡面其實裝滿了", "我們三百年的生存適應"]),
    ("它裡面其實裝滿了我們三百年的生存適應", ["它裡面其實裝滿了", "我們三百年的生存適應"]),
    ("因為受到早期富商仕紳那種精緻點心文化的影響", ["因為受到早期富商仕紳", "那種精緻點心文化的影響"]),
    ("氨基酸和糖分會直接碰撞出那種濃郁的焦香", ["氨基酸和糖分", "會直接碰撞出那種濃郁的焦香"]),
    
    # 播客長句斷句
    ("想像一下，你人生中吃過最棒的一碗肉臊飯", ["想像一下", "你人生中吃過最棒的一碗肉臊飯"]),
    ("那是紅蔥頭被高溫的動物油脂逼出來的濃烈焦香", ["那是紅蔥頭被高溫動物油脂", "逼出來的濃烈焦香"]),
    ("接著，老闆就遞給你一碗剛起鍋還冒著熱氣的白飯", ["接著，老闆就遞給你", "一碗剛起鍋還冒著熱氣的白飯"]),
    ("接著 老闆就遞給你一碗剛起鍋還冒著熱氣的白飯", ["接著，老闆就遞給你", "一碗剛起鍋還冒著熱氣的白飯"]),
    ("而且幾乎存在於我們每一個臺灣人的記憶裡面", ["而且幾乎存在於", "我們每一個臺灣人的記憶裡面"]),
    ("當時的社會底層到底是遇到了什麼樣的困境", ["當時的社會底層", "到底是遇到了什麼樣的困境"]),
    ("哇 這根本就是古代版的真空包裝技術嗎？", ["哇！這根本就是", "古代版的真空包裝技術嗎？"]),
    ("是透過巨大的機械剪切力去粗暴的撕裂肌肉纖維", ["是透過巨大的機械剪切力", "去粗暴地撕裂肌肉纖維"]),
    ("對，這種擠壓會瞬間壓破脂肪細胞的細胞壁", ["對，這種擠壓會瞬間", "壓破脂肪細胞的細胞壁"]),
    ("難怪，有時候我們去吃那種很便宜大量製造的滷肉飯", ["難怪，有時候我們去吃", "那種很便宜大量製造的滷肉飯"]),
    ("這樣是不是也能做出一樣的味道又比較健康", ["這樣是不是也能做出一樣的味道", "又比較健康？"]),
    ("當你把它切片丟進135到145度的滾燙豬油裡", ["當你把它切片", "丟進135到145度的滾燙豬油裡"]),
    ("把這些在135度以上產生的脆弱香氣分子", ["把這些在135度以上", "產生的脆弱香氣分子"]),
    ("豬油的分子結構就像是一個個微型的保險箱", ["豬油的分子結構", "就像是一個個微型的保險箱"]),
    ("不過，當這套底層技術在臺灣島上開枝散葉之後", ["不過，當這套底層技術", "在臺灣島上開枝散葉之後"]),
    ("沒錯，這是一場從味覺看臺灣文化地理的大辯證", ["沒錯，這是一場", "從味覺看臺灣文化地理的大辯證"]),
    ("直接給你一整塊厚切的三層肉還插著一根竹籤", ["直接給你一整塊厚切的三層肉", "還插著一根竹籤"]),
    ("對那些在碼頭搬貨或是在田裡幹活的勞工來說", ["對那些在碼頭搬貨", "或是在田裡幹活的勞工來說"]),
    ("而且他在近代還完成了一場驚人的階級跨越", ["而且他在近代", "還完成了一場驚人的階級跨越"]),
    ("下一次，當你坐在路邊攤，看著那碗泛著瑪瑙光澤的肉臊飯時", ["下一次，當你坐在路邊攤", "看著那碗泛著瑪瑙光澤的肉臊飯時"]),
    ("希望你能感受到，這三百年來，島嶼先民在匱乏中相濡以沫的溫暖體溫", ["希望你能感受到，這三百年來", "島嶼先民在匱乏中相濡以沫的溫暖體溫"]),
    ("這三百年來，島嶼先民在匱乏中相濡以沫的溫暖體溫", ["這三百年來", "島嶼先民在匱乏中相濡以沫的溫暖體溫"]),
    ("節目的最後，我想留給你們一個源自史料、", ["節目的最後", "我想留給你們一個", "源自史料非常震撼的小細節"]),
    ("節目的最後，我想留給你們一個源自史料、非常震撼的小細節", ["節目的最後", "我想留給你們一個", "源自史料非常震撼的小細節"]),
    ("我想留給你們一個源自史料非常震撼的小細節", ["我想留給你們一個", "源自史料非常震撼的小細節"]),
    ("但你知道「臊」這個字在漢朝的《說文解字》裡是什麼意思嗎", ["但你知道「臊」這個字", "在漢朝《說文解字》裡是什麼意思嗎？"]),
    ("也就是豬脂肪在加熱時散發出來的那種強烈腥臭味", ["也就是豬脂肪在加熱時", "散發出來的那種強烈腥臭味"]),
    ("爛牌也能打成神作，在你的生命中", ["爛牌也能打成神作！", "在你的生命中"]),
    ("非常感謝你今天跟我們一起進行這場深度解析", ["非常感謝你今天", "跟我們一起進行這場深度解析"]),
    ("我們下次見囉，謝謝你的收聽", ["我們下次見囉！", "謝謝你的收聽"]),
]

def split_long_item(item):
    txt = item['text']
    for pat, parts in SPECIFIC_SPLITS:
        if txt == pat or txt.startswith(pat[:10]) and len(pat) > 15:
            dur = item['end'] - item['start']
            total_chars = sum(len(p) for p in parts)
            res = []
            cur_st = item['start']
            for p in parts:
                p_dur = dur * (len(p) / total_chars)
                res.append({'start': cur_st, 'end': cur_st + p_dur, 'text': p})
                cur_st += p_dur
            return res
            
    if len(txt) > 18:
        split_pos = -1
        for p in ['，', '、', '而且', '但是', '因為', '所以', '接著', '還有', '那種']:
            idx = txt.find(p)
            if idx >= 6 and idx <= len(txt) - 5:
                split_pos = idx + (1 if p in ['，', '、'] else 0)
                break
        if split_pos != -1:
            p1 = txt[:split_pos].rstrip('，')
            p2 = txt[split_pos:].lstrip('，')
            dur = item['end'] - item['start']
            mid = item['start'] + dur * (len(p1) / (len(p1) + len(p2)))
            return [{'start': item['start'], 'end': mid, 'text': p1},
                    {'start': mid, 'end': item['end'], 'text': p2}]
                    
    return [item]

def format_video_subtitles(segs):
    """
    說明短片影視級說話呼吸語氣斷句優化：
    - 單人解說節奏明快，段落過渡詞（好、接著、首先、重點來了）單獨開行。
    - 連貫句子在 8~14 字內自然合併，嚴禁跨句生硬黏貼。
    - 超長句（> 18 字）依子句邊界自然斷開。
    """
    merged = []
    i = 0
    while i < len(segs):
        cur = segs[i]
        txt = cur['text']
        
        # 特殊過渡詞處理
        TRANSITION_WORDS = ['準備好了嗎？', '好，我們直接進到第一部分', '重點來了', '也就是說', '這代表什麼？', '接著']
        if any(txt == w for w in TRANSITION_WORDS):
            merged.append(cur)
            i += 1
            continue

        # 如果當前行很短（< 8 字）且下一句緊接著（pause < 0.3s）
        if i + 1 < len(segs):
            nxt = segs[i+1]
            pause = nxt['start'] - cur['end']
            comb_len = len(txt) + len(nxt['text'])
            
            # 若下一句是段落過渡詞或問答，不合併
            if not any(nxt['text'].startswith(w) for w in TRANSITION_WORDS) and not txt.endswith('？'):
                if pause <= 0.30 and comb_len <= 15:
                    sep = '，' if len(txt) >= 4 and len(nxt['text']) >= 4 and not txt.endswith('，') else ''
                    cur['text'] = txt + sep + nxt['text']
                    cur['end'] = nxt['end']
                    merged.append(cur)
                    i += 2
                    continue

        merged.append(cur)
        i += 1

    formatted = []
    for item in merged:
        formatted.extend(split_long_item(item))

    return formatted

def format_podcast_subtitles(segs):
    """
    雙人對談 Podcast 說話語氣斷句優化：
    - 嚴格保護講者輪替反饋詞（對吧？、沒錯、真的、好、你說、完全正確、原來如此）。
    - 保持對話提問與回應的呼吸停頓。
    - 同一講者的連貫吐氣在 8~16 字內自然銜接。
    """
    STANDALONE_INTERACTIONS = {
        '對吧？', '對啊', '對', '沒錯', '沒錯沒錯', '真的', '哇', '好', '你說',
        '就是啊', '完全正確', '是的', '原來如此', '天啊', '等等', '有多不一樣？',
        '有多不一樣', '階級跨越怎麼說？', '階級跨越怎麼說', '度小月是這樣來的？',
        '度小月是這樣來的', '我皮超厚的耶', '蛤，為什麼？不都是油嗎？', '加熱不就好了'
    }

    merged = []
    i = 0
    while i < len(segs):
        cur = segs[i]
        txt = cur['text']

        # 若是互動詞，絕對獨立保留，體現講者情緒與停頓
        if txt in STANDALONE_INTERACTIONS:
            merged.append(cur)
            i += 1
            continue

        # 嘗試合併同講者短句（< 7 字）
        if i + 1 < len(segs):
            nxt = segs[i+1]
            pause = nxt['start'] - cur['end']
            comb_len = len(txt) + len(nxt['text'])
            
            if nxt['text'] not in STANDALONE_INTERACTIONS and not txt.endswith('？'):
                if pause <= 0.25 and comb_len <= 15:
                    sep = '，' if len(txt) >= 4 and len(nxt['text']) >= 4 and not txt.endswith('，') else ''
                    cur['text'] = txt + sep + nxt['text']
                    cur['end'] = nxt['end']
                    merged.append(cur)
                    i += 2
                    continue

        merged.append(cur)
        i += 1

    formatted = []
    for item in merged:
        formatted.extend(split_long_item(item))

    return formatted

def enforce_monotonicity(subs):
    for j in range(len(subs) - 1):
        if subs[j]['end'] > subs[j+1]['start']:
            subs[j]['end'] = subs[j+1]['start']
        if subs[j]['end'] <= subs[j]['start']:
            subs[j]['end'] = subs[j]['start'] + 0.35
    return subs

def save_srt_file(subs, path: Path):
    lines = []
    for idx, item in enumerate(subs, 1):
        lines.append(f"{idx}\n{sec_to_time(item['start'])} --> {sec_to_time(item['end'])}\n{item['text']}\n")
    path.write_text("\n".join(lines), encoding='utf-8')
    lens = [len(x['text']) for x in subs]
    print(f"✅ 已輸出高規格字幕：{path.name}")
    print(f"   總行數: {len(subs)} 行 | 最小: {min(lens)} 字 | 平均: {sum(lens)/len(lens):.1f} 字 | 最大: {max(lens)} 字")

def main():
    print("🎬 [1/2] 正在製作說明影片影視級字幕...")
    v_raw = load_segments_from_log(LOG_VID)
    v_fmt = format_video_subtitles(v_raw)
    v_clean = enforce_monotonicity(v_fmt)
    save_srt_file(v_clean, VID_SRT)

    print("\n🎙️ [2/2] 正在製作播客對談影視級字幕...")
    p_raw = load_segments_from_log(LOG_POD)
    p_fmt = format_podcast_subtitles(p_raw)
    p_clean = enforce_monotonicity(p_fmt)
    save_srt_file(p_clean, POD_SRT)

if __name__ == '__main__':
    main()
