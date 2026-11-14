# -*- coding: utf-8 -*-
"""
更新《舌尖上的臺灣》工作日誌.md，同步第 07 章的進度儀表板、矩陣與執行記錄。
"""

import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
LOG_PATH = BASE_DIR / "舌尖上的臺灣" / "工作日誌.md"

def update_log(v1_id, v2_id, v1_duration, v2_duration, v1_lines, v2_lines):
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 更新最新更新時間
    content = re.sub(
        r"\*\*最新更新時間\*\*：.*",
        "**最新更新時間**：2026 年 11 月 14 日 15:30",
        content
    )

    # 2. 更新儀表板百分比 (40.0% -> 46.7%)
    old_dashboard = """│ 史料收集完成度     │ [████████░░░░░░░░░░░░] 40.0% (第01~06章考證史料專卷完工) │
│ 章節內容撰寫       │ [████████░░░░░░░░░░░░] 40.0% (第01~06章萬字深度長文完工) │
│ 歷史插圖生成       │ [████████░░░░░░░░░░░░] 40.0% (第01~06章歷史插畫雙軌縮圖完工)│
│ 說明影片生成 (NLM) │ [████████░░░░░░░░░░░░] 40.0% (第01~06章說明影片全數完成) │
│ 深度對談音訊 (NLM) │ [████████░░░░░░░░░░░░] 40.0% (第01~06章對談音訊全數完成) │
│ 影視級字幕 (.srt)  │ [████████░░░░░░░░░░░░] 40.0% (第01~06章雙軌影視級字幕) │
│ YouTube 排程發布   │ [████████░░░░░░░░░░░░] 40.0% (第01~06章共12支影片排程成功) │"""

    new_dashboard = """│ 史料收集完成度     │ [█████████░░░░░░░░░░░] 46.7% (第01~07章考證史料專卷完工) │
│ 章節內容撰寫       │ [█████████░░░░░░░░░░░] 46.7% (第01~07章萬字深度長文完工) │
│ 歷史插圖生成       │ [█████████░░░░░░░░░░░] 46.7% (第01~07章歷史插畫雙軌縮圖完工)│
│ 說明影片生成 (NLM) │ [█████████░░░░░░░░░░░] 46.7% (第01~07章說明影片全數完成) │
│ 深度對談音訊 (NLM) │ [█████████░░░░░░░░░░░] 46.7% (第01~07章對談音訊全數完成) │
│ 影視級字幕 (.srt)  │ [█████████░░░░░░░░░░░] 46.7% (第01~07章雙軌影視級字幕) │
│ YouTube 排程發布   │ [█████████░░░░░░░░░░░] 46.7% (第01~07章共14支影片排程成功) │"""

    if old_dashboard in content:
        content = content.replace(old_dashboard, new_dashboard)
        print("✅ 儀表板已成功更新至 46.7%！")
    else:
        print("⚠️ 未能直接比對 old_dashboard，嘗試正則替換...")
        content = re.sub(r'40\.0% \(第01~06章[^)]*\)', '46.7% (第01~07章完工)', content)

    # 3. 更新矩陣表格
    matrix_old = """| **07** | 甘甜的舌尖密碼 | 📁 待整理 | 📝 待撰寫 | 🎨 待生成 | 🎬 待生成 | 🎙️ 待生成 | ⏳ 待對齊 | **2026-11-19 17:30 / 19:30** |"""
    matrix_new = f"""| **07** | 甘甜的舌尖密碼 | ✅ 6大文獻 | ✅ 2.1萬字 | ✅ 4幅插圖 | ✅ {v1_duration} | ✅ {v2_duration} | ✅ 雙軌{v1_lines + v2_lines}行 | **2026-11-19 17:30 / 19:30** |"""

    if matrix_old in content:
        content = content.replace(matrix_old, matrix_new)
        print("✅ 全系列矩陣表格第 07 章已更新為完工！")
    else:
        print("⚠️ 未能直接比對 matrix_old")

    # 4. 追加第 07 章的執行日誌
    additions = f"""
---

### 2026-11-14：第 07 章《甘甜的舌尖密碼》完整規格產製與發布

1. **史料考證專卷編纂**：
   - 彙整沈光文《臺灣輿地跋尾》、季麒光《臺灣雜記》、康熙高拱乾《臺灣府志·物產志·糖》（瓦溜淋泥法）、康熙周鍾瑄《諸羅縣志·風俗志》（「饌品尚甜，以糖多為豪爽風雅」）、乾隆范咸《重修臺灣府志》（三郊之首「糖郊李勝興」）、日治片岡巖《臺灣風俗誌》、托斯丹·范伯倫（Thorstein Veblen）《有閒階級論》炫耀性消費（Conspicuous Consumption）與風味向下滲透（Trickle-down effect）、蔗糖非還原糖高溫焦糖化（Caramelization）、250°C 生鐵鑊氣與烏醋水解酸催化梅納反應（Maillard Reaction）、琥珀糖膜鎖水機制、番薯粉糊化三維半流體溶膠阻礙擴散與 T1R2/T1R3 甜味受體時間放大效應、高糖對黑豆蔭油高鈉與烏醋嗆酸之神經味覺掩蔽（Taste Masking）、扁魚（IMP）+ 香菇（GMP）+ 大骨（Glu）之鮮味乘數效應、白糖粿純糯米拉絲黏彈性與古法椪糖（膨糖）碳酸氫鈉熱分解微孔發泡與玻璃化轉變（Tg 62°C）。
   - 產出檔案：[`歷史資料/02_唐山渡海與閩粵交融/07_甘甜的舌尖密碼考證史料.md`](file:///d:/Antigravity/科技歷史/臺灣史/舌尖上的臺灣/歷史資料/02_唐山渡海與閩粵交融/07_甘甜的舌尖密碼考證史料.md)。
2. **深度長文專論創作**：
   - 撰寫 21,000+ 字學術深度長文（21,704 字元），內含 4 組學術深度對照表（明鄭清領臺灣製糖工藝演進、五條港三郊與東亞白銀糖貿易矩陣、阿舍菜貴族宴席與現代小吃味覺下滲對比、臺南經典甜味小吃食品物化反應光譜）與 4 組 4K 微距影視級分鏡腳本。
   - 頂部嵌入影音導讀模組，直通 YouTube 雙軌排程影片。
   - 產出檔案：[`02_唐山渡海與閩粵交融/第07章_甘甜的舌尖密碼_為什麼臺南人的菜這麼甜明鄭煮糖府城富庶與貴族炫耀心理學.md`](file:///d:/Antigravity/科技歷史/臺灣史/舌尖上的臺灣/02_唐山渡海與閩粵交融/第07章_甘甜的舌尖密碼_為什麼臺南人的菜這麼甜明鄭煮糖府城富庶與貴族炫耀心理學.md)。
3. **歷史視覺插畫與 1280x720 雙軌縮圖產製**：
   - 府城水仙宮五條港糖商繁華古典 Rembrandt 暖金油畫：`assets/images/food_ch07/food_ch07_hero_banner.jpg`。
   - 糖廍石車榨蔗與生鐵鑊熬糖古典寫實油畫：`assets/images/food_ch07/food_ch07_sugar_craft.jpg`。
   - 說明短片封面縮圖（1280x720 焦糖赤金風格）：`assets/images/food_ch07/food_ch07_youtube_thumbnail.jpg`。
   - 播客對談封面縮圖（1280x720 沉穩深藍琥珀金風格）：`assets/images/food_ch07/food_ch07_podcast_thumbnail.jpg`。
4. **NotebookLM 生成與影音處理（100% 正體繁體中文語音）**：
   - 筆記本：`《舌尖上的臺灣》第07章 甘甜的舌尖密碼` (ID: `0fdef0e2-4251-4174-ac05-97f77c7ed4e4`)。
   - 說明短片：`第07章_甘甜的舌尖密碼_說明影片.mp4`（長度 {v1_duration}）。
   - 深度對談音訊：`food_ch07_podcast_deepdive.m4a`（長度 {v2_duration}）。
   - FFmpeg 雙人對談 1080p 高畫質影片合成：`第07章_甘甜的舌尖密碼_播客深度對談.mp4`。
5. **語意呼吸律影視級字幕轉錄與精修**：
   - 第一階段：依據使用者要求進行 100+ 個專有詞彙與同音字全面校正（消除陳永華、瓦溜淋泥法、糖郊李勝興、范伯倫《有閒階級論》炫耀性消費、阿舍菜、生炒鱔魚意麵、焦糖化、梅納反應、琥珀糖膜、半流體溶膠、T1R2/T1R3 甜味受體、味覺掩蔽、鮮味乘數、白糖粿、椪糖玻璃化轉變等語音轉錄偏誤）。
   - 第二階段：依據人類自然說話之語調停頓與呼吸律斷句，徹底消除斷在破詞缺陷處，並將對話交談語氣詞（「對吧？」、「真的！」、「沒錯」、「確實」等）獨立成行。
   - 說明影片字幕：`第07章_甘甜的舌尖密碼_說明影片.srt` ({v1_lines} 行)。
   - 播客對談字幕：`第07章_甘甜的舌尖密碼_雙人對談.srt` ({v2_lines} 行，合計 {v1_lines + v2_lines} 行)。
6. **GitHub Releases 音訊託管**：
   - 上傳 `food_ch07_podcast_deepdive.m4a` 至 `clive520/taiwan-history` Releases `v1.0.0`。
   - URL: `https://github.com/clive520/taiwan-history/releases/download/v1.0.0/food_ch07_podcast_deepdive.m4a`。
7. **YouTube API 雙軌排程上架**：
   - 官方播放清單：**`舌尖上的臺灣`** (Playlist ID: `PLAFdajbNY8qg`)。
   - 說明短片：ID [`{v1_id}`](https://youtu.be/{v1_id})，排程 **2026-11-19 17:30**。
   - 深度對談：ID [`{v2_id}`](https://youtu.be/{v2_id})，排程 **2026-11-19 19:30**。
   - 說明欄均內建完整 4 組網頁與文庫連結。
8. **資料庫與長文連結更新**：
   - 更新 `js/data-food.js` 與 `舌尖上的臺灣/js/data.js`，將第 07 章狀態切換為 `published`，登錄雙軌 Video ID、音訊 Releases 連結與 Banner。
"""

    content = content.rstrip() + "\n" + additions

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("🎉 Successfully updated 工作日誌.md for Chapter 07!")

if __name__ == "__main__":
    if len(sys.argv) >= 7:
        update_log(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6]))
    else:
        print("Usage: python update_food_ch07_log.py <v1_id> <v2_id> <v1_dur> <v2_dur> <v1_lines> <v2_lines>")
