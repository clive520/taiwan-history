import re

path1 = r'd:\Antigravity\科技歷史\臺灣史\js\data-food.js'
path2 = r'd:\Antigravity\科技歷史\臺灣史\舌尖上的臺灣\js\data.js'

with open(path1, 'r', encoding='utf-8') as f:
    content = f.read()

old_ch01 = '''  {
    "id": "ch01",
    "chapterNo": "01",
    "period": "indigenous",
    "periodName": "第一篇：山海風土與島嶼原味",
    "periodFolder": "舌尖上的臺灣/01_山海風土與島嶼原味",
    "title": "粟米、野豬與香料火種",
    "subtitle": "南島先民的煙燻、採集與土地智慧",
    "era": "史前文明 – 早期接觸",
    "coordinates": {
      "lat": 22.7135,
      "lng": 120.6548,
      "locationName": "屏東三地門排灣族部落"
    },
    "figures": ["小米", "Cinavu", "馬告", "刺蔥", "小米酒"],
    "summary": "探尋南島先民與島嶼山林的共存滋味，假酸漿葉包裹的醃肉、石板上的山豬油脂與馬告火種。",
    "status": "planned",
    "file": "第01章_粟米野豬與香料火種_南島先民的煙燻採集與土地智慧.md",
    "videoSchedule": "2026-11-16 17:30",
    "podcastSchedule": "2026-11-16 19:30"
  },'''

new_ch01 = '''  {
    "id": "ch01",
    "chapterNo": "01",
    "period": "indigenous",
    "periodName": "第一篇：山海風土與島嶼原味",
    "periodFolder": "舌尖上的臺灣/01_山海風土與島嶼原味",
    "title": "粟米、野豬與香料火種",
    "subtitle": "南島先民的煙燻、採集與土地智慧",
    "era": "史前文明 – 早期接觸",
    "coordinates": {
      "lat": 22.7135,
      "lng": 120.6548,
      "locationName": "屏東三地門排灣族部落"
    },
    "figures": ["小米", "Cinavu", "馬告", "刺蔥", "小米酒"],
    "summary": "探尋南島先民與島嶼山林的共存滋味，假酸漿葉包裹的醃肉、石板上的山豬油脂與馬告火種。",
    "status": "published",
    "bannerImage": "assets/images/food_ch01/food_ch01_hero_banner.jpg",
    "youtube": "tT9wePxt0ZY",
    "podcastYoutube": "r7MVQa5En9A",
    "audioFile": "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/food_ch01_podcast_deepdive.m4a",
    "file": "第01章_粟米野豬與香料火種_南島先民的煙燻採集與土地智慧.md",
    "videoSchedule": "2026-11-13 17:30",
    "podcastSchedule": "2026-11-13 19:30"
  },'''

content = content.replace(old_ch01, new_ch01)

date_map = {
    '02': ('2026-11-14 17:30', '2026-11-14 19:30'),
    '03': ('2026-11-15 17:30', '2026-11-15 19:30'),
    '04': ('2026-11-16 17:30', '2026-11-16 19:30'),
    '05': ('2026-11-17 17:30', '2026-11-17 19:30'),
    '06': ('2026-11-18 17:30', '2026-11-18 19:30'),
    '07': ('2026-11-19 17:30', '2026-11-19 19:30'),
    '08': ('2026-11-20 17:30', '2026-11-20 19:30'),
    '09': ('2026-11-21 17:30', '2026-11-21 19:30'),
    '10': ('2026-11-22 17:30', '2026-11-22 19:30'),
    '11': ('2026-11-23 17:30', '2026-11-23 19:30'),
    '12': ('2026-11-24 17:30', '2026-11-24 19:30'),
    '13': ('2026-11-25 17:30', '2026-11-25 19:30'),
    '14': ('2026-11-26 17:30', '2026-11-26 19:30'),
    '15': ('2026-11-27 17:30', '2026-11-27 19:30'),
}

for ch, (vs, ps) in date_map.items():
    pattern = rf'("chapterNo": "{ch}",[\s\S]*?"videoSchedule": ")[^"]+(",[\s\S]*?"podcastSchedule": ")[^"]+(")'
    content = re.sub(pattern, rf'\g<1>{vs}\g<2>{ps}\g<3>', content)

with open(path1, 'w', encoding='utf-8') as f:
    f.write(content)

with open(path2, 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated data-food.js and 舌尖上的臺灣/js/data.js successfully!')
