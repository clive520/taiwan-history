# -*- coding: utf-8 -*-
"""
生成《島嶼鐵道物語》第 07 章全套高畫質視覺素材與雙軌縮圖
1. rail_ch07_hero_banner.jpg (1920x1080)
2. rail_ch07_craft_scene.jpg (1920x1080)
3. rail_ch07_podcast_bg.jpg (1920x1080 嚴格無拉伸背景)
4. rail_ch07_youtube_thumbnail.jpg (1280x720 說明短片縮圖)
5. rail_ch07_podcast_thumbnail.jpg (1280x720 播客長片縮圖)
"""
import sys
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
OUT_DIR1 = BASE_DIR / "assets" / "images" / "rail_ch07"
OUT_DIR2 = BASE_DIR / "島嶼鐵道物語" / "assets" / "images" / "rail_ch07"

OUT_DIR1.mkdir(parents=True, exist_ok=True)
OUT_DIR2.mkdir(parents=True, exist_ok=True)

RAW_HERO = Path(sys.argv[1]) if len(sys.argv) > 1 else None
RAW_CRAFT = Path(sys.argv[2]) if len(sys.argv) > 2 else None
FONT_PATH = "C:/Windows/Fonts/msjhbd.ttc"

if not RAW_HERO or not RAW_HERO.exists() or not RAW_CRAFT or not RAW_CRAFT.exists():
    print("❌ 請傳入有效的 RAW_HERO 與 RAW_CRAFT 檔案路徑！")
    sys.exit(1)

print("1. 處理 1920x1080 主視覺與工藝圖 (嚴格 ImageOps.fit 無拉伸)...")
hero_img = Image.open(RAW_HERO).convert("RGB")
hero_1080 = ImageOps.fit(hero_img, (1920, 1080), method=Image.Resampling.LANCZOS)
hero_1080.save(OUT_DIR1 / "rail_ch07_hero_banner.jpg", quality=95)

craft_img = Image.open(RAW_CRAFT).convert("RGB")
craft_1080 = ImageOps.fit(craft_img, (1920, 1080), method=Image.Resampling.LANCZOS)
craft_1080.save(OUT_DIR1 / "rail_ch07_craft_scene.jpg", quality=95)

print("2. 製作 1920x1080 播客無拉伸底圖 (rail_ch07_podcast_bg.jpg)...")
bg_base = hero_1080.copy()
enh_c = ImageEnhance.Contrast(bg_base).enhance(1.08)
enh_b = ImageEnhance.Brightness(enh_c).enhance(0.88)

vignette = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
for y in range(1080):
    a = int(min(190, (y / 1080) ** 1.45 * 200))
    v_draw.line([(0, y), (1920, y)], fill=(10, 12, 18, a))
for x in range(320):
    a_x = int((1.0 - (x / 320)) * 145)
    for y in range(1080):
        c = vignette.getpixel((x, y))
        v_draw.point((x, y), fill=(10, 12, 18, min(255, c[3] + a_x)))
    for y in range(1080):
        rx = 1919 - x
        c = vignette.getpixel((rx, y))
        v_draw.point((rx, y), fill=(10, 12, 18, min(255, c[3] + a_x)))

bg_final = Image.alpha_composite(enh_b.convert("RGBA"), vignette).convert("RGB")
bg_final.save(OUT_DIR1 / "rail_ch07_podcast_bg.jpg", quality=95)

print("3. 製作 1280x720 說明短片封面縮圖 (rail_ch07_youtube_thumbnail.jpg)...")
yt_bg = ImageOps.fit(hero_img, (1280, 720), method=Image.Resampling.LANCZOS).convert("RGBA")
ov_yt = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
d_ov = ImageDraw.Draw(ov_yt)

for y in range(720):
    if y > 220:
        a = int(((y - 220) / 500) ** 1.2 * 235)
        d_ov.line([(0, y), (1280, y)], fill=(8, 12, 22, a))
for x in range(850):
    a = int((1.0 - (x / 850)) * 195)
    for y in range(720):
        orig = ov_yt.getpixel((x, y))
        d_ov.point((x, y), fill=(8, 12, 22, min(255, orig[3] + a)))

yt_comp = Image.alpha_composite(yt_bg, ov_yt)
draw_yt = ImageDraw.Draw(yt_comp)

font_badge = ImageFont.truetype(FONT_PATH, 28)
font_title = ImageFont.truetype(FONT_PATH, 64)
font_sub = ImageFont.truetype(FONT_PATH, 34)
font_meta = ImageFont.truetype(FONT_PATH, 24)

badge_text = " 島嶼鐵道物語｜第 07 章 "
bbox = font_badge.getbbox(badge_text)
bw, bh = bbox[2] - bbox[0] + 32, bbox[3] - bbox[1] + 22
bx, by = 60, 50
draw_yt.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(15, 23, 42, 235), outline=(56, 189, 248, 240), width=2)
draw_yt.text((bx + 16, by + 6), badge_text, fill=(224, 242, 254), font=font_badge)

