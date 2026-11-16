import os
import shutil
import urllib.request
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont

# 建立暫存資料夾
temp_dir = "temp_art_ch09"
os.makedirs(temp_dir, exist_ok=True)

# 挑選高品質 Unsplash 歷史/食物地景圖
image_sources = {
    # 蒸汽火車 / 鐵路月台
    "train": "https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=1920&q=85",
    # 日式木盒便當 / 白飯漬物
    "bento": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1920&q=85",
    # 復古咖啡館 / 黑咖啡
    "cafe": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1920&q=85",
    # 生啤酒 / 金黃酒液白沫
    "beer": "https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=1920&q=85"
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

def apply_rembrandt_vintage_filter(img, warm_tint=(255, 230, 200), vignette_strength=0.4):
    """施放大正浪漫油畫復古濾鏡"""
    # 調整暖色調
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.15)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    
    # 混合暖色層
    overlay = Image.new("RGB", img.size, warm_tint)
    img = Image.blend(img, overlay, 0.12)
    
    # 暗角效果
    w, h = img.size
    vignette = Image.new("L", (w, h), 0)
    v_draw = ImageDraw.Draw(vignette)
    v_draw.ellipse([int(-w*0.2), int(-h*0.2), int(w*1.2), int(h*1.2)], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(w // 8))
    
    black = Image.new("RGB", img.size, (15, 10, 5))
    img = Image.composite(img, black, vignette)
    return img

print("Processing Hero Banner (1920x1080)...")
# 1. Hero Banner: 蒸汽火車 + 鐵道意象
img_train = Image.open(os.path.join(temp_dir, "train.jpg")).convert("RGB")
img_train = img_train.resize((1920, 1080), Image.Resampling.LANCZOS)
hero_banner = apply_rembrandt_vintage_filter(img_train, warm_tint=(255, 220, 180))

# 底部漸層暗條
draw = ImageDraw.Draw(hero_banner, "RGBA")
for y in range(800, 1080):
    alpha = int(220 * ((y - 800) / 280))
    draw.rectangle([0, y, 1920, y+1], fill=(15, 12, 10, alpha))

f_title = ImageFont.truetype(font_bold, 54)
f_sub = ImageFont.truetype(font_reg, 28)
f_tag = ImageFont.truetype(font_bold, 24)

# 壓印標題
draw.rectangle([80, 840, 480, 880], fill=(184, 134, 11, 240))
draw.text((100, 846), "【舌尖上的臺灣】第 09 章", fill=(255, 255, 255), font=f_tag)
draw.text((80, 895), "汽笛聲中的木片便當", fill=(255, 248, 230), font=f_title)
draw.text((80, 970), "1908 縱貫鐵路全通・經木盒吸濕防餿・鐵道飯店與生啤酒摩登生活", fill=(212, 175, 55), font=f_sub)

hero_banner.save("assets/images/food_ch09/food_ch09_hero_banner.jpg", quality=95)

print("Processing Bento Craft Banner (1920x1080)...")
# 2. Bento Craft Banner: 木盒便當 + 咖啡/啤酒雙圖拼接
img_bento = Image.open(os.path.join(temp_dir, "bento.jpg")).convert("RGB").resize((960, 1080), Image.Resampling.LANCZOS)
img_cafe = Image.open(os.path.join(temp_dir, "cafe.jpg")).convert("RGB").resize((960, 1080), Image.Resampling.LANCZOS)

craft_banner = Image.new("RGB", (1920, 1080))
craft_banner.paste(img_bento, (0, 0))
craft_banner.paste(img_cafe, (960, 0))
craft_banner = apply_rembrandt_vintage_filter(craft_banner, warm_tint=(255, 215, 170))

draw_c = ImageDraw.Draw(craft_banner, "RGBA")
# 底部漸層
for y in range(800, 1080):
    alpha = int(220 * ((y - 800) / 280))
    draw_c.rectangle([0, y, 1920, y+1], fill=(12, 10, 8, alpha))

draw_c.rectangle([80, 840, 520, 880], fill=(139, 69, 19, 240))
draw_c.text((100, 846), "【飲食風土考證】工藝與物性", fill=(255, 255, 255), font=f_tag)
draw_c.text((80, 895), "經木薄盒調濕防餿與大正喫茶沙龍", fill=(255, 248, 230), font=f_title)
draw_c.text((80, 970), "薄檜木微孔毛細平衡・波麗路黑膠爵士・高砂麥酒生啤酒", fill=(230, 190, 100), font=f_sub)

craft_banner.save("assets/images/food_ch09/food_ch09_bento_craft.jpg", quality=95)

print("Processing YouTube Thumbnails (1280x720)...")
# 3. 短片縮圖 (1280x720): 蒸汽火車 + 便當
yt_thumb = img_train.resize((1280, 720), Image.Resampling.LANCZOS)
yt_thumb = apply_rembrandt_vintage_filter(yt_thumb, warm_tint=(255, 225, 190), vignette_strength=0.5)

draw_yt = ImageDraw.Draw(yt_thumb, "RGBA")
# 漸層覆蓋層（左側與底部暗化以凸顯文字）
for x in range(0, 900):
    alpha = int(220 * (1 - (x / 900)))
    draw_yt.rectangle([x, 0, x+1, 720], fill=(10, 8, 5, alpha))

f_yt_tag = ImageFont.truetype(font_bold, 28)
f_yt_title = ImageFont.truetype(font_bold, 62)
f_yt_sub = ImageFont.truetype(font_bold, 34)
f_yt_extra = ImageFont.truetype(font_reg, 26)

# 標籤
draw_yt.rectangle([60, 60, 480, 110], fill=(190, 120, 20, 240))
draw_yt.text((80, 68), "【舌尖上的臺灣 第09章】", fill=(255, 255, 255), font=f_yt_tag)

# 大標題
draw_yt.text((60, 140), "汽笛聲中的", fill=(255, 255, 255), font=f_yt_title)
draw_yt.text((60, 220), "木片便當", fill=(255, 215, 0), font=f_yt_title)

# 副標
draw_yt.rectangle([60, 320, 680, 380], fill=(20, 30, 45, 210))
draw_yt.text((80, 332), "縱貫鐵路全通・經木防餿奇蹟", fill=(130, 220, 255), font=f_yt_sub)

# 條列亮點
draw_yt.text((65, 415), "▪ 1908 縱貫鐵道全通與時間觀革命", fill=(240, 240, 240), font=f_yt_extra)
draw_yt.text((65, 465), "▪ 阿里山檜木 0.8mm 薄片呼吸科學", fill=(240, 240, 240), font=f_yt_extra)
draw_yt.text((65, 515), "▪ 從日之丸漬物到黃金炸排骨傳奇", fill=(240, 240, 240), font=f_yt_extra)
draw_yt.text((65, 565), "▪ 臺灣鐵道飯店法式西餐與生啤酒", fill=(240, 240, 240), font=f_yt_extra)

# 右下角精華導讀章戳
draw_yt.rectangle([980, 600, 1220, 660], fill=(200, 40, 40, 230))
draw_yt.text((1005, 612), "8分鐘精華導讀", fill=(255, 255, 255), font=f_yt_tag)

yt_thumb.save("assets/images/food_ch09/food_ch09_youtube_thumbnail.jpg", quality=95)

# 4. 播客縮圖 (1280x720): 喫茶店 + 生啤酒 + 爵士黑膠氛圍（深邃金褐色調）
pod_img = Image.open(os.path.join(temp_dir, "cafe.jpg")).convert("RGB").resize((1280, 720), Image.Resampling.LANCZOS)
pod_thumb = apply_rembrandt_vintage_filter(pod_img, warm_tint=(240, 200, 160), vignette_strength=0.6)

draw_pod = ImageDraw.Draw(pod_thumb, "RGBA")
# 左側暗化
for x in range(0, 950):
    alpha = int(230 * (1 - (x / 950)))
    draw_pod.rectangle([x, 0, x+1, 720], fill=(8, 12, 18, alpha))

draw_pod.rectangle([60, 60, 520, 110], fill=(40, 80, 120, 240))
draw_pod.text((80, 68), "【舌尖上的臺灣 深度播客】", fill=(255, 255, 255), font=f_yt_tag)

draw_pod.text((60, 140), "汽笛聲中的", fill=(255, 255, 255), font=f_yt_title)
draw_pod.text((60, 220), "木片便當", fill=(255, 195, 80), font=f_yt_title)

draw_pod.rectangle([60, 320, 720, 380], fill=(15, 25, 35, 220))
draw_pod.text((80, 332), "摩登生活、喫茶沙龍與生啤酒", fill=(255, 215, 120), font=f_yt_sub)

draw_pod.text((65, 415), "🎙️ 鐵道飯店全臺第一部電梯與西餐", fill=(235, 235, 235), font=f_yt_extra)
draw_pod.text((65, 465), "🎙️ 大稻埕波麗路黑膠交響與相親傳奇", fill=(235, 235, 235), font=f_yt_extra)
draw_pod.text((65, 515), "🎙️ 山水亭文人沙龍與天馬茶房風雲", fill=(235, 235, 235), font=f_yt_extra)
draw_pod.text((65, 565), "🎙️ 建國啤酒廠前身高砂麥酒底層發酵", fill=(235, 235, 235), font=f_yt_extra)

# 右下角雙人深度對談章戳
draw_pod.rectangle([960, 600, 1220, 660], fill=(30, 90, 140, 230))
draw_pod.text((980, 612), "PODCAST 深度對談", fill=(255, 255, 255), font=f_yt_tag)

pod_thumb.save("assets/images/food_ch09/food_ch09_podcast_thumbnail.jpg", quality=95)

# 複製鏡像至 舌尖上的臺灣/assets/images/ch09/
mirror_dir = "舌尖上的臺灣/assets/images/ch09"
for fn in [
    "food_ch09_hero_banner.jpg",
    "food_ch09_bento_craft.jpg",
    "food_ch09_youtube_thumbnail.jpg",
    "food_ch09_podcast_thumbnail.jpg"
]:
    src = os.path.join("assets/images/food_ch09", fn)
    dst = os.path.join(mirror_dir, fn)
    shutil.copy2(src, dst)
    # 同步兼具標準縮圖檔名
    if fn == "food_ch09_youtube_thumbnail.jpg":
        shutil.copy2(src, os.path.join(mirror_dir, "ch09_youtube_thumbnail.jpg"))
    elif fn == "food_ch09_podcast_thumbnail.jpg":
        shutil.copy2(src, os.path.join(mirror_dir, "ch09_podcast_thumbnail.jpg"))

print("All Chapter 09 visuals created successfully!")
