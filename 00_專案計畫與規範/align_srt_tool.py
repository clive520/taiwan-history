import json
import re
import difflib
import argparse
import sys

def format_timestamp(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours = millis // 3600000
    millis %= 3600000
    minutes = millis // 60000
    millis %= 60000
    secs = millis // 1000
    millis %= 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def align_and_export_srt(approved_txt_path, whisper_json_path, output_srt_path):
    print(f"[*] 讀取文字校對稿: {approved_txt_path}")
    with open(approved_txt_path, 'r', encoding='utf-8-sig') as f:
        raw_lines = [l.strip() for l in f if l.strip()]

    approved_lines = []
    has_numbered = any(re.match(r'^\d+\.\s*(.+)$', l) for l in raw_lines)
    for l in raw_lines:
        if l.startswith('【') or l.startswith('說明') or l.startswith('本稿') or l.startswith('#') or l.startswith('註') or l.startswith('您可以'):
            continue
        m = re.match(r'^\d+\.\s*(.+)$', l)
        if m:
            approved_lines.append(m.group(1))
        elif not has_numbered:
            approved_lines.append(l)

    print(f"[*] 總字幕行數: {len(approved_lines)}")

    print(f"[*] 讀取 Whisper 單字時間戳: {whisper_json_path}")
    with open(whisper_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict) and 'words' in data:
        whisper_words = data['words']
    elif isinstance(data, list):
        whisper_words = data
    else:
        raise ValueError("Invalid whisper words json format")

    whisper_chars, whisper_char_to_word = [], []
    for w_idx, w in enumerate(whisper_words):
        for c in w['word']:
            clean_c = re.sub(r'[^\w]', '', c)
            if clean_c:
                whisper_chars.append(clean_c)
                whisper_char_to_word.append(w_idx)

    whisper_full_str = ''.join(whisper_chars)

    approved_char_boundaries, approved_chars = [], []
    curr_idx = 0
    for l in approved_lines:
        clean_l = re.sub(r'[^\w]', '', l)
        st_c, ed_c = curr_idx, curr_idx + len(clean_l)
        approved_char_boundaries.append((st_c, ed_c))
        approved_chars.extend(list(clean_l))
        curr_idx = ed_c

    approved_full_str = ''.join(approved_chars)

    print("[*] 執行字元級序列匹配 (Sequence Matching)...")
    matcher = difflib.SequenceMatcher(None, whisper_full_str, approved_full_str)
    ratio = matcher.ratio()
    print(f"[*] 文字與音訊匹配度 (Similarity): {ratio:.2%}")

    app_to_whisp = [None] * len(approved_full_str)
    for b in matcher.get_matching_blocks():
        for i in range(b.size):
            app_to_whisp[b.b + i] = b.a + i

    last_val = 0
    for i in range(len(app_to_whisp)):
        if app_to_whisp[i] is None:
            next_val = len(whisper_full_str) - 1
            for j in range(i + 1, len(app_to_whisp)):
                if app_to_whisp[j] is not None:
                    next_val = app_to_whisp[j]
                    break
            app_to_whisp[i] = min(max(last_val, int(round((last_val + next_val) / 2))), len(whisper_full_str) - 1)
        else:
            last_val = app_to_whisp[i]

    subtitles = []
    for l_idx, (st_c, ed_c) in enumerate(approved_char_boundaries):
        if st_c == ed_c:
            continue
        w_start_idx = app_to_whisp[st_c]
        w_end_idx = app_to_whisp[min(ed_c - 1, len(app_to_whisp) - 1)]
        s_time = whisper_words[whisper_char_to_word[w_start_idx]]['start']
        e_time = whisper_words[whisper_char_to_word[w_end_idx]]['end']
        subtitles.append({'index': l_idx + 1, 'start': s_time, 'end': e_time, 'text': approved_lines[l_idx]})

    print("[*] 執行時間軸防呆校正 (單調性、防重疊、最小顯示時間保證)...")
    for i in range(len(subtitles)):
        # 保證每條字幕至少顯示 0.4 秒
        if subtitles[i]['end'] - subtitles[i]['start'] < 0.4:
            subtitles[i]['end'] = subtitles[i]['start'] + 0.4

        if i > 0:
            if subtitles[i]['start'] < subtitles[i-1]['start']:
                subtitles[i]['start'] = subtitles[i-1]['start'] + 0.05
            if subtitles[i]['start'] < subtitles[i-1]['end']:
                # 若與前一條重疊，檢查是否能平分或推移
                if subtitles[i]['start'] >= subtitles[i-1]['start'] + 0.35:
                    subtitles[i-1]['end'] = subtitles[i]['start']
                else:
                    subtitles[i-1]['end'] = subtitles[i-1]['start'] + 0.35
                    subtitles[i]['start'] = subtitles[i-1]['end']
                if subtitles[i]['end'] - subtitles[i]['start'] < 0.4:
                    subtitles[i]['end'] = subtitles[i]['start'] + 0.4

        if subtitles[i]['end'] <= subtitles[i]['start']:
            subtitles[i]['end'] = subtitles[i]['start'] + 0.5

    max_duration = whisper_words[-1]['end'] + 0.5
    if subtitles[-1]['end'] > max_duration:
        subtitles[-1]['end'] = max_duration

    print(f"[*] 寫入標準 UTF-8-BOM SRT 字幕: {output_srt_path}")
    with open(output_srt_path, 'w', encoding='utf-8-sig') as f:
        for s in subtitles:
            f.write(f"{s['index']}\n{format_timestamp(s['start'])} --> {format_timestamp(s['end'])}\n{s['text']}\n\n")

    print(f"[OK] 大功告成！共產出 {len(subtitles)} 條精準字幕。")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='高品質字幕強制對齊工具')
    parser.add_argument('--approved', required=True, help='文字校對稿路徑 (.txt)')
    parser.add_argument('--whisper', required=True, help='Whisper 單字時間戳路徑 (.json)')
    parser.add_argument('--output', required=True, help='輸出 SRT 路徑 (.srt)')
    args = parser.parse_args()

    align_and_export_srt(args.approved, args.whisper, args.output)

