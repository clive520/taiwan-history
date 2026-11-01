# -*- coding: utf-8 -*-
"""
第 14 章 說明影片與雙人對談 SRT 全面自然語意與錯字精修器
"""
import sys
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH14_DIR = BASE_DIR / "05_日治時期的統治轉型與抗爭"

VIDEO_SRT = CH14_DIR / "第14章_現代化骨架與殖民之刃_說明影片.srt"
PODCAST_SRT = CH14_DIR / "第14章_現代化骨架與殖民之刃_雙人對談.srt"

PODCAST_CORRECTIONS = [
    # 專有名詞與特定勘誤
    (r"虐擊", "瘧疾"),
    (r"禍亂，還有赤利", "霍亂，還有赤痢"),
    (r"赤利", "赤痢"),
    (r"禍亂", "霍亂"),
    (r"驚人的好損", "驚人的耗損"),
    (r"風火連天", "烽火連天"),
    (r"十之無畏，氣之可惜", "食之無味，棄之可惜"),
    (r"1988年，第四任", "1898年，第四任"),
    (r"耳聿袁太郎", "兒玉源太郎"),
    (r"後彤興平", "後藤新平"),
    (r"後藤興平", "後藤新平"),
    (r"熱帶病床", "熱帶病瘴"),
    (r"搖錢術", "搖錢樹"),
    (r"絕對心不同的對吧，當然心不同", "絕對行不通的對吧，當然行不通"),
    (r"心不同", "行不通"),
    (r"士生", "士紳"),
    (r"總統府甚至發明", "總督府甚至發明"),
    (r"總統府哪來那麼多現金", "總督府哪來那麼多現金"),
    (r"如果總統府倒台", "如果總督府倒臺"),
    (r"伸張制度", "紳章制度"),
    (r"運作機制更優惠", "運作機制更幽微"),
    (r"立牌眾議", "力排眾議"),
    (r"現耕電農", "佃農"),
    (r"1%地級圖", "精密地籍圖"),
    (r"地級圖", "地籍圖"),
    (r"日本帝國的城王綁在一起", "日本帝國的存亡綁在一起"),
    (r"這倒太狠了", "這招太狠了"),
    (r"買斷了你個中程", "買斷了你的忠誠"),
    (r"影田", "隱田"),
    (r"遞稅收入", "地稅收入"),
    (r"正式轉信為", "正式轉型為"),
    (r"長谷山警戒", "長谷川謹介"),
    (r"長谷山", "長谷川"),
    (r"舊山縣", "舊山線"),
    (r"鋼筒沉香", "鋼筒沉箱"),
    (r"胡新亭", "湖心亭"),
    (r"卻反效促成了", "卻反向促成了"),
    (r"荒天漢地", "荒天旱地"),
    (r"坑田田", "看天田"),
    (r"鹽減化", "鹽鹼化"),
    (r"八田羽一", "八田與一"),
    (r"八天羽翼", "八田與一"),
    (r"八天與一", "八田與一"),
    (r"八田與衣", "八田與一"),
    (r"15萬雜土地", "15萬甲土地"),
    (r"嘉南大準", "嘉南大圳"),
    (r"加南大圳", "嘉南大圳"),
    (r"加南大郡", "嘉南大圳"),
    (r"大型蒸汽產", "大型蒸汽鏟"),
    (r"半水利田主式大壩", "半水力填築式大壩"),
    (r"黏土新墻", "黏土心牆"),
    (r"吃到三分之一圈", "赤道三分之一圈"),
    (r"刻在殉功碑上", "刻在殉工碑上"),
    (r"水利俱樂部", "水利組合"),
    (r"三年輪座給水制", "三年輪作給水制"),
    (r"第一年種水到有水", "第一年種水稻有水"),
    (r"颱風欠壽", "颱風歉收"),
    (r"變賣填產", "變賣田產"),
    (r"淪為認認宰割的電農", "淪為任人宰割的佃農"),
    (r"電農", "佃農"),
    (r"經驗與人道", "精湛與人道"),
    (r"米糖香客", "米糖相剋"),
    (r"低夯 進嘎 或揮霞棒", "第一憨，種甘蔗予會社磅"),
    (r"日本裁罰", "日本財閥"),
    (r"三井或三林", "三井或三菱"),
    (r"會社會擁有", "會社擁有"),
    (r"甘蔗過邦的時候", "甘蔗過磅的時候"),
    (r"過邦", "過磅"),
    (r"毫無一價能力", "毫無議價能力"),
    (r"一價能力", "議價能力"),
    (r"基永吉與莫永仁", "磯永吉與末永仁"),
    (r"自當會社", "製糖會社"),
    (r"製藤會社", "製糖會社"),
    (r"米谷", "米穀"),
    (r"但業了滿足", "但為了滿足"),
    (r"番薯千度日", "番薯籤度日"),
    (r"李英璋", "李應章"),
    (r"搭著火車圈道串聯", "搭著火車全島串聯"),
    (r"圈道串聯", "全島串聯"),
    (r"讓人氣急疲格大", "讓人起雞皮疙瘩"),
    (r"這坊鋼鐵骨架", "這幅鋼鐵骨架"),
    (r"非常好的扣文", "非常好的叩問"),
    (r"現代版的數位電腦", "現代版的數位佃農"),
    (r"數位電腦", "數位佃農"),
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
]