tech_badge = " 地底千米 × 石底大斜坑 "
bbox_s = font_badge.getbbox(tech_badge)
bws, bhs = bbox_s[2] - bbox_s[0] + 32, bbox_s[3] - bbox_s[1] + 22
bsx = 1280 - 60 - bws
draw_yt.rounded_rectangle([bsx, by, bsx + bws, by + bhs], radius=8, fill=(14, 116, 144, 230), outline=(224, 242, 254, 220), width=2)
draw_yt.text((bsx + 16, by + 6), tech_badge, fill=(255, 255, 255), font=font_badge)

title_main = "黑金深處的礦坑呼嘯"
draw_yt.text((62, 434), title_main, fill=(0, 0, 0, 210), font=font_title, stroke_width=6, stroke_fill=(0, 0, 0, 220))
draw_yt.text((60, 430), title_main, fill=(255, 255, 255), font=font_title, stroke_width=2, stroke_fill=(15, 23, 42))

sub_main = "平溪支線、石底大斜坑與基隆河煤鐵哀歌"
draw_yt.text((62, 524), sub_main, fill=(125, 211, 252), font=font_sub, stroke_width=3, stroke_fill=(0, 0, 0, 200))

meta_main = "顏雲年臺陽鐵道 × 橫跨十分瀑布鋼橋 × 40°C井下血淚 × 祈福天燈重生"
draw_yt.text((62, 588), meta_main, fill=(226, 232, 240), font=font_meta)

yt_comp.convert("RGB").save(OUT_DIR1 / "rail_ch07_youtube_thumbnail.jpg", quality=95)

print("4. 製作 1280x720 播客深度對談縮圖 (rail_ch07_podcast_thumbnail.jpg)...")
pod_bg = ImageOps.fit(craft_img, (1280, 720), method=Image.Resampling.LANCZOS).convert("RGBA")
ov_pod = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
d_pod = ImageDraw.Draw(ov_pod)

for y in range(720):
    if y > 200:
        a = int(((y - 200) / 520) ** 1.15 * 240)
        d_pod.line([(0, y), (1280, y)], fill=(10, 14, 24, a))
for x in range(880):
    a = int((1.0 - (x / 880)) * 205)
    for y in range(720):
        orig = ov_pod.getpixel((x, y))
        d_pod.point((x, y), fill=(10, 14, 24, min(255, orig[3] + a)))

pod_comp = Image.alpha_composite(pod_bg, ov_pod)
draw_pod = ImageDraw.Draw(pod_comp)

pod_badge = " 深度鐵道史學播客｜第 07 集 "
bbox_p = font_badge.getbbox(pod_badge)
bwp, bhp = bbox_p[2] - bbox_p[0] + 32, bbox_p[3] - bbox_p[1] + 22
draw_pod.rounded_rectangle([bx, by, bx + bwp, by + bhp], radius=8, fill=(15, 23, 42, 235), outline=(56, 189, 248, 240), width=2)
draw_pod.text((bx + 16, by + 6), pod_badge, fill=(224, 242, 254), font=font_badge)

pod_right = " 1918–1986 × 臺灣煤炭之王 "
bbox_pr = font_badge.getbbox(pod_right)
bwpr, bhpr = bbox_pr[2] - bbox_pr[0] + 32, bbox_pr[3] - bbox_pr[1] + 22
bprx = 1280 - 60 - bwpr
draw_pod.rounded_rectangle([bprx, by, bprx + bwpr, by + bhpr], radius=8, fill=(14, 116, 144, 230), outline=(224, 242, 254, 220), width=2)
draw_pod.text((bprx + 16, by + 6), pod_right, fill=(255, 255, 255), font=font_badge)

pod_title = "黑金、大斜坑與矽肺哀歌"
draw_pod.text((62, 434), pod_title, fill=(0, 0, 0, 210), font=font_title, stroke_width=6, stroke_fill=(0, 0, 0, 220))
draw_pod.text((60, 430), pod_title, fill=(255, 255, 255), font=font_title, stroke_width=2, stroke_fill=(15, 23, 42))

pod_sub = "平溪線百年地底戰史與天燈下的礦工血淚"
draw_pod.text((62, 524), pod_sub, fill=(125, 211, 252), font=font_sub, stroke_width=3, stroke_fill=(0, 0, 0, 200))

pod_meta = "雙人深度對談 × 15度傾角千米深坑 × 菁桐洗選降煤櫃 × 入坑九死一生"
draw_pod.text((62, 588), pod_meta, fill=(226, 232, 240), font=font_meta)

pod_comp.convert("RGB").save(OUT_DIR1 / "rail_ch07_podcast_thumbnail.jpg", quality=95)

print("5. 同步複製 5 大圖檔至 島嶼鐵道物語/assets/images/rail_ch07/ ...")
for f in OUT_DIR1.glob("*.jpg"):
    shutil.copy2(f, OUT_DIR2 / f.name)
    print(f"   ✅ {f.name}")

print("🎉 第 07 章 5 大高畫質視覺資產產製完成！")
