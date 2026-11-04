# -*- coding: utf-8 -*-
"""
第 15 章 說明影片與雙人對談 SRT 全面自然語意與錯字精修器
"""
import sys
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH15_DIR = BASE_DIR / "05_日治時期的統治轉型與抗爭"

VIDEO_SRT = CH15_DIR / "第15章_臺灣人的臺灣_說明影片.srt"
PODCAST_SRT = CH15_DIR / "第15章_臺灣人的臺灣_雙人對談.srt"

CORRECTIONS = [
    # 專有名詞與特定勘誤
    (r"浴血列槍", "浴血獵槍"),
    (r"西萊安事件", "西來庵事件"),
    (r"武裝抗議挫敗", "武裝抗日挫敗"),
    (r"撕裂與充足的十字路口", "撕裂與重組的十字路口"),
    (r"總統府甚至發明", "總督府甚至發明"),
    (r"如果總統府倒台", "如果總督府倒臺"),
    (r"總統府", "總督府"),
    (r"蔣[偉偉衛位]水", "蔣渭水"),
    (r"林[現憲]堂", "林獻堂"),
    (r"蔡培[夥貨獲火]", "蔡培火"),
    (r"林[程承成]祿", "林呈祿"),
    (r"蔡[會慧]如", "蔡惠如"),
    (r"莫[納那]魯[島島道]", "莫那·魯道"),
    (r"莫那魯道", "莫那·魯道"),
    (r"達多[莫納]那", "達多·莫那"),
    (r"達多莫那", "達多·莫那"),
    (r"花[剛岡]一郎", "花岡一郎"),
    (r"花[剛岡]二郎", "花岡二郎"),
    (r"佐久間左馬[態太]", "佐久間左馬太"),
    (r"吉村克[已己]", "吉村克己"),
    (r"石塚英[藏藏]", "石塚英藏"),
    (r"人見[次治]郎", "人見次郎"),
    (r"大[安案]醫院", "大安醫院"),
    (r"臨床講[意義]", "臨床講義"),
    (r"[知智]識營養不良[症政]", "智識營養不良症"),
    (r"美[泰台臺]團", "美臺團"),
    (r"致警事件", "治警事件"),
    (r"置警事件", "治警事件"),
    (r"自警事件", "治警事件"),
    (r"憶難忘", "意難忘"),
    (r"理[番蕃]政策", "理蕃政策"),
    (r"五年理[番蕃]計[畫劃]", "五年理蕃計畫"),
    (r"[愛隘]勇線", "隘勇線"),
    (r"賽德[客克]族", "賽德克族"),
    (r"馬[荷赫]坡社", "馬赫坡社"),
    (r"和歌社", "荷歌社"),
    (r"波阿[倫崙]社", "波阿崙社"),
    (r"三氯硝基甲[烷皖]", "三氯硝基甲烷"),
    (r"[靡糜]爛性毒氣", "糜爛性毒氣"),
    (r"[穿川]中島", "川中島"),
    (r"[青清]流部落", "清流部落"),
    (r"味方[番蕃]", "味方蕃"),
    (r"[鯨擎黥]面", "黥面"),
    (r"誤社事件", "霧社事件"),
    (r"大正民[主竹]", "大正民主"),
    (r"六三法[撤徹]廢", "六三法撤廢"),
    (r"內地延長[主竹]義", "內地延長主義"),
    (r"靜修女學[校堂]", "靜修女學校"),
    (r"臺灣[民明]報", "臺灣民報"),
    (r"臺灣工友總[聯連]盟", "臺灣工友總聯盟"),
    (r"彩虹[橋喬]", "彩虹橋"),
    (r"哈[卡考]烏圖克斯", "Hakaw Utux"),
    (r"哈卡烏圖克斯", "Hakaw Utux"),
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
