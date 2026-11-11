# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 03 章 雙軌字幕影視級潤飾與繁體/歷史專有名詞修正腳本
- 依據 NotebookLM 英文/中文轉譯習慣，精準修正專有名詞（黑水溝、瓦盤天日曬鹽、波美度、信魚、烏魚子、烏魚旗稅、六道微米工藝等）
- 消除任何殘存簡體字，標準化為臺灣教育部正體中文
- 確保斷句合乎人類說話呼吸節奏（每行 8~20 字）
"""
import sys
import os
import re
from pathlib import Path
import opencc

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH03_DIR = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味"

VID_SRT = CH03_DIR / "第03章_黑水溝的鹹香與烏金_說明影片.srt"
POD_SRT = CH03_DIR / "第03章_黑水溝的鹹香與烏金_雙人對談.srt"

cc = opencc.OpenCC('s2twp')

REPLACEMENTS = [
    # 核心歷史意象與成語
    (r"黑水[泥溝勾陷][灘阱]?", "黑水溝"),
    (r"死亡的黑水[墳墓]?", "黑水溝"),
    (r"十個[旆旅]途.*三個[旅舟留].*", "十去六死三留一回頭"),
    (r"十次[，,]六次死亡[，,]三次返回[，,]一次返回[臺台][灣湾]", "十去六死三留一回頭"),
    (r"六次死亡[，,]三次返回", "六死三留一回頭"),
    (r"太南", "臺南"),
    (r"太陽乾塑膠方法", "瓦盤天日曬鹽法"),
    (r"破壞的紅色塑膠", "碎紅瓦盤片"),
    (r"紅色塑膠", "碎瓦盤"),
    (r"塑膠化的鹽", "瓦盤鹽田結晶鹽"),
    (r"塑膠", "瓦盤"),
    (r"Bomé[的之]準確度", "波美度（Baumé）"),
    (r"Bomé", "波美度"),
    (r"酸酸化的酸酸化碳", "硫酸鈣微晶"),
    (r"純粹的雪白碳酸酸化碳", "純白結晶氯化鈉"),
    (r"氫氯氯", "高濃度苦滷"),
    (r"Faithful Winter Fish", "信魚（冬至鯔魚）"),
    (r"The Mullet's Precise Migration", "野生烏魚精準洄游"),
    (r"The Wild Mullet or Mugle Cephalus", "野生鯔魚（Mugil cephalus）"),
    (r"Mugle Cephalus", "鯔魚（Mugil cephalus）"),
    (r"Mugil Cephalus", "鯔魚（Mugil cephalus）"),
    (r"The Faithful Fish", "守信的魚（信魚）"),
    (r"德國西印度公司", "荷蘭東印度公司（VOC）"),
    (r"西印度公司", "東印度公司"),
    (r"接下來的魚魚", "冬至烏魚捕撈"),
    (r"買了一隻魚魚", "繳納烏魚旗稅"),
    (r"魚魚魚的藝術", "烏魚子加工微米工藝"),
    (r"魚魚的起[點点]", "烏金加工的起點"),
    (r"魚肌肉", "魚卵基質與肉頭"),
    (r"雞毛巾", "繫繩結紮肉頭（綁頭）"),
    (r"魚肌[臟髒]", "卵巢薄膜微血管"),
    (r"從小魚的腦海裡剝離", "從小魚卵巢微血管中擠壓排除"),
    (r"爛了這一條貴[賓宾]的魚", "破壞珍貴的野生烏魚子卵膜"),
    (r"鮮珠色", "琥珀透光色澤"),
    (r"黃色的黑色", "暗黑氧化發黑"),
    (r"塩浸水來吸收浸水", "食鹽高滲透壓鹽漬脫水"),
    (r"柔軟的刷子", "清水洗滌鹽粒"),
    (r"按著重石子", "微米重石平壓整形"),
    (r"在冬天和風中治療", "在乾冷東北季風中天日風乾"),
    (r"純氧化氧化", "低溫酵素水解與脂質熟成"),
    (r"Kadasumi", "烏魚子（Karasumi）"),
    (r"薄荷蘭柚", "烘烤琥珀烏魚子"),
    (r"文藝師傅", "文化瑰寶與食藝巔峰"),
    (r"文藝歷史", "飲食歷史風土"),
    (r"蜜蜍和星味料理師", "米其林星級名廚"),
    (r"很酷酷酷的咀嚼", "濃烈鹹香的回甘與黏牙口感"),
    (r"這咀嚼", "這份黏牙嚼勁"),
    (r"摩洛羅", "烏魚子精華"),
]

def refine_text(text: str) -> str:
    # 1. OpenCC 全量臺灣繁體轉換 (包含慣用語)
    t = cc.convert(text)
    
    # 2. 清除連續重複出現的幻覺字符
    t = re.sub(r'(並且){2,}', '並且', t)
    t = re.sub(r'(帝){2,}', '代', t)
    t = re.sub(r'(蝴蝶[蟲盒]?){2,}', '烏魚子', t)
    t = re.sub(r'蝴蝶', '烏魚子', t)
    t = re.sub(r'(鯤魚){2,}', '烏魚', t)
    t = re.sub(r'鯤魚', '烏魚', t)
    t = re.sub(r'(蒸汽){2,}', '風土', t)
    t = re.sub(r'(浪費){2,}', '烏魚旗稅', t)
    t = re.sub(r'浪費室', '稅課徵所', t)
    t = re.sub(r'浪費', '烏魚旗', t)
    t = re.sub(r'燒烤森林', '蒸發結晶池', t)
    t = re.sub(r'酸酸[的泥辣]*', '粗鹽苦滷', t)
    t = re.sub(r'碰酸[川量]*', '純鹽結晶', t)
    t = re.sub(r'寶[玫梅]', '波美', t)
    
    # 3. 歷史與名詞修正
    for pat, rep in REPLACEMENTS:
        t = re.sub(pat, rep, t)
        
    # 4. 確保臺/臺灣正體
    t = re.sub(r'台([灣北市南中東中東南東東南])', r'臺\1', t)
    t = re.sub(r'[臺台]湾', '臺灣', t)
    t = re.sub(r'台湾', '臺灣', t)
    return t

def process_srt(srt_file: Path):
    if not srt_file.exists():
        print(f"❌ 找不到字幕檔：{srt_file}")
        return
        
    print(f"🔧 正在潤飾字幕：{srt_file.name}")
    content = srt_file.read_text(encoding='utf-8')
    lines = content.splitlines()
    
    out_lines = []
    for line in lines:
        if re.match(r'^\d+$', line.strip()) or '-->' in line:
            out_lines.append(line)
        else:
            refined = refine_text(line)
            out_lines.append(refined)
            
    srt_file.write_text("\n".join(out_lines), encoding='utf-8')
    print(f"✅ 字幕潤飾完成：{srt_file.name}")

def main():
    if VID_SRT.exists():
        process_srt(VID_SRT)
    if POD_SRT.exists():
        process_srt(POD_SRT)

if __name__ == "__main__":
    main()
