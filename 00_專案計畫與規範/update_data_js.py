# -*- coding: utf-8 -*-
import sys
import re
from pathlib import Path

p = Path(r"d:\Antigravity\科技歷史\臺灣史\js\data.js")
c = p.read_text(encoding='utf-8')

pattern = r'"status":\s*"planned",\s*"file":\s*"第14章_現代化骨架與殖民之刃_縱貫鐵路嘉南大圳與後藤新平的科學統治\.md",'
replacement = '''"status": "published",
    "bannerImage": "assets/images/ch14/ch14_hero_banner.jpg",
    "youtube": "ALfbszmd7VI",
    "podcastYoutube": "GEcZQh1kJqw",
    "notebooklm": "https://notebook.google.com/notebook/4a8b0145-f20d-41f8-a94a-022fc220f854",
    "audioFile": "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/ch14_podcast_deepdive.m4a",
    "srtFile": "第14章_現代化骨架與殖民之刃_說明影片.srt",
    "file": "第14章_現代化骨架與殖民之刃_縱貫鐵路嘉南大圳與後藤新平的科學統治.md",'''

new_c, count = re.subn(pattern, replacement, c)
if count > 0:
    p.write_text(new_c, encoding='utf-8')
    print(f"✅ Successfully updated js/data.js (replaced {count} occurrences)!")
else:
    print("❌ Pattern not found in js/data.js")
