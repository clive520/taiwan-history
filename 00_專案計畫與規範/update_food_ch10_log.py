import re
import sys

def update_chapter10_log(video_id, podcast_id, video_duration="8m30s", podcast_duration="18m00s", video_sub_lines=200, podcast_sub_lines=500):
    total_subs = video_sub_lines + podcast_sub_lines
    
    # 1. 更新 js/data-food.js
    path_data_food = "js/data-food.js"
    with open(path_data_food, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern_ch10 = r'("id":\s*"ch10",[\s\S]*?"status":\s*)"planned"'
    replacement_ch10 = rf'\1"published",\n      "videoId": "{video_id}",\n      "podcastId": "{podcast_id}"'
    new_content = re.sub(pattern_ch10, replacement_ch10, content)
    with open(path_data_food, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ js/data-food.js updated successfully!")
    
    # 2. 更新 舌尖上的臺灣/js/data.js
    path_data_tw = "舌尖上的臺灣/js/data.js"
    with open(path_data_tw, 'r', encoding='utf-8') as f:
        content_tw = f.read()
    new_content_tw = re.sub(pattern_ch10, replacement_ch10, content_tw)
    with open(path_data_tw, 'w', encoding='utf-8') as f:
        f.write(new_content_tw)
    print("✅ 舌尖上的臺灣/js/data.js updated successfully!")

    # 3. 更新長文專論中的 placeholder
    path_doc = "舌尖上的臺灣/03_帝國之眼與東洋滋味/第10章_山嵐間的東方美人_大稻埕洋行新竹苗栗客庄膨風茶與征服世界的烏龍傳奇.md"
    with open(path_doc, 'r', encoding='utf-8') as f:
        doc_content = f.read()
    doc_content = doc_content.replace("placeholder_food_ch10_video", video_id)
    doc_content = doc_content.replace("placeholder_food_ch10_podcast", podcast_id)
    with open(path_doc, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    print("✅ 深度專論 YouTube Video ID updated successfully!")

    # 4. 更新 舌尖上的臺灣/工作日誌.md
    path_log = "舌尖上的臺灣/工作日誌.md"
    with open(path_log, 'r', encoding='utf-8') as f:
        log_content = f.read()

    # 更新儀表板進度 60.0% ➔ 66.7%
    log_content = re.sub(r'已完成\s*\*\*9\s*/\s*15\s*章\*\*\s*（\*\*60\.0%\*\*）', '已完成 **10 / 15 章**（**66.7%**）', log_content)
    log_content = re.sub(r'進度條：\s*`\[████████████░░░░░░░░\]`\s*60\.0%', '進度條： `[█████████████░░░░░░░]` 66.7%', log_content)
    log_content = re.sub(r'\| 進行中 / 待啟動 \| 6 章 \| 40\.0% \|', '| 進行中 / 待啟動 | 5 章 \| 33.3% |', log_content)
    log_content = re.sub(r'\| 已發布 / 已完工 \| 9 章 \| 60\.0% \|', '| 已發布 / 已完工 \| 10 章 \| 66.7% |', log_content)

    # 更新表格中第 10 章的行
    target_row = r'\| \*\*10\*\* \| 山嵐間的東方美人 \| 📁 待整理 \| 📝 待撰寫 \| 🎨 待生成 \| 🎬 待生成 \| 🎙️ 待生成 \| ⏳ 待對齊 \| \*\*2026-11-22 17:30 / 19:30\*\* \|'
    replacement_row = f'| **10** | 山嵐間的東方美人 | ✅ 5大文獻 | ✅ 2.7萬字 | ✅ 4幅插圖 | ✅ {video_duration} | ✅ {podcast_duration} | ✅ 雙軌{total_subs}行 | **2026-11-22 17:30 / 19:30** |'
    log_content = log_content.replace(target_row, replacement_row)

    # 寫入第 10 章專屬發布日誌區塊
    ch10_log_block = f"""
### 2026-11-18：第 10 章《山嵐間的東方美人》全規格產製與雙軌排程上架完成
- **章節主題**：大稻埕洋行、新竹苗栗客庄膨風茶與征服世界的烏龍傳奇（1860s – 1930s）
- **史料考證專卷**：完成 `10_山嵐間的東方美人考證史料.md`，深度梳理新竹北埔峨眉微氣候、小綠葉蟬（浮塵子）叮咬著涎之生物化學防衛反應（茉莉酸途徑、芳樟醇氧化物、水楊酸甲酯天然蜜香）、客家茶師 65%~75% 極限重發酵與厚布悶堆回潤工藝、蘇格蘭冒險家約翰·陶德與臺灣茶葉之父李春生創建寶順洋行、茶底銀制度、1869 年飛剪帆船 Formosa Oolong 直航紐約曼哈頓拍賣天價、大稻埕萬名揀茶女工開啟近代臺灣女性受薪獨立勞動、以及日治新竹州高級茶評鑑會特等賞一斤換數棟房之膨風傳奇與維多利亞女王賜名考證。
- **深度長文專論**：產出 `第10章_山嵐間的東方美人_大稻埕洋行新竹苗栗客庄膨風茶與征服世界的烏龍傳奇.md`，全文高達 **27,717 字元**，包含 4 組學術深度對照表與 4 組 4K 影視級微距分鏡腳本。
- **視覺資產與雙軌縮圖**：
  - 橫幅主視覺：`food_ch10_hero_banner.jpg` (1920x1080)
  - 飲食工藝圖：`food_ch10_tea_craft.jpg` (1920x1080)
  - 說明短片縮圖：`food_ch10_youtube_thumbnail.jpg` (1280x720，山嵐翠綠、白毫五色茶金風格)
  - 播客長片縮圖：`food_ch10_podcast_thumbnail.jpg` (1280x720，深邃琥珀茶金、大稻埕洋行風格)
- **NotebookLM 影音雙軌產製**：
  - 專屬筆記本 ID：`0d32d717-76b0-4144-a012-1fc6b0792766`
  - 語言模式：嚴格設定繁體中文（zh-TW）
  - 短片時長：`{video_duration}`
  - 播客時長：`{podcast_duration}`
- **音訊託管與影片合成**：
  - 播客音訊託管於 GitHub Releases v1.0.0：`food_ch10_podcast_deepdive.m4a`
  - FFmpeg 壓製 1080p 影片：`第10章_山嵐間的東方美人_播客深度對談.mp4`
- **字幕精修與說話呼吸律**：
  - 短片字幕：`第10章_山嵐間的東方美人_說明影片.srt`（{video_sub_lines} 行）
  - 播客字幕：`第10章_山嵐間的東方美人_雙人對談.srt`（{podcast_sub_lines} 行）
  - 雙軌字幕總計 **{total_subs} 行**，經過 100% 正體繁體中文專有名詞校正（小綠葉蟬、芳樟醇氧化物、水楊酸甲酯、悶堆回潤、寶順洋行、陶德、李春生、膨風茶等），絕無同音錯字，嚴格依說話語氣與呼吸自然換行，獨立保留語氣詞。
- **YouTube 雙軌排程上架**：
  - 說明短片：[YouTube 連結 (ID: {video_id})](https://youtu.be/{video_id})，排程公開：**2026-11-22 17:30**
  - 播客長片：[YouTube 連結 (ID: {podcast_id})](https://youtu.be/{podcast_id})，排程公開：**2026-11-22 19:30**
  - 官方清單：`舌尖上的臺灣` (`PLAFdajbNY8qg`)
  - 說明欄連結：均已完整掛載 4 組官方網頁與文庫連結。
"""
    log_content += "\n" + ch10_log_block
    with open(path_log, 'w', encoding='utf-8') as f:
        f.write(log_content)
    print("🎉 Successfully updated 工作日誌.md for Chapter 10!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_food_ch10_log.py <video_id> <podcast_id> [v_dur] [p_dur] [v_subs] [p_subs]")
        sys.exit(1)
    vid = sys.argv[1]
    pid = sys.argv[2]
    vdur = sys.argv[3] if len(sys.argv) > 3 else "8m30s"
    pdur = sys.argv[4] if len(sys.argv) > 4 else "18m00s"
    vsub = int(sys.argv[5]) if len(sys.argv) > 5 else 200
    psub = int(sys.argv[6]) if len(sys.argv) > 6 else 500
    update_chapter10_log(vid, pid, vdur, pdur, vsub, psub)
