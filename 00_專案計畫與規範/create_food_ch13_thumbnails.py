# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 13 章視覺素材與雙軌縮圖產製腳本
保證嚴格 16:9 比例、無變形、無拉伸，使用 ImageOps.fit
"""
import os
import shutil
import urllib.request
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont, ImageOps

temp_dir = "temp_art_ch13"
os.makedirs(temp_dir, exist_ok=True)

# 來源原創油畫大作
BANDO_IMAGE = r"C:\Users\admin\.gemini\antigravity\brain\e6ad31e6-5e47-44d3-86ec-3061599c52d4\taiwan_bando_master_chef_legend_v2_1795403963696.jpg"

# 挑選高品質 Unsplash 夜市/鐵板燒/熱炒/街頭大排檔實景高畫質圖
image_sources = {
    # 亞洲熱鬧夜市街景、鎢絲燈光、熱氣騰騰
    "night_market_street": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1920&q=85",
    # 街頭鐵板翻炒、金黃鑊氣與油煙
    "wok_stirfry": "https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=1920&q=85",
    # 酥脆金黃炸物/街頭小吃
    "fried_food": "https://images.unsplash.com/photo-1562967914-608f82629710?w=1920&q=85",
    # 蒸籠白煙瀰漫/中式老餐館
    "steamer_steam": "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?w=1920&q=85",
    # 深夜食堂溫暖燈光排檔
    "midnight_diner": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1920&q=85"
}

headers = {'User-Agent': 'Mozilla/5.0'}

for name, url in image_sources.items():
    path = os.path.join(temp_dir, f"{name}.jpg")
    if not os.path.exists(path):
        print(f"Downloading {name}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as resp, open(path, 'wb') as f:
                f.write(resp.read())
        except Exception as e:
            print(f"Failed to download {name}: {e}")

font_bold = "C:/Windows/Fonts/msjhbd.ttc"
font_reg = "C:/Windows/Fonts/msjh.ttc"

def apply_night_warmth_filter(img, warm_tint=(255, 215, 160), vignette_strength=0.45):
    """施加夜市燈火與溫暖懷舊油畫濾鏡"""
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.22)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.18)
    
    overlay = Image.new("RGB", img.size, warm_tint)
    img = Image.blend(img, overlay, 0.12)
    
    # 暈影暗角效果
    w, h = img.size
    vignette = Image.new("L", (w, h), 0)
    v_draw = ImageDraw.Draw(vignette)
    v_draw.ellipse([int(-w*0.18), int(-h*0.18), int(w*1.18), int(h*1.18)], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(w // 8))
    
    black = Image.new("RGB", img.size, (15, 10, 8))
    img = Image.composite(img, black, vignette)
    return img

# 確保輸出目錄存在
out_dir_root = "d:/Antigravity/科技歷史/assets/images/food_ch13"
out_dir_tw = "d:/Antigravity/科技歷史/臺灣史/assets/images/food_ch13"
out_dir_food = "d:/Antigravity/科技歷史/臺灣史/舌尖上的臺灣/assets/images/ch13"
for d in [out_dir_root, out_dir_tw, out_dir_food]:
    os.makedirs(d, exist_ok=True)

def save_all_places(img, filename):
    for d in [out_dir_root, out_dir_tw, out_dir_food]:
        dest = os.path.join(d, filename)
        img.save(dest, quality=95)
    print(f" Saved {filename} to 3 directories.")

# 1. Hero Banner (1920x1080)
print("1. Processing Hero Banner (1920x1080)...")
img_bando = Image.open(BANDO_IMAGE).convert("RGB")
hero_banner = ImageOps.fit(img_bando, (1920, 1080), Image.Resampling.LANCZOS)
hero_banner = apply_night_warmth_filter(hero_banner, warm_tint=(255, 210, 155))

draw_h = ImageDraw.Draw(hero_banner, "RGBA")
for y in range(760, 1080):
    alpha = int(235 * ((y - 760) / 320))
    draw_h.rectangle([0, y, 1920, y+1], fill=(14, 8, 5, alpha))

f_title = ImageFont.truetype(font_bold, 54)
f_sub = ImageFont.truetype(font_reg, 28)
f_tag = ImageFont.truetype(font_bold, 24)

# 典雅暗紅喜慶標籤
draw_h.rectangle([80, 820, 480, 864], fill=(190, 45, 30, 240))
draw_h.text((100, 827), "【舌尖上的臺灣】第 13 章", fill=(255, 255, 255), font=f_tag)
draw_h.text((80, 880), "黑夜裡的流動盛宴", fill=(255, 250, 240), font=f_title)
draw_h.text((80, 955), "辦桌文化的鼎盛・夜市宵夜經濟與「客廳即工廠」的深夜慰藉", fill=(245, 210, 120), font=f_sub)

save_all_places(hero_banner, "food_ch13_hero_banner.jpg")

# 2. Night Market Craft Banner (1920x1080)
print("2. Processing Night Market Craft Banner (1920x1080)...")
# 雙圖拼接：鐵板翻炒鑊氣 + 酥脆金黃小吃
path_wok = os.path.join(temp_dir, "wok_stirfry.jpg")
path_fried = os.path.join(temp_dir, "fried_food.jpg")

img_wok = Image.open(path_wok).convert("RGB")
img_wok = ImageOps.fit(img_wok, (960, 1080), Image.Resampling.LANCZOS)

img_fried = Image.open(path_fried).convert("RGB")
img_fried = ImageOps.fit(img_fried, (960, 1080), Image.Resampling.LANCZOS)

craft_banner = Image.new("RGB", (1920, 1080))
craft_banner.paste(img_wok, (0, 0))
craft_banner.paste(img_fried, (960, 0))
craft_banner = apply_night_warmth_filter(craft_banner, warm_tint=(255, 205, 145))

draw_c = ImageDraw.Draw(craft_banner, "RGBA")
for y in range(760, 1080):
    alpha = int(235 * ((y - 760) / 320))
    draw_c.rectangle([0, y, 1920, y+1], fill=(14, 8, 5, alpha))

draw_c.rectangle([80, 820, 520, 864], fill=(180, 70, 20, 240))
draw_c.text((100, 827), "【飲食風土考證】夜市宵夜與代工經濟", fill=(255, 255, 255), font=f_tag)
draw_c.text((80, 880), "黑手女工的深夜慰藉與街頭分子烹飪科學", fill=(255, 250, 240), font=f_title)
draw_c.text((80, 955), "客廳即工廠・三班倒卡路里後勤・蚵仔煎雙澱粉羽衣與九層塔丁香酚炸裂", fill=(245, 205, 110), font=f_sub)

save_all_places(craft_banner, "food_ch13_nightmarket_craft.jpg")

# 3. YouTube Short Video Thumbnail (1280x720)
print("3. Processing YouTube Video Thumbnail (1280x720)...")
yt_thumb = ImageOps.fit(img_bando, (1280, 720), Image.Resampling.LANCZOS)
yt_thumb = apply_night_warmth_filter(yt_thumb, warm_tint=(255, 215, 160), vignette_strength=0.5)

draw_yt = ImageDraw.Draw(yt_thumb, "RGBA")
for x in range(0, 920):
    alpha = int(230 * (1 - (x / 920)))
    draw_yt.rectangle([x, 0, x+1, 720], fill=(14, 8, 5, alpha))

f_yt_tag = ImageFont.truetype(font_bold, 28)
f_yt_title = ImageFont.truetype(font_bold, 60)
f_yt_sub = ImageFont.truetype(font_bold, 32)
f_yt_extra = ImageFont.truetype(font_reg, 26)

draw_yt.rectangle([60, 55, 480, 105], fill=(195, 40, 25, 240))
draw_yt.text((80, 63), "【舌尖上的臺灣 第13章】", fill=(255, 255, 255), font=f_yt_tag)

draw_yt.text((60, 130), "黑夜裡的", fill=(255, 255, 255), font=f_yt_title)
draw_yt.text((60, 205), "流動盛宴！", fill=(255, 215, 0), font=f_yt_title)

draw_yt.text((60, 290), "總鋪師傳奇・夜市宵夜與客廳即工廠", fill=(255, 240, 190), font=f_yt_sub)

points = [
    "✦  高雄內門傳奇：惡地宋江陣到總鋪師之鄉",
    "✦  柏油路上的盛唐：封街搭棚空間游擊戰",
    "✦  勞工深夜救贖：三班倒加工出口區宵夜狂潮",
    "✦  硬核烹飪科學：大封肉明膠化與雙澱粉羽衣"
]

y_pos = 360
for pt in points:
    draw_yt.rectangle([60, y_pos+4, 68, y_pos+26], fill=(235, 80, 30))
    draw_yt.text((80, y_pos), pt, fill=(240, 240, 240), font=f_yt_extra)
    y_pos += 46

draw_yt.rectangle([60, 570, 320, 618], fill=(180, 50, 20, 230))
draw_yt.text((75, 578), "流動宴飲文化史", fill=(255, 255, 255), font=f_yt_tag)

save_all_places(yt_thumb, "food_ch13_youtube_thumbnail.jpg")

# 4. Podcast 1080p Background & 720p Thumbnail (Strict 16:9)
print("4. Processing Podcast 1080p Background & 720p Thumbnail...")
# 底圖以溫暖夜市街景為基底，乾淨高貴、嚴禁變形
path_diner = os.path.join(temp_dir, "night_market_street.jpg")
img_diner = Image.open(path_diner).convert("RGB")
podcast_bg_1080 = ImageOps.fit(img_diner, (1920, 1080), Image.Resampling.LANCZOS)
podcast_bg_1080 = apply_night_warmth_filter(podcast_bg_1080, warm_tint=(255, 210, 150), vignette_strength=0.42)

# 儲存純淨 1080p 影片底圖
save_all_places(podcast_bg_1080, "food_ch13_podcast_bg.jpg")

# 製作 Podcast 專用縮圖 (1280x720)
pod_thumb = ImageOps.fit(podcast_bg_1080, (1280, 720), Image.Resampling.LANCZOS)
draw_pod = ImageDraw.Draw(pod_thumb, "RGBA")

for x in range(0, 960):
    alpha = int(235 * (1 - (x / 960)))
    draw_pod.rectangle([x, 0, x+1, 720], fill=(14, 8, 5, alpha))

f_pod_badge = ImageFont.truetype(font_bold, 26)
f_pod_title = ImageFont.truetype(font_bold, 62)
f_pod_sub = ImageFont.truetype(font_bold, 32)
f_pod_body = ImageFont.truetype(font_reg, 26)

draw_pod.rectangle([60, 55, 520, 105], fill=(205, 45, 25, 240))
draw_pod.text((80, 63), "🎙️ 深度文化播客・文獻對談", fill=(255, 255, 255), font=f_pod_badge)

draw_pod.text((60, 135), "烈火、夜市與大鐵勺", fill=(255, 255, 255), font=f_pod_title)
draw_pod.text((60, 215), "臺灣外燴與深夜食堂的社會史詩", fill=(255, 215, 0), font=f_pod_title)

draw_pod.text((60, 300), "從內門泥岩惡地到全球代工霸主的卡路里後勤", fill=(255, 240, 190), font=f_pod_sub)

pod_bullets = [
    "1. 內門羅漢門惡地為何誕生全臺密度最高總鋪師？",
    "2. 封街搭棚、砌臨時大灶的流動空間建築學",
    "3. 謝東閔「客廳即工廠」與加工出口區三班倒夜市經濟",
    "4. 大封肉 85°C 明膠化與扁魚白菜滷 8 倍鮮味核爆",
    "5. 蚵仔煎雙澱粉羽衣與鹽酥雞九層塔丁香酚炸裂"
]

y_pos = 360
for b in pod_bullets:
    draw_pod.text((60, y_pos), b, fill=(240, 240, 240), font=f_pod_body)
    y_pos += 44

badges = ["1080P 超高畫質", "全正體繁體中文", "飲食人類學考證", "雙人廣播對談"]
bx = 60
for bg_text in badges:
    tw = len(bg_text) * 16 + 24
    draw_pod.rectangle([bx, 600, bx + tw, 640], fill=(35, 18, 12, 220), outline=(215, 60, 30), width=2)
    draw_pod.text((bx + 12, 608), bg_text, fill=(255, 235, 205), font=f_pod_badge)
    bx += tw + 18

save_all_places(pod_thumb, "food_ch13_podcast_thumbnail.jpg")

print("🎉 全部第 13 章視覺素材與縮圖生成完成！嚴格 16:9，無拉伸！")
