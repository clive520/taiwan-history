# -*- coding: utf-8 -*-
"""
《島嶼鐵道物語》第 10 章 Faster-Whisper 語音轉錄與自然呼吸律精修腳本
"""
import sys
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
RAIL_DIR = BASE_DIR / "島嶼鐵道物語" / "03_環島天險與現代提速"

cc = opencc.OpenCC('s2twp')

CH10_PROMPT = (
    "島嶼鐵道物語, 花東線, 臺東線, 花東縱谷, 歐亞板塊, 菲律賓海板塊, 762毫米, 1,067毫米, "
    "東拓工程, 臺東線鐵路拓寬工程, 阿美族, Pangcah, Silamalay, 黃皮仔, 東線光華號, "
    "LDR2300, DR2000, DR2050, 東線小叮噹, 光華號小姐, 璞石閣, 玉里, 里壠, 關山, 池上, "
    "花蓮新站, 舊花蓮站, 溪口河底隧道, 自強隧道, 掃叭隧道, 光復隧道, 三線軌, 1982年6月27日"
)

CORRECTIONS = [
    (r"[臺台]灣", "臺灣"),
    (r"全[臺台]", "全臺"),
    (r"在[臺台]", "在臺"),
    (r"[臺台]鐵", "臺鐵"),
    (r"[臺台]北", "臺北"),
    (r"[臺台]東", "臺東"),
    (r"花東[線線]", "花東線"),
    (r"花東[縱總]谷", "花東縱谷"),
    (r"歐亞板[塊快]", "歐亞板塊"),
    (r"菲律賓海板[塊快]", "菲律賓海板塊"),
    (r"阿美[族足]", "阿美族"),
    (r"黃皮[仔子]", "黃皮仔"),
    (r"白鐵[仔子]", "白鐵仔"),
    (r"藍皮[仔子]", "藍皮仔"),
    (r"東線小[丁叮][噹當]", "東線小叮噹"),
    (r"光華號小[姐解]", "光華號小姐"),
    (r"東[拓托]工程", "東拓工程"),
    (r"三[線線]軌", "三線軌"),
    (r"溪口河[底地]隧道", "溪口河底隧道"),
    (r"自強[隧遂]道", "自強隧道"),
    (r"掃[叭巴]隧道", "掃叭隧道"),
    (r"光復[隧遂]道", "光復隧道"),
    (r"璞石[閣格]", "璞石閣"),
    (r"里[壠龍壟]", "里壠"),
    (r"關[山杉]", "關山"),
    (r"玉[里理]", "玉里"),
    (r"池[上尚]", "池上"),
    (r"[壽受]豐溪", "壽豐溪"),
    (r"秀姑[巒蘭]溪", "秀姑巒溪"),
    (r"卑南[溪西]", "卑南溪"),
    (r"[辮辯變]狀溪流", "辮狀溪流"),
    (r"集團[移遺]住", "集團移住"),
    (r"762[公毫]?[釐厘米]", "762毫米"),
    (r"1067[公毫]?[釐厘米]", "1,067毫米"),
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
        for cl in clauses:
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
        initial_prompt=CH10_PROMPT,
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
        words = [{'word': w.word, 'start': w.start, 'end': w.end} for w in seg.words] if seg.words else []
        for p in split_long_sentence(txt, words, seg.start, seg.end, max_chars=17):
            p['text'] = re.sub(r'[。．]+$', '', p['text'].strip())
            if p['text']:
                raw_subs.append(p)
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
    (BASE_DIR / srt_path.name).write_text(srt_path.read_text(encoding='utf-8-sig'), encoding='utf-8-sig')
    print(f"   ✅ 完成轉錄與精修 ({time.time()-t0:.1f}s)：{srt_path.name} 共 {len(merged)} 條字幕")

def main():
    vid_mp4 = RAIL_DIR / "第10章_縱谷間的窄軌拓寬記_說明影片.mp4"
    pod_m4a = RAIL_DIR / "第10章_縱谷間的窄軌拓寬記_雙人對談.m4a"
    vid_srt = RAIL_DIR / "第10章_縱谷間的窄軌拓寬記_說明影片.srt"
    pod_srt = RAIL_DIR / "第10章_縱谷間的窄軌拓寬記_雙人對談.srt"
    print("⏳ 載入 Faster-Whisper medium 模型...")
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    if vid_mp4.exists() and not vid_srt.exists():
        process_audio_to_srt(model, vid_mp4, vid_srt)
    if pod_m4a.exists() and not pod_srt.exists():
        process_audio_to_srt(model, pod_m4a, pod_srt)

if __name__ == "__main__":
    main()
