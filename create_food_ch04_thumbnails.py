# -*- coding: utf-8 -*-
"""
生成《舌尖上的臺灣》第 04 章 1280x720 雙軌縮圖
1. YouTube 說明短片縮圖：肉臊暖金風格/五條港碼頭肉臊攤
2. Podcast 深度對談縮圖：深褐琥珀金風格/紅蔥酥與黑豆陶缸
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
IMG_DIR = BASE_DIR / "assets" / "images" / "food_ch04"
CH04_DIR = BASE_DIR / "舌尖上的臺灣" / "assets" / "images" / "ch04"

IMG_DIR.mkdir(parents=True, exist_ok=True)
CH04_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/msjhbd.ttc"

def make_youtube_thumbnail():
    bg_path = IMG_DIR / "food_ch04_hero_banner.jpg"
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
    
    # 建立多層次暗部漸層遮罩 (焦糖深褐微墨黑)
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    for y in range(target_h):
        alpha_bottom = int(max(0, (y - 280) / 440) * 205)
        draw_ov.line([(0, y), (target_w, y)], fill=(18, 10, 8, alpha_bottom))
        
    for x in range(750):
        alpha_left = int((1.0 - (x / 750)) * 160)
        for y in range(target_h):
            orig_color = overlay.getpixel((x, y))
            draw_ov.point((x, y), fill=(orig_color[0], orig_color[1], orig_color[2], min(255, orig_color[3] + alpha_left)))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    font_badge = ImageFont.truetype(FONT_PATH, 28)
    font_title = ImageFont.truetype(FONT_PATH, 72)
    font_sub = ImageFont.truetype(FONT_PATH, 34)
    font_meta = ImageFont.truetype(FONT_PATH, 24)
    
    # 1. 系列徽章 (肉燥焦糖暖金頂部卡片)
    bx, by = 60, 50
    badge_text = " 舌尖上的臺灣・第 04 章 "
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 30
    bh = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(180, 83, 9, 240), outline=(254, 243, 199, 200), width=2)
    draw.text((bx + 15, by + 8), badge_text, fill=(255, 255, 255), font=font_badge)
    
    # 2. 主標題 (一碗肉臊的百年身世)
    tx, ty = 60, 420
    title_text = "一碗肉臊的百年身世"
    for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4)]:
        draw.text((tx + ox, ty + oy), title_text, fill=(0, 0, 0, 220), font=font_title)
    draw.text((tx, ty), title_text, fill=(255, 251, 235), font=font_title)
    
    # 3. 副標題
    sx, sy = 60, 520
    sub_text = "黑豬肉・紅蔥頭・黑豆蔭油"
    for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((sx + ox, sy + oy), sub_text, fill=(0, 0, 0, 200), font=font_sub)
    draw.text((sx, sy), sub_text, fill=(251, 191, 36), font=font_sub)
    
    # 4. 底部資訊欄標籤
    mx, my = 60, 595
    meta_text = "府城五條港碼頭 / 羅漢腳碎肉封存 / 黑豆陶缸日曬工藝"
    draw.text((mx, my), meta_text, fill=(214, 211, 209), font=font_meta)
    
    # 存檔
    out_rgb = img.convert("RGB")
    out_path1 = IMG_DIR / "food_ch04_youtube_thumbnail.jpg"
    out_path2 = CH04_DIR / "ch04_youtube_thumbnail.jpg"
    out_rgb.save(out_path1, quality=95)
    out_rgb.save(out_path2, quality=95)
    print(f"✅ 已生成 YouTube 縮圖: {out_path1.name} (1280x720)")

def make_podcast_thumbnail():
    bg_path = IMG_DIR / "food_ch04_braised_pork.jpg"
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
        alpha_bottom = int(max(0, (y - 260) / 460) * 215)
        draw_ov.line([(0, y), (target_w, y)], fill=(20, 10, 8, alpha_bottom))
        
    for x in range(720):
        alpha_left = int((1.0 - (x / 720)) * 165)
        for y in range(target_h):
            orig_color = overlay.getpixel((x, y))
            draw_ov.point((x, y), fill=(orig_color[0], orig_color[1], orig_color[2], min(255, orig_color[3] + alpha_left)))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    font_badge = ImageFont.truetype(FONT_PATH, 28)
    font_title = ImageFont.truetype(FONT_PATH, 68)
    font_sub = ImageFont.truetype(FONT_PATH, 34)
    font_meta = ImageFont.truetype(FONT_PATH, 24)
    
    # 1. 播客標籤 (深褐底 + 暖琥珀金邊框)
    bx, by = 60, 50
    badge_text = " 深度對談 PODCAST・EP 04 "
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 30
    bh = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(28, 16, 12, 240), outline=(245, 158, 11, 220), width=2)
    draw.text((bx + 15, by + 8), badge_text, fill=(251, 191, 36), font=font_badge)
    
    # 2. 播客主標 (深度對談：一碗肉臊的百年身世)
    tx, ty = 60, 420
    title_text = "深度對談：一碗肉臊的百年身世"
    for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4)]:
        draw.text((tx + ox, ty + oy), title_text, fill=(0, 0, 0, 230), font=font_title)
    draw.text((tx, ty), title_text, fill=(255, 255, 255), font=font_title)
    
    # 3. 播客副標
    sx, sy = 60, 520
    sub_text = "從羅漢腳碎肉封存到南北流派大辯證"
    for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((sx + ox, sy + oy), sub_text, fill=(0, 0, 0, 200), font=font_sub)
    draw.text((sx, sy), sub_text, fill=(251, 191, 36), font=font_sub)
    
    # 4. 底部資訊欄
    mx, my = 60, 595
    meta_text = "手切帶皮五花 / 豬油爆煸紅蔥酥 / 180天陶缸熟成醬香"
    draw.text((mx, my), meta_text, fill=(214, 211, 209), font=font_meta)
    
    out_rgb = img.convert("RGB")
    out_path1 = IMG_DIR / "food_ch04_podcast_thumbnail.jpg"
    out_path2 = CH04_DIR / "ch04_podcast_thumbnail.jpg"
    out_rgb.save(out_path1, quality=95)
    out_rgb.save(out_path2, quality=95)
    print(f"✅ 已生成 Podcast 縮圖: {out_path1.name} (1280x720)")

if __name__ == "__main__":
    make_youtube_thumbnail()
    make_podcast_thumbnail()
