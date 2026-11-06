# -*- coding: utf-8 -*-
"""
第 17 章 說明影片與雙人對談 SRT 全面自然語意與錯字精修器
"""
import sys
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH17_DIR = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇"

VIDEO_SRT = CH17_DIR / "第17章_走出戒嚴的民主奇蹟_說明影片.srt"
PODCAST_SRT = CH17_DIR / "第17章_走出戒嚴的民主奇蹟_雙人對談.srt"

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
    (r"美麗[島鳥]", "美麗島"),
    (r"黃信[介界]", "黃信介"),
    (r"施明[德得]", "施明德"),
    (r"姚嘉[文聞]", "姚嘉文"),
    (r"張俊[宏紅]", "張俊宏"),
    (r"林義[雄雄]", "林義雄"),
    (r"呂秀[蓮連]", "呂秀蓮"),
    (r"陳[菊局]", "陳菊"),
    (r"林弘[宣宣]", "林弘宣"),
    (r"鄭南[榕容]", "鄭南榕"),
    (r"詹益[樺華]", "詹益樺"),
    (r"陳文[成誠]", "陳文成"),
    (r"劉宜[良量]", "劉宜良"),
    (r"汪希[苓令]", "汪希苓"),
    (r"竹[聯連]幫", "竹聯幫"),
    (r"陳啟[禮里]", "陳啟禮"),
    (r"李登[輝輝]", "李登輝"),
    (r"彭明[敏敏]", "彭明敏"),
    (r"尤[清清]", "尤清"),
    (r"謝長[廷廷]", "謝長廷"),
    (r"蘇貞[昌昌]", "蘇貞昌"),
    (r"萬年老[國國]代", "萬年老國代"),
    (r"萬年國[會會]", "萬年國會"),
    (r"釋字第?261號", "釋字第261號"),
    (r"野百[合和]", "野百合"),
    (r"三月學[運運]", "三月學運"),
    (r"中山[樓樓]", "中山樓"),
    (r"獨[台臺]會", "獨臺會"),
    (r"廖偉[程成]", "廖偉程"),
    (r"100行動[聯連]盟", "100行動聯盟"),
    (r"李鎮[源淵]", "李鎮源"),
    (r"林山[田填]", "林山田"),
    (r"陳師[孟孟]", "陳師孟"),
    (r"刑法第一百[條條]", "刑法第一百條"),
    (r"懲治叛[亂亂]條例", "懲治叛亂條例"),
    (r"[2二]條[1一]", "二條一"),
    (r"動員戡[亂亂]時期臨時[條條]款", "動員戡亂時期臨時條款"),
    (r"國是[會會議]", "國是會議"),
    (r"大港埔圓[環圈]", "大港埔圓環"),
    (r"東風[ -]?15", "東風-15"),
    (r"尼米[茲茲]號", "尼米茲號"),
    (r"獨立[號號]", "獨立號"),
    (r"航空母[艦艦]", "航空母艦"),
    (r"寧靜革[命命]", "寧靜革命"),
    (r"主權在[民皿]", "主權在民"),
    (r"蠻長", "滿長"),
    (r"蠻多", "滿多"),
    (r"蠻好", "滿好"),
    (r"蠻大", "滿大"),
    (r"38年", "三十八年"),
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
            elif cur_len <= 4 and gap < 0.8:
                needs_join = True
            elif cur_len <= 6 and gap < 0.4:
                needs_join = True
            elif cur_len + nxt_len <= 20 and gap < 0.3:
                needs_join = True
                
            if needs_join and (cur_len + nxt_len <= 24):
                sep = ' ' if (cur_t and cur_t[-1] not in '，、：:') else ''
                combined_t = clean_text(cur_t + sep + nxt_t, corrections)
                cur['text'] = combined_t
                cur['end'] = nxt['end']
                merged.append(cur)
                i += 2
                continue
                
        # 若當前仍極短 (<= 3 字) 且前一行合併後不超過 24 字
        if merged and cur_len <= 3 and (count_cjk(merged[-1]['text']) + cur_len <= 24):
            prev = merged[-1]
            if cur['start'] - prev['end'] < 1.0:
                sep = ' ' if (prev['text'] and prev['text'][-1] not in '，、：:') else ''
                prev['text'] = clean_text(prev['text'] + sep + cur_t, corrections)
                prev['end'] = cur['end']
                i += 1
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
                delims = [m.end() for m in re.finditer(r'(因為|所以|但是|而且|也就是|如果|這時候|接下來|到|從|在)', txt)]
            if not delims:
                delims = [len(txt) // 2]
                
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
