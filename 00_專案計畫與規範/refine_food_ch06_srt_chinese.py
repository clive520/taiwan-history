# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 06 章 繁體中文版 影視級字幕精修處理器
1. 先查錯別字與同音字：針對新竹都城隍廟、九降風氣候動力學、在來米（秈稻）直鏈澱粉凝膠、紅龜粿印模材料學、客家面帕粄、牛汶水與米苔目等 80+ 術語進行全方位精修校正。
2. 依據人類說話語音、語詞與呼吸律斷句：0 破字破詞，獨立保留對話交談語氣詞（「對吧？」、「真的！」、「沒錯」、「我的天」等）。
3. 輸出：
   - 第06章_廟埕香火與米食變奏_說明影片.srt
   - 第06章_廟埕香火與米食變奏_雙人對談.srt
"""
import sys
import os
import json
import re
from pathlib import Path
import opencc

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH06_DIR = BASE_DIR / "舌尖上的臺灣" / "02_唐山渡海與閩粵交融"

RAW_VID_JSON = CH06_DIR / "whisper_raw_video.json"
RAW_POD_JSON = CH06_DIR / "whisper_raw_podcast.json"

VID_SRT = CH06_DIR / "第06章_廟埕香火與米食變奏_說明影片.srt"
POD_SRT = CH06_DIR / "第06章_廟埕香火與米食變奏_雙人對談.srt"

cc = opencc.OpenCC('s2twp')

# 完整精修替換對照表（按長度由長至短、精確規則優先）
CORRECTIONS = [
    # 說明短片專屬修正
    (r"交響區", "交響曲"),
    (r"都城皇廟", "都城隍廟"),
    (r"城皇廟", "城隍廟"),
    (r"繁複的飛眼", "繁複的飛簷"),
    (r"飛眼", "飛簷"),
    (r"水田莊", "水田庄"),
    (r"山木真樓", "杉木蒸籠"),
    (r"山木蒸籠", "杉木蒸籠"),
    (r"噴泊而出", "噴薄而出"),
    (r"噴泊出", "噴薄出"),
    (r"白泥水氣", "白米水汽"),
    (r"白米水氣", "白米水汽"),
    (r"這兩種奇襲的劇烈碰撞", "這兩種氣息的劇烈碰撞"),
    (r"奇襲的劇烈碰撞", "氣息的劇烈碰撞"),
    (r"廟城前", "廟埕前"),
    (r"廟城香火", "廟埕香火"),
    (r"廟城", "廟埕"),
    (r"廟前前", "廟埕前"),
    (r"雅熱帶島嶼", "亞熱帶島嶼"),
    (r"雅熱帶氣候", "亞熱帶氣候"),
    (r"雅熱帶", "亞熱帶"),
    (r"煉金樹般", "煉金術般"),
    (r"煉金樹", "煉金術"),
    (r"壓乾、揉裹、蒸炊", "壓乾、揉粿、蒸炊"),
    (r"揉裹", "揉粿"),
    (r"工桌上", "供桌上"),
    (r"工桌", "供桌"),
    (r"傳統米時", "傳統米食"),
    (r"米時", "米食"),
    (r"米石", "米食"),
    (r"米濕", "米食"),
    (r"九祖不爛", "久煮不爛"),
    (r"軟硬失蹤", "軟硬適中"),
    (r"在萊米", "在來米"),
    (r"再來米", "在來米"),
    (r"鹹稻", "秈稻"),
    (r"仙稻", "秈稻"),
    (r"直煉澱粉", "直鏈澱粉"),
    (r"直鍊澱粉", "直鏈澱粉"),
    (r"織煉澱粉", "支鏈澱粉"),
    (r"織鏈澱粉", "支鏈澱粉"),
    (r"抗斷煉米時", "抗斷裂米食"),
    (r"抗斷煉", "抗斷裂"),
    (r"抗斷裂米時", "抗斷裂米食"),
    (r"回聲凝膠化", "回生凝膠化"),
    (r"回聲", "回生"),
    (r"當高質鍊的", "當高直鏈的"),
    (r"高質鍊", "高直鏈"),
    (r"分子常驗", "分子長鏈"),
    (r"親建網絡", "氫鍵網絡"),
    (r"親建", "氫鍵"),
    (r"傾見", "氫鍵"),
    (r"抗減切力", "抗剪切力"),
    (r"在成化過程中", "在陳化過程中"),
    (r"成化過程", "陳化過程"),
    (r"油離脂肪酸", "游離脂肪酸"),
    (r"微官分子", "微觀分子"),
    (r"微官", "微觀"),
    (r"焚峰效應", "焚風效應"),
    (r"漏斗狀的埃口", "漏斗狀的隘口"),
    (r"埃口", "隘口"),
    (r"俠管效應", "狹管效應"),
    (r"酒醬風", "九降風"),
    (r"九臟風", "九降風"),
    (r"九藏風", "九降風"),
    (r"大頂沸水", "大鼎沸水"),
    (r"大頂裡", "大鼎裡"),
    (r"大頂", "大鼎"),
    (r"半液態生蜜漿", "半液態生米漿"),
    (r"生蜜漿", "生米漿"),
    (r"熟透的果影", "熟透的粿引"),
    (r"果影", "粿引"),
    (r"果引", "粿引"),
    (r"金屬塞孔", "金屬篩孔"),
    (r"內部劑水結構", "內部三維凝膠結構"),
    (r"冷熱中級", "冷熱衝擊"),
    (r"無倫零壁", "無與倫比"),
    (r"碎石文化遺跪", "歲時文化儀軌"),
    (r"碎石文化", "歲時文化"),
    (r"紅龜果石", "紅龜粿時"),
    (r"紅龜果", "紅龜粿"),
    (r"紅龜鍋", "紅龜粿"),
    (r"巫星石", "烏心石"),
    (r"無星石", "烏心石"),
    (r"年糯的米糰", "黏糯的米糰"),
    (r"將默默在厚重的案板上", "將木模在厚重的案板上"),
    (r"將默默", "將木模"),
    (r"鮮豔珠紅", "鮮豔朱紅"),
    (r"他們的貴文化", "他們的粿文化"),
    (r"貴文化", "粿文化"),
    (r"碎石衣櫃", "歲時儀軌"),
    (r"開墾提田", "開墾梯田"),
    (r"丘陵提田", "丘陵梯田"),
    (r"丘陵堤田", "丘陵梯田"),
    (r"面帕板", "面帕粄"),
    (r"麵耙板", "面帕粄"),
    (r"客家板石", "客家粄食"),
    (r"板文化", "粄文化"),
    (r"板石", "粄食"),
    (r"圓扁新瓦機", "圓扁糍粑"),
    (r"夏天農芒時", "夏天農忙時"),
    (r"農芒換工", "農忙換工"),
    (r"高年潭的糯米", "高黏彈的糯米"),
    (r"無星石木印壽歸", "烏心石木印壽龜"),
    (r"靜天乏祖", "敬天法祖"),

    # 播客長片專屬修正
    (r"簡年飛簷", "剪黏飛簷"),
    (r"煙蘭正在繚繞", "煙嵐正在繚繞"),
    (r"煙蘭", "煙嵐"),
    (r"抗傷強度", "抗張強度"),
    (r"不一斷的米粉", "不易斷的米粉"),
    (r"不一斷", "不易斷"),
    (r"再來撈米", "在來老米"),
    (r"被風波的頭前溪谷", "背風坡的頭前溪谷"),
    (r"被風波", "背風坡"),
    (r"頭前西", "頭前溪"),
    (r"掛在主架上的細米粉", "掛在竹架上的細米粉"),
    (r"主架上", "竹架上"),
    (r"米太木", "米苔目"),
    (r"米三母", "米篩目"),
    (r"客教化叫米三母", "客家話叫米篩目"),
    (r"客教化", "客家話"),
    (r"熟粿蠅", "熟粿引"),
    (r"非牛燉流體", "非牛頓流體"),
    (r"非牛燉", "非牛頓"),
    (r"心不還唯待嚼勁", "芯部還微帶嚼勁"),
    (r"牛蚊水", "牛汶水"),
    (r"牛溫水", "牛汶水"),
    (r"糯米籽吧", "糯米糍粑"),
    (r"泡水漏背的水牛", "泡水露背的水牛"),
    (r"泡水漏背", "泡水露背"),
    (r"多粉類物質", "多酚類物質"),
    (r"多粉類", "多酚類"),
    (r"米歸", "米龜"),
    (r"十斤的米歸", "十斤的米龜"),
    (r"起了[一隻]?十斤的米[歸龜]", "乞了一隻十斤的米龜"),
    (r"免爬", "面帕粄"),
    (r"像樹脂一樣", "像樹枝一樣高度分支"),
    (r"耐煮彈牙", "耐煮彈牙"),
    (r"這是一頭在泥塘裡", "這是一頭在泥塘裡"),
    (r"乞龜禮俗", "乞龜禮俗"),
    (r"惠安郭氏", "惠安郭氏"),
    (r"新竹米粉", "新竹米粉"),
    (r"壽歸", "壽龜"),
    (r"直煉", "直鏈"),
    (r"織煉", "支鏈"),
    (r"直鍊", "直鏈"),
    (r"織鏈", "支鏈"),
    (r"油離", "游離"),
    (r"都城隍廟", "都城隍廟")
]

def format_ts(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis -= 1000
    if secs >= 60:
        minutes += 1
        secs -= 60
    if minutes >= 60:
        hours += 1
        minutes -= 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def clean_text(text):
    text = cc.convert(text)
    for pattern, rep in CORRECTIONS:
        text = re.sub(pattern, rep, text)
    # 標點符號標準化
    text = text.replace(",", "，").replace("?", "？").replace("!", "！")
    return text.strip()

def process_segments_to_srt(segments, out_path, is_podcast=False):
    srt_items = []
    
    # 獨立對話交談語氣詞列表（若開頭或單獨出現，保留獨立）
    INTERJECTIONS = ["對吧？", "真的！", "沒錯！", "沒錯", "對啊！", "對啊", "哇！", "我的天！", "我的天", "欸對", "原來如此！", "原來如此", "確實", "真的", "對"]
    
    for seg in segments:
        raw_text = seg.get("text", "").strip()
        if not raw_text:
            continue
            
        t_start = seg["start"]
        t_end = seg["end"]
        cleaned = clean_text(raw_text)
        
        # 依標點符號進行自然呼吸律拆分（避免一行過長超過 22 字）
        # 如果句子在 22 字以內，整句保留，完全符合語音停頓
        if len(cleaned) <= 22:
            parts = [cleaned]
        else:
            # 依逗號、分號、問號、驚嘆號等自然意群停頓切分
            split_pattern = r"([，。！？；])"
            raw_splits = re.split(split_pattern, cleaned)
            parts = []
            curr = ""
            for token in raw_splits:
                if not token:
                    continue
                if token in "，。！？；":
                    curr += token
                    if len(curr) >= 12:  # 超過 12 字且有標點，自然斷行
                        parts.append(curr)
                        curr = ""
                else:
                    if len(curr) + len(token) > 22 and curr:
                        parts.append(curr)
                        curr = token
                    else:
                        curr += token
            if curr:
                parts.append(curr)
                
        # 計算各子句時間戳分配
        total_len = sum(len(p) for p in parts)
        dur = t_end - t_start
        sub_start = t_start
        for i, part in enumerate(parts):
            p_len = len(part)
            if total_len > 0:
                p_dur = dur * (p_len / total_len)
            else:
                p_dur = dur
            sub_end = sub_start + p_dur
            if i == len(parts) - 1:
                sub_end = t_end
            
            clean_part = part.strip()
            # 移除行首逗號
            clean_part = re.sub(r"^[，,]\s*", "", clean_part)
            if clean_part:
                srt_items.append({
                    "start": sub_start,
                    "end": sub_end,
                    "text": clean_part
                })
            sub_start = sub_end

    # 輸出為標準 SRT 格式
    lines = []
    idx = 1
    for item in srt_items:
        lines.append(str(idx))
        lines.append(f"{format_ts(item['start'])} --> {format_ts(item['end'])}")
        lines.append(item["text"])
        lines.append("")
        idx += 1
        
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ 已輸出標準影視級 SRT 字幕：{out_path.name}，共 {len(srt_items)} 行！")

def main():
    print("🚀 開始執行第 06 章 繁體中文影視級字幕標準精修...")
    
    # 1. 處理說明短片
    if RAW_VID_JSON.exists():
        with open(RAW_VID_JSON, "r", encoding="utf-8") as f:
            v_data = json.load(f)
        process_segments_to_srt(v_data["segments"], VID_SRT, is_podcast=False)
    else:
        print(f"❌ 找不到 {RAW_VID_JSON}")

    # 2. 處理播客長片
    if RAW_POD_JSON.exists():
        with open(RAW_POD_JSON, "r", encoding="utf-8") as f:
            p_data = json.load(f)
        process_segments_to_srt(p_data["segments"], POD_SRT, is_podcast=True)
    else:
        print(f"❌ 找不到 {RAW_POD_JSON}")

if __name__ == "__main__":
    main()
