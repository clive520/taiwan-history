# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 03 章 雙軌影音統一語音轉錄與影視級自然語意 SRT 生成腳本
主題：黑水溝的鹹香與烏金——沿海鹽田、討海人補給與烏魚子傳奇
規範：遵循《影視級字幕製作標準作業程序_SOP.md》
- WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)
- beam_size=5, condition_on_previous_text=False (杜絕死循環)
- 即時打印轉錄進度
- 說明片與播客長片雙軌特化斷句策略 (0 破詞破句、自然呼吸群)
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

import jieba
from faster_whisper import WhisperModel

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH03_DIR = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味"

VID_FILE = CH03_DIR / "第03章_黑水溝的鹹香與烏金_說明影片.mp4"
VID_SRT = CH03_DIR / "第03章_黑水溝的鹹香與烏金_說明影片.srt"

POD_FILE = CH03_DIR / "food_ch03_podcast_deepdive.m4a"
POD_SRT = CH03_DIR / "第03章_黑水溝的鹹香與烏金_雙人對談.srt"

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

FOOD_CH03_CORRECTIONS = COMMON_CORRECTIONS + [
    # 地理與地名
    (r"黑水[溝勾]", "黑水溝"),
    (r"澎湖水道", "澎湖水道"),
    (r"臺江內海", "臺江內海"),
    (r"安平港", "安平港"),
    (r"[魍芒]港", "魍港"),
    (r"布袋港?", "布袋"),
    (r"七股鹽田", "七股鹽田"),
    (r"北門鹽田", "北門鹽田"),
    (r"[瀨賴]口[鹽田]?", "瀨口鹽田"),
    (r"[瀨賴]口", "瀨口"),
    (r"洲北場", "洲北場"),
    (r"洲南場", "洲南場"),
    
    # 歷史人物與文獻
    (r"陳永[華花]", "陳永華"),
    (r"鄭成功", "鄭成功"),
    (r"鄭經", "鄭經"),
    (r"東[番番]記", "《東番記》"),
    (r"陳[第弟]", "陳第"),
    (r"裨海[紀記]遊", "《裨海紀遊》"),
    (r"郁永[河何]", "郁永河"),
    (r"熱蘭遮城日記", "《熱蘭遮城日記》"),
    (r"熱蘭[遮折]城", "熱蘭遮城"),
    (r"臺灣府志", "《臺灣府志》"),
    (r"高拱[乾幹]", "高拱乾"),
    (r"范[咸鹹]", "范咸"),
    
    # 制度與稅賦
    (r"烏[魚於]旗[稅水]?", "烏魚旗稅"),
    (r"烏[魚於]旗", "烏魚旗"),
    (r"荷蘭東印度公司", "荷蘭東印度公司"),
    (r"荷[蘭西]時代", "荷蘭時代"),
    
    # 魚類與烏魚子工藝
    (r"烏[金斤]", "烏金"),
    (r"烏[魚於][子仔]", "烏魚子"),
    (r"烏[魚於]", "烏魚"),
    (r"[鯔鲻]魚", "鯔魚"),
    (r"信[魚於]", "信魚"),
    (r"正頭[烏鳥]", "正頭烏"),
    (r"回頭[烏鳥]", "回頭烏"),
    (r"肉頭", "肉頭"),
    (r"綁頭", "綁頭"),
    (r"排血", "排血"),
    (r"鹽漬", "鹽漬"),
    (r"板壓", "板壓"),
    (r"壓石", "壓石"),
    (r"天日[曬曬]鹽", "天日曬鹽"),
    (r"天日[風曝]曬", "天日曝曬"),
    (r"東北季風", "東北季風"),
    (r"琥[珀泊]色", "琥珀色"),
    (r"黏牙", "黏牙"),
    (r"谷[氨胺]酸", "谷氨酸"),
    (r"卵磷脂", "卵磷脂"),
    (r"油[脂酯]", "油脂"),
    
    # 鹽田技術
    (r"瓦[盤盤]鹽田", "瓦盤鹽田"),
    (r"瓦[盤盤]", "瓦盤"),
    (r"土[盤盤]鹽田", "土盤鹽田"),
    (r"土[盤盤]", "土盤"),
    (r"淋[滷鹵]", "淋滷"),
    (r"[滷鹵]缸", "滷缸"),
    (r"飽和[滷鹵]水", "飽和滷水"),
    (r"[滷鹵]水", "滷水"),
    (r"波美[度渡]", "波美度"),
    (r"氯化[鈉納]", "氯化鈉"),
    (r"苦[滷鹵]", "苦滷"),
    (r"硫酸[鈣丐]", "硫酸鈣"),
    (r"氯化[鎂美]", "氯化鎂"),
    
    # 討海人與生活
    (r"鹹水泡[飯反]", "鹹水泡飯"),
    (r"鹹[魚於]乾", "鹹魚乾"),
    (r"地瓜[籤簽]", "地瓜籤"),
    (r"羅漢[腳角]", "羅漢腳"),
    (r"討海[人仁]", "討海人"),
    (r"十去六死三回頭", "十去六死三回頭"),
]

