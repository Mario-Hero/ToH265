#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# Transform video to H265 format
# Created by Mario Chen, 2025.01.06, Dongguan
# My Github site: https://github.com/Mario-Hero

import subprocess
import os
import sys
from enum import Enum

class HW(Enum):
    '''Hardware acceleration options'''
    NVIDIA = 1
    INTEL = 2
    AMD = 3
    CPU = 4  # Don't use CPU, it's too slow

HARDWARE = HW.NVIDIA
ENCODER = {
    HW.NVIDIA: "hevc_nvenc",
    HW.INTEL: "hevc_qsv",
    HW.AMD: "hevc_amf",
    HW.CPU: "libx265",
}.get(HARDWARE)
TRANS_VIDEO_SIZE = 4  # GB. If the video size is less than this, do not convert

CODEC_BITRATE_SCALE = {"h264": 0.5, "wmv2": 0.5, "vc1": 0.5}
VIDEO_EXT_SUPPORTED = (".mp4", ".mkv", ".wmv", ".mov")
TARGET_EXT = (".mp4", ".mkv", ".mov")
PREFERRED_EXT = ".mp4"  # if the file not in TARGET_EXT, convert to this format


def is_tool_in_path(tool_name, cmd="-version"):
    """Check if the tool is in the system PATH"""
    try:
        # Windows下需要加shell=True，Linux下不需要，但加了也能兼容
        result = subprocess.run(
            [tool_name, cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            check=True,
        )
        # 只要能正常执行，并且返回码为0，就说明找到了
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception as _:
        # 其他异常返回False
        return False


def is_file_over_ngb(file_path, n):
    """Check if the file size is greater than n GB"""
    try:
        file_size = os.path.getsize(file_path)
        return file_size > int(n * 1024 * 1024 * 1024)
    except OSError as e:
        print(f"Error: {e}")
        return False


def get_codec(input_path):
    """Get the codec of the video file"""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=nw=1:nk=1",
            input_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    codec = result.stdout.decode("utf-8").strip()
    print(f"{input_path} codec is {codec}")
    return codec


def ffprobe_bitrate(input_path, stream_bitrate=True):
    """Get the bitrate of the video file"""
    return subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=bit_rate" if stream_bitrate else "format=bit_rate",
            "-of",
            "default=nw=1:nk=1",
            input_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )


def get_sound_bitrate(input_path) -> str:
    """Get the sound bitrate of the video file"""
    sound_bitrate_result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=bit_rate",
            "-of",
            "default=nw=1:nk=1",
            input_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    if sound_bitrate_result.returncode != 0:
        print(
            f"Error getting sound bitrate for {input_path}: {sound_bitrate_result.stdout.decode('utf-8')}"
        )
        return ""
    else:
        sound_bitrate_res = sound_bitrate_result.stdout.decode("utf-8").strip()
        if sound_bitrate_res == "N/A":
            print(f"Sound bitrate not available for {input_path}")
            return ""
        else:
            return str(int(sound_bitrate_res) // 1000) + "k"


def get_bitrate(input_path) -> float:
    """Get the bitrate of the video file"""
    bitrate_result = ffprobe_bitrate(input_path)
    if bitrate_result.returncode != 0:
        print(
            f"Error getting bitrate for {input_path}: {bitrate_result.stdout.decode('utf-8')}"
        )
        return -1
    bitrate_res = bitrate_result.stdout.decode("utf-8").strip()
    if bitrate_res == "N/A":
        print(f"Stream bitrate not available for {input_path}")
        format_bitrate_result = ffprobe_bitrate(input_path, False)
        bitrate_res = format_bitrate_result.stdout.decode("utf-8").strip()
        if bitrate_res == "N/A":
            print(f"Format bitrate not available for {input_path}")
            return -1
    return float(bitrate_res)


def convert_video(input_path) -> bool:
    """Convert the video to H265 format"""
    if os.path.isdir(input_path):
        for child_dir in os.listdir(input_path):
            convert_video(os.path.join(input_path, child_dir))

    if not input_path.lower().endswith(VIDEO_EXT_SUPPORTED):
        print(f"The file {input_path} is not a supported video format.")
        return False

    codec = get_codec(input_path)
    if codec == "hevc":
        print(f"The video {input_path} is already in HEVC format.")
        return True

    if codec not in CODEC_BITRATE_SCALE:
        print(f"The codec {codec} is not supported")
        return False

    if not is_file_over_ngb(input_path, TRANS_VIDEO_SIZE):
        print(f"The file {input_path} is not over {TRANS_VIDEO_SIZE} GB")
        return False

    original_bitrate = get_bitrate(input_path)
    if original_bitrate < 0:
        print(f"Error getting bitrate for {input_path}")
        return False
    print(f"Original bitrate of {input_path} is {original_bitrate}")

    # Calculate the new bitrate
    new_bitrate = int(original_bitrate * CODEC_BITRATE_SCALE[codec])

    # Create a temporary output file name
    name, ext = os.path.splitext(input_path)
    original_ext = ext
    if ext.lower() not in TARGET_EXT:
        # If the file is not in the target extensions, convert to the preferred extension
        ext = PREFERRED_EXT

    i = 1
    temp_output_path = f"{name}_temp_{i}{ext}"
    while os.path.exists(temp_output_path):
        i += 1
        temp_output_path = f"{name}_temp_{i}{ext}"

    i = 1
    final_output_path = f"{name}{ext}"
    if input_path != final_output_path:
        # the final_output_path change the extension,
        # but still need to check if it exists
        i = 1
        final_output_path = f"{name}_{i}{ext}"
        while os.path.exists(final_output_path):
            final_output_path = f"{name}_{i}{ext}"
            i += 1

    if original_ext.lower() != ".wmv":
        trans_result = trans_codec(input_path, new_bitrate, temp_output_path)
    else:
        trans_result = trans_codec_same_sound_bitrate(
            input_path, new_bitrate, temp_output_path
        )
    if trans_result.returncode != 0:
        print(f"Error converting {input_path}")
        if os.path.exists(temp_output_path):
            os.remove(temp_output_path)
        return False
    if os.path.getsize(temp_output_path) >= os.path.getsize(input_path):
        print("The converted video is larger than the original video.")
        os.remove(temp_output_path)
        return False
    else:
        # Replace the original video with the converted video
        os.remove(input_path)
        os.rename(temp_output_path, final_output_path)
        return True


def trans_codec(input_path, new_bitrate, temp_output_path):
    """Run ffmpeg to convert the video codec. Copy the audio stream"""
    return subprocess.run(
        [
            "ffmpeg",
            "-hwaccel",
            "auto",
            "-i",
            input_path,
            "-c:v",
            ENCODER,
            "-b:v",
            str(new_bitrate),
            "-c:a",
            "copy",
            temp_output_path,
        ],
        check=True,
    )


def trans_codec_same_sound_bitrate(input_path, new_bitrate, temp_output_path):
    """Run ffmpeg to convert the video codec, but keep the same audio bitrate in aac format"""
    sound_bitrate = get_sound_bitrate(input_path)
    print(f"Get sound bitrate: {sound_bitrate}")
    if sound_bitrate != "":
        return subprocess.run(
            [
                "ffmpeg",
                "-hwaccel",
                "auto",
                "-i",
                input_path,
                "-c:v",
                ENCODER,
                "-b:v",
                str(new_bitrate),
                "-c:a",
                "aac",
                "-b:a",
                sound_bitrate,  # Copy the audio bitrate
                temp_output_path,
            ],
            check=True,
        )
    else:
        return subprocess.run(
            [
                "ffmpeg",
                "-hwaccel",
                "auto",
                "-i",
                input_path,
                "-c:v",
                ENCODER,
                "-b:v",
                str(new_bitrate),
                "-c:a",
                "aac",
                "-q:a",
                "2",  # VBR audio quality
                temp_output_path,
            ],
            check=True,
        )


if __name__ == "__main__":
    if not is_tool_in_path("ffmpeg"):
        print("ffmpeg not found, please install ffmpeg and add it to your PATH.")
        os.system("pause")
        sys.exit(1)
    if not is_tool_in_path("ffprobe"):
        print("ffprobe not found, please install ffprobe and add it to your PATH.")
        os.system("pause")
        sys.exit(1)
    if HARDWARE == HW.NVIDIA and not is_tool_in_path("nvcc", "--version"):
        print(
            "You choose nvidia graphics card, but cuda not found, please install cuda"
        )
        os.system("pause")
        sys.exit(1)
    if len(sys.argv) < 2:
        print("Usage: python3 toh265.py <videos or folders>")
        os.system("pause")
        sys.exit(1)

    ret = True
    for input_video in sys.argv[1:]:
        ret = ret & convert_video(input_video)

    if len(sys.argv) == 2 and not ret:
        os.system("pause")
