# -*- coding: utf-8 -*-
import sys, io, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = Path('d:/Antigravity/科技歷史/臺灣史')

for fname in [
    '05_日治時期的統治轉型與抗爭/whisper_words_ch13_video.json',
    '05_日治時期的統治轉型與抗爭/whisper_words_ch13_podcast.json',
    '04_清領時代的拓墾烽火與變革/whisper_words_ch12_video.json',
    '04_清領時代的拓墾烽火與變革/whisper_words_ch12_podcast.json',
    '04_清領時代的拓墾烽火與變革/whisper_words_ch11_video.json',
    '04_清領時代的拓墾烽火與變革/whisper_words_ch11_podcast.json',
    '04_清領時代的拓墾烽火與變革/whisper_words_ch10_video.json',
    '04_清領時代的拓墾烽火與變革/whisper_words_ch10_podcast.json',
]:
    with open(base / fname, 'r', encoding='utf-8') as f:
        d = json.load(f)
    segs = d.get('segments', [])
    print(f"=== {Path(fname).name} (Total: {len(segs)}) ===")
    count = 0
    for i, s in enumerate(segs):
        t = s['text'].strip()
        if len(t) <= 3:
            prev_t = segs[i-1]['text'].strip() if i > 0 else ''
            next_t = segs[i+1]['text'].strip() if i < len(segs)-1 else ''
            gap_prev = s['start'] - segs[i-1]['end'] if i > 0 else 999
            gap_next = segs[i+1]['start'] - s['end'] if i < len(segs)-1 else 999
            print(f"   [{i:3d}] [{s['start']:.2f}->{s['end']:.2f}]: \"{t}\" (gap_prev={gap_prev:.2f}s: \"{prev_t}\" | gap_next={gap_next:.2f}s: \"{next_t}\")")
            count += 1
            if count >= 8:
                break
