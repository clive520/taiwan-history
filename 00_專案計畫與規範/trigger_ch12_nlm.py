# -*- coding: utf-8 -*-
import subprocess
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

NOTEBOOK_ID = "ee220930-b26c-412d-8939-29b55f50a41f"

video_focus = """聚焦於 1860 年四口開港與茶糖樟腦外銷引發的「經濟重心北移」及大稻埕傳奇；深度剖析 1874 年牡丹社事件與沈葆楨開山撫番（八通關古道、億載金城）；生動展現 1884 年中法戰爭滬尾大捷劉銘傳「棄基保滬」戰略伏擊；系統歸納 1885 臺灣建省後劉銘傳六大洋務新政（基隆至新竹鐵路、獅球嶺隧道貫通、騰雲號機車、跨海電報海纜、臺灣郵政總局自辦郵票、臺北電燈與清賦事業），並客觀反思大嵙崁戰役武力剿番對原住民族造成的沉痛歷史代價。"""

podcast_focus = """深入探討晚清臺灣三十年間如何從海外封禁荒島躍升為全大清帝國最先進的現代化行省。兩位學者生動對談：1. 約翰·陶德與李春生開拓 Formosa Oolong 外銷紐約如何造就大稻埕；2. 牡丹社事件日本野心與沈葆楨億載金城、廢除渡臺禁令與開山撫番；3. 孤拔艦隊威脅下劉銘傳棄基保滬、孫開華與林朝棟在沙崙林投刺叢中白刃殲滅法軍；4. 獅球嶺隧道 30 個月艱苦開鑿、「曠宇天開」石刻與騰雲號奔馳；5. 領先大清八年的獨立郵政與跨海電報海纜；6. 深刻反思大嵙崁戰役武力圍剿泰雅族的血淚代價與劉銘傳去職後的遺憾。"""

print("🚀 正在觸發第 12 章 說明影片 (Explainer Video, Heritage 風格)...", flush=True)
cmd_video = [
    "nlm", "video", "create", NOTEBOOK_ID,
    "--format", "explainer",
    "--style", "heritage",
    "--language", "zh-TW",
    "--focus", video_focus,
    "--confirm",
    "--json"
]
res_video = subprocess.run(cmd_video, capture_output=True, text=True, encoding="utf-8")
print(res_video.stdout)
if res_video.stderr:
    print(res_video.stderr, file=sys.stderr)

print("\n🚀 正在觸發第 12 章 雙人深度對談 (Podcast Deep-Dive)...", flush=True)
cmd_audio = [
    "nlm", "audio", "create", NOTEBOOK_ID,
    "--format", "deep_dive",
    "--language", "zh-TW",
    "--focus", podcast_focus,
    "--confirm",
    "--json"
]
res_audio = subprocess.run(cmd_audio, capture_output=True, text=True, encoding="utf-8")
print(res_audio.stdout)
if res_audio.stderr:
    print(res_audio.stderr, file=sys.stderr)

print("\n✅ 雙軌影音生成任務已成功送出至 NotebookLM 後端！", flush=True)
