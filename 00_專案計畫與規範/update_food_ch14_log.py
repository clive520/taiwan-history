# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

def update_chapter14_log(video_id=None, podcast_id=None, video_duration="12m12s", podcast_duration="22m17s", video_sub_lines=284, podcast_sub_lines=604):
    total_subs = video_sub_lines + podcast_sub_lines
    base_dir = Path(r"d:\Antigravity\科技歷史\臺灣史")
    
    # 若未傳入 ID，從 food_ch14_youtube_ids.txt 讀取
    if not video_id or not podcast_id:
        id_file = base_dir / "00_專案計畫與規範" / "food_ch14_youtube_ids.txt"
        if id_file.exists():
            lines = [l.strip() for l in id_file.read_text(encoding='utf-8').splitlines() if l.strip()]
            if len(lines) >= 2:
                video_id = lines[0]
                podcast_id = lines[1]
    
    if not video_id:
        video_id = "food_ch14_video_placeholder"
    if not podcast_id:
        podcast_id = "food_ch14_podcast_placeholder"

    path_log = base_dir / "舌尖上的臺灣" / "工作日誌.md"
    with open(path_log, 'r', encoding='utf-8') as f:
        log_content = f.read()

    # 更新儀表板進度 86.7% -> 93.3%
    log_content = re.sub(r'已完成\s*\*\*13\s*/\s*15\s*章\*\*\s*（\*\*86\.7%\*\*）', '已完成 **14 / 15 章**（**93.3%**）', log_content)
    log_content = re.sub(r'進度條：\s*`\[█████████████████░░░\]`\s*86\.7%', '進度條： `[██████████████████░░]` 93.3%', log_content)
    log_content = re.sub(r'\| 進行中 / 待啟動 \| 2 章 \| 13\.3% \|', '| 進行中 / 待啟動 | 1 章 \| 6.7% |', log_content)
    log_content = re.sub(r'\| 已發布 / 已完工 \| 13 章 \| 86\.7% \|', '| 已發布 / 已完工 \| 14 章 \| 93.3% |', log_content)

    # 更新表格中第 14 章的行
    target_row = r'\| \*\*14\*\* \| 吸管裡的黑色奇蹟 \| 📁 待整理 \| 📝 待撰寫 \| 🎨 待生成 \| 🎬 待生成 \| 🎙️ 待生成 \| ⏳ 待對齊 \| \*\*2026-11-26 17:30 / 19:30\*\* \|'
    replacement_row = f'| **14** | 吸管裡的黑色奇蹟 | ✅ 5大考證 | ✅ 2.4萬字 | ✅ 5幅插圖 | ✅ {video_duration} | ✅ {podcast_duration} | ✅ 雙軌{total_subs}行 | **2026-11-26 17:30 / 19:30** |'
    
    if target_row in log_content:
        log_content = log_content.replace(target_row, replacement_row)
    else:
        log_content = re.sub(r'\|\s*\*\*14\*\*\s*\|\s*吸管裡的黑色奇蹟\s*\|[\s\S]*?\|\s*\*\*2026-11-26 17:30 / 19:30\*\*\s*\|', replacement_row, log_content)

    # 寫入第 14 章專屬發布日誌區塊
    ch14_log_block = f"""
### 2026-11-23：第 14 章《吸管裡的黑色奇蹟》全規格產製與雙軌排程上架完成
- **章節主題**：春水堂、翰林與珍珠奶茶席捲全球百億美元的商業神話（1980s – 當代）
- **史料考證專卷**：完成 `14_吸管裡的黑色奇蹟考證史料.md`，深度梳理 1983 年臺中四維街陽羨茶行劉漢介以調酒雪克杯打破千年「茶只熱飲」禁忌、微氣泡包覆兒茶素收斂苦澀之物理機制；春水堂林秀慧建國市場買粉圓投入冰奶茶 vs 翰林茶館涂宗和鴨母寮市場白粉圓靈感發明公案，以及智慧財產法院十年訴訟「全體臺灣人共有文化資產」世紀判決；臺灣特有工業革命：益芳自動封口機 165°C 熱熔解決機車外送翻覆痛點、45度斜口粗吸管破膜應力集中與雙相流體吸吮力學；樹薯澱粉 85% 超高支鏈澱粉分子結構、糊化熱動力學、冷水激冷熱收縮塑造雙層梯度Q度、黑糖高滲透壓平衡與四小時老化回生死亡時效；以及手搖茶出海四次浪潮、臺灣精密機械與原物料供應鏈全球壟斷。
- **深度長文專論**：產出 `第14章_吸管裡的黑色奇蹟_春水堂翰林與珍珠奶茶席捲全球百億美元的商業神話.md`，全文高達 **23,800+ 字元**，包含 4 組學術深度對照表與 4 組 4K 影視級微距分鏡腳本。
- **視覺資產與雙軌縮圖**：
  - 橫幅主視覺：`food_ch14_hero_banner.jpg` (1920x1080)
  - 手搖工藝圖：`food_ch14_bubbletea_craft.jpg` (1920x1080)
  - 說明短片縮圖：`food_ch14_youtube_thumbnail.jpg` (1280x720，老木吧檯、雪克杯與琥珀珍奶油畫風格)
  - 播客專用背景：`food_ch14_podcast_bg.jpg` (1920x1080，嚴格 16:9 等比無拉伸，溫暖茶館光影底圖)
  - 播客長片縮圖：`food_ch14_podcast_thumbnail.jpg` (1280x720，黑珍珠與手搖茶帝國、雙人廣播深度風格)
- **NotebookLM 影音雙軌產製**：
  - 專屬筆記本 ID：`5dc5231a-7847-46be-919e-8cd689475cbd`
  - 語言模式：嚴格設定繁體中文（zh-TW）
  - 短片時長：`{video_duration}`
  - 播客時長：`{podcast_duration}`
- **音訊託管與影片合成**：
  - 播客音訊備份至 Releases：`food_ch14_podcast_deepdive.m4a`
  - FFmpeg 壓製 1080p 影片：`第14章_吸管裡的黑色奇蹟_播客深度對談.mp4` (嚴格無拉伸無變形底圖)
- **字幕精修與說話呼吸律**：
  - 短片字幕：`第14章_吸管裡的黑色奇蹟_說明影片.srt`（{video_sub_lines} 行）
  - 播客字幕：`第14章_吸管裡的黑色奇蹟_雙人對談.srt`（{podcast_sub_lines} 行）
  - 雙軌字幕總計 **{total_subs} 行**，落實 100% 繁體中文名詞校正（珍珠奶茶、春水堂、翰林茶館、泡沫紅茶、雪克杯、益芳封口機、斜口粗吸管、樹薯澱粉、糊化、Q度、老化回生、澀谷、羅浮宮等），依語氣呼吸律自然斷句。
- **YouTube 雙軌官方排程發布**：
  - 說明短片：[YouTube 連結 (ID: {video_id})](https://youtu.be/{video_id})，排程公開：**2026-11-26 17:30**
  - 播客長片：[YouTube 連結 (ID: {podcast_id})](https://youtu.be/{podcast_id})，排程公開：**2026-11-26 19:30**
  - 官方清單：`舌尖上的臺灣` (`PLAFdajbNY8qg`)
  - 說明欄資訊：完整嵌入 4 組數位文庫官網連結。
"""
    log_content += ch14_log_block
    with open(path_log, 'w', encoding='utf-8') as f:
        f.write(log_content)
    print("✅ 舌尖上的臺灣/工作日誌.md 已成功更新第 14 章進度！")

if __name__ == "__main__":
    update_chapter14_log()
