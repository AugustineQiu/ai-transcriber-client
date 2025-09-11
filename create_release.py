#!/usr/bin/env python3
"""
创建发布包脚本
Create Release Package Script
"""

import os
import shutil
import zipfile
from pathlib import Path
import time

def create_release_package():
    """创建发布包"""
    print("📦 创建AI转录器客户端发布包...")
    
    # 定义源文件和目标目录
    source_dir = Path(__file__).parent
    release_dir = Path("/var/www/releases")
    release_dir.mkdir(exist_ok=True)
    
    # 发布包名称
    timestamp = int(time.time())
    release_name = f"ai-transcriber-client-v1.0.0-{timestamp}"
    package_path = release_dir / f"{release_name}.zip"
    
    # 需要包含的文件
    files_to_include = [
        "main.py",
        "downloader.py", 
        "uploader.py",
        "config.py",
        "unified_gui.py",
        "run_gui.py",
        "run.sh",
        "run.bat",
        "requirements.txt",
        "README.md"
    ]
    
    # 创建临时目录
    temp_dir = release_dir / "temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    try:
        print("📂 复制文件...")
        
        # 复制文件到临时目录
        for file_name in files_to_include:
            source_file = source_dir / file_name
            if source_file.exists():
                shutil.copy2(source_file, temp_dir / file_name)
                print(f"✅ 复制: {file_name}")
            else:
                print(f"⚠️ 跳过: {file_name} (不存在)")
        
        # 创建安装说明
        install_instructions = """# AI转录器本地客户端 v1.0.0

## 🚀 快速开始

### Windows用户:
1. 解压此文件到任意目录
2. 双击运行 `run.bat` (默认启动图形界面)

### Linux/Mac用户:
1. 解压此文件到任意目录
2. 在终端中运行: `chmod +x run.sh`
3. 运行: `./run.sh` (默认启动图形界面)

### Python用户:
1. 安装依赖: `pip install -r requirements.txt`
2. 直接运行: `python run_gui.py`

## ⚙️ 配置

首次运行时，请点击"配置"按钮设置:
- 服务器地址 (默认: http://localhost:8000，支持自动端口检测)
- API密钥 (可选)
- 下载目录
- 音频质量等选项

## 🎯 主要功能

- 📹 下载视频: 下载视频文件到本地
- 🎵 下载音频: 下载音频文件到本地  
- 🎤 下载并转录: 下载音频并上传到服务器转录

## 🌐 支持的网站

YouTube、Bilibili、Twitter、Vimeo、SoundCloud 等数百个视频平台

## ❓ 常见问题

### 403错误
程序已集成最新反检测策略，如仍遇到问题请:
1. 检查网络连接
2. 尝试使用不同的网络环境
3. 联系技术支持

### 服务器连接问题
1. 确保服务器地址正确
2. 检查防火墙设置
3. 验证API密钥配置

## 📞 技术支持

如有问题请联系技术支持或查看项目文档。
"""
        
        with open(temp_dir / "安装说明.md", 'w', encoding='utf-8') as f:
            f.write(install_instructions)
        
        # 创建启动说明
        startup_guide = """@echo off
echo ======================================
echo    AI转录器本地客户端 v1.0.0
echo    AI Transcriber Local Client
echo ======================================
echo.
echo 🚀 启动方式:
echo.
echo 1. 图形界面 (默认):
echo    run.bat
echo.
echo 2. 命令行模式:
echo    run.bat --cli
echo.
echo 3. 直接转录URL:
echo    run.bat "https://www.youtube.com/watch?v=视频ID"
echo.
echo ⚙️ 更多选项:
echo    run.bat --help
echo.
pause
"""
        
        with open(temp_dir / "启动说明.bat", 'w', encoding='utf-8') as f:
            f.write(startup_guide)
        
        print("📦 创建ZIP文件...")
        
        # 创建ZIP文件
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        print(f"✅ 发布包已创建: {package_path}")
        print(f"📊 文件大小: {package_path.stat().st_size / 1024 / 1024:.1f}MB")
        
        # 创建最新版本链接
        latest_path = release_dir / "ai-transcriber-client-latest.zip"
        if latest_path.exists():
            latest_path.unlink()
        shutil.copy2(package_path, latest_path)
        print(f"🔗 最新版本链接: {latest_path}")
        
        return str(latest_path)
        
    except Exception as e:
        print(f"❌ 创建发布包失败: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return None

def main():
    """主函数"""
    return create_release_package()

if __name__ == "__main__":
    result = main()
    if result:
        print("🎉 发布包创建成功!")
    else:
        print("❌ 发布包创建失败!")