#!/usr/bin/env python3
"""
统一GUI程序 - AI转录器客户端
Unified GUI Program - AI Transcriber Client
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
import sys
from pathlib import Path
import json
from typing import Optional, Dict, Any

# 导入我们的模块
from config import get_config, ConfigManager
from downloader import AudioDownloader, DownloadResult  
from uploader import ServerUploader, UploadResult

class UnifiedTranscriberGUI:
    """统一转录器GUI界面"""
    
    def __init__(self):
        """初始化GUI"""
        self.root = tk.Tk()
        self.root.title("🎤 AI转录器 - 本地客户端")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 配置
        self.config = get_config()
        self.config_manager = ConfigManager()
        
        # 工具实例
        self.downloader = AudioDownloader()
        self.uploader = ServerUploader()
        
        # 设置进度回调
        self.downloader.set_progress_callback(self._progress_callback)
        self.uploader.set_progress_callback(self._progress_callback)
        
        # 当前任务
        self.current_task = None
        self.current_thread = None
        
        # 初始化界面
        self._setup_ui()
        self._setup_styles()
        
        print("🎮 GUI界面已启动")
    
    def _setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 配置按钮样式
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
        style.configure('Config.TButton', font=('Arial', 9))
        
        # 配置标签样式
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 10))
    
    def _setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🎤 AI转录器本地客户端", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="支持YouTube、Bilibili等数百个视频平台", style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # URL输入区域
        url_frame = ttk.LabelFrame(main_frame, text=" 🎬 输入视频URL ", padding="10")
        url_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(0, weight=1)
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=('Arial', 10))
        url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 粘贴按钮
        paste_btn = ttk.Button(url_frame, text="📋 粘贴", command=self._paste_url)
        paste_btn.grid(row=0, column=1)
        
        # 示例链接
        example_label = ttk.Label(url_frame, text="示例: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        example_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # 操作按钮区域
        action_frame = ttk.LabelFrame(main_frame, text=" 🚀 选择操作 ", padding="10")
        action_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        action_frame.columnconfigure((0, 1, 2), weight=1)
        
        # 三个主要操作按钮
        download_video_btn = ttk.Button(action_frame, text="📹 下载视频", 
                                      command=self._download_video, style='Action.TButton')
        download_video_btn.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        download_audio_btn = ttk.Button(action_frame, text="🎵 下载音频", 
                                      command=self._download_audio, style='Action.TButton')
        download_audio_btn.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        transcribe_btn = ttk.Button(action_frame, text="🎤 下载并转录", 
                                  command=self._download_and_transcribe, style='Action.TButton')
        transcribe_btn.grid(row=0, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # 配置和帮助按钮
        config_frame = ttk.Frame(action_frame)
        config_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        config_btn = ttk.Button(config_frame, text="⚙️ 配置", command=self._open_config, style='Config.TButton')
        config_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        help_btn = ttk.Button(config_frame, text="❓ 帮助", command=self._show_help, style='Config.TButton')
        help_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        test_btn = ttk.Button(config_frame, text="🧪 测试", command=self._run_test, style='Config.TButton')
        test_btn.pack(side=tk.LEFT)
        
        # 进度区域
        progress_frame = ttk.LabelFrame(main_frame, text=" 📊 进度和日志 ", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=1, padx=(10, 0))
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=15, font=('Consolas', 9))
        self.log_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 底部状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.server_status_var = tk.StringVar(value="检查服务器连接中...")
        server_label = ttk.Label(status_frame, textvariable=self.server_status_var)
        server_label.grid(row=0, column=0, sticky=tk.W)
        
        # 初始化检查服务器连接
        threading.Thread(target=self._check_server_connection, daemon=True).start()
    
    def _paste_url(self):
        """粘贴URL"""
        try:
            clipboard = self.root.clipboard_get()
            self.url_var.set(clipboard)
            self._log("📋 已粘贴URL")
        except tk.TclError:
            self._log("⚠️ 剪贴板为空或无法访问")
    
    def _log(self, message: str):
        """添加日志"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def _progress_callback(self, data: Dict[str, Any]):
        """进度回调函数"""
        if data.get('status') == 'downloading':
            percent = data.get('percent', 0)
            self.progress_var.set(percent)
            self.status_var.set(f"下载中 {percent:.1f}%")
        elif data.get('status') == 'uploading':
            percent = data.get('percent', 0)
            self.progress_var.set(percent)
            self.status_var.set(f"上传中 {percent:.1f}%")
        elif data.get('status') == 'finished':
            self.progress_var.set(100)
            self.status_var.set("完成")
    
    def _check_server_connection(self):
        """检查服务器连接状态"""
        if self.uploader.test_connection():
            self.server_status_var.set(f"🌐 服务器连接正常: {self.config.server_url}")
        else:
            self.server_status_var.set("⚠️ 服务器连接失败")
    
    def _get_url(self) -> Optional[str]:
        """获取并验证URL"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入视频URL")
            return None
        if not (url.startswith('http://') or url.startswith('https://')):
            messagebox.showerror("错误", "请输入有效的URL（以http://或https://开头）")
            return None
        return url
    
    def _download_video(self):
        """下载视频"""
        url = self._get_url()
        if not url:
            return
        
        self._log("🎬 开始下载视频...")
        self._run_in_thread(self._do_download_video, url)
    
    def _download_audio(self):
        """下载音频"""
        url = self._get_url()
        if not url:
            return
        
        self._log("🎵 开始下载音频...")
        self._run_in_thread(self._do_download_audio, url)
    
    def _download_and_transcribe(self):
        """下载并转录"""
        url = self._get_url()
        if not url:
            return
        
        # 检查服务器连接
        if not self.uploader.test_connection():
            messagebox.showerror("错误", "服务器连接失败，请检查网络或配置")
            return
        
        self._log("🎤 开始下载并转录...")
        self._run_in_thread(self._do_download_and_transcribe, url)
    
    def _run_in_thread(self, func, *args):
        """在新线程中运行函数"""
        if self.current_thread and self.current_thread.is_alive():
            messagebox.showwarning("警告", "任务正在进行中，请等待完成")
            return
        
        self.progress_var.set(0)
        self.status_var.set("处理中...")
        self.current_thread = threading.Thread(target=func, args=args, daemon=True)
        self.current_thread.start()
    
    def _do_download_video(self, url: str):
        """执行视频下载"""
        try:
            self._log("📹 开始下载视频文件（包含视频和音频）...")
            result = self.downloader.download_video(url)
            
            if result.success:
                self._log(f"✅ 视频下载完成: {result.file_path}")
                self._log(f"📊 文件大小: {result.file_size / 1024 / 1024:.1f}MB")
                self._log(f"⏱️ 时长: {result.duration}秒")
                messagebox.showinfo("成功", f"视频文件已保存到:\n{result.file_path}")
            else:
                self._log(f"❌ 下载失败: {result.error_message}")
                messagebox.showerror("错误", f"下载失败:\n{result.error_message}")
        
        except Exception as e:
            error_msg = f"下载异常: {str(e)}"
            self._log(f"❌ {error_msg}")
            messagebox.showerror("错误", error_msg)
        
        finally:
            self.status_var.set("就绪")
    
    def _do_download_audio(self, url: str):
        """执行音频下载"""
        try:
            self._log("🎵 开始下载音频文件（仅音频，无视频）...")
            result = self.downloader.download_audio(url)
            
            if result.success:
                self._log(f"✅ 音频下载完成: {result.file_path}")
                self._log(f"📊 文件大小: {result.file_size / 1024 / 1024:.1f}MB")
                self._log(f"⏱️ 时长: {result.duration}秒")
                messagebox.showinfo("成功", f"音频文件已保存到:\n{result.file_path}")
            else:
                self._log(f"❌ 音频下载失败: {result.error_message}")
                messagebox.showerror("错误", f"音频下载失败:\n{result.error_message}")
        
        except Exception as e:
            error_msg = f"下载异常: {str(e)}"
            self._log(f"❌ {error_msg}")
            messagebox.showerror("错误", error_msg)
        
        finally:
            self.status_var.set("就绪")
    
    def _do_download_and_transcribe(self, url: str):
        """执行下载并转录"""
        try:
            # 第一步：下载音频
            self._log("🎵 第1步: 下载音频...")
            download_result = self.downloader.download_audio(url)
            
            if not download_result.success:
                self._log(f"❌ 音频下载失败: {download_result.error_message}")
                messagebox.showerror("错误", f"音频下载失败:\n{download_result.error_message}")
                return
            
            self._log(f"✅ 音频下载完成: {download_result.file_path}")
            
            # 第二步：上传并转录
            self._log("🚀 第2步: 上传并转录...")
            upload_result = self.uploader.upload_file(download_result.file_path)
            
            if not upload_result.success:
                self._log(f"❌ 上传失败: {upload_result.error}")
                messagebox.showerror("错误", f"上传失败:\n{upload_result.error}")
                return
            
            self._log(f"✅ 上传成功! 任务ID: {upload_result.task_id}")
            
            # 第三步：等待转录完成
            self._log("⏳ 第3步: 等待转录完成...")
            final_result = self.uploader.wait_for_completion(upload_result.task_id)
            
            if final_result.get('status') == 'completed':
                self._log("🎉 转录完成!")
                
                # 下载结果
                result_file = self.uploader.download_result(upload_result.task_id)
                if result_file:
                    self._log(f"📄 结果已保存: {result_file}")
                
                messagebox.showinfo("成功", f"转录完成!\n任务ID: {upload_result.task_id}\n音频文件: {download_result.file_path}")
            else:
                error_msg = final_result.get('error', '转录失败')
                self._log(f"❌ 转录失败: {error_msg}")
                messagebox.showerror("错误", f"转录失败:\n{error_msg}")
        
        except Exception as e:
            error_msg = f"处理异常: {str(e)}"
            self._log(f"❌ {error_msg}")
            messagebox.showerror("错误", error_msg)
        
        finally:
            self.status_var.set("就绪")
    
    def _open_config(self):
        """打开配置窗口"""
        ConfigWindow(self.root, self.config_manager, callback=self._reload_config)
    
    def _reload_config(self):
        """重新加载配置"""
        self.config = get_config()
        self.downloader = AudioDownloader()
        self.uploader = ServerUploader()
        self.downloader.set_progress_callback(self._progress_callback)
        self.uploader.set_progress_callback(self._progress_callback)
        self._log("🔄 配置已重新加载")
        threading.Thread(target=self._check_server_connection, daemon=True).start()
    
    def _run_test(self):
        """运行系统测试"""
        self._log("🧪 开始系统测试...")
        threading.Thread(target=self._do_test, daemon=True).start()
    
    def _do_test(self):
        """执行系统测试"""
        try:
            # 测试1: 下载器
            self._log("🔍 测试1: 音频下载器...")
            info = self.downloader.get_video_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            if info:
                self._log(f"✅ 下载器测试通过: {info.get('title')}")
            else:
                self._log("❌ 下载器测试失败")
            
            # 测试2: 服务器连接
            self._log("🔍 测试2: 服务器连接...")
            if self.uploader.test_connection():
                self._log("✅ 服务器连接测试通过")
            else:
                self._log("❌ 服务器连接测试失败")
            
            # 测试3: 支持的网站
            self._log("🔍 测试3: 支持的网站...")
            sites = self.downloader.get_supported_sites()
            self._log(f"✅ 支持 {len(sites)} 个网站: {', '.join(sites[:5])}...")
            
            self._log("🎉 系统测试完成!")
            
        except Exception as e:
            self._log(f"❌ 测试异常: {str(e)}")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
🎤 AI转录器本地客户端 - 使用帮助

📋 主要功能:
• 📹 下载视频: 下载视频文件到本地
• 🎵 下载音频: 下载音频文件到本地  
• 🎤 下载并转录: 下载音频并上传到服务器转录

🌐 支持的网站:
• YouTube, Bilibili, Twitter, Vimeo
• SoundCloud 等数百个视频平台

⚙️ 配置选项:
• 音频质量: best(最佳), good(良好), fast(快速)
• 下载目录: 可自定义文件保存位置
• 服务器设置: 转录服务器地址和API密钥

🔧 使用步骤:
1. 输入或粘贴视频URL
2. 选择对应的操作
3. 等待处理完成

❓ 常见问题:
• 403错误: 程序已集成最新反检测策略
• 网络问题: 检查网络连接和防火墙设置
• 服务器错误: 检查服务器地址和API密钥配置

📞 获取支持:
如有问题请联系技术支持或查看项目文档。
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("帮助")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=('Arial', 10))
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
    
    def run(self):
        """运行GUI"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 用户退出")
        except Exception as e:
            print(f"❌ GUI异常: {e}")


