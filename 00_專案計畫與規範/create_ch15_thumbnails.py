# -*- coding: utf-8 -*-
"""
生成第 15 章 高點擊率 YouTube 影片與播客縮圖
規範：1280x720 HD、簡化大字、強對比度、陰影外框、無 Emoji
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

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
    
    tag_bg = (195, 25, 25, 240) if not is_podcast else (18, 95, 175, 240)
    tag_bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_h = tag_bbox[3] - tag_bbox[1]
    
    pad_x, pad_y = 20, 8
    pill_box = [start_x, start_y, start_x + tag_w + pad_x * 2, start_y + tag_h + pad_y * 2]
    draw.rounded_rectangle(pill_box, radius=12, fill=tag_bg, outline=(255, 255, 255, 200), width=2)
    draw.text((start_x + pad_x, start_y + pad_y - 2), tag_text, font=font_tag, fill=(255, 255, 255))
    
    y_l1 = start_y + tag_h + pad_y * 2 + 35
    for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (0, -4), (-4, 0)]:
        draw.text((start_x + dx, y_l1 + dy), line1, font=font_l1, fill=(0, 0, 0))
    color_l1 = (255, 225, 25) if not is_podcast else (100, 220, 255)
    draw.text((start_x, y_l1), line1, font=font_l1, fill=color_l1)
    
    y_l2 = y_l1 + 105
    for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (0, -4), (-4, 0)]:
        draw.text((start_x + dx, y_l2 + dy), line2, font=font_l2, fill=(0, 0, 0))
    draw.text((start_x, y_l2), line2, font=font_l2, fill=(255, 255, 255))
    
    y_l3 = y_l2 + 125
    l3_bbox = draw.textbbox((0, 0), line3, font=font_l3)
    l3_w = l3_bbox[2] - l3_bbox[0]
    l3_h = l3_bbox[3] - l3_bbox[1]
    draw.rounded_rectangle([start_x, y_l3 - 6, start_x + l3_w + 24, y_l3 + l3_h + 10], radius=8, fill=(0, 0, 0, 160))
    draw.text((start_x + 12, y_l3), line3, font=font_l3, fill=(230, 235, 245))
    
    final_rgb = im.convert("RGB")
    final_rgb.save(out_path, "JPEG", quality=95)
    print(f"✅ 縮圖已成功生成：{out_path} ({target_w}x{target_h})")

def main():
    base_dir = Path("D:/Antigravity/科技歷史/臺灣史")
    ch15_img_dir = base_dir / "assets/images/ch15"
    ch15_img_dir.mkdir(parents=True, exist_ok=True)
    
    bg_video = ch15_img_dir / "ch15_hero_banner.jpg"
    out_video = ch15_img_dir / "ch15_youtube_thumbnail.jpg"
    
    create_thumbnail(
        bg_path=bg_video,
        out_path=out_video,
        tag_text="臺灣史 EP15",
        line1="臺灣人的臺灣！",
        line2="啟蒙與血的警鐘",
        line3="蔣渭水文化協會 × 議會請願 × 霧社事件",
        is_podcast=False
    )
    
    bg_podcast = ch15_img_dir / "ch15_wushe_uprising.jpg"
    out_podcast = ch15_img_dir / "ch15_podcast_thumbnail.jpg"
    
    create_thumbnail(
        bg_path=bg_podcast,
        out_path=out_podcast,
        tag_text="PODCAST 深度對談 EP15",
        line1="筆桿與彩虹橋",
        line2="臺灣魂的覺醒！",
        line3="文化協會啟蒙風暴與賽德克最後誓約",
        is_podcast=True
    )

if __name__ == "__main__":
    main()
