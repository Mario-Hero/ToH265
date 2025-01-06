#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Created by Mario Chen, 2025.01.06, Dongguan
# My Github site: https://github.com/Mario-Hero

import subprocess
import os
import sys

def is_h264(input_path):
    # Check if the video codec is H264 using ffmpeg
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'default=nw=1:nk=1', input_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    codec = result.stdout.decode('utf-8').strip()
    print(f'{input_path} codec is {codec}')
    return codec == 'h264'

def convert_video(input_path):
    # Check if the video codec is H264
    if os.path.isdir(input_path):
        for child_dir in os.listdir(input_path):
            convert_video(os.path.join(input_path, child_dir))

    if not input_path.lower().endswith('.mp4'):
        print(f"The file {input_path} is not an mp4 file")
        return False
    if not is_h264(input_path):
        return False

    # Get the original bitrate using ffmpeg
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=bit_rate', '-of', 'default=nw=1:nk=1', input_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    original_bitrate = int(result.stdout)
    
    # Calculate the new bitrate (half of the original)
    new_bitrate = original_bitrate // 2
    
    # Create a temporary output file name
    name, ext = os.path.splitext(input_path)
    i = 1
    temp_output_path = f'{name}_temp_{i}{ext}'
    while os.path.exists(temp_output_path):
        i += 1
        temp_output_path = f'{name}_temp_{i}{ext}'

    # Convert the video using ffmpeg
    subprocess.run(
        ['ffmpeg', '-hwaccel','cuvid','-i', input_path, '-c:v', 'hevc_nvenc', '-b:v', str(new_bitrate), '-c:a', 'copy', temp_output_path]
    )

    # Replace the original video with the converted video
    os.replace(temp_output_path, input_path)
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_video.py <input_video>")
        sys.exit(1)
    ret = True
    for input_video in sys.argv[1:]:
        ret = ret & convert_video(input_video)
    
    if len(sys.argv) == 2 and not ret:
        os.system("pause")