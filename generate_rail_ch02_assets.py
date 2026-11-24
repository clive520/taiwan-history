# -*- coding: utf-8 -*-
"""
生成《島嶼鐵道物語》第 02 章全套高畫質視覺素材與雙軌縮圖
1. rail_ch02_hero_banner.jpg (1920x1080)
2. rail_ch02_craft_scene.jpg (1920x1080)
3. rail_ch02_podcast_bg.jpg (1920x1080 嚴格無拉伸背景)
4. rail_ch02_youtube_thumbnail.jpg (1280x720 說明短片縮圖)
5. rail_ch02_podcast_thumbnail.jpg (1280x720 播客長片縮圖)
"""
import sys
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
OUT_DIR1 = BASE_DIR / "assets" / "images" / "rail_ch02"
OUT_DIR2 = BASE_DIR / "島嶼鐵道物語" / "assets" / "images" / "rail_ch02"

OUT_DIR1.mkdir(parents=True, exist_ok=True)
OUT_DIR2.mkdir(parents=True, exist_ok=True)

RAW_HERO = Path(r"C:\Users\admin\.gemini\antigravity\brain\e6ad31e6-5e47-44d3-86ec-3061599c52d4\yutengping_bridge_1908_oil_painting_1795559420692.jpg")
RAW_CRAFT = Path(r"C:\Users\admin\.gemini\antigravity\brain\e6ad31e6-5e47-44d3-86ec-3061599c52d4\daan_river_bridge_1908_v2_1795559524844.jpg")
FONT_PATH = "C:/Windows/Fonts/msjhbd.ttc"

print("1. 處理 1920x1080 主視覺與工程圖 (嚴格 ImageOps.fit 無拉伸)...")
hero_img = Image.open(RAW_HERO).convert("RGB")
hero_1080 = ImageOps.fit(hero_img, (1920, 1080), method=Image.Resampling.LANCZOS)
hero_1080.save(OUT_DIR1 / "rail_ch02_hero_banner.jpg", quality=95)

craft_img = Image.open(RAW_CRAFT).convert("RGB")
craft_1080 = ImageOps.fit(craft_img, (1920, 1080), method=Image.Resampling.LANCZOS)
craft_1080.save(OUT_DIR1 / "rail_ch02_craft_scene.jpg", quality=95)

print("2. 製作 1920x1080 播客無拉伸底圖 (rail_ch02_podcast_bg.jpg)...")
bg_base = hero_1080.copy()
enh_c = ImageEnhance.Contrast(bg_base).enhance(1.08)
enh_b = ImageEnhance.Brightness(enh_c).enhance(0.90)

vignette = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
for y in range(1080):
    a = int(min(185, (y / 1080) ** 1.45 * 195))
    v_draw.line([(0, y), (1920, y)], fill=(8, 10, 20, a))
for x in range(300):
    a_x = int((1.0 - (x / 300)) * 140)
    for y in range(1080):
        c = vignette.getpixel((x, y))
        v_draw.point((x, y), fill=(8, 10, 20, min(255, c[3] + a_x)))
    for y in range(1080):
        rx = 1919 - x
        c = vignette.getpixel((rx, y))
        v_draw.point((rx, y), fill=(8, 10, 20, min(255, c[3] + a_x)))

bg_final = Image.alpha_composite(enh_b.convert("RGBA"), vignette).convert("RGB")
bg_final.save(OUT_DIR1 / "rail_ch02_podcast_bg.jpg", quality=95)

print("3. 製作 1280x720 說明短片封面縮圖 (rail_ch02_youtube_thumbnail.jpg)...")
yt_bg = ImageOps.fit(hero_img, (1280, 720), method=Image.Resampling.LANCZOS).convert("RGBA")
ov_yt = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
d_ov = ImageDraw.Draw(ov_yt)

for y in range(720):
    if y > 220:
        a = int(((y - 220) / 500) ** 1.2 * 235)
        d_ov.line([(0, y), (1280, y)], fill=(8, 12, 28, a))
for x in range(850):
    a = int((1.0 - (x / 850)) * 195)
    for y in range(720):
        orig = ov_yt.getpixel((x, y))
        d_ov.point((x, y), fill=(8, 12, 28, min(255, orig[3] + a)))

yt_comp = Image.alpha_composite(yt_bg, ov_yt)
draw_yt = ImageDraw.Draw(yt_comp)

font_badge = ImageFont.truetype(FONT_PATH, 28)
font_title = ImageFont.truetype(FONT_PATH, 64)
font_sub = ImageFont.truetype(FONT_PATH, 34)
font_meta = ImageFont.truetype(FONT_PATH, 24)

badge_text = " 島嶼鐵道物語｜第 02 章 "
bbox = font_badge.getbbox(badge_text)
bw, bh = bbox[2] - bbox[0] + 32, bbox[3] - bbox[1] + 22
bx, by = 60, 50
draw_yt.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(15, 23, 42, 235), outline=(99, 102, 241, 240), width=2)
draw_yt.text((bx + 16, by + 6), badge_text, fill=(199, 210, 254), font=font_badge)

