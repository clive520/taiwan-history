# -*- coding: utf-8 -*-
"""
生成《舌尖上的臺灣》第 15 章全套高畫質視覺素材與雙軌縮圖
1. food_ch15_hero_banner.jpg (1920x1080)
2. food_ch15_michelin_craft.jpg (1920x1080)
3. food_ch15_podcast_bg.jpg (1920x1080 嚴格無拉伸背景)
4. food_ch15_youtube_thumbnail.jpg (1280x720 說明短片縮圖)
5. food_ch15_podcast_thumbnail.jpg (1280x720 播客長片縮圖)
"""
import sys
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
OUT_DIR1 = BASE_DIR / "assets" / "images" / "food_ch15"
OUT_DIR2 = BASE_DIR / "舌尖上的臺灣" / "assets" / "images" / "food_ch15"

OUT_DIR1.mkdir(parents=True, exist_ok=True)
OUT_DIR2.mkdir(parents=True, exist_ok=True)

RAW_HERO = Path(r"C:\Users\admin\.gemini\antigravity\brain\e6ad31e6-5e47-44d3-86ec-3061599c52d4\chapter15_hero_banner_1795475686209.jpg")
RAW_CRAFT = Path(r"C:\Users\admin\.gemini\antigravity\brain\e6ad31e6-5e47-44d3-86ec-3061599c52d4\taiwan_culinary_craft_ch15_1795475690940.jpg")
FONT_PATH = "C:/Windows/Fonts/msjhbd.ttc"

print("1. 處理 1920x1080 主視覺與工藝圖 (嚴格 ImageOps.fit 無拉伸)...")
hero_img = Image.open(RAW_HERO).convert("RGB")
hero_1080 = ImageOps.fit(hero_img, (1920, 1080), method=Image.Resampling.LANCZOS)
hero_1080.save(OUT_DIR1 / "food_ch15_hero_banner.jpg", quality=95)

craft_img = Image.open(RAW_CRAFT).convert("RGB")
craft_1080 = ImageOps.fit(craft_img, (1920, 1080), method=Image.Resampling.LANCZOS)
craft_1080.save(OUT_DIR1 / "food_ch15_michelin_craft.jpg", quality=95)

print("2. 製作 1920x1080 播客無拉伸底圖 (food_ch15_podcast_bg.jpg)...")
# 對 Hero Banner 進行優雅的暗角與微深邃調色處理，適合作為 1080p 影片背景
bg_base = hero_1080.copy()
enh_c = ImageEnhance.Contrast(bg_base).enhance(1.08)
enh_b = ImageEnhance.Brightness(enh_c).enhance(0.92)

# 加一個深邃漸變遮罩
vignette = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
for y in range(1080):
    a = int(min(180, (y / 1080) ** 1.5 * 190))
    v_draw.line([(0, y), (1920, y)], fill=(10, 8, 12, a))
# 四周暗角
for x in range(300):
    a_x = int((1.0 - (x / 300)) * 140)
    for y in range(1080):
        c = vignette.getpixel((x, y))
        v_draw.point((x, y), fill=(10, 8, 12, min(255, c[3] + a_x)))
    for y in range(1080):
        rx = 1919 - x
        c = vignette.getpixel((rx, y))
        v_draw.point((rx, y), fill=(10, 8, 12, min(255, c[3] + a_x)))

bg_final = Image.alpha_composite(enh_b.convert("RGBA"), vignette).convert("RGB")
bg_final.save(OUT_DIR1 / "food_ch15_podcast_bg.jpg", quality=95)

print("3. 製作 1280x720 說明短片封面縮圖 (food_ch15_youtube_thumbnail.jpg)...")
yt_bg = ImageOps.fit(hero_img, (1280, 720), method=Image.Resampling.LANCZOS).convert("RGBA")
ov_yt = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
d_ov = ImageDraw.Draw(ov_yt)

# 底部與左側漸變遮罩
for y in range(720):
    if y > 240:
        a = int(((y - 240) / 480) ** 1.2 * 230)
        d_ov.line([(0, y), (1280, y)], fill=(8, 10, 15, a))
for x in range(850):
    a = int((1.0 - (x / 850)) * 190)
    for y in range(720):
        orig = ov_yt.getpixel((x, y))
        d_ov.point((x, y), fill=(8, 10, 15, min(255, orig[3] + a)))

yt_comp = Image.alpha_composite(yt_bg, ov_yt)
draw_yt = ImageDraw.Draw(yt_comp)

font_badge = ImageFont.truetype(FONT_PATH, 28)
font_title = ImageFont.truetype(FONT_PATH, 66)
font_sub = ImageFont.truetype(FONT_PATH, 34)
font_meta = ImageFont.truetype(FONT_PATH, 24)

# 膠囊標籤 (黑金奢華米其林風)
badge_text = " 舌尖上的臺灣｜第 15 章 完結篇 "
bbox = font_badge.getbbox(badge_text)
bw, bh = bbox[2] - bbox[0] + 30, bbox[3] - bbox[1] + 16
bx, by = 60, 50
draw_yt.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(20, 20, 25, 230), outline=(212, 175, 55, 240), width=2)
draw_yt.text((bx + 15, by + 8), badge_text, fill=(245, 215, 110), font=font_badge)

