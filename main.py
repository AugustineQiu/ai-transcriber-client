#!/usr/bin/env python3
"""
AI转录器本地客户端 - 主程序
AI Transcriber Local Client - Main Program
"""

import sys
import os
import argparse
import signal
from pathlib import Path
from typing import Optional

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config import ConfigManager, get_config
from downloader import AudioDownloader, DownloadResult
from uploader import ServerUploader, UploadResult

# 颜色输出支持
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    
    def colored_print(text: str, color: str = 'white'):
        colors = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE,
            'bright_red': Fore.LIGHTRED_EX,
            'bright_green': Fore.LIGHTGREEN_EX,
        }
        print(colors.get(color, Fore.WHITE) + text)
        
except ImportError:
    def colored_print(text: str, color: str = 'white'):
        print(text)


class TranscriberClient:
    """AI转录器客户端"""
    
    def __init__(self):
        """初始化客户端"""
        self.config = get_config()
        self.downloader = AudioDownloader()
        self.uploader = ServerUploader()
        self.current_operation = None
        
        # 设置信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器，用于优雅退出"""
        colored_print(f"\n⚠️ 收到退出信号 ({signum})，正在清理...", 'yellow')
        
        if self.current_operation:
            colored_print("🛑 正在中断当前操作...", 'yellow')
        
        # 清理临时文件
        self.downloader.cleanup_temp_files()
        
        colored_print("👋 程序已退出", 'cyan')
        sys.exit(0)
    
    def show_banner(self):
        """显示程序横幅"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                  🎤 AI转录器本地客户端                      ║
║               AI Transcriber Local Client                ║
║                                                          ║
║   🎬 支持YouTube、Bilibili等数百个视频平台                  ║
║   🚀 本地下载，服务器转录，完全绕过反机器人检测               ║
║   💾 支持多种音频格式和质量选择                             ║
║                                                          ║
║                    版本: 1.0.0                          ║
╚═══════════════════════════════════════════════════════════╝
"""
        colored_print(banner, 'cyan')
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
🔧 使用方法:
  
基本用法:
  python main.py <视频URL>
  
高级用法:
  python main.py <视频URL> [选项]

📋 可用选项:
  -h, --help           显示此帮助信息
  -c, --config         运行配置向导
  -s, --server URL     指定服务器地址
  -q, --quality TYPE   音频质量 (best/good/fast)
  -o, --output DIR     下载目录
  -k, --keep-local     保留本地下载文件
  -w, --wait           等待转录完成并显示结果
  -v, --verbose        显示详细信息
  --no-color           禁用彩色输出
  --test               运行系统测试

📋 使用示例:
  python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  python main.py "https://www.bilibili.com/video/BV1xx411c7mu" -q good -w
  python main.py --config
  python main.py --test
