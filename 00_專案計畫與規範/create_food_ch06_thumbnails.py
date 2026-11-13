# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 06 章 視覺圖像與 1280x720 雙軌縮圖合成腳本
- 融合新竹都城隍廟百年古廟、烏心石雕龜桃粿印、紅麴紅龜粿與九降風米食文化
- 應用古典油畫調色（Rembrandt 暖金光影、深紅赤褐基調）
- 輸出：
  1. assets/images/food_ch06/food_ch06_hero_banner.jpg (16:9 橫幅主視覺)
  2. assets/images/food_ch06/food_ch06_rice_cake_craft.jpg (工藝微距特寫)
  3. assets/images/food_ch06/food_ch06_youtube_thumbnail.jpg (1280x720 說明短片縮圖)
  4. assets/images/food_ch06/food_ch06_podcast_thumbnail.jpg (1280x720 播客對談縮圖)
  5. 同步鏡像至 舌尖上的臺灣/assets/images/ch06/
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
IMG_DIR = BASE_DIR / "assets" / "images" / "food_ch06"
CH06_DIR = BASE_DIR / "舌尖上的臺灣" / "assets" / "images" / "ch06"
TEMP_DIR = Path(r"d:\Antigravity\科技歷史\temp_art")

IMG_DIR.mkdir(parents=True, exist_ok=True)
CH06_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/msjhbd.ttc"

def apply_oil_painting_warmth(img, warm_factor=1.15, contrast_factor=1.2, brightness=0.95):
    """將圖像轉換為古典寫實油畫調色風格"""
    enh_c = ImageEnhance.Contrast(img).enhance(contrast_factor)
    enh_col = ImageEnhance.Color(enh_c).enhance(1.25)
    enh_b = ImageEnhance.Brightness(enh_col).enhance(brightness)
    
    # 增加暖金與紅棕色調 (Rembrandt Chiaroscuro)
    r, g, b = enh_b.split()
    r = r.point(lambda i: min(255, int(i * 1.08 + 8)))
    g = g.point(lambda i: min(255, int(i * 0.98 + 2)))
    b = b.point(lambda i: max(0, int(i * 0.88 - 5)))
    return Image.merge("RGB", (r, g, b))

