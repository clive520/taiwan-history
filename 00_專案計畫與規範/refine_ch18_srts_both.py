# -*- coding: utf-8 -*-
"""
第 18 章 說明影片與雙人對談 SRT 全面自然語意與錯字精修器
目標：最小字數 >= 6, 最大字數 <= 24, 自然斷句, 0 破句, 0 錯字
"""
import sys
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH18_DIR = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇"

VIDEO_SRT = CH18_DIR / "第18章_矽島崛起與世界舞台_說明影片.srt"
PODCAST_SRT = CH18_DIR / "第18章_矽島崛起與世界舞台_雙人對談.srt"

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
    (r"孫運[璿旋璇]", "孫運璿"),
    (r"李國[鼎頂]", "李國鼎"),
    (r"潘文[淵源]", "潘文淵"),
    (r"方賢[齊齊]", "方賢齊"),
    (r"費[驊驊]", "費驊"),
    (r"尹仲[容容]", "尹仲容"),
    (r"謝東[閔閔]", "謝東閔"),
    (r"張忠[謀謀]", "張忠謀"),
    (r"史欽[泰泰]", "史欽泰"),
    (r"曾繁[城成]", "曾繁城"),
    (r"曹興[誠誠]", "曹興誠"),
    (r"楊丁[元元]", "楊丁元"),
    (r"劉英[達達]", "劉英達"),
    (r"胡定[華華]", "胡定華"),
    (r"宣明[智智]", "宣明智"),
    (r"施振[榮榮]", "施振榮"),
    (r"童子[賢賢]", "童子賢"),
    (r"郭台[銘銘]", "郭台銘"),
    (r"林百[里里]", "林百里"),
    (r"林本[堅堅]", "林本堅"),
    (r"黃仁[勳勳]", "黃仁勳"),
    (r"蘇姿[丰丰]", "蘇姿丰"),
    (r"蔡明[介介]", "蔡明介"),
    (r"工[研言]院", "工研院"),
    (r"工業技術[研言]究院", "工業技術研究院"),
    (r"小[欣心][欣心]豆漿[店店頭]", "小欣欣豆漿店"),
    (r"雙極[性姓]", "雙極性"),
    (r"積體[電甸]路", "積體電路"),
    (r"矽[島鳥]", "矽島"),
    (r"矽[盾頓]", "矽盾"),
    (r"矽晶[圓圓]", "矽晶圓"),
    (r"晶[圓圓]代工", "晶圓代工"),
    (r"純晶[圓圓]代工", "純晶圓代工"),
    (r"聯華[電甸]子", "聯華電子"),
    (r"聯[電甸]", "聯電"),
    (r"台積[電甸]", "台積電"),
    (r"臺灣積體[電甸]路", "臺灣積體電路"),
    (r"新竹科學[工公]業園區", "新竹科學工業園區"),
    (r"竹[科科]", "竹科"),
    (r"無塵[室市]", "無塵室"),
    (r"浸潤式[微微]影", "浸潤式微影"),
    (r"極紫外[光廣]", "極紫外光"),
    (r"先進[製製]程", "先進製程"),
    (r"摩爾定[律綠]", "摩爾定律"),
    (r"客廳即[工公]廠", "客廳即工廠"),
    (r"加工出口[區嶇]", "加工出口區"),
    (r"前鎮加工[區嶇]", "前鎮加工區"),
    (r"埃[米米]", "埃米"),
    (r"奈[米米]", "奈米"),
    (r"微[米米]", "微米"),
    (r"宏[碁基]", "宏碁"),
    (r"華[碩碩]", "華碩"),
    (r"鴻[海每]", "鴻海"),
    (r"廣[達達]", "廣達"),
    (r"仁[寶寶]", "仁寶"),
    (r"緯[創創]", "緯創"),
    (r"和[碩碩]", "和碩"),
    (r"艾司摩[爾爾]", "艾司摩爾"),
    (r"德州[儀儀]器", "德州儀器"),
    (r"飛利[浦普]", "飛利浦"),
    (r"無晶[圓圓]廠", "無晶圓廠"),
    (r"超純[水誰]", "超純水"),
    (r"去離子[水誰]", "去離子水"),
    (r"蠻長", "滿長"),
    (r"蠻多", "滿多"),
    (r"蠻好", "滿好"),
    (r"蠻大", "滿大"),
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
        
    # 自然語意合併過短行 (< 6 字)
    merged = []
    i = 0
    while i < len(entries):
        cur = entries[i]
        cur_t = cur['text']
        cur_len = count_cjk(cur_t)
        
        # 若當前行為極短行（< 6 字）
        if cur_len < 6:
            # 優先往後合併
            if i + 1 < len(entries):
                nxt = entries[i+1]
                nxt_t = nxt['text']
                comb_len = cur_len + count_cjk(nxt_t)
                if comb_len <= 24:
                    sep = '，' if cur_len >= 3 and count_cjk(nxt_t) >= 4 else ' '
                    nxt['text'] = clean_text(cur_t + sep + nxt_t, corrections)
                    nxt['start'] = cur['start']
                    i += 1
                    continue
            # 若無法往後合併且有前一行，則往前合併
            if merged:
                prev = merged[-1]
                prev_t = prev['text']
                comb_len = count_cjk(prev_t) + cur_len
                if comb_len <= 24:
                    sep = '，' if count_cjk(prev_t) >= 4 and cur_len >= 3 else ' '
                    prev['text'] = clean_text(prev_t + sep + cur_t, corrections)
                    prev['end'] = cur['end']
                    i += 1
                    continue
                    
        merged.append(cur)
        i += 1
        
    # 拆分過長行（> 24 字）
    final_entries = []
    for e in merged:
        txt = e['text']
        c_len = count_cjk(txt)
        dur = e['end'] - e['start']
        
        if c_len > 24:
            delims = [m.start() for m in re.finditer(r'[，、\s]', txt)]
            if not delims:
                delims = [m.end() for m in re.finditer(r'(因為|所以|但是|而且|也就是|如果|這時候|接下來)', txt)]
            if not delims:
                delims = [m.end() for m in re.finditer(r'[在與和]', txt)]
                
            if delims:
                mid = len(txt) / 2.0
                best_split = min(delims, key=lambda d: abs(d - mid))
                p1 = clean_text(txt[:best_split], corrections)
                p2 = clean_text(txt[best_split:], corrections)
            else:
                half = len(txt) // 2
                p1 = clean_text(txt[:half], corrections)
                p2 = clean_text(txt[half:], corrections)
                
            l1 = count_cjk(p1)
            l2 = count_cjk(p2)
            if l1 > 0 and l2 > 0:
                t_mid = e['start'] + dur * (l1 / (l1 + l2))
                final_entries.append({"start": e['start'], "end": t_mid, "text": p1})
                final_entries.append({"start": t_mid, "end": e['end'], "text": p2})
                continue
                
        final_entries.append(e)
        
    # 時間戳防重疊修正
    for j in range(len(final_entries) - 1):
        if final_entries[j]['end'] > final_entries[j+1]['start']:
            final_entries[j]['end'] = final_entries[j+1]['start']
            
    # 統計指標
    lens = [count_cjk(x['text']) for x in final_entries]
    min_l = min(lens) if lens else 0
    max_l = max(lens) if lens else 0
    avg_l = sum(lens) / len(lens) if lens else 0
    
    # 寫入回 SRT
    out_lines = []
    for idx, fe in enumerate(final_entries, 1):
        s_str = sec_to_time(fe['start'])
        e_str = sec_to_time(fe['end'])
        out_lines.append(f"{idx}\n{s_str} --> {e_str}\n{fe['text']}\n")
        
    srt_path.write_text("\n".join(out_lines), encoding='utf-8')
    print(f"✅ 精修完成！行數: {len(final_entries)}, 最小長度: {min_l}, 最大長度: {max_l}, 平均長度: {avg_l:.1f}")
    return len(final_entries)

if __name__ == '__main__':
    v_lines = refine_file(VIDEO_SRT, CORRECTIONS)
    p_lines = refine_file(PODCAST_SRT, CORRECTIONS)
    print(f"\n🎉 雙軌 SRT 全面精修完畢！說明影片: {v_lines} 行, 播客對談: {p_lines} 行")
