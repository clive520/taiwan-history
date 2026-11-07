# -*- coding: utf-8 -*-
"""
生成第 18 章 高點擊率 YouTube 影片與播客縮圖（全系列完結篇）
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
    
    # 科技感深色暗角遮罩
    for x in range(920):
        alpha = int(230 * (1 - (x / 920) ** 1.3))
        draw_overlay.line([(x, 0), (x, target_h)], fill=(10, 15, 25, alpha))
        
    for y in range(target_h - 260, target_h):
        prog = (y - (target_h - 260)) / 260
        alpha = int(215 * (prog ** 1.2))
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
    
    # 頂部主題徽章
    tag_bg = (195, 25, 25, 240) if not is_podcast else (18, 95, 175, 240)
    tag_bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_h = tag_bbox[3] - tag_bbox[1]
    
    pad_x, pad_y = 20, 8
    pill_box = [start_x, start_y, start_x + tag_w + pad_x * 2, start_y + tag_h + pad_y * 2]
    draw.rounded_rectangle(pill_box, radius=12, fill=tag_bg, outline=(255, 255, 255, 200), width=2)
    draw.text((start_x + pad_x, start_y + pad_y - 2), tag_text, fill=(255, 255, 255), font=font_tag)
    
    y_l1 = start_y + tag_h + pad_y * 2 + 35
    
    # 雙層文字陰影渲染函數
    def draw_text_with_shadow(draw_obj, pos, text, font, fill_color, shadow_color=(0, 0, 0, 240), offset=4):
        x, y = pos
        for dx in range(-offset, offset + 1):
            for dy in range(-offset, offset + 1):
                if dx*dx + dy*dy <= offset*offset:
                    draw_obj.text((x + dx, y + dy), text, font=font, fill=shadow_color)
        draw_obj.text((x, y), text, font=font, fill=fill_color)
    
    color_l1 = (255, 230, 40) if not is_podcast else (255, 255, 255)
    draw_text_with_shadow(draw, (start_x, y_l1), line1, font_l1, color_l1, offset=5)
    
    y_l2 = y_l1 + 105
    color_l2 = (255, 255, 255) if not is_podcast else (255, 215, 0)
    draw_text_with_shadow(draw, (start_x, y_l2), line2, font_l2, color_l2, offset=5)
    
    y_l3 = y_l2 + 120
    color_l3 = (210, 240, 255) if not is_podcast else (180, 230, 255)
    draw_text_with_shadow(draw, (start_x, y_l3), line3, font_l3, color_l3, offset=3)
    
    # 右下角醒目角標
    sub_tag = "400年全系列完結篇" if not is_podcast else "高音質無損串流"
    sub_font = ImageFont.truetype(font_path, 28)
    sub_bbox = draw.textbbox((0, 0), sub_tag, font=sub_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_h = sub_bbox[3] - sub_bbox[1]
    
    badge_x = target_w - sub_w - 75
    badge_y = target_h - sub_h - 60
    badge_box = [badge_x - 15, badge_y - 8, badge_x + sub_w + 15, badge_y + sub_h + 8]
    draw.rounded_rectangle(badge_box, radius=10, fill=(0, 0, 0, 190), outline=(255, 215, 0, 220), width=2)
    draw.text((badge_x, badge_y - 2), sub_tag, fill=(255, 215, 0), font=sub_font)
    
    # 轉為 RGB 並儲存高品質 JPEG
    im.convert("RGB").save(out_path, "JPEG", quality=95)
    print(f"✅ 縮圖已成功生成：{out_path}")

if __name__ == "__main__":
    base_dir = Path(r"d:\Antigravity\科技歷史\臺灣史")
    ch18_img_dir = base_dir / "assets/images/ch18"
    
    bg_video = ch18_img_dir / "ch18_hero_banner.jpg"
    bg_podcast = ch18_img_dir / "ch18_wafer_cleanroom.jpg"
    
    out_video = ch18_img_dir / "ch18_youtube_thumbnail.jpg"
    out_podcast = ch18_img_dir / "ch18_podcast_thumbnail.jpg"
    
    if bg_video.exists():
        create_thumbnail(
            bg_video, out_video,
            tag_text="【臺灣史 第18章・完結篇】",
            line1="矽島崛起",
            line2="與世界舞台",
            line3="客廳即工廠・竹科奇蹟・台積電傳奇",
            is_podcast=False
        )
    else:
        print(f"⏳ 背景檔案不存在：{bg_video}")
        
    if bg_podcast.exists():
        create_thumbnail(
            bg_podcast, out_podcast,
            tag_text="【臺灣史 PODCAST EP18・完結篇】",
            line1="撼動世界的",
            line2="奈米奇蹟！",
            line3="豆漿店豪賭・張忠謀純代工・矽盾傳奇",
            is_podcast=True
        )
    else:
        print(f"⏳ 背景檔案不存在：{bg_podcast}")
