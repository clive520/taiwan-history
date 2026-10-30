# -*- coding: utf-8 -*-
import subprocess
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

NOTEBOOK_ID = "e31351ff-da48-4c4e-9a58-9726b6c184dc"

video_focus = """聚焦於 1895 年馬關條約割讓臺灣引發的全臺悲憤；深入剖析「臺灣民主國」成立、藍地黃虎旗與永清年號背後效忠大清待援的政治矛盾，以及唐景崧逃亡與臺北開城；生動重現桃竹苗客家義軍（吳湯興、徐驤、姜紹祖敢字營）利用泥田刺竹非對稱游擊與姜紹祖十九歲絕筆；詳盡解說臺灣史上最大陸戰「彰化八卦山戰役」黑旗軍吳彭年七星隊與客家義民壯烈犧牲；解析徐驤曾文溪殉國、劉永福內渡與巴克禮導引臺南和平進城；最後探討抗日三猛與 1915 噍吧哖西來庵事件余清芳虎頭山血戰，如何促成 1920 年代林獻堂、蔣渭水走向臺灣文化協會與非暴力文化啟蒙的大轉向。"""

podcast_focus = """深度思辨 1895 至 1915 年間臺灣先民在殖民鐵蹄下的二十年抗爭史詩。兩位學者生動對談：1. 馬關割臺時臺灣被清廷拋棄的絕望與「臺灣民主國」藍地黃虎旗背後複雜的政治算計；2. 為什麼正規軍崩潰後，桃竹苗客家農民（吳湯興、徐驤、姜紹祖）會爆發全民誓死抗暴？姜紹祖「遑恤身家為存國格」的心靈震撼；3. 彰化八卦山決戰雙方戰術武器對比與黑旗軍七星隊壯烈犧牲；4. 日軍戰死 164 人卻病死 4,600 餘人（含能久親王）反映的風土氣候；5. 總督府《六三法》與《匪徒刑罰令》高壓下「抗日三猛」簡大獅、柯鐵虎、林少貓的游擊悲劇；6. 1915 噍吧哖西來庵神道符咒起義在現代火砲下的滅村慘劇，以及臺灣人如何從血泊中覺醒，轉向 1920 年代蔣渭水、林獻堂以文化、演講、議會爭奪尊嚴的文明啟蒙！"""

print("🚀 正在觸發第 13 章 說明影片 (Explainer Video, Heritage 風格)...", flush=True)
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

print("\n🚀 正在觸發第 13 章 雙人深度對談 (Podcast Deep-Dive)...", flush=True)
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
