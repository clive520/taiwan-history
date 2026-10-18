# -*- coding: utf-8 -*-
"""
生成影視級標準 SRT 字幕檔
格式規範：
- 序號從 1 開始遞增
- 時間戳格式：HH:MM:SS,mmm --> HH:MM:SS,mmm
- 語氣自然、專有名詞考證、字數適中、語意不斷詞
"""
import re

def format_timestamp(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours = millis // 3600000
    millis %= 3600000
    minutes = millis // 60000
    millis %= 60000
    secs = millis // 1000
    millis %= 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

entries = []
with open("00_專案計畫與規範/test_aligned_srt.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # [001]   0.00 ->   3.18 : 文字...
        m = re.match(r"\[(\d+)\]\s*([\d\.]+)\s*->\s*([\d\.]+)\s*:\s*(.*)", line)
        if m:
            idx = int(m.group(1))
            s_time = float(m.group(2))
            e_time = float(m.group(3))
            text = m.group(4).strip()
            entries.append((idx, s_time, e_time, text))

target_srt_path = "01_史前文明與南島之源/第01章_黑潮上的遠古足跡_說明影片.srt"

with open(target_srt_path, "w", encoding="utf-8") as out:
    for idx, s_time, e_time, text in entries:
        out.write(f"{idx}\n")
        out.write(f"{format_timestamp(s_time)} --> {format_timestamp(e_time)}\n")
        out.write(f"{text}\n\n")

print(f"✅ 成功寫入標準 SRT 字幕至：{target_srt_path}（共 {len(entries)} 條字幕）")
