# -*- coding: utf-8 -*-
"""
為《臺灣史》專案繪製高解析度關聯圖表（取代 ASCII 代碼方框）
輸出高品質 PNG 圖片，具備深色主題、圓角卡片、流暢箭頭與微軟正黑體字型。
涵蓋第 08 章、第 07 章、第 04 章等所有關係戰術圖。
"""
import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "C:/Windows/Fonts/msjhbd.ttc"  # 微軟正黑體 粗體
FONT_REG_PATH = "C:/Windows/Fonts/msjh.ttc"  # 微軟正黑體 常規

def get_font(size, bold=True):
    path = FONT_PATH if bold else FONT_REG_PATH
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.truetype(FONT_PATH, size)

def draw_arrow(draw, start, end, color=(56, 189, 248), width=3, arrow_size=10):
    """繪製帶有實心箭頭的平滑引導線"""
    x1, y1 = start
    x2, y2 = end
    draw.line([start, end], fill=color, width=width)
    
    angle = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - arrow_size * math.cos(angle - math.pi / 6),
          y2 - arrow_size * math.sin(angle - math.pi / 6))
    p2 = (x2 - arrow_size * math.cos(angle + math.pi / 6),
          y2 - arrow_size * math.sin(angle + math.pi / 6))
    
    draw.polygon([end, p1, p2], fill=color)

def draw_card(draw, box, title, subtitle="", bg=(30, 41, 59), border=(56, 189, 248), 
              title_color=(248, 250, 252), sub_color=(148, 163, 184), 
              radius=12, border_width=2, title_size=20, sub_size=15):
    """繪製現代化深色資訊卡片"""
    x1, y1, x2, y2 = box
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=bg, outline=border, width=border_width)
    
    font_t = get_font(title_size, bold=True)
    tb = draw.textbbox((0, 0), title, font=font_t)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]
    
    if subtitle:
        font_s = get_font(sub_size, bold=False)
        lines = subtitle.split("\n")
        line_heights = []
        total_sub_h = 0
        for l in lines:
            bb = draw.textbbox((0, 0), l, font=font_s)
            lh = bb[3] - bb[1]
            line_heights.append((bb[2]-bb[0], lh))
            total_sub_h += lh + 4
            
        total_h = th + 10 + total_sub_h
        top_y = y1 + ((y2 - y1) - total_h) / 2
        
        tx = x1 + ((x2 - x1) - tw) / 2
        draw.text((tx, top_y), title, font=font_t, fill=title_color)
        
        curr_y = top_y + th + 10
        for i, l in enumerate(lines):
            lw, lh = line_heights[i]
            # 如果多行則靠左居中 padding
            lx = x1 + 25 if len(lines) > 1 else x1 + ((x2 - x1) - lw) / 2
            draw.text((lx, curr_y), l, font=font_s, fill=sub_color)
            curr_y += lh + 4
    else:
        tx = x1 + ((x2 - x1) - tw) / 2
        ty = y1 + ((y2 - y1) - th) / 2 - 2
        draw.text((tx, ty), title, font=font_t, fill=title_color)

