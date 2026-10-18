import os
import json
import argparse
from faster_whisper import WhisperModel

def transcribe_audio(input_media, output_json, prompt="", model_size="medium"):
    print(f"[*] 載入 Faster-Whisper 模型: {model_size}...")
    try:
        model = WhisperModel(model_size, device="cuda", compute_type="float16")
        print("[*] 啟用 CUDA (GPU) 加速推理")
    except Exception as e:
        print(f"[!] 使用 CPU 推理 (int8，啟用 8 線程)")
        model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=8)

    print(f"[*] 轉錄媒體檔案: {input_media}")
    print(f"[*] 注入 Initial Prompt: {prompt}")

    segments, info = model.transcribe(
        input_media,
        language="zh",
        initial_prompt=prompt,
        word_timestamps=True,
        beam_size=5,
        vad_filter=True
    )

    print(f"[*] 辨識語言: {info.language} (機率: {info.language_probability:.2f})")

    words_list = []
    full_text = []

    for seg in segments:
        full_text.append(seg.text)
        if seg.words:
            for w in seg.words:
                words_list.append({
                    "word": w.word,
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 3)
                })

    result = {
        "text": "".join(full_text),
        "language": info.language,
        "duration": info.duration,
        "words": words_list
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_json)), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[✓] 成功產出單字級時間戳 JSON: {output_json}")
    print(f"[*] 總單字數: {len(words_list)}，時長: {info.duration:.1f} 秒")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Faster-Whisper 單字級轉錄工具")
    parser.add_argument("input", help="輸入之音訊或影片檔路徑")
    parser.add_argument("output", help="輸出之 JSON 檔案路徑")
    parser.add_argument("--prompt", default="", help="專有名詞 Initial Prompt")
    parser.add_argument("--model", default="medium", help="Whisper 模型大小 (預設: medium)")
    args = parser.parse_args()

    transcribe_audio(args.input, args.output, args.prompt, args.model)