class ConfigWindow:
    """配置窗口"""
    
    def __init__(self, parent, config_manager: ConfigManager, callback=None):
        self.parent = parent
        self.config_manager = config_manager
        self.callback = callback
        
        # 当前配置
        self.config = get_config()
        
        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ 配置")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置配置界面"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 服务器配置
        server_frame = ttk.LabelFrame(main_frame, text=" 🌐 服务器配置 ", padding="10")
        server_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(server_frame, text="服务器地址:").grid(row=0, column=0, sticky=tk.W)
        self.server_url_var = tk.StringVar(value=self.config.server_url)
        ttk.Entry(server_frame, textvariable=self.server_url_var, width=50).grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(server_frame, text="API密钥:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.api_key_var = tk.StringVar(value=self.config.api_key or "")
        ttk.Entry(server_frame, textvariable=self.api_key_var, width=50, show="*").grid(row=1, column=1, padx=(10, 0), pady=(5, 0))
        
        # 下载配置
        download_frame = ttk.LabelFrame(main_frame, text=" 📥 下载配置 ", padding="10")
        download_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(download_frame, text="音频质量:").grid(row=0, column=0, sticky=tk.W)
        self.quality_var = tk.StringVar(value=self.config.audio_quality)
        quality_combo = ttk.Combobox(download_frame, textvariable=self.quality_var, 
                                   values=["best", "good", "fast"], state="readonly")
        quality_combo.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        ttk.Label(download_frame, text="音频格式:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.audio_format_var = tk.StringVar(value=getattr(self.config, 'audio_format', 'mp3'))
        format_combo = ttk.Combobox(download_frame, textvariable=self.audio_format_var,
                                  values=["mp3", "wav", "flac", "m4a", "ogg"], state="readonly")
        format_combo.grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)
        
        ttk.Label(download_frame, text="视频质量:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.video_quality_var = tk.StringVar(value=getattr(self.config, 'video_quality', '720p'))
        video_quality_combo = ttk.Combobox(download_frame, textvariable=self.video_quality_var,
                                         values=["best", "1080p", "720p", "480p", "360p"], state="readonly")
        video_quality_combo.grid(row=2, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)
        
        ttk.Label(download_frame, text="下载目录:").grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.download_dir_var = tk.StringVar(value=self.config.download_dir)
        dir_frame = ttk.Frame(download_frame)
        dir_frame.grid(row=3, column=1, padx=(10, 0), pady=(5, 0), sticky=(tk.W, tk.E))
        ttk.Entry(dir_frame, textvariable=self.download_dir_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="浏览", command=self._browse_directory).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 其他选项
        options_frame = ttk.LabelFrame(main_frame, text=" ⚙️ 其他选项 ", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.verbose_var = tk.BooleanVar(value=self.config.verbose)
        ttk.Checkbutton(options_frame, text="显示详细信息", variable=self.verbose_var).pack(anchor=tk.W)
        
        self.progress_var = tk.BooleanVar(value=self.config.show_progress)
        ttk.Checkbutton(options_frame, text="显示进度条", variable=self.progress_var).pack(anchor=tk.W)
        
        self.colors_var = tk.BooleanVar(value=self.config.use_colors)
        ttk.Checkbutton(options_frame, text="使用彩色输出", variable=self.colors_var).pack(anchor=tk.W)
        
        self.keep_files_var = tk.BooleanVar(value=getattr(self.config, 'keep_local_files', False))
        ttk.Checkbutton(options_frame, text="保留本地下载文件", variable=self.keep_files_var).pack(anchor=tk.W)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="保存", command=self._save_config).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=self.window.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="恢复默认", command=self._reset_defaults).pack(side=tk.LEFT)
    
    def _browse_directory(self):
        """浏览目录"""
        directory = filedialog.askdirectory(initialdir=self.download_dir_var.get())
        if directory:
            self.download_dir_var.set(directory)
    
    def _reset_defaults(self):
        """恢复默认设置"""
        if messagebox.askyesno("确认", "确定要恢复默认设置吗？"):
            self.server_url_var.set("http://localhost:8000")
            self.api_key_var.set("")
            self.quality_var.set("best")
            self.audio_format_var.set("mp3")
            self.video_quality_var.set("720p")
            self.download_dir_var.set("./downloads")
            self.keep_files_var.set(False)
            self.verbose_var.set(True)
            self.progress_var.set(True)
            self.colors_var.set(True)
    
    def _save_config(self):
        """保存配置"""
        try:
            # 更新配置
            new_config = {
                'server_url': self.server_url_var.get().strip(),
                'api_key': self.api_key_var.get().strip() or None,
                'audio_quality': self.quality_var.get(),
                'audio_format': self.audio_format_var.get(),
                'video_quality': self.video_quality_var.get(),
                'download_dir': self.download_dir_var.get().strip(),
                'keep_local_files': self.keep_files_var.get(),
                'verbose': self.verbose_var.get(),
                'show_progress': self.progress_var.get(),
                'use_colors': self.colors_var.get()
            }
            
            # 验证配置
            if not new_config['server_url']:
                messagebox.showerror("错误", "服务器地址不能为空")
                return
            
            if not new_config['download_dir']:
                messagebox.showerror("错误", "下载目录不能为空")
                return
            
            # 保存配置
            self.config_manager.update(**new_config)
            self.config_manager.save_config()
            messagebox.showinfo("成功", "配置已保存")
            
            # 执行回调
            if self.callback:
                self.callback()
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败:\n{str(e)}")


def main():
    """主函数"""
    print("🚀 启动统一GUI程序...")
    
    try:
        # 创建并运行GUI
        app = UnifiedTranscriberGUI()
        app.run()
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())