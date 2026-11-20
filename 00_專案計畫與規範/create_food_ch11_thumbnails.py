# -*- coding: utf-8 -*-
import os
import shutil
import urllib.request
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont, ImageOps

# 建立暫存資料夾
temp_dir = "temp_art_ch11"
os.makedirs(temp_dir, exist_ok=True)

# 挑選高品質 Unsplash 歷史/牛肉麵/香料辣椒/夜市老攤地景圖
image_sources = {
    # 頂級精緻熱氣騰騰牛肉麵大碗 (主視覺)
    "beef_noodles": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=1920&q=85",
    # 濃郁紅湯拉麵/燉牛肉高湯
    "ramen_bowl": "https://images.unsplash.com/photo-1552611052-33e04de081de?w=1920&q=85",
    # 四川傳統辣椒香料八角與醬料台
    "chili_spices": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=1920&q=85",
    # 復古夜市攤位 / 暖黃鎢絲燈老巷弄
    "night_stall": "https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=1920&q=85",
    # 復古懷舊亞洲老街景
    "vintage_street": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1920&q=85",
    # 咕嘟慢燉厚底鐵鍋高湯
    "pot_simmer": "https://images.unsplash.com/photo-1547592180-85f173990554?w=1920&q=85"
}

headers = {'User-Agent': 'Mozilla/5.0'}

for name, url in image_sources.items():
    path = os.path.join(temp_dir, f"{name}.jpg")
    if not os.path.exists(path):
        print(f"Downloading {name}...")
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp, open(path, 'wb') as f:
            f.write(resp.read())

font_bold = "C:/Windows/Fonts/msjhbd.ttc"
font_reg = "C:/Windows/Fonts/msjh.ttc"

