# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 03 章 說明影片 語音轉錄與影視級自然語意 SRT 生成腳本
"""
import sys
import os
import json
import time
import re
from pathlib import Path
import jieba

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

from faster_whisper import WhisperModel

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH03_DIR = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味"
VID_FILE = CH03_DIR / "第03章_黑水溝的鹹香與烏金_說明影片.mp4"
RAW_JSON = CH03_DIR / "第03章_說明影片_raw_words.json"
OUT_SRT = CH03_DIR / "第03章_黑水溝的鹹香與烏金_說明影片.srt"

PROMPT_TEXT = (
    "黑水溝, 澎湖水道, 臺灣海峽, 烏金, 烏魚子, 鯔魚, Mugil cephalus, 信魚, 正頭烏, 回頭烏, "
    "陳永華, 瀨口鹽田, 瓦盤鹽田, 瓦盤, 土盤, 天日曬鹽, 淋滷, 滷缸, 飽和滷水, 波美度, "
    "氯化鈉, 苦滷, 硫酸鈣, 氯化鎂, 烏魚旗, 烏魚旗稅, 荷蘭東印度公司, VOC, "
    "熱蘭遮城日記, 東番記, 陳第, 裨海紀遊, 郁永河, 臺灣府志, 高拱乾, 范咸, "
    "安平港, 魍港, 布袋, 七股鹽田, 北門鹽田, 洲北場, 洲南場, 肉頭, 綁頭, 排血, "
    "鹽漬, 脫水, 板壓, 壓石, 天日曝曬, 東北季風, 琥珀色, 黏牙, 谷氨酸, 卵磷脂, "
    "鹹水泡飯, 鹹魚乾, 地瓜籤, 羅漢腳, 討海人"
)

CUSTOM_WORDS = [
    "黑水溝", "澎湖水道", "臺灣海峽", "烏金", "烏魚子", "鯔魚", "信魚", "正頭烏", "回頭烏",
    "陳永華", "瀨口鹽田", "瀨口", "瓦盤鹽田", "瓦盤", "土盤", "天日曬鹽", "淋滷", "滷缸",
    "飽和滷水", "波美度", "氯化鈉", "苦滷", "硫酸鈣", "氯化鎂", "烏魚旗", "烏魚旗稅",
    "荷蘭東印度公司", "VOC", "熱蘭遮城日記", "東番記", "陳第", "裨海紀遊", "郁永河", "臺灣府志",
    "高拱乾", "范咸", "安平港", "魍港", "布袋", "七股鹽田", "北門鹽田", "洲北場", "洲南場",
    "肉頭", "綁頭", "排血", "鹽漬", "板壓", "壓石", "天日風乾", "東北季風", "琥珀色",
    "黏牙", "谷氨酸", "卵磷脂", "鹹水泡飯", "鹹魚乾", "地瓜籤", "羅漢腳", "討海人",
    "十去六死三回頭", "水溶性", "滲透壓", "水分活度", "結締組織", "凝膠基質"
]
for w in CUSTOM_WORDS:
    jieba.add_word(w)

CORRECTIONS = [
    (r"台([灣北市南中東中東南東東南])", r"臺\1"),
    (r"[臺台]灣", "臺灣"),
    (r"黑水[溝勾]", "黑水溝"),
    (r"烏[金斤]", "烏金"),
    (r"烏[魚於][子仔]", "烏魚子"),
    (r"陳永[華花]", "陳永華"),
    (r"[瀨賴]口", "瀨口"),
    (r"瓦[盤盤]", "瓦盤"),
    (r"天日[曬曬]鹽", "天日曬鹽"),
    (r"信[魚於]", "信魚"),
    (r"正頭[烏鳥]", "正頭烏"),
    (r"回頭[烏鳥]", "回頭烏"),
    (r"波美[度渡]", "波美度"),
    (r"苦[滷鹵]", "苦滷"),
    (r"烏[魚於]旗", "烏魚旗"),
    (r"熱蘭[遮折周週]城?", "熱蘭遮城"),
    (r"東[番番]記", "《東番記》"),
    (r"陳[第弟]", "陳第"),
    (r"裨海[紀記]遊", "《裨海紀遊》"),
    (r"郁永[河何]", "郁永河"),
    (r"鹹水泡[飯反]", "鹹水泡飯"),
    (r"地瓜[籤簽]", "地瓜籤"),
    (r"羅漢[腳角]", "羅漢腳"),
    (r"討海[人仁]", "討海人"),
    (r"琥[珀泊]色", "琥珀色"),
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

def clean_text(t: str) -> str:
    for pat, rep in CORRECTIONS:
        t = re.sub(pat, rep, t)
    t = t.replace('?', '？').replace('!', '！').replace(',', '，')
    t = re.sub(r'^[，。！？、；：\s]+', '', t)
    t = re.sub(r'[，。！？、；：\s]+$', '', t)
    return t

def split_long_text_by_jieba(text: str, max_len=15):
    words = list(jieba.cut(text))
    lines = []
    cur = []
    for w in words:
        if sum(len(x) for x in cur) + len(w) > max_len and len(cur) > 0:
            lines.append("".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append("".join(cur))
    return lines

def transcribe_video():
    if not VID_FILE.exists():
        print(f"❌ 找不到影片檔案：{VID_FILE}")
        return False
        
    print("🚀 初始化 Faster-Whisper (medium, int8, cpu_threads=8)...")
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)
    
    print(f"🎙️ 開始轉錄說明影片：{VID_FILE.name}")
    t0 = time.time()
    segments, info = model.transcribe(
        str(VID_FILE),
        language="zh",
        initial_prompt=PROMPT_TEXT,
        word_timestamps=True,
        beam_size=1,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=450)
    )
    
    words_data = []
    seg_list = []
    for seg in segments:
        seg_list.append({
            'start': seg.start,
            'end': seg.end,
            'text': seg.text
        })
        if seg.words:
            for w in seg.words:
                words_data.append({
                    'word': w.word,
                    'start': w.start,
                    'end': w.end
                })
                
    with open(RAW_JSON, 'w', encoding='utf-8') as f:
        json.dump({'segments': seg_list, 'words': words_data}, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 轉錄完成！共獲取 {len(words_data)} 個詞彙標籤，耗時 {time.time()-t0:.1f} 秒")
    
    # Jieba 自然語意斷句（說明短片特化：8~16字，平均11~13字）
    subtitles = []
    for seg in seg_list:
        text = seg['text'].strip()
        cleaned = clean_text(text)
        if not cleaned:
            continue
            
        if len(cleaned) <= 16:
            subtitles.append((seg['start'], seg['end'], cleaned))
        else:
            parts = re.split(r'([ ？!！，,])', text)
            chunks = []
            cur_c = ""
            for p in parts:
                if p in [' ', '？', '!', '！', '，', ',']:
                    cur_c += p
                    if len(cur_c.strip()) >= 6:
                        chunks.append(cur_c.strip())
                        cur_c = ""
                else:
                    cur_c += p
            if cur_c.strip():
                chunks.append(cur_c.strip())
                
            refined_chunks = []
            for c in chunks:
                c_clean = clean_text(c)
                if len(c_clean) > 16:
                    sub_lines = split_long_text_by_jieba(c_clean, max_len=14)
                    refined_chunks.extend(sub_lines)
                else:
                    refined_chunks.append(c_clean)
                    
            total_len = sum(len(c) for c in refined_chunks)
            dur = seg['end'] - seg['start']
            cur_st = seg['start']
            for c in refined_chunks:
                c_clean = clean_text(c)
                if not c_clean:
                    continue
                c_dur = dur * (len(c_clean) / total_len)
                cur_et = cur_st + c_dur
                subtitles.append((cur_st, cur_et, c_clean))
                cur_st = cur_et
                
    # 平滑合併短行 (< 6 字)
    merged = []
    i = 0
    while i < len(subtitles):
        st, et, txt = subtitles[i]
        if i < len(subtitles) - 1:
            nst, net, ntxt = subtitles[i+1]
            pause = nst - et
            if len(txt) <= 5 and pause < 0.35 and (len(txt) + len(ntxt) <= 16):
                txt = txt + " " + ntxt
                et = net
                i += 1
            elif len(ntxt) <= 5 and pause < 0.35 and (len(txt) + len(ntxt) <= 16):
                txt = txt + " " + ntxt
                et = net
                i += 1
        merged.append((st, et, clean_text(txt)))
        i += 1
        
    with open(OUT_SRT, 'w', encoding='utf-8') as f:
        for idx, (st, et, txt) in enumerate(merged, 1):
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(st)} --> {format_timestamp(et)}\n")
            f.write(f"{txt}\n\n")
            
    lengths = [len(txt) for _, _, txt in merged]
    print(f"🎉 說明短片影視級字幕生成完成！")
    print(f"📄 輸出檔案：{OUT_SRT.name}")
    print(f"📊 總字幕行數：{len(merged)} 行 (最短: {min(lengths)}, 平均: {sum(lengths)/len(lengths):.1f}, 最長: {max(lengths)} 字)")
    return True

if __name__ == "__main__":
    transcribe_video()