# =========================================================================
# 圖表 1：第08章【東寧王國軍屯開拓戰略示意圖】
# =========================================================================
def render_ch08_military_tuntian_diagram(out_path):
    W, H = 1200, 700
    im = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(im)
    
    draw.rounded_rectangle([15, 15, W-15, H-15], radius=16, outline=(51, 65, 85), width=2)
    
    font_main = get_font(26, bold=True)
    font_sub = get_font(16, bold=False)
    
    main_title = "【東寧王國軍屯開拓戰略示意圖】"
    sub_title = "寓兵於農・劃分官田／私田／營盤田・奠定臺灣西半部地名人文根基"
    
    tb = draw.textbbox((0, 0), main_title, font=font_main)
    draw.text(((W - (tb[2]-tb[0]))/2, 35), main_title, font=font_main, fill=(245, 158, 11))
    
    sb = draw.textbbox((0, 0), sub_title, font=font_sub)
    draw.text(((W - (sb[2]-sb[0]))/2, 75), sub_title, font=font_sub, fill=(148, 163, 184))
    
    card_center = [W/2 - 130, 120, W/2 + 130, 195]
    draw_card(draw, card_center, "承天府（中樞京畿）", "赤崁・延平王府・總制政務", 
              bg=(24, 34, 53), border=(245, 158, 11), title_color=(255, 230, 0), border_width=3)
    
    mid_x = W / 2
    draw.line([(mid_x, 195), (mid_x, 235)], fill=(148, 163, 184), width=3)
    
    left_x = 310
    right_x = 890
    draw.line([(left_x, 235), (right_x, 235)], fill=(148, 163, 184), width=3)
    
    draw_arrow(draw, (left_x, 235), (left_x, 265), color=(56, 189, 248), width=3, arrow_size=12)
    draw_arrow(draw, (right_x, 235), (right_x, 265), color=(244, 63, 94), width=3, arrow_size=12)
    
    draw_card(draw, [60, 270, 560, 340], "【北路屯墾線】（天興州主管）", "軍屯營盤縱深開拓・嘉南平原大糧倉",
              bg=(15, 30, 55), border=(56, 189, 248), title_color=(56, 189, 248), title_size=19)
    
    stations_north = ["新港", "查畝營(柳營)", "林鳳營", "諸羅山(嘉義)"]
    step_w = (500) / 4
    for i, st in enumerate(stations_north):
        sx = 60 + i * (step_w + 5)
        sy = 360
        draw_card(draw, [sx, sy, sx + step_w - 5, sy + 50], st, "", 
                  bg=(30, 41, 59), border=(100, 116, 139), title_size=15, title_color=(241, 245, 249))
        if i < len(stations_north) - 1:
            draw_arrow(draw, (sx + step_w - 5, sy + 25), (sx + step_w + 5, sy + 25), color=(56, 189, 248), width=2, arrow_size=8)
            
    draw_card(draw, [60, 440, 290, 620], "【開荒闢草】", "• 嚴禁強佔原住民各社熟地\n• 插標掛牌開拓無主荒埔\n• 犯番界者軍法處斬保和平",
              bg=(18, 30, 49), border=(52, 211, 153), title_color=(52, 211, 153), title_size=18, sub_size=14, border_width=2)
    draw_arrow(draw, (175, 410), (175, 440), color=(52, 211, 153), width=2, arrow_size=10)
    
    draw_card(draw, [330, 440, 560, 620], "【築陂引水】", "• 修築土堤攔蓄山洪雨水\n• 闢烏山頭與急水溪水利\n• 看天田改造成兩熟良田",
              bg=(18, 30, 49), border=(56, 189, 248), title_color=(56, 189, 248), title_size=18, sub_size=14, border_width=2)
    draw_arrow(draw, (445, 410), (445, 440), color=(56, 189, 248), width=2, arrow_size=10)
    
    draw_card(draw, [640, 270, 1140, 340], "【南路屯墾線】（萬年州主管）", "軍鎮親兵分布・鞏固府治南翼防禦",
              bg=(45, 20, 35), border=(244, 63, 94), title_color=(251, 113, 133), title_size=19)
              
    stations_south = ["鳳山", "前鎮", "後勁", "左營", "萬年城"]
    step_s = (500) / 5
    for i, st in enumerate(stations_south):
        sx = 640 + i * (step_s + 5)
        sy = 360
        draw_card(draw, [sx, sy, sx + step_s - 5, sy + 50], st, "", 
                  bg=(30, 41, 59), border=(100, 116, 139), title_size=15, title_color=(241, 245, 249))
        if i < len(stations_south) - 1:
            draw_arrow(draw, (sx + step_s - 5, sy + 25), (sx + step_s + 5, sy + 25), color=(244, 63, 94), width=2, arrow_size=8)
            
    draw_card(draw, [640, 440, 1140, 620], "【寓兵於農・秋收操練】", 
              "• 各鎮各營劃定責任防區，發給鐵犁、耕牛與種籽，農忙全軍耕耘自給\n• 農隙進行水陸戰陣操演，號令森嚴，隨時防備清荷聯軍突襲海疆\n• 收穫糧穀全歸本營軍餉，不自民間加派一粒糙米，消弭軍民衝突",
              bg=(35, 22, 35), border=(251, 146, 60), title_color=(251, 146, 60), title_size=18, sub_size=14, border_width=2)
    draw_arrow(draw, (890, 410), (890, 440), color=(251, 146, 60), width=2, arrow_size=10)
    
    ft = get_font(13, bold=False)
    draw.text((60, 655), "資料來源：楊英《先王實錄》、夏琳《海紀輯要》、連橫《臺灣通史·陳永華列傳》考證繪製", font=ft, fill=(100, 116, 139))
    
    im.save(out_path, "PNG")
    print(f"[OK] 成功繪製圖表 1: {out_path}")

