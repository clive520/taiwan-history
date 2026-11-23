# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 14 章視覺素材與雙軌縮圖產製腳本
保證嚴格 16:9 比例、無變形、無拉伸，使用 ImageOps.fit
"""
import os
import shutil
import urllib.request
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont, ImageOps

temp_dir = "temp_art_ch14"
os.makedirs(temp_dir, exist_ok=True)

# 來源原創油畫大作
BOBA_IMAGE = r"C:\Users\admin\.gemini\antigravity\brain\e6ad31e6-5e47-44d3-86ec-3061599c52d4\boba_tea_commercial_miracle_ch14_1795409723761.jpg"

# 挑選高品質 Unsplash 珍珠奶茶/手搖茶/茶藝館/黑糖粉圓實景圖
image_sources = {
    # 經典黑糖珍珠奶茶特寫
    "boba_cup": "https://images.unsplash.com/photo-1558857563-b37cf2d4c062?w=1920&q=85",
    # 手搖茶吧檯製作
    "tea_stall": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=1920&q=85",
    # 溫暖茶館吧檯光影
    "tea_salon": "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=1920&q=85",
    # 傳統茶葉沖泡
    "tea_brew": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=1920&q=85"
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

def apply_amber_caramel_filter(img, warm_tint=(255, 215, 155), vignette_strength=0.45):
    """施加焦糖琥珀與茶香溫暖懷舊油畫濾鏡"""
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.20)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.15)
    
    overlay = Image.new("RGB", img.size, warm_tint)
    img = Image.blend(img, overlay, 0.12)
    
    # 暈影暗角效果
    w, h = img.size
    vignette = Image.new("L", (w, h), 0)
    v_draw = ImageDraw.Draw(vignette)
    v_draw.ellipse([int(-w*0.18), int(-h*0.18), int(w*1.18), int(h*1.18)], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(w // 8))
    
    black = Image.new("RGB", img.size, (16, 10, 6))
    img = Image.composite(img, black, vignette)
    return img

# 確保輸出目錄存在
out_dir_root = "d:/Antigravity/科技歷史/assets/images/food_ch14"
out_dir_tw = "d:/Antigravity/科技歷史/臺灣史/assets/images/food_ch14"
out_dir_food = "d:/Antigravity/科技歷史/臺灣史/舌尖上的臺灣/assets/images/ch14"
for d in [out_dir_root, out_dir_tw, out_dir_food]:
    os.makedirs(d, exist_ok=True)

def save_all_places(img, filename):
    for d in [out_dir_root, out_dir_tw, out_dir_food]:
        dest = os.path.join(d, filename)
        img.save(dest, quality=95)
    print(f" Saved {filename} to 3 directories.")

# 1. Hero Banner (1920x1080)
print("1. Processing Hero Banner (1920x1080)...")
img_boba = Image.open(BOBA_IMAGE).convert("RGB")
hero_banner = ImageOps.fit(img_boba, (1920, 1080), Image.Resampling.LANCZOS)
hero_banner = apply_amber_caramel_filter(hero_banner, warm_tint=(255, 215, 160))

draw_h = ImageDraw.Draw(hero_banner, "RGBA")
for y in range(760, 1080):
    alpha = int(235 * ((y - 760) / 320))
    draw_h.rectangle([0, y, 1920, y+1], fill=(14, 8, 5, alpha))

f_title = ImageFont.truetype(font_bold, 54)
f_sub = ImageFont.truetype(font_reg, 28)
f_tag = ImageFont.truetype(font_bold, 24)

# 典雅焦糖金標籤
draw_h.rectangle([80, 820, 480, 864], fill=(195, 115, 25, 240))
draw_h.text((100, 827), "【舌尖上的臺灣】第 14 章", fill=(255, 255, 255), font=f_tag)
draw_h.text((80, 880), "吸管裡的黑色奇蹟", fill=(255, 250, 240), font=f_title)
draw_h.text((80, 955), "春水堂、翰林與珍珠奶茶席捲全球百億美元的商業神話", fill=(245, 215, 120), font=f_sub)

save_all_places(hero_banner, "food_ch14_hero_banner.jpg")

# 2. Bubble Tea Craft Banner (1920x1080)
print("2. Processing Bubble Tea Craft Banner (1920x1080)...")
path_stall = os.path.join(temp_dir, "tea_stall.jpg")
path_brew = os.path.join(temp_dir, "tea_brew.jpg")

img_stall = Image.open(path_stall).convert("RGB")
img_stall = ImageOps.fit(img_stall, (960, 1080), Image.Resampling.LANCZOS)

img_brew = Image.open(path_brew).convert("RGB")
img_brew = ImageOps.fit(img_brew, (960, 1080), Image.Resampling.LANCZOS)

craft_banner = Image.new("RGB", (1920, 1080))
craft_banner.paste(img_stall, (0, 0))
craft_banner.paste(img_brew, (960, 0))
craft_banner = apply_amber_caramel_filter(craft_banner, warm_tint=(255, 210, 150))

draw_c = ImageDraw.Draw(craft_banner, "RGBA")
for y in range(760, 1080):
    alpha = int(235 * ((y - 760) / 320))
    draw_c.rectangle([0, y, 1920, y+1], fill=(14, 8, 5, alpha))

draw_c.rectangle([80, 820, 520, 864], fill=(175, 95, 20, 240))
draw_c.text((100, 827), "【飲食風土考證】手搖工藝與商業出海", fill=(255, 255, 255), font=f_tag)
draw_c.text((80, 880), "雪克杯微氣泡、益芳封口機與雙相流體力學", fill=(255, 250, 240), font=f_title)
draw_c.text((80, 955), "打破茶只熱飲禁忌・45度斜口粗吸管破膜・樹薯澱粉Q度與四小時老化時效", fill=(245, 210, 110), font=f_sub)

save_all_places(craft_banner, "food_ch14_bubbletea_craft.jpg")

# 3. YouTube Short Video Thumbnail (1280x720)
print("3. Processing YouTube Video Thumbnail (1280x720)...")
yt_thumb = ImageOps.fit(img_boba, (1280, 720), Image.Resampling.LANCZOS)
yt_thumb = apply_amber_caramel_filter(yt_thumb, warm_tint=(255, 215, 160), vignette_strength=0.5)

draw_yt = ImageDraw.Draw(yt_thumb, "RGBA")
for x in range(0, 920):
    alpha = int(230 * (1 - (x / 920)))
    draw_yt.rectangle([x, 0, x+1, 720], fill=(14, 8, 5, alpha))

f_yt_tag = ImageFont.truetype(font_bold, 28)
f_yt_title = ImageFont.truetype(font_bold, 60)
f_yt_sub = ImageFont.truetype(font_bold, 32)
f_yt_extra = ImageFont.truetype(font_reg, 26)

draw_yt.rectangle([60, 55, 480, 105], fill=(200, 120, 20, 240))
draw_yt.text((80, 63), "【舌尖上的臺灣 第14章】", fill=(255, 255, 255), font=f_yt_tag)

draw_yt.text((60, 130), "吸管裡的", fill=(255, 255, 255), font=f_yt_title)
draw_yt.text((60, 205), "黑色奇蹟！", fill=(255, 215, 0), font=f_yt_title)

draw_yt.text((60, 290), "春水堂、翰林與珍奶百億美元神話", fill=(255, 240, 190), font=f_yt_sub)

points = [
    "✦  四維街雪克杯：打破千年茶道冷飲禁忌",
    "✦  世紀發明公案：春水堂 vs 翰林茶館判決",
    "✦  街頭工業革命：益芳封口機與斜口粗吸管",
    "✦  硬核分子科學：樹薯澱粉Q度與老化時效"
]

y_pos = 360
for pt in points:
    draw_yt.rectangle([60, y_pos+4, 68, y_pos+26], fill=(235, 135, 25))
    draw_yt.text((80, y_pos), pt, fill=(240, 240, 240), font=f_yt_extra)
    y_pos += 46

draw_yt.rectangle([60, 570, 320, 618], fill=(180, 100, 15, 230))
draw_yt.text((75, 578), "手搖茶全球擴張史", fill=(255, 255, 255), font=f_yt_tag)

save_all_places(yt_thumb, "food_ch14_youtube_thumbnail.jpg")

# 4. Podcast 1080p Background & 720p Thumbnail (Strict 16:9)
print("4. Processing Podcast 1080p Background & 720p Thumbnail...")
path_salon = os.path.join(temp_dir, "tea_salon.jpg")
img_salon = Image.open(path_salon).convert("RGB")
podcast_bg_1080 = ImageOps.fit(img_salon, (1920, 1080), Image.Resampling.LANCZOS)
podcast_bg_1080 = apply_amber_caramel_filter(podcast_bg_1080, warm_tint=(255, 215, 155), vignette_strength=0.42)

# 儲存純淨 1080p 影片底圖
save_all_places(podcast_bg_1080, "food_ch14_podcast_bg.jpg")

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

draw_pod.rectangle([60, 55, 520, 105], fill=(210, 125, 25, 240))
draw_pod.text((80, 63), "🎙️ 深度文化播客・文獻對談", fill=(255, 255, 255), font=f_pod_badge)

draw_pod.text((60, 135), "黑珍珠、封口機", fill=(255, 255, 255), font=f_pod_title)
draw_pod.text((60, 215), "臺灣手搖茶的全球商業帝國", fill=(255, 215, 0), font=f_pod_title)

draw_pod.text((60, 300), "從四維街老木吧檯到巴黎羅浮宮的感官征服", fill=(255, 240, 190), font=f_pod_sub)

pod_bullets = [
    "1. 陽羨茶行雪克杯如何用微氣泡物理包覆兒茶素？",
    "2. 春水堂林秀慧 vs 翰林涂宗和十年訴訟司法定論",
    "3. 益芳封口機 0.8 秒熱熔拯救機車外送的工業奇蹟",
    "4. 45 度斜口粗吸管破膜應力與雙相流體吸吮力學",
    "5. 樹薯澱粉 85% 支鏈澱粉「Q度」與四小時老化時效"
]

y_pos = 360
for b in pod_bullets:
    draw_pod.text((60, y_pos), b, fill=(240, 240, 240), font=f_pod_body)
    y_pos += 44

badges = ["1080P 超高畫質", "全正體繁體中文", "飲食人類學考證", "雙人廣播對談"]
bx = 60
for bg_text in badges:
    tw = len(bg_text) * 16 + 24
    draw_pod.rectangle([bx, 600, bx + tw, 640], fill=(35, 20, 12, 220), outline=(215, 130, 30), width=2)
    draw_pod.text((bx + 12, 608), bg_text, fill=(255, 235, 205), font=f_pod_badge)
    bx += tw + 18

save_all_places(pod_thumb, "food_ch14_podcast_thumbnail.jpg")

print("🎉 全部第 14 章視覺素材與縮圖生成完成！嚴格 16:9，無拉伸！")
