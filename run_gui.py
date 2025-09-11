#!/usr/bin/env python3
"""
GUI启动器 - AI转录器客户端
GUI Launcher - AI Transcriber Client

双击此文件或运行: python run_gui.py
"""

import sys
import os
import subprocess
from pathlib import Path

def check_requirements():
    """检查运行要求"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查必需模块
    required_modules = ['tkinter', 'requests', 'yt_dlp', 'tqdm']
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'tkinter':
                import tkinter
            elif module == 'requests':
                import requests
            elif module == 'yt_dlp':
                import yt_dlp
            elif module == 'tqdm':
                import tqdm
            print(f"✅ {module} 已安装")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} 未安装")
    
    if missing_modules:
        print(f"\n📦 缺少必需模块: {', '.join(missing_modules)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_modules)}")
        return False
    
    return True

def install_requirements():
    """尝试安装依赖"""
    try:
        print("📦 自动安装依赖包...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 未找到requirements.txt文件")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🎤 AI转录器本地客户端 - GUI启动器")
    print("AI Transcriber Local Client - GUI Launcher")
    print("=" * 60)
    
    # 切换到脚本目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 检查运行环境
    if not check_requirements():
        # 尝试自动安装
        if Path("requirements.txt").exists():
            if install_requirements():
                print("🔄 重新检查环境...")
                if not check_requirements():
                    input("❌ 环境检查失败，请手动安装依赖。按回车键退出...")
                    return 1
            else:
                input("❌ 自动安装失败，请手动安装依赖。按回车键退出...")
                return 1
        else:
            input("❌ 环境检查失败，请手动安装依赖。按回车键退出...")
            return 1
    
    print("\n🚀 启动GUI界面...")
    
    try:
        # 导入并启动GUI
        from unified_gui import UnifiedTranscriberGUI
        
        app = UnifiedTranscriberGUI()
        app.run()
        
    except ImportError as e:
        print(f"❌ 导入GUI模块失败: {e}")
        print("请确保unified_gui.py文件存在")
        input("按回车键退出...")
        return 1
    
    except Exception as e:
        print(f"❌ 启动GUI失败: {e}")
        input("按回车键退出...")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 用户退出")
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        input("按回车键退出...")