PROMPT_TEXT = (
    "黑水溝, 澎湖水道, 臺灣海峽, 烏金, 烏魚子, 鯔魚, Mugil cephalus, 信魚, 正頭烏, 回頭烏, "
    "陳永華, 瀨口鹽田, 瓦盤鹽田, 瓦盤, 土盤, 天日曬鹽, 淋滷, 滷缸, 飽和滷水, 波美度, "
    "氯化鈉, 苦滷, 硫酸鈣, 氯化鎂, 烏魚旗, 烏魚旗稅, 荷蘭東印度公司, VOC, "
    "熱蘭遮城日記, 東番記, 陳第, 裨海紀遊, 郁永河, 臺灣府志, 高拱乾, 范咸, "
    "安平港, 魍港, 布袋, 七股鹽田, 北門鹽田, 洲北場, 洲南場, 肉頭, 綁頭, 排血, "
    "鹽漬, 脫水, 板壓, 壓石, 天日曝曬, 東北季風, 琥珀色, 黏牙, 谷氨酸, 卵磷脂, "
    "鹹水泡飯, 鹹魚乾, 地瓜籤, 羅漢腳, 討海人, 十去六死三回頭"
)

CUSTOM_WORDS = [
    "黑水溝", "澎湖水道", "臺灣海峽", "烏金", "烏魚子", "鯔魚", "信魚", "正頭烏", "回頭烏",
    "陳永華", "瀨口鹽田", "瀨口", "瓦盤鹽田", "瓦盤", "土盤", "天日曬鹽", "淋滷", "滷缸",
    "飽和滷水", "波美度", "氯化鈉", "苦滷", "硫酸鈣", "氯化鎂", "烏魚旗", "烏魚旗稅",
    "荷蘭東印度公司", "VOC", "熱蘭遮城日記", "東番記", "陳第", "裨海紀遊", "郁永河", "臺灣府志",
    "高拱乾", "范咸", "安平港", "魍港", "布袋", "七股鹽田", "北門鹽田", "洲北場", "洲南場",
    "肉頭", "綁頭", "排血", "鹽漬", "板壓", "壓石", "天日曝曬", "天日風乾", "東北季風",
    "琥珀色", "黏牙", "谷氨酸", "卵磷脂", "鹹水泡飯", "鹹魚乾", "地瓜籤", "羅漢腳", "討海人",
    "十去六死三回頭", "水溶性", "滲透壓", "水分活度", "結締組織", "凝膠基質", "沒錯", "確實"
]
for w in CUSTOM_WORDS:
    jieba.add_word(w)

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
    for pat, rep in FOOD_CH03_CORRECTIONS:
        t = re.sub(pat, rep, t)
    t = re.sub(r'[，。！？、；：\s]+$', '', t)
    t = re.sub(r'^[，。！？、；：\s]+', '', t)
    t = t.replace('”', '').replace('"', '').replace("'", '').replace('（', '')
    t = t.replace('）', '').replace('(', '').replace(')', '').replace('—', '')
    t = t.replace('…', '').replace('～', '').replace('~', '')
    return t

def split_natural_sentences(words, min_chars=6, max_chars=18, max_pause=0.55):
    """
    通用自然語意斷句（保護自然吐氣意群、0破字破詞）
    """
    subtitles = []
    cur_words = []
    
    for i, w in enumerate(words):
        cur_words.append(w)
        cur_text = clean_text("".join([x.word for x in cur_words]))
        
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

def process_media(model, media_path: Path, srt_path: Path, min_chars=6, max_chars=18, max_pause=0.55):
    print(f"\n" + "="*60)
    print(f"🎙️ 正在處理：{media_path.name}")
    print(f"📦 檔案大小：{media_path.stat().st_size / (1024*1024):.2f} MB")
    print("="*60)
    
    t0 = time.time()
    segments, info = model.transcribe(
        str(media_path),
        language="zh",
        word_timestamps=True,
        initial_prompt=PROMPT_TEXT,
        beam_size=5,
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=450)
    )
    
    print(f"[*] 音訊時長：{info.duration:.1f} 秒 (~{info.duration/60:.1f} 分鐘)")
    all_words = []
    seg_idx = 0
    for seg in segments:
        seg_idx += 1
        s_txt = seg.text.strip()
        print(f"  [{format_timestamp(seg.start)} -> {format_timestamp(seg.end)}] {s_txt}", flush=True)
        if seg.words:
            all_words.extend(seg.words)
            
    print(f"\n✅ 語音解碼完成！共獲取 {len(all_words)} 個詞彙標籤，耗時 {time.time()-t0:.1f} 秒")
    
    # 自然語意斷句
    subs = split_natural_sentences(all_words, min_chars=min_chars, max_chars=max_chars, max_pause=max_pause)
    write_srt(subs, srt_path)
    
    lengths = [len(txt) for _, _, txt in subs]
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    print(f"📄 已生成廣播級字幕：{srt_path.name}")
    print(f"📊 總字幕行數：{len(subs)} 行 (最短: {min(lengths) if lengths else 0}, 平均: {avg_len:.1f}, 最長: {max(lengths) if lengths else 0} 字)")
    print("="*60 + "\n")

def main():
    print("🚀 初始化 Faster-Whisper (medium, int8, cpu_threads=8)...")
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)
    
    # 1. 處理說明短片 (約 3~4 分鐘)
    if VID_FILE.exists():
        process_media(model, VID_FILE, VID_SRT, min_chars=6, max_chars=18, max_pause=0.55)
    else:
        print(f"❌ 找不到說明影片檔案：{VID_FILE}")

    # 2. 處理播客長片
    if POD_FILE.exists():
        process_media(model, POD_FILE, POD_SRT, min_chars=8, max_chars=20, max_pause=0.60)
    else:
        print(f"❌ 找不到播客音訊檔案：{POD_FILE}")

if __name__ == "__main__":
    main()
