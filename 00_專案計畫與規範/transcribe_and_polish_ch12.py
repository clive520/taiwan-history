# -*- coding: utf-8 -*-
"""
《島嶼鐵道物語》第 12 章 Faster-Whisper 語音轉錄與自然呼吸律精修腳本
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

CH12_PROMPT = (
    "島嶼鐵道物語, 臺鐵便當, 池上飯包, 池上便當, 經木, 木片便當, 李約典, 李約翰, 林來富, "
    "李陳雲, 月桃葉, 奮起湖便當, 林金坤, 福隆便當, 鄉野便當, 臺鐵餐旅服務總所, "
    "沖茶師, 沖茶生, 鐵路玻璃杯, 玻璃杯蓋, 香片, 烏龍茶, 茶葉蛋, 黑松汽水, 蘋果西打, "
    "八角木片盒, 不銹鋼便當盒, 月台叫賣, 燒ㄟ便當, 池上飯包文化故事館, 鐵路便當節"
)

CORRECTIONS = [
    (r"[臺台]灣", "臺灣"),
    (r"全[臺台]", "全臺"),
    (r"在[臺台]", "在臺"),
    (r"[臺台]鐵", "臺鐵"),
    (r"[臺台]北", "臺北"),
    (r"[臺台]東", "臺東"),
    (r"池[上尚]飯包", "池上飯包"),
    (r"池[上尚]便當", "池上便當"),
    (r"池[上尚]米", "池上米"),
    (r"[經精]木", "經木"),
    (r"李約[典點]", "李約典"),
    (r"李約[漢翰]", "李約翰"),
    (r"林來[富福]", "林來富"),
    (r"奮起[湖胡]便當", "奮起湖便當"),
    (r"[福浮]隆便當", "福隆便當"),
    (r"月桃[葉業]", "月桃葉"),
    (r"[沖衝]茶[師生]", lambda m: "沖茶" + m.group(0)[-1]),
    (r"毛細[孔空]", "毛細孔"),
    (r"維管[束數]", "維管束"),
    (r"雪裡[紅洪]", "雪裡紅"),
    (r"蘿蔔[乾干]", "蘿蔔乾"),
    (r"豆[乾干]", "豆乾"),
    (r"卜[肉右]", "卜肉"),
    (r"叫[賣邁]", "叫賣"),
    (r"扁[擔單]", "扁擔"),
    (r"茶[葉業]蛋", "茶葉蛋"),
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
        initial_prompt=CH12_PROMPT,
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
    vid_mp4 = RAIL_DIR / "第12章_月台上的時代交響_說明影片.mp4"
    pod_m4a = RAIL_DIR / "第12章_月台上的時代交響_雙人對談.m4a"
    vid_srt = RAIL_DIR / "第12章_月台上的時代交響_說明影片.srt"
    pod_srt = RAIL_DIR / "第12章_月台上的時代交響_雙人對談.srt"
    print("⏳ 載入 Faster-Whisper medium 模型...")
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    if vid_mp4.exists() and not vid_srt.exists():
        process_audio_to_srt(model, vid_mp4, vid_srt)
    if pod_m4a.exists() and not pod_srt.exists():
        process_audio_to_srt(model, pod_m4a, pod_srt)

if __name__ == "__main__":
    main()
