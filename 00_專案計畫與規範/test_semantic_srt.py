# -*- coding: utf-8 -*-
import sys, io, json, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def count_cjk_chars(text):
    return len(re.findall(r'[\u4e00-\u9fff0-9a-zA-Z]', text))

def test_segment_merging(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    segs = d.get('segments', [])
    
    merged = []
    cur = None
    
    for s in segs:
        txt = s.get('text', '').strip()
        if not txt:
            continue
        start = s['start']
        end = s['end']
        
        if cur is None:
            cur = {'start': start, 'end': end, 'text': txt}
            continue
            
        gap = start - cur['end']
        cur_chars = count_cjk_chars(cur['text'])
        new_chars = count_cjk_chars(txt)
        
        # Decide if we should merge cur and s:
        # Conditions to merge:
        # 1. Total chars <= 22
        # 2. gap < 0.4s (no pause)
        # 3. cur text is very short (<= 4 chars) OR new text <= 4 chars OR (total <= 16 chars and gap < 0.25s)
        should_merge = False
        if cur_chars + new_chars <= 22:
            if cur_chars <= 4 and gap < 0.45:
                should_merge = True
            elif new_chars <= 4 and gap < 0.45:
                should_merge = True
            elif cur_chars + new_chars <= 16 and gap < 0.3:
                should_merge = True
                
        if should_merge:
            sep = ' ' if not cur['text'][-1] in '，、。！？；：,!?' else ''
            cur['text'] = cur['text'] + sep + txt
            cur['end'] = end
        else:
            merged.append(cur)
            cur = {'start': start, 'end': end, 'text': txt}
            
    if cur:
        merged.append(cur)
        
    return merged

if __name__ == '__main__':
    base = Path('d:/Antigravity/科技歷史/臺灣史')
    for label, path in [
        ('Ch13 Video', base / '05_日治時期的統治轉型與抗爭/whisper_words_ch13_video.json'),
        ('Ch13 Podcast', base / '05_日治時期的統治轉型與抗爭/whisper_words_ch13_podcast.json'),
        ('Ch12 Video', base / '04_清領時代的拓墾烽火與變革/whisper_words_ch12_video.json'),
        ('Ch12 Podcast', base / '04_清領時代的拓墾烽火與變革/whisper_words_ch12_podcast.json'),
        ('Ch11 Video', base / '04_清領時代的拓墾烽火與變革/whisper_words_ch11_video.json'),
        ('Ch11 Podcast', base / '04_清領時代的拓墾烽火與變革/whisper_words_ch11_podcast.json'),
        ('Ch10 Video', base / '04_清領時代的拓墾烽火與變革/whisper_words_ch10_video.json'),
        ('Ch10 Podcast', base / '04_清領時代的拓墾烽火與變革/whisper_words_ch10_podcast.json'),
    ]:
        res = test_segment_merging(path)
        lens = [count_cjk_chars(r['text']) for r in res]
        raw_count = len(json.load(open(path, encoding='utf-8'))['segments'])
        print(f"{label}: raw={raw_count}, merged={len(res)}, max_len={max(lens)}, avg_len={sum(lens)/len(lens):.1f}")
        print(f"   Sample 1: [{res[0]['start']:.2f}->{res[0]['end']:.2f}] {res[0]['text']}")
        print(f"   Sample 2: [{res[1]['start']:.2f}->{res[1]['end']:.2f}] {res[1]['text']}")
        print(f"   Sample 3: [{res[2]['start']:.2f}->{res[2]['end']:.2f}] {res[2]['text']}")
        print(f"   Sample 4: [{res[3]['start']:.2f}->{res[3]['end']:.2f}] {res[3]['text']}")
