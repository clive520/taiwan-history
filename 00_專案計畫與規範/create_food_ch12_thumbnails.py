# -*- coding: utf-8 -*-
import os
import shutil
import urllib.request
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont, ImageOps

# 建立暫存資料夾
temp_dir = "temp_art_ch12"
os.makedirs(temp_dir, exist_ok=True)

# 挑選高品質 Unsplash 歷史/小麥麵粉/麵包烘焙/早餐豆漿/早市老攤地景圖
image_sources = {
    # 師傅雙手揉麵與小麥粉飛揚 (主視覺)
    "baker_hands": "https://images.unsplash.com/photo-1586985289688-ca3cf47d3e6e?w=1920&q=85",
    # 晨光小麥揉麵台
    "flour_knead": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=1920&q=85",
    # 金黃芝麻麵包/剛出爐烤餅
    "sesame_bread": "https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=1920&q=85",
    # 手工餃子/麵食工藝
    "dumplings": "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?w=1920&q=85",
    # 晨光早餐店/傳統烘焙木架暖光
    "bakery_morning": "https://images.unsplash.com/photo-1517433670267-08bbd4be890f?w=1920&q=85",
    # 晨曦市集老攤位/暖黃鎢絲燈
    "morning_stall": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1920&q=85"
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

def apply_wheat_gold_filter(img, warm_tint=(255, 220, 165), vignette_strength=0.45):
    """施加晨光麥香與溫暖懷舊油畫濾鏡"""
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.20)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.15)
    
    overlay = Image.new("RGB", img.size, warm_tint)
    img = Image.blend(img, overlay, 0.11)
    
    # 暈影暗角效果
    w, h = img.size
    vignette = Image.new("L", (w, h), 0)
    v_draw = ImageDraw.Draw(vignette)
    v_draw.ellipse([int(-w*0.18), int(-h*0.18), int(w*1.18), int(h*1.18)], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(w // 8))
    
    black = Image.new("RGB", img.size, (18, 12, 8))
    img = Image.composite(img, black, vignette)
    return img

print("1. Processing Hero Banner (1920x1080)...")
img_baker = Image.open(os.path.join(temp_dir, "baker_hands.jpg")).convert("RGB")
img_baker = ImageOps.fit(img_baker, (1920, 1080), Image.Resampling.LANCZOS)
hero_banner = apply_wheat_gold_filter(img_baker, warm_tint=(255, 225, 175))

draw = ImageDraw.Draw(hero_banner, "RGBA")
for y in range(780, 1080):
    alpha = int(230 * ((y - 780) / 300))
    draw.rectangle([0, y, 1920, y+1], fill=(16, 10, 6, alpha))

f_title = ImageFont.truetype(font_bold, 54)
f_sub = ImageFont.truetype(font_reg, 28)
f_tag = ImageFont.truetype(font_bold, 24)

# 晨光麥金標籤
draw.rectangle([80, 830, 480, 872], fill=(195, 120, 25, 240))
draw.text((100, 836), "【舌尖上的臺灣】第 12 章", fill=(255, 255, 255), font=f_tag)
draw.text((80, 885), "晨光裡的麵粉香", fill=(255, 250, 240), font=f_title)
draw.text((80, 960), "美援麵粉・燒餅油條・清漿與眷村水餃烙餅的庶民突圍", fill=(240, 205, 110), font=f_sub)

os.makedirs("assets/images/food_ch12", exist_ok=True)
os.makedirs("舌尖上的臺灣/assets/images/ch12", exist_ok=True)

hero_banner.save("assets/images/food_ch12/food_ch12_hero_banner.jpg", quality=95)
hero_banner.save("舌尖上的臺灣/assets/images/ch12/food_ch12_hero_banner.jpg", quality=95)

print("2. Processing Dough Craft Banner (1920x1080)...")
# 雙圖無縫拼接：揉麵小麥粉 + 手工水餃
img_flour = Image.open(os.path.join(temp_dir, "flour_knead.jpg")).convert("RGB")
img_flour = ImageOps.fit(img_flour, (960, 1080), Image.Resampling.LANCZOS)

img_dumplings = Image.open(os.path.join(temp_dir, "dumplings.jpg")).convert("RGB")
img_dumplings = ImageOps.fit(img_dumplings, (960, 1080), Image.Resampling.LANCZOS)

craft_banner = Image.new("RGB", (1920, 1080))
craft_banner.paste(img_flour, (0, 0))
craft_banner.paste(img_dumplings, (960, 0))
craft_banner = apply_wheat_gold_filter(craft_banner, warm_tint=(255, 215, 160))

draw_c = ImageDraw.Draw(craft_banner, "RGBA")
for y in range(780, 1080):
    alpha = int(230 * ((y - 780) / 300))
    draw_c.rectangle([0, y, 1920, y+1], fill=(16, 10, 6, alpha))

draw_c.rectangle([80, 830, 520, 872], fill=(160, 95, 20, 240))
draw_c.text((100, 836), "【飲食風土考證】麵食工藝與社會變遷", fill=(255, 255, 255), font=f_tag)
draw_c.text((80, 885), "冷戰美援小麥與永和中正橋頭的庶民早餐史詩", fill=(255, 250, 240), font=f_title)
draw_c.text((80, 960), "公法480號・以麵代米戰略・貼爐炭烤與等電點凝乳科學", fill=(240, 200, 105), font=f_sub)

craft_banner.save("assets/images/food_ch12/food_ch12_dough_craft.jpg", quality=95)
craft_banner.save("舌尖上的臺灣/assets/images/ch12/food_ch12_dough_craft.jpg", quality=95)

print("3. Processing YouTube Short Video Thumbnail (1280x720)...")
yt_thumb = ImageOps.fit(img_baker, (1280, 720), Image.Resampling.LANCZOS)
yt_thumb = apply_wheat_gold_filter(yt_thumb, warm_tint=(255, 225, 175), vignette_strength=0.5)

draw_yt = ImageDraw.Draw(yt_thumb, "RGBA")
for x in range(0, 920):
    alpha = int(225 * (1 - (x / 920)))
    draw_yt.rectangle([x, 0, x+1, 720], fill=(14, 10, 6, alpha))

f_yt_tag = ImageFont.truetype(font_bold, 28)
f_yt_title = ImageFont.truetype(font_bold, 60)
f_yt_sub = ImageFont.truetype(font_bold, 32)
f_yt_extra = ImageFont.truetype(font_reg, 26)

draw_yt.rectangle([60, 55, 480, 105], fill=(200, 120, 20, 240))
draw_yt.text((80, 63), "【舌尖上的臺灣 第12章】", fill=(255, 255, 255), font=f_yt_tag)

draw_yt.text((60, 130), "晨光裡的", fill=(255, 255, 255), font=f_yt_title)
draw_yt.text((60, 205), "麵粉香！", fill=(255, 215, 0), font=f_yt_title)

draw_yt.text((60, 290), "美援麵粉・燒餅油條與永和豆漿傳奇", fill=(255, 240, 190), font=f_yt_sub)

points = [
    "✦  中美合作短褲：美援小麥童年記憶",
    "✦  永和豆漿傳奇：中正橋頭退伍老兵",
    "✦  以麵代米：國家級主食大翻轉",
    "✦  硬核科學：貼爐烘烤與鹹豆漿凝乳"
]

y_pos = 360
for pt in points:
    draw_yt.rectangle([60, y_pos+4, 68, y_pos+26], fill=(235, 140, 30))
    draw_yt.text((80, y_pos), pt, fill=(240, 240, 240), font=f_yt_extra)
    y_pos += 46

draw_yt.rectangle([60, 570, 300, 618], fill=(180, 95, 15, 230))
draw_yt.text((75, 578), "庶民早餐文化史", fill=(255, 255, 255), font=f_yt_tag)

yt_thumb.save("assets/images/food_ch12/food_ch12_youtube_thumbnail.jpg", quality=95)
yt_thumb.save("舌尖上的臺灣/assets/images/ch12/food_ch12_youtube_thumbnail.jpg", quality=95)

print("4. Processing Podcast 1080p Background & 720p Thumbnail (Strict 16:9)...")
img_bakery = Image.open(os.path.join(temp_dir, "bakery_morning.jpg")).convert("RGB")
podcast_bg_1080 = ImageOps.fit(img_bakery, (1920, 1080), Image.Resampling.LANCZOS)
podcast_bg_1080 = apply_wheat_gold_filter(podcast_bg_1080, warm_tint=(255, 220, 170), vignette_strength=0.4)

# 儲存 1920x1080 的 Podcast 影片底圖
podcast_bg_1080.save("assets/images/food_ch12/food_ch12_podcast_bg.jpg", quality=95)
podcast_bg_1080.save("舌尖上的臺灣/assets/images/ch12/food_ch12_podcast_bg.jpg", quality=95)

# 製作 Podcast 專用縮圖 (1280x720)
pod_thumb = ImageOps.fit(podcast_bg_1080, (1280, 720), Image.Resampling.LANCZOS)
draw_pod = ImageDraw.Draw(pod_thumb, "RGBA")

for x in range(0, 960):
    alpha = int(235 * (1 - (x / 960)))
    draw_pod.rectangle([x, 0, x+1, 720], fill=(15, 10, 6, alpha))

f_pod_badge = ImageFont.truetype(font_bold, 26)
f_pod_title = ImageFont.truetype(font_bold, 62)
f_pod_sub = ImageFont.truetype(font_bold, 32)
f_pod_body = ImageFont.truetype(font_reg, 26)

draw_pod.rectangle([60, 55, 520, 105], fill=(215, 125, 25, 240))
draw_pod.text((80, 63), "🎙️ 深度文化播客・文獻對談", fill=(255, 255, 255), font=f_pod_badge)

draw_pod.text((60, 135), "麵香、美援與炭爐", fill=(255, 255, 255), font=f_pod_title)
draw_pod.text((60, 215), "臺灣早餐文化的混血史詩", fill=(255, 215, 0), font=f_pod_title)

draw_pod.text((60, 300), "從中正橋頭豆漿攤到全球華人早餐符號", fill=(255, 240, 190), font=f_pod_sub)

pod_bullets = [
    "1. 中美合作麵粉袋與冷戰 PL 480 法案秘辛",
    "2. 李國鼎與農復會「以麵代米」外匯經濟學",
    "3. 永和豆漿如何演化成「24小時不夜城」",
    "4. 燒餅油酥分層與油條化學氣孔流體力學",
    "5. 鹹豆漿大豆球蛋白 pH 4.5 等電點分子解碼"
]

y_pos = 360
for b in pod_bullets:
    draw_pod.text((60, y_pos), b, fill=(240, 240, 240), font=f_pod_body)
    y_pos += 44

badges = ["1080P 超高畫質", "全正體繁體中文", "飲食人類學考證", "雙人廣播對談"]
bx = 60
for bg_text in badges:
    tw = len(bg_text) * 16 + 24
    draw_pod.rectangle([bx, 600, bx + tw, 640], fill=(35, 22, 12, 220), outline=(210, 130, 30), width=2)
    draw_pod.text((bx + 12, 608), bg_text, fill=(255, 235, 205), font=f_pod_badge)
    bx += tw + 18

pod_thumb.save("assets/images/food_ch12/food_ch12_podcast_thumbnail.jpg", quality=95)
pod_thumb.save("舌尖上的臺灣/assets/images/ch12/food_ch12_podcast_thumbnail.jpg", quality=95)

print("✅ 全部第 12 章視覺素材生成完成！")
