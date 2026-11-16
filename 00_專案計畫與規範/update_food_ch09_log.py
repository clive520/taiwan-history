import re
import sys

def update_chapter09_log(video_id, podcast_id, video_duration="8m30s", podcast_duration="14m15s", video_sub_lines=260, podcast_sub_lines=380):
    total_subs = video_sub_lines + podcast_sub_lines
    
    # 1. 更新 js/data-food.js
    path_data_food = "js/data-food.js"
    with open(path_data_food, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern_ch09 = r'("id":\s*"ch09",[\s\S]*?"status":\s*)"planned"'
    replacement_ch09 = rf'\1"published",\n      "videoId": "{video_id}",\n      "podcastId": "{podcast_id}"'
    new_content = re.sub(pattern_ch09, replacement_ch09, content)
    with open(path_data_food, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ js/data-food.js updated successfully!")
    
    # 2. 更新 舌尖上的臺灣/js/data.js
    path_data_tw = "舌尖上的臺灣/js/data.js"
    with open(path_data_tw, 'r', encoding='utf-8') as f:
        content_tw = f.read()
    new_content_tw = re.sub(pattern_ch09, replacement_ch09, content_tw)
    with open(path_data_tw, 'w', encoding='utf-8') as f:
        f.write(new_content_tw)
    print("✅ 舌尖上的臺灣/js/data.js updated successfully!")

    # 3. 更新長文專論中的 placeholder
    path_doc = "舌尖上的臺灣/03_帝國之眼與東洋滋味/第09章_汽笛聲中的木片便當_縱貫鐵路通車生啤酒喫茶店與鐵路便當的摩登生活.md"
    with open(path_doc, 'r', encoding='utf-8') as f:
        doc_content = f.read()
    doc_content = doc_content.replace("placeholder_food_ch09_video", video_id)
    doc_content = doc_content.replace("placeholder_food_ch09_podcast", podcast_id)
    with open(path_doc, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    print("✅ 深度專論 YouTube Video ID updated successfully!")

    # 4. 更新 舌尖上的臺灣/工作日誌.md
    path_log = "舌尖上的臺灣/工作日誌.md"
    with open(path_log, 'r', encoding='utf-8') as f:
        log_content = f.read()

    # 更新儀表板進度 53.3% ➔ 60.0%
    log_content = re.sub(r'已完成\s*\*\*8\s*/\s*15\s*章\*\*\s*（\*\*53\.3%\*\*）', '已完成 **9 / 15 章**（**60.0%**）', log_content)
    log_content = re.sub(r'進度條：\s*`\[██████████░░░░░░░░░\]`\s*53\.3%', '進度條： `[████████████░░░░░░░░]` 60.0%', log_content)
    log_content = re.sub(r'\| 進行中 / 待啟動 \| 7 章 \| 46\.7% \|', '| 進行中 / 待啟動 | 6 章 | 40.0% |', log_content)
    log_content = re.sub(r'\| 已發布 / 已完工 \| 8 章 \| 53\.3% \|', '| 已發布 / 已完工 | 9 章 | 60.0% |', log_content)

    # 更新表格中第 09 章的行
    target_row = r'\| \*\*09\*\* \| 汽笛聲中的木片便當 \| 📁 待整理 \| 📝 待撰寫 \| 🎨 待生成 \| 🎬 待生成 \| 🎙️ 待生成 \| ⏳ 待對齊 \| \*\*2026-11-21 17:30 / 19:30\*\* \|'
    replacement_row = f'| **09** | 汽笛聲中的木片便當 | ✅ 5大文獻 | ✅ 3.4萬字 | ✅ 4幅插圖 | ✅ {video_duration} | ✅ {podcast_duration} | ✅ 雙軌{total_subs}行 | **2026-11-21 17:30 / 19:30** |'
    log_content = log_content.replace(target_row, replacement_row)

    # 寫入第 09 章專屬發布日誌區塊
    ch09_log_block = f"""
### 2026-11-17：第 09 章《汽笛聲中的木片便當》全規格產製與雙軌排程上架完成
- **章節主題**：縱貫鐵路通車、生啤酒、喫茶店與鐵路便當的摩登生活（1908–1940 年代）
- **史料考證專卷**：完成 `09_汽笛聲中的木片便當考證史料.md`，深度梳理縱貫鐵路全通時刻表時間觀、臺灣鐵道飯店頂級法式西餐與廚師培育、經木（0.8mm檜木薄片）微孔呼吸吸濕與天然殺菌素防酸餿物理化學、月台便當從日之丸漬物到黃金炸排骨演進、大稻埕波麗路黑膠交響相親、山水亭文人沙龍、女給制度、以及建國啤酒廠前身（高砂麥酒）引進德國氨壓縮冷凍機克服亞熱帶高溫之低溫發酵生啤酒釀造歷史。
- **深度長文專論**：產出 `第09章_汽笛聲中的木片便當_縱貫鐵路通車生啤酒喫茶店與鐵路便當的摩登生活.md`，全文高達 **34,854 字元**，包含 4 組學術深度對照表與 4 組 4K 影視級微距分鏡腳本。
- **視覺資產與雙軌縮圖**：
  - 橫幅主視覺：`food_ch09_hero_banner.jpg` (1920x1080)
  - 飲食工藝圖：`food_ch09_bento_craft.jpg` (1920x1080)
  - 說明短片縮圖：`food_ch09_youtube_thumbnail.jpg` (1280x720，大正鐵道、木片便當暖金視覺)
  - 播客長片縮圖：`food_ch09_podcast_thumbnail.jpg` (1280x720，深邃琥珀藍金色調、喫茶店黑膠爵士風格)
- **NotebookLM 影音雙軌產製**：
  - 專屬筆記本 ID：`8db2ad14-e79e-4630-98aa-f4ce4074d441`
  - 語言模式：嚴格設定繁體中文（zh-TW）
  - 短片時長：`{video_duration}`
  - 播客時長：`{podcast_duration}`
- **音訊託管與影片合成**：
  - 播客音訊託管於 GitHub Releases v1.0.0：`food_ch09_podcast_deepdive.m4a`
  - FFmpeg 壓製 1080p 影片：`第09章_汽笛聲中的木片便當_播客深度對談.mp4`
- **字幕精修與說話呼吸律**：
  - 短片字幕：`第09章_汽笛聲中的木片便當_說明影片.srt`（{video_sub_lines} 行）
  - 播客字幕：`第09章_汽笛聲中的木片便當_雙人對談.srt`（{podcast_sub_lines} 行）
  - 雙軌字幕總計 **{total_subs} 行**，經過 100% 正體繁體中文專有名詞校正，絕無同音錯字，嚴格依說話語氣與呼吸自然換行，獨立保留語氣詞。
- **YouTube 雙軌排程上架**：
  - 說明短片：[YouTube 連結 (ID: {video_id})](https://youtu.be/{video_id})，排程公開：**2026-11-21 17:30**
  - 播客長片：[YouTube 連結 (ID: {podcast_id})](https://youtu.be/{podcast_id})，排程公開：**2026-11-21 19:30**
  - 官方清單：`舌尖上的臺灣` (`PLAFdajbNY8qg`)
  - 說明欄連結：均已完整掛載 4 組官方網頁與文庫連結。
"""
    log_content += "\n" + ch09_log_block
    with open(path_log, 'w', encoding='utf-8') as f:
        f.write(log_content)
    print("🎉 Successfully updated 工作日誌.md for Chapter 09!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_food_ch09_log.py <video_id> <podcast_id> [v_dur] [p_dur] [v_subs] [p_subs]")
        sys.exit(1)
    vid = sys.argv[1]
    pid = sys.argv[2]
    vdur = sys.argv[3] if len(sys.argv) > 3 else "8m30s"
    pdur = sys.argv[4] if len(sys.argv) > 4 else "14m15s"
    vsub = int(sys.argv[5]) if len(sys.argv) > 5 else 260
    psub = int(sys.argv[6]) if len(sys.argv) > 6 else 380
    update_chapter09_log(vid, pid, vdur, pdur, vsub, psub)
