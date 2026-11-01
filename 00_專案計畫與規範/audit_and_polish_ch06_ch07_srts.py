# -*- coding: utf-8 -*-
import sys
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")

CORRECTIONS = [
    # 專有名詞校驗
    (r"大園長官", "大員長官"),
    (r"大園水道", "大員水道"),
    (r"大園", "大員"),
    (r"民政陣營", "明鄭陣營"),
    (r"鄭成空", "鄭成功"),
    (r"護光楊英", "戶官楊英"),
    (r"戶官楊英所記錄的從征[史實]錄", "戶官楊英所記錄的《從征實錄》"),
    (r"從征[史實]錄", "《從征實錄》"),
    (r"路耳門", "鹿耳門"),
    (r"鹿兒門", "鹿耳門"),
    (r"過懷一", "郭懷一"),
    (r"郭懷[億亦義]", "郭懷一"),
    (r"郭懷[二貳]", "郭懷二"),
    (r"歐[灣完]平原", "歐汪平原"),
    (r"歐[灣完]", "歐汪"),
    (r"二[曾重]行溪", "二層行溪"),
    (r"二[曾重]溪", "二層行溪"),
    (r"普羅[民名]遮城", "普羅民遮城"),
    (r"普羅民[折遮]城", "普羅民遮城"),
    (r"熱[蘭藍]遮城", "熱蘭遮城"),
    (r"熱蘭[折遮]城", "熱蘭遮城"),
    (r"費爾[勃博伯]格", "費爾勃格"),
    (r"揆[一億]", "揆一"),
    (r"奎一", "揆一"),
    (r"葵一", "揆一"),
    (r"西[拉啦]雅", "西拉雅"),
    (r"西拉雅[足族]", "西拉雅族"),
    (r"王[田天]", "王田"),
    (r"人頭[稅水]", "人頭稅"),
    (r"贌[社射]", "贌社"),
    (r"贌[商傷]", "贌商"),
    (r"撲社", "贌社"),
    (r"樸社", "贌社"),
    (r"新港[社射]", "新港社"),
    (r"麻豆[社射]", "麻豆社"),
    (r"蕭[壠壟隴]社", "蕭壠社"),
    (r"目加[溜留]灣社", "目加溜灣社"),
    (r"咬[𠺕溜][吧巴]", "咬𠺕吧"),
    (r"巴[達打]維亞", "巴達維亞"),
    (r"火[繩勝]槍", "火繩槍"),
    (r"赤[崁嵌]", "赤崁"),
    (r"烏特[勒利]支", "烏特勒支"),
    (r"拔[克客]西", "拔克西"),
    (r"馬[德得]夫", "馬德夫"),
    (r"貝[德得]爾", "貝德爾"),
    (r"赫克[托託]號", "赫克托號"),
    (r"斯[霍獲]達號", "斯霍達號"),
    (r"陳[澤則]", "陳澤"),
    (r"全[臺台]大[屯純]墾", "全臺大屯墾"),
    (r"天[興新]縣", "天興縣"),
    (r"萬[年連]縣", "萬年縣"),
    (r"東[都督]明京", "東都明京"),
    (r"永[曆歷]", "永曆"),
    (r"遷[界借]令", "遷界令"),
    (r"海[禁進]", "海禁"),
    (r"蜻蜓", "清廷"),
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

def parse_time(s):
    h, m, sec_milli = s.split(":")
    sec, milli = sec_milli.split(",")
    return int(h)*3600 + int(m)*60 + int(sec) + int(milli)/1000.0

def format_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t))*1000))
    if ms >= 1000: ms = 999
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def count_cjk(s):
    return len(re.findall(r'[\u4e00-\u9fff\w]', s))

def clean_punctuation(text):
    t = text.strip()
    t = re.sub(r',\s*', '，', t)
    t = re.sub(r'^[，。！？、；：,!?;:]+', '', t)
    t = re.sub(r'[，。、；;,\.]+$', '', t)
    return t