# =========================================================================
# 圖表 2：第08章【東寧王國科舉文官考選三級體系】
# =========================================================================
def render_ch08_confucian_exam_diagram(out_path):
    W, H = 1200, 750
    im = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(im)
    
    draw.rounded_rectangle([15, 15, W-15, H-15], radius=16, outline=(51, 65, 85), width=2)
    
    font_main = get_font(26, bold=True)
    font_sub = get_font(16, bold=False)
    
    main_title = "【東寧王國科舉文官考選三級體系】"
    sub_title = "全臺首學・建立文官法理法治・首開原住民族教育融合與科舉取士制度"
    
    tb = draw.textbbox((0, 0), main_title, font=font_main)
    draw.text(((W - (tb[2]-tb[0]))/2, 35), main_title, font=font_main, fill=(245, 158, 11))
    
    sb = draw.textbbox((0, 0), sub_title, font=font_sub)
    draw.text(((W - (sb[2]-sb[0]))/2, 75), sub_title, font=font_sub, fill=(148, 163, 184))
    
    card_w = 960
    left_x = (W - card_w) / 2
    right_x = left_x + card_w
    
    top_box = [left_x, 125, right_x, 255]
    draw_card(draw, top_box, "第 3 階：國學大試（全臺首學最高決選）",
              "主考官：延平王鄭經與諮議參軍陳永華親臨主持\n試期規程：三年一大試，錄取者直接由承天府授官（六官之屬與地方知事）\n核心意義：以儒學文官取代武將軍閥專權，將流亡軍團體制轉型為法理國家治理",
              bg=(28, 38, 62), border=(245, 158, 11), title_color=(255, 215, 0), sub_color=(226, 232, 240),
              title_size=20, sub_size=15, border_width=3)
    
    draw_arrow(draw, (W/2, 325), (W/2, 255), color=(245, 158, 11), width=4, arrow_size=14)
    tag_font = get_font(14, bold=True)
    draw.rounded_rectangle([W/2 + 20, 275, W/2 + 160, 305], radius=6, fill=(30, 41, 59), outline=(245, 158, 11), width=1)
    draw.text((W/2 + 30, 281), "▲ 擇優拔擢進入國學", font=tag_font, fill=(245, 158, 11))
    
    mid_box = [left_x, 325, right_x, 455]
    draw_card(draw, mid_box, "第 2 階：州縣科試（府州縣學資格評選）",
              "主辦機構：承天府尹、天興州與萬年州學官教諭共同監考\n考核內容：四書五經義理、經史策論、農田水利與海防貿易時事經世之學\n考核結果：評列一等與二等拔萃士子，保送入承天府「國子學（太學）」深造經筵",
              bg=(20, 35, 55), border=(56, 189, 248), title_color=(56, 189, 248), sub_color=(226, 232, 240),
              title_size=20, sub_size=15, border_width=2)
              
    draw_arrow(draw, (W/2, 525), (W/2, 455), color=(56, 189, 248), width=4, arrow_size=14)
    draw.rounded_rectangle([W/2 + 20, 475, W/2 + 160, 505], radius=6, fill=(30, 41, 59), outline=(56, 189, 248), width=1)
    draw.text((W/2 + 30, 481), "▲ 科試合格保送府學", font=tag_font, fill=(56, 189, 248))
    
    base_box = [left_x, 525, right_x, 675]
    draw_card(draw, base_box, "第 1 階：蒙學歲試（基層社學義塾與平埔族教育）",
              "設立規模：每二十里設一所社學義塾，官府撥給公田租息延請塾師\n招生對象：凡八歲以上軍民子弟均須入學就讀，學習基本漢字與四書童蒙經傳\n平埔政策：首創平埔各社原住民子弟入學免除全家徭役賦稅，開展多元族群文化融合",
              bg=(18, 38, 45), border=(52, 211, 153), title_color=(52, 211, 153), sub_color=(226, 232, 240),
              title_size=20, sub_size=15, border_width=2)
              
    ft = get_font(13, bold=False)
    draw.text((left_x, 705), "史料依據：江日昇《臺灣外記》、沈光文《臺灣輿地纂要》、連橫《臺灣通史》卷十一〈教育志〉", font=ft, fill=(100, 116, 139))
    
    im.save(out_path, "PNG")
    print(f"[OK] 成功繪製圖表 2: {out_path}")

