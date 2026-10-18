# -*- coding: utf-8 -*-
import json

transcript_path = r"C:\Users\admin\.gemini\antigravity\brain\e6ad31e6-5e47-44d3-86ec-3061599c52d4\.system_generated\logs\transcript.jsonl"
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        idx = data.get("step_index")
        if idx in range(60, 150):
            tc = data.get("tool_calls", [])
            for c in tc:
                args = c.get("args", {})
                if "CommandLine" in args:
                    cmd = args["CommandLine"]
                    if "whisper" in cmd or "transcribe" in cmd or "python" in cmd or "pip" in cmd or "nlm" in cmd or "json" in cmd:
                        print(f"Step {idx}: {cmd[:150]}")
