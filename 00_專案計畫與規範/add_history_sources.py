# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

CH06_NOTEBOOK = "c5354897-5c84-4a22-81e7-bc4ee2d0585b"
CH07_NOTEBOOK = "c3127091-0bff-4fea-be05-93089cfaeeb1"

base_dir = Path("D:/Antigravity/科技歷史/臺灣史")
history_dir = base_dir / "歷史資料"

ch06_files = []
ch07_files = []

for root, dirs, files in os.walk(history_dir):
    for f in files:
        if f.startswith("06"):
            ch06_files.append(Path(root) / f)
        elif f.startswith("07"):
            ch07_files.append(Path(root) / f)

print(f"找到 Ch06 考證史料: {ch06_files}")
print(f"找到 Ch07 考證史料: {ch07_files}")

for f in ch06_files:
    print(f"\n[EXEC] nlm source add {CH06_NOTEBOOK} --file {f.name} --wait")
    res = subprocess.run(["nlm", "source", "add", CH06_NOTEBOOK, "--file", str(f), "--wait"], capture_output=True, text=True, encoding="utf-8")
    print(res.stdout)
    if res.stderr:
        print(res.stderr, file=sys.stderr)

for f in ch07_files:
    print(f"\n[EXEC] nlm source add {CH07_NOTEBOOK} --file {f.name} --wait")
    res = subprocess.run(["nlm", "source", "add", CH07_NOTEBOOK, "--file", str(f), "--wait"], capture_output=True, text=True, encoding="utf-8")
    print(res.stdout)
    if res.stderr:
        print(res.stderr, file=sys.stderr)

print("\n✅ 史料添加完成！")
