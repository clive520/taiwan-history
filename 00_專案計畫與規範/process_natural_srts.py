# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 04 章 影視級人聲呼吸律與同音錯字精修腳本
1. 嚴格基於 Faster-Whisper 語音停頓原稿（保持真人呼吸與交談節奏）
2. 全面校正歷史考證、生物化學、民俗與地方術語之同音錯字
3. 遵循《影視級字幕製作標準作業程序_SOP》：
   - 拒絕機械式字數硬切（0 破詞破字）
   - 說話語氣自然銜接，單行 8~16 字（極限不超過 18 字）
   - 跨講者回饋詞獨立成行
"""
import sys
import os
import re
from pathlib import Path
import opencc

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH04_DIR = BASE_DIR / "舌尖上的臺灣" / "02_唐山渡海與閩粵交融"

VID_SRT = CH04_DIR / "第04章_一碗肉臊的百年身世_說明影片.srt"
POD_SRT = CH04_DIR / "第04章_一碗肉臊的百年身世_雙人對談.srt"

LOG_VID = Path(r"C:\Users\admin\.gemini\antigravity\brain\e6ad31e6-5e47-44d3-86ec-3061599c52d4\.system_generated\tasks\task-11619.log")
LOG_POD = Path(r"C:\Users\admin\.gemini\antigravity\brain\e6ad31e6-5e47-44d3-86ec-3061599c52d4\.system_generated\tasks\task-11578.log")

cc = opencc.OpenCC('s2twp')

# 完整同音字與錯別字修正表
CORRECTIONS = [
    # 專有名詞與核心料理
    (r'肉[燥噪][飯反]', '肉臊飯'),
    (r'乳[肉酪][飯反]', '滷肉飯'),
    (r'滷肉[飯反]', '滷肉飯'),
    (r'肉燒[飯反]', '肉臊飯'),
    (r'肉鬆飯', '肉臊飯'),
    (r'肉燒', '肉臊'),
    (r'肉[燥噪]', '肉臊'),
    (r'[焢空炕]肉[飯反]', '爌肉飯'),
    (r'[焢空炕]肉', '爌肉'),
    (r'黑豆[蔭蔭印應]油', '黑豆蔭油'),
    (r'[蔭蔭印應]油', '蔭油'),
    (r'黑豆醬油', '黑豆醬油'),
    (r'輕人黑豆', '青仁黑豆'),
    (r'青仁黑豆', '青仁黑豆'),
    (r'[杜肚]小[岳月]', '度小月'),
    (r'小[岳月]期間', '小月期間'),
    (r'小[岳月]', '小月'),
    (r'蛋在[麵面]', '擔仔麵'),
    (r'蛋仔[麵面]', '擔仔麵'),
    (r'擔仔[麵面]', '擔仔麵'),
    (r'蛋子賣[麵面]', '挑擔賣麵'),
    (r'挑[著着]蛋子', '挑著擔子'),
    (r'挑起扁[單擔]', '挑起扁擔'),
    (r'洪玉頭', '洪芋頭'),
    (r'食慕[餘魚][松鬆]', '虱目魚鬆'),
    (r'虱目[餘魚][松鬆]', '虱目魚鬆'),
    
    # 科學術語
    (r'福[安溫]酸', '谷氨酸'),
    (r'浮[安溫]酸', '谷氨酸'),
    (r'谷[氨胺]酸', '谷氨酸'),
    (r'有禮案積算', '游離氨基酸'),
    (r'游離[氨胺]基酸', '游離氨基酸'),
    (r'[氨胺]基酸', '氨基酸'),
    (r'鶴變', '褐變'),
    (r'青[腱鍵]', '氫鍵'),
    (r'親[腱鍵]', '氫鍵'),
    (r'供價界', '共價鍵'),
    (r'共價[界鍵]', '共價鍵'),
    (r'可[容溶]性', '可溶性'),
    (r'[融溶]膠凝膠[項相]邊', '溶膠凝膠相變'),
    (r'[項相]邊', '相變'),
    (r'單[煉鏈]的明膠', '單鏈的明膠'),
    (r'螺圓', '螺旋'),
    (r'明膠微[低滴]', '明膠微滴'),
    (r'非[急極]性微[膠酵]束', '非極性微膠束'),
    (r'比奇類與差分類化合物', '吡嗪類與吡咯類化合物'),
    (r'堅果交[向香]', '堅果焦香'),
    (r'發[炎煙]點高達190度', '發煙點高達190度'),
    (r'發[炎煙]點', '發煙點'),
    (r'[基肌]間脂肪', '肌間脂肪'),
    (r'[溶熔]點', '熔點'),
    (r'水解[霉酶]', '水解酶'),
    (r'食品[圍微][觀觀]結構[修學]的核心', '食品微觀結構學的核心'),
    (r'梅[納納]反應', '梅納反應'),
    (r'膠原蛋白', '膠原蛋白'),
    (r'三螺旋結構', '三螺旋結構'),
    (r'三螺旋膠原蛋白', '三螺旋膠原蛋白'),
    
    # 歷史文獻與地名
    (r'水星公司場', '水仙宮市場'),
    (r'水仙宮市場', '水仙宮市場'),
    (r'水仙宮', '水仙宮'),
    (r'侏羅縣[治志]拉?', '《諸羅縣志》啦'),
    (r'諸羅縣[治志]', '《諸羅縣志》'),
    (r'重修台[灣湾][輔府][治志]', '《重修臺灣府志》'),
    (r'台[灣湾][輔府][治志]', '《臺灣府志》'),
    (r'台[灣湾]福祉', '《臺灣府志》'),
    (r'官方[歷立]的禁宰石碑', '官方立的禁宰石碑'),
    (r'折損[因陰][得德]', '折損陰德'),
    (r'中[原元]普渡', '中元普渡'),
    (r'王爺建[教醮]', '王爺建醮'),
    (r'馬[腦瑙]', '瑪瑙'),
    (r'百年[生身][事世]', '百年身世'),
    (r'羅漢[角腳]', '羅漢腳'),
    (r'[鮮先]明', '先民'),
    (r'島嶼[鮮先]明', '島嶼先民'),
    (r'[資隻]身渡海', '隻身渡海'),
    (r'敗敗[丸完]', '拜拜完'),
    (r'[雅亞]熱帶氣候', '亞熱帶氣候'),
    (r'分子三[味位]液體', '分子三位一體'),
    (r'分子三[味位]一體', '分子三位一體'),
    (r'[這这]個[峰風][威味]方程式', '這個風味方程式'),
    (r'早期的[一移]民', '早期的移民'),
    (r'像木[蟹屑]一樣', '像木屑一樣'),
    (r'立體[集幾]合形狀', '立體幾何形狀'),
    (r'熱力學之[律旅]', '熱力學之旅'),
    (r'竹皮', '豬皮'),
    (r'三大地[獄域]流派', '三大地域流派'),
    (r'地[獄域]差異', '地域差異'),
    (r'地[獄域]流派', '地域流派'),
    (r'富商[四仕][生紳]', '富商仕紳'),
    (r'[同銅]班美食', '銅板美食'),
    (r'大口[拔扒]下', '大口扒下'),
    (r'做[出粗]活', '做粗活'),
    (r'[芥街]頭小吃', '街頭小吃'),
    (r'[應硬][任韌]的膠原蛋白', '硬韌的膠原蛋白'),
    (r'黏[醇唇][豐厚]+', '黏唇豐厚'),
    (r'黏[醇唇]感', '黏唇感'),
    (r'一[玩碗]把脂肪', '一碗把脂肪'),
    (r'[垂催]化劑', '催化劑'),
    (r'10度有保表', '濕度又爆表'),
    (r'[建見]方的肉[夾丁角]', '見方的肉丁'),
    (r'皮\s*[汁脂]\s*肉', '皮、脂、肉'),
    (r'什麼魔法[司時]客', '什麼魔法時刻'),
    (r'嘴唇微[膩抿]', '嘴唇微抿'),
    (r'[燒稍]涼的空氣', '稍涼的空氣'),
    (r'雲[加嘉]南沿海是[危微][險鹹]的沙[子質]土壤', '雲嘉南沿海是微鹹的沙質土壤'),
    (r'白[化話][紋文]', '白話文'),
    (r'解除[風封][陰印]', '解除封印'),
    (r'爆銷了', '報銷了'),
    (r'[圍微]孔陶[鋼缸]', '微孔陶缸'),
    (r'[鋼缸]內溫度', '缸內溫度'),
    (r'[獨毒][立辣]太陽', '毒辣太陽'),
    (r'[喜洗]好[曲麴]的黑豆', '洗好麴的黑豆'),
    (r'大[變辯][整證]', '大辯證'),
    (r'吃[除粗]飽的', '吃粗飽的'),
    (r'[西細][脆碎]狀', '細碎狀'),
    (r'勞動重[症鎮]', '勞動重鎮'),
    (r'[不步]?14小時', '24小時'),
    (r'[這這]片便宜', '這碗便宜'),
    (r'深度探探', '深度探討'),
    (r'抗[蒸熱]氣候', '抗熱氣候'),
    (r'源自[實史]料', '源自史料'),
    (r'sou這個字', '「臊」這個字'),
    (r'[屎豕]膏臭[眼也]', '豕膏臭也'),
    (r'高溫多[餘雨]', '高溫多雨'),
    (r'台([灣北市南中東中東南東東南])', r'臺\1'),
    (r'全台', '全臺'),
    (r'在台', '在臺'),
    (r'來台', '來臺'),
    (r'[臺台]灣', '臺灣'),
]

def clean_line_text(text: str) -> str:
    t = cc.convert(text)
    for pat, rep in CORRECTIONS:
        t = re.sub(pat, rep, t)
    # 移除句首句末不自然的標點，但保留文中的逗號或語氣問號/驚嘆號
    t = re.sub(r'^[，。！？、；：,\.!\?;:\s]+', '', t)
    t = re.sub(r'[，。；、,\.;\s]+$', '', t)
    # 將英文問號驚嘆號轉換為全形
    t = t.replace('?', '？').replace('!', '！')
    return t.strip()

def time_to_sec(ts):
    h, m, s_ms = ts.split(":")
    s, ms = s_ms.split(",")
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0

def sec_to_time(sec):
    td = max(0.0, sec)
    hrs = int(td // 3600)
    mins = int((td % 3600) // 60)
    secs = int(td % 60)
    millis = int(round((td - int(td)) * 1000))
    if millis >= 1000: millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def parse_log_segments(log_path: Path):
    if not log_path.exists():
        print(f"[ERROR] 找不到記錄檔: {log_path}")
        return []
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    pattern = re.compile(r'^\s*\[(\d{2}:\d{2}:\d{2},\d{3})\s*->\s*(\d{2}:\d{2}:\d{2},\d{3})\]\s*(.*)$', re.MULTILINE)
    matches = pattern.findall(content)
    segments = []
    for st, et, raw_txt in matches:
        txt = clean_line_text(raw_txt)
        if txt:
            segments.append({
                'start': time_to_sec(st),
                'end': time_to_sec(et),
                'text': txt
            })
    return segments

def optimize_cadence(segments, max_chars=16, min_chars=4, max_pause=0.35, is_podcast=False):
    """
    優化自然語氣斷句：
    1. 將同講者、短停頓（< max_pause）、語意未完的短碎行平滑合併（合併後 <= max_chars）。
    2. 對話輪替詞（對吧？、沒錯、真的）獨立保留，不與前後句黏合。
    3. 針對極少數超長句（> 20 字），依語法停頓標點或連接詞自然拆分。
    """
    # 獨立回饋詞清單（嚴禁被黏合）
    STANDALONE_WORDS = {
        '對吧？', '對啊', '對', '沒錯', '沒錯沒錯', '真的', '哇', '好', '你說',
        '就是啊', '完全正確', '是的', '原來如此', '天啊', '等等', '有多不一樣',
        '阶级跨越怎么说', '階級跨越怎麼說', '杜小月是這樣來的', '我皮超厚的耶'
    }

    merged = []
    i = 0
    while i < len(segments):
        cur = segments[i]
        
        # 若當前詞為獨立對話回饋詞，直接獨立成行
        if cur['text'] in STANDALONE_WORDS:
            merged.append(cur)
            i += 1
            continue

        # 嘗試與下一句合併
        if i + 1 < len(segments):
            nxt = segments[i+1]
            pause = nxt['start'] - cur['end']
            
            # 若下一句是獨立對話詞，不合併
            if nxt['text'] in STANDALONE_WORDS:
                merged.append(cur)
                i += 1
                continue
                
            # 若當前句以句末問號/驚嘆號結尾，不合併
            if cur['text'].endswith('？') or cur['text'].endswith('！'):
                merged.append(cur)
                i += 1
                continue

            # 判斷是否適合合併：
            # 1. 停頓極短（< max_pause）
            # 2. 合併後總字數 <= max_chars
            # 3. 當前句長度較短（< 10 字），且非完整獨立陳述
            combined_len = len(cur['text']) + len(nxt['text'])
            if pause <= max_pause and combined_len <= max_chars:
                # 判斷是否需要逗號
                if not cur['text'].endswith('，') and len(cur['text']) >= 4 and len(nxt['text']) >= 4:
                    sep = '，'
                else:
                    sep = ''
                cur['text'] = cur['text'] + sep + nxt['text']
                cur['end'] = nxt['end']
                i += 2
                merged.append(cur)
                continue

        merged.append(cur)
        i += 1

    # 處理極少數超長行 (> 18 字)
    final_subs = []
    for item in merged:
        txt = item['text']
        if len(txt) > 18:
            # 尋找最佳自然拆分點（逗號、連接詞）
            split_idx = -1
            for p in ['，', '、', '而且', '但是', '因為', '所以', '接著', '還有']:
                pos = txt.find(p)
                if pos >= 7 and pos <= len(txt) - 6:
                    split_idx = pos + (1 if p in ['，', '、'] else 0)
                    break
            
            if split_idx != -1:
                p1 = txt[:split_idx].rstrip('，')
                p2 = txt[split_idx:].lstrip('，')
                dur = item['end'] - item['start']
                mid_t = item['start'] + dur * (len(p1) / (len(p1) + len(p2)))
                final_subs.append({'start': item['start'], 'end': mid_t, 'text': p1})
                final_subs.append({'start': mid_t, 'end': item['end'], 'text': p2})
                continue

        final_subs.append(item)

    # 確保時間戳單調且無重疊
    for j in range(len(final_subs) - 1):
        if final_subs[j]['end'] > final_subs[j+1]['start']:
            final_subs[j]['end'] = final_subs[j+1]['start']
        if final_subs[j]['end'] <= final_subs[j]['start']:
            final_subs[j]['end'] = final_subs[j]['start'] + 0.3

    return final_subs

def write_srt(subs, out_path: Path):
    lines = []
    for idx, item in enumerate(subs, 1):
        st = sec_to_time(item['start'])
        et = sec_to_time(item['end'])
        lines.append(f"{idx}\n{st} --> {et}\n{item['text']}\n")
    out_path.write_text("\n".join(lines), encoding='utf-8')
    lens = [len(x['text']) for x in subs]
    print(f"📄 已成功導出影視級字幕：{out_path.name}")
    print(f"   總行數: {len(subs)} 行 | 最小長度: {min(lens)} | 平均長度: {sum(lens)/len(lens):.1f} | 最大長度: {max(lens)}")

def main():
    print("🎬 開始處理說明影片字幕...")
    vid_segs = parse_log_segments(LOG_VID)
    vid_optimized = optimize_cadence(vid_segs, max_chars=16, min_chars=4, max_pause=0.35, is_podcast=False)
    write_srt(vid_optimized, VID_SRT)

    print("\n🎙️ 開始處理播客對談字幕...")
    pod_segs = parse_log_segments(LOG_POD)
    pod_optimized = optimize_cadence(pod_segs, max_chars=16, min_chars=3, max_pause=0.30, is_podcast=True)
    write_srt(pod_optimized, POD_SRT)

if __name__ == "__main__":
    main()
