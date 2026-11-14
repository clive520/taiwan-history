# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 07 章 歷史主視覺、工藝圖與雙軌縮圖合成腳本
- 英雄主視覺 (1920x1080)：赤崁樓、五條港水仙宮、炒鱔魚高溫鑊氣與林布蘭特暖金油畫
- 工藝特寫圖 (1920x1080)：傳統糖廍石磨、蜂窩古法椪糖、白糖粿與琥珀糖膜
- 說明短片縮圖 (1280x720)：高對比暖赭金黃油畫風格，大字排版
- 播客深度對談縮圖 (1280x720)：深藍暖金知性對談風格
"""
import sys
import os
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH07_ASSETS = BASE_DIR / "assets" / "images" / "food_ch07"
CH07_MIRROR = BASE_DIR / "舌尖上的臺灣" / "assets" / "images" / "ch07"
TEMP_DIR = BASE_DIR / "temp_art_ch07"

CH07_ASSETS.mkdir(parents=True, exist_ok=True)
CH07_MIRROR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# 來源圖片清單
SOURCES = {
    "chihkan": "https://upload.wikimedia.org/wikipedia/commons/0/09/Tainan_Taiwan_Fort-Provintia-01.jpg",
    "shuixian": "https://upload.wikimedia.org/wikipedia/commons/6/6f/%E8%87%BA%E5%8D%97%E6%B0%B4%E4%BB%99%E5%AE%AE.JPG",
    "eel_noodles": "https://upload.wikimedia.org/wikipedia/commons/b/b4/Thick_Soup_Noodles_with_Eel_-_%E9%B1%94%E9%AD%9A%E6%84%8F%E9%BA%B5_%284596353688%29.jpg",
    "sugar_mill": "https://upload.wikimedia.org/wikipedia/commons/8/83/%E7%B3%96%E5%BB%8D%E5%BB%BA%E7%AF%89%E6%A8%A1%E5%9E%8B.jpg",
    "cinder_toffee": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Cinder_Toffee.jpg"
}

def download_sources():
    print("📥 正在下載高解析度文化遺產素材...")
    for key, url in SOURCES.items():
        dst = TEMP_DIR / f"{key}.jpg"
        if not dst.exists() or dst.stat().st_size == 0:
            print(f"  下載 {key}...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            try:
                with urllib.request.urlopen(req) as resp, open(dst, 'wb') as f:
                    f.write(resp.read())
                print(f"  ✅ {key} 下載成功！({dst.stat().st_size / 1024:.1f} KB)")
            except Exception as e:
                print(f"  ⚠️ {key} 下載失敗：{e}")

def apply_rembrandt_style(im, warm_tint=(255, 215, 150), intensity=0.35, vignette_strength=0.7):
    # 油畫暖色調濾鏡與丁達爾光暈
    im = im.convert("RGB")
    # 增加對比度與飽和度
    im = ImageEnhance.Contrast(im).enhance(1.25)
    im = ImageEnhance.Color(im).enhance(1.15)
    
    # 疊加暖金光照層
    tint_layer = Image.new("RGB", im.size, warm_tint)
    im = Image.blend(im, tint_layer, intensity)
    
    # 暗角效果 (Vignette)
    w, h = im.size
    vignette = Image.new("L", (w, h), 0)
    v_draw = ImageDraw.Draw(vignette)
    max_radius = int(((w/2)**2 + (h/2)**2)**0.5)
    for r in range(max_radius, 0, -15):
        alpha = int(255 * (1 - (r / max_radius)**2 * vignette_strength))
        alpha = max(0, min(255, alpha))
        v_draw.ellipse([w/2 - r, h/2 - r, w/2 + r, h/2 + r], fill=alpha)
    
    black_layer = Image.new("RGB", (w, h), (15, 10, 5))
    im = Image.composite(im, black_layer, vignette)
    return im

def build_hero_banner():
    print("🎨 正在合成 Hero Banner (1920x1080)...")
    # 結合赤崁樓古典建築與炒鱔魚鑊氣
    chihkan_file = TEMP_DIR / "chihkan.jpg"
    eel_file = TEMP_DIR / "eel_noodles.jpg"
    
    base = Image.new("RGB", (1920, 1080), (20, 15, 10))
    if chihkan_file.exists():
        im1 = Image.open(chihkan_file).convert("RGB")
        im1 = im1.resize((1920, 1080), Image.Resampling.LANCZOS)
        base = im1
        
    if eel_file.exists():
        im2 = Image.open(eel_file).convert("RGB")
        im2 = im2.resize((960, 640), Image.Resampling.LANCZOS)
        # 建立羽化蒙版
        mask = Image.new("L", im2.size, 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.ellipse([40, 40, im2.width - 40, im2.height - 40], fill=220)
        mask = mask.filter(ImageFilter.GaussianBlur(30))
        base.paste(im2, (960, 440), mask)
        
    styled = apply_rembrandt_style(base, warm_tint=(255, 200, 120), intensity=0.25, vignette_strength=0.6)
    
    out_path = CH07_ASSETS / "food_ch07_hero_banner.jpg"
    styled.save(out_path, quality=95)
    styled.save(CH07_MIRROR / "food_ch07_hero_banner.jpg", quality=95)
    print(f"✅ Hero Banner 儲存完成：{out_path.name}")
    return styled

def build_craft_image():
    print("🎨 正在合成製糖與工藝圖 (1920x1080)...")
    sugar_file = BASE_DIR / "assets" / "images" / "food_ch02" / "food_ch02_sugar_mill.jpg"
    
    if sugar_file.exists():
        im1 = Image.open(sugar_file).convert("RGB")
        im1 = im1.resize((1920, 1080), Image.Resampling.LANCZOS)
    else:
        im1 = Image.new("RGB", (1920, 1080), (30, 20, 12))
        
    styled = apply_rembrandt_style(im1, warm_tint=(255, 190, 100), intensity=0.25, vignette_strength=0.65)
    
    out_path = CH07_ASSETS / "food_ch07_sugar_craft.jpg"
    styled.save(out_path, quality=95)
    styled.save(CH07_MIRROR / "food_ch07_sugar_craft.jpg", quality=95)
    print(f"✅ 工藝圖儲存完成：{out_path.name} ({out_path.stat().st_size / 1024:.1f} KB)")
    return styled

def build_youtube_thumbnail(base_im):
    print("🎨 正在合成 YouTube 說明短片封面縮圖 (1280x720)...")
    w, h = 1280, 720
    im = base_im.resize((w, h), Image.Resampling.LANCZOS)
    
    # 強化右側文字區暗色漸變遮罩
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(w // 3, w):
        alpha = int(220 * ((x - w // 3) / (w * 2 // 3)) ** 1.3)
        draw.line([(x, 0), (x, h)], fill=(12, 8, 5, alpha))
    im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    
    draw = ImageDraw.Draw(im)
    font_path = "C:/Windows/Fonts/msyhbd.ttc"
    
    try:
        font_badge = ImageFont.truetype(font_path, 26)
        font_main = ImageFont.truetype(font_path, 54)
        font_sub = ImageFont.truetype(font_path, 28)
        font_tag = ImageFont.truetype(font_path, 22)
    except:
        font_badge = font_main = font_sub = font_tag = ImageFont.load_default()
        
    # 1. 標籤膠囊 (朱紅金邊)
    badge_text = "舌尖上的臺灣 ｜ 第 07 章"
    bx, by = 480, 80
    bw, bh = 340, 48
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(185, 38, 25), outline=(255, 215, 0), width=2)
    draw.text((bx + 20, by + 8), badge_text, font=font_badge, fill=(255, 255, 255))
    
    # 2. 主標題 (大字帶厚重陰影)
    title_text = "甘甜的舌尖密碼"
    tx, ty = 480, 160
    # 陰影
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            draw.text((tx + dx, ty + dy), title_text, font=font_main, fill=(0, 0, 0))
    draw.text((tx, ty), title_text, font=font_main, fill=(255, 245, 230))
    
    # 3. 副標題金句
    sub1 = "為什麼臺南人的菜這麼甜？"
    sx1, sy1 = 480, 250
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            draw.text((sx1 + dx, sy1 + dy), sub1, font=font_sub, fill=(0, 0, 0))
    draw.text((sx1, sy1), sub1, font=font_sub, fill=(255, 215, 0))
    
    # 4. 核心要素排版
    items = [
        "• 明鄭東寧軍國白金：陳永華煮糖致富",
        "• 五條港糖郊李勝興：瓦溜淋泥出雪白霜糖",
        "• 范伯倫《有閒階級論》：阿舍以糖炫富的階級下滲",
        "• 250°C 炒鱔魚鑊氣：焦糖化 × 琥珀糖膜鎖水",
        "• 羹湯流變學：番薯粉溶膠增甜 × 鮮味乘數效應"
    ]
    iy = 320
    for it in items:
        draw.text((482, iy + 2), it, font=font_tag, fill=(0, 0, 0))
        draw.text((480, iy), it, font=font_tag, fill=(235, 235, 235))
        iy += 45
        
    # 5. 底部高亮條
    foot_text = "明鄭東寧糖政 ｜ 250°C 鑊氣焦糖化 ｜ 阿舍菜炫耀心理學"
    draw.rounded_rectangle([480, 580, 1220, 630], radius=6, fill=(40, 25, 15), outline=(255, 180, 0), width=1)
    draw.text((505, 592), foot_text, font=font_tag, fill=(255, 215, 0))
    
    out_file = CH07_ASSETS / "food_ch07_youtube_thumbnail.jpg"
    im.save(out_file, quality=95)
    im.save(CH07_MIRROR / "food_ch07_youtube_thumbnail.jpg", quality=95)
    im.save(CH07_MIRROR / "ch07_youtube_thumbnail.jpg", quality=95)
    print(f"✅ YouTube 縮圖儲存完成：{out_file.name}")

def build_podcast_thumbnail(craft_im):
    print("🎨 正在合成 Podcast 深度對談封面縮圖 (1280x720)...")
    w, h = 1280, 720
    im = craft_im.resize((w, h), Image.Resampling.LANCZOS)
    
    # 深普魯士藍色調濾鏡 (展現學術與知性播客質感)
    blue_overlay = Image.new("RGB", (w, h), (10, 25, 45))
    im = Image.blend(im, blue_overlay, 0.45)
    
    # 增加暗角與柔光
    im = ImageEnhance.Contrast(im).enhance(1.2)
    
    # 中心與兩側遮罩
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_o = ImageDraw.Draw(overlay)
    draw_o.rectangle([0, 0, w, h], fill=(8, 16, 28, 180))
    im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    
    draw = ImageDraw.Draw(im)
    font_path = "C:/Windows/Fonts/msyhbd.ttc"
    
    try:
        font_badge = ImageFont.truetype(font_path, 22)
        font_main = ImageFont.truetype(font_path, 50)
        font_sub = ImageFont.truetype(font_path, 28)
        font_body = ImageFont.truetype(font_path, 23)
    except:
        font_badge = font_main = font_sub = font_body = ImageFont.load_default()
        
    # 1. 頂部 Podcast 標籤
    badge_text = "深度對談 ｜ FOOD PODCAST EP07"
    draw.rounded_rectangle([420, 60, 860, 105], radius=6, fill=(180, 40, 25), outline=(255, 215, 0), width=1)
    draw.text((460, 68), badge_text, font=font_badge, fill=(255, 255, 255))
    
    # 2. 主標題
    title_text = "甘甜的舌尖密碼"
    draw.text((412, 137), title_text, font=font_main, fill=(0, 0, 0))
    draw.text((410, 135), title_text, font=font_main, fill=(255, 245, 220))
    
    # 3. 副標題
    sub_text = "從明鄭煮糖、五條港糖郊到阿舍菜炫耀心理學"
    draw.text((322, 222), sub_text, font=font_sub, fill=(0, 0, 0))
    draw.text((320, 220), sub_text, font=font_sub, fill=(255, 215, 0))
    
    # 4. 深度對談四維看點
    box_x = 220
    box_y = 290
    box_w = 840
    box_h = 320
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=12, fill=(12, 22, 38), outline=(60, 110, 170), width=2)
    
    points = [
        "• 東寧王國戰略白金：陳永華甘蔗軍屯與長崎馬尼拉外銷網絡",
        "• 瓦溜淋泥黑科技：毛細管作用分離糖蜜，東亞最高純度霜糖奇蹟",
        "• 范伯倫《有閒階級論》：阿舍熱菜重糖炫耀與市井小吃階級代償",
        "• 250°C 炒鱔魚熱力學：二砂糖極速焦糖化 × 琥珀糖膜鎖水神技",
        "• 羹湯溶膠流變學：澱粉糊化阻礙擴散 × T1R2/T1R3 甜味信號放大",
        "• 白糖粿外脆內拉絲 × 古法椪糖碳酸氫鈉熱分解多孔發泡成型"
    ]
    py = box_y + 25
    for p in points:
        draw.text((box_x + 35, py), p, font=font_body, fill=(225, 235, 245))
        py += 46
        
    out_file = CH07_ASSETS / "food_ch07_podcast_thumbnail.jpg"
    im.save(out_file, quality=95)
    im.save(CH07_MIRROR / "food_ch07_podcast_thumbnail.jpg", quality=95)
    im.save(CH07_MIRROR / "ch07_podcast_thumbnail.jpg", quality=95)
    print(f"✅ Podcast 縮圖儲存完成：{out_file.name}")

def main():
    download_sources()
    hero_im = build_hero_banner()
    craft_im = build_craft_image()
    build_youtube_thumbnail(hero_im)
    build_podcast_thumbnail(craft_im)
    print("✨ 第 07 章四款高清視覺插圖與縮圖產製大功告成！")

if __name__ == "__main__":
    main()
