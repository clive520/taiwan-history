# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 10 章 Podcast 封面縮圖重製、影片壓製與 YouTube 縮圖即時更新腳本
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageOps

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
ASSETS_DIR = BASE_DIR / "assets" / "images" / "food_ch10"
MIRROR_DIR = BASE_DIR / "舌尖上的臺灣" / "assets" / "images" / "ch10"
VIDEO_DIR = BASE_DIR / "舌尖上的臺灣" / "03_帝國之眼與東洋滋味"
AI_MASTER = ASSETS_DIR / "food_ch10_oriental_beauty_ai_master.jpg"

PODCAST_THUMB_MAIN = ASSETS_DIR / "food_ch10_podcast_thumbnail.jpg"
AUDIO_FILE = VIDEO_DIR / "food_ch10_podcast_deepdive.m4a"
VIDEO_OUTPUT = VIDEO_DIR / "第10章_山嵐間的東方美人_播客深度對談.mp4"
VIDEO_ID = "rlhbgn4T1z8"

def generate_podcast_thumbnail():
    print("🎨 正在生成無變形 16:9 高畫質 Podcast 封面背景圖...")
    img = Image.open(AI_MASTER).convert('RGB')
    
    # 嚴格 16:9 等比裁切填滿 (1280x720)
    fitted = ImageOps.fit(img, (1280, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    
    # 色彩微調
    enhancer = ImageEnhance.Color(fitted)
    fitted = enhancer.enhance(1.06)
    enhancer = ImageEnhance.Contrast(fitted)
    fitted = enhancer.enhance(1.08)
    
    # 左側深色漸層遮罩
    overlay = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw_ol = ImageDraw.Draw(overlay)
    for x in range(0, 960):
        factor = 1 - (x / 960)**1.3
        alpha = int(245 * max(0, factor))
        draw_ol.rectangle([x, 0, x+1, 720], fill=(12, 10, 8, alpha))
        
    fitted.paste(Image.alpha_composite(Image.new('RGBA', (1280, 720), (0, 0, 0, 0)), overlay), (0, 0), overlay)
    
    font_bold = 'C:/Windows/Fonts/msjhbd.ttc'
    f_tag = ImageFont.truetype(font_bold, 26)
    f_title = ImageFont.truetype(font_bold, 64)
    f_sub = ImageFont.truetype(font_bold, 30)
    f_bullet_icon = ImageFont.truetype(font_bold, 22)
    f_extra = ImageFont.truetype(font_bold, 25)
    f_badge = ImageFont.truetype(font_bold, 24)
    
    draw = ImageDraw.Draw(fitted)
    
    def draw_text_with_shadow(xy, text, font, fill, shadow_fill=(5, 4, 3), offset=(2, 2)):
        x, y = xy
        draw.text((x + offset[0], y + offset[1]), text, font=font, fill=shadow_fill)
        draw.text((x, y), text, font=font, fill=fill)
        
    # 1. 頂部系列標籤
    draw.rounded_rectangle([60, 52, 540, 106], radius=10, fill=(150, 75, 20), outline=(225, 160, 80), width=2)
    draw_text_with_shadow((82, 63), '【舌尖上的臺灣 深度播客】', f_tag, (255, 255, 255))
    
    # 2. 主標題
    draw_text_with_shadow((60, 130), '山嵐間的', f_title, (255, 250, 240), offset=(3, 3))
    draw_text_with_shadow((60, 212), '東方美人', f_title, (255, 205, 65), offset=(3, 3))
    
    # 3. 副標題欄
    draw.rounded_rectangle([60, 312, 690, 372], radius=8, fill=(28, 22, 18, 230), outline=(190, 140, 60), width=2)
    draw_text_with_shadow((80, 324), '大稻埕茶金歲月與膨風茶傳奇', f_sub, (255, 225, 140))
    
    # 4. 重點條目 (使用琥珀金菱形 bullet + 象牙白字體)
    bullets = [
        '小綠葉蟬刺吸與茶樹分子自衛武器',
        '陶德與李春生：寶順洋行與茶底銀信貸',
        '萬名大稻埕揀茶女工與近代女性受薪',
        '新竹州特等獎一斤換數棟房的膨風神話'
    ]
    y_start = 405
    for i, b in enumerate(bullets):
        y = y_start + i * 50
        draw_text_with_shadow((65, y+1), '◆', f_bullet_icon, (255, 195, 60), offset=(2, 2))
        draw_text_with_shadow((95, y), b, f_extra, (245, 245, 245), offset=(2, 2))
        
    # 5. 左下方 PODCAST 規格標籤 (避開 YouTube 右下角時間戳)
    draw.rounded_rectangle([60, 620, 390, 672], radius=8, fill=(175, 55, 20), outline=(235, 120, 70), width=2)
    draw_text_with_shadow((80, 631), 'PODCAST 雙人深度對談', f_badge, (255, 255, 255))
    
    # 儲存主要縮圖
    fitted.save(str(PODCAST_THUMB_MAIN), quality=95)
    print(f"✅ 已輸出主要縮圖：{PODCAST_THUMB_MAIN}")
    
    # 同步鏡像至 舌尖上的臺灣/assets/images/ch10/
    MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PODCAST_THUMB_MAIN, MIRROR_DIR / "food_ch10_podcast_thumbnail.jpg")
    shutil.copy2(PODCAST_THUMB_MAIN, MIRROR_DIR / "ch10_podcast_thumbnail.jpg")
    shutil.copy2(AI_MASTER, MIRROR_DIR / "food_ch10_oriental_beauty_ai_master.jpg")
    print(f"✅ 已同步鏡像至：{MIRROR_DIR}")

def render_podcast_video():
    print(f"\n🎬 正在使用 FFmpeg 重新壓製 Podcast 1080p 影片...")
    cmd = [
        "ffmpeg", "-loop", "1",
        "-i", str(PODCAST_THUMB_MAIN),
        "-i", str(AUDIO_FILE),
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        "-shortest", "-y",
        str(VIDEO_OUTPUT)
    ]
    print(f"[EXEC] {' '.join(cmd)}")
    ret = subprocess.run(cmd, check=True)
    if ret.returncode == 0:
        print(f"✅ Podcast 影片壓製完成：{VIDEO_OUTPUT} (檔案大小: {VIDEO_OUTPUT.stat().st_size / (1024*1024):.2f} MB)")
    else:
        print("❌ FFmpeg 壓製失敗")
        sys.exit(1)

def update_youtube_thumbnail():
    print(f"\n🌐 正在透過 YouTube API 更新線上影片 (ID: {VIDEO_ID}) 自訂封面縮圖...")
    uploader_path = BASE_DIR / "00_專案計畫與規範" / "youtube_api_uploader.py"
    sys.path.insert(0, str(uploader_path.parent))
    from youtube_api_uploader import get_authenticated_service
    from googleapiclient.http import MediaFileUpload
    
    youtube = get_authenticated_service()
    if not youtube:
        print("❌ 無法取得 YouTube API 驗證客戶端")
        return False
        
    try:
        request = youtube.thumbnails().set(
            videoId=VIDEO_ID,
            media_body=MediaFileUpload(str(PODCAST_THUMB_MAIN), mimetype="image/jpeg")
        )
        response = request.execute()
        print(f"🎉 成功更新 YouTube 縮圖！Response: {response}")
        return True
    except Exception as e:
        print(f"❌ YouTube 縮圖更新異常：{e}")
        return False

if __name__ == "__main__":
    generate_podcast_thumbnail()
    render_podcast_video()
    update_youtube_thumbnail()
    print("\n✨ 全部重製與發布更新流程圓滿完成！")
