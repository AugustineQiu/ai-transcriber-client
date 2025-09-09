#!/usr/bin/env python3
"""
打包脚本 - 将Python项目打包为可执行文件
Build Script - Package Python project as executable files
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import platform

def colored_print(text: str, color: str = 'white'):
    """彩色输出"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")

def run_command(cmd: str, description: str = "") -> bool:
    """运行命令"""
    if description:
        colored_print(f"🔧 {description}", 'blue')
    
    colored_print(f"   执行: {cmd}", 'cyan')
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        colored_print(f"❌ 命令执行失败: {e}", 'red')
        if e.stderr:
            print(e.stderr)
        return False

def install_build_dependencies():
    """安装构建依赖"""
    colored_print("📦 安装构建依赖...", 'yellow')
    
    dependencies = [
        "pyinstaller",
        "auto-py-to-exe"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"安装 {dep}"):
            return False
    
    return True

def create_build_spec():
    """创建PyInstaller规格文件"""
    colored_print("📝 创建构建规格文件...", 'yellow')
    
    # 检测操作系统
    system = platform.system().lower()
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 分析主脚本
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
    ],
    hiddenimports=[
        'yt_dlp',
        'requests',
        'tqdm',
        'colorama',
        'yaml',
        'click',
        'pathvalidate'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 创建PYZ档案
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ai-transcriber-client',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# macOS应用包配置
{"" if system != "darwin" else '''
app = BUNDLE(
    exe,
    name='AI-Transcriber-Client.app',
    icon=None,
    bundle_identifier='com.aitranscriber.client',
    version='1.0.0'
)
'''}
"""
    
    with open('ai-transcriber-client.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    colored_print("✅ 规格文件创建完成", 'green')
    return True

def build_executable():
    """构建可执行文件"""
    colored_print("🏗️ 开始构建可执行文件...", 'yellow')
    
    # 清理旧的构建文件
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            colored_print(f"🧹 清理旧的{dir_name}目录", 'cyan')
    
    # 运行PyInstaller
    cmd = "pyinstaller --clean ai-transcriber-client.spec"
    if not run_command(cmd, "运行PyInstaller构建"):
        return False
    
    colored_print("✅ 可执行文件构建完成!", 'green')
    return True

def create_distribution():
    """创建发布包"""
    colored_print("📦 创建发布包...", 'yellow')
    
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # 确定平台标识
    platform_map = {
        'windows': 'windows',
        'darwin': 'macos', 
        'linux': 'linux'
    }
    
    arch_map = {
        'x86_64': 'x64',
        'amd64': 'x64',
        'arm64': 'arm64',
        'aarch64': 'arm64'
    }
    
    platform_name = platform_map.get(system, system)
    arch_name = arch_map.get(machine, machine)
    
    # 创建发布目录
    release_name = f"ai-transcriber-client-{platform_name}-{arch_name}"
    release_dir = Path("releases") / release_name
    
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制可执行文件
    dist_dir = Path("dist")
    if system == "darwin":
        # macOS应用包
        app_bundle = dist_dir / "AI-Transcriber-Client.app"
        if app_bundle.exists():
            shutil.copytree(app_bundle, release_dir / "AI-Transcriber-Client.app")
    else:
        # Windows/Linux可执行文件
        exe_name = "ai-transcriber-client.exe" if system == "windows" else "ai-transcriber-client"
        exe_path = dist_dir / exe_name
        if exe_path.exists():
            shutil.copy2(exe_path, release_dir / exe_name)
    
    # 复制文档
    docs = ['README.md', 'requirements.txt']
    for doc in docs:
        if os.path.exists(doc):
            shutil.copy2(doc, release_dir / doc)
    
    # 创建启动脚本 (Linux/macOS)
    if system != "windows":
        launch_script = release_dir / "run.sh"
        with open(launch_script, 'w', encoding='utf-8') as f:
            f.write(f"""#!/bin/bash
# AI转录器客户端启动脚本

cd "$(dirname "$0")"
./ai-transcriber-client "$@"
""")
        os.chmod(launch_script, 0o755)
    
    # 创建Windows批处理文件
    if system == "windows":
        bat_script = release_dir / "run.bat"
        with open(bat_script, 'w', encoding='utf-8') as f:
            f.write("""@echo off
REM AI转录器客户端启动脚本
cd /d "%~dp0"
ai-transcriber-client.exe %*
pause
""")
    
    # 创建压缩包
    if system == "windows":
        archive_name = f"{release_name}.zip"
        shutil.make_archive(f"releases/{release_name}", 'zip', release_dir)
    else:
        archive_name = f"{release_name}.tar.gz"
        shutil.make_archive(f"releases/{release_name}", 'gztar', release_dir)
    
    colored_print(f"✅ 发布包创建完成: releases/{archive_name}", 'green')
    return True

def show_build_info():
    """显示构建信息"""
    colored_print("\n📋 构建信息:", 'cyan')
    colored_print(f"   操作系统: {platform.system()}", 'white')
    colored_print(f"   架构: {platform.machine()}", 'white')
    colored_print(f"   Python版本: {sys.version}", 'white')
    
    # 检查可执行文件
    dist_dir = Path("dist")
    if dist_dir.exists():
        colored_print(f"   输出目录: {dist_dir.absolute()}", 'white')
        
        files = list(dist_dir.iterdir())
        if files:
            colored_print("   生成的文件:", 'white')
            for file in files:
                size = file.stat().st_size / (1024*1024) if file.is_file() else 0
                colored_print(f"     - {file.name} ({size:.1f}MB)", 'cyan')

def main():
    """主函数"""
    colored_print("🏗️ AI转录器客户端构建工具", 'magenta')
    colored_print("=" * 50, 'cyan')
    
    # 检查环境
    if not os.path.exists('main.py'):
        colored_print("❌ 未找到main.py文件，请在项目根目录运行", 'red')
        sys.exit(1)
    
    show_build_info()
    
    # 构建步骤
    steps = [
        ("安装构建依赖", install_build_dependencies),
        ("创建构建规格", create_build_spec), 
        ("构建可执行文件", build_executable),
        ("创建发布包", create_distribution)
    ]
    
    for step_name, step_func in steps:
        colored_print(f"\n🚀 步骤: {step_name}", 'yellow')
        if not step_func():
            colored_print(f"❌ 步骤失败: {step_name}", 'red')
            sys.exit(1)
        colored_print(f"✅ 步骤完成: {step_name}", 'green')
    
    colored_print("\n🎉 构建完成!", 'green')
    colored_print("=" * 50, 'cyan')
    
    show_build_info()
    
    colored_print("\n💡 使用说明:", 'blue')
    colored_print("   1. 在releases目录中找到适合你系统的版本", 'white')
    colored_print("   2. 解压并运行可执行文件", 'white')
    colored_print("   3. 首次运行建议使用 --config 配置服务器地址", 'white')

if __name__ == "__main__":
    main()