def parse_srt(content):
    blocks = content.strip().split("\n\n")
    entries = []
    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if len(lines) >= 3:
            tc = lines[1]
            text = " ".join(lines[2:])
            m = re.match(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", tc)
            if m:
                entries.append({
                    "start_s": m.group(1),
                    "end_s": m.group(2),
                    "text": text
                })
    return entries

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

def clean_text(text, corrections):
    t = text.strip()
    for pat, rep in corrections:
        t = re.sub(pat, rep, t)
    t = re.sub(r'^[，。！？、；：,!?;:]+', '', t)
    t = re.sub(r'[，。、；;,\.]+$', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def count_cjk(s):
    return len(re.findall(r'[\u4e00-\u9fff\w]', s))

def refine_file(srt_path, corrections):
    print(f"\n[*] 正在精修: {srt_path.name}")
    raw_content = srt_path.read_text(encoding='utf-8')
    entries = parse_srt(raw_content)
    print(f"[*] 原始字幕行數: {len(entries)}")
    
    # 錯字校正
    for e in entries:
        e['text'] = clean_text(e['text'], corrections)
        e['start'] = time_to_sec(e['start_s'])
        e['end'] = time_to_sec(e['end_s'])
        
    # 自然語意合併過短行 (< 6 字或以介詞/連詞結尾者)
    merged = []
    i = 0
    while i < len(entries):
        cur = entries[i]
        cur_t = cur['text']
        cur_len = count_cjk(cur_t)
        
        if i + 1 < len(entries):
            nxt = entries[i+1]
            nxt_t = nxt['text']
            nxt_len = count_cjk(nxt_t)
            gap = nxt['start'] - cur['end']
            
            needs_join = False
            # 結尾是破句介詞/連詞/動詞
            if re.search(r'(在|了|的|和|與|將|把|以|從|由|向|對|而|但|因為|所以|包括|則是|也就是|所謂的)$', cur_t):
                needs_join = True
            elif cur_len <= 5 and gap < 0.5:
                needs_join = True
            elif cur_len + nxt_len <= 20 and gap < 0.25:
                needs_join = True
                
            if needs_join and (cur_len + nxt_len <= 24):
                sep = ' ' if (cur_t and cur_t[-1] not in '，、：:') else ''
                combined_t = clean_text(cur_t + sep + nxt_t, corrections)
                cur['text'] = combined_t
                cur['end'] = nxt['end']
                merged.append(cur)
                i += 2
                continue
                
        merged.append(cur)
        i += 1
        
    # 拆分過長行（> 24 字元）
    final_subs = []
    for item in merged:
        txt = item["text"]
        c_len = count_cjk(txt)
        t_start = item["start"]
        t_end = item["end"]
        duration = t_end - t_start
        
        if c_len > 24:
            delims = [m.start() for m in re.finditer(r'[，、\s]', txt)]
            if not delims:
                delims = [m.end() for m in re.finditer(r'(因為|所以|但是|而且|也就是|如果|這時候|接下來)', txt)]
            if delims:
                mid = len(txt) / 2.0
                best_split = min(delims, key=lambda d: abs(d - mid))
                part1 = clean_text(txt[:best_split], corrections)
                part2 = clean_text(txt[best_split:], corrections)
                len1 = count_cjk(part1)
                len2 = count_cjk(part2)
                if len1 > 0 and len2 > 0:
                    t_mid = t_start + duration * (len1 / (len1 + len2))
                    final_subs.append({"start": t_start, "end": t_mid, "text": part1})
                    final_subs.append({"start": t_mid, "end": t_end, "text": part2})
                    continue
        final_subs.append(item)
        
    # 時間戳防重疊修復
    for j in range(len(final_subs) - 1):
        if final_subs[j]['end'] > final_subs[j+1]['start']:
            final_subs[j]['end'] = final_subs[j+1]['start']
            
    # 寫入 SRT
    out_lines = []
    for idx, e in enumerate(final_subs, 1):
        s_str = sec_to_time(e['start'])
        e_str = sec_to_time(e['end'])
        out_lines.append(f"{idx}\n{s_str} --> {e_str}\n{e['text']}\n")
        
    srt_path.write_text("\n".join(out_lines), encoding='utf-8')
    lens = [count_cjk(e['text']) for e in final_subs]
    avg_l = sum(lens) / len(lens) if lens else 0
    max_l = max(lens) if lens else 0
    min_l = min(lens) if lens else 0
    print(f"✅ [精修完成] {srt_path.name}: 共 {len(final_subs)} 行 (最小 {min_l} 字, 平均 {avg_l:.1f} 字, 最大 {max_l} 字)")

def main():
    refine_file(PODCAST_SRT, PODCAST_CORRECTIONS)

if __name__ == '__main__':
    main()
