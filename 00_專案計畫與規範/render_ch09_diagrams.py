#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render High-Resolution Infographic Diagram PNGs for Chapter 09
1. 澎湖海戰雙方水師戰術部署與五爪開花示意圖
2. 康熙朝廷棄留臺灣大辯論與一府三縣建制體系架構圖
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = r"d:\Antigravity\科技歷史\臺灣史\assets\images\ch09"
os.makedirs(OUT_DIR, exist_ok=True)

# Fonts
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
    import math
    angle = math.atan2(y1 - y0, x1 - x0)
    angle1 = angle + math.pi * 0.85
    angle2 = angle - math.pi * 0.85
    p1 = (x1 + arrow_size * math.cos(angle1), y1 + arrow_size * math.sin(angle1))
    p2 = (x1 + arrow_size * math.cos(angle2), y1 + arrow_size * math.sin(angle2))
    draw.polygon([end, p1, p2], fill=fill)


def render_penghu_naval_battle():
    width, height = 1200, 820
    im = Image.new("RGB", (width, height), "#0b101d")
    draw = ImageDraw.Draw(im)

    # Title Banner
    draw_rounded_card(draw, (40, 25, 1160, 95), fill="#131c31", outline="#3b82f6", width=2, radius=14)
    font_title = get_font(26, bold=True)
    font_sub = get_font(15, bold=False)
    draw.text((600, 45), "1683 年澎湖海戰雙方水師戰術部署與「五爪開花」破陣圖", fill="#60a5fa", font=font_title, anchor="mm")
    draw.text((600, 75), "施琅提督親率三百艘戰艦出八罩島 · 西南狂風助戰 · 撕裂劉國軒二十里砲壘長堤防線", fill="#94a3b8", font=font_sub, anchor="mm")

    # TOP: Dongning Fleet Defense (Red / Orange Theme)
    draw_rounded_card(draw, (40, 115, 1160, 275), fill="#1a1423", outline="#ef4444", width=2, radius=14)
    draw.text((600, 138), "【東寧王國澎湖守備陣線：武平侯 劉國軒 統帥 200 艘戰艦、守軍 20,000 人】", fill="#f87171", font=get_font(18, bold=True), anchor="mm")

    # 3 sub-defense cards
    # Left: Xiyu
    draw_rounded_card(draw, (65, 165, 395, 255), fill="#261b2e", outline="#f43f5e", width=1, radius=10)
    draw.text((230, 190), "西嶼砲台前哨", fill="#fb7185", font=get_font(16, bold=True), anchor="mm")
    draw.text((230, 215), "扼守吼門水道外圍險隘", fill="#e2e8f0", font=get_font(13), anchor="mm")
    draw.text((230, 235), "部署烏金砲與快哨戰船", fill="#94a3b8", font=get_font(12), anchor="mm")

    # Center: Magong Harbour
    draw_rounded_card(draw, (425, 165, 775, 255), fill="#2e1d24", outline="#ef4444", width=2, radius=10)
    draw.text((600, 190), "娘媽宮（馬公）核心水寨", fill="#fca5a5", font=get_font(17, bold=True), anchor="mm")
    draw.text((600, 215), "二十里連綿土壘砲台 · 百門紅夷大砲", fill="#fecaca", font=get_font(13, bold=True), anchor="mm")
    draw.text((600, 235), "沉船塞港 · 兩百艘主力鳥船以逸待勞", fill="#cbd5e1", font=get_font(12), anchor="mm")

    # Right: Fengguiwei
    draw_rounded_card(draw, (805, 165, 1135, 255), fill="#261b2e", outline="#f43f5e", width=1, radius=10)
    draw.text((970, 190), "風櫃尾荷蘭城堡砲台", fill="#fb7185", font=get_font(16, bold=True), anchor="mm")
    draw.text((970, 215), "居高臨下封鎖外海航道", fill="#e2e8f0", font=get_font(13), anchor="mm")
    draw.text((970, 235), "重砲交錯射角掩護內港", fill="#94a3b8", font=get_font(12), anchor="mm")

    # MIDDLE: The Clash & South-West Gale Event Card
    draw_rounded_card(draw, (180, 295, 1020, 395), fill="#1e293b", outline="#f59e0b", width=2, radius=12)
    draw.text((600, 323), "⚡ 六月二十二日正午：海象氣候大轉折 —— 強勁西南風驟起！", fill="#fbbf24", font=get_font(18, bold=True), anchor="mm")
    draw.text((600, 350), "施琅洞悉夏至風信逆風破陣 · 清軍戰船順風疾馳壓境 · 火攻硝煙盡灌東寧陣營", fill="#fef3c7", font=get_font(14), anchor="mm")
    draw.text((600, 373), "東寧大將林陞、江勝陣亡 · 劉國軒戰線崩潰，率親隨由吼門小徑突圍逃回臺南", fill="#cbd5e1", font=get_font(13), anchor="mm")

    # Arrows from bottom to top
    draw_arrow(draw, (230, 470), (230, 410), fill="#38bdf8", width=3)
    draw_arrow(draw, (430, 470), (520, 410), fill="#38bdf8", width=3)
    draw_arrow(draw, (600, 470), (600, 410), fill="#eab308", width=4)
    draw_arrow(draw, (770, 470), (680, 410), fill="#38bdf8", width=3)
    draw_arrow(draw, (970, 470), (970, 410), fill="#38bdf8", width=3)

    # BOTTOM: Qing Naval Formation (Five-Claw Blossom)
    draw_rounded_card(draw, (40, 480, 1160, 785), fill="#0f2338", outline="#0284c7", width=2, radius=14)
    draw.text((600, 505), "【大清帝國水師「五爪開花」突擊體系：提督 施琅 統帥 300 艘戰艦、官兵 21,000 人】", fill="#38bdf8", font=get_font(18, bold=True), anchor="mm")

    # 4 division cards
    # Claw 1: Left Flank Lin Xian
    draw_rounded_card(draw, (65, 535, 315, 680), fill="#13314f", outline="#38bdf8", width=1, radius=10)
    draw.text((190, 560), "左翼第一爪：牛心灣", fill="#7dd3fc", font=get_font(15, bold=True), anchor="mm")
    draw.text((190, 590), "總兵 林賢 率 50 艘", fill="#ffffff", font=get_font(14, bold=True), anchor="mm")
    draw.text((190, 620), "牽制西側外圍守軍", fill="#cbd5e1", font=get_font(13), anchor="mm")
    draw.text((190, 645), "穿插包抄西嶼咽喉", fill="#94a3b8", font=get_font(12), anchor="mm")

    # Claw 2 & Center: Main Fleet Shi Lang
    draw_rounded_card(draw, (340, 535, 860, 680), fill="#1e3a5f", outline="#f59e0b", width=2, radius=12)
    draw.text((600, 560), "中軍主攻主力爪：娘媽宮正港突穿（旗艦陣列）", fill="#fde047", font=get_font(17, bold=True), anchor="mm")
    draw.text((600, 590), "福建水師提督 施琅 親督 56 艘巨型鳥船 結鋒矢陣", fill="#ffffff", font=get_font(15, bold=True), anchor="mm")
    draw.text((600, 620), "集中千斤佛郎機與噴筒火攻 · 萬彈齊發正面硬撼敵方長堤防線", fill="#fef08a", font=get_font(13), anchor="mm")
    draw.text((600, 645), "副將藍理帶傷衝鋒 · 突破沉船阻隔直搗東寧中樞座船", fill="#cbd5e1", font=get_font(12), anchor="mm")

    # Claw 3: Right Flank Dong Yi
    draw_rounded_card(draw, (885, 535, 1135, 680), fill="#13314f", outline="#38bdf8", width=1, radius=10)
    draw.text((1010, 560), "右翼第二爪：雞籠嶼", fill="#7dd3fc", font=get_font(15, bold=True), anchor="mm")
    draw.text((1010, 590), "總兵 董義 率 50 艘", fill="#ffffff", font=get_font(14, bold=True), anchor="mm")
    draw.text((1010, 620), "迂迴打擊風櫃尾側翼", fill="#cbd5e1", font=get_font(13), anchor="mm")
    draw.text((1010, 645), "壓制岸砲火力掩護中軍", fill="#94a3b8", font=get_font(12), anchor="mm")

    # Claw 4 & 5: Reserve & Flanking Fleets
    draw_rounded_card(draw, (180, 700, 1020, 765), fill="#102a43", outline="#0284c7", width=1, radius=10)
    draw.text((600, 720), "奇兵夾擊兩爪：總兵 陳蟒、魏明 率 80 艘高速快哨 埋伏西嶼外海，斷敵退路", fill="#93c5fd", font=get_font(14, bold=True), anchor="mm")
    draw.text((600, 745), "後續預備隊 60 艘坐鎮望安八罩島基地，隨時應對風暴逆浪並轉運救護傷患", fill="#94a3b8", font=get_font(12), anchor="mm")

    out_file = os.path.join(OUT_DIR, "ch09_diagram_penghu_naval_battle.png")
    im.save(out_file, "PNG", quality=95)
    print(f"Saved: {out_file} ({os.path.getsize(out_file)} bytes)")