def polish_srt(srt_path):
    print(f"\n[*] 正在全面校對並優化語意切分：{srt_path.name}")
    content = srt_path.read_text(encoding='utf-8')
    blocks = content.strip().split("\n\n")
    
    parsed = []
    for b in blocks:
        lines = b.splitlines()
        if len(lines) >= 3:
            idx = int(lines[0])
            time_line = lines[1]
            text = "\n".join(lines[2:])
            m = re.match(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", time_line)
            if m:
                # 替換專有名詞
                t = text
                for pat, rep in CORRECTIONS:
                    t = re.sub(pat, rep, t)
                t = clean_punctuation(t)
                parsed.append({
                    "start": parse_time(m.group(1)),
                    "end": parse_time(m.group(2)),
                    "text": t
                })
                
    # 拆分過長行（> 22 字元）
    new_subs = []
    for item in parsed:
        txt = item["text"]
        txt = re.sub(r'《+从征', '《從征', txt)
        txt = re.sub(r'《+從征', '《從征', txt)
        txt = re.sub(r'實錄》+', '實錄》', txt)
        txt = txt.replace('大圓', '大員')
        c_len = count_cjk(txt)
        t_start = item["start"]
        t_end = item["end"]
        duration = t_end - t_start
        
        if c_len > 22:
            # 優先以標點與空格切分
            delims = [m.start() for m in re.finditer(r'[，、\s]', txt)]
            if not delims:
                # 若無標點，以虛詞、助詞或自然語法停頓點切分
                delims = [m.end() for m in re.finditer(r'(這邊|切斷了|重砲|發生的事|轉向|也就是|因為|如果|但是|而且)', txt)]
            if not delims:
                # 最後備案：靠近中點的 的/在/和/與
                delims = [m.end() for m in re.finditer(r'[在與和]', txt)]
                
            if delims:
                mid = len(txt) / 2.0
                best_split = min(delims, key=lambda d: abs(d - mid))
                part1 = clean_punctuation(txt[:best_split])
                part2 = clean_punctuation(txt[best_split:])
                len1 = count_cjk(part1)
                len2 = count_cjk(part2)
                if len1 > 0 and len2 > 0:
                    t_mid = t_start + duration * (len1 / (len1 + len2))
                    new_subs.append({"start": t_start, "end": t_mid, "text": part1})
                    new_subs.append({"start": t_mid, "end": t_end, "text": part2})
                    continue
                    
        new_subs.append({"start": t_start, "end": t_end, "text": txt})
        
    # 時間戳防重疊修正
    for i in range(len(new_subs)-1):
        if new_subs[i]["end"] > new_subs[i+1]["start"]:
            new_subs[i]["end"] = new_subs[i+1]["start"]
            
    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, s in enumerate(new_subs, 1):
            f.write(f"{idx}\n{format_time(s['start'])} --> {format_time(s['end'])}\n{s['text']}\n\n")
            
    lens = [count_cjk(s['text']) for s in new_subs]
    avg_l = sum(lens)/len(lens) if lens else 0
    max_l = max(lens) if lens else 0
    long_cnt = sum(1 for l in lens if l > 24)
    print(f"✅ {srt_path.name}: 總行數 {len(new_subs)}, 平均 {avg_l:.1f} 字, 最大 {max_l} 字, 超過24字: {long_cnt}")

def main():
    targets = [
        BASE_DIR / "02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_說明影片.srt",
        BASE_DIR / "02_大航海時代與荷西競逐/第06章_血濺赤崁與大鹿港_雙人對談.srt",
        BASE_DIR / "03_明鄭東寧與海上孤忠/第07章_決戰大員九個月_說明影片.srt",
        BASE_DIR / "03_明鄭東寧與海上孤忠/第07章_決戰大員九個月_雙人對談.srt",
    ]
    for p in targets:
        polish_srt(p)
    print("\n🎉 四份 SRT 字幕校驗與語意平滑全數完成！")

if __name__ == '__main__':
    main()
