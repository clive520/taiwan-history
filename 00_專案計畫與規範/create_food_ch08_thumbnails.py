# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 08 章 歷史主視覺、農藝工藝圖與雙軌縮圖合成腳本
- 英雄主視覺 (1920x1080)：陽明山竹子湖火山梯田、山嵐晨霧與磯永吉農學場景
- 育種工藝特寫圖 (1920x1080)：水稻穗花、顯微鏡育種手繪、金黃稻浪與白玉蓬萊米
- 說明短片縮圖 (1280x720)：大稻金黃與翠綠山嵐微霧風格，高對比大字排版
- 播客深度對談縮圖 (1280x720)：沉穩深藍琥珀金知性風格
"""
import sys
import os
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH08_ASSETS = BASE_DIR / "assets" / "images" / "food_ch08"
CH08_MIRROR = BASE_DIR / "舌尖上的臺灣" / "assets" / "images" / "ch08"
TEMP_DIR = BASE_DIR / "temp_art_ch08"

CH08_ASSETS.mkdir(parents=True, exist_ok=True)
CH08_MIRROR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "terraces": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=1920&q=80",
    "golden_rice": "https://images.unsplash.com/photo-1536657464919-892534f60d6e?w=1920&q=80",
    "lab_botany": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=1920&q=80",
    "white_grains": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=1920&q=80"
}

def download_sources():
    print("📥 正在下載高解析度自然地景與農藝素材...")
    for key, url in SOURCES.items():
        dst = TEMP_DIR / f"{key}.jpg"
        if not dst.exists() or dst.stat().st_size == 0:
            print(f"  下載 {key}...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as resp, open(dst, 'wb') as f:
                f.write(resp.read())
            print(f"  ✅ {key} 下載成功！({dst.stat().st_size / 1024:.1f} KB)")

def apply_rembrandt_style(im, warm_tint=(255, 220, 160), intensity=0.30, vignette_strength=0.65):
    im = im.convert("RGB")
    im = ImageEnhance.Contrast(im).enhance(1.20)
    im = ImageEnhance.Color(im).enhance(1.15)
    
    tint_layer = Image.new("RGB", im.size, warm_tint)
    im = Image.blend(im, tint_layer, intensity)
    
    w, h = im.size
    vignette = Image.new("L", (w, h), 0)
    v_draw = ImageDraw.Draw(vignette)
    max_radius = int(((w/2)**2 + (h/2)**2)**0.5)
    for r in range(max_radius, 0, -15):
        alpha = int(255 * (1 - (r / max_radius)**2 * vignette_strength))
        alpha = max(0, min(255, alpha))
        v_draw.ellipse([w/2 - r, h/2 - r, w/2 + r, h/2 + r], fill=alpha)
    
    black_layer = Image.new("RGB", (w, h), (10, 15, 8))
    im = Image.composite(im, black_layer, vignette)
    return im

def build_hero_banner():
    print("🎨 正在合成 Hero Banner (1920x1080)...")
    im_terraces = Image.open(TEMP_DIR / "terraces.jpg").convert("RGB").resize((1920, 1080), Image.Resampling.LANCZOS)
    im_rice = Image.open(TEMP_DIR / "golden_rice.jpg").convert("RGB").resize((1920, 1080), Image.Resampling.LANCZOS)
    
    # 水平漸層融合：左側竹子湖梯田群山晨霧，右側金色稻穗麥芒
    mask = Image.new("L", (1920, 1080), 0)
    m_draw = ImageDraw.Draw(mask)
    for x in range(1920):
        # 400 到 1500 漸變
        if x < 400:
            val = 0
        elif x > 1500:
            val = 255
        else:
            val = int(255 * ((x - 400) / 1100))
        m_draw.line([(x, 0), (x, 1080)], fill=val)
        
    blended = Image.composite(im_rice, im_terraces, mask)
    hero = apply_rembrandt_style(blended, warm_tint=(250, 225, 170), intensity=0.25, vignette_strength=0.60)
    
    out_path = CH08_ASSETS / "food_ch08_hero_banner.jpg"
    hero.save(out_path, quality=95)
    hero.save(CH08_MIRROR / "food_ch08_hero_banner.jpg", quality=95)
    print(f"✅ Hero Banner 合成完成：{out_path.name}")
    return hero

def build_craft_image():
    print("🎨 正在合成農藝育種工藝特寫圖 (1920x1080)...")
    im_rice = Image.open(TEMP_DIR / "golden_rice.jpg").convert("RGB").resize((1920, 1080), Image.Resampling.LANCZOS)
    im_grains = Image.open(TEMP_DIR / "white_grains.jpg").convert("RGB").resize((1920, 1080), Image.Resampling.LANCZOS)
    
    # 斜角對稱融合：左上方金黃未脫粒稻穗，右下方晶瑩剔透白玉米粒
    mask = Image.new("L", (1920, 1080), 0)
    m_draw = ImageDraw.Draw(mask)
    for x in range(1920):
        for y in range(0, 1080, 20):
            diag = (x * 0.7 + y * 0.3)
            val = max(0, min(255, int((diag - 500) / 900 * 255)))
            m_draw.rectangle([x, y, x+1, y+20], fill=val)
            
    mask = mask.filter(ImageFilter.GaussianBlur(radius=30))
    blended = Image.composite(im_grains, im_rice, mask)
    craft = apply_rembrandt_style(blended, warm_tint=(255, 230, 180), intensity=0.28, vignette_strength=0.70)
    
    out_path = CH08_ASSETS / "food_ch08_rice_craft.jpg"
    craft.save(out_path, quality=95)
    craft.save(CH08_MIRROR / "food_ch08_rice_craft.jpg", quality=95)
    print(f"✅ 農藝工藝圖合成完成：{out_path.name}")
    return craft

def get_font(size, bold=True):
    font_names = [
        "msjhbd.ttc", "msjh.ttc", "mingliub.ttc", "simhei.ttf", "arialbd.ttf"
    ]
    windir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    for name in font_names:
        p = windir / name
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_text_with_halo(draw, xy, text, font, fill, halo_fill=(0, 0, 0), halo_radius=4):
    x, y = xy
    for dx in range(-halo_radius, halo_radius + 1):
        for dy in range(-halo_radius, halo_radius + 1):
            if dx * dx + dy * dy <= halo_radius * halo_radius:
                draw.text((x + dx, y + dy), text, font=font, fill=halo_fill)
    draw.text((x, y), text, font=font, fill=fill)

def build_youtube_thumbnail(hero_img):
    print("🎨 正在產製說明短片縮圖 (1280x720)...")
    base = hero_img.copy().resize((1280, 720), Image.Resampling.LANCZOS)
    
    # 底部暗部襯托，保證文字極度清晰
    overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    o_draw = ImageDraw.Draw(overlay)
    for y in range(300, 720):
        alpha = int(220 * ((y - 300) / 420) ** 1.3)
        o_draw.line([(0, y), (1280, y)], fill=(12, 18, 10, alpha))
        
    base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(base)
    
    font_tag = get_font(34, bold=True)
    font_main = get_font(72, bold=True)
    font_sub = get_font(38, bold=True)
    
    # 標籤
    draw_text_with_halo(draw, (70, 390), "【舌尖上的臺灣 EP08】", font_tag, fill="#7CFF88", halo_fill=(0, 0, 0), halo_radius=4)
    # 主標題
    draw_text_with_halo(draw, (70, 450), "蓬萊米誕生記！", font_main, fill="#FFF6A8", halo_fill=(15, 20, 5), halo_radius=6)
    # 副標題
    draw_text_with_halo(draw, (72, 555), "竹子湖原種田與翻轉東亞餐桌的米食革命", font_sub, fill="#FFFFFF", halo_fill=(0, 0, 0), halo_radius=5)
    
    # 右下角裝飾標籤
    draw_text_with_halo(draw, (72, 625), "磯永吉 ✕ 末永仁 ✕ 臺中65號 ✕ 嘉南大圳", get_font(28, bold=True), fill="#5CE1E6", halo_fill=(0, 0, 0), halo_radius=3)
    
    out_path = CH08_ASSETS / "food_ch08_youtube_thumbnail.jpg"
    base.save(out_path, quality=95)
    base.save(CH08_MIRROR / "food_ch08_youtube_thumbnail.jpg", quality=95)
    base.save(CH08_MIRROR / "ch08_youtube_thumbnail.jpg", quality=95)
    print(f"✅ 說明短片縮圖完成：{out_path.name}")

def build_podcast_thumbnail(craft_img):
    print("🎨 正在產製播客深度對談縮圖 (1280x720)...")
    base = craft_img.copy().resize((1280, 720), Image.Resampling.LANCZOS)
    
    # 深藍暖金知性濾鏡
    blue_tint = Image.new("RGB", (1280, 720), (10, 25, 45))
    base = Image.blend(base, blue_tint, 0.40)
    
    overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    o_draw = ImageDraw.Draw(overlay)
    for y in range(280, 720):
        alpha = int(235 * ((y - 280) / 440) ** 1.2)
        o_draw.line([(0, y), (1280, y)], fill=(6, 12, 24, alpha))
        
    base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(base)
    
    font_tag = get_font(32, bold=True)
    font_main = get_font(68, bold=True)
    font_sub = get_font(36, bold=True)
    
    draw_text_with_halo(draw, (70, 390), "🎙️ 深度對談・第 08 章", font_tag, fill="#64D2FF", halo_fill=(0, 0, 0), halo_radius=4)
    draw_text_with_halo(draw, (70, 450), "綠色奇蹟與白米悲歌", font_main, fill="#FFE680", halo_fill=(5, 10, 25), halo_radius=6)
    draw_text_with_halo(draw, (72, 550), "磯永吉小屋、臺中65號雜交與吃番薯籤的農民", font_sub, fill="#FFFFFF", halo_fill=(0, 0, 0), halo_radius=5)
    draw_text_with_halo(draw, (72, 620), "直鏈澱粉跳水 ✕ 幼苗插秧法 ✕ 米糖相剋政治經濟學", get_font(26, bold=True), fill="#B4E5A2", halo_fill=(0, 0, 0), halo_radius=3)
    
    out_path = CH08_ASSETS / "food_ch08_podcast_thumbnail.jpg"
    base.save(out_path, quality=95)
    base.save(CH08_MIRROR / "food_ch08_podcast_thumbnail.jpg", quality=95)
    base.save(CH08_MIRROR / "ch08_podcast_thumbnail.jpg", quality=95)
    print(f"✅ 播客對談縮圖完成：{out_path.name}")

def main():
    download_sources()
    hero = build_hero_banner()
    craft = build_craft_image()
    build_youtube_thumbnail(hero)
    build_podcast_thumbnail(craft)
    print("\n🎉 第 08 章所有歷史主視覺與 1280x720 雙軌縮圖產製圓滿完成！")

if __name__ == "__main__":
    main()