def build_hero_banner():
    """合成第 06 章 16:9 宏大歷史橫幅 (新竹都城隍廟與歲時米食神聖祭壇)"""
    w, h = 1920, 1080
    
    # 底層：新竹都城隍廟三川殿巍峨建築
    temple_path = TEMP_DIR / "temple.jpg"
    im_temple = Image.open(temple_path).convert("RGB")
    
    # 剪裁並縮放至 1920x1080
    tw, th = im_temple.size
    target_ratio = w / h
    current_ratio = tw / th
    if current_ratio > target_ratio:
        crop_w = int(th * target_ratio)
        offset = (tw - crop_w) // 2
        im_temple = im_temple.crop((offset, 0, offset + crop_w, th))
    else:
        crop_h = int(tw / target_ratio)
        offset = (th - crop_h) // 2
        im_temple = im_temple.crop((0, offset, tw, offset + crop_h))
    
    canvas = im_temple.resize((w, h), Image.Resampling.LANCZOS)
    canvas = apply_oil_painting_warmth(canvas, warm_factor=1.1, contrast_factor=1.15, brightness=0.9)
    
    # 融入八卦藻井金碧流光 (右上角半透明天工神韻)
    interior_path = TEMP_DIR / "temple_interior.jpg"
    if interior_path.exists():
        im_in = Image.open(interior_path).convert("RGB")
        im_in = im_in.resize((900, 675), Image.Resampling.LANCZOS)
        im_in = apply_oil_painting_warmth(im_in, contrast_factor=1.3, brightness=1.05)
        
        # 建立圓形羽化遮罩
        mask = Image.new("L", im_in.size, 0)
        draw_m = ImageDraw.Draw(mask)
        draw_m.ellipse([50, 50, 850, 625], fill=160)
        mask = mask.filter(ImageFilter.GaussianBlur(60))
        
        canvas.paste(im_in, (w - 850, -50), mask)

    # 融入前景神聖木雕粿印與紅龜粿 (右下角至正中微距靜物)
    mold_path = TEMP_DIR / "kue_mold.jpg"
    angku_path = TEMP_DIR / "ang_ku_kueh.jpg"
    
    if mold_path.exists():
        im_mold = Image.open(mold_path).convert("RGB")
        # 旋轉並縮放木印
        im_mold = im_mold.rotate(-15, expand=True, resample=Image.Resampling.BICUBIC)
        mw = 600
        mh = int(im_mold.height * (mw / im_mold.width))
        im_mold = im_mold.resize((mw, mh), Image.Resampling.LANCZOS)
        im_mold = apply_oil_painting_warmth(im_mold, contrast_factor=1.25, brightness=0.92)
        
        mold_mask = Image.new("L", im_mold.size, 0)
        draw_mm = ImageDraw.Draw(mold_mask)
        draw_mm.ellipse([40, 40, mw - 40, mh - 40], fill=210)
        mold_mask = mold_mask.filter(ImageFilter.GaussianBlur(35))
        
        canvas.paste(im_mold, (w - 680, h - mh + 50), mold_mask)

    if angku_path.exists():
        im_angku = Image.open(angku_path).convert("RGB")
        aw = 520
        ah = int(im_angku.height * (aw / im_angku.width))
        im_angku = im_angku.resize((aw, ah), Image.Resampling.LANCZOS)
        # 強調鮮紅紅麴
        enh_ang = ImageEnhance.Color(im_angku).enhance(1.4)
        enh_ang = ImageEnhance.Contrast(enh_ang).enhance(1.2)
        
        ang_mask = Image.new("L", im_angku.size, 0)
        draw_am = ImageDraw.Draw(ang_mask)
        draw_am.ellipse([30, 30, aw - 30, ah - 30], fill=230)
        ang_mask = ang_mask.filter(ImageFilter.GaussianBlur(30))
        
        canvas.paste(enh_ang, (w - 550, h - ah + 30), ang_mask)

    # 施加整體古典油畫暗角與香火薄霧
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_v = ImageDraw.Draw(vignette)
    
    # 左側暗區（提供文字與主題視覺呼吸）
    for x in range(w // 2):
        alpha = int((1.0 - (x / (w // 2))) * 140)
        draw_v.line([(x, 0), (x, h)], fill=(12, 8, 6, alpha))
        
    # 底部深沉暗角
    for y in range(h):
        if y > h - 400:
            alpha_b = int(((y - (h - 400)) / 400) * 160)
            draw_v.line([(0, y), (w, y)], fill=(10, 6, 4, alpha_b))
            
    canvas = Image.alpha_composite(canvas.convert("RGBA"), vignette).convert("RGB")
    
    # 輕微畫布紋理質感
    canvas = canvas.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=3))
    
    hero_out1 = IMG_DIR / "food_ch06_hero_banner.jpg"
    hero_out2 = CH06_DIR / "food_ch06_hero_banner.jpg"
    canvas.save(hero_out1, quality=95)
    canvas.save(hero_out2, quality=95)
    print(f"✅ 已成功合成並輸出 16:9 主視覺 Banner：{hero_out1.name}")

def build_craft_image():
    """合成工藝微距特寫：烏心石粿印、紅麴紅龜粿與古木工作台"""
    w, h = 1920, 1080
    mold_path = TEMP_DIR / "kue_mold.jpg"
    angku_path = TEMP_DIR / "ang_ku_kueh.jpg"
    
    im_mold = Image.open(mold_path).convert("RGB")
    tw, th = im_mold.size
    target_ratio = w / h
    crop_w = int(th * target_ratio)
    offset = (tw - crop_w) // 2
    canvas = im_mold.crop((offset, 0, offset + crop_w, th)).resize((w, h), Image.Resampling.LANCZOS)
    canvas = apply_oil_painting_warmth(canvas, warm_factor=1.2, contrast_factor=1.25, brightness=0.88)
    
    # 在左側融入特寫紅龜粿
    im_ang = Image.open(angku_path).convert("RGB")
    aw = 750
    ah = int(im_ang.height * (aw / im_ang.width))
    im_ang = im_ang.resize((aw, ah), Image.Resampling.LANCZOS)
    im_ang = apply_oil_painting_warmth(im_ang, warm_factor=1.3, contrast_factor=1.25, brightness=0.95)
    
    ang_mask = Image.new("L", im_ang.size, 0)
    draw_m = ImageDraw.Draw(ang_mask)
    draw_m.ellipse([40, 40, aw - 40, ah - 40], fill=225)
    ang_mask = ang_mask.filter(ImageFilter.GaussianBlur(40))
    
    canvas.paste(im_ang, (100, h - ah - 60), ang_mask)
    
    # 底部與邊緣暗角
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_v = ImageDraw.Draw(vignette)
    for y in range(h):
        alpha_t = int(max(0, 1.0 - (y / 250)) * 120)
        alpha_b = int(max(0, (y - (h - 350)) / 350) * 160)
        draw_v.line([(0, y), (w, y)], fill=(15, 10, 8, max(alpha_t, alpha_b)))
    
    canvas = Image.alpha_composite(canvas.convert("RGBA"), vignette).convert("RGB")
    craft_out1 = IMG_DIR / "food_ch06_rice_cake_craft.jpg"
    craft_out2 = CH06_DIR / "food_ch06_rice_cake_craft.jpg"
    canvas.save(craft_out1, quality=95)
    canvas.save(craft_out2, quality=95)
    print(f"✅ 已成功合成工藝特寫圖：{craft_out1.name}")

def make_youtube_thumbnail():
    """製作 1280x720 YouTube 說明影片封面縮圖（廟埕朱紅金黃暖色系）"""
    bg_path = IMG_DIR / "food_ch06_hero_banner.jpg"
    img = Image.open(bg_path).convert("RGBA")
    
    target_w, target_h = 1280, 720
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    # 底部深沉暗角
    for y in range(target_h):
        alpha_bottom = int(max(0, (y - 280) / 440) * 220)
        draw_ov.line([(0, y), (target_w, y)], fill=(16, 10, 8, alpha_bottom))
        
    # 左側文字閱讀保護漸變
    for x in range(780):
        alpha_left = int((1.0 - (x / 780)) * 175)
        for y in range(target_h):
            orig_color = overlay.getpixel((x, y))
            draw_ov.point((x, y), fill=(orig_color[0], orig_color[1], orig_color[2], min(255, orig_color[3] + alpha_left)))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    font_badge = ImageFont.truetype(FONT_PATH, 28)
    font_title = ImageFont.truetype(FONT_PATH, 68)
    font_sub = ImageFont.truetype(FONT_PATH, 34)
    font_meta = ImageFont.truetype(FONT_PATH, 24)
    
    # 1. 膠囊徽章 (城隍朱紅與暖金)
    bx, by = 60, 50
    badge_text = " 舌尖上的臺灣｜第 06 章 "
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 30
    bh = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(185, 28, 28, 245), outline=(254, 226, 226, 210), width=2)
    draw.text((bx + 15, by + 8), badge_text, fill=(255, 255, 255), font=font_badge)
    
    # 2. 主標題：廟埕香火與米食變奏
    tx, ty = 60, 420
    title_text = "廟埕香火與米食變奏"
    for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4)]:
        draw.text((tx + ox, ty + oy), title_text, fill=(0, 0, 0, 240), font=font_title)
    draw.text((tx, ty), title_text, fill=(255, 251, 235), font=font_title)
    
    # 3. 副標題
    sx, sy = 60, 520
    sub_text = "新竹米粉・紅龜粿・客家粄條・米苔目"
    for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((sx + ox, sy + oy), sub_text, fill=(0, 0, 0, 210), font=font_sub)
    draw.text((sx, sy), sub_text, fill=(254, 240, 138), font=font_sub)
    
    # 4. 元資料標籤
    mx, my = 60, 600
    meta_text = "在來米澱粉化學 ｜ 九降風天然氣刀 ｜ 歲時禮俗密碼"
    draw.text((mx + 1, my + 1), meta_text, fill=(0, 0, 0, 180), font=font_meta)
    draw.text((mx, my), meta_text, fill=(243, 244, 246), font=font_meta)
    
    out1 = IMG_DIR / "food_ch06_youtube_thumbnail.jpg"
    out2 = CH06_DIR / "food_ch06_youtube_thumbnail.jpg"
    out3 = CH06_DIR / "ch06_youtube_thumbnail.jpg"
    
    img = img.convert("RGB")
    img.save(out1, quality=95)
    img.save(out2, quality=95)
    img.save(out3, quality=95)
    print(f"✅ 已成功產製 YouTube 說明影片縮圖：{out1.name}")

