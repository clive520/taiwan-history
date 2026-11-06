# -*- coding: utf-8 -*-
"""
第 16 章 說明影片與雙人對談 SRT 全面自然語意與錯字精修器
"""
import sys
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH16_DIR = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇"

VIDEO_SRT = CH16_DIR / "第16章_時代巨變與傷痕記憶_說明影片.srt"
PODCAST_SRT = CH16_DIR / "第16章_時代巨變與傷痕記憶_雙人對談.srt"

CORRECTIONS = [
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
    (r"陳[移宜]", "陳儀"),
    (r"葛[鏡敬]恩", "葛敬恩"),
    (r"柯遠[分芬]", "柯遠芬"),
    (r"彭孟[集緝]", "彭孟緝"),
    (r"彭夢緝", "彭孟緝"),
    (r"湯[德得][章彰]", "湯德章"),
    (r"陳[新心薪]", "陳炘"),
    (r"林茂[深盛生]", "林茂生"),
    (r"潘木[知之枝]", "潘木枝"),
    (r"王添[燈丁灯]", "王添灯"),
    (r"吳鴻[齊祺麒]", "吳鴻麒"),
    (r"施江[男南]", "施江南"),
    (r"阮[照朝]日", "阮朝日"),
    (r"柯[奇旗]化", "柯旗化"),
    (r"雷[政鎮震]", "雷震"),
    (r"殷海[廣光]", "殷海光"),
    (r"[伯白]楊", "柏楊"),
    (r"傅[思斯]年", "傅斯年"),
    (r"黃榮[璨燦]", "黃榮燦"),
    (r"天馬茶[坊房]", "天馬茶房"),
    (r"林江[麥妹邁]", "林江邁"),
    (r"傅學[同通]", "傅學通"),
    (r"陳文[西溪]", "陳文溪"),
    (r"二二八處理[委為]員會", "二二八處理委員會"),
    (r"三十二條[處處]理大綱", "三十二條處理大綱"),
    (r"21師", "二十一師"),
    (r"大[正政]公園", "大正公園"),
    (r"大東信[託托]", "大東信託"),
    (r"大公企[業業]", "大公企業"),
    (r"懲治叛[亂亂]條例", "懲治叛亂條例"),
    (r"2條1", "二條一"),
    (r"檢肅匪[諜諜]條例", "檢肅匪諜條例"),
    (r"新生訓[導導]處", "新生訓導處"),
    (r"綠[洲洲]山莊", "綠洲山莊"),
    (r"泰[源元]監獄", "泰源監獄"),
    (r"第十三中[隊隊]", "第十三中隊"),
    (r"新英文[法發]", "新英文法"),
    (r"自由中[國國]", "自由中國"),
    (r"中國民主[黨黨]", "中國民主黨"),
    (r"大力水[手手]", "大力水手"),
    (r"馬場[町丁]", "馬場町"),
    (r"四六事[件件]", "四六事件"),
    (r"四萬[換喚]一[塊元]", "四萬換一塊"),
    (r"狗去豬[來來]", "狗去豬來"),
    (r"[簞簞]食壺[漿漿]", "簞食壺漿"),
    (r"抓[耙把]仔", "抓耙仔"),
    (r"應即槍[決決]可也", "應即槍決可也"),
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
    if not srt_path.exists():
        print(f"[WARN] 檔案不存在: {srt_path}")
        return 0
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
    return len(final_subs)

def main():
    l_pod = refine_file(PODCAST_SRT, CORRECTIONS)
    l_vid = refine_file(VIDEO_SRT, CORRECTIONS)
    return l_vid, l_pod

if __name__ == '__main__':
    main()
