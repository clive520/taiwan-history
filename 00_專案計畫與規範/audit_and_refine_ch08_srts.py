# -*- coding: utf-8 -*-
import sys
import os
import json
import re
from pathlib import Path

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH08_DIR = BASE_DIR / "舌尖上的臺灣" / "03_帝國之眼與東洋滋味"

VID_SRT = CH08_DIR / "第08章_改變世界的綠色奇蹟_說明影片.srt"
POD_SRT = CH08_DIR / "第08章_改變世界的綠色奇蹟_雙人對談.srt"

EXTRA_CORRECTIONS = [
    (r"白米單身背後", "白米誕生背後"),
    (r"白米單身", "白米誕生"),
    (r"有沒有撐起一碗", "有沒有盛起一碗"),
    (r"撐起一碗", "盛起一碗"),
    (r"撐起那碗", "盛起那碗"),
    (r"災難米花粉", "在來米花粉"),
    (r"災難米", "在來米"),
    (r"織煉澱粉", "支鏈澱粉"),
    (r"直煉澱粉", "直鏈澱粉"),
    (r"如果你去干擾熊", "如果我們去看"),
    (r"干擾熊", "去看"),
    (r"竹子胡", "竹子湖"),
    (r"嘉南大郡", "嘉南大圳"),
    (r"朋萊米", "蓬萊米"),
    (r"再來米", "在來米"),
    (r"仙稻", "秈稻"),
    (r"梗稻", "粳稻"),
]

def fix_file(p):
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()
    for pat, rep in EXTRA_CORRECTIONS:
        c = re.sub(pat, rep, c)
    with open(p, "w", encoding="utf-8") as f:
        f.write(c)
    print(f"✅ 已完成深度語意校正：{p.name}")

fix_file(VID_SRT)
fix_file(POD_SRT)