"""
        print(help_text)
    
    def run_system_test(self):
        """运行系统测试"""
        colored_print("🧪 运行系统测试...", 'blue')
        
        # 测试1: 配置检查
        colored_print("\n1️⃣ 配置检查", 'yellow')
        config = get_config()
        colored_print(f"✅ 服务器地址: {config.server_url}")
        colored_print(f"✅ 下载目录: {config.download_dir}")
        colored_print(f"✅ 音频质量: {config.audio_quality}")
        
        # 测试2: 下载器检查
        colored_print("\n2️⃣ 下载器检查", 'yellow')
        try:
            downloader = AudioDownloader()
            sites = downloader.get_supported_sites()
            colored_print(f"✅ yt-dlp可用，支持{len(sites)}个平台")
            colored_print(f"   热门平台: {', '.join(sites[:5])}")
        except Exception as e:
            colored_print(f"❌ 下载器检查失败: {e}", 'red')
        
        # 测试3: 服务器连接
        colored_print("\n3️⃣ 服务器连接检查", 'yellow')
        uploader = ServerUploader()
        if uploader.test_connection():
            colored_print("✅ 服务器连接正常")
        else:
            colored_print("❌ 服务器连接失败", 'red')
        
        colored_print("\n🎯 系统测试完成!", 'green')
    
    def process_url(self, url: str, wait_for_completion: bool = False) -> bool:
        """
        处理视频URL
        
        Args:
            url: 视频URL
            wait_for_completion: 是否等待转录完成
        
        Returns:
            bool: 处理是否成功
        """
        try:
            colored_print(f"\n🎯 开始处理: {url}", 'blue')
            
            # 步骤1: 下载音频
            colored_print("\n📥 步骤 1/3: 下载音频", 'yellow')
            self.current_operation = "downloading"
            
            download_result = self.downloader.download_audio(url)
            
            if not download_result.success:
                colored_print(f"❌ 下载失败: {download_result.error_message}", 'red')
                return False
            
            colored_print(f"✅ 下载成功: {download_result.title}", 'green')
            
            # 步骤2: 上传到服务器
            colored_print("\n📤 步骤 2/3: 上传到服务器", 'yellow')
            self.current_operation = "uploading"
            
            upload_result = self.uploader.upload_file(download_result.file_path)
            
            if not upload_result.success:
                colored_print(f"❌ 上传失败: {upload_result.error}", 'red')
                # 清理本地文件
                if not self.config.keep_local_files:
                    try:
                        os.remove(download_result.file_path)
                    except:
                        pass
                return False
            
            colored_print(f"✅ 上传成功，任务ID: {upload_result.task_id}", 'green')
            
            # 步骤3: 等待转录完成（可选）
            if wait_for_completion:
                colored_print("\n⏳ 步骤 3/3: 等待转录完成", 'yellow')
                self.current_operation = "transcribing"
                
                result = self.uploader.wait_for_completion(upload_result.task_id)
                
                if result.get('status') == 'completed':
                    colored_print("🎉 转录完成!", 'bright_green')
                    
                    # 显示结果摘要
                    transcription = result.get('result', {})
                    if transcription:
                        text_preview = transcription.get('text', '')[:200]
                        colored_print(f"📝 转录预览: {text_preview}...", 'cyan')
                else:
                    colored_print(f"⚠️ 转录未完成: {result.get('error', '未知错误')}", 'yellow')
                    colored_print(f"💡 请使用任务ID查询结果: {upload_result.task_id}", 'blue')
            else:
                colored_print(f"\n💡 转录任务已提交，任务ID: {upload_result.task_id}", 'blue')
                colored_print("   使用 --wait 选项可等待转录完成", 'blue')
            
            # 清理本地文件（如果配置了不保留）
            if not self.config.keep_local_files:
                try:
                    os.remove(download_result.file_path)
                    colored_print(f"🧹 已清理本地文件: {download_result.file_path}", 'cyan')
                except Exception as e:
                    colored_print(f"⚠️ 清理本地文件失败: {e}", 'yellow')
            else:
                colored_print(f"💾 本地文件已保留: {download_result.file_path}", 'cyan')
            
            self.current_operation = None
            return True
            
        except KeyboardInterrupt:
            colored_print("\n⚠️ 用户中断操作", 'yellow')
            return False
        except Exception as e:
            colored_print(f"\n❌ 处理异常: {e}", 'red')
            return False
    
    def interactive_mode(self):
        """交互模式"""
        colored_print("\n🎮 进入交互模式", 'blue')
        colored_print("输入视频URL开始转录，输入 'quit' 退出\n")
        
        while True:
            try:
                url = input("🔗 请输入视频URL: ").strip()
                
                if not url:
                    continue
                elif url.lower() in ['quit', 'exit', 'q']:
                    break
                elif url.lower() in ['help', 'h']:
                    self.show_help()
                    continue
                elif url.lower() in ['config', 'c']:
                    ConfigManager().setup_wizard()
                    # 重新加载配置
                    self.config = get_config()
                    self.downloader = AudioDownloader()
                    self.uploader = ServerUploader()
                    continue
                elif url.lower() in ['test', 't']:
                    self.run_system_test()
                    continue
                
                # 询问是否等待完成
                wait_input = input("⏳ 是否等待转录完成？[y/N]: ").strip().lower()
                wait = wait_input in ['y', 'yes', '是']
                
                # 处理URL
                success = self.process_url(url, wait_for_completion=wait)
                
                if success:
                    colored_print("✅ 任务完成!", 'green')
                else:
                    colored_print("❌ 任务失败!", 'red')
                
                print("-" * 60)
                
            except KeyboardInterrupt:
                colored_print("\n👋 退出交互模式", 'cyan')
                break
            except EOFError:
                break


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AI转录器本地客户端',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  %(prog)s "https://www.bilibili.com/video/BV1xx411c7mu" -q good -w
  %(prog)s --config
  %(prog)s --test
        """
    )
    
    # 位置参数
    parser.add_argument(
        'url', 
        nargs='?',
        help='视频URL'
    )
    
    # 可选参数
    parser.add_argument(
        '-c', '--config',
        action='store_true',
        help='运行配置向导'
    )
    
    parser.add_argument(
        '-s', '--server',
        metavar='URL',
        help='服务器地址'
    )
    
    parser.add_argument(
        '-q', '--quality',
        choices=['best', 'good', 'fast'],
        help='音频质量'
    )
    
    parser.add_argument(
        '-o', '--output',
        metavar='DIR',
        help='下载目录'
    )
    
    parser.add_argument(
        '-k', '--keep-local',
        action='store_true',
        help='保留本地下载文件'
    )
    
    parser.add_argument(
        '-w', '--wait',
        action='store_true',
        help='等待转录完成并显示结果'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细信息'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='禁用彩色输出'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='运行系统测试'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 创建客户端
    client = TranscriberClient()
    
    # 显示横幅
    if not args.no_color:
        client.show_banner()
    
    # 更新配置
    config_manager = ConfigManager()
    if args.server:
        config_manager.set('server_url', args.server)
    if args.quality:
        config_manager.set('audio_quality', args.quality)
    if args.output:
        config_manager.set('download_dir', args.output)
    if args.keep_local:
        config_manager.set('keep_local_files', True)
    if args.verbose:
        config_manager.set('verbose', True)
    if args.no_color:
        config_manager.set('use_colors', False)
    
    # 执行操作
    if args.config:
        # 运行配置向导
        config_manager.setup_wizard()
        
    elif args.test:
        # 运行系统测试
        client.run_system_test()
        
    elif args.url:
        # 处理单个URL
        success = client.process_url(args.url, wait_for_completion=args.wait)
        sys.exit(0 if success else 1)
        
    else:
        # 交互模式
        client.interactive_mode()


if __name__ == "__main__":
    main()