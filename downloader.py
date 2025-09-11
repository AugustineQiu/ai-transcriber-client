#!/usr/bin/env python3
"""
音频下载模块
Audio Downloader Module
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import hashlib
import time

import yt_dlp
from tqdm import tqdm

from config import get_config

@dataclass
class DownloadResult:
    """下载结果"""
    success: bool
    file_path: Optional[str] = None
    title: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    format: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AudioDownloader:
    """音频下载器"""
    
    def __init__(self):
        """初始化下载器"""
        self.config = get_config()
        self.download_dir = Path(self.config.download_dir)
        self.download_dir.mkdir(exist_ok=True, parents=True)
        
        # 临时目录
        self.temp_dir = Path(self.config.temp_dir) if self.config.temp_dir else None
        
        # 进度回调函数
        self.progress_callback: Optional[Callable] = None
        
        print(f"📂 下载目录: {self.download_dir}")
    
    def set_progress_callback(self, callback: Callable):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def _get_yt_dlp_options(self, output_path: str) -> Dict[str, Any]:
        """获取yt-dlp配置选项"""
        
        # 质量映射
        quality_map = {
            "best": "bestaudio/best",
            "good": "bestaudio[abr<=128]/best[abr<=128]", 
            "fast": "worstaudio/worst"
        }
        
        # 基础选项 (增强反检测)
        audio_format = getattr(self.config, 'audio_format', 'mp3')
        options = {
            'format': quality_map.get(self.config.audio_quality, "bestaudio/best"),
            'outtmpl': f"{str(output_path)}.{audio_format}",
            'extractaudio': True,
            'audioformat': audio_format,
            'audioquality': '0' if self.config.audio_quality == 'best' else '5',
            'no_warnings': not self.config.verbose,
            'quiet': not self.config.verbose,
            'no_color': not self.config.use_colors,
            
            # 反检测措施
            'force_ipv4': True,  # 强制使用IPv4
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'headers': {
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['dash', 'hls'],
                }
            },
            'cachedir': False,  # 禁用缓存
        }
        
        # 添加进度钩子
        if self.config.show_progress:
            options['progress_hooks'] = [self._progress_hook]
        
        # 临时目录
        if self.temp_dir:
            self.temp_dir.mkdir(exist_ok=True, parents=True)
            options['temp_dir'] = str(self.temp_dir)
        
        return options
    
    def _progress_hook(self, d: Dict[str, Any]):
        """yt-dlp进度回调"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = d.get('downloaded_bytes', 0) / d['total_bytes'] * 100
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                if self.progress_callback:
                    self.progress_callback({
                        'status': 'downloading',
                        'percent': percent,
                        'speed': speed,
                        'eta': eta
                    })
        
        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback({
                    'status': 'finished',
                    'filename': d.get('filename')
                })
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        # 移除或替换不安全的字符
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # 限制长度
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename
    
    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """获取视频信息"""
        try:
            options = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True
            }
            
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
                
        except Exception as e:
            print(f"❌ 获取视频信息失败: {e}")
            return None
    
    def download_audio(self, url: str, custom_filename: Optional[str] = None) -> DownloadResult:
        """
        下载音频文件
        
        Args:
            url: 视频URL
            custom_filename: 自定义文件名
        
        Returns:
            DownloadResult: 下载结果
        """
        print(f"🎬 开始处理: {url}")
        
        try:
            # 获取视频信息
            info = self.get_video_info(url)
            if not info:
                return DownloadResult(
                    success=False,
                    error_message="无法获取视频信息"
                )
            
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            
            print(f"📹 标题: {title}")
            print(f"⏱️ 时长: {duration}秒")
            print(f"👤 作者: {uploader}")
            
            # 检查文件大小限制
            filesize_approx = info.get('filesize_approx') or info.get('filesize', 0)
            if filesize_approx > self.config.max_file_size:
                return DownloadResult(
                    success=False,
                    error_message=f"文件太大: {filesize_approx / 1024 / 1024:.1f}MB > {self.config.max_file_size / 1024 / 1024:.1f}MB"
                )
            
            # 生成文件名
            if custom_filename:
                filename = custom_filename
            else:
                safe_title = self._sanitize_filename(title)
                timestamp = int(time.time())
                filename = f"{safe_title}_{timestamp}"
            
            # 输出路径（不带扩展名，yt-dlp会自动添加）
            output_path = self.download_dir / filename
            
            # yt-dlp选项
            options = self._get_yt_dlp_options(str(output_path))
            
            print(f"📥 开始下载...")
            
            # 下载
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            
            # 查找下载的文件
            downloaded_files = list(self.download_dir.glob(f"{filename}*"))
            if not downloaded_files:
                return DownloadResult(
                    success=False,
                    error_message="下载完成但找不到文件"
                )
            
            downloaded_file = downloaded_files[0]
            file_size = downloaded_file.stat().st_size
            
            print(f"✅ 下载完成: {downloaded_file.name}")
            print(f"📊 文件大小: {file_size / 1024 / 1024:.1f}MB")
            
            return DownloadResult(
                success=True,
                file_path=str(downloaded_file),
                title=title,
                duration=duration,
                file_size=file_size,
                format=downloaded_file.suffix[1:],  # 去掉点号
                metadata={
                    'uploader': uploader,
                    'url': url,
                    'download_time': time.time()
                }
            )
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 下载失败: {error_msg}")
            
            return DownloadResult(
                success=False,
                error_message=error_msg
            )
    
    def download_video(self, url: str, custom_filename: Optional[str] = None) -> DownloadResult:
        """
        下载视频文件（包含视频和音频）
        
        Args:
            url: 视频URL
            custom_filename: 自定义文件名（可选）
            
        Returns:
            DownloadResult: 下载结果
        """
        try:
            print(f"🔍 获取视频信息...")
            info = self.get_video_info(url)
            
            if not info:
                return DownloadResult(
                    success=False,
                    error_message="无法获取视频信息"
                )
            
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            
            print(f"🎬 标题: {title}")
            print(f"⏱️ 时长: {duration}秒")
            print(f"👤 作者: {uploader}")
            
            # 检查文件大小限制
            filesize_approx = info.get('filesize_approx') or info.get('filesize', 0)
            if filesize_approx > self.config.max_file_size:
                return DownloadResult(
                    success=False,
                    error_message=f"文件太大: {filesize_approx / 1024 / 1024:.1f}MB > {self.config.max_file_size / 1024 / 1024:.1f}MB"
                )
            
            # 生成文件名
            if custom_filename:
                filename = custom_filename
            else:
                safe_title = self._sanitize_filename(title)
                timestamp = int(time.time())
                filename = f"{safe_title}_{timestamp}"
            
            # 获取视频质量配置
            video_quality = getattr(self.config, 'video_quality', '720p')
            
            # 视频质量映射
            quality_map = {
                "best": "bestvideo+bestaudio/best",
                "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]", 
                "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
                "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]"
            }
            
            # 视频下载选项
            options = {
                'format': quality_map.get(video_quality, "bestvideo[height<=720]+bestaudio/best"),
                'outtmpl': f"{str(self.download_dir / filename)}.%(ext)s",
                'merge_output_format': 'mp4',  # 合并为mp4格式
                'no_warnings': not self.config.verbose,
                'quiet': not self.config.verbose,
                'no_color': not self.config.use_colors,
                
                # 反检测措施
                'force_ipv4': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                'headers': {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                },
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'skip': ['dash', 'hls'],
                    }
                },
                'cachedir': False,
                'progress_hooks': [self._progress_hook] if self.progress_callback else []
            }
            
            print(f"📥 开始下载视频...")
            
            # 下载
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            
            # 查找下载的文件
            downloaded_files = list(self.download_dir.glob(f"{filename}*"))
            if not downloaded_files:
                return DownloadResult(
                    success=False,
                    error_message="下载完成但找不到文件"
                )
            
            downloaded_file = downloaded_files[0]
            file_size = downloaded_file.stat().st_size
            
            print(f"✅ 视频下载完成: {downloaded_file.name}")
            print(f"📊 文件大小: {file_size / 1024 / 1024:.1f}MB")
            
            return DownloadResult(
                success=True,
                file_path=str(downloaded_file),
                title=title,
                duration=duration,
                file_size=file_size,
                format=downloaded_file.suffix[1:],  # 去掉点号
                metadata={
                    'uploader': uploader,
                    'url': url,
                    'download_time': time.time(),
                    'type': 'video'
                }
            )
            
        except Exception as e:
            error_msg = f"视频下载失败: {str(e)}"
            print(f"❌ {error_msg}")
            
            return DownloadResult(
                success=False,
                error_message=error_msg
            )
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                print(f"🧹 清理临时文件: {self.temp_dir}")
            except Exception as e:
                print(f"⚠️ 清理临时文件失败: {e}")
    
    def get_supported_sites(self) -> list:
        """获取支持的网站列表"""
        try:
            with yt_dlp.YoutubeDL() as ydl:
                extractors = ydl.list_extractors()
                sites = [extractor.IE_NAME for extractor in extractors[:50]]  # 前50个
                return sites
        except Exception:
            return ["youtube", "bilibili", "twitter", "vimeo", "soundcloud"]


def test_downloader():
    """测试下载器"""
    print("🧪 测试音频下载器...")
    
    downloader = AudioDownloader()
    
    # 测试获取视频信息
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"🔍 测试获取视频信息: {test_url}")
    info = downloader.get_video_info(test_url)
    
    if info:
        print(f"✅ 视频信息获取成功:")
        print(f"  标题: {info.get('title')}")
        print(f"  时长: {info.get('duration')}秒")
        print(f"  作者: {info.get('uploader')}")
    else:
        print("❌ 视频信息获取失败")
    
    # 显示支持的网站
    sites = downloader.get_supported_sites()
    print(f"\n🌐 支持的网站 (前10个): {', '.join(sites[:10])}")


if __name__ == "__main__":
    test_downloader()