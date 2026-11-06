# -*- coding: utf-8 -*-
"""
第 16 章 語音轉錄 (Faster-Whisper) 與 自然語意 SRT 生成器
規範：自然語意斷句、8~22字/行、0錯字破句、臺/臺灣標準繁體
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
CH16_DIR = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇"

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

CH16_CORRECTIONS = COMMON_CORRECTIONS + [
    (r"陳[移宜]", "陳儀"),
    (r"葛[鏡敬]恩", "葛敬恩"),
    (r"柯遠[分芬]", "柯遠芬"),
    (r"彭孟[集緝]", "彭孟緝"),
    (r"彭夢緝", "彭孟緝"),
    (r"湯[德得][章彰]", "湯德章"),
    (r"陳[新心薪]", "陳炘"),
    (r"林茂[深盛生]", "林茂生"),
    (r"潘木[知之枝]", "潘木枝"),
    (r"王添[燈丁灯]", "王添灯"),
    (r"吳鴻[齊祺麒]", "吳鴻麒"),
    (r"施江[男南]", "施江南"),
    (r"阮[照朝]日", "阮朝日"),
    (r"柯[奇旗]化", "柯旗化"),
    (r"雷[政鎮震]", "雷震"),
    (r"殷海[廣光]", "殷海光"),
    (r"[伯白]楊", "柏楊"),
    (r"傅[思斯]年", "傅斯年"),
    (r"黃榮[璨燦]", "黃榮燦"),
    (r"天馬茶[坊房]", "天馬茶房"),
    (r"林江[麥妹邁]", "林江邁"),
    (r"傅學[同通]", "傅學通"),
    (r"陳文[西溪]", "陳文溪"),
    (r"二二八處理[委為]員會", "二二八處理委員會"),
    (r"三十二條[處處]理大綱", "三十二條處理大綱"),
    (r"21師", "二十一師"),
    (r"大[正政]公園", "大正公園"),
    (r"大東信[託托]", "大東信託"),
    (r"大公企[業業]", "大公企業"),
    (r"懲治叛[亂亂]條例", "懲治叛亂條例"),
    (r"2條1", "二條一"),
    (r"檢肅匪[諜諜]條例", "檢肅匪諜條例"),
    (r"新生訓[導導]處", "新生訓導處"),
    (r"綠[洲洲]山莊", "綠洲山莊"),
    (r"泰[源元]監獄", "泰源監獄"),
    (r"第十三中[隊隊]", "第十三中隊"),
    (r"新英文[法發]", "新英文法"),
    (r"自由中[國國]", "自由中國"),
    (r"中國民主[黨黨]", "中國民主黨"),
    (r"大力水[手手]", "大力水手"),
    (r"馬場[町丁]", "馬場町"),
    (r"四六事[件件]", "四六事件"),
    (r"四萬[換喚]一[塊元]", "四萬換一塊"),
    (r"狗去豬[來來]", "狗去豬來"),
    (r"[簞簞]食壺[漿漿]", "簞食壺漿"),
    (r"抓[耙把]仔", "抓耙仔"),
    (r"應即槍[決決]可也", "應即槍決可也"),
]

CH16_PROMPT = (
    "臺灣史, 第16章, 時代巨變, 傷痕記憶, 戰後接收, 昭和天皇, 玉音放送, 臺灣光復, "
    "國軍第七十軍, 基隆港, 葛超智, 被出賣的臺灣, 臺灣省行政長官公署, 陳儀, 葛敬恩, "
    "柯遠芬, 彭孟緝, 高雄要塞司令部, 貿易局, 專賣局, 舊臺幣, 惡性通貨膨脹, 四萬換一塊, "
    "新臺幣, 米荒, 天馬茶房, 林江邁, 傅學通, 陳文溪, 查緝私煙, 太平町, 臺北放送局, "
    "新公園, 二二八事件, 二二八事件處理委員會, 三十二條處理大綱, 王添灯, 寅冬亥親電, "
    "二十一師, 劉雨卿, 清鄉, 湯德章, 大正公園, 湯德章紀念公園, 陳炘, 大東信託, "
    "大公企業, 林茂生, 哥倫比亞大學, 民報, 潘木枝, 水上機場, 嘉義火車站, 吳鴻麒, "
    "施江南, 阮朝日, 戒嚴令, 陳誠, 懲治叛亂條例, 二條一, 唯一死刑, 戡亂時期檢肅匪諜條例, "
    "沒收財產, 硃批, 應即槍決可也, 保密局, 警備總部, 軍訓教官, 抓耙仔, 四六事件, "
    "傅斯年, 臺大哲學系事件, 綠島, 新生訓導處, 綠洲山莊, 泰源監獄, 第十三中隊, "
    "柯旗化, 台灣監獄島, 新英文法, 自由中國, 雷震, 殷海光, 胡適, 中國民主黨, "
    "柏楊, 大力水手, 馬場町, 馬場町刑場, 黃榮燦, 恐怖的檢查, 轉型正義, 人權博物館"
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
            CH16_DIR / "第16章_時代巨變與傷痕記憶_說明影片.mp4",
            CH16_DIR / "whisper_words_ch16_video.json",
            CH16_DIR / "第16章_時代巨變與傷痕記憶_說明影片.srt",
            CH16_PROMPT,
            CH16_CORRECTIONS
        ),
        (
            CH16_DIR / "第16章_時代巨變與傷痕記憶_雙人對談.m4a",
            CH16_DIR / "whisper_words_ch16_podcast.json",
            CH16_DIR / "第16章_時代巨變與傷痕記憶_雙人對談.srt",
            CH16_PROMPT,
            CH16_CORRECTIONS
        ),
    ]
    
    for media_p, json_p, srt_p, prompt, corrections in tasks:
        if not media_p.exists():
            print(f"[ERROR] 找不到媒體檔案: {media_p}")
            continue
        transcribe_and_make_srt(model, media_p, json_p, srt_p, prompt, corrections)
        
    print("\n🎉 第 16 章雙軌轉錄與自然語意 SRT 生成完畢！")

if __name__ == '__main__':
    main()
