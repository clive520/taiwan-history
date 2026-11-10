# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 01 章 語音轉錄 (Faster-Whisper medium int8) 與 自然語意 SRT 生成器
主題：粟米、野豬與香料火種——南島先民的煙燻、採集與土地智慧
規範：自然語意斷句、8~24字/行、0錯字破句、臺/臺灣標準繁體
"""
import sys
import os
import json
import time
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

from faster_whisper import WhisperModel

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
FOOD_CH01_DIR = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味"

COMMON_CORRECTIONS = [
    (r"蜻蜓", "清廷"),
    (r"清景", "清廷"),
    (r"輕艇", "清廷"),
    (r"台([灣北市南中東中東南東東南])", r"臺\1"),
    (r"全台", "全臺"),
    (r"在台", "在臺"),
    (r"來台", "來臺"),
    (r"割台", "割臺"),
    (r"治台", "治臺"),
    (r"保台", "保臺"),
    (r"平台", "平臺"),
    (r"開台", "開臺"),
    (r"回台", "回臺"),
    (r"返台", "返臺"),
    (r"犯台", "犯臺"),
    (r"[臺台]灣", "臺灣"),
]

FOOD_CH01_CORRECTIONS = COMMON_CORRECTIONS + [
    # 專有名詞與食材
    (r"吉[拿納南]富", "吉拿富"),
    (r"奇[拿納南]富", "吉拿富"),
    (r"西那富", "吉拿富"),
    (r"[Cc]inavu", "Cinavu"),
    (r"[Qq]avay", "Qavay"),
    (r"阿[拜擺]", "阿拜"),
    (r"阿里[鳳風]鳳", "阿里鳳鳳"),
    (r"假[酸宣]漿", "假酸漿"),
    (r"月[桃挑]", "月桃"),
    (r"馬[告告]", "馬告"),
    (r"麻[告告]", "馬告"),
    (r"馬[搞搞]", "馬告"),
    (r"[Mm]akauy", "Makauy"),
    (r"刺[蔥聰]", "刺蔥"),
    (r"食[茱朱]萸", "食茱萸"),
    (r"鳥不[踏踏]", "鳥不踏"),
    (r"土[肉月]桂", "土肉桂"),
    (r"相[思斯]樹", "相思樹"),
    (r"相[思斯]木", "相思木"),
    (r"九[芎弓]", "九芎"),
    (r"九[芎弓]木", "九芎木"),
    (r"大武[山衫]", "大武山"),
    (r"北大武[山衫]", "北大武山"),
    (r"三地[門們]", "三地門"),
    (r"地磨[兒ㄦ]", "地磨兒"),
    (r"霧[台臺]", "霧臺"),
    (r"隘[寮撩]溪", "隘寮溪"),
    (r"排[灣彎]族", "排灣族"),
    (r"魯[凱豈]族", "魯凱族"),
    (r"泰[雅亞]族", "泰雅族"),
    (r"布[農濃]族", "布農族"),
    (r"卑[南難]族", "卑南族"),
    (r"阿[美眉]族", "阿美族"),
    (r"收[穫獲]祭", "收穫祭"),
    (r"[Mm]asalut", "Masalut"),
    (r"播[種重]祭", "播種祭"),
    (r"分肉[制治]度", "分肉制度"),
    (r"[Pp]atjara", "Patjara"),
    (r"特[權全]肉", "特權肉"),
    (r"[Vv]asa", "Vasa"),
    (r"頭[目木]", "頭目"),
    (r"[Mm]azangiljan", "Mazangiljan"),
    (r"石[板版]屋", "石板屋"),
    (r"石[板版]烤肉", "石板烤肉"),
    (r"[板版]岩", "板岩"),
    (r"[頁頁]岩", "頁岩"),
    (r"[片片]岩", "片岩"),
    (r"火[塘堂]", "火塘"),
    (r"[Qq]atja", "Qatja"),
    (r"冷[燻熏]", "冷燻"),
    (r"煙[燻熏]", "煙燻"),
    (r"[Dd]jalan", "Djalan"),
    (r"[癒愈]創木[酚粉]", "癒創木酚"),
    (r"水分[活和]度", "水分活度"),
    (r"東[番番]記", "東番記"),
    (r"陳[第弟]", "陳第"),
    (r"[裨卑]海[紀記]遊", "裨海紀遊"),
    (r"郁永[河何]", "郁永河"),
    (r"伊能[嘉家]矩", "伊能嘉矩"),
    (r"佐山[融勇]吉", "佐山融吉"),
    (r"[蕃番]族調查[報保]告書", "蕃族調查報告書"),
    (r"雙人[連聯]杯", "雙人連杯"),
    (r"口[嚼嚼]酒", "口嚼酒"),
    (r"樹[豆逗]", "樹豆"),
    (r"野[豬豬]", "野豬"),
    (r"山[豬豬]", "山豬"),
    (r"山[羌羌]", "山羌"),
    (r"水[鹿路]", "水鹿"),
    (r"粟[米米]", "粟米"),
    (r"小米[酒九]", "小米酒"),
    (r"酒[麴麴]", "酒麴"),
    (r"美拉[德得]反應", "美拉德反應"),
    (r"梅[納納]反應", "梅納反應"),
    (r"支[鏈鏈]澱粉", "支鏈澱粉"),
    (r"水溶性多[醣糖]黏質", "水溶性多醣黏質"),
    (r"多[醣糖]黏質", "多醣黏質"),
    (r"[檸檸][檬檬]醛", "檸檬醛"),
    (r"香[葉頁]醇", "香葉醇"),
    (r"芳[樟章]醇", "芳樟醇"),
    (r"肉[桂貴]醛", "肉桂醛"),
    (r"新[臺台]菜", "新臺菜"),
    (r"米其[林琳]", "米其林"),
    (r"大[坌分]坑文化", "大坌坑文化"),
    (r"卑[南難]遺址", "卑南遺址"),
    (r"安和[路陸]遺址", "安和路遺址"),
    (r"沈有[容榮]", "沈有容"),
]

def format_timestamp(seconds: float) -> str:
    total_ms = int(round(seconds * 1000))
    hours = total_ms // 3600000
    rem = total_ms % 3600000
    minutes = rem // 60000
    rem = rem % 60000
    secs = rem // 1000
    ms = rem % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

def clean_text(text: str) -> str:
    t = text.strip()
    t = re.sub(r'[\s\u3000]+', '', t)
    for pat, rep in FOOD_CH01_CORRECTIONS:
        t = re.sub(pat, rep, t)
    t = t.replace('，', '').replace('。', '').replace('、', '').replace('；', '')
    t = t.replace('？', '').replace('！', '').replace('：', '').replace('“', '')
    t = t.replace('”', '').replace('"', '').replace("'", '').replace('（', '')
    t = t.replace('）', '').replace('(', '').replace(')', '').replace('—', '')
    t = t.replace('…', '').replace('～', '').replace('~', '')
    return t

def split_natural_sentences(words, min_chars=8, max_chars=22, max_pause=0.65):
    """
    基於詞級時間戳，依據標點、停頓與字數限制進行自然語意切分
    """
    subtitles = []
    cur_words = []
    
    for i, w in enumerate(words):
        cur_words.append(w)
        cur_text = clean_text("".join([x.word for x in cur_words]))
        
        # 判斷是否需要切分
        need_split = False
        
        # 1. 停頓過長
        if i < len(words) - 1:
            pause = words[i+1].start - w.end
            if pause >= max_pause and len(cur_text) >= min_chars:
                need_split = True
        else:
            need_split = True
            
        # 2. 字數達到上限
        if len(cur_text) >= max_chars:
            need_split = True
            
        # 3. 原始文本含明確停頓標點
        if any(p in w.word for p in ['。', '！', '？', '；', '\n']) and len(cur_text) >= min_chars:
            need_split = True

        if need_split and len(cur_text) > 0:
            start_time = cur_words[0].start
            end_time = cur_words[-1].end
            # 確保結束時間大於開始時間
            if end_time <= start_time:
                end_time = start_time + 0.5
            subtitles.append((start_time, end_time, cur_text))
            cur_words = []
            
    if cur_words:
        cur_text = clean_text("".join([x.word for x in cur_words]))
        if len(cur_text) > 0:
            start_time = cur_words[0].start
            end_time = cur_words[-1].end
            if end_time <= start_time:
                end_time = start_time + 0.5
            subtitles.append((start_time, end_time, cur_text))
            
    return subtitles

def write_srt(subtitles, srt_path: Path):
    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, (st, et, txt) in enumerate(subtitles, start=1):
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(st)} --> {format_timestamp(et)}\n")
            f.write(f"{txt}\n\n")

def transcribe_and_make_srt(model, audio_path: Path, output_srt: Path, prompt_text=""):
    print(f"\n==================================================")
    print(f"🎙️ 正在處理音訊：{audio_path.name}")
    print(f"📦 檔案大小：{audio_path.stat().st_size / (1024*1024):.2f} MB")
    
    t0 = time.time()
    segments, info = model.transcribe(
        str(audio_path),
        language="zh",
        word_timestamps=True,
        initial_prompt=prompt_text,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500)
    )
    
    all_words = []
    print("⏳ 正在轉錄語音片段...")
    for seg in segments:
        if seg.words:
            all_words.extend(seg.words)
            
    print(f"✅ 轉錄完成！共獲取 {len(all_words)} 個詞彙標籤，耗時 {time.time()-t0:.1f} 秒")
    
    # 自然語意斷句
    subs = split_natural_sentences(all_words, min_chars=8, max_chars=22, max_pause=0.6)
    write_srt(subs, output_srt)
    
    lengths = [len(txt) for _, _, txt in subs]
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    print(f"📄 已生成廣播級字幕：{output_srt.name}")
    print(f"📊 總字幕行數：{len(subs)} 行 (最短: {min(lengths) if lengths else 0}, 平均: {avg_len:.1f}, 最長: {max(lengths) if lengths else 0} 字)")
    print("==================================================\n")

if __name__ == "__main__":
    prompt = "粟米, 小米, 排灣族, 泰雅族, 魯凱族, 布農族, 三地門, 北大武山, 隘寮溪, Cinavu, 吉拿富, Qavay, 阿拜, 假酸漿, Lavu, 月桃葉, 馬告, Makauy, 山胡椒, 刺蔥, Tana, 食茱萸, 土肉桂, 相思木, 九芎木, 石板屋, 火塘, 冷燻, Djalan, 癒創木酚, 水分活度, Patjara, 分肉制度, 特權肉, Vasa, Masalut, 收穫祭, 東番記, 陳第, 裨海紀遊, 郁永河, 伊能嘉矩, 佐山融吉, 蕃族調查報告書, 連杯, 口嚼酒."
    
    print("🚀 初始化 Faster-Whisper (medium, int8, cpu_threads=8)...")
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)
    
    # 1. 處理播客音訊
    pod_audio = FOOD_CH01_DIR / "food_ch01_podcast_deepdive.m4a"
    pod_srt = FOOD_CH01_DIR / "第01章_粟米野豬與香料火種_雙人對談.srt"
    if pod_audio.exists():
        transcribe_and_make_srt(model, pod_audio, pod_srt, prompt)
        
    # 2. 處理說明影片 (如果存在)
    vid_file = FOOD_CH01_DIR / "第01章_粟米野豬與香料火種_說明影片.mp4"
    vid_srt = FOOD_CH01_DIR / "第01章_粟米野豬與香料火種_說明影片.srt"
    if vid_file.exists():
        transcribe_and_make_srt(model, vid_file, vid_srt, prompt)