def render_debate_and_governance():
    width, height = 1200, 820
    im = Image.new("RGB", (width, height), "#0b101d")
    draw = ImageDraw.Draw(im)

    # Title Banner
    draw_rounded_card(draw, (40, 25, 1160, 95), fill="#171e2e", outline="#f59e0b", width=2, radius=14)
    font_title = get_font(26, bold=True)
    font_sub = get_font(15, bold=False)
    draw.text((600, 45), "康熙朝廷「棄留臺灣大辯論」與 1684 年一府三縣建制體系", fill="#fbbf24", font=font_title, anchor="mm")
    draw.text((600, 75), "從紫禁城金鑾殿激烈廷爭 · 到施琅《恭陳臺灣棄留疏》拍板設府 · 確立大清治理體系", fill="#94a3b8", font=font_sub, anchor="mm")

    # TOP: Two Debating Sides
    # Left: Abandon Taiwan Faction
    draw_rounded_card(draw, (40, 115, 580, 310), fill="#25161c", outline="#f43f5e", width=2, radius=14)
    draw.text((310, 140), "【棄臺派觀點：朝中滿漢重臣主流】", fill="#fb7185", font=get_font(17, bold=True), anchor="mm")
    draw.text((310, 165), "代表人物：大學士李光地、尚書梁清標及廷臣", fill="#fda4af", font=get_font(13), anchor="mm")
    
    abandon_points = [
        "• 荒島無益論：「臺灣孤懸海外，荒礫黑子之地，得之無所加，不得無所損」",
        "• 財政負擔論：「海外孤島駐兵防守，歲耗百萬糧餉，空竭國帑得不償失」",
        "• 空島防患論：「主張遷其人、棄其地，將全島數十萬漢民強遷回閩粵內地」"
    ]
    for idx, p in enumerate(abandon_points):
        draw.text((65, 195 + idx * 35), p, fill="#f1f5f9", font=get_font(12, bold=False))

    # Right: Retain Taiwan Faction
    draw_rounded_card(draw, (620, 115, 1160, 310), fill="#102a24", outline="#10b981", width=2, radius=14)
    draw.text((890, 140), "【留臺派觀點：水師提督 施琅】", fill="#34d399", font=get_font(17, bold=True), anchor="mm")
    draw.text((890, 165), "核心依據：名垂青史之《恭陳臺灣棄留疏》（1684 年 2 月）", fill="#6ee7b7", font=get_font(13), anchor="mm")

    retain_points = [
        "• 東南門戶論：「臺灣乃江浙閩粵四省左臂門戶，若棄之必為荷蘭強寇復據」",
        "• 沃野千里論：「土地膏腴，稻二熟、糖鹽豐饒，駐軍屯墾足以自給自足」",
        "• 安土重結論：「百姓在臺拓荒二十餘載，安居樂業，強遷必致家破人亡激起民變」"
    ]
    for idx, p in enumerate(retain_points):
        draw.text((645, 195 + idx * 35), p, fill="#f1f5f9", font=get_font(12, bold=False))

    # MIDDLE: Kangxi Decision
    draw_rounded_card(draw, (200, 330, 1000, 420), fill="#2e2010", outline="#f59e0b", width=2, radius=12)
    draw.text((600, 355), "👑 康熙帝玄燁拍板定奪：斷然採納施琅奏議", fill="#fde047", font=get_font(18, bold=True), anchor="mm")
    draw.text((600, 385), "「臺灣棄取，所關重大。棄而不守，尤為不可；棄之必成大患，留之方可安海！」", fill="#fef08a", font=get_font(15, bold=True), anchor="mm")

    # Arrows down to Taiwan Fu
    draw_arrow(draw, (600, 420), (600, 465), fill="#f59e0b", width=3)

    # BOTTOM: 1684 Taiwan Fu Governance Structure
    draw_rounded_card(draw, (40, 470, 1160, 785), fill="#0f1f33", outline="#3b82f6", width=2, radius=14)
    draw.text((600, 498), "【1684 年（康熙二十三年）大清帝國正式建制：福建省臺灣府行政體系】", fill="#60a5fa", font=get_font(18, bold=True), anchor="mm")

    # Top Leaders of Taiwan
    draw_rounded_card(draw, (100, 525, 570, 595), fill="#173152", outline="#60a5fa", width=1, radius=10)
    draw.text((335, 548), "臺灣分巡道（兼兵備道）", fill="#93c5fd", font=get_font(16, bold=True), anchor="mm")
    draw.text((335, 572), "全臺最高民政、司法、教育監察與海防決策官員", fill="#cbd5e1", font=get_font(12), anchor="mm")

    draw_rounded_card(draw, (630, 525, 1100, 595), fill="#173152", outline="#60a5fa", width=1, radius=10)
    draw.text((865, 548), "臺灣鎮總兵（駐防府城）", fill="#93c5fd", font=get_font(16, bold=True), anchor="mm")
    draw.text((865, 572), "統轄水陸八營近萬名綠營官兵，戍守臺澎海疆", fill="#cbd5e1", font=get_font(12), anchor="mm")

    # Center: Taiwan Fu
    draw_rounded_card(draw, (380, 610, 820, 670), fill="#1e3a63", outline="#38bdf8", width=2, radius=10)
    draw.text((600, 630), "臺灣府（府知府）", fill="#ffffff", font=get_font(17, bold=True), anchor="mm")
    draw.text((600, 652), "府治設於原承天府赤崁（今臺南市中西區）", fill="#bae6fd", font=get_font(13), anchor="mm")

    # Lines down to Three Counties
    draw_arrow(draw, (450, 670), (230, 695), fill="#38bdf8", width=2)
    draw_arrow(draw, (600, 670), (600, 695), fill="#38bdf8", width=2)
    draw_arrow(draw, (750, 670), (970, 695), fill="#38bdf8", width=2)

    # 3 Counties
    # 1. Taiwan County
    draw_rounded_card(draw, (65, 695, 395, 770), fill="#112a45", outline="#0284c7", width=1, radius=10)
    draw.text((230, 718), "臺灣縣（首善之畿）", fill="#7dd3fc", font=get_font(15, bold=True), anchor="mm")
    draw.text((230, 745), "縣治：臺南府城周邊（原承天府核心）", fill="#e2e8f0", font=get_font(12), anchor="mm")

    # 2. Fengshan County
    draw_rounded_card(draw, (425, 695, 775, 770), fill="#112a45", outline="#0284c7", width=1, radius=10)
    draw.text((600, 718), "鳳山縣（南路咽喉）", fill="#7dd3fc", font=get_font(15, bold=True), anchor="mm")
    draw.text((600, 745), "縣治：興隆庄（今高雄左營舊城）", fill="#e2e8f0", font=get_font(12), anchor="mm")

    # 3. Zhuluo County
    draw_rounded_card(draw, (805, 695, 1135, 770), fill="#112a45", outline="#0284c7", width=1, radius=10)
    draw.text((970, 718), "諸羅縣（北路宏闊）", fill="#7dd3fc", font=get_font(15, bold=True), anchor="mm")
    draw.text((970, 745), "縣治：佳里興（後遷嘉義），管至雞籠淡水", fill="#e2e8f0", font=get_font(12), anchor="mm")

    out_file = os.path.join(OUT_DIR, "ch09_diagram_debate_and_governance.png")
    im.save(out_file, "PNG", quality=95)
    print(f"Saved: {out_file} ({os.path.getsize(out_file)} bytes)")


if __name__ == "__main__":
    render_penghu_naval_battle()
    render_debate_and_governance()
    print("All Chapter 09 diagrams successfully rendered!")
