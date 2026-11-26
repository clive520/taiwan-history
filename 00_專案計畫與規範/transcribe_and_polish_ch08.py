# -*- coding: utf-8 -*-
"""
《島嶼鐵道物語》第 08 章 Faster-Whisper 語音轉錄與自然呼吸律精修腳本
- 使用 Faster-Whisper medium 模型進行單字級時間戳轉錄
- 依據自然語音呼吸停頓與標點進行斷句（8~16字，絕不腰斬詞彙）
- 套用《島嶼鐵道物語》第 08 章專有名詞字典與同音錯別字精修
- 輸出標準 UTF-8 with BOM SRT 字幕檔
"""
import sys
import os
import json
import time
import re
from pathlib import Path
import opencc
from faster_whisper import WhisperModel

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
RAIL_DIR = BASE_DIR / "島嶼鐵道物語" / "02_高山森林與產業支線"

cc = opencc.OpenCC('s2twp')

CH08_PROMPT = (
    "島嶼鐵道物語, 集集支線, 集集線, 集集車站, 濁水溪, 二水車站, 源泉, 濁水, 龍泉, 水里, 水裡坑, "
    "車埕, 外車埕, 門牌潭, 大觀發電廠, 武界壩, 武界引水隧道, 日月潭水力發電, 臺灣電力株式會社, "
    "高木友枝, 松木幹一郎, 佩爾頓式水輪機, 1,067毫米, 綠色隧道, 樟腦專賣局, 集集山蕉, "
    "振昌木業, 孫海, 丹大林區, 丹大林道, 貯木池, 鳶口, 紅檜, 扁柏, 山中小台北, "
    "雨淋板, 榫卯, 追掛大栓繼, 解體重組, 車籠埔斷層, 921大地震, 九二一集集大地震"
)

CORRECTIONS = [
    (r"[臺台]灣", "臺灣"),
    (r"全[臺台]", "全臺"),
    (r"在[臺台]", "在臺"),
    (r"[臺台]鐵", "臺鐵"),
    (r"[臺台]電", "臺電"),
    (r"[臺台]北", "臺北"),
    (r"集集[支枝]線", "集集支線"),
    (r"集集[站站]", "集集站"),
    (r"[濁著卓]水溪", "濁水溪"),
    (r"[濁著卓]水站", "濁水站"),
    (r"二水[車社]站", "二水車站"),
    (r"外車[呈程城]", "外車埕"),
    (r"車[呈程城]", "車埕"),
    (r"水[裡里]坑", "水裡坑"),
    (r"門[牌排]潭", "門牌潭"),
    (r"大[觀官關]發電[廠場]", "大觀發電廠"),
    (r"武[界介屆]壩", "武界壩"),
    (r"武[界介屆]引水隧道", "武界引水隧道"),
    (r"水[社色射]大山", "水社大山"),
    (r"高木友[枝支知]", "高木友枝"),
    (r"松木幹[一億]郎", "松木幹一郎"),
    (r"振[昌倉]木業", "振昌木業"),
    (r"[孫損]海", "孫海"),
    (r"丹大[林琳]區", "丹大林區"),
    (r"丹大[林琳]道", "丹大林道"),
    (r"[貯儲注]木池", "貯木池"),
    (r"[鳶淵冤]口", "鳶口"),
    (r"紅[檜會繪]", "紅檜"),
    (r"[扁邊]柏", "扁柏"),
    (r"雨[淋林鄰]板", "雨淋板"),
    (r"[榫損筍][卯卵]", "榫卯"),
    (r"追掛大栓[繼計記]", "追掛大栓繼"),
    (r"解[體替][重從]組", "解體重組"),
    (r"車籠[埔鋪浦]斷層", "車籠埔斷層"),
    (r"佩爾頓[式室]", "佩爾頓式"),
    (r"[樟張章]腦", "樟腦"),
    (r"山[蕉焦焦]", "山蕉"),
    (r"賽璐[珞洛落]", "賽璐珞"),
    (r"蛇[籠龍隆]", "蛇籠"),
    (r"1067[公毫][釐厘分米]", "1067毫米"),
    (r"一千零六十七", "1067"),
]

def apply_corrections(text):
    t = cc.convert(text)
    for pat, rep in CORRECTIONS:
        t = re.sub(pat, rep, t)
    return t

def format_timestamp(seconds):
    ms = int(round(seconds * 1000))
    hrs = ms // 3600000
    ms %= 3600000
    mins = ms // 60000
    ms %= 60000
    secs = ms // 1000
    ms %= 1000
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"

def count_cjk(text):
    return len(re.sub(r'[\s，。！？、：；「」『』（）(),.!?:;"\'-]', '', text))