# 右側金星標籤
star_badge = " ⭐⭐⭐ 全球首家三星臺灣料理 "
bbox_s = font_badge.getbbox(star_badge)
bws, bhs = bbox_s[2] - bbox_s[0] + 30, bbox_s[3] - bbox_s[1] + 16
bsx = 1280 - 60 - bws
draw_yt.rounded_rectangle([bsx, by, bsx + bws, by + bhs], radius=8, fill=(180, 83, 9, 230), outline=(254, 243, 199, 220), width=2)
draw_yt.text((bsx + 15, by + 8), star_badge, fill=(255, 255, 255), font=font_badge)

# 主標題
title_yt = "當代風土的米其林交響"
tx, ty = 60, 420
for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4)]:
    draw_yt.text((tx + ox, ty + oy), title_yt, fill=(0, 0, 0, 240), font=font_title)
draw_yt.text((tx, ty), title_yt, fill=(255, 253, 245), font=font_title)

# 副標題
sub_yt = "從路邊攤到世界殿堂・新臺菜世紀復興"
sx, sy = 60, 520
for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
    draw_yt.text((sx + ox, sy + oy), sub_yt, fill=(0, 0, 0, 220), font=font_sub)
draw_yt.text((sx, sy), sub_yt, fill=(252, 211, 77), font=font_sub)

# 底部元數據
meta_yt = "態芮 Taïrroir ✕ RAW ✕ 山海樓 ✕ 馬告刺蔥分子科學 ✕ 四百年大結語"
draw_yt.text((60, 590), meta_yt, fill=(203, 213, 225), font=font_meta)

yt_comp.convert("RGB").save(OUT_DIR1 / "food_ch15_youtube_thumbnail.jpg", quality=95)

print("4. 製作 1280x720 播客封面縮圖 (food_ch15_podcast_thumbnail.jpg)...")
# 使用工藝圖與主視覺做深色奢華融合
pod_bg = ImageOps.fit(craft_img, (1280, 720), method=Image.Resampling.LANCZOS).convert("RGBA")
ov_pod = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
d_pod = ImageDraw.Draw(ov_pod)

for y in range(720):
    a = int(min(240, 100 + (y / 720) * 140))
    d_pod.line([(0, y), (1280, y)], fill=(12, 10, 18, a))
for x in range(900):
    a = int((1.0 - (x / 900)) * 210)
    for y in range(720):
        orig = ov_pod.getpixel((x, y))
        d_pod.point((x, y), fill=(12, 10, 18, min(255, orig[3] + a)))

pod_comp = Image.alpha_composite(pod_bg, ov_pod)
draw_pod = ImageDraw.Draw(pod_comp)

# 膠囊標籤 (播客深金調)
badge_pod = " 🎙️ 深度文化播客｜全系列大收官 "
bbox_p = font_badge.getbbox(badge_pod)
bpw, bph = bbox_p[2] - bbox_p[0] + 30, bbox_p[3] - bbox_p[1] + 16
draw_pod.rounded_rectangle([60, 50, 60 + bpw, 50 + bph], radius=8, fill=(15, 23, 42, 235), outline=(212, 175, 55, 230), width=2)
draw_pod.text((75, 58), badge_pod, fill=(253, 224, 71), font=font_badge)

# 右上角標籤
right_pod = " 舌尖上的臺灣 完結篇 "
bbox_rp = font_badge.getbbox(right_pod)
brpw, brph = bbox_rp[2] - bbox_rp[0] + 30, bbox_rp[3] - bbox_rp[1] + 16
draw_pod.rounded_rectangle([1280 - 60 - brpw, 50, 1280 - 60, 50 + brph], radius=8, fill=(88, 28, 135, 220), outline=(233, 213, 255, 200), width=2)
draw_pod.text((1280 - 60 - brpw + 15, 58), right_pod, fill=(255, 255, 255), font=font_badge)

# 主標題
title_pod = "新臺菜與米其林三星"
tx, ty = 60, 420
for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4)]:
    draw_pod.text((tx + ox, ty + oy), title_pod, fill=(0, 0, 0, 240), font=font_title)
draw_pod.text((tx, ty), title_pod, fill=(255, 253, 245), font=font_title)

# 副標題
sub_pod = "態芮 Taïrroir・RAW・島嶼風土的自信交響"
sx, sy = 60, 520
for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
    draw_pod.text((sx + ox, sy + oy), sub_pod, fill=(0, 0, 0, 220), font=font_sub)
draw_pod.text((sx, sy), sub_pod, fill=(253, 224, 71), font=font_sub)

# 底部元數據
meta_pod = "雙人深度對談 ✕ 茶葉蛋鹹豆漿的法式重組 ✕ 四百年島嶼味覺全回顧"
draw_pod.text((60, 590), meta_pod, fill=(226, 232, 240), font=font_meta)

pod_comp.convert("RGB").save(OUT_DIR1 / "food_ch15_podcast_thumbnail.jpg", quality=95)

print("5. 同步所有 5 個檔案至 舌尖上的臺灣/assets/images/food_ch15/ ...")
for item in OUT_DIR1.glob("*.jpg"):
    shutil.copy2(item, OUT_DIR2 / item.name)
    print(f"  -> 已同步: {item.name}")

print("\n🎉 第 15 章全套視覺素材產製完成！")