# =========================================================================
# 圖表 3：第08章【1670 年《鄭英通商條約》全球貿易物流網絡】
# =========================================================================
def render_ch08_trade_network_diagram(out_path):
    W, H = 1200, 750
    im = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(im)
    
    draw.rounded_rectangle([15, 15, W-15, H-15], radius=16, outline=(51, 65, 85), width=2)
    
    font_main = get_font(26, bold=True)
    font_sub = get_font(16, bold=False)
    
    main_title = "【1670 年《鄭英通商條約》全球貿易物流網絡】"
    sub_title = "突破滿清遷界禁海・西洋火器換取臺灣蔗糖・融入大航海世界經貿體系"
    
    tb = draw.textbbox((0, 0), main_title, font=font_main)
    draw.text(((W - (tb[2]-tb[0]))/2, 35), main_title, font=font_main, fill=(245, 158, 11))
    
    sb = draw.textbbox((0, 0), sub_title, font=font_sub)
    draw.text(((W - (sb[2]-sb[0]))/2, 75), sub_title, font=font_sub, fill=(148, 163, 184))
    
    box_eic = [70, 130, 420, 280]
    draw_card(draw, box_eic, "英國東印度公司（EIC）", 
              "代表人物：萬丹商館使節\n常設據點：臺灣安平英國商館\n國際定位：正式承認鄭氏政權主權\n給予稱號：The King of Tywan（臺灣國王）",
              bg=(25, 25, 55), border=(129, 140, 248), title_color=(165, 180, 252), sub_color=(226, 232, 240),
              title_size=19, sub_size=14, border_width=3)
              
    box_tung = [780, 130, 1130, 280]
    draw_card(draw, box_tung, "東寧王國（安平王府）", 
              "主政領袖：鄭經（延平王）\n首席謀臣：陳永華（諮議參軍）\n外貿政策：統一進口稅率 3%\n外銷主力：特級白糖、黑糖、鹿皮、生絲",
              bg=(35, 25, 20), border=(245, 158, 11), title_color=(255, 215, 0), sub_color=(226, 232, 240),
              title_size=19, sub_size=14, border_width=3)
              
    draw_arrow(draw, (420, 175), (780, 175), color=(244, 63, 94), width=4, arrow_size=14)
    tag_f = get_font(14, bold=True)
    draw.rounded_rectangle([470, 145, 730, 172], radius=6, fill=(30, 41, 59), outline=(244, 63, 94), width=1)
    draw.text((485, 150), "輸入：燧發洋槍・黑火藥・鉛碇・呢絨", font=tag_f, fill=(251, 113, 133))
    
    draw_arrow(draw, (780, 235), (420, 235), color=(52, 211, 153), width=4, arrow_size=14)
    draw.rounded_rectangle([470, 238, 730, 265], radius=6, fill=(30, 41, 59), outline=(52, 211, 153), width=1)
    draw.text((485, 243), "輸出：優質蔗糖・梅花鹿皮・轉口生絲", font=tag_f, fill=(52, 211, 153))
    
    center_tung_x = 955
    draw.line([(center_tung_x, 280), (center_tung_x, 340)], fill=(148, 163, 184), width=3)
    
    split_left_x = 320
    split_right_x = 880
    draw.line([(split_left_x, 340), (split_right_x, 340)], fill=(148, 163, 184), width=3)
    
    draw_arrow(draw, (split_left_x, 340), (split_left_x, 390), color=(56, 189, 248), width=3, arrow_size=12)
    draw_arrow(draw, (split_right_x, 340), (split_right_x, 390), color=(251, 146, 60), width=3, arrow_size=12)
    
    box_jp = [70, 390, 570, 650]
    draw_card(draw, box_jp, "【日本長崎貿易線】（長崎出島商館）",
              "• 政策待遇：德川幕府特許東寧「洋艘」直靠長崎，免受鎖國牽連\n• 出口商品：年銷數萬擔臺灣蔗糖、梅花鹿皮與華南轉口生絲\n• 輸入戰略物資：寬永通寶銅錢、火器鑄砲用紅銅、鋼鐵武士刀\n• 戰略效益：彌補東寧硬通貨與造砲金屬原料的絕對匱乏",
              bg=(15, 30, 50), border=(56, 189, 248), title_color=(56, 189, 248), sub_color=(226, 232, 240),
              title_size=19, sub_size=15, border_width=2)
              
    box_sea = [630, 390, 1130, 650]
    draw_card(draw, box_sea, "【山海五商走私網絡與南洋貿易】",
              "• 突破清廷遷界令：山商設蘇杭密購，海商設舟山金廈偷渡入臺\n• 秘密走私物資：自內陸採購造船生鐵、軍用硝石、絲織品與藥材\n• 南洋遠洋貿易：船隊航向呂宋（馬尼拉）、暹羅、巴達維亞\n• 戰略效益：瓦解清朝「遷界餓死東寧」意圖，獲取高額貿易順差",
              bg=(35, 25, 15), border=(251, 146, 60), title_color=(251, 146, 60), sub_color=(226, 232, 240),
              title_size=19, sub_size=15, border_width=2)
              
    ft = get_font(13, bold=False)
    draw.text((70, 690), "檔案來源：British East India Company, Factory Records: China and Japan / Formosa (1670)、夏琳《閩海紀要》", font=ft, fill=(100, 116, 139))
    
    im.save(out_path, "PNG")
    print(f"[OK] 成功繪製圖表 3: {out_path}")

