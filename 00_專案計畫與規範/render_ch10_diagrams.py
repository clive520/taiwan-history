#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render High-Resolution Infographic Diagram PNGs for Chapter 10
1. 清初「渡臺禁令」政策體系與黑水溝橫渡命運流向示意圖
2. 清領前期土地拓墾「一田二主」三層租佃架構與大圳水利組織體系圖
"""
import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = r"d:\Antigravity\科技歷史\臺灣史\assets\images\ch10"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_REGULAR = "C:/Windows/Fonts/msjh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msjhbd.ttc"

def get_font(size, bold=False):
    f_path = FONT_BOLD if bold else FONT_REGULAR
    try:
        return ImageFont.truetype(f_path, size)
    except:
        return ImageFont.load_default()

def draw_rounded_card(draw, box, fill, outline, width=2, radius=12):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def draw_arrow(draw, start, end, fill, width=3, arrow_size=10):
    x0, y0 = start
    x1, y1 = end
    draw.line([start, end], fill=fill, width=width)
    angle = math.atan2(y1 - y0, x1 - x0)
    angle1 = angle + math.pi * 0.85
    angle2 = angle - math.pi * 0.85
    p1 = (x1 + arrow_size * math.cos(angle1), y1 + arrow_size * math.sin(angle1))
    p2 = (x1 + arrow_size * math.cos(angle2), y1 + arrow_size * math.sin(angle2))
    draw.polygon([end, p1, p2], fill=fill)

def render_migration_diagram():
    width, height = 1200, 840
    im = Image.new("RGB", (width, height), "#0a0f1d")
    draw = ImageDraw.Draw(im)

    # 1. Title Banner
    draw_rounded_card(draw, (40, 25, 1160, 95), fill="#111827", outline="#3b82f6", width=2, radius=14)
    draw.text((600, 45), "清初「渡臺禁令」政策體系與黑水溝橫渡命運流向示意圖", fill="#60a5fa", font=get_font(26, bold=True), anchor="mm")
    draw.text((600, 75), "康熙二十三年消極防臺國策 · 渡臺三禁嚴格管控 · 偷渡慘案與「六死三留一回頭」命運終局", fill="#94a3b8", font=get_font(15), anchor="mm")

    # 2. TOP: Qing Court 3 Bans (Red / Amber Policy Theme)
    draw_rounded_card(draw, (40, 115, 1160, 260), fill="#181528", outline="#a855f7", width=2, radius=14)
    draw.text((600, 138), "【大清朝廷消極防臺總綱：1684 年《渡臺禁令》三大嚴苛限制】", fill="#c084fc", font=get_font(17, bold=True), anchor="mm")

    # 3 Policy Cards
    # Card 1: License check
    draw_rounded_card(draw, (65, 160, 395, 245), fill="#231d38", outline="#c084fc", width=1, radius=10)
    draw.text((230, 180), "一、原籍照單審查", fill="#e9d5ff", font=get_font(15, bold=True), anchor="mm")
    draw.text((230, 205), "須經原籍官府、海防同知核驗給照", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((230, 225), "限由廈門出航 · 澎湖驗照 · 鹿耳門登陸", fill="#94a3b8", font=get_font(11), anchor="mm")

    # Card 2: No family
    draw_rounded_card(draw, (425, 160, 775, 245), fill="#2e1a24", outline="#f43f5e", width=1, radius=10)
    draw.text((600, 180), "二、絕對嚴禁攜眷", fill="#fda4af", font=get_font(15, bold=True), anchor="mm")
    draw.text((600, 205), "妻女父母嚴禁隨行 · 在臺不得迎眷", fill="#fecdd3", font=get_font(12, bold=True), anchor="mm")
    draw.text((600, 225), "使移民無家室之累 · 隨時可驅逐遣返", fill="#cbd5e1", font=get_font(11), anchor="mm")

    # Card 3: Cantonese ban
    draw_rounded_card(draw, (805, 160, 1135, 245), fill="#231d38", outline="#c084fc", width=1, radius=10)
    draw.text((970, 180), "三、粵東客民厲禁", fill="#e9d5ff", font=get_font(15, bold=True), anchor="mm")
    draw.text((970, 205), "廣東潮州、惠州籍客民一概禁渡", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((970, 225), "指為鄭黨海盜巢穴 · 被迫轉入地下私渡", fill="#94a3b8", font=get_font(11), anchor="mm")

    # Arrow Down to Ocean Perils
    draw_arrow(draw, (600, 260), (600, 285), fill="#f59e0b", width=3)

    # 3. MIDDLE: The Ocean Crossing Perils & Private Smuggling Horrors
    draw_rounded_card(draw, (40, 285, 1160, 480), fill="#0f172a", outline="#f59e0b", width=2, radius=14)
    draw.text((600, 310), "⚡ 臺灣海峽怒濤險阻與「黑船」私渡偷渡三酷刑 ⚡", fill="#fbbf24", font=get_font(17, bold=True), anchor="mm")

    # Middle 4 cards: Physical Nature & 3 Smuggling Crimes
    draw_rounded_card(draw, (65, 335, 315, 460), fill="#1e293b", outline="#38bdf8", width=1, radius=10)
    draw.text((190, 355), "黑水溝天塹", fill="#38bdf8", font=get_font(15, bold=True), anchor="mm")
    draw.text((190, 380), "深黑如墨 · 廣八十里", fill="#f1f5f9", font=get_font(13, bold=True), anchor="mm")
    draw.text((190, 405), "黑潮支流下旋怒浪奔騰", fill="#cbd5e1", font=get_font(11), anchor="mm")
    draw.text((190, 425), "暗礁密布 · 遇落漈舟碎", fill="#94a3b8", font=get_font(11), anchor="mm")

    draw_rounded_card(draw, (335, 335, 585, 460), fill="#2b1810", outline="#ef4444", width=1, radius=10)
    draw.text((460, 355), "私渡刑之一：放生", fill="#f87171", font=get_font(15, bold=True), anchor="mm")
    draw.text((460, 380), "荒礁沙洲拋棄滅頂", fill="#fecaca", font=get_font(13, bold=True), anchor="mm")
    draw.text((460, 405), "梢舵遇水師巡邏欺騙下船", fill="#cbd5e1", font=get_font(11), anchor="mm")
    draw.text((460, 425), "漲潮荒島覆沒 · 渴死溺斃", fill="#94a3b8", font=get_font(11), anchor="mm")

    draw_rounded_card(draw, (605, 335, 855, 460), fill="#2b1810", outline="#ef4444", width=1, radius=10)
    draw.text((730, 355), "私渡刑之二：灌水", fill="#f87171", font=get_font(15, bold=True), anchor="mm")
    draw.text((730, 380), "密閉底艙鎖死窒息", fill="#fecaca", font=get_font(13, bold=True), anchor="mm")
    draw.text((730, 405), "壓艙木板鐵釘封鎖百人", fill="#cbd5e1", font=get_font(11), anchor="mm")
    draw.text((730, 425), "進水窒息腐臭 · 拋海餵魚", fill="#94a3b8", font=get_font(11), anchor="mm")

    draw_rounded_card(draw, (875, 335, 1135, 460), fill="#2b1810", outline="#ef4444", width=1, radius=10)
    draw.text((1005, 355), "私渡刑之三：種芋頭", fill="#f87171", font=get_font(15, bold=True), anchor="mm")
    draw.text((1005, 380), "岸灘軟泥陷溺滅頂", fill="#fecaca", font=get_font(13, bold=True), anchor="mm")
    draw.text((1005, 405), "趁水深強逼跳海搶灘登陸", fill="#cbd5e1", font=get_font(11), anchor="mm")
    draw.text((1005, 425), "雙腳陷深泥 · 潮漲沒頭顱", fill="#94a3b8", font=get_font(11), anchor="mm")

    # Arrows Down to Destination
    draw_arrow(draw, (350, 480), (250, 505), fill="#ef4444", width=3)
    draw_arrow(draw, (600, 480), (600, 505), fill="#10b981", width=3)
    draw_arrow(draw, (850, 480), (950, 505), fill="#64748b", width=3)

    # 4. BOTTOM: Six Dead, Three Remain, One Return (Fate Breakdown)
    draw_rounded_card(draw, (40, 505, 1160, 810), fill="#131c31", outline="#10b981", width=2, radius=14)
    draw.text((600, 530), "【生死統計真實：「六死、三留、一回頭」移民終局與社會演進】", fill="#34d399", font=get_font(17, bold=True), anchor="mm")

    # 3 Fate Column Cards
    # Fate 1: 60% Die
    draw_rounded_card(draw, (65, 555, 395, 785), fill="#24141d", outline="#ef4444", width=2, radius=12)
    draw.text((230, 580), "【 六 死 】 60% 命喪怒海與荒野", fill="#f87171", font=get_font(16, bold=True), anchor="mm")
    draw.text((230, 610), "◆ 沉船觸礁、黑水溝深淵吞噬", fill="#e2e8f0", font=get_font(13), anchor="mm")
    draw.text((230, 635), "◆ 底艙窒息、沙洲拋棄、岸泥陷溺", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((230, 660), "◆ 瘴癘瘟疫奪命 · 漢番生番衝突殉難", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((230, 695), "深遠文化影響：", fill="#fb7185", font=get_font(12, bold=True), anchor="mm")
    draw.text((230, 720), "全臺盛行「有應公／萬善爺」義塚合祀", fill="#fecdd3", font=get_font(12), anchor="mm")
    draw.text((230, 745), "媽祖航海護庇信仰與中元普渡拔薦", fill="#fecdd3", font=get_font(12), anchor="mm")

    # Fate 2: 30% Remain
    draw_rounded_card(draw, (425, 555, 775, 785), fill="#112920", outline="#10b981", width=2, radius=12)
    draw.text((600, 580), "【 三 留 】 30% 僥倖登陸立錐成家", fill="#34d399", font=get_font(16, bold=True), anchor="mm")
    draw.text((600, 610), "◆ 赤足「羅漢腳」打工拓墾、草寮棲身", fill="#e2e8f0", font=get_font(13), anchor="mm")
    draw.text((600, 635), "◆ 投效墾首墾戶 · 承佃開荒整水田", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((600, 660), "◆ 參與修築八堡圳、瑠公圳等大水利", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((600, 695), "深遠社會影響：", fill="#6ee7b7", font=get_font(12, bold=True), anchor="mm")
    draw.text((600, 720), "男女極端失衡（200:100）· 結社互助", fill="#a7f3d0", font=get_font(12), anchor="mm")
    draw.text((600, 745), "落地生根轉化為臺灣本土社會主力基石", fill="#a7f3d0", font=get_font(12, bold=True), anchor="mm")

    # Fate 3: 10% Return
    draw_rounded_card(draw, (805, 555, 1135, 785), fill="#1e2230", outline="#94a3b8", width=2, radius=12)
    draw.text((970, 580), "【 一回頭 】 10% 歷劫折返唐山故里", fill="#cbd5e1", font=get_font(16, bold=True), anchor="mm")
    draw.text((970, 610), "◆ 不堪臺灣水土不服、瘴癘毒烈", fill="#e2e8f0", font=get_font(13), anchor="mm")
    draw.text((970, 635), "◆ 積蓄耗盡、無地可耕、生計斷絕", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((970, 660), "◆ 目睹海難驚魂，戒懼不敢復涉巨浸", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((970, 695), "原鄉傳播效應：", fill="#94a3b8", font=get_font(12, bold=True), anchor="mm")
    draw.text((970, 720), "「臺灣錢淹腳目，臺灣水黑如墨」", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((970, 745), "留下冒險與警世並存之閩粵移民傳說", fill="#cbd5e1", font=get_font(12), anchor="mm")

    im.save(os.path.join(OUT_DIR, "ch10_diagram_taiwan_strait_migration.png"), "PNG")
    print("Saved: ch10_diagram_taiwan_strait_migration.png")


def render_land_and_water_diagram():
    width, height = 1200, 860
    im = Image.new("RGB", (width, height), "#0a0f1d")
    draw = ImageDraw.Draw(im)

    # 1. Title Banner
    draw_rounded_card(draw, (40, 25, 1160, 95), fill="#111827", outline="#10b981", width=2, radius=14)
    draw.text((600, 45), "清領前期土地拓墾「一田二主」三層租佃架構與大圳水利組織體系圖", fill="#34d399", font=get_font(25, bold=True), anchor="mm")
    draw.text((600, 75), "官府墾照特權 · 墾首招佃分墾 · 永佃改良與水利命脈（施世榜八堡圳 vs 郭錫瑠瑠公圳）", fill="#94a3b8", font=get_font(15), anchor="mm")

    # LEFT HALF: Land Tenure "Yi Tian Er Zhu" (Width 40-580)
    draw_rounded_card(draw, (40, 115, 580, 825), fill="#131c31", outline="#3b82f6", width=2, radius=14)
    draw.text((310, 140), "【清代臺灣土地產權：「一田二主」三層租佃體系】", fill="#60a5fa", font=get_font(17, bold=True), anchor="mm")

    # Level 1: Qing State
    draw_rounded_card(draw, (65, 165, 555, 260), fill="#1e2238", outline="#818cf8", width=1, radius=10)
    draw.text((310, 185), "① 清朝官府（國家最高宗主權）", fill="#a5b4fc", font=get_font(15, bold=True), anchor="mm")
    draw.text((310, 210), "核發「墾照」憑證 · 登記地籍「冊籍」", fill="#e2e8f0", font=get_font(12), anchor="mm")
    draw.text((310, 235), "向大租戶徵收每年固定之「正供國稅」", fill="#cbd5e1", font=get_font(12), anchor="mm")

    draw_arrow(draw, (310, 260), (310, 280), fill="#818cf8", width=3)

    # Level 2: Big Rent Holder (Kenshou)
    draw_rounded_card(draw, (65, 280, 555, 435), fill="#1e293b", outline="#38bdf8", width=2, radius=10)
    draw.text((310, 305), "② 大租戶 / 墾首（擁有「田底權」）", fill="#38bdf8", font=get_font(15, bold=True), anchor="mm")
    draw.text((310, 330), "資本雄厚之豪紳集團（如施世榜、陳賴李墾號）", fill="#f1f5f9", font=get_font(12, bold=True), anchor="mm")
    draw.text((310, 355), "負責包繳官稅 · 每年從小租戶收取固定「大租谷」", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((310, 380), "★ 特權案例：施琅家族「施侯大租」（跨彰臺南鳳萬石）", fill="#fde047", font=get_font(12, bold=True), anchor="mm")
    draw.text((310, 405), "享有朝廷恩賜王田官莊 · 歷經百年形成巨大地租利益", fill="#cbd5e1", font=get_font(11), anchor="mm")

    draw_arrow(draw, (310, 435), (310, 455), fill="#38bdf8", width=3)

    # Level 3: Small Rent Holder (Kenhux)
    draw_rounded_card(draw, (65, 455, 555, 595), fill="#19283d", outline="#0284c7", width=1, radius=10)
    draw.text((310, 480), "③ 小租戶 / 墾戶（擁有「田面權」永佃權）", fill="#7dd3fc", font=get_font(15, bold=True), anchor="mm")
    draw.text((310, 505), "實質出資整地、築堤修渠、購牛購種的投資者", fill="#f1f5f9", font=get_font(12, bold=True), anchor="mm")
    draw.text((310, 530), "產權可自由典買抵押 · 成為農村實際地主與地方領袖", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((310, 555), "向現耕佃農收取收成 40% ~ 50% 之高額「小租谷」", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((310, 575), "承擔水圳維修與田租調解職能", fill="#94a3b8", font=get_font(11), anchor="mm")

    draw_arrow(draw, (310, 595), (310, 615), fill="#0284c7", width=3)

    # Level 4: Tenant Farmers (Luohan-jiao)
    draw_rounded_card(draw, (65, 615, 555, 805), fill="#241926", outline="#f43f5e", width=1, radius=10)
    draw.text((310, 640), "④ 現耕佃農 / 佃丁（底層耕作者 · 羅漢腳）", fill="#fb7185", font=get_font(15, bold=True), anchor="mm")
    draw.text((310, 665), "無田產家室之單身漢 · 日夜揮汗從事耕耘插秧", fill="#fecdd3", font=get_font(12), anchor="mm")
    draw.text((310, 690), "承擔旱澇蟲風天災全部風險 · 繳交沉重小租與水費", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((310, 715), "農忙耕作 · 農閒散工 · 荒年歉收即淪為抗官或械鬥主力", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((310, 750), "產權體系總評：", fill="#f43f5e", font=get_font(12, bold=True), anchor="mm")
    draw.text((310, 775), "多重產權動員拓荒資本 · 亦種下深重中間剝削與抗租糾紛", fill="#fecdd3", font=get_font(11), anchor="mm")

    # RIGHT HALF: Two Water Irrigation Miracles (Width 620-1160)
    draw_rounded_card(draw, (620, 115, 1160, 825), fill="#0f2922", outline="#10b981", width=2, radius=14)
    draw.text((890, 140), "【清領前期兩大水利奇蹟：八堡圳 vs 瑠公圳】", fill="#34d399", font=get_font(17, bold=True), anchor="mm")

    # Section A: Babao Canal (Changhua)
    draw_rounded_card(draw, (645, 165, 1135, 480), fill="#133d32", outline="#34d399", width=2, radius=12)
    draw.text((890, 190), "◆ 彰化八堡圳（施厝圳 · 1709 - 1719）", fill="#6ee7b7", font=get_font(16, bold=True), anchor="mm")
    draw.text((890, 215), "主持領袖：施世榜（墾號施長齡） · 關鍵巧匠：林先生", fill="#f0fdf4", font=get_font(13, bold=True), anchor="mm")
    draw.text((890, 240), "取水流域：濁水溪鼻仔頭（二水出山口）", fill="#cbd5e1", font=get_font(12), anchor="mm")

    # Sub-card: Shigou engineering
    draw_rounded_card(draw, (665, 260, 1115, 375), fill="#0d2821", outline="#10b981", width=1, radius=8)
    draw.text((890, 280), "★ 核心工程突破：「林先生石笱導水法」", fill="#fde047", font=get_font(14, bold=True), anchor="mm")
    draw.text((890, 305), "以削尖竹篾編織倒立圓錐筍狀巨籠（竹笱）", fill="#e2e8f0", font=get_font(12), anchor="mm")
    draw.text((890, 328), "內填濁水溪滾圓卵石 · 層層斜壘插入奔騰激流", fill="#e2e8f0", font=get_font(12), anchor="mm")
    draw.text((890, 352), "柔性破浪 · 阻截泥沙 · 成功馴服巨流導入圳口", fill="#86efac", font=get_font(12, bold=True), anchor="mm")

    draw.text((890, 400), "灌溉範圍：涵蓋彰化十三堡中之八堡，達 20,000 餘甲", fill="#a7f3d0", font=get_font(13, bold=True), anchor="mm")
    draw.text((890, 425), "經貿效應：彰化躍升「全臺米倉」 · 促成鹿港「一府二鹿」盛世", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((890, 450), "人文崇祀：二水立「林先生廟」· 每年「彰化跑水節」感念恩澤", fill="#94a3b8", font=get_font(11), anchor="mm")

    # Section B: Liugong Canal (Taipei)
    draw_rounded_card(draw, (645, 500, 1135, 805), fill="#133d32", outline="#34d399", width=2, radius=12)
    draw.text((890, 525), "◆ 臺北瑠公圳（1740 - 1767）", fill="#6ee7b7", font=get_font(16, bold=True), anchor="mm")
    draw.text((890, 550), "主持領袖：郭錫瑠（瑠公 · 傾家開墾） · 其子郭元芬續修", fill="#f0fdf4", font=get_font(13, bold=True), anchor="mm")
    draw.text((890, 575), "取水流域：新店溪青潭溪口（碧潭山壁開硿引水）", fill="#cbd5e1", font=get_font(12), anchor="mm")

    # Sub-card: Wooden Aqueduct
    draw_rounded_card(draw, (665, 595, 1115, 710), fill="#0d2821", outline="#10b981", width=1, radius=8)
    draw.text((890, 615), "★ 核心工程突破：「木筧穿溪」與地下暗管", fill="#fde047", font=get_font(14, bold=True), anchor="mm")
    draw.text((890, 640), "初以檜木打造巨大水槽 · 架木樁凌空飛渡景美溪", fill="#e2e8f0", font=get_font(12), anchor="mm")
    draw.text((890, 663), "乾隆三十年山洪沖毀 · 瑠公憂憤病逝", fill="#fca5a5", font=get_font(12), anchor="mm")
    draw.text((890, 687), "郭元芬改建「地下暗管」埋入河床 · 終告貫通通水", fill="#86efac", font=get_font(12, bold=True), anchor="mm")

    draw.text((890, 735), "灌溉範圍：大加蚋堡、大安、松山、景美，達 1,200 餘甲", fill="#a7f3d0", font=get_font(13, bold=True), anchor="mm")
    draw.text((890, 760), "經貿效應：臺北盆地由旱埔化為千頃水田 · 奠定艋舺與臺北城繁榮", fill="#cbd5e1", font=get_font(12), anchor="mm")
    draw.text((890, 785), "人文紀念：景美留有留公圳古道碑 · 碧潭青潭口引水遺跡永存", fill="#94a3b8", font=get_font(11), anchor="mm")

    im.save(os.path.join(OUT_DIR, "ch10_diagram_land_tenure_water_system.png"), "PNG")
    print("Saved: ch10_diagram_land_tenure_water_system.png")

if __name__ == "__main__":
    render_migration_diagram()
    render_land_and_water_diagram()
    print("All Chapter 10 diagram PNGs rendered successfully!")