def make_podcast_thumbnail():
    """製作 1280x720 Podcast 深度對談封面縮圖（深藍暖金對談系）"""
    bg_path = IMG_DIR / "food_ch06_rice_cake_craft.jpg"
    img = Image.open(bg_path).convert("RGBA")
    
    target_w, target_h = 1280, 720
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    # 深邃沉穩深藍底漸變 (8, 18, 38)
    for x in range(target_w):
        alpha_x = int(min(1.0, max(0, (750 - x) / 750)) * 220)
        draw_ov.line([(x, 0), (x, target_h)], fill=(8, 16, 32, alpha_x))
        
    for y in range(target_h):
        if y > 380:
            alpha_y = int(((y - 380) / 340) * 190)
            orig_line = [overlay.getpixel((px, y)) for px in range(target_w)]
            for px in range(target_w):
                c = orig_line[px]
                draw_ov.point((px, y), fill=(8, 14, 28, min(255, c[3] + alpha_y)))
                
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    font_badge = ImageFont.truetype(FONT_PATH, 26)
    font_title = ImageFont.truetype(FONT_PATH, 66)
    font_sub = ImageFont.truetype(FONT_PATH, 32)
    font_host = ImageFont.truetype(FONT_PATH, 24)
    font_meta = ImageFont.truetype(FONT_PATH, 22)
    
    # 1. 頂部徽章 (深藍底金邊)
    bx, by = 60, 50
    badge_text = " 深度對談｜FOOD PODCAST EP06 "
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 30
    bh = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(15, 23, 42, 240), outline=(234, 179, 8, 220), width=2)
    draw.text((bx + 15, by + 8), badge_text, fill=(254, 240, 138), font=font_badge)
    
    # 2. 播客主標題
    tx, ty = 60, 420
    title_text = "廟埕香火與米食變奏"
    for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4)]:
        draw.text((tx + ox, ty + oy), title_text, fill=(0, 0, 0, 240), font=font_title)
    draw.text((tx, ty), title_text, fill=(255, 255, 255), font=font_title)
    
    # 3. 播客副標題
    sx, sy = 60, 520
    sub_text = "從城隍廟祈年到客庄面帕粄的生命交響"
    for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((sx + ox, sy + oy), sub_text, fill=(0, 0, 0, 210), font=font_sub)
    draw.text((sx, sy), sub_text, fill=(250, 204, 21), font=font_sub)
    
    # 4. 對談亮點條列
    mx, my = 60, 600
    meta_text = "• 30%直鏈澱粉凝膠網絡 • 烏心石木模天人幾何 • 沸水大鼎2秒瞬時定型"
    draw.text((mx + 1, my + 1), meta_text, fill=(0, 0, 0, 200), font=font_meta)
    draw.text((mx, my), meta_text, fill=(226, 232, 240), font=font_meta)
    
    out1 = IMG_DIR / "food_ch06_podcast_thumbnail.jpg"
    out2 = CH06_DIR / "food_ch06_podcast_thumbnail.jpg"
    out3 = CH06_DIR / "ch06_podcast_thumbnail.jpg"
    
    img = img.convert("RGB")
    img.save(out1, quality=95)
    img.save(out2, quality=95)
    img.save(out3, quality=95)
    print(f"✅ 已成功產製 Podcast 深度對談縮圖：{out1.name}")

if __name__ == "__main__":
    print("🎨 開始合成《舌尖上的臺灣》第 06 章全系列視覺圖與雙軌縮圖...")
    build_hero_banner()
    build_craft_image()
    make_youtube_thumbnail()
    make_podcast_thumbnail()
    print("✨ 第 06 章所有視覺資產產製完成！")
