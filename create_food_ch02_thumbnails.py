# -*- coding: utf-8 -*-
"""
生成《舌尖上的臺灣》第 02 章 1280x720 雙軌縮圖
1. YouTube 說明短片縮圖：琥珀金/熱蘭遮城/蔗田史詩
2. Podcast 深度對談縮圖：深藍沉穩/糖廍石磨水牛
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
IMG_DIR = BASE_DIR / "assets" / "images" / "food_ch02"
CH02_DIR = BASE_DIR / "舌尖上的臺灣" / "assets" / "images" / "ch02"

FONT_PATH = "C:/Windows/Fonts/msjhbd.ttc"

def make_youtube_thumbnail():
    bg_path = IMG_DIR / "food_ch02_hero_banner.jpg"
    img = Image.open(bg_path).convert("RGBA")
    
    # 裁切並縮放到 1280x720
    target_w, target_h = 1280, 720
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h
    
    if img_ratio > target_ratio:
        new_w = int(img.height * target_ratio)
        offset = (img.width - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, img.height))
    else:
        new_h = int(img.width / target_ratio)
        offset = (img.height - new_h) // 2
        img = img.crop((0, offset, img.width, offset + new_h))
        
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # 建立多層次暗角與漸層遮罩 (深海藍黑漸層，襯托金文字)
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    for y in range(target_h):
        # 底部暗部漸層
        alpha_bottom = int(max(0, (y - 300) / 420) * 190)
        # 左側暗部漸層
        draw_ov.line([(0, y), (target_w, y)], fill=(12, 18, 28, alpha_bottom))
        
    for x in range(700):
        alpha_left = int((1.0 - (x / 700)) * 140)
        for y in range(target_h):
            orig_color = overlay.getpixel((x, y))
            draw_ov.point((x, y), fill=(orig_color[0], orig_color[1], orig_color[2], min(255, orig_color[3] + alpha_left)))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    # 字型加載
    font_badge = ImageFont.truetype(FONT_PATH, 28)
    font_title = ImageFont.truetype(FONT_PATH, 74)
    font_sub = ImageFont.truetype(FONT_PATH, 34)
    font_meta = ImageFont.truetype(FONT_PATH, 24)
    
    # 1. 系列徽章 (琥珀金頂部卡片)
    bx, by = 60, 50
    badge_text = " 舌尖上的臺灣・第 02 章 "
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 30
    bh = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(212, 143, 24, 240), outline=(255, 215, 0, 255), width=2)
    draw.text((bx + 15, by + 8), badge_text, fill=(20, 20, 20), font=font_badge)
    
    # 2. 主標題 (大航海的蔗香與鹿皮)
    tx, ty = 60, 420
    title_text = "大航海的蔗香與鹿皮"
    # 陰影
    draw.text((tx + 4, ty + 4), title_text, fill=(0, 0, 0, 240), font=font_title)
    draw.text((tx, ty), title_text, fill=(255, 238, 190), font=font_title)
    
    # 3. 副標題 (荷西東印度公司・水牛糖廍・熱帶果物登陸)
    sx, sy = 62, 520
    sub_text = "荷西東印度公司・水牛糖廍・熱帶果物登陸"
    draw.text((sx + 2, sy + 2), sub_text, fill=(0, 0, 0, 220), font=font_sub)
    draw.text((sx, sy), sub_text, fill=(235, 185, 95), font=font_sub)
    
    # 4. 底部微標籤
    mx, my = 62, 600
    meta_text = "1624–1662 臺南大員熱蘭遮城｜荷蘭豆・檨仔・蓮霧登陸史"
    draw.text((mx + 2, my + 2), meta_text, fill=(0, 0, 0, 200), font=font_meta)
    draw.text((mx, my), meta_text, fill=(200, 210, 225), font=font_meta)
    
    out_rgb = img.convert("RGB")
    out_p1 = IMG_DIR / "food_ch02_youtube_thumbnail.jpg"
    out_p2 = CH02_DIR / "ch02_youtube_thumbnail.jpg"
    out_rgb.save(out_p1, quality=95)
    out_rgb.save(out_p2, quality=95)
    print(f"✅ 生成 YouTube 說明短片縮圖：{out_p1.name}")

def make_podcast_thumbnail():
    bg_path = IMG_DIR / "food_ch02_sugar_mill.jpg"
    img = Image.open(bg_path).convert("RGBA")
    
    target_w, target_h = 1280, 720
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h
    
    if img_ratio > target_ratio:
        new_w = int(img.height * target_ratio)
        offset = (img.width - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, img.height))
    else:
        new_h = int(img.width / target_ratio)
        offset = (img.height - new_h) // 2
        img = img.crop((0, offset, img.width, offset + new_h))
        
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    # 深邃暖黑金漸層
    for y in range(target_h):
        alpha_bottom = int(max(0, (y - 250) / 470) * 220)
        draw_ov.line([(0, y), (target_w, y)], fill=(16, 12, 10, alpha_bottom))
        
    for x in range(800):
        alpha_left = int((1.0 - (x / 800)) * 160)
        for y in range(target_h):
            orig_color = overlay.getpixel((x, y))
            draw_ov.point((x, y), fill=(orig_color[0], orig_color[1], orig_color[2], min(255, orig_color[3] + alpha_left)))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    font_badge = ImageFont.truetype(FONT_PATH, 28)
    font_title = ImageFont.truetype(FONT_PATH, 74)
    font_sub = ImageFont.truetype(FONT_PATH, 34)
    font_meta = ImageFont.truetype(FONT_PATH, 24)
    
    # 1. Podcast 專屬徽章
    bx, by = 60, 50
    badge_text = " 🎙️ 深度對談 PODCAST・第 02 章 "
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 30
    bh = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(28, 45, 75, 240), outline=(90, 160, 240, 255), width=2)
    draw.text((bx + 15, by + 8), badge_text, fill=(230, 242, 255), font=font_badge)
    
    # 2. 主標題 (荷蘭人帶來的美味遺產)
    tx, ty = 60, 420
    title_text = "荷蘭人帶來的美味遺產"
    draw.text((tx + 4, ty + 4), title_text, fill=(0, 0, 0, 240), font=font_title)
    draw.text((tx, ty), title_text, fill=(255, 235, 180), font=font_title)
    
    # 3. 副標題 (從鹿皮海嘯到一碗「臺南甜」)
    sx, sy = 62, 520
    sub_text = "從鹿皮海嘯到一碗「臺南甜」"
    draw.text((sx + 2, sy + 2), sub_text, fill=(0, 0, 0, 220), font=font_sub)
    draw.text((sx, sy), sub_text, fill=(235, 175, 80), font=font_sub)
    
    # 4. 底部微標籤
    mx, my = 62, 600
    meta_text = "熱力學糖廍｜瓦溜淋泥白糖法｜哥倫布大交換在臺灣"
    draw.text((mx + 2, my + 2), meta_text, fill=(0, 0, 0, 200), font=font_meta)
    draw.text((mx, my), meta_text, fill=(210, 200, 180), font=font_meta)
    
    out_rgb = img.convert("RGB")
    out_p1 = IMG_DIR / "food_ch02_podcast_thumbnail.jpg"
    out_p2 = CH02_DIR / "ch02_podcast_thumbnail.jpg"
    out_rgb.save(out_p1, quality=95)
    out_rgb.save(out_p2, quality=95)
    print(f"✅ 生成 Podcast 深度對談縮圖：{out_p1.name}")

if __name__ == "__main__":
    make_youtube_thumbnail()
    make_podcast_thumbnail()
