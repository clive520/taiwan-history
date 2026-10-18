@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_EXE=C:\Users\admin\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"

"%PYTHON_EXE%" -X utf8 "00_專案計畫與規範\youtube_api_uploader.py" --video "01_史前文明與南島之源\第01章_黑潮上的遠古足跡_說明影片.mp4" --srt "01_史前文明與南島之源\第01章_黑潮上的遠古足跡_說明影片.srt" --thumbnail "assets\images\ch01\ch01_hero_banner.jpg" --title "【臺灣史 EP01】黑潮上的遠古足跡：長濱文化、左鎮人定年真相與舊石器時代的曙光" --desc-file "01_史前文明與南島之源\ch01_desc.txt" --schedule "2026-10-26 17:30" --playlist "台灣史"

echo.
pause
