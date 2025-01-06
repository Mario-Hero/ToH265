# h264toh265 视频转码脚本

Python脚本，能把H264格式的MP4文件，以一半的码率转换为H265格式。使用ffmpeg和nvidia显卡加速。

A Python script that can convert H264 format MP4 files to H265 format at half the bitrate. Use ffmpeg and Nvidia graphics card acceleration.

## 依赖 Dependency

### Python 3.5+

### ffmpeg

[Download FFmpeg](https://ffmpeg.org/download.html) 安装 ffmpeg 并添加到环境变量PATH

Install ffmpeg and add it to the environment variable PATH

### cuda

[CUDA Toolkit  Downloads](https://developer.nvidia.com/cuda-downloads) 安装CUDA. 

Install CUDA.

## 用法 Usage

下载 `h264toh265.py`, 把视频文件或文件夹拖动到Python脚本上即可开始转码为h265。码率为原H264视频的一半。如果拖入的是文件夹，则会把该文件夹下的所有h264格式视频都转换了。

Download `h264toh265.py`, drag a video file or folder onto the Python script to start transcoding. The bitrate is half of the original H264 video. If dragged a folder, all H264 format videos in that folder will be converted.

## License

This project is licensed under the GNU Lesser General Public License (LGPL) 2.1. See the [LICENSE](./LICENSE) file for details.