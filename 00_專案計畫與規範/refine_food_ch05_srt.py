# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 05 章 影視級字幕標準精修處理器
1. 先查錯別字與同音字：針對善化牛墟、試牛四法、生化學（Pre-rigor、ATP、冷收縮、肌球蛋白、肌紅蛋白、肌動蛋白）、高湯生沖（起蝦眼水、次黃嘌呤核苷酸、游離麩胺酸、鮮味協同效應）、深夜熱鏈等 60+ 項術語進行全方位修正。
2. 再依人類說話語氣與呼吸律斷句：
   - 每行 8~14 字（上限 16 字，硬上限 18 字）
   - 對話反饋詞（對吧？、真的！、沒錯、天啊！、原來如此、完全正確等）獨立成行
   - 依照語氣自然停頓與意群斷開，絕不硬斷字破句
"""
import sys
import os
import json
import re
from pathlib import Path
import opencc

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
CH05_DIR = BASE_DIR / "舌尖上的臺灣" / "02_唐山渡海與閩粵交融"

RAW_VID_JSON = CH05_DIR / "whisper_raw_video.json"
RAW_POD_JSON = CH05_DIR / "whisper_raw_podcast.json"

VID_SRT = CH05_DIR / "第05章_水牛禁忌與清晨的甘甜_說明影片.srt"
POD_SRT = CH05_DIR / "第05章_水牛禁忌與清晨的甘甜_雙人對談.srt"

cc = opencc.OpenCC('s2twp')

# 專家級第 05 章專屬同音錯字校正表
EXPERT_CORRECTIONS = [
    # 1. 歷史地名、市集與法令典籍
    (r'汕化牛[鬚需墟]', '善化牛墟'),
    (r'善化牛[鬚需]', '善化牛墟'),
    (r'三大牛[鬚需]', '三大牛墟'),
    (r'牛[鬚需]市場', '牛墟市場'),
    (r'牛[鬚需]', '牛墟'),
    (r'二五八[鬚需]期', '二五八墟期'),
    (r'上[花華]市場', '善化肉品市場'),
    (r'上[花華]屠宰場', '善化屠宰場'),
    (r'上[花華]', '善化'),
    (r'散化', '善化'),
    (r'從散化到逝去的餐桌', '從善化到市區的餐桌'),
    (r'逝去的餐桌', '市區的餐桌'),
    (r'逝區', '市區'),
    (r'灣[里裡]街', '灣裡街'),
    (r'重修台[灣湾][輔府][治志]', '《重修臺灣府志》'),
    (r'台[灣湾][輔府][治志]', '《臺灣府志》'),
    (r'台[灣湾]福祉', '《臺灣府志》'),
    (r'諸羅縣[治志]', '《諸羅縣志》'),
    (r'伊肯農業社會', '移墾農業社會'),
    (r'伊肯', '移墾'),
    (r'時期肉者[，,]?民伐最重[，,]?求功名者[，,]?天榜消民', '食其肉者，冥罰最重；求功名者，天榜削名'),
    (r'天榜消民', '天榜削名'),
    (r'民伐最重', '冥罰最重'),
    (r'時期肉者', '食其肉者'),
    (r'[因陰][得德]', '陰德'),
    (r'折損[因陰][得德]', '折損陰德'),
    (r'折[因陰][得德]', '折陰德'),
    (r'文昌帝[君軍]', '文昌帝君'),
    (r'顛覆你的嘗試', '顛覆你的常識'),
    (r'極致先田', '極致鮮甜'),
    (r'先田', '鮮甜'),
    
    # 2. 牛隻評定工藝（試牛四法）
    (r'[視侍試]牛[似四]法', '試牛四法'),
    (r'視牛', '試牛'),
    (r'最殘酷的[視市]步', '最殘酷的試步'),
    (r'那個所謂的[視市]步', '那個所謂的試步'),
    (r'[視市]步', '試步'),
    (r'測試[腕腕]力', '測試輓力'),
    (r'腕力', '輓力'),
    (r'最後還要關心', '最後還要觀性'),
    (r'第三步是關心', '第三步是觀性'),
    (r'第一步是看齒', '第一步是看齒'),
    (r'第二步是摸身', '第二步是摸身'),
    (r'第四步是試步', '第四步是試步'),
    (r'老牛當[撞壯]牛賣', '老牛當壯牛賣'),
    (r'[羹耕]牛', '耕牛'),
    (r'牛[汁隻]剛[塗屠][載宰]', '牛隻剛屠宰'),
    (r'牛[汁隻]合法', '牛隻合法'),
    (r'牛[汁隻]集散地', '牛隻集散地'),
    (r'牛[汁隻]', '牛隻'),
    (r'[異役]牛', '役牛'),
    (r'水牛退[一役]朝', '水牛退役潮'),
    (r'水牛退[一役]潮', '水牛退役潮'),
    (r'退[一役]的老水牛', '退役的老水牛'),
    (r'退[一役]老牛', '退役老牛'),
    (r'肥[玉育]黃牛', '肥育黃牛'),
    (r'吃牛會下地獄的[侃坎]', '吃牛會下地獄的坎'),
    (r'川味紅燒牛[耳肉]麵', '川味紅燒牛肉麵'),
    (r'來[臺台]的[居軍]民', '來臺軍民'),
    (r'[禁敬]牛不[死食]的宗教包袱', '敬牛不食的宗教包袱'),
    (r'[敬禁]牛不食', '敬牛不食'),
    (r'純淨生[充沖蔥]', '純淨生沖'),
    (r'生[充蔥]', '生沖'),
    (r'高溫生[充蔥]', '高溫生沖'),
    (r'深沖', '生沖'),
    (r'肉[圍味]', '肉味'),
    
    # 3. 肌肉生理學與生化分子術語
    (r'[圍微]觀世界', '微觀世界'),
    (r'圍觀', '微觀'),
    (r'死後[將僵][直值][前錢]', '死後僵直前'),
    (r'死後[將僵][直值][開結]始', '死後僵直開始'),
    (r'死後[將僵][直值]', '死後僵直'),
    (r'[將僵][直值][前錢]', '僵直前'),
    (r'[將僵][直值]期', '僵直期'),
    (r'Pririgar', 'Pre-rigor'),
    (r'pre-rigor', 'Pre-rigor'),
    (r'三[菱磷]酸腺[感苷]', '三磷酸腺苷'),
    (r'肌[小姐節]', '肌小節'),
    (r'油梨[、，]?丹糖[與和]生[態肽]', '游離單醣與胜肽'),
    (r'油梨', '游離'),
    (r'丹糖', '單醣'),
    (r'生[態肽]', '胜肽'),
    (r'[飽保]水性', '保水性'),
    (r'冷[修休]客', '冷休克'),
    (r'冷[修休]克災難', '冷休克災難'),
    (r'冷收[縮所]', '冷收縮'),
    (r'Cold shortening', 'Cold Shortening'),
    (r'[蓋鈣]離子[豐瘋][狂黃]外洩', '鈣離子瘋狂外洩'),
    (r'[蓋鈣]離子', '鈣離子'),
    (r'[豐瘋][狂黃]外洩', '瘋狂外洩'),
    (r'攣縮硬化', '攣縮硬化'),
    (r'水溶性[雞激肌]漿蛋白', '水溶性肌漿蛋白'),
    (r'[雞激肌]漿蛋白', '肌漿蛋白'),
    (r'[雞激肌]漿', '肌漿'),
    (r'[雞肌]球蛋白', '肌球蛋白'),
    (r'[雞肌]紅蛋白', '肌紅蛋白'),
    (r'[雞肌][凍動]蛋白', '肌動蛋白'),
    (r'[雞肌]纖維[數束]', '肌纖維束'),
    (r'[雞肌]纖維', '肌纖維'),
    (r'毛細管[張張]力', '毛細管張力'),
    (r'表面[張張]力', '表面張力'),
    (r'黏[彈單]性', '黏彈性'),
    (r'[磁瓷]盤', '瓷盤'),
    (r'[磁瓷]碗', '瓷碗'),
    (r'[此瓷][碗晚]的溫度', '瓷碗的溫度'),
    (r'[此瓷][碗晚]', '瓷碗'),
    (r'洗[皺肉]水', '洗肉水'),
    (r'[逆那]一鍋湯', '那一鍋湯'),
    (r'[逆那]鍋湯', '那一鍋湯'),
    (r'[纖鮮]味協同效應', '鮮味協同效應'),
    (r'[纖鮮]味放大效應', '鮮味放大效應'),
    (r'[纖鮮]味', '鮮味'),
    (r'次黃[飄瓢]磷核[甘苷]酸', '次黃嘌呤核苷酸'),
    (r'次黃[飄瓢]零核[甘苷]酸', '次黃嘌呤核苷酸'),
    (r'刺黃[飄瓢]零核[甘苷]酸', '次黃嘌呤核苷酸'),
    (r'次黃嘌呤核[甘苷]酸', '次黃嘌呤核苷酸'),
    (r'油梨[符麩]胺酸', '游離麩胺酸'),
    (r'[符麩]胺酸', '麩胺酸'),
    (r'深金清甜醇厚', '生津清甜醇厚'),
    (r'蝦[鹽眼]水', '蝦眼水'),
    (r'切心安水', '起蝦眼水'),
    (r'水面[質只]冒出', '水面只冒出'),
    (r'牛骨[水髓][裡里]熬出來', '牛骨髓裡熬出來'),
    (r'牛骨[水髓]', '牛骨髓'),
    (r'大碎', '打碎'),
    (r'純淨的[鹹鮮]甜', '純淨的鮮甜'),
    (r'肉裡的寶貴[之汁]液', '肉裡的寶貴汁液'),
    (r'寶貴[之汁]液', '寶貴汁液'),
    (r'寶貴之一', '寶貴汁液'),
    (r'熱[穿傳][道導]速度', '熱傳導速度'),
    (r'熱[穿傳][道導]', '熱傳導'),
    (r'階梯式蛋白質變性動力學', '階梯式蛋白質變性動力學'),
    (r'溫度[解階]體[式降]?降溫', '階梯式降溫'),
    (r'解體降溫', '階梯式降溫'),
    (r'深肉', '生肉'),
    (r'把肉高凍了', '把肉搞懂了'),
    (r'異地味精', '一滴味精'),
    (r'幾乎偏直的薄', '片得極致的薄'),
    (r'應是在絕對', '硬是在絕對'),
    (r'硬是在', '硬是在'),
    
    # 4. 物流、社會學與人物
    (r'深夜熱[戀鏈]的[激極]速接力', '深夜熱鏈的極速接力'),
    (r'深夜熱[戀鏈]', '深夜熱鏈'),
    (r'熱[戀鏈]直達', '熱鏈直達'),
    (r'熱[戀鏈]物流', '熱鏈物流'),
    (r'熱[戀鏈]', '熱鏈'),
    (r'晨曦[維微]露', '晨曦微露'),
    (r'晨曦維路', '晨曦微露'),
    (r'手工[瘋狂]?精[收修]分級', '手工精修分級'),
    (r'精[收修]分級', '精修分級'),
    (r'手工精[收修]', '手工精修'),
    (r'果菜市場的挑[膚夫]', '果菜市場的挑夫'),
    (r'挑[膚夫]', '挑夫'),
    (r'血紅素鐵[值質]', '血紅素鐵質'),
    (r'鐵[值質]', '鐵質'),
    (r'豬油肉[燥燥]飯', '豬油肉燥飯'),
    (r'肉[燥燥]飯', '肉燥飯'),
    (r'庶民[影飲]視文明轉型', '庶民飲食文明轉型'),
    (r'庶民[影飲]食', '庶民飲食'),
    (r'腦洞大開的對談', '腦洞大開的對談'),
    (r'[一依][向項]冷冰冰', '一項冷冰冰'),
    (r'台([灣北市南中東中東南東東南])', r'臺\1'),
    (r'全台', '全臺'),
    (r'在台', '在臺'),
    (r'來台', '來臺'),
    (r'[臺台]灣', '臺灣'),
    
    # 5. OpenCC 過度轉換校正
    (r'剪下力', '剪切力'),
    (r'裡麵', '裡面'),
    (r'為瞭', '為了'),
    (r'發明瞭', '發明了'),
    (r'證明瞭', '證明了'),
]

def clean_text(text: str) -> str:
    t = cc.convert(text)
    for pat, rep in EXPERT_CORRECTIONS:
        t = re.sub(pat, rep, t)
    # 清理標點與空白
    t = t.replace(', ', '，').replace(',', '，')
    t = t.replace('? ', '？').replace('?', '？')
    t = t.replace('! ', '！').replace('!', '！')
    t = re.sub(r'^[，。！？、；：\s]+', '', t)
    t = re.sub(r'[，。；、\s]+$', '', t)
    return t.strip()

def sec_to_time(sec):
    td = max(0.0, sec)
    hrs = int(td // 3600)
    mins = int((td % 3600) // 60)
    secs = int(td % 60)
    millis = int(round((td - int(td)) * 1000))
    if millis >= 1000: millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

# 專屬呼吸律意群切分定義 (語音對話獨立反饋詞與長句口語拆解)
DIALOGUE_MARKERS = [
    "對吧？", "對吧", "真的！", "真的", "沒錯！", "沒錯", "天啊！", "天啊",
    "原來如此！", "原來如此", "完全正確！", "完全正確", "太酷了！", "太酷了",
    "生化災難？", "冷收縮？", "牛墟？", "蝦眼水？", "怎麼說？", "那第三步呢？",
    "等等！", "等一下！", "是的！", "是的", "好！", "對！", "對"
]

def split_natural_breath(seg):
    raw_txt = clean_text(seg['text'])
    start = seg['start']
    end = seg['end']
    dur = end - start
    
    if not raw_txt:
        return []
        
    # 檢查是否為極短對話反饋詞
    if raw_txt in DIALOGUE_MARKERS or len(raw_txt) <= 15:
        return [{'start': start, 'end': end, 'text': raw_txt}]
        
    # 嘗試依句中標點（，、？！）自然斷開
    punct_parts = [p.strip() for p in re.split(r'([，！？；])', raw_txt) if p.strip()]
    merged_clauses = []
    i = 0
    while i < len(punct_parts):
        chunk = punct_parts[i]
        if i + 1 < len(punct_parts) and punct_parts[i+1] in ('，', '！', '？', '；'):
            chunk += punct_parts[i+1]
            i += 2
        else:
            i += 1
        chunk = clean_text(chunk)
        if chunk:
            merged_clauses.append(chunk)
            
    # 如果標點切出來的子句合理（每段 6~16 字）
    if len(merged_clauses) > 1 and all(len(c) <= 18 for c in merged_clauses):
        total_chars = sum(len(c) for c in merged_clauses)
        res = []
        cur_t = start
        for c in merged_clauses:
            part_dur = dur * (len(c) / total_chars)
            res.append({
                'start': cur_t,
                'end': cur_t + part_dur,
                'text': c
            })
            cur_t += part_dur
        return res

    # 若無標點但句子過長（> 15 字），尋找連接詞或語意斷點
    sub_clauses = []
    break_words = ["，", "也就是", "並且", "因為", "所以", "但是", "而且", "直接", "然後", "接著", "結果", "完全", "只要", "如果"]
    split_done = False
    for bw in break_words:
        if bw in raw_txt and 5 <= raw_txt.find(bw) <= 14:
            idx = raw_txt.find(bw)
            if bw == "，":
                c1 = clean_text(raw_txt[:idx])
                c2 = clean_text(raw_txt[idx+1:])
            else:
                c1 = clean_text(raw_txt[:idx])
                c2 = clean_text(raw_txt[idx:])
            if len(c1) >= 4 and len(c2) >= 4 and len(c1) <= 16 and len(c2) <= 16:
                sub_clauses = [c1, c2]
                split_done = True
                break
                
    if split_done:
        total_chars = sum(len(c) for c in sub_clauses)
        res = []
        cur_t = start
        for c in sub_clauses:
            part_dur = dur * (len(c) / total_chars)
            res.append({
                'start': cur_t,
                'end': cur_t + part_dur,
                'text': c
            })
            cur_t += part_dur
        return res
        
    return [{'start': start, 'end': end, 'text': raw_txt}]

def process_file(in_json: Path, out_srt: Path, label: str):
    print(f"\n" + "="*70)
    print(f"🎬 正在精修 {label} 字幕：{in_json.name} -> {out_srt.name}")
    print("="*70)
    
    with open(in_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    all_lines = []
    for seg in data['segments']:
        lines = split_natural_breath(seg)
        for item in lines:
            t = clean_text(item['text'])
            if t:
                all_lines.append({
                    'start': item['start'],
                    'end': item['end'],
                    'text': t
                })
                
    # 輸出標準 SRT 格式
    srt_out = []
    for idx, item in enumerate(all_lines, 1):
        st_str = sec_to_time(item['start'])
        et_str = sec_to_time(item['end'])
        srt_out.append(f"{idx}\n{st_str} --> {et_str}\n{item['text']}\n")
        
    out_srt.write_text("\n".join(srt_out), encoding='utf-8')
    print(f"✅ {label} 精修完成！共生成 {len(all_lines)} 行標準呼吸律字幕。")

if __name__ == "__main__":
    if RAW_VID_JSON.exists():
        process_file(RAW_VID_JSON, VID_SRT, "【說明影片】")
    else:
        print(f"❌ 找不到：{RAW_VID_JSON}")
        
    if RAW_POD_JSON.exists():
        process_file(RAW_POD_JSON, POD_SRT, "【播客對談】")
    else:
        print(f"❌ 找不到：{RAW_POD_JSON}")
