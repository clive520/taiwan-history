import os
import sys
from refine_food_ch10_srt import build_srt_from_whisper_json

base_dir = r"d:\Antigravity\科技歷史\臺灣史\舌尖上的臺灣\03_帝國之眼與東洋滋味"
video_json = os.path.join(base_dir, "whisper_raw_video.json")
video_srt = os.path.join(base_dir, "第10章_山嵐間的東方美人_說明影片.srt")

pod_json = os.path.join(base_dir, "whisper_raw_podcast.json")
pod_srt = os.path.join(base_dir, "第10章_山嵐間的東方美人_雙人對談.srt")

print("Processing Video Subtitles...")
n_v = build_srt_from_whisper_json(video_json, video_srt)

print("\nProcessing Podcast Subtitles...")
n_p = build_srt_from_whisper_json(pod_json, pod_srt)

print(f"\n🎉 All Chapter 10 SRTs refined successfully!")
print(f"Video SRT lines: {n_v}")
print(f"Podcast SRT lines: {n_p}")
print(f"Total Subtitle Lines: {n_v + n_p}")
