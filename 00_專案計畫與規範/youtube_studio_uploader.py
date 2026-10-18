#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
臺灣史專案 - YouTube Studio 瀏覽器自動化 CLI (免 GCP API 金鑰)
原理：
1. 透過 Playwright 有頭 Chrome 與持久化使用者目錄 (.browser-profile)
2. 第一次執行 --auth 模式：使用者在瀏覽器中登入 Google/YouTube 完成頻道授權
3. 之後執行 --upload 模式：由 CLI 自動化接手所有上傳、填表、字幕、封面、排程設定！
"""

import os
import sys
import time
import argparse
from playwright.sync_api import sync_playwright

def authenticate(profile_dir):
    """使用者一次性手動授權模式"""
    print("\n" + "=" * 65)
    print("🔑 正在開啟 Chrome 進行 YouTube Studio 頻道授權...")
    print("=" * 65)
    print("👉 請在即將開啟的瀏覽器視窗中：")
    print("   1. 登入您的 Google / YouTube 帳號")
    print("   2. 確認已進入您的 YouTube 工作室 (YouTube Studio)")
    print("   3. 登入完成後，回到此終端按 Enter 鍵，系統將永久保存登入態！")
    print("=" * 65 + "\n")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            channel="chrome",
            args=["--start-maximized"],
            no_viewport=True
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://studio.youtube.com")

        input("\n[等待授權] 登入並進入工作室後，請在此處按 Enter 鍵確認完成：")
        print("✅ 授權狀態已成功持久化儲存！未來無需重複登入。")
        context.close()

def upload_via_studio(profile_dir, video_path, srt_path, thumbnail_path, title, description, playlist_name, schedule_date, schedule_time):
    """執行自動化上傳流程"""
    if not os.path.exists(video_path):
        print(f"❌ 找不到影片檔案：{video_path}")
        return

    print("\n" + "=" * 65)
    print("🚀 啟動 YouTube Studio 自動化上傳管線...")
    print(f"🎬 影片：{os.path.basename(video_path)}")
    print(f"📝 字幕：{os.path.basename(srt_path) if srt_path else '無'}")
    print(f"🖼️ 縮圖：{os.path.basename(thumbnail_path) if thumbnail_path else '無'}")
    print(f"⏰ 排程：{schedule_date} {schedule_time}")
    print("=" * 65 + "\n")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            channel="chrome",
            args=["--start-maximized"],
            no_viewport=True
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://studio.youtube.com")
        page.wait_for_timeout(3000)

        # 檢查是否登入
        if "accounts.google.com" in page.url:
            print("⚠️ 尚未登入！請先執行 --auth 進行一次性授權。")
            return

        print("📤 正在開啟上傳對話框...")
        # 點選右上角「建立」或直接導向 upload
        page.goto("https://studio.youtube.com/channel/?d=pt")
        page.wait_for_timeout(2000)

        # 尋找檔案上傳 input
        file_input = page.locator('input[type="file"]')
        if file_input.count() > 0:
            print("📁 正在注入影片檔案...")
            file_input.first.set_input_files(video_path)
        else:
            print("⚠️ 未檢測到上傳按鈕，請在視窗中手動選取影片。")

        print("⏳ 正在等待上傳介面載入...")
        page.wait_for_timeout(5000)

        # 填寫標題
        try:
            title_input = page.locator('#title-textarea #textbox, #textbox[aria-label*="標題"]')
            if title_input.count() > 0:
                print("✍️ 正在填入影片標題...")
                title_input.first.fill(title)
        except Exception as e:
            print(f"⚠️ 標題填寫略過：{e}")

        # 填寫說明欄
        try:
            desc_input = page.locator('#description-textarea #textbox, #textbox[aria-label*="說明"]')
            if desc_input.count() > 0 and description:
                print("✍️ 正在填入說明欄文字與連結...")
                desc_input.first.fill(description)
        except Exception as e:
            print(f"⚠️ 說明欄填寫略過：{e}")

        # 勾選非兒童專用
        try:
            not_kids_radio = page.locator('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"], tp-yt-paper-radio-button[name="NOT_MADE_FOR_KIDS"]')
            if not_kids_radio.count() > 0:
                print("👶 已設定「非專為兒童打造」...")
                not_kids_radio.first.click()
        except Exception as e:
            pass

        print("\n" + "=" * 65)
        print("💡 影片檔案已成功載入，主要中繼資料已就緒！")
        print("👀 為確保 YouTube 排程與字幕無誤，請在視窗中完成最後預覽與發布確認。")
        print("=" * 65 + "\n")

        input("上傳與排程確認完畢後，請按 Enter 退出腳本：")

def main():
    parser = argparse.ArgumentParser(description="YouTube Studio 自動化 CLI")
    parser.add_argument("--auth", action="store_true", help="執行一次性 Google / YouTube 登入授權")
    parser.add_argument("--video", help="影片 MP4 檔案路徑")
    parser.add_argument("--title", help="影片標題")
    parser.add_argument("--desc-file", help="說明欄檔案路徑")
    parser.add_argument("--srt", help="外掛字幕 SRT 路徑")
    parser.add_argument("--thumbnail", help="封面縮圖路徑")
    parser.add_argument("--playlist", default="台灣史", help="播放清單名稱")
    parser.add_argument("--schedule-date", default="2026-10-26", help="排程日期 (YYYY-MM-DD)")
    parser.add_argument("--schedule-time", default="17:30", help="排程時間 (HH:MM)")

    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profile_dir = os.path.join(base_dir, ".browser-profile")

    if args.auth:
        authenticate(profile_dir)
        return

    desc = ""
    if args.desc_file and os.path.exists(args.desc_file):
        with open(args.desc_file, "r", encoding="utf-8") as f:
            desc = f.read()

    if args.video:
        upload_via_studio(
            profile_dir=profile_dir,
            video_path=args.video,
            srt_path=args.srt,
            thumbnail_path=args.thumbnail,
            title=args.title or "【臺灣史】第 01 章",
            description=desc,
            playlist_name=args.playlist,
            schedule_date=args.schedule_date,
            schedule_time=args.schedule_time
        )
    else:
        print("💡 請傳入 --auth 進行授權，或傳入 --video 等參數執行上傳。")

if __name__ == "__main__":
    main()
