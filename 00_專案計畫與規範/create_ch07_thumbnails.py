# -*- coding: utf-8 -*-
"""
生成第 07 章 高點擊率 YouTube 影片與播客縮圖
規範：1280x720 HD、簡化大字、強對比度、陰影外框、無 Emoji
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_thumbnail(bg_path, out_path, tag_text, line1, line2, line3, is_podcast=False):
    # 1. 讀取背景圖並裁切縮放為 1280x720
    im = Image.open(bg_path).convert("RGBA")
    target_w, target_h = 1280, 720
    
    # 保持比例縮放並居中裁切
    scale = max(target_w / im.width, target_h / im.height)
    new_w = int(im.width * scale)
    new_h = int(im.height * scale)
    im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    im = im.crop((left, top, left + target_w, top + target_h))
    
    # 2. 建立漸層遮罩（左側深色陰影便於襯托大字，底部深色漸層）
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    # 左側暗部漸層（寬度 850px）
    for x in range(850):
        alpha = int(220 * (1 - (x / 850) ** 1.3))
        draw_overlay.line([(x, 0), (x, target_h)], fill=(10, 15, 25, alpha))
        
    # 底部暗部漸層（高度 250px）
    for y in range(target_h - 250, target_h):
        prog = (y - (target_h - 250)) / 250
        alpha = int(210 * (prog ** 1.2))
        draw_overlay.line([(0, y), (target_w, y)], fill=(5, 10, 18, alpha))
        
    im = Image.alpha_composite(im, overlay)
    draw = ImageDraw.Draw(im)
    
    # 3. 字體設定
    font_path = "C:/Windows/Fonts/msjhbd.ttc"  # 微軟正黑體 粗體
    
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
    
    # (B) 主標第 1 行（金黃色超大字 + 黑色外框與立體陰影）
    y_l1 = start_y + tag_h + pad_y * 2 + 35
    # 陰影
    draw.text((start_x + 5, y_l1 + 5), line1, font=font_l1, fill=(0, 0, 0, 240), stroke_width=6, stroke_fill=(0, 0, 0))
    # 主體
    draw.text((start_x, y_l1), line1, font=font_l1, fill=(255, 230, 0), stroke_width=6, stroke_fill=(15, 15, 15))
    
    # (C) 主標第 2 行（純白色超大字 + 黑色外框與立體陰影）
    y_l2 = y_l1 + 115
    draw.text((start_x + 5, y_l2 + 5), line2, font=font_l2, fill=(0, 0, 0, 240), stroke_width=6, stroke_fill=(0, 0, 0))
    draw.text((start_x, y_l2), line2, font=font_l2, fill=(255, 255, 255), stroke_width=6, stroke_fill=(15, 15, 15))
    
    # (D) 副標第 3 行（青色/金色長條膠囊）
    y_l3 = y_l2 + 130
    sub_bbox = draw.textbbox((0, 0), line3, font=font_l3)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_h = sub_bbox[3] - sub_bbox[1]
    
    sub_pad_x, sub_pad_y = 22, 10
    sub_box = [start_x, y_l3, start_x + sub_w + sub_pad_x * 2, y_l3 + sub_h + sub_pad_y * 2]
    sub_bg = (15, 45, 80, 230) if not is_podcast else (40, 25, 75, 230)
    sub_border = (0, 220, 255) if not is_podcast else (240, 190, 70)
    
    draw.rounded_rectangle(sub_box, radius=10, fill=sub_bg, outline=sub_border, width=2)
    draw.text((start_x + sub_pad_x, y_l3 + sub_pad_y - 2), line3, font=font_l3, fill=(240, 245, 255))
    
    # 4. 輸出保存為 RGB JPEG
    im_final = im.convert("RGB")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    im_final.save(out_path, "JPEG", quality=95)
    print(f"✅ 成功生成封面縮圖：{out_path} ({Path(out_path).stat().st_size / 1024:.1f} KB)")

def main():
    base_dir = Path("d:/Antigravity/科技歷史/臺灣史")
    
    # 1. 說明影片封面
    bg_video = base_dir / "assets/images/ch07/ch07_hero_banner.jpg"
    out_video = base_dir / "assets/images/ch07/ch07_youtube_thumbnail.jpg"
    create_thumbnail(
        bg_path=bg_video,
        out_path=out_video,
        tag_text="【臺灣史 EP07】重點解說",
        line1="決戰九個月！",
        line2="擊潰荷蘭帝國",
        line3="熱蘭遮城大圍攻・鄭成功收復臺灣歷史真相",
        is_podcast=False
    )
    
    # 2. 播客專題封面
    bg_podcast = base_dir / "assets/images/ch07/ch07_coyett_surrender.jpg"
    out_podcast = base_dir / "assets/images/ch07/ch07_podcast_thumbnail.jpg"
    create_thumbnail(
        bg_path=bg_podcast,
        out_path=out_podcast,
        tag_text="【臺灣史 PODCAST EP07】",
        line1="熱蘭遮大圍城",
        line2="驅荷復臺秘辛",
        line3="雙人深度對談 25分鐘・鹿耳門奇蹟與降約真相",
        is_podcast=True
    )

if __name__ == "__main__":
    main()