def split_long_sentence(text, words, start_t, end_t, max_chars=17):
    """若單一呼吸句超過 18 字，依單字時間戳在自然逗號或詞彙邊界切分，絕不腰斬詞彙"""
    if count_cjk(text) <= max_chars or not words:
        return [{'start': start_t, 'end': end_t, 'text': text}]
    
    parts = re.split(r'([，、：；！？])', text)
    clauses = []
    buf = ""
    for p in parts:
        buf += p
        if p in '，、：；！？':
            if buf.strip():
                clauses.append(buf.strip())
            buf = ""
    if buf.strip():
        clauses.append(buf.strip())
    
    if len(clauses) > 1:
        total_c = sum(count_cjk(c) for c in clauses) or 1
        res = []
        cur_t = start_t
        dur = max(0.2, end_t - start_t)
        acc = ""
        acc_start = cur_t
        for i, cl in enumerate(clauses):
            cl_c = count_cjk(cl)
            cl_dur = dur * (cl_c / total_c)
            if acc and count_cjk(acc) + cl_c > max_chars:
                res.append({'start': acc_start, 'end': cur_t, 'text': acc.rstrip('，、：；')})
                acc = cl
                acc_start = cur_t
            else:
                acc = acc + cl if acc else cl
            cur_t += cl_dur
        if acc:
            res.append({'start': acc_start, 'end': end_t, 'text': acc.rstrip('，、：；')})
        return res
    
    mid = len(words) // 2
    w_left = "".join(w['word'] for w in words[:mid])
    w_right = "".join(w['word'] for w in words[mid:])
    t_mid = words[mid]['start'] if mid < len(words) else (start_t + end_t) / 2
    return [
        {'start': start_t, 'end': t_mid, 'text': apply_corrections(w_left).strip('，、。')},
        {'start': t_mid, 'end': end_t, 'text': apply_corrections(w_right).strip('，、。')}
    ]

def process_audio_to_srt(model, media_path, srt_path):
    print(f"\n🎙️ 開始轉錄：{media_path.name}")
    t0 = time.time()
    segments, info = model.transcribe(
        str(media_path),
        language="zh",
        initial_prompt=CH08_PROMPT,
        word_timestamps=True,
        beam_size=2,
        vad_filter=True
    )
    print(f"   音訊長度：{info.duration:.1f} 秒")
    
    raw_subs = []
    for seg in segments:
        txt = apply_corrections(seg.text.strip())
        if not txt:
            continue
        words = []
        if seg.words:
            for w in seg.words:
                words.append({'word': w.word, 'start': w.start, 'end': w.end})
        pieces = split_long_sentence(txt, words, seg.start, seg.end, max_chars=17)
        for p in pieces:
            p['text'] = re.sub(r'[。．]+$', '', p['text'].strip())
            if p['text']:
                raw_subs.append(p)
                
    # 合併過短的碎片（如 <= 3 字且間隔 < 0.30s）
    merged = []
    for item in raw_subs:
        if not merged:
            merged.append(item)
            continue
        prev = merged[-1]
        gap = item['start'] - prev['end']
        if (count_cjk(prev['text']) <= 3 or count_cjk(item['text']) <= 3) and gap < 0.30 and (count_cjk(prev['text']) + count_cjk(item['text']) <= 16):
            if not prev['text'].endswith(('？', '！', '?', '!')):
                prev['text'] = prev['text'] + '，' + item['text']
                prev['end'] = item['end']
                continue
        merged.append(item)
        
    for i in range(len(merged) - 1):
        if merged[i]['end'] > merged[i+1]['start']:
            merged[i]['end'] = merged[i+1]['start']
            
    with open(srt_path, 'w', encoding='utf-8-sig') as f:
        for idx, sub in enumerate(merged, 1):
            f.write(f"{idx}\n{format_timestamp(sub['start'])} --> {format_timestamp(sub['end'])}\n{sub['text']}\n\n")
            
    # 同步一份至根目錄方便備份查閱
    root_srt = BASE_DIR / srt_path.name
    root_srt.write_text(srt_path.read_text(encoding='utf-8-sig'), encoding='utf-8-sig')
    print(f"   ✅ 完成轉錄與精修 ({time.time()-t0:.1f}s)：{srt_path.name} 共 {len(merged)} 條字幕")

def main():
    vid_mp4 = RAIL_DIR / "第08章_樟腦巨木與濁水溪的迴音_說明影片.mp4"
    pod_m4a = RAIL_DIR / "第08章_樟腦巨木與濁水溪的迴音_雙人對談.m4a"
    vid_srt = RAIL_DIR / "第08章_樟腦巨木與濁水溪的迴音_說明影片.srt"
    pod_srt = RAIL_DIR / "第08章_樟腦巨木與濁水溪的迴音_雙人對談.srt"
    
    print("⏳ 載入 Faster-Whisper medium 模型...")
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    
    if vid_mp4.exists():
        process_audio_to_srt(model, vid_mp4, vid_srt)
    else:
        print(f"⚠️ 找不到說明影片：{vid_mp4}")
        
    if pod_m4a.exists():
        process_audio_to_srt(model, pod_m4a, pod_srt)
    else:
        print(f"⚠️ 找不到對談音訊：{pod_m4a}")

if __name__ == "__main__":
    main()
