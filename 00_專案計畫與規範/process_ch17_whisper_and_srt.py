# -*- coding: utf-8 -*-
"""
第 17 章 語音轉錄 (Faster-Whisper) 與 自然語意 SRT 生成器
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
CH17_DIR = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇"

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

CH17_CORRECTIONS = COMMON_CORRECTIONS + [
    (r"美麗[島鳥]", "美麗島"),
    (r"黃信[介界]", "黃信介"),
    (r"施明[德得]", "施明德"),
    (r"姚嘉[文聞]", "姚嘉文"),
    (r"張俊[宏紅]", "張俊宏"),
    (r"林義[雄雄]", "林義雄"),
    (r"呂秀[蓮連]", "呂秀蓮"),
    (r"陳[菊局]", "陳菊"),
    (r"林弘[宣宣]", "林弘宣"),
    (r"鄭南[榕容]", "鄭南榕"),
    (r"詹益[樺華]", "詹益樺"),
    (r"陳文[成誠]", "陳文成"),
    (r"劉宜[良量]", "劉宜良"),
    (r"汪希[苓令]", "汪希苓"),
    (r"竹[聯連]幫", "竹聯幫"),
    (r"陳啟[禮里]", "陳啟禮"),
    (r"李登[輝輝]", "李登輝"),
    (r"彭明[敏敏]", "彭明敏"),
    (r"尤[清清]", "尤清"),
    (r"謝長[廷廷]", "謝長廷"),
    (r"蘇貞[昌昌]", "蘇貞昌"),
    (r"萬年老[國國]代", "萬年老國代"),
    (r"萬年國[會會]", "萬年國會"),
    (r"釋字第?261號", "釋字第261號"),
    (r"野百[合和]", "野百合"),
    (r"三月學[運運]", "三月學運"),
    (r"中山[樓樓]", "中山樓"),
    (r"獨[台臺]會", "獨臺會"),
    (r"廖偉[程成]", "廖偉程"),
    (r"100行動[聯連]盟", "100行動聯盟"),
    (r"李鎮[源淵]", "李鎮源"),
    (r"林山[田填]", "林山田"),
    (r"陳師[孟孟]", "陳師孟"),
    (r"刑法第一百[條條]", "刑法第一百條"),
    (r"懲治叛[亂亂]條例", "懲治叛亂條例"),
    (r"[2二]條[1一]", "二條一"),
    (r"動員戡[亂亂]時期臨時[條條]款", "動員戡亂時期臨時條款"),
    (r"國是[會會議]", "國是會議"),
    (r"大港埔圓[環圈]", "大港埔圓環"),
    (r"東風[ -]?15", "東風-15"),
    (r"尼米[茲茲]號", "尼米茲號"),
    (r"獨立[號號]", "獨立號"),
    (r"航空母[艦艦]", "航空母艦"),
    (r"寧靜革[命命]", "寧靜革命"),
    (r"主權在[民皿]", "主權在民"),
    (r"蠻長", "滿長"),
    (r"蠻多", "滿多"),
    (r"蠻好", "滿好"),
    (r"蠻大", "滿大"),
]

CH17_PROMPT = (
    "臺灣史, 第17章, 走出戒嚴, 民主奇蹟, 美麗島事件, 野百合學運, 總統直選, 黨外運動, "
    "美麗島雜誌, 黃信介, 許信良, 施明德, 張俊宏, 姚嘉文, 林義雄, 呂秀蓮, 陳菊, 林弘宣, "
    "世界人權日, 新興街, 大港埔圓環, 美麗島站, 催淚瓦斯, 警備總部, 懲治叛亂條例, 二條一, "
    "景美看守所, 第一法庭, 軍法大審, 青年辯護律師團, 尤清, 陳水扁, 謝長廷, 蘇貞昌, "
    "林宅血案, 林游阿妹, 林奐均, 林亮均, 林亭均, 陳文成, 卡內基梅隆大學, 臺大研究生圖書館, "
    "江南案, 劉宜良, 蔣經國傳, 汪希苓, 竹聯幫, 陳啟禮, 蔣經國, 民主進步黨, 圓山大飯店, "
    "突破黨禁, 解除戒嚴, 戒嚴令, 兩岸探親, 報禁, 鄭南榕, 自由時代, 百分之百的言論自由, "
    "自焚殉道, 詹益樺, 國民大會, 萬年老國代, 陽明山中山樓, 三月學運, 中正紀念堂, 自由廣場, "
    "大中至正, 野百合, 四大訴求, 解散國大, 廢除臨時條款, 召開國是會議, 國是會議, 李登輝, "
    "釋字第261號, 動員戡亂時期臨時條款, 獨台會案, 廖偉程, 刑法第一百條, 100行動聯盟, "
    "李鎮源, 林山田, 陳師孟, 國會全面改選, 臺灣省長民選, 1996年總統選舉, 第一次全民直選總統, "
    "連戰, 彭明敏, 第三次臺海危機, 東風-15, 飛彈演習, 獨立號, 尼米茲號, 航空母艦, 寧靜革命, 主權在民"
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
            CH17_DIR / "第17章_走出戒嚴的民主奇蹟_說明影片.mp4",
            CH17_DIR / "whisper_words_ch17_video.json",
            CH17_DIR / "第17章_走出戒嚴的民主奇蹟_說明影片.srt",
            CH17_PROMPT,
            CH17_CORRECTIONS
        ),
        (
            CH17_DIR / "第17章_走出戒嚴的民主奇蹟_雙人對談.m4a",
            CH17_DIR / "whisper_words_ch17_podcast.json",
            CH17_DIR / "第17章_走出戒嚴的民主奇蹟_雙人對談.srt",
            CH17_PROMPT,
            CH17_CORRECTIONS
        ),
    ]
    
    for media_p, json_p, srt_p, prompt, corrections in tasks:
        if not media_p.exists():
            print(f"[ERROR] 找不到媒體檔案: {media_p}")
            continue
        transcribe_and_make_srt(model, media_p, json_p, srt_p, prompt, corrections)
        
    print("\n🎉 第 17 章雙軌轉錄與自然語意 SRT 生成完畢！")

if __name__ == '__main__':
    main()
