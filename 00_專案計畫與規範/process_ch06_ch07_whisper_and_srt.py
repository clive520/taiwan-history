# -*- coding: utf-8 -*-
"""
第 06 章 與 第 07 章 語音轉錄 (Faster-Whisper) 與 自然語意 SRT 生成器
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

CH06_DIR = BASE_DIR / "02_大航海時代與荷西競逐"
CH07_DIR = BASE_DIR / "03_明鄭東寧與海上孤忠"

COMMON_CORRECTIONS = [
    (r"蜻蜓", "清廷"),
    (r"清景", "清廷"),
    (r"輕艇", "清廷"),
    (r"青菜大臣", "欽差大臣"),
    (r"秦才大臣", "欽差大臣"),
    (r"應抗", "硬抗"),
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

CH06_CORRECTIONS = COMMON_CORRECTIONS + [
    (r"過懷一", "郭懷一"),
    (r"郭懷[億亦義]", "郭懷一"),
    (r"郭懷[二貳]", "郭懷二"),
    (r"油[車東]行", "油車行"),
    (r"二[曾層]行溪", "二層行溪"),
    (r"二重溪", "二層行溪"),
    (r"歐[汪灣]平原", "歐汪平原"),
    (r"普羅[民名]遮城", "普羅民遮城"),
    (r"普羅民[折遮]城", "普羅民遮城"),
    (r"熱[蘭藍]遮城", "熱蘭遮城"),
    (r"熱蘭[折遮]城", "熱蘭遮城"),
    (r"費爾[勃博伯]格", "費爾勃格"),
    (r"揆[一億]", "揆一"),
    (r"奎一", "揆一"),
    (r"西[拉啦]雅", "西拉雅"),
    (r"西拉雅[足族]", "西拉雅族"),
    (r"王[田天]", "王田"),
    (r"王田[體提]制", "王田體制"),
    (r"人頭[稅水]", "人頭稅"),
    (r"贌[社射]", "贌社"),
    (r"贌[商傷]", "贌商"),
    (r"撲社", "贌社"),
    (r"樸社", "贌社"),
    (r"新港[社射]", "新港社"),
    (r"麻豆[社射]", "麻豆社"),
    (r"蕭[壠壟隴]社", "蕭壠社"),
    (r"目加[溜留]灣社", "目加溜灣社"),
    (r"咬[𠺕溜][吧巴]", "咬𠺕吧"),
    (r"巴[達打]維亞", "巴達維亞"),
    (r"荷蘭東印度[公司共司]", "荷蘭東印度公司"),
    (r"火[繩勝]槍", "火繩槍"),
    (r"赤[崁嵌]", "赤崁"),
    (r"大鹿[港剛]", "大鹿港"),
]

CH07_CORRECTIONS = COMMON_CORRECTIONS + [
    (r"鄭[成承]功", "鄭成功"),
    (r"國[姓勝]爺", "國姓爺"),
    (r"延平[王汪]", "延平王"),
    (r"何[斌賓]", "何斌"),
    (r"鹿[耳爾]門", "鹿耳門"),
    (r"北[線線]尾", "北線尾"),
    (r"臺江[內外]海", "臺江內海"),
    (r"熱[蘭藍]遮城", "熱蘭遮城"),
    (r"熱蘭[折遮]城", "熱蘭遮城"),
    (r"普羅[民名]遮城", "普羅民遮城"),
    (r"烏特[勒勒]支", "烏特勒支"),
    (r"烏特勒支[碉堡雕寶]", "烏特勒支碉堡"),
    (r"揆[一億]", "揆一"),
    (r"奎一", "揆一"),
    (r"拔[克客]西", "拔克西"),
    (r"拔隊[長張]", "拔隊長"),
    (r"馬[德得]夫", "馬德夫"),
    (r"貝[德得]爾", "貝德爾"),
    (r"赫克[托託]號", "赫克托號"),
    (r"斯[霍獲]達號", "斯霍達號"),
    (r"陳[澤則]", "陳澤"),
    (r"全[臺台]大[屯純]墾", "全臺大屯墾"),
    (r"營[盤盤]田", "營盤田"),
    (r"天[興新]縣", "天興縣"),
    (r"萬[年連]縣", "萬年縣"),
    (r"東[都督]明京", "東都明京"),
    (r"永[曆歷]", "永曆"),
    (r"遷[界借]令", "遷界令"),
    (r"海[禁進]", "海禁"),
    (r"巴[達打]維亞", "巴達維亞"),
    (r"荷蘭東印度[公司共司]", "荷蘭東印度公司"),
    (r"赤[崁嵌]", "赤崁"),
]

CH06_PROMPT = (
    "臺灣史, 郭懷一, 郭懷二, 普羅民遮城, 熱蘭遮城, 費爾勃格, 揆一, 油車行, 赤崁, 大鹿港, "
    "歐汪平原, 二層行溪, 笨港, 麻豆社, 新港社, 蕭壠社, 目加溜灣社, 西拉雅族, 人頭稅, 王田, "
    "王田體制, 甲數, 贌社, 贌社制度, 贌商, 鹿皮貿易, 荷蘭東印度公司, VOC, 德商, 咬𠺕吧, "
    "巴達維亞, 竹竿綁鐮刀, 火繩槍, 拔克西, 何斌, 鄭成功, 鄭芝龍"
)

CH07_PROMPT = (
    "臺灣史, 鄭成功, 國姓爺, 延平王, 朱成功, 揆一, 何斌, 鹿耳門, 鹿耳門水道, 北線尾, "
    "北線尾沙洲, 臺江內海, 臺江海戰, 安平, 臺灣城, 熱蘭遮城, 普羅民遮城, 赤崁樓, 拔克西, "
    "拔隊長, 馬德夫, 貝德爾, 赫克托號, 斯霍達號, 瑪莉亞號, 烏特勒支碉堡, 荷蘭東印度公司, "
    "VOC, 巴達維亞, 雅加達, 全臺大屯墾, 軍屯, 營盤田, 前鎮, 後勁, 左營, 仁武, 柳營, "
    "新營, 萬年縣, 天興縣, 東都明京, 永曆, 隆武, 滿清, 海禁, 遷界令"
)

def format_timestamp(seconds: float) -> str:
    td = max(0.0, seconds)
    hrs = int(td // 3600)
    mins = int((td % 3600) // 60)
    secs = int(td % 60)
    millis = int(round((td - int(td)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def count_cjk(s: str) -> int:
    return len(re.findall(r'[\u4e00-\u9fff\w]', s))

def apply_corrections(text: str, corrections) -> str:
    t = text
    for pat, rep in corrections:
        t = re.sub(pat, rep, t)
    return t

def clean_punctuation(text: str) -> str:
    t = text.strip()
    t = re.sub(r',\s*', '，', t)
    t = re.sub(r'^[，。！？、；：,!?;:]+', '', t)
    t = re.sub(r'[，。、；;,\.]+$', '', t)
    return t

def process_segments_semantically(segments, corrections):
    merged_subs = []
    cur = None
    
    for s in segments:
        raw_t = s.get('text', '').strip()
        if not raw_t:
            continue
            
        corr_t = apply_corrections(raw_t, corrections)
        t = clean_punctuation(corr_t)
        if not t:
            continue
            
        start = s['start']
        end = s['end']
        
        if cur is None:
            cur = {'start': start, 'end': end, 'text': t}
            continue
            
        gap = start - cur['end']
        cur_len = count_cjk(cur['text'])
        new_len = count_cjk(t)
        
        should_merge = False
        if cur_len + new_len <= 22:
            no_strong_end = not cur['text'].endswith(('？', '！', '?', '!'))
            if no_strong_end:
                if (cur_len <= 4 or new_len <= 4) and gap < 0.40:
                    should_merge = True
                elif (cur_len + new_len <= 16) and gap < 0.25:
                    should_merge = True
                    
        if should_merge:
            if not cur['text'][-1] in '，、：:':
                sep = '，' if cur_len >= 6 and new_len >= 5 else ' '
            else:
                sep = ''
            cur['text'] = clean_punctuation(cur['text'] + sep + t)
            cur['end'] = end
        else:
            merged_subs.append(cur)
            cur = {'start': start, 'end': end, 'text': t}
            
    if cur:
        merged_subs.append(cur)
        
    for i in range(len(merged_subs) - 1):
        if merged_subs[i]['end'] > merged_subs[i+1]['start']:
            merged_subs[i]['end'] = merged_subs[i+1]['start']
            
    return merged_subs

def transcribe_and_make_srt(model, media_path, json_path, srt_path, prompt, corrections):
    print(f"\n" + "="*70)
    print(f"🎙️ 開始轉錄: {Path(media_path).name}")
    print(f"="*70)
    start_t = time.time()
    
    segments, info = model.transcribe(
        str(media_path),
        language="zh",
        initial_prompt=prompt,
        word_timestamps=True,
        beam_size=1,
        vad_filter=True
    )
    
    print(f"[*] 音訊總長度: {info.duration:.1f} 秒 (~{info.duration/60:.1f} 分鐘)")
    print(f"[*] 辨識語言: {info.language}")
    
    words_list = []
    full_text = []
    segment_list = []
    
    for segment in segments:
        seg_data = {
            "id": segment.id,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        }
        segment_list.append(seg_data)
        full_text.append(segment.text)
        
        if segment.words:
            for w in segment.words:
                words_list.append({
                    "word": w.word,
                    "start": w.start,
                    "end": w.end,
                    "probability": w.probability
                })
                
    elapsed = time.time() - start_t
    print(f"[*] 轉錄完成！耗時: {elapsed:.1f} 秒")
    print(f"[*] 總句數: {len(segment_list)}, 總字數: {len(words_list)}")
    
    # 儲存 JSON
    result_data = {
        "text": "".join(full_text),
        "segments": segment_list,
        "words": words_list
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 儲存轉錄 JSON: {Path(json_path).name}")
    
    # 產出語意 SRT
    subs = process_segments_semantically(segment_list, corrections)
    with open(srt_path, 'w', encoding='utf-8') as f:
        for idx, sub in enumerate(subs, 1):
            s_str = format_timestamp(sub['start'])
            e_str = format_timestamp(sub['end'])
            f.write(f"{idx}\n{s_str} --> {e_str}\n{sub['text']}\n\n")
            
    lens = [count_cjk(s['text']) for s in subs]
    avg_l = sum(lens) / len(lens) if lens else 0
    max_l = max(lens) if lens else 0
    print(f"✅ [SRT 生成完成] {Path(srt_path).name}: 共 {len(subs)} 行 (平均 {avg_l:.1f} 字, 最大 {max_l} 字)")

def main():
    print("[*] 正在初始化 Faster-Whisper (medium, CPU int8, 8 threads)...", flush=True)
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)
    
    tasks = [
        # Ch06
        (
            CH06_DIR / "第06章_血濺赤崁與大鹿港_說明影片.mp4",
            CH06_DIR / "whisper_words_ch06_video.json",
            CH06_DIR / "第06章_血濺赤崁與大鹿港_說明影片.srt",
            CH06_PROMPT,
            CH06_CORRECTIONS
        ),
        (
            CH06_DIR / "第06章_血濺赤崁與大鹿港_雙人對談.m4a",
            CH06_DIR / "whisper_words_ch06_podcast.json",
            CH06_DIR / "第06章_血濺赤崁與大鹿港_雙人對談.srt",
            CH06_PROMPT,
            CH06_CORRECTIONS
        ),
        # Ch07
        (
            CH07_DIR / "第07章_決戰大員九個月_說明影片.mp4",
            CH07_DIR / "whisper_words_ch07_video.json",
            CH07_DIR / "第07章_決戰大員九個月_說明影片.srt",
            CH07_PROMPT,
            CH07_CORRECTIONS
        ),
        (
            CH07_DIR / "第07章_決戰大員九個月_雙人對談.m4a",
            CH07_DIR / "whisper_words_ch07_podcast.json",
            CH07_DIR / "第07章_決戰大員九個月_雙人對談.srt",
            CH07_PROMPT,
            CH07_CORRECTIONS
        ),
    ]
    
    for media_p, json_p, srt_p, prompt, corrections in tasks:
        if not media_p.exists():
            print(f"[ERROR] 找不到媒體檔案: {media_p}")
            continue
        transcribe_and_make_srt(model, media_p, json_p, srt_p, prompt, corrections)
        
    print("\n🎉 全部轉錄與 SRT 生成完畢！")

if __name__ == '__main__':
    main()
