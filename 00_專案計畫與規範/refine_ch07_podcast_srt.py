# -*- coding: utf-8 -*-
import sys
import re
import json
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

srt_path = Path(r"d:\Antigravity\科技歷史\臺灣史\03_明鄭東寧與海上孤忠\第07章_決戰大員九個月_雙人對談.srt")
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
            parsed.append({
                "idx": idx,
                "start_str": m.group(1),
                "end_str": m.group(2),
                "text": text
            })

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

new_subs = []
for item in parsed:
    txt = item["text"]
    c_len = count_cjk(txt)
    t_start = parse_time(item["start_str"])
    t_end = parse_time(item["end_str"])
    duration = t_end - t_start
    
    if c_len > 22 and ('，' in txt or '、' in txt or ' ' in txt):
        # 尋找最接近中點的標點切分
        delims = [m.start() for m in re.finditer(r'[，、\s]', txt)]
        if delims:
            mid = len(txt) / 2.0
            best_split = min(delims, key=lambda d: abs(d - mid))
            part1 = txt[:best_split].strip(" ，、")
            part2 = txt[best_split+1:].strip(" ，、")
            
            len1 = count_cjk(part1)
            len2 = count_cjk(part2)
            if len1 > 0 and len2 > 0:
                t_mid = t_start + duration * (len1 / (len1 + len2))
                new_subs.append({
                    "start": t_start,
                    "end": t_mid,
                    "text": part1
                })
                new_subs.append({
                    "start": t_mid,
                    "end": t_end,
                    "text": part2
                })
                continue
                
    new_subs.append({
        "start": t_start,
        "end": t_end,
        "text": txt
    })

# 時間防重疊修正
for i in range(len(new_subs)-1):
    if new_subs[i]["end"] > new_subs[i+1]["start"]:
        new_subs[i]["end"] = new_subs[i+1]["start"]

with open(srt_path, "w", encoding="utf-8") as f:
    for idx, s in enumerate(new_subs, 1):
        f.write(f"{idx}\n{format_time(s['start'])} --> {format_time(s['end'])}\n{s['text']}\n\n")

lens = [count_cjk(s['text']) for s in new_subs]
avg_l = sum(lens)/len(lens)
max_l = max(lens)
long_cnt = sum(1 for l in lens if l > 24)
print(f"優化完成！總行數: {len(new_subs)}, 平均字數: {avg_l:.1f}, 最大字數: {max_l}, 超過24字數: {long_cnt}")
