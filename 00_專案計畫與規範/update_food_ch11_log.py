# -*- coding: utf-8 -*-
import re
import sys

def update_chapter11_log(video_id="dtvBLfRG0V4", podcast_id="iPfVskJT3vk", video_duration="7m05s", podcast_duration="17m25s", video_sub_lines=213, podcast_sub_lines=508):
    total_subs = video_sub_lines + podcast_sub_lines
    path_log = "舌尖上的臺灣/工作日誌.md"
    with open(path_log, 'r', encoding='utf-8') as f:
        log_content = f.read()

    # 更新儀表板進度
    log_content = re.sub(r'已完成\s*\*\*10\s*/\s*15\s*章\*\*\s*（\*\*66\.7%\*\*）', '已完成 **11 / 15 章**（**73.3%**）', log_content)
    log_content = re.sub(r'進度條：\s*`\[█████████████░░░░░░░\]`\s*66\.7%', '進度條： `[██████████████░░░░░░]` 73.3%', log_content)
    log_content = re.sub(r'\| 進行中 / 待啟動 \| 5 章 \| 33\.3% \|', '| 進行中 / 待啟動 | 4 章 \| 26.7% |', log_content)
    log_content = re.sub(r'\| 已發布 / 已完工 \| 10 章 \| 66\.7% \|', '| 已發布 / 已完工 \| 11 章 \| 73.3% |', log_content)

    # 更新表格中第 11 章的行
    target_row = r'\| \*\*11\*\* \| 那一碗鄉愁的紅湯 \| 📁 待整理 \| 📝 待撰寫 \| 🎨 待生成 \| 🎬 待生成 \| 🎙️ 待生成 \| ⏳ 待對齊 \| \*\*2026-11-23 17:30 / 19:30\*\* \|'
    replacement_row = f'| **11** | 那一碗鄉愁的紅湯 | ✅ 5大文獻 | ✅ 3.1萬字 | ✅ 5幅插圖 | ✅ {video_duration} | ✅ {podcast_duration} | ✅ 雙軌{total_subs}行 | **2026-11-23 17:30 / 19:30** |'
    
    if target_row in log_content:
        log_content = log_content.replace(target_row, replacement_row)
    else:
        # 正則容錯替換
        log_content = re.sub(r'\|\s*\*\*11\*\*\s*\|\s*那一碗鄉愁的紅湯\s*\|[\s\S]*?\|\s*\*\*2026-11-23 17:30 / 19:30\*\*\s*\|', replacement_row, log_content)

    # 寫入第 11 章專屬發布日誌區塊
    ch11_log_block = f"""
### 2026-11-19：第 11 章《那一碗鄉愁的紅湯》全規格產製與雙軌排程上架完成
- **章節主題**：岡山豆瓣醬、四川老兵與臺灣紅燒牛肉麵的混血傳奇（1949 – 1980s）
- **史料考證專卷**：完成 `11_那一碗鄉愁的紅湯考證史料.md`，深度梳理高雄岡山空軍機校眷村微氣候、四川老兵劉明德因應蠶豆匱乏改良黃豆日曬發酵辣豆瓣醬、美援麵粉與戰後都市化衝擊傳統漢人「敬牛如親、終生不食牛肉」之農耕戒律、臺北寶慶路防空洞與桃源街克難木輪牛肉麵攤之興起、分子料理學解析（牛腱I型膠原蛋白慢火明膠水解、美拉德褐變反應、臺灣發酵酸菜有機酸協同去膩）、梁實秋《雅舍談吃》考證川味紅燒牛肉麵乃臺灣特產之定論、以及每年國際牛肉麵節與國家級文化認同。
- **深度長文專論**：產出 `第11章_那一碗鄉愁的紅湯_岡山豆瓣醬四川老兵與臺灣紅燒牛肉麵的混血傳奇.md`，全文高達 **31,075 字元**，包含 4 組學術深度對照表與 4 組 4K 影視級微距分鏡腳本。
- **視覺資產與雙軌縮圖**：
  - 橫幅主視覺：`food_ch11_hero_banner.jpg` (1920x1080)
  - 飲食工藝圖：`food_ch11_beef_noodle_craft.jpg` (1920x1080)
  - 說明短片縮圖：`food_ch11_youtube_thumbnail.jpg` (1280x720，眷村暖紅、油畫大碗風格)
  - 播客專用背景：`food_ch11_podcast_bg.jpg` (1920x1080，嚴格 16:9 等比無拉伸，鎢絲燈夜市巷弄底圖)
  - 播客長片縮圖：`food_ch11_podcast_thumbnail.jpg` (1280x720，眷村紅調、雙人廣播深度風格)
- **NotebookLM 影音雙軌產製**：
  - 專屬筆記本 ID：`73a11068-cf22-4088-a743-96cbb9e95c71`
  - 語言模式：嚴格設定繁體中文（zh-TW）
  - 短片時長：`{video_duration}` (41.4 MB)
  - 播客時長：`{podcast_duration}` (12.4 MB)
- **音訊託管與影片合成**：
  - 播客音訊備份至 Releases：`food_ch11_podcast_deepdive.m4a`
  - FFmpeg 壓製 1080p 影片：`第11章_那一碗鄉愁的紅湯_播客深度對談.mp4` (106 MB，背景絕不拉伸)
- **字幕精修與說話呼吸律**：
  - 短片字幕：`第11章_那一碗鄉愁的紅湯_說明影片.srt`（{video_sub_lines} 行）
  - 播客字幕：`第11章_那一碗鄉愁的紅湯_雙人對談.srt`（{podcast_sub_lines} 行）
  - 雙軌字幕總計 **{total_subs} 行**，落實 100% 繁體中文名詞校正（岡山豆瓣醬、劉明德、牛腱子、明膠水解、雅舍談吃、梁實秋、桃源街等），依語氣呼吸律自然斷句。
- **YouTube 雙軌官方排程發布**：
  - 說明短片：[YouTube 連結 (ID: {video_id})](https://youtu.be/{video_id})，排程公開：**2026-11-23 17:30**
  - 播客長片：[YouTube 連結 (ID: {podcast_id})](https://youtu.be/{podcast_id})，排程公開：**2026-11-23 19:30**
  - 官方清單：`舌尖上的臺灣` (`PLAFdajbNY8qg`)
  - 說明欄資訊：完整嵌入 4 組數位文庫官網連結。
"""
    log_content += ch11_log_block
    with open(path_log, 'w', encoding='utf-8') as f:
        f.write(log_content)
    print("✅ 舌尖上的臺灣/工作日誌.md 已成功更新第 11 章進度！")

if __name__ == "__main__":
    update_chapter11_log()
