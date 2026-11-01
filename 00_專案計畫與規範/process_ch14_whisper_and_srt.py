# -*- coding: utf-8 -*-
"""
第 14 章 語音轉錄 (Faster-Whisper) 與 自然語意 SRT 生成器
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
CH14_DIR = BASE_DIR / "05_日治時期的統治轉型與抗爭"

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

CH14_CORRECTIONS = COMMON_CORRECTIONS + [
    (r"後藤[新心]平", "後藤新平"),
    (r"兒玉[源原]太郎", "兒玉源太郎"),
    (r"八田[與與]一", "八田與一"),
    (r"長谷[川川]謹介", "長谷川謹介"),
    (r"新渡[戶戶]稻造", "新渡戶稻造"),
    (r"磯[永泳]吉", "磯永吉"),
    (r"末[永泳]仁", "末永仁"),
    (r"簡[吉級]", "簡吉"),
    (r"李應[章張]", "李應章"),
    (r"烏山[頭投]水庫", "烏山頭水庫"),
    (r"烏山[嶺領]", "烏山嶺"),
    (r"官田[溪西]", "官田溪"),
    (r"曾文[溪西]", "曾文溪"),
    (r"濁水[溪西]", "濁水溪"),
    (r"大安[溪西]鐵橋", "大安溪鐵橋"),
    (r"大甲[溪西]鐵橋", "大甲溪鐵橋"),
    (r"勝興[車車站]", "勝興車站"),
    (r"湖心[亭庭]", "湖心亭"),
    (r"載仁[親清]王", "載仁親王"),
    (r"看天[田天]", "看天田"),
    (r"嘉南[大太]圳", "嘉南大圳"),
    (r"一田[二兩]主", "一田二主"),
    (r"大租[權全]", "大租權"),
    (r"大租[戶戶]", "大租戶"),
    (r"小租[戶戶]", "小租戶"),
    (r"國勢[調條]查", "國勢調查"),
    (r"舊[慣貫]調查", "舊慣調查"),
    (r"蓬[萊萊]米", "蓬萊米"),
    (r"在[來萊]米", "在來米"),
    (r"米糖[相向]剋", "米糖相剋"),
    (r"米糖[相向]克", "米糖相剋"),
    (r"半水力[填田]築", "半水力填築"),
    (r"五分[車車]", "五分車"),
    (r"折[重中]扣秤", "折重扣秤"),
    (r"殉[工公]碑", "殉工碑"),
]

CH14_PROMPT = (
    "臺灣史, 日治時期, 後藤新平, 兒玉源太郎, 生物學原則, 治臺三策, 臨時臺灣土地調查局, "
    "一田二主, 大租權, 小租戶, 大租補償公債, 隱田, 財政獨立, 臨時臺灣舊慣調查會, "
    "岡松參太郎, 織田萬, 臺灣私法, 番族慣習調查報告書, 無主林野官有化, 國勢調查, "
    "戶籍, 保甲制, 壯丁團, 長谷川謹介, 鐵道部, 縱貫鐵路, 舊山線, 三義, 勝興車站, "
    "折返式軌道, 大安溪鐵橋, 大甲溪鐵橋, 濁水溪鐵橋, 氣壓沉箱工法, 臺中公園, 湖心亭, "
    "載仁親王, 一日生活圈, 八田與一, 烏山頭水庫, 珊瑚潭, 半水力填築式大壩, 官田溪, "
    "曾文溪, 烏山嶺隧道, 殉工碑, 嘉南大圳, 給排水路, 三年輪作給水法, 看天田, 水利組合, "
    "新渡戶稻造, 糖業改良意見書, 臺灣製糖, 大日本製糖, 明治製糖, 鹽水港製糖, "
    "原料採集區域制度, 第一憨種甘蔗予會社磅, 蓬萊米, 在來米, 磯永吉, 末永仁, 竹子湖, "
    "米糖相剋, 二林蔗農事件, 李應章, 簡吉, 臺灣農民組合"
)

def format_timestamp(seconds: float) -> str:
    td = max(0.0, seconds)
    hrs = int(td // 3600)
    mins = int((td % 3600) // 60)
    secs = int(td % 60)
    millis = int(round((td - int(td)) * 1000))
    if millis >= 1000: millis = 999
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
        
    # 拆分過長行（> 22 字元）
    final_subs = []
    for item in merged_subs:
        txt = item["text"]
        c_len = count_cjk(txt)
        t_start = item["start"]
        t_end = item["end"]
        duration = t_end - t_start
        
        if c_len > 22:
            delims = [m.start() for m in re.finditer(r'[，、\s]', txt)]
            if not delims:
                delims = [m.end() for m in re.finditer(r'(因為|所以|但是|而且|也就是|如果|這時候|接下來)', txt)]
            if not delims:
                delims = [m.end() for m in re.finditer(r'[在與和]', txt)]
                
            if delims:
                mid = len(txt) / 2.0
                best_split = min(delims, key=lambda d: abs(d - mid))
                part1 = clean_punctuation(txt[:best_split])
                part2 = clean_punctuation(txt[best_split:])
                len1 = count_cjk(part1)
                len2 = count_cjk(part2)
                if len1 > 0 and len2 > 0:
                    t_mid = t_start + duration * (len1 / (len1 + len2))
                    final_subs.append({"start": t_start, "end": t_mid, "text": part1})
                    final_subs.append({"start": t_mid, "end": t_end, "text": part2})
                    continue
                    
        final_subs.append(item)
        
    # 時間戳防重疊修正
    for i in range(len(final_subs) - 1):
        if final_subs[i]['end'] > final_subs[i+1]['start']:
            final_subs[i]['end'] = final_subs[i+1]['start']
            
    return final_subs

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
    
    result_data = {
        "text": "".join(full_text),
        "segments": segment_list,
        "words": words_list
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 儲存轉錄 JSON: {Path(json_path).name}")
    
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
        (
            CH14_DIR / "第14章_現代化骨架與殖民之刃_說明影片.mp4",
            CH14_DIR / "whisper_words_ch14_video.json",
            CH14_DIR / "第14章_現代化骨架與殖民之刃_說明影片.srt",
            CH14_PROMPT,
            CH14_CORRECTIONS
        ),
        (
            CH14_DIR / "第14章_現代化骨架與殖民之刃_雙人對談.m4a",
            CH14_DIR / "whisper_words_ch14_podcast.json",
            CH14_DIR / "第14章_現代化骨架與殖民之刃_雙人對談.srt",
            CH14_PROMPT,
            CH14_CORRECTIONS
        ),
    ]
    
    for media_p, json_p, srt_p, prompt, corrections in tasks:
        if not media_p.exists():
            print(f"[ERROR] 找不到媒體檔案: {media_p}")
            continue
        transcribe_and_make_srt(model, media_p, json_p, srt_p, prompt, corrections)
        
    print("\n🎉 第 14 章雙軌轉錄與自然語意 SRT 生成完畢！")

if __name__ == '__main__':
    main()