def apply_crimson_nostalgia_filter(img, warm_tint=(255, 210, 170), vignette_strength=0.45):
    """施加眷村紅湯溫暖懷舊油畫濾鏡"""
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.22)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.16)
    
    overlay = Image.new("RGB", img.size, warm_tint)
    img = Image.blend(img, overlay, 0.10)
    
    # 暈影暗角效果
    w, h = img.size
    vignette = Image.new("L", (w, h), 0)
    v_draw = ImageDraw.Draw(vignette)
    v_draw.ellipse([int(-w*0.18), int(-h*0.18), int(w*1.18), int(h*1.18)], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(w // 8))
    
    black = Image.new("RGB", img.size, (20, 10, 8))
    img = Image.composite(img, black, vignette)
    return img

print("1. Processing Hero Banner (1920x1080)...")
img_noodles = Image.open(os.path.join(temp_dir, "beef_noodles.jpg")).convert("RGB")
img_noodles = ImageOps.fit(img_noodles, (1920, 1080), Image.Resampling.LANCZOS)
hero_banner = apply_crimson_nostalgia_filter(img_noodles, warm_tint=(255, 215, 170))

draw = ImageDraw.Draw(hero_banner, "RGBA")
for y in range(780, 1080):
    alpha = int(230 * ((y - 780) / 300))
    draw.rectangle([0, y, 1920, y+1], fill=(16, 8, 6, alpha))

f_title = ImageFont.truetype(font_bold, 54)
f_sub = ImageFont.truetype(font_reg, 28)
f_tag = ImageFont.truetype(font_bold, 24)

# 眷村紅牌標籤
draw.rectangle([80, 830, 480, 872], fill=(186, 42, 28, 240))
draw.text((100, 836), "【舌尖上的臺灣】第 11 章", fill=(255, 255, 255), font=f_tag)
draw.text((80, 885), "那一碗鄉愁的紅湯", fill=(255, 248, 235), font=f_title)
draw.text((80, 960), "岡山豆瓣醬・四川老兵・臺灣紅燒牛肉麵的混血傳奇", fill=(235, 195, 105), font=f_sub)

os.makedirs("assets/images/food_ch11", exist_ok=True)
os.makedirs("舌尖上的臺灣/assets/images/ch11", exist_ok=True)

hero_banner.save("assets/images/food_ch11/food_ch11_hero_banner.jpg", quality=95)
hero_banner.save("舌尖上的臺灣/assets/images/ch11/food_ch11_hero_banner.jpg", quality=95)

print("2. Processing Beef Noodle Craft Banner (1920x1080)...")
# 雙圖無縫拼接：辣椒豆瓣香料 + 慢燉鐵鍋
img_spices = Image.open(os.path.join(temp_dir, "chili_spices.jpg")).convert("RGB")
img_spices = ImageOps.fit(img_spices, (960, 1080), Image.Resampling.LANCZOS)

img_pot = Image.open(os.path.join(temp_dir, "pot_simmer.jpg")).convert("RGB")
img_pot = ImageOps.fit(img_pot, (960, 1080), Image.Resampling.LANCZOS)

craft_banner = Image.new("RGB", (1920, 1080))
craft_banner.paste(img_spices, (0, 0))
craft_banner.paste(img_pot, (960, 0))
craft_banner = apply_crimson_nostalgia_filter(craft_banner, warm_tint=(255, 205, 160))

draw_c = ImageDraw.Draw(craft_banner, "RGBA")
for y in range(780, 1080):
    alpha = int(230 * ((y - 780) / 300))
    draw_c.rectangle([0, y, 1920, y+1], fill=(16, 8, 6, alpha))

draw_c.rectangle([80, 830, 520, 872], fill=(145, 35, 22, 240))
draw_c.text((100, 836), "【飲食風土考證】工藝與社會變遷", fill=(255, 255, 255), font=f_tag)
draw_c.text((80, 885), "岡山日曬豆瓣醬與打破敬牛傳統的肉食革命", fill=(255, 248, 235), font=f_title)
draw_c.text((80, 960), "劉明德黃豆改良工藝・美援麵粉普及・桃源街克難麵攤奇蹟", fill=(235, 190, 100), font=f_sub)

craft_banner.save("assets/images/food_ch11/food_ch11_beef_noodle_craft.jpg", quality=95)
craft_banner.save("舌尖上的臺灣/assets/images/ch11/food_ch11_beef_noodle_craft.jpg", quality=95)

print("3. Processing YouTube Short Video Thumbnail (1280x720)...")
yt_thumb = ImageOps.fit(img_noodles, (1280, 720), Image.Resampling.LANCZOS)
yt_thumb = apply_crimson_nostalgia_filter(yt_thumb, warm_tint=(255, 215, 175), vignette_strength=0.5)

draw_yt = ImageDraw.Draw(yt_thumb, "RGBA")
for x in range(0, 920):
    alpha = int(225 * (1 - (x / 920)))
    draw_yt.rectangle([x, 0, x+1, 720], fill=(14, 8, 6, alpha))

f_yt_tag = ImageFont.truetype(font_bold, 28)
f_yt_title = ImageFont.truetype(font_bold, 60)
f_yt_sub = ImageFont.truetype(font_bold, 32)
f_yt_extra = ImageFont.truetype(font_reg, 26)

draw_yt.rectangle([60, 55, 480, 105], fill=(195, 40, 25, 240))
draw_yt.text((80, 63), "【舌尖上的臺灣 第11章】", fill=(255, 255, 255), font=f_yt_tag)

draw_yt.text((60, 130), "那一碗", fill=(255, 255, 255), font=f_yt_title)
draw_yt.text((60, 205), "鄉愁的紅湯！", fill=(255, 215, 0), font=f_yt_title)

draw_yt.text((60, 290), "岡山豆瓣醬・四川老兵與紅燒牛肉麵", fill=(255, 235, 180), font=f_yt_sub)

points = [
    "✦  四川沒有的牛肉麵：臺灣獨創傳奇",
    "✦  岡山烈日與劉明德黃豆豆瓣醬秘辛",
    "✦  打破敬牛禁忌：美援麵粉與戰後都市化",
    "✦  分子料理學：明膠水解與發酵酸菜協同"
]

y_pos = 360
for pt in points:
    draw_yt.rectangle([60, y_pos+4, 68, y_pos+26], fill=(235, 60, 35))
    draw_yt.text((80, y_pos), pt, fill=(240, 240, 240), font=f_yt_extra)
    y_pos += 46

draw_yt.rectangle([60, 570, 300, 618], fill=(185, 30, 20, 230))
draw_yt.text((75, 578), "國食文化混血史", fill=(255, 255, 255), font=f_yt_tag)

yt_thumb.save("assets/images/food_ch11/food_ch11_youtube_thumbnail.jpg", quality=95)
yt_thumb.save("舌尖上的臺灣/assets/images/ch11/food_ch11_youtube_thumbnail.jpg", quality=95)

print("4. Processing Podcast 1080p Background & 720p Thumbnail (Strict 16:9)...")
# 背景圖必須是精緻、未變形、暖色調的高解析 1920x1080
# 選用復古老巷弄與暖黃燈光
img_night = Image.open(os.path.join(temp_dir, "night_stall.jpg")).convert("RGB")
podcast_bg_1080 = ImageOps.fit(img_night, (1920, 1080), Image.Resampling.LANCZOS)
podcast_bg_1080 = apply_crimson_nostalgia_filter(podcast_bg_1080, warm_tint=(255, 210, 165), vignette_strength=0.4)

# 儲存 1920x1080 的 Podcast 影片底圖
podcast_bg_1080.save("assets/images/food_ch11/food_ch11_podcast_bg.jpg", quality=95)
podcast_bg_1080.save("舌尖上的臺灣/assets/images/ch11/food_ch11_podcast_bg.jpg", quality=95)

# 製作 Podcast 專用縮圖 (1280x720)
pod_thumb = ImageOps.fit(podcast_bg_1080, (1280, 720), Image.Resampling.LANCZOS)
draw_pod = ImageDraw.Draw(pod_thumb, "RGBA")

for x in range(0, 960):
    alpha = int(235 * (1 - (x / 960)))
    draw_pod.rectangle([x, 0, x+1, 720], fill=(15, 8, 6, alpha))

f_pod_badge = ImageFont.truetype(font_bold, 26)
f_pod_title = ImageFont.truetype(font_bold, 62)
f_pod_sub = ImageFont.truetype(font_bold, 32)
f_pod_body = ImageFont.truetype(font_reg, 26)

draw_pod.rectangle([60, 55, 520, 105], fill=(210, 50, 30, 240))
draw_pod.text((80, 63), "🎙️ 深度文化播客・文獻對談", fill=(255, 255, 255), font=f_pod_badge)

draw_pod.text((60, 135), "紅湯、鄉愁與眷村", fill=(255, 255, 255), font=f_pod_title)
draw_pod.text((60, 215), "臺灣紅燒牛肉麵的混血傳奇", fill=(255, 215, 0), font=f_pod_title)

draw_pod.text((60, 300), "從岡山日曬辣豆瓣到征服世界的國民國食", fill=(255, 235, 180), font=f_pod_sub)

pod_bullets = [
    "1. 梁實秋《雅舍談吃》的四川原鄉牛肉麵之謎",
    "2. 岡山空軍機校與劉明德改良黃豆辣豆瓣醬",
    "3. 美援麵粉潮與打破臺灣傳統「敬牛農耕戒律」",
    "4. 桃源街與寶慶路防空洞的戰後庶民經濟記憶",
    "5. 硬核解碼：牛腱明膠水解與發酵酸菜分子協同"
]

y_pos = 360
for b in pod_bullets:
    draw_pod.text((60, y_pos), b, fill=(240, 240, 240), font=f_pod_body)
    y_pos += 44

badges = ["1080P 超高畫質", "全正體繁體中文", "飲食人類學考證", "雙人廣播對談"]
bx = 60
for bg_text in badges:
    tw = len(bg_text) * 16 + 24
    draw_pod.rectangle([bx, 600, bx + tw, 640], fill=(40, 20, 15, 220), outline=(200, 60, 40), width=2)
    draw_pod.text((bx + 12, 608), bg_text, fill=(255, 230, 200), font=f_pod_badge)
    bx += tw + 18

pod_thumb.save("assets/images/food_ch11/food_ch11_podcast_thumbnail.jpg", quality=95)
pod_thumb.save("舌尖上的臺灣/assets/images/ch11/food_ch11_podcast_thumbnail.jpg", quality=95)

print("✅ 全部第 11 章視覺素材生成完成！")
