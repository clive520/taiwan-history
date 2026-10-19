# -*- coding: utf-8 -*-
import json
import re

path = r"d:\Antigravity\科技歷史\臺灣史\js\data.js"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace ch09 planned block with published
ch09_old_pattern = r'\{\s*"id":\s*"ch09",[\s\S]*?"file":\s*"第09章_澎湖海戰與帝國落幕_施琅水師破浪與東寧王國降清\.md",\s*"videoSchedule":\s*"2026-11-03 17:30",\s*"podcastSchedule":\s*"2026-11-03 19:30"\s*\}'

ch09_new = '''{
    "id": "ch09",
    "chapterNo": "09",
    "period": "tungning",
    "periodName": "第三時期：明鄭東寧與海上孤忠",
    "periodFolder": "03_明鄭東寧與海上孤忠",
    "title": "澎湖海戰與帝國落幕",
    "subtitle": "施琅水師破浪與東寧王國降清",
    "era": "1683 – 1684",
    "coordinates": {
      "lat": 23.5658,
      "lng": 119.5632,
      "locationName": "澎湖媽宮水域與風櫃尾"
    },
    "figures": [
      "施琅 (水師提督)",
      "劉國軒 (武平侯)",
      "鄭克塽 (延平王)",
      "鄭克𡒉 (監國)",
      "康熙帝玄燁",
      "馮錫範",
      "李光地"
    ],
    "summary": "劉國軒與施琅的水師宿命對決、澎湖海戰風向逆轉、東寧降清與康熙朝廷『棄留臺灣』廷議大辯論。",
    "status": "published",
    "bannerImage": "assets/images/ch09/ch09_hero_banner.jpg",
    "youtube": "MFRHdUPsYao",
    "podcastYoutube": "cMvQqIYZCvE",
    "audioFile": "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/ch09_podcast_deepdive.m4a",
    "notebooklm": "https://notebook.google.com/notebook/384ad7a6-8b75-43c6-be97-4407e005ffc1",
    "srtFile": "第09章_澎湖海戰與帝國落幕_說明影片.srt",
    "file": "第09章_澎湖海戰與帝國落幕_施琅水師破浪與東寧王國降清.md",
    "videoSchedule": "2026-11-03 17:30",
    "podcastSchedule": "2026-11-03 19:30"
  }'''

new_text, count = re.subn(ch09_old_pattern, ch09_new, text)
if count == 1:
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_text)
    print("Successfully updated ch09 in data.js!")
else:
    print(f"Error: pattern match count = {count}")
