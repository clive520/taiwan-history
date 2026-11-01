# -*- coding: utf-8 -*-
import sys
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
SRT_PATH = BASE_DIR / "05_日治時期的統治轉型與抗爭/第14章_現代化骨架與殖民之刃_說明影片.srt"

CORRECTIONS = [
    # 專有名詞與特定勘誤
    (r"成童代價", "沉重代價"),
    (r"血裂", "血淚"),
    (r"現代化外溢", "現代化外衣"),
    (r"虐擊", "瘧疾"),
    (r"孽急", "瘧疾"),
    (r"臺灣脈雀論", "臺灣賣卻論"),
    (r"把臺灣脈給", "把臺灣賣給"),
    (r"兒玉元太郎", "兒玉源太郎"),
    (r"比目語", "比目魚"),
    (r"精密地基圖", "精密地籍圖"),
    (r"一田二足體制", "一田二主體制"),
    (r"一田二足", "一田二主"),
    (r"客稅田地", "課稅田地"),
    (r"《臺灣司法》", "《臺灣私法》"),
    (r"《藩族慣習調查報告書》", "《蕃族慣習調查報告書》"),
    (r"藩族慣習", "蕃族慣習"),
    (r"摩收原住民山林地", "沒收原住民山林地"),
    (r"最鋒利的發力武器", "最鋒利的法律武器"),
    (r"國事調查", "國勢調查"),
    (r"午夜臨時", "午夜零時"),
    (r"80萬產主女性", "80萬纏足女性"),
    (r"產主女性", "纏足女性"),
    (r"鴉片西施者", "鴉片吸食者"),
    (r"常谷川經界", "長谷川謹介"),
    (r"長谷川經界", "長谷川謹介"),
    (r"穿越賢軍的舊山線", "穿越險峻的舊山線"),
    (r"賢軍", "險峻"),
    (r"濁水心", "濁水溪"),
    (r"流沙天線", "流沙天塹"),
    (r"生桶氣壓沉香工法", "深筒氣壓沉箱工法"),
    (r"沉香工法", "沉箱工法"),
    (r"臺中問員", "臺中公園"),
    (r"問員", "公園"),
    (r"湖興亭", "湖心亭"),
    (r"茶與梅", "茶與煤"),
    (r"嚴減化", "鹽鹼化"),
    (r"八田羽衣", "八田與一"),
    (r"八田與衣", "八田與一"),
    (r"炭芳", "坍方"),
    (r"工人和祭司", "工人和技師"),
    (r"年輕祭司", "年輕技師"),
    (r"半水利天主式工法", "半水力填築式工法"),
    (r"半水利天主式", "半水力填築式"),
    (r"永遠藏綿", "永遠長眠"),
    (r"截水跟排水渠道", "給水跟排水渠道"),
    (r"吃到三分之一圈", "赤道三分之一圈"),
    (r"三年輪座給水法", "三年輪作給水法"),
    (r"三年輪座", "三年輪作"),
    (r"資湯會社", "製糖會社"),
    (r"自割農", "自耕農"),
    (r"任人宰割的電農", "任人宰割的佃農"),
    (r"電農", "佃農"),
    (r"米糖香客", "米糖相剋"),
    (r"三井、三林", "三井、三菱"),
    (r"第一夯種甘蔗與會社綁", "第一憨種甘蔗予會社磅"),
    (r"這農種出來的甘蔗", "蔗農種出來的甘蔗"),
    (r"這農", "蔗農"),
    (r"沒有溢價空間", "沒有議價空間"),
    (r"過曝的時候", "過磅的時候"),
    (r"番薯前", "番薯籤"),
    (r"打動單一市場", "打通單一市場"),
    (r"惠色資本", "會社資本"),
    (r"彰化二零", "彰化二林"),
    (r"二零浙農事件", "二林蔗農事件"),
    (r"浙農", "蔗農"),
    (r"拿著貶單", "拿著扁擔"),
    (r"貶單", "扁擔"),
    (r"隨後剪輯更是整合", "隨後簡吉更是整合"),
    (r"剪輯更是整合", "簡吉更是整合"),
    (r"有人那條貫通全島的鐵路", "有了那條貫通全島的鐵路"),
    (r"跨地獄串聯", "跨地域串聯"),
    (r"即為關鍵", "極為關鍵"),
    (r"殘酷詐取", "殘酷榨取"),
    (r"水鎮背後", "水圳背後"),
    (r"水鎮", "水圳"),
    (r"鳴客著", "銘刻著"),
    (r"深深鳴記", "深深銘記"),
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
            idx = lines[0]
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

def clean_text(text):
    t = text.strip()
    for pat, rep in CORRECTIONS:
        t = re.sub(pat, rep, t)
    t = re.sub(r'^[，。！？、；：,!?;:]+', '', t)
    t = re.sub(r'[，。、；;,\.]+$', '', t)
    return t

def count_cjk(s):
    return len(re.findall(r'[\u4e00-\u9fff\w]', s))

def refine():
    raw_content = SRT_PATH.read_text(encoding='utf-8')
    entries = parse_srt(raw_content)
    print(f"[*] 讀取原始字幕: {len(entries)} 條")
    
    # 進行錯字校正
    for e in entries:
        e['text'] = clean_text(e['text'])
        e['start'] = time_to_sec(e['start_s'])
        e['end'] = time_to_sec(e['end_s'])
        
    # 自然語意合併過短行 (< 6 字或以介詞結尾者)
    merged = []
    i = 0
    while i < len(entries):
        cur = entries[i]
        cur_t = cur['text']
        cur_len = count_cjk(cur_t)
        
        # 檢查是否需要與下一句合併
        if i + 1 < len(entries):
            nxt = entries[i+1]
            nxt_t = nxt['text']
            nxt_len = count_cjk(nxt_t)
            gap = nxt['start'] - cur['end']
            
            # 若當前句以介詞/連詞結尾，如「隱藏在」、「編撰了」、「打著…旗號」
            needs_join = False
            if re.search(r'(在|了|的|和|與|將|把|以|從|由|向|對|而|但|因為|所以|包括|則是)$', cur_t):
                needs_join = True
            elif cur_len <= 5 and gap < 0.5:
                needs_join = True
            elif cur_len + nxt_len <= 20 and gap < 0.25:
                needs_join = True
                
            if needs_join and (cur_len + nxt_len <= 24):
                # 合併
                sep = ' ' if (cur_t and cur_t[-1] not in '，、：:') else ''
                combined_t = clean_text(cur_t + sep + nxt_t)
                cur['text'] = combined_t
                cur['end'] = nxt['end']
                merged.append(cur)
                i += 2
                continue
                
        merged.append(cur)
        i += 1
        
    # 寫回 SRT
    out_lines = []
    for idx, e in enumerate(merged, 1):
        s_str = sec_to_time(e['start'])
        e_str = sec_to_time(e['end'])
        out_lines.append(f"{idx}\n{s_str} --> {e_str}\n{e['text']}\n")
        
    SRT_PATH.write_text("\n".join(out_lines), encoding='utf-8')
    lens = [count_cjk(e['text']) for e in merged]
    avg_l = sum(lens) / len(lens) if lens else 0
    max_l = max(lens) if lens else 0
    min_l = min(lens) if lens else 0
    print(f"✅ [說明影片字幕精修完成] 共 {len(merged)} 行 (最小 {min_l} 字, 平均 {avg_l:.1f} 字, 最大 {max_l} 字)")

if __name__ == '__main__':
    refine()