tech_badge = " 1908 縱貫線 404km 全通 "
bbox_s = font_badge.getbbox(tech_badge)
bws, bhs = bbox_s[2] - bbox_s[0] + 32, bbox_s[3] - bbox_s[1] + 22
bsx = 1280 - 60 - bws
draw_yt.rounded_rectangle([bsx, by, bsx + bws, by + bhs], radius=8, fill=(67, 56, 202, 230), outline=(224, 231, 255, 220), width=2)
draw_yt.text((bsx + 16, by + 6), tech_badge, fill=(255, 255, 255), font=font_badge)

title_yt = "南北貫通的一日革命"
tx, ty = 60, 420
for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4)]:
    draw_yt.text((tx + ox, ty + oy), title_yt, fill=(0, 0, 0, 240), font=font_title)
draw_yt.text((tx, ty), title_yt, fill=(255, 255, 255), font=font_title)

sub_yt = "長谷川謹介、魚藤坪斷橋力學與舊山線奇蹟"
sx, sy = 60, 520
for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
    draw_yt.text((sx + ox, sy + oy), sub_yt, fill=(0, 0, 0, 220), font=font_sub)
draw_yt.text((sx, sy), sub_yt, fill=(253, 224, 71), font=font_sub)

meta_yt = "速成延長主義 × 糯米三合土磚拱 × 大安溪蛇籠治水 × 14小時一日生活圈"
draw_yt.text((60, 590), meta_yt, fill=(203, 213, 225), font=font_meta)

yt_comp.convert("RGB").save(OUT_DIR1 / "rail_ch02_youtube_thumbnail.jpg", quality=95)

print("4. 製作 1280x720 播客封面縮圖 (rail_ch02_podcast_thumbnail.jpg)...")
pod_bg = ImageOps.fit(craft_img, (1280, 720), method=Image.Resampling.LANCZOS).convert("RGBA")
ov_pod = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
d_pod = ImageDraw.Draw(ov_pod)

for y in range(720):
    a = int(min(240, 100 + (y / 720) * 140))
    d_pod.line([(0, y), (1280, y)], fill=(10, 14, 26, a))
for x in range(900):
    a = int((1.0 - (x / 900)) * 210)
    for y in range(720):
        orig = ov_pod.getpixel((x, y))
        d_pod.point((x, y), fill=(10, 14, 26, min(255, orig[3] + a)))

pod_comp = Image.alpha_composite(pod_bg, ov_pod)
draw_pod = ImageDraw.Draw(pod_comp)

badge_pod = " 深度鐵道史學播客｜第 02 集 "
bbox_p = font_badge.getbbox(badge_pod)
bpw, bph = bbox_p[2] - bbox_p[0] + 32, bbox_p[3] - bbox_p[1] + 22
draw_pod.rounded_rectangle([60, 50, 60 + bpw, 50 + bph], radius=8, fill=(15, 23, 42, 235), outline=(129, 140, 248, 230), width=2)
draw_pod.text((76, 56), badge_pod, fill=(224, 231, 255), font=font_badge)

right_pod = " 半月苦旅 → 14小時革命 "
bbox_rp = font_badge.getbbox(right_pod)
brpw, brph = bbox_rp[2] - bbox_rp[0] + 32, bbox_rp[3] - bbox_rp[1] + 22
draw_pod.rounded_rectangle([1280 - 60 - brpw, 50, 1280 - 60, 50 + brph], radius=8, fill=(49, 46, 129, 220), outline=(199, 210, 254, 200), width=2)
draw_pod.text((1280 - 60 - brpw + 16, 56), right_pod, fill=(255, 255, 255), font=font_badge)

title_pod = "焊鑄島嶼脊骨的縱貫奇蹟"
tx, ty = 60, 420
for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (-4, 0), (0, -4)]:
    draw_pod.text((tx + ox, ty + oy), title_pod, fill=(0, 0, 0, 240), font=font_title)
draw_pod.text((tx, ty), title_pod, fill=(255, 255, 255), font=font_title)

sub_pod = "后里斷崖、伯公坑索道與 1908 湖心亭全通式"
sx, sy = 60, 520
for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
    draw_pod.text((sx + ox, sy + oy), sub_pod, fill=(0, 0, 0, 220), font=font_sub)
draw_pod.text((sx, sy), sub_pod, fill=(253, 224, 71), font=font_sub)

meta_pod = "雙人深度對談 × 速成延長主義真相 × 龍騰斷橋抗震秘密 × 全島共同體誕生"
draw_pod.text((60, 590), meta_pod, fill=(203, 213, 225), font=font_meta)

pod_comp.convert("RGB").save(OUT_DIR1 / "rail_ch02_podcast_thumbnail.jpg", quality=95)

print("5. 同步所有檔案至 島嶼鐵道物語/assets/images/rail_ch02/ ...")
for item in OUT_DIR1.glob("*.jpg"):
    shutil.copy2(item, OUT_DIR2 / item.name)
    print(f"  -> 已同步: {item.name}")

print("\n🎉 第 02 章全套視覺素材產製完成！")
