# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 03 章 播客深度對談 語音轉錄與影視級自然語意 SRT 生成腳本
主題：黑水溝的鹹香與烏金——沿海鹽田、討海人補給與烏魚子傳奇
規範：遵循《影視級字幕製作標準作業程序_SOP.md》
- 雙人對談特化斷句策略：保護對話輪替，吐氣語意群（8~20字/行），自然停頓換行
- 0 錯字破句、臺/臺灣標準繁體
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
AUDIO_FILE = CH03_DIR / "food_ch03_podcast_deepdive.m4a"
RAW_JSON = CH03_DIR / "第03章_播客深度對談_raw_words.json"
OUT_SRT = CH03_DIR / "第03章_黑水溝的鹹香與烏金_雙人對談.srt"

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
    # 地名與地理
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
    
    # 歷史人物與典籍
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
    
    # 討海人與底層飲食
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

def clean_text(t: str) -> str:
    for pat, rep in FOOD_CH03_CORRECTIONS:
        t = re.sub(pat, rep, t)
    t = t.replace('?', '？').replace('!', '！').replace(',', '，')
    t = re.sub(r'^[，。！？、；：\s]+', '', t)
    t = re.sub(r'[，。！？、；：\s]+$', '', t)
    return t

def split_natural_dialogue_units(words, max_chars=18, min_chars=6, pause_thresh=0.5):
    """
    雙人播客專屬：依據自然停頓、對話轉折與詞級意群進行智慧切分
    """
    cues = []
    current_tokens = []
    
    def flush():
        nonlocal current_tokens
        if not current_tokens:
            return
        text = "".join(tok["word"] for tok in current_tokens)
        cleaned = clean_text(text)
        if cleaned:
            cues.append({
                "start": current_tokens[0]["start"],
                "end": current_tokens[-1]["end"],
                "text": cleaned
            })
        current_tokens = []

    for i, tok in enumerate(words):
        w_text = tok["word"].strip()
        if not w_text:
            continue
            
        # 若與前一詞停頓過大，表示自然呼吸換氣或換人發話
        if current_tokens:
            prev_end = current_tokens[-1]["end"]
            curr_start = tok["start"]
            gap = curr_start - prev_end
            
            cur_len = sum(len(t["word"].strip()) for t in current_tokens)
            
            # 條件 1: 停頓明顯 (> 0.5s) 且已累積基本長度
            if gap >= pause_thresh and cur_len >= min_chars:
                flush()
            # 條件 2: 遇到強語氣停頓標點（句號、問號、感嘆號）
            elif any(p in current_tokens[-1]["word"] for p in ["。", "！", "？", "\n"]):
                flush()
            # 條件 3: 當前詞是明顯的發話轉折詞（例如「沒錯」、「對」、「其實」、「而且」、「那麼」）且前句長度已足
            elif w_text in ["沒錯", "對", "其實", "而且", "那麼", "確實", "也就是說", "你看"] and cur_len >= 8:
                flush()
            # 條件 4: 字數達到上限且處於停頓標點或詞界
            elif cur_len + len(w_text) > max_chars:
                flush()

        current_tokens.append(tok)
        
    flush()
    return cues

def main():
    if not AUDIO_FILE.exists():
        print(f"找不到音訊檔: {AUDIO_FILE}")
        return

    print(f"=== 開始轉錄第 03 章播客音訊: {AUDIO_FILE.name} ===")
    t0 = time.time()
    
    # 優先使用 GPU，若不可用降階至 CPU
    try:
        model = WhisperModel("large-v3", device="cuda", compute_type="float16")
        print("Using CUDA device (float16)")
    except Exception as e:
        print(f"CUDA unavailable ({e}), using CPU (int8)")
        model = WhisperModel("large-v3", device="cpu", compute_type="int8")

    segments, info = model.transcribe(
        str(AUDIO_FILE),
        beam_size=1,
        language="zh",
        initial_prompt=PROMPT_TEXT,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=400)
    )

    all_words = []
    print("正在解碼語音流與詞級時間戳...")
    for seg in segments:
        if seg.words:
            for w in seg.words:
                all_words.append({
                    "start": w.start,
                    "end": w.end,
                    "word": w.word
                })

    with open(RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(all_words, f, ensure_ascii=False, indent=2)
    print(f"詞級時間戳已儲存至: {RAW_JSON} (共 {len(all_words)} 詞)")

    # 執行自然對談意群分段
    cues = split_natural_dialogue_units(all_words, max_chars=18, min_chars=6, pause_thresh=0.45)

    # 輸出 SRT
    with open(OUT_SRT, "w", encoding="utf-8") as f:
        for idx, cue in enumerate(cues, 1):
            s_time = format_timestamp(cue["start"])
            e_time = format_timestamp(cue["end"])
            f.write(f"{idx}\n{s_time} --> {e_time}\n{cue['text']}\n\n")

    print(f"SRT 字幕生成完成: {OUT_SRT} (共 {len(cues)} 條字幕)")
    print(f"轉錄耗時: {time.time() - t0:.1f} 秒")

if __name__ == "__main__":
    main()
