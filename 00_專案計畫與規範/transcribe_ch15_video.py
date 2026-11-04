# -*- coding: utf-8 -*-
"""
第 15 章 說明影片 Whisper 轉錄與自然語意 SRT 生成
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
CH15_DIR = BASE_DIR / "05_日治時期的統治轉型與抗爭"

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

CH15_CORRECTIONS = COMMON_CORRECTIONS + [
    (r"蔣[偉偉衛位]水", "蔣渭水"),
    (r"林[現憲]堂", "林獻堂"),
    (r"蔡培[夥貨獲火]", "蔡培火"),
    (r"林[程承成]祿", "林呈祿"),
    (r"蔡[會慧]如", "蔡惠如"),
    (r"莫[納那]魯[島島道]", "莫那·魯道"),
    (r"莫那魯道", "莫那·魯道"),
    (r"達多[莫納]那", "達多·莫那"),
    (r"達多莫那", "達多·莫那"),
    (r"花[剛岡]一郎", "花岡一郎"),
    (r"花[剛岡]二郎", "花岡二郎"),
    (r"佐久間左馬[態太]", "佐久間左馬太"),
    (r"吉村克[已己]", "吉村克己"),
    (r"石塚英[藏藏]", "石塚英藏"),
    (r"人見[次治]郎", "人見次郎"),
    (r"大[安案]醫院", "大安醫院"),
    (r"臨床講[意義]", "臨床講義"),
    (r"[知智]識營養不良[症政]", "智識營養不良症"),
    (r"美[泰台臺]團", "美臺團"),
    (r"致警事件", "治警事件"),
    (r"置警事件", "治警事件"),
    (r"自警事件", "治警事件"),
    (r"憶難忘", "意難忘"),
    (r"理[番蕃]政策", "理蕃政策"),
    (r"五年理[番蕃]計[畫劃]", "五年理蕃計畫"),
    (r"[愛隘]勇線", "隘勇線"),
    (r"賽德[客克]族", "賽德克族"),
    (r"馬[荷赫]坡社", "馬赫坡社"),
    (r"和歌社", "荷歌社"),
    (r"波阿[倫崙]社", "波阿崙社"),
    (r"三氯硝基甲[烷皖]", "三氯硝基甲烷"),
    (r"[靡糜]爛性毒氣", "糜爛性毒氣"),
    (r"[穿川]中島", "川中島"),
    (r"[青清]流部落", "清流部落"),
    (r"味方[番蕃]", "味方蕃"),
    (r"[鯨擎黥]面", "黥面"),
    (r"誤社事件", "霧社事件"),
    (r"大正民[主竹]", "大正民主"),
    (r"六三法[撤徹]廢", "六三法撤廢"),
    (r"內地延長[主竹]義", "內地延長主義"),
    (r"靜修女學[校堂]", "靜修女學校"),
    (r"臺灣[民明]報", "臺灣民報"),
    (r"臺灣工友總[聯連]盟", "臺灣工友總聯盟"),
    (r"彩虹[橋喬]", "彩虹橋"),
    (r"哈[卡考]烏圖克斯", "Hakaw Utux"),
    (r"哈卡烏圖克斯", "Hakaw Utux"),
    (r"總統府甚至發明", "總督府甚至發明"),
    (r"如果總統府倒台", "如果總督府倒臺"),
    (r"總統府", "總督府"),
]

CH15_PROMPT = (
    "臺灣史, 第15章, 臺灣人的臺灣, 大正民主, 民族自決, 威爾遜, 新民會, 臺灣青年, "
    "六三法撤廢, 內地延長主義, 臺灣議會設置請願運動, 林獻堂, 蔡培火, 林呈祿, 蔣渭水, "
    "臺灣文化協會, 靜修女學校, 大安醫院, 臨床講義, 智識營養不良症, 文化講演會, 讀報社, "
    "文化劇, 美臺團, 蔡惠如, 臺灣民報, 有力者大會, 治安警察法, 治警事件, 意難忘, "
    "臺灣民眾黨, 國際聯盟, 鴉片專賣, 臺灣工友總聯盟, 大眾葬, 理蕃政策, 佐久間左馬太, "
    "五年理蕃計畫, 隘勇線, 賽德克族, 莫那·魯道, 達多·莫那, 霧社公學校, 馬赫坡社, "
    "荷歌社, 波阿崙社, 斯庫社, 羅多夫社, 塔羅灣社, 彩虹橋, Hakaw Utux, 花岡一郎, "
    "花岡二郎, 吉村克己, 敬酒事件, 毒氣彈, 三氯硝基甲烷, 川中島, 清流部落, 石塚英藏, 人見次郎"
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

def main():
    media_path = CH15_DIR / "第15章_臺灣人的臺灣_說明影片.mp4"
    json_path = CH15_DIR / "whisper_words_ch15_video.json"
    srt_path = CH15_DIR / "第15章_臺灣人的臺灣_說明影片.srt"
    
    print("[*] 正在初始化 Faster-Whisper (medium, CPU int8, 8 threads)...", flush=True)
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)
    
    print(f"\n" + "="*70)
    print(f"🎙️ 開始轉錄說明影片: {media_path.name}")
    print(f"="*70)
    start_t = time.time()
    
    segments, info = model.transcribe(
        str(media_path),
        language="zh",
        initial_prompt=CH15_PROMPT,
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
    print(f"✅ 儲存轉錄 JSON: {json_path.name}")
    
    subs = process_segments_semantically(segment_list, CH15_CORRECTIONS)
    with open(srt_path, 'w', encoding='utf-8') as f:
        for idx, sub in enumerate(subs, 1):
            s_str = format_timestamp(sub['start'])
            e_str = format_timestamp(sub['end'])
            f.write(f"{idx}\n{s_str} --> {e_str}\n{sub['text']}\n\n")
            
    lens = [count_cjk(s['text']) for s in subs]
    avg_l = sum(lens) / len(lens) if lens else 0
    max_l = max(lens) if lens else 0
    print(f"✅ [SRT 生成完成] {srt_path.name}: 共 {len(subs)} 行 (平均 {avg_l:.1f} 字, 最大 {max_l} 字)")

if __name__ == '__main__':
    main()