# =========================================================================
# 圖表 4：第07章【北線尾海陸遭遇戰 戰術示意圖】
# =========================================================================
def render_ch07_beixianwei_tactics_diagram(out_path):
    W, H = 1200, 720
    im = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(im)
    
    draw.rounded_rectangle([15, 15, W-15, H-15], radius=16, outline=(51, 65, 85), width=2)
    
    font_main = get_font(26, bold=True)
    font_sub = get_font(16, bold=False)
    
    main_title = "【北線尾海陸遭遇戰 雙方戰術部署示意圖】"
    sub_title = "1661 年 5 月 1 日・陳澤籐牌軍低姿態滾進・大破荷蘭莫里斯火槍方陣"
    
    tb = draw.textbbox((0, 0), main_title, font=font_main)
    draw.text(((W - (tb[2]-tb[0]))/2, 35), main_title, font=font_main, fill=(245, 158, 11))
    
    sb = draw.textbbox((0, 0), sub_title, font=font_sub)
    draw.text(((W - (sb[2]-sb[0]))/2, 75), sub_title, font=font_sub, fill=(148, 163, 184))
    
    # 頂部：鹿耳門水道
    draw_card(draw, [W/2 - 220, 120, W/2 + 220, 185], "【鹿耳門水道 / 臺江內海入口】", "明鄭戰船主力游弋封鎖海面・切斷荷軍海上救援路徑",
              bg=(20, 35, 60), border=(56, 189, 248), title_color=(56, 189, 248), title_size=18, sub_size=14)
              
    draw_arrow(draw, (W/2, 185), (W/2, 225), color=(56, 189, 248), width=3, arrow_size=10)
    
    # 左右夾擊兩翼：鄭軍
    draw_card(draw, [80, 220, 480, 330], "【鄭軍左翼伏兵：弓弩隊】", 
              "• 指揮官：侍衛鎮部將\n• 戰術位置：隱蔽於茂密蘆葦與泥灘灌木中\n• 戰術打擊：密集箭雨壓制荷軍兩翼，使其無法展開隊形",
              bg=(20, 40, 40), border=(52, 211, 153), title_color=(52, 211, 153), title_size=18, sub_size=14)
              
    draw_card(draw, [720, 220, 1120, 330], "【陳澤中軍：籐牌精兵】", 
              "• 指揮官：宣毅前鎮陳澤\n• 裝備特性：浸油堅韌圓籐牌、單手鋒利滾刀\n• 戰術突擊：利用射擊硝煙貼地飛滾前進，專斷敵足脛",
              bg=(45, 30, 20), border=(251, 146, 60), title_color=(251, 146, 60), title_size=18, sub_size=14)
              
    # 往中央荷軍斜向引導箭頭
    draw_arrow(draw, (480, 275), (550, 380), color=(52, 211, 153), width=4, arrow_size=14)
    draw_arrow(draw, (720, 275), (650, 380), color=(251, 146, 60), width=4, arrow_size=14)
    
    # 中央核心交戰帶：荷軍火槍方陣
    draw_card(draw, [180, 380, 1020, 500], "【荷軍主力：拔德爾隊長（Thomas Pedel）240 名火槍方陣】",
              "• 戰術體系：17 世紀歐洲先進「莫里斯連鎖排槍射擊法（Maurice Tactics）」\n• 致命弱點：泥沼沙洲機動力大失、缺乏長矛手與騎兵掩護、重型火槍裝填緩慢（需 40 步程序）\n• 戰局結果：拔德爾隊長及 118 名歐洲火槍兵陣亡，方陣瞬間崩潰混亂",
              bg=(45, 20, 25), border=(244, 63, 94), title_color=(251, 113, 133), sub_color=(226, 232, 240),
              title_size=19, sub_size=14, border_width=3)
              
    # 往南水道潰退箭頭
    draw_arrow(draw, (W/2, 500), (W/2, 560), color=(244, 63, 94), width=4, arrow_size=14)
    
    # 底部：殘兵潰退
    draw_card(draw, [W/2 - 250, 560, W/2 + 250, 635], "【南水道潰退線】", "殘存荷蘭士兵丟棄槍械跳海，爭搶舢舨狼狽逃回熱蘭遮城",
              bg=(30, 25, 35), border=(168, 85, 247), title_color=(192, 132, 252), title_size=17, sub_size=14)
              
    ft = get_font(13, bold=False)
    draw.text((80, 670), "資料來源：江樹生譯註《熱蘭遮城日誌》第四冊、揆一《被遺誤的臺灣》、楊英《從征實錄》考證繪製", font=ft, fill=(100, 116, 139))
    
    im.save(out_path, "PNG")
    print(f"[OK] 成功繪製圖表 4: {out_path}")

