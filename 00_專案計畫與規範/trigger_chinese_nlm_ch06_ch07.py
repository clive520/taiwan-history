# -*- coding: utf-8 -*-
import subprocess
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

CH06_NOTEBOOK = "c5354897-5c84-4a22-81e7-bc4ee2d0585b"
CH07_NOTEBOOK = "c3127091-0bff-4fea-be05-93089cfaeeb1"

ch06_video_focus = """請以繁體中文與生動深刻的歷史解說口吻，詳述1652年郭懷一抗荷事件的歷史全貌。聚焦於荷蘭東印度公司在臺灣實施的殘酷人頭稅、王田地租與贌社制度對漢人農民與拓荒者的殘酷壓榨；生動描繪郭懷一在赤崁油車行歃血為盟、萬名農民以竹竿綁鐮刀發動起義；重現赤崁市街混戰、荷蘭守軍與西拉雅盟軍的火槍長矛夾擊，以及歐汪平原與二層行溪畔的慘烈決戰；最後探討起義失敗後荷蘭築造普羅民遮城（赤崁樓）加強軍事控制，以及這場悲劇如何為九年後鄭成功攻臺埋下漢人傾力響應的歷史伏筆。"""

ch06_audio_focus = """請兩位主持人以地道自然、引人入勝的繁體中文展開深度的歷史播客對談。探討1652年郭懷一抗荷事件與17世紀臺灣早期漢人移民的拓荒血淚：1. 荷蘭東印度公司的殖民經濟體制（人頭稅、王田、鹿皮貿易）如何把漢人移民逼上絕路？2. 郭懷一的起義籌備、油車行密謀為何被親弟告密？3. 起義農民手持竹槍、鐮刀對抗荷軍現代火繩槍與西拉雅族戰士聯軍的戰術悲劇；4. 為何荷蘭當局隨後興建普羅民遮城（今赤崁樓）？5. 這場起義在臺灣移墾史與反殖民史上的深遠意義，以及九年後延平王鄭成功大軍登陸時漢民簞食壺漿迎王師的歷史連鎖反應。"""

ch07_video_focus = """請以繁體中文與宏大史詩感的歷史紀錄片解說口吻，詳述1661年至1662年延平王鄭成功攻臺之役與九個月熱蘭遮城大圍城。聚焦於鄭軍在清廷海禁與遷界令下的戰略抉擇、何斌獻圖引路、大軍趁天文大潮奇襲突破鹿耳門水道；重現北線尾沙洲由陳澤率軍擊潰荷蘭拔隊長拔克西精銳火槍隊的關鍵首勝，以及臺江內海砲火連天的激烈海戰；詳細解析鄭成功採取全臺分營大屯墾、以持久戰圍困堅固熱蘭遮城的戰略；最後描繪烏特勒支碉堡（高地稜堡）決戰砲轟破城，荷蘭長官揆一簽字開城投降，荷蘭在臺三十八年統治正式終結、開創明鄭東寧新紀元的歷史高潮。"""

ch07_audio_focus = """請兩位主持人以流暢生動、富含歷史思辨的繁體中文展開深度播客對談。剖析1661-1662年鄭成功驅荷復臺與熱蘭遮城九個月大圍城：1. 鄭成功面臨大清海禁遷界絕境，為何通事何斌的臺灣海圖成為反清復海的關鍵命運轉折？2. 鹿耳門水道奇蹟漲潮與北線尾沙洲遭遇戰——陳澤的藤牌兵如何大破荷蘭火繩槍精銳？3. 熱蘭遮城（大員市街與雙層稜堡）的歐洲近代星形要塞防禦體系為何如此難攻？4. 鄭成功如何巧妙實施「全臺大屯墾」，解決兩萬大軍斷糧危機並奠定臺灣農業市街基礎？5. 烏特勒支碉堡爭奪戰與荷蘭長官揆一孤注一擲的心路歷程；6. 荷蘭簽署開城降約撤離臺灣的文明轉向與對東亞海域地緣政治的劃時代影響。"""

print("="*70)
print("🚀 [1/4] 觸發第 06 章 說明影片 (Explainer Video, Heritage, zh-TW)...")
print("="*70)
cmd_v06 = [
    "nlm", "video", "create", CH06_NOTEBOOK,
    "--format", "explainer",
    "--style", "heritage",
    "--language", "zh-TW",
    "--focus", ch06_video_focus,
    "--confirm", "--json"
]
res_v06 = subprocess.run(cmd_v06, capture_output=True, text=True, encoding="utf-8")
print(res_v06.stdout)
if res_v06.stderr:
    print(res_v06.stderr, file=sys.stderr)

print("\n" + "="*70)
print("🚀 [2/4] 觸發第 06 章 播客對談 (Deep Dive Audio, zh-TW)...")
print("="*70)
cmd_a06 = [
    "nlm", "audio", "create", CH06_NOTEBOOK,
    "--format", "deep_dive",
    "--language", "zh-TW",
    "--focus", ch06_audio_focus,
    "--confirm", "--json"
]
res_a06 = subprocess.run(cmd_a06, capture_output=True, text=True, encoding="utf-8")
print(res_a06.stdout)
if res_a06.stderr:
    print(res_a06.stderr, file=sys.stderr)

print("\n" + "="*70)
print("🚀 [3/4] 觸發第 07 章 說明影片 (Explainer Video, Heritage, zh-TW)...")
print("="*70)
cmd_v07 = [
    "nlm", "video", "create", CH07_NOTEBOOK,
    "--format", "explainer",
    "--style", "heritage",
    "--language", "zh-TW",
    "--focus", ch07_video_focus,
    "--confirm", "--json"
]
res_v07 = subprocess.run(cmd_v07, capture_output=True, text=True, encoding="utf-8")
print(res_v07.stdout)
if res_v07.stderr:
    print(res_v07.stderr, file=sys.stderr)

print("\n" + "="*70)
print("🚀 [4/4] 觸發第 07 章 播客對談 (Deep Dive Audio, zh-TW)...")
print("="*70)
cmd_a07 = [
    "nlm", "audio", "create", CH07_NOTEBOOK,
    "--format", "deep_dive",
    "--language", "zh-TW",
    "--focus", ch07_audio_focus,
    "--confirm", "--json"
]
res_a07 = subprocess.run(cmd_a07, capture_output=True, text=True, encoding="utf-8")
print(res_a07.stdout)
if res_a07.stderr:
    print(res_a07.stderr, file=sys.stderr)

print("\n✅ 第 06 章與第 07 章四項繁體中文影音任務已全數送出至 NotebookLM 後端！")
