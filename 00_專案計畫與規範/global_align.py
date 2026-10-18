# -*- coding: utf-8 -*-
"""
全局序列對齊演算法 (Global Sequence Matcher)
使用 difflib.SequenceMatcher 將精確修訂後的語意字幕流與 Whisper 語音字符流進行全域單調對齊
"""
import json
import re
import difflib
from ch01_subtitles_script import ALL_LINES

with open("01_史前文明與南島之源/whisper_words_ch01_video.json", "r", encoding="utf-8") as f:
    data = json.load(f)

words = data["words"]

# 1. 建立 Whisper 字符時間戳流
clean_stream = []
for wi, w in enumerate(words):
    raw = w["word"].strip()
    clean_w = re.sub(r"[,.?!;:，。？！；：、~'\" \(\)\[\]【】《》「」『』—]", "", raw)
    if not clean_w:
        continue
    w_start = w["start"]
    w_end = w["end"]
    w_dur = max(0.01, w_end - w_start)
    c_dur = w_dur / len(clean_w)
    for ci, ch in enumerate(clean_w):
        clean_stream.append({
            "char": ch,
            "start": w_start + ci * c_dur,
            "end": w_start + (ci + 1) * c_dur,
            "word_idx": wi
        })

stream_text = "".join(x["char"] for x in clean_stream)

# 2. 建立所有字幕行的乾淨字符與行映射
line_chars = [] # [(char, line_idx, is_start, is_end)]
clean_lines = []
for li, line in enumerate(ALL_LINES):
    # 去除章節提示符號但保留文字
    c_line = re.sub(r"[,.?!;:，。？！；：、~'\" \(\)\[\]【】《》「」『』—]", "", line)
    clean_lines.append(c_line)
    for ci, ch in enumerate(c_line):
        line_chars.append({
            "char": ch,
            "line_idx": li,
            "is_start": (ci == 0),
            "is_end": (ci == len(c_line) - 1),
            "char_in_line": ci,
            "line_len": len(c_line)
        })

sub_text = "".join(x["char"] for x in line_chars)

print(f"Whisper Stream Text Length: {len(stream_text)}")
print(f"Subtitle Text Length:       {len(sub_text)}")

# 3. 使用 SequenceMatcher 進行全域對齊
matcher = difflib.SequenceMatcher(None, sub_text, stream_text)
matching_blocks = matcher.get_matching_blocks()
print(f"Found {len(matching_blocks)} matching blocks.")

# 建立 sub_text 字符到 stream_text 字符的映射
sub_to_stream = {}
for block in matching_blocks:
    for offset in range(block.size):
        sub_to_stream[block.a + offset] = block.b + offset

# 4. 為每一行字幕計算 start_time 與 end_time
line_spans = {}
char_cursor = 0
for li, line in enumerate(ALL_LINES):
    c_len = len(clean_lines[li])
    matched_stream_indices = []
    for ci in range(char_cursor, char_cursor + c_len):
        if ci in sub_to_stream:
            matched_stream_indices.append(sub_to_stream[ci])
    
    char_cursor += c_len
    line_spans[li] = matched_stream_indices

# 填補未匹配邊界的平滑時間戳
srt_entries = []
prev_end = 0.0

for li, line in enumerate(ALL_LINES):
    indices = line_spans[li]
    if indices:
        s_time = clean_stream[min(indices)]["start"]
        e_time = clean_stream[max(indices)]["end"]
    else:
        s_time = prev_end
        e_time = s_time + 2.0
    
    # 確保時間單調遞增且不回退
    if s_time < prev_end:
        s_time = prev_end
    if e_time <= s_time:
        e_time = s_time + 1.2
    
    prev_end = e_time
    srt_entries.append((li + 1, s_time, e_time, line))

with open("00_專案計畫與規範/test_aligned_srt.txt", "w", encoding="utf-8") as out:
    for num, s, e, text in srt_entries:
        out.write(f"[{num:03d}] {s:6.2f} -> {e:6.2f} : {text}\n")

print(f"Successfully generated {len(srt_entries)} aligned subtitle entries!")
