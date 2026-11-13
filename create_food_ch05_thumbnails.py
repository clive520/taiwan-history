# -*- coding: utf-8 -*-
"""
生成《舌尖上的臺灣》第 05 章 1280x720 雙軌縮圖
1. YouTube 說明短片縮圖：暖赭朱紅風格，善化牛墟晨霧
2. Podcast 深度對談縮圖：深褐金琥珀風格，溫體牛與生沖分子熱力學
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
IMG_DIR = BASE_DIR / "assets" / "images" / "food_ch05"
CH05_DIR = BASE_DIR / "舌尖上的臺灣" / "assets" / "images" / "ch05"

IMG_DIR.mkdir(parents=True, exist_ok=True)
CH05_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/msjhbd.ttc"

def make_craft_image():
    # 由 Hero Banner 衍生具深邃溫暖琥珀影調的工藝景像
    hero_path = IMG_DIR / "food_ch05_hero_banner.jpg"
    craft_path1 = IMG_DIR / "food_ch05_beef_soup.jpg"
    craft_path2 = CH05_DIR / "food_ch05_beef_soup.jpg"
    
    im = Image.open(hero_path).convert("RGB")
    # 微調對比度與暖色度
    enh_c = ImageEnhance.Contrast(im).enhance(1.15)
    enh_col = ImageEnhance.Color(enh_c).enhance(1.1)
    
    enh_col.save(craft_path1, quality=95)
    enh_col.save(craft_path2, quality=95)
    print("✅ 已生成工藝視覺圖: food_ch05_beef_soup.jpg")

def make_youtube_thumbnail():
    bg_path = IMG_DIR / "food_ch05_hero_banner.jpg"
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
    
    # 底部暗角漸變
    for y in range(target_h):
        alpha_bottom = int(max(0, (y - 280) / 440) * 210)
        draw_ov.line([(0, y), (target_w, y)], fill=(15, 10, 8, alpha_bottom))
        
    # 左側遮罩漸變（便於閱讀文字）
    for x in range(780):
        alpha_left = int((1.0 - (x / 780)) * 170)
        for y in range(target_h):
            orig_color = overlay.getpixel((x, y))
            draw_ov.point((x, y), fill=(orig_color[0], orig_color[1], orig_color[2], min(255, orig_color[3] + alpha_left)))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    font_badge = ImageFont.truetype(FONT_PATH, 28)
    font_title = ImageFont.truetype(FONT_PATH, 70)
    font_sub = ImageFont.truetype(FONT_PATH, 34)
    font_meta = ImageFont.truetype(FONT_PATH, 24)
    
    # 1. 膠囊徽章 (朱紅赭石)
    bx, by = 60, 50
    badge_text = " 舌尖上的臺灣｜第 05 章 "
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 30
    bh = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(185, 28, 28, 240), outline=(254, 226, 226, 200), width=2)
    draw.text((bx + 15, by + 8), badge_text, fill=(255, 255, 255), font=font_badge)
    
    # 2. 主標題
    tx, ty = 60, 420
    title_text = "水牛禁忌與清晨的甘甜"
    for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4)]:
        draw.text((tx + ox, ty + oy), title_text, fill=(0, 0, 0, 230), font=font_title)
    draw.text((tx, ty), title_text, fill=(255, 251, 235), font=font_title)
    
    # 3. 副標題
    sx, sy = 60, 520
    sub_text = "善化牛墟・溫體現沖・屠宰聚落"
    for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((sx + ox, sy + oy), sub_text, fill=(0, 0, 0, 200), font=font_sub)
    draw.text((sx, sy), sub_text, fill=(251, 191, 36), font=font_sub)
    
    # 4. 底部資訊
    mx, my = 60, 595
    meta_text = "清領禁牛令碑記 / 1960農業機械化役退 / 98°C生沖熱力學"
    draw.text((mx, my), meta_text, fill=(229, 231, 235), font=font_meta)
    
    # 右下角小標
    badge_r_text = "400年飲食文化考證"
    font_r = ImageFont.truetype(FONT_PATH, 24)
    r_bbox = font_r.getbbox(badge_r_text)
    rw = r_bbox[2] - r_bbox[0] + 24
    rh = r_bbox[3] - r_bbox[1] + 14
    rx = target_w - rw - 60
    ry = target_h - rh - 50
    draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=6, fill=(0, 0, 0, 180), outline=(251, 191, 36, 180), width=1)
    draw.text((rx + 12, ry + 6), badge_r_text, fill=(251, 191, 36), font=font_r)
    
    # 存檔
    out_rgb = img.convert("RGB")
    out_path1 = IMG_DIR / "food_ch05_youtube_thumbnail.jpg"
    out_path2 = CH05_DIR / "ch05_youtube_thumbnail.jpg"
    out_rgb.save(out_path1, quality=95)
    out_rgb.save(out_path2, quality=95)
    print(f"✅ 已生成 YouTube 縮圖: {out_path1.name} (1280x720)")

def make_podcast_thumbnail():
    bg_path = IMG_DIR / "food_ch05_beef_soup.jpg"
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
    
    for y in range(target_h):
        alpha_bottom = int(max(0, (y - 260) / 460) * 220)
        draw_ov.line([(0, y), (target_w, y)], fill=(24, 14, 10, alpha_bottom))
        
    for x in range(750):
        alpha_left = int((1.0 - (x / 750)) * 175)
        for y in range(target_h):
            orig_color = overlay.getpixel((x, y))
            draw_ov.point((x, y), fill=(orig_color[0], orig_color[1], orig_color[2], min(255, orig_color[3] + alpha_left)))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    font_badge = ImageFont.truetype(FONT_PATH, 28)
    font_title = ImageFont.truetype(FONT_PATH, 66)
    font_sub = ImageFont.truetype(FONT_PATH, 34)
    font_meta = ImageFont.truetype(FONT_PATH, 24)
    
    # 1. 播客標籤 (深褐暖金)
    bx, by = 60, 50
    badge_text = " 深度對談 PODCAST｜EP 05 "
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 30
    bh = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(30, 20, 15, 240), outline=(245, 158, 11, 230), width=2)
    draw.text((bx + 15, by + 8), badge_text, fill=(251, 191, 36), font=font_badge)
    
    # 2. 播客主標
    tx, ty = 60, 420
    title_text = "深度對談：水牛禁忌與清晨的甘甜"
    for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4)]:
        draw.text((tx + ox, ty + oy), title_text, fill=(0, 0, 0, 240), font=font_title)
    draw.text((tx, ty), title_text, fill=(255, 255, 255), font=font_title)
    
    # 3. 播客副標
    sx, sy = 60, 520
    sub_text = "從敬牛不食到臺南清晨一碗鮮甜的文化突變"
    for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((sx + ox, sy + oy), sub_text, fill=(0, 0, 0, 200), font=font_sub)
    draw.text((sx, sy), sub_text, fill=(251, 191, 36), font=font_sub)
    
    # 4. 底部資訊
    mx, my = 60, 595
    meta_text = "Pre-rigor死後僵直前生化 / 拒絕冷縮 / 琥珀高湯鮮味倍增"
    draw.text((mx, my), meta_text, fill=(229, 231, 235), font=font_meta)
    
    # 右下角小標
    badge_r_text = "無損原音深度剖析"
    font_r = ImageFont.truetype(FONT_PATH, 24)
    r_bbox = font_r.getbbox(badge_r_text)
    rw = r_bbox[2] - r_bbox[0] + 24
    rh = r_bbox[3] - r_bbox[1] + 14
    rx = target_w - rw - 60
    ry = target_h - rh - 50
    draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=6, fill=(0, 0, 0, 180), outline=(245, 158, 11, 180), width=1)
    draw.text((rx + 12, ry + 6), badge_r_text, fill=(251, 191, 36), font=font_r)
    
    out_rgb = img.convert("RGB")
    out_path1 = IMG_DIR / "food_ch05_podcast_thumbnail.jpg"
    out_path2 = CH05_DIR / "ch05_podcast_thumbnail.jpg"
    out_rgb.save(out_path1, quality=95)
    out_rgb.save(out_path2, quality=95)
    print(f"✅ 已生成 Podcast 縮圖: {out_path1.name} (1280x720)")

if __name__ == "__main__":
    make_craft_image()
    make_youtube_thumbnail()
    make_podcast_thumbnail()
