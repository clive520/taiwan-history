# -*- coding: utf-8 -*-
"""
生成《舌尖上的臺灣》第 03 章 1280x720 雙軌縮圖
1. YouTube 說明短片縮圖：琥珀金/瓦盤鹽田/黑水溝
2. Podcast 深度對談縮圖：深海藍/烏魚子日光熟成
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
IMG_DIR = BASE_DIR / "assets" / "images" / "food_ch03"
CH03_DIR = BASE_DIR / "舌尖上的臺灣" / "assets" / "images" / "ch03"

FONT_PATH = "C:/Windows/Fonts/msjhbd.ttc"

def make_youtube_thumbnail():
    bg_path = IMG_DIR / "food_ch03_hero_banner.jpg"
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
    
    # 建立多層次暗部漸層遮罩 (海青深藍微墨黑)
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    for y in range(target_h):
        alpha_bottom = int(max(0, (y - 280) / 440) * 200)
        draw_ov.line([(0, y), (target_w, y)], fill=(10, 18, 30, alpha_bottom))
        
    for x in range(720):
        alpha_left = int((1.0 - (x / 720)) * 150)
        for y in range(target_h):
            orig_color = overlay.getpixel((x, y))
            draw_ov.point((x, y), fill=(orig_color[0], orig_color[1], orig_color[2], min(255, orig_color[3] + alpha_left)))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    font_badge = ImageFont.truetype(FONT_PATH, 28)
    font_title = ImageFont.truetype(FONT_PATH, 72)
    font_sub = ImageFont.truetype(FONT_PATH, 34)
    font_meta = ImageFont.truetype(FONT_PATH, 24)
    
    # 1. 系列徽章 (澄金橘頂部卡片)
    bx, by = 60, 50
    badge_text = " 舌尖上的臺灣・第 03 章 "
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 30
    bh = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(217, 119, 6, 240), outline=(254, 243, 199, 200), width=2)
    draw.text((bx + 15, by + 8), badge_text, fill=(255, 255, 255), font=font_badge)
    
    # 2. 主標題 (黑水溝的鹹香與烏金)
    tx, ty = 60, 420
    title_text = "黑水溝的鹹香與烏金"
    for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4)]:
        draw.text((tx + ox, ty + oy), title_text, fill=(0, 0, 0, 220), font=font_title)
    draw.text((tx, ty), title_text, fill=(255, 251, 235), font=font_title)
    
    # 3. 副標題
    sx, sy = 60, 520
    sub_text = "瓦盤鹽田・信魚傳奇・琥珀烏金"
    for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((sx + ox, sy + oy), sub_text, fill=(0, 0, 0, 200), font=font_sub)
    draw.text((sx, sy), sub_text, fill=(251, 191, 36), font=font_sub)
    
    # 4. 底部資訊欄標籤
    mx, my = 60, 595
    meta_text = "臺南安平 / 瀨口鹽田 / 荷治烏魚旗 / 冬至黑潮季風"
    draw.text((mx, my), meta_text, fill=(203, 213, 225), font=font_meta)
    
    # 存檔
    out_rgb = img.convert("RGB")
    out_path1 = IMG_DIR / "food_ch03_youtube_thumbnail.jpg"
    out_path2 = CH03_DIR / "ch03_youtube_thumbnail.jpg"
    out_rgb.save(out_path1, quality=95)
    out_rgb.save(out_path2, quality=95)
    print(f"✅ 已生成 YouTube 縮圖: {out_path1.name} (1280x720)")

def make_podcast_thumbnail():
    bg_path = IMG_DIR / "food_ch03_mullet_roe.jpg"
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
        alpha_bottom = int(max(0, (y - 260) / 460) * 210)
        draw_ov.line([(0, y), (target_w, y)], fill=(8, 14, 24, alpha_bottom))
        
    for x in range(700):
        alpha_left = int((1.0 - (x / 700)) * 160)
        for y in range(target_h):
            orig_color = overlay.getpixel((x, y))
            draw_ov.point((x, y), fill=(orig_color[0], orig_color[1], orig_color[2], min(255, orig_color[3] + alpha_left)))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    font_badge = ImageFont.truetype(FONT_PATH, 28)
    font_title = ImageFont.truetype(FONT_PATH, 74)
    font_sub = ImageFont.truetype(FONT_PATH, 34)
    font_meta = ImageFont.truetype(FONT_PATH, 24)
    
    # 1. 播客標籤 (沉穩群青藍底 + 暖金邊框)
    bx, by = 60, 50
    badge_text = " 深度對談 PODCAST・EP 03 "
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 30
    bh = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(15, 23, 42, 240), outline=(245, 158, 11, 220), width=2)
    draw.text((bx + 15, by + 8), badge_text, fill=(251, 191, 36), font=font_badge)
    
    # 2. 播客主標 (浪尖上的金色奇蹟)
    tx, ty = 60, 420
    title_text = "浪尖上的金色奇蹟"
    for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4)]:
        draw.text((tx + ox, ty + oy), title_text, fill=(0, 0, 0, 230), font=font_title)
    draw.text((tx, ty), title_text, fill=(255, 255, 255), font=font_title)
    
    # 3. 播客副標
    sx, sy = 60, 520
    sub_text = "黑水溝的鹹水命與烏金傳奇"
    for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((sx + ox, sy + oy), sub_text, fill=(0, 0, 0, 200), font=font_sub)
    draw.text((sx, sy), sub_text, fill=(251, 191, 36), font=font_sub)
    
    # 4. 底部資訊欄
    mx, my = 60, 595
    meta_text = "陳永華天日曬鹽 / 鹹水泡飯抗病學 / 六道微米熟成"
    draw.text((mx, my), meta_text, fill=(226, 232, 240), font=font_meta)
    
    out_rgb = img.convert("RGB")
    out_path1 = IMG_DIR / "food_ch03_podcast_thumbnail.jpg"
    out_path2 = CH03_DIR / "ch03_podcast_thumbnail.jpg"
    out_rgb.save(out_path1, quality=95)
    out_rgb.save(out_path2, quality=95)
    print(f"✅ 已生成 Podcast 縮圖: {out_path1.name} (1280x720)")

if __name__ == "__main__":
    make_youtube_thumbnail()
    make_podcast_thumbnail()
