#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人機協同 YouTube 上傳啟動器 (HITL YouTube Upload Launcher)
遵循 hitl-browser 規範：
1. 啟動本機可見 Chrome (headless=False)
2. 掛載持久化使用者設定檔 (.browser-profile) 保留登入狀態
3. 自動開啟目標目錄並導向 YouTube Studio 上傳介面
"""

import os
import sys
import subprocess
import time
from playwright.sync_api import sync_playwright

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ch01_dir = os.path.join(base_dir, "01_史前文明與南島之源")
    video_file = os.path.join(ch01_dir, "第01章_黑潮上的遠古足跡_說明影片.mp4")
    srt_file = os.path.join(ch01_dir, "第01章_黑潮上的遠古足跡_說明影片.srt")
    banner_file = os.path.join(base_dir, "assets", "images", "ch01", "ch01_hero_banner.jpg")
    profile_dir = os.path.join(base_dir, ".browser-profile")

    print("\n" + "=" * 65)
    print("🚀 臺灣史第 01 章 YouTube 人機協同上傳啟動器")
    print("=" * 65)
    print(f"🎬 影片檔案：{video_file}")
    print(f"📝 字幕檔案：{srt_file}")
    print(f"🖼️ 建議封面：{banner_file}")
    print(f"🌐 說明欄連結：https://clive520.github.io/taiwan-history/article.html?id=ch01")
    print("=" * 65 + "\n")

    # 1. 自動以檔案總管開啟檔案目錄並反白選取影片，方便直接拖曳上傳
    try:
        subprocess.Popen(f'explorer.exe /select,"{video_file}"')
        print("📂 已為您開啟本機檔案總管並反白選取影片檔案。")
    except Exception as e:
        print(f"⚠️ 無法自動開啟檔案總管：{e}")

    # 2. 啟動 Playwright 可見 Chrome 視窗
    print("🌐 正在啟動可視化 Chrome 瀏覽器...")
    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                channel="chrome",
                args=["--start-maximized"],
                no_viewport=True
            )
        except Exception as e:
            print(f"無法以系統 Chrome 啟動，嘗試 Chromium：{e}")
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                args=["--start-maximized"],
                no_viewport=True
            )

        page = context.pages[0] if context.pages else context.new_page()
        upload_url = "https://studio.youtube.com/channel/?d=pt"
        page.goto(upload_url)

        print("\n" + "=" * 65)
        print("💡 瀏覽器已開啟至 YouTube Studio。")
        print("👉 請在視窗中確認 Google / YouTube 帳號登入與授權。")
        print("👉 授權後即可將檔案總管中的影片拖入上傳！")
        print("👉 說明文案與排程時間（2026-10-26 17:30）已整理於：")
        print("   01_史前文明與南島之源\\YouTube_第01章發布資訊與文案.md")
        print("=" * 65 + "\n")

        print("視窗將保持開啟，操作完成或檢視完畢後，請於此處按 Enter 結束本腳本。")
        try:
            input("按 Enter 鍵結束：")
        except KeyboardInterrupt:
            pass
        print("程式結束。")

if __name__ == "__main__":
    main()