# =========================================================================
# 圖表 5：第04章【大員轉口貿易三角物流航線示意圖】
# =========================================================================
def render_ch04_trade_routes_diagram(out_path):
    W, H = 1200, 720
    im = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(im)
    
    draw.rounded_rectangle([15, 15, W-15, H-15], radius=16, outline=(51, 65, 85), width=2)
    
    font_main = get_font(26, bold=True)
    font_sub = get_font(16, bold=False)
    
    main_title = "【17 世紀荷蘭東印度公司 大員轉口貿易三角網絡】"
    sub_title = "臺灣大員（熱蘭遮城）為轉運樞紐・連結日本、東南亞與巴達維亞之跨國經貿體系"
    
    tb = draw.textbbox((0, 0), main_title, font=font_main)
    draw.text(((W - (tb[2]-tb[0]))/2, 35), main_title, font=font_main, fill=(245, 158, 11))
    
    sb = draw.textbbox((0, 0), sub_title, font=font_sub)
    draw.text(((W - (sb[2]-sb[0]))/2, 75), sub_title, font=font_sub, fill=(148, 163, 184))
    
    # 頂部：東南亞香料群島
    draw_card(draw, [W/2 - 220, 120, W/2 + 220, 210], "【東南亞（香料群島 / 萬丹）】",
              "產出核心：丁香、肉豆蔻、胡椒、沉香、檀香\n航向大員：運往臺灣轉銷日本與明帝國市場",
              bg=(20, 40, 35), border=(52, 211, 153), title_color=(52, 211, 153), title_size=18, sub_size=14)
              
    # 左側：臺灣大員（樞紐）
    draw_card(draw, [80, 280, 460, 430], "【臺灣大員（熱蘭遮城）】中樞轉運港",
              "• 本土特產：年銷十萬張梅花鹿皮、數萬擔優質蔗糖\n• 轉口大宗：中國生絲、高級綢緞、南京瓷器、中藥材\n• 樞紐地位：VOC 遠東利潤最高之轉口商館（貢獻全公司26%純利）",
              bg=(35, 25, 20), border=(245, 158, 11), title_color=(255, 215, 0), title_size=19, sub_size=14, border_width=3)
              
    # 右側：巴達維亞（VOC 總部）
    draw_card(draw, [740, 280, 1120, 430], "【巴達維亞（東印度公司總督府）】",
              "• 戰略地位：荷蘭東印度公司（VOC）亞洲最高統治中樞\n• 物流運轉：調度全亞洲蓋倫戰艦、火藥軍械、歐洲呢絨白銀\n• 航向阿姆斯特丹：將大員收購之絲綢、香料、瓷器運返歐洲",
              bg=(20, 30, 55), border=(56, 189, 248), title_color=(56, 189, 248), title_size=19, sub_size=14, border_width=3)
              
    # 雙向核心動脈
    draw_arrow(draw, (460, 340), (740, 340), color=(245, 158, 11), width=4, arrow_size=14)
    draw_arrow(draw, (740, 370), (460, 370), color=(56, 189, 248), width=4, arrow_size=14)
    tag_f = get_font(13, bold=True)
    draw.rounded_rectangle([530, 315, 670, 338], radius=6, fill=(30, 41, 59), outline=(245, 158, 11), width=1)
    draw.text((545, 319), "鹿皮・砂糖・絲綢", font=tag_f, fill=(245, 158, 11))
    draw.rounded_rectangle([530, 375, 670, 398], radius=6, fill=(30, 41, 59), outline=(56, 189, 248), width=1)
    draw.text((545, 379), "白銀・軍火・呢絨", font=tag_f, fill=(56, 189, 248))
    
    # 下方：日本長崎（出島商館）
    draw_card(draw, [W/2 - 250, 510, W/2 + 250, 640], "【日本長崎（出島荷蘭商館）】",
              "• 關鍵輸出：石見銀山白銀、寬永通寶、金線、漆器\n• 大額輸入：大員運來之特級生絲、砂糖、臺灣鹿皮\n• 經貿循環：白銀運往大員收購絲綢，形成巨額資本循環",
              bg=(45, 20, 35), border=(244, 63, 94), title_color=(251, 113, 133), title_size=18, sub_size=14)
              
    # 臺灣 -> 日本
    draw_arrow(draw, (270, 430), (W/2 - 150, 510), color=(251, 146, 60), width=3, arrow_size=12)
    # 日本 -> 巴達維亞
    draw_arrow(draw, (W/2 + 150, 510), (930, 430), color=(168, 85, 247), width=3, arrow_size=12)
    
    ft = get_font(13, bold=False)
    draw.text((80, 675), "史料來源：曹永和《臺灣早期歷史研究》、包樂史（Leonard Blussé）《巴達維亞城日記》", font=ft, fill=(100, 116, 139))
    
    im.save(out_path, "PNG")
    print(f"[OK] 成功繪製圖表 5: {out_path}")

def main():
    base_dir = Path("d:/Antigravity/科技歷史/臺灣史")
    
    # 第 08 章
    ch08_img_dir = base_dir / "assets/images/ch08"
    ch08_img_dir.mkdir(parents=True, exist_ok=True)
    render_ch08_military_tuntian_diagram(ch08_img_dir / "ch08_diagram_military_tuntian.png")
    render_ch08_confucian_exam_diagram(ch08_img_dir / "ch08_diagram_confucian_exam.png")
    render_ch08_trade_network_diagram(ch08_img_dir / "ch08_diagram_trade_network.png")
    
    # 第 07 章
    ch07_img_dir = base_dir / "assets/images/ch07"
    ch07_img_dir.mkdir(parents=True, exist_ok=True)
    render_ch07_beixianwei_tactics_diagram(ch07_img_dir / "ch07_diagram_beixianwei_tactics.png")
    
    # 第 04 章
    ch04_img_dir = base_dir / "assets/images/ch04"
    ch04_img_dir.mkdir(parents=True, exist_ok=True)
    render_ch04_trade_routes_diagram(ch04_img_dir / "ch04_diagram_trade_routes.png")

if __name__ == "__main__":
    main()
