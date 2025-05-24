# ToH265 视频转码脚本

Python脚本，能把视频文件以合适的码率转换为H265格式，缩小文件大小。使用ffmpeg和nvidia显卡加速。

A Python script that can convert video files to H265 format at proper bitrate. Use ffmpeg and Nvidia graphics card acceleration.

## 依赖 Dependency

### Python 3.5+

### ffmpeg

[Download FFmpeg](https://ffmpeg.org/download.html) 安装 ffmpeg 并添加到环境变量PATH

Install ffmpeg and add it to the environment variable PATH

### cuda for Nvidia Card

[CUDA Toolkit  Downloads](https://developer.nvidia.com/cuda-downloads) N卡需要安装CUDA. 

Install CUDA if you are using Nvidia graphics card.

## 用法 Usage

下载 `ToH265.py`, 把视频文件或文件夹拖动到Python脚本上即可开始转码为h265。如果视频为H264格式，则导出的码率为原H264视频的一半，大小就会变为原视频的一半，从而节省空间。如果拖入的是文件夹，则会把该文件夹下的所有视频都转换了。具体码率见下方表格，H264以外的编码格式对应转换比率还在测试当中。

**使用前请配置好参数！**

Download `ToH265.py`, drag the video file or folder onto the Python script to start transcoding to H265. If the video is in H264 format, the exported bitrate is half of the original H264 video. The size will become half of the original video to save disk space.If dragged into a folder, all videos in that folder will be converted. The specific bitrate is shown in the table below, and the conversion ratios for encoding formats other than H264 are still under testing. 

**Please configure the parameters before use!**

## 支持的视频格式 Supported Format

| 输入编码格式：视频格式<br/>Input encoding format: Video format | 导出视频的码率比例<br/>Bitrate ratio of exported video |
| ------------------------------------------------------------ | ------------------------------------------------------ |
| H264: MP4, MKV, MOV                                          | 0.5                                                    |
| VC1: WMV                                                     | 0.5                                                    |

## 参数配置 Parameters

```Python
# 硬件加速配置 Hardware for accelerations
HARDWARE = HW.NVIDIA # HW.NVIDIA or HW.INTEL or HW.AMD

# 转码大小限制。如果视频小于 4GB 就不转码。（因为视频太小，转了也节省不了多少空间）
# Transcoding size limit. If the video is less than 4GB, it will not be transcoded. (Because the video is too small, even if you convert it, it won't save much space)
TRANS_VIDEO_SIZE = 4  # GB. If the video size is less than this, do not convert
```

## License

This project is licensed under the GNU Lesser General Public License (LGPL) 2.1. See the [LICENSE](./LICENSE) file for details.