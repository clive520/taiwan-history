# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"d:\Antigravity\科技歷史\臺灣史\js\data.js")
c = p.read_text(encoding="utf-8")

old_snippet = """    "status": "planned",
    "file": "第15章_臺灣人的臺灣_文化協會議會設置請願運動與霧社事件的警鐘.md",
    "videoSchedule": "2026-11-09 17:30",
    "podcastSchedule": "2026-11-09 19:30"
  },
  {
    "id": "ch16","""

new_snippet = """    "status": "published",
    "bannerImage": "assets/images/ch15/ch15_hero_banner.jpg",
    "youtube": "7_yMQ5iIR0E",
    "podcastYoutube": "M3FS3qXw3TM",
    "notebooklm": "https://notebook.google.com/notebook/89f33278-4573-4715-9de5-c5fb6c241c05",
    "audioFile": "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/ch15_podcast_deepdive.m4a",
    "srtFile": "第15章_臺灣人的臺灣_說明影片.srt",
    "file": "第15章_臺灣人的臺灣_文化協會議會設置請願運動與霧社事件的警鐘.md",
    "videoSchedule": "2026-11-09 17:30",
    "podcastSchedule": "2026-11-09 19:30"
  },
  {
    "id": "ch16","""

# 統一換行符號
c_norm = c.replace("\r\n", "\n")
if old_snippet in c_norm:
    c_norm = c_norm.replace(old_snippet, new_snippet)
    p.write_text(c_norm, encoding="utf-8")
    print("SUCCESS: data.js updated correctly!")
else:
    print("ERROR: old_snippet not found")
