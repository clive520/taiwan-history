import os
import shutil
import urllib.request
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont

# 建立暫存資料夾
temp_dir = "temp_art_ch10"
os.makedirs(temp_dir, exist_ok=True)

# 挑選高品質 Unsplash 歷史/茶葉地景圖
image_sources = {
    # 梯田茶山 / 山嵐晨霧
    "teahills": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=1920&q=85",
    # 琥珀色茶湯 / 晶透玻璃茶器
    "teacup": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=1920&q=85",
    # 古典港口 / 帆船水岸
    "port": "https://images.unsplash.com/photo-1506477331477-33d5d8b3dc85?w=1920&q=85",
    # 茶葉工藝 / 乾茶五色芽
    "leaves": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?w=1920&q=85"
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

def apply_tea_gold_filter(img, warm_tint=(255, 230, 190), vignette_strength=0.4):
    """施加茶金琥珀油畫復古濾鏡"""
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.2)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.18)
    
    overlay = Image.new("RGB", img.size, warm_tint)
    img = Image.blend(img, overlay, 0.12)
    
    # 暗角效果
    w, h = img.size
    vignette = Image.new("L", (w, h), 0)
    v_draw = ImageDraw.Draw(vignette)
    v_draw.ellipse([int(-w*0.2), int(-h*0.2), int(w*1.2), int(h*1.2)], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(w // 8))
    
    black = Image.new("RGB", img.size, (18, 12, 6))
    img = Image.composite(img, black, vignette)
    return img

print("Processing Hero Banner (1920x1080)...")
# 1. Hero Banner: 梯田茶山 + 山嵐
img_hills = Image.open(os.path.join(temp_dir, "teahills.jpg")).convert("RGB")
img_hills = img_hills.resize((1920, 1080), Image.Resampling.LANCZOS)
hero_banner = apply_tea_gold_filter(img_hills, warm_tint=(255, 225, 175))

draw = ImageDraw.Draw(hero_banner, "RGBA")
for y in range(800, 1080):
    alpha = int(220 * ((y - 800) / 280))
    draw.rectangle([0, y, 1920, y+1], fill=(15, 12, 8, alpha))

f_title = ImageFont.truetype(font_bold, 54)
f_sub = ImageFont.truetype(font_reg, 28)
f_tag = ImageFont.truetype(font_bold, 24)

draw.rectangle([80, 840, 480, 880], fill=(184, 115, 51, 240)) # 琥珀銅金
draw.text((100, 846), "【舌尖上的臺灣】第 10 章", fill=(255, 255, 255), font=f_tag)
draw.text((80, 895), "山嵐間的東方美人", fill=(255, 248, 230), font=f_title)
draw.text((80, 970), "小綠葉蟬叮咬的蜜香奇蹟・大稻埕洋行千帆・客庄膨風茶傳奇", fill=(230, 195, 95), font=f_sub)

hero_banner.save("assets/images/food_ch10/food_ch10_hero_banner.jpg", quality=95)

print("Processing Tea Craft Banner (1920x1080)...")
# 2. Tea Craft Banner: 琥珀茶湯 + 港口帆船雙圖拼接
img_cup = Image.open(os.path.join(temp_dir, "teacup.jpg")).convert("RGB").resize((960, 1080), Image.Resampling.LANCZOS)
img_port = Image.open(os.path.join(temp_dir, "port.jpg")).convert("RGB").resize((960, 1080), Image.Resampling.LANCZOS)

craft_banner = Image.new("RGB", (1920, 1080))
craft_banner.paste(img_cup, (0, 0))
craft_banner.paste(img_port, (960, 0))
craft_banner = apply_tea_gold_filter(craft_banner, warm_tint=(255, 215, 160))

draw_c = ImageDraw.Draw(craft_banner, "RGBA")
for y in range(800, 1080):
    alpha = int(220 * ((y - 800) / 280))
    draw_c.rectangle([0, y, 1920, y+1], fill=(12, 10, 8, alpha))

draw_c.rectangle([80, 840, 520, 880], fill=(139, 69, 19, 240))
draw_c.text((100, 846), "【飲食風土考證】工藝與商貿", fill=(255, 255, 255), font=f_tag)
draw_c.text((80, 895), "五色斑斕白毫烏龍與大稻埕茶金歲月", fill=(255, 248, 230), font=f_title)
draw_c.text((80, 970), "客庄重發酵回潤工藝・陶德與李春生開闢 Formosa Oolong 航線", fill=(230, 190, 100), font=f_sub)

craft_banner.save("assets/images/food_ch10/food_ch10_tea_craft.jpg", quality=95)

print("Processing YouTube Thumbnails (1280x720)...")
# 3. 短片縮圖 (1280x720): 山嵐茶園 + 琥珀茶
yt_thumb = img_hills.resize((1280, 720), Image.Resampling.LANCZOS)
yt_thumb = apply_tea_gold_filter(yt_thumb, warm_tint=(255, 230, 180), vignette_strength=0.5)

draw_yt = ImageDraw.Draw(yt_thumb, "RGBA")
for x in range(0, 900):
    alpha = int(220 * (1 - (x / 900)))
    draw_yt.rectangle([x, 0, x+1, 720], fill=(12, 10, 6, alpha))

f_yt_tag = ImageFont.truetype(font_bold, 28)
f_yt_title = ImageFont.truetype(font_bold, 62)
f_yt_sub = ImageFont.truetype(font_bold, 34)
f_yt_extra = ImageFont.truetype(font_reg, 26)

draw_yt.rectangle([60, 60, 480, 110], fill=(180, 100, 20, 240))
draw_yt.text((80, 68), "【舌尖上的臺灣 第10章】", fill=(255, 255, 255), font=f_yt_tag)

draw_yt.text((60, 140), "山嵐間的", fill=(255, 255, 255), font=f_yt_title)
draw_yt.text((60, 220), "東方美人", fill=(255, 215, 0), font=f_yt_title)

draw_yt.rectangle([60, 320, 680, 380], fill=(25, 35, 20, 210))
draw_yt.text((80, 332), "小綠葉蟬叮咬的蜜香奇蹟", fill=(160, 240, 180), font=f_yt_sub)

draw_yt.text((65, 415), "▪ 茉莉酸化學求救與天然熟果蜜香", fill=(240, 240, 240), font=f_yt_extra)
draw_yt.text((65, 465), "▪ 客庄茶師極限重發酵與悶堆回潤", fill=(240, 240, 240), font=f_yt_extra)
draw_yt.text((65, 515), "▪ 陶德與李春生 Formosa 紐約爆紅", fill=(240, 240, 240), font=f_yt_extra)
draw_yt.text((65, 565), "▪ 維多利亞女王水晶杯賜名東方美人", fill=(240, 240, 240), font=f_yt_extra)

draw_yt.rectangle([980, 600, 1220, 660], fill=(190, 40, 40, 230))
draw_yt.text((1005, 612), "8分鐘精華導讀", fill=(255, 255, 255), font=f_yt_tag)

yt_thumb.save("assets/images/food_ch10/food_ch10_youtube_thumbnail.jpg", quality=95)

# 4. 播客縮圖 (1280x720): 博物館級 1870 大稻埕洋行與東方美人油畫（嚴格 16:9 等比無變形）
master_ai_path = "assets/images/food_ch10/food_ch10_oriental_beauty_ai_master.jpg"
if os.path.exists(master_ai_path):
    pod_img = Image.open(master_ai_path).convert("RGB")
else:
    pod_img = Image.open(os.path.join(temp_dir, "teacup.jpg")).convert("RGB")

from PIL import ImageOps
pod_thumb = ImageOps.fit(pod_img, (1280, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

enhancer = ImageEnhance.Color(pod_thumb)
pod_thumb = enhancer.enhance(1.06)
enhancer = ImageEnhance.Contrast(pod_thumb)
pod_thumb = enhancer.enhance(1.08)

overlay_pod = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
draw_ol = ImageDraw.Draw(overlay_pod)
for x in range(0, 960):
    factor = 1 - (x / 960)**1.3
    alpha = int(245 * max(0, factor))
    draw_ol.rectangle([x, 0, x+1, 720], fill=(12, 10, 8, alpha))
pod_thumb.paste(Image.alpha_composite(Image.new("RGBA", (1280, 720), (0, 0, 0, 0)), overlay_pod), (0, 0), overlay_pod)

f_bullet_icon = ImageFont.truetype(font_bold, 22)
f_extra = ImageFont.truetype(font_bold, 25)
f_badge = ImageFont.truetype(font_bold, 24)
draw_pod = ImageDraw.Draw(pod_thumb)

def draw_text_shadow(xy, text, font, fill, shadow_fill=(5, 4, 3), offset=(2, 2)):
    x, y = xy
    draw_pod.text((x + offset[0], y + offset[1]), text, font=font, fill=shadow_fill)
    draw_pod.text((x, y), text, font=font, fill=fill)

draw_pod.rounded_rectangle([60, 52, 540, 106], radius=10, fill=(150, 75, 20), outline=(225, 160, 80), width=2)
draw_text_shadow((82, 63), "【舌尖上的臺灣 深度播客】", f_tag, (255, 255, 255))

draw_text_shadow((60, 130), "山嵐間的", f_yt_title, (255, 250, 240), offset=(3, 3))
draw_text_shadow((60, 212), "東方美人", f_yt_title, (255, 205, 65), offset=(3, 3))

draw_pod.rounded_rectangle([60, 312, 690, 372], radius=8, fill=(28, 22, 18, 230), outline=(190, 140, 60), width=2)
draw_text_shadow((80, 324), "大稻埕茶金歲月與膨風茶傳奇", f_sub, (255, 225, 140))

bullets = [
    "小綠葉蟬刺吸與茶樹分子自衛武器",
    "陶德與李春生：寶順洋行與茶底銀信貸",
    "萬名大稻埕揀茶女工與近代女性受薪",
    "新竹州特等獎一斤換數棟房的膨風神話"
]
for i, b in enumerate(bullets):
    y = 405 + i * 50
    draw_text_shadow((65, y+1), "◆", f_bullet_icon, (255, 195, 60), offset=(2, 2))
    draw_text_shadow((95, y), b, f_extra, (245, 245, 245), offset=(2, 2))

draw_pod.rounded_rectangle([60, 620, 390, 672], radius=8, fill=(175, 55, 20), outline=(235, 120, 70), width=2)
draw_text_shadow((80, 631), "PODCAST 雙人深度對談", f_badge, (255, 255, 255))

pod_thumb.save("assets/images/food_ch10/food_ch10_podcast_thumbnail.jpg", quality=95)

# 複製鏡像至 舌尖上的臺灣/assets/images/ch10/
mirror_dir = "舌尖上的臺灣/assets/images/ch10"
for fn in [
    "food_ch10_hero_banner.jpg",
    "food_ch10_tea_craft.jpg",
    "food_ch10_youtube_thumbnail.jpg",
    "food_ch10_podcast_thumbnail.jpg"
]:
    src = os.path.join("assets/images/food_ch10", fn)
    dst = os.path.join(mirror_dir, fn)
    shutil.copy2(src, dst)
    if fn == "food_ch10_youtube_thumbnail.jpg":
        shutil.copy2(src, os.path.join(mirror_dir, "ch10_youtube_thumbnail.jpg"))
    elif fn == "food_ch10_podcast_thumbnail.jpg":
        shutil.copy2(src, os.path.join(mirror_dir, "ch10_podcast_thumbnail.jpg"))

print("All Chapter 10 visuals created successfully!")
