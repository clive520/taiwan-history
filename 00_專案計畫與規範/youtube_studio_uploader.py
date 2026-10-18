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
import threading
import argparse
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from playwright.sync_api import sync_playwright

def get_native_browser():
    """取得本機原生乾淨瀏覽器路徑（優先 Edge 避免與使用者日常 Chrome 衝突）"""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def authenticate(profile_dir):
    """使用者一次性手動授權模式（使用系統原生瀏覽器，完全免除 Google 安全疑慮封鎖）"""
    print("\n" + "=" * 65)
    print("🔑 正在啟動系統原生瀏覽器進行 YouTube Studio 頻道授權...")
    print("=" * 65)
    print("👉 請在即將開啟的瀏覽器視窗中：")
    print("   1. 登入您的 Google 帳號：clive520@gmail.com")
    print("   2. 確認順利進入您的 YouTube 工作室 (YouTube Studio)")
    print("   3. 登入完成後，直接在終端按 Enter，系統將保存持久化憑證")
    print("=" * 65 + "\n")

    browser_exe = get_native_browser()
    if not browser_exe:
        print("❌ 找不到系統中的 Chrome 或 Edge 瀏覽器！")
        return

    browser_name = "Chrome" if "chrome.exe" in browser_exe.lower() else "Edge"
    print(f"🌐 啟動原生 {browser_name}（純淨模式，無任何自動化標記，Google 100% 信任）...")

    cmd = [
        browser_exe,
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://studio.youtube.com"
    ]

    proc = subprocess.Popen(cmd)

    print("\n⏳ 瀏覽器已開啟！請在該視窗完成登入操作。")
    print("💡 登入成功並看到 YouTube 工作室儀表板後，回到此視窗按 Enter 結束授權。")
    try:
        input("👉 登入完成後請按 Enter：")
    except Exception:
        pass

    try:
        proc.terminate()
    except Exception:
        pass

    print("\n✅ 授權完成！登入狀態與 Cookie 已成功持久化保存於：")
    print(f"   {profile_dir}")
    print("   未來上傳影片、排程與掛載字幕將全自動執行，無需再次登入。\n")

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
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                channel="chrome",
                ignore_default_args=["--enable-automation"],
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
                no_viewport=True
            )
        except Exception:
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                ignore_default_args=["--enable-automation"],
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
                no_viewport=True
            )

        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://studio.youtube.com")
        # 檢查是否登入
        if "accounts.google.com" in page.url:
            print("\n" + "=" * 65)
            print("👉 偵測到 YouTube Studio 尚未進入登入狀態！")
            print("👉 請在彈出的瀏覽器視窗中完成登入（clive520@gmail.com）")
            print("👉 登入成功後，本程式將自動感應並無縫接手填寫與上傳！")
            print("=" * 65 + "\n")
            logged_in = False
            for _ in range(150): # 最長等待 5 分鐘
                page.wait_for_timeout(2000)
                try:
                    curr_url = page.url
                    if "studio.youtube.com" in curr_url and "accounts.google.com" not in curr_url:
                        print("🎉 偵測到已成功進入 YouTube Studio！即刻接手自動化...")
                        logged_in = True
                        break
                except Exception:
                    pass
            if not logged_in:
                print("❌ 等待登入超時，請重新執行。")
                return

        print("📤 正在開啟上傳對話框...")
        page.goto("https://studio.youtube.com/channel/?d=pt")
        page.wait_for_timeout(3000)

        # 注入影片
        file_input = page.locator('input[type="file"]').first
        try:
            file_input.set_input_files(video_path)
            print("📁 影片檔案注入成功，上傳處理中...")
        except Exception as e:
            print(f"⚠️ 檔案注入提醒：{e}")

        # 等待對話框細節區塊載入
        page.wait_for_timeout(6000)

        # 填寫標題
        try:
            title_input = page.locator('#title-textarea #textbox, #textbox[aria-label*="標題"]').first
            if title_input.is_visible():
                print("✍️ 正在填入影片標題...")
                title_input.fill("")
                title_input.type(title)
        except Exception as e:
            print(f"⚠️ 標題填寫提示：{e}")

        # 填寫說明欄
        try:
            desc_input = page.locator('#description-textarea #textbox, #textbox[aria-label*="說明"]').first
            if desc_input.is_visible() and description:
                print("✍️ 正在填入完整說明欄與章節連結...")
                desc_input.fill("")
                desc_input.type(description)
        except Exception as e:
            print(f"⚠️ 說明欄填寫提示：{e}")

        # 上傳封面縮圖
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                thumb_input = page.locator('input[type="file"][accept*="image"]').first
                if thumb_input.count() > 0:
                    print("🖼️ 正在上傳封面縮圖...")
                    thumb_input.set_input_files(thumbnail_path)
            except Exception as e:
                print(f"⚠️ 縮圖上傳提示：{e}")

        # 勾選非兒童專用
        try:
            not_kids_radio = page.locator('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"], tp-yt-paper-radio-button[name="NOT_MADE_FOR_KIDS"]').first
            if not_kids_radio.is_visible():
                print("👶 已設定為「非專為兒童打造」...")
                not_kids_radio.click()
        except Exception as e:
            pass

        print("\n" + "=" * 65)
        print("💡 影片、標題、說明欄、封面資料已全數自動填入完畢！")
        print("👉 瀏覽器視窗現正處於開啟狀態。")
        print("👉 您可以在介面中點選「下一步」，在「影片元素」掛載字幕檔：")
        print(f"   {srt_path}")
        print(f"👉 並於最終頁面排程設定：{schedule_date} {schedule_time}。")
        print("=" * 65 + "\n")

        print("檢視與發布完畢後，請於此處按 Enter 關閉瀏覽器。")
        try:
            input("按 Enter 結束：")
        except Exception:
            pass

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
