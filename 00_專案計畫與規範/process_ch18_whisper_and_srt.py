# -*- coding: utf-8 -*-
"""
第 18 章 語音轉錄 (Faster-Whisper medium int8) 與 自然語意 SRT 生成器
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
CH18_DIR = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇"

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

CH18_CORRECTIONS = COMMON_CORRECTIONS + [
    (r"孫運[璿旋璇]", "孫運璿"),
    (r"李國[鼎頂]", "李國鼎"),
    (r"潘文[淵源]", "潘文淵"),
    (r"方賢[齊齊]", "方賢齊"),
    (r"費[驊驊]", "費驊"),
    (r"尹仲[容容]", "尹仲容"),
    (r"謝東[閔閔]", "謝東閔"),
    (r"張忠[謀謀]", "張忠謀"),
    (r"史欽[泰泰]", "史欽泰"),
    (r"曾繁[城成]", "曾繁城"),
    (r"曹興[誠誠]", "曹興誠"),
    (r"楊丁[元元]", "楊丁元"),
    (r"劉英[達達]", "劉英達"),
    (r"胡定[華華]", "胡定華"),
    (r"宣明[智智]", "宣明智"),
    (r"施振[榮榮]", "施振榮"),
    (r"童子[賢賢]", "童子賢"),
    (r"郭台[銘銘]", "郭台銘"),
    (r"林百[里里]", "林百里"),
    (r"林本[堅堅]", "林本堅"),
    (r"黃仁[勳勳]", "黃仁勳"),
    (r"蘇姿[丰丰]", "蘇姿丰"),
    (r"蔡明[介介]", "蔡明介"),
    (r"工[研言]院", "工研院"),
    (r"工業技術[研言]究院", "工業技術研究院"),
    (r"小[欣心][欣心]豆漿[店店頭]", "小欣欣豆漿店"),
    (r"雙極[性姓]", "雙極性"),
    (r"積體[電甸]路", "積體電路"),
    (r"矽[島鳥]", "矽島"),
    (r"矽[盾頓]", "矽盾"),
    (r"矽晶[圓圓]", "矽晶圓"),
    (r"晶[圓圓]代工", "晶圓代工"),
    (r"純晶[圓圓]代工", "純晶圓代工"),
    (r"聯華[電甸]子", "聯華電子"),
    (r"聯[電甸]", "聯電"),
    (r"台積[電甸]", "台積電"),
    (r"臺灣積體[電甸]路", "臺灣積體電路"),
    (r"新竹科學[工公]業園區", "新竹科學工業園區"),
    (r"竹[科科]", "竹科"),
    (r"無塵[室市]", "無塵室"),
    (r"浸潤式[微微]影", "浸潤式微影"),
    (r"極紫外[光廣]", "極紫外光"),
    (r"先進[製製]程", "先進製程"),
    (r"摩爾定[律綠]", "摩爾定律"),
    (r"客廳即[工公]廠", "客廳即工廠"),
    (r"加工出口[區嶇]", "加工出口區"),
    (r"前鎮加工[區嶇]", "前鎮加工區"),
    (r"埃[米米]", "埃米"),
    (r"奈[米米]", "奈米"),
    (r"微[米米]", "微米"),
    (r"宏[碁基]", "宏碁"),
    (r"華[碩碩]", "華碩"),
    (r"鴻[海每]", "鴻海"),
    (r"廣[達達]", "廣達"),
    (r"仁[寶寶]", "仁寶"),
    (r"緯[創創]", "緯創"),
    (r"和[碩碩]", "和碩"),
    (r"艾司摩[爾爾]", "艾司摩爾"),
    (r"德州[儀儀]器", "德州儀器"),
    (r"飛利[浦普]", "飛利浦"),
    (r"無晶[圓圓]廠", "無晶圓廠"),
    (r"超純[水誰]", "超純水"),
    (r"去離子[水誰]", "去離子水"),
    (r"蠻長", "滿長"),
    (r"蠻多", "滿多"),
    (r"蠻好", "滿好"),
    (r"蠻大", "滿大"),
]

CH18_PROMPT = (
    "臺灣史, 第18章, 矽島崛起, 世界舞台, 客廳即工廠, 竹科奇蹟, 台積電, 半導體, TSMC, "
    "孫運璿, 李國鼎, 潘文淵, 方賢齊, 費驊, 尹仲容, 謝東閔, 高雄加工出口區, 前鎮加工區, "
    "第一次石油危機, 小欣欣豆漿店, 南陽街, CMOS, 互補金屬氧化物半導體, 雙極性, Bipolar, "
    "工研院, 工業技術研究院, ITRI, 電子工業研究發展中心, ERSO, RCA, 普林斯頓, 芬利廠, "
    "史欽泰, 曾繁城, 曹興誠, 楊丁元, 劉英達, 胡定華, 3微米, 示範工廠, 電子錶晶片, 良率, "
    "聯華電子, 聯電, UMC, 新竹科學工業園區, 竹科, 國立清華大學, 國立交通大學, 德州儀器, TI, "
    "張忠謀, Morris Chang, 整合元件製造商, IDM, 純晶圓代工, Pure-play Foundry, 飛利浦, Philips, "
    "行政院開發基金, 無晶圓廠, Fabless, 輝達, NVIDIA, 黃仁勳, 高通, Qualcomm, 超微, AMD, "
    "蘇姿丰, 聯發科, 蔡明介, 個人電腦, PC, 宏碁, Acer, 施振榮, 華碩, ASUS, 童子賢, "
    "鴻海精密, 富士康, Foxconn, 郭台銘, 廣達電腦, Quanta, 林百里, 仁寶, 緯創, 和碩, 電子五哥, "
    "983出貨, 摩爾定律, 浸潤式微影, Immersion Lithography, 林本堅, Burn Lin, 去離子水, "
    "193奈米, 134奈米, 157奈米, 艾司摩爾, ASML, 極紫外光, EUV, 7奈米, 5奈米, 3奈米, 2奈米, "
    "埃米, Angstrom, GAA, 奈米片, CoWoS, 先進封裝, 南科, 晶圓十八廠, GigaFab, 矽盾, Silicon Shield, "
    "克雷格·艾迪生, 人工智慧, AI晶片, 寧靜革命, 美麗島, 自由民主, 全系列完結篇"
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
            else:
                # 無標點強制拆分
                half = len(txt) // 2
                part1 = clean_punctuation(txt[:half])
                part2 = clean_punctuation(txt[half:])
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
    min_l = min(lens) if lens else 0
    print(f"✅ [SRT 生成完成] {Path(srt_path).name}: 共 {len(subs)} 行 (最小 {min_l} 字, 平均 {avg_l:.1f} 字, 最大 {max_l} 字)")
    return len(subs)

def main():
    print("[*] 正在初始化 Faster-Whisper (medium, CPU int8, 8 threads)...", flush=True)
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)
    
    tasks = [
        (
            CH18_DIR / "第18章_矽島崛起與世界舞台_說明影片.mp4",
            BASE_DIR / "00_專案計畫與規範/whisper_words_ch18_video.json",
            CH18_DIR / "第18章_矽島崛起與世界舞台_說明影片.srt",
            CH18_PROMPT,
            CH18_CORRECTIONS
        ),
        (
            CH18_DIR / "第18章_矽島崛起與世界舞台_雙人對談.m4a",
            BASE_DIR / "00_專案計畫與規範/whisper_words_ch18_podcast.json",
            CH18_DIR / "第18章_矽島崛起與世界舞台_雙人對談.srt",
            CH18_PROMPT,
            CH18_CORRECTIONS
        ),
    ]
    
    line_counts = []
    for media_p, json_p, srt_p, prompt, corrections in tasks:
        if not media_p.exists():
            print(f"[ERROR] 找不到媒體檔案: {media_p}")
            continue
        cnt = transcribe_and_make_srt(model, media_p, json_p, srt_p, prompt, corrections)
        line_counts.append(cnt)
        
    print(f"\n🎉 第 18 章雙軌轉錄與自然語意 SRT 生成完畢！行數：{line_counts}")

if __name__ == '__main__':
    main()
