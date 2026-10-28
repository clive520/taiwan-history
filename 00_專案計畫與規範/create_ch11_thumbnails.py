# -*- coding: utf-8 -*-
"""
生成第 11 章 高點擊率 YouTube 影片與播客縮圖
規範：1280x720 HD、簡化大字、強對比度、陰影外框、無 Emoji
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_thumbnail(bg_path, out_path, tag_text, line1, line2, line3, is_podcast=False):
    im = Image.open(bg_path).convert("RGBA")
    target_w, target_h = 1280, 720
    
    scale = max(target_w / im.width, target_h / im.height)
    new_w = int(im.width * scale)
    new_h = int(im.height * scale)
    im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    im = im.crop((left, top, left + target_w, top + target_h))
    
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    for x in range(880):
        alpha = int(225 * (1 - (x / 880) ** 1.3))
        draw_overlay.line([(x, 0), (x, target_h)], fill=(10, 15, 25, alpha))
        
    for y in range(target_h - 250, target_h):
        prog = (y - (target_h - 250)) / 250
        alpha = int(210 * (prog ** 1.2))
        draw_overlay.line([(0, y), (target_w, y)], fill=(5, 10, 18, alpha))
        
    im = Image.alpha_composite(im, overlay)
    draw = ImageDraw.Draw(im)
    
    font_path = "C:/Windows/Fonts/msjhbd.ttc"
    
    font_tag = ImageFont.truetype(font_path, 34)
    font_l1 = ImageFont.truetype(font_path, 88)
    font_l2 = ImageFont.truetype(font_path, 88)
    font_l3 = ImageFont.truetype(font_path, 36)
    
    start_x = 75
    start_y = 65
    
    # (A) 頂部膠囊徽章 (Pill Badge)
    tag_bg = (195, 25, 25, 240) if not is_podcast else (18, 95, 175, 240)
    tag_bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_h = tag_bbox[3] - tag_bbox[1]
    
    pad_x, pad_y = 20, 8
    pill_box = [start_x, start_y, start_x + tag_w + pad_x * 2, start_y + tag_h + pad_y * 2]
    draw.rounded_rectangle(pill_box, radius=12, fill=tag_bg, outline=(255, 255, 255, 200), width=2)
    draw.text((start_x + pad_x, start_y + pad_y - 2), tag_text, font=font_tag, fill=(255, 255, 255))
    
    # (B) 主標第 1 行
    y_l1 = start_y + tag_h + pad_y * 2 + 35
    draw.text((start_x + 5, y_l1 + 5), line1, font=font_l1, fill=(0, 0, 0, 240), stroke_width=6, stroke_fill=(0, 0, 0))
    draw.text((start_x, y_l1), line1, font=font_l1, fill=(255, 230, 0), stroke_width=6, stroke_fill=(15, 15, 15))
    
    # (C) 主標第 2 行
    y_l2 = y_l1 + 105
    color_l2 = (255, 255, 255) if not is_podcast else (100, 220, 255)
    draw.text((start_x + 5, y_l2 + 5), line2, font=font_l2, fill=(0, 0, 0, 240), stroke_width=6, stroke_fill=(0, 0, 0))
    draw.text((start_x, y_l2), line2, font=font_l2, fill=color_l2, stroke_width=6, stroke_fill=(15, 15, 15))
    
    # (D) 副標第 3 行
    y_l3 = y_l2 + 115
    pad_box_x, pad_box_y = 16, 6
    l3_bbox = draw.textbbox((0, 0), line3, font=font_l3)
    l3_w = l3_bbox[2] - l3_bbox[0]
    l3_h = l3_bbox[3] - l3_bbox[1]
    
    box_sub = [start_x, y_l3, start_x + l3_w + pad_box_x * 2, y_l3 + l3_h + pad_box_y * 2]
    draw.rounded_rectangle(box_sub, radius=8, fill=(0, 0, 0, 190), outline=(255, 255, 255, 100), width=1)
    draw.text((start_x + pad_box_x, y_l3 + pad_box_y - 2), line3, font=font_l3, fill=(240, 240, 240))
    
    # 存檔
    out_rgb = im.convert("RGB")
    out_rgb.save(out_path, "JPEG", quality=92)
    print(f"[OK] 生成成功: {out_path} ({Path(out_path).stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    base_dir = Path("d:/Antigravity/科技歷史/臺灣史")
    ch11_img_dir = base_dir / "assets/images/ch11"
    ch11_img_dir.mkdir(parents=True, exist_ok=True)
    
    hero_img = ch11_img_dir / "ch11_hero_banner.jpg"
    sub_img = ch11_img_dir / "ch11_hero_banner.jpg"  # 若有第二張則可換
    
    # 1. 說明影片縮圖
    video_thumb = ch11_img_dir / "ch11_youtube_thumbnail.jpg"
    create_thumbnail(
        bg_path=hero_img,
        out_path=video_thumb,
        tag_text="臺灣史 EP11",
        line1="三年一反五年一亂！",
        line2="朱一貴與林爽文生死博弈",
        line3="天地會大里杙誓師 · 諸羅城極限圍城與六堆義民",
        is_podcast=False
    )
    
    # 2. 播客專題縮圖
    podcast_thumb = ch11_img_dir / "ch11_podcast_thumbnail.jpg"
    create_thumbnail(
        bg_path=sub_img,
        out_path=podcast_thumb,
        tag_text="歷史大對談 EP11",
        line1="天地會與全島械鬥",
        line2="官逼民反與生存博弈",
        line3="雙人深度對談 20分鐘 · 黑色義民旗與乾隆十全武功",
        is_podcast=True
    )
