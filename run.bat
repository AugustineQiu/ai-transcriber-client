@echo off
:: AI转录器客户端启动脚本 (Windows)
:: AI Transcriber Client Launcher Script (Windows)

chcp 65001 >nul
setlocal enabledelayedexpansion

:: 颜色代码 (仅在支持ANSI的Windows Terminal中有效)
set "RED=[31m"
set "GREEN=[32m"
set "YELLOW=[33m"
set "BLUE=[34m"
set "PURPLE=[35m"
set "CYAN=[36m"
set "NC=[0m"

:: 显示横幅
:show_banner
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                  🎤 AI转录器本地客户端                      ║
echo ║               AI Transcriber Local Client                ║
echo ║                                                          ║
echo ║   🎬 支持YouTube、Bilibili等数百个视频平台                  ║
echo ║   🚀 本地下载，服务器转录，完全绕过反机器人检测               ║
echo ║   💾 支持多种音频格式和质量选择                             ║
echo ║                                                          ║
echo ║                    版本: 1.0.0                          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
goto :eof

:: 检查Python环境
:check_python
where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :eof
)

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3"
    goto :eof
)

echo ❌ 未找到Python，请安装Python 3.8或更高版本
echo    下载地址: https://www.python.org/downloads/
pause
exit /b 1

:: 检查虚拟环境
:check_venv
if not exist "client-env" (
    echo 🔧 创建Python虚拟环境...
    %PYTHON_CMD% -m venv client-env
    
    echo 📦 安装依赖包...
    call client-env\Scripts\activate.bat
    pip install -r requirements.txt
    
    echo ✅ 环境配置完成!
)
goto :eof

:: 激活虚拟环境
:activate_venv
call client-env\Scripts\activate.bat
goto :eof

:: 显示帮助
:show_help
echo 🔧 使用方法:
echo   %~n0 [视频URL]                    - 转录指定URL
echo   %~n0 --gui                       - 启动图形界面 (推荐)
echo   %~n0 --config                    - 运行配置向导
echo   %~n0 --test                      - 运行系统测试
echo   %~n0 --interactive               - 进入交互模式
echo   %~n0 --build                     - 构建可执行文件
echo   %~n0 --help                      - 显示此帮助
echo.
echo 📋 示例:
echo   %~n0 --gui                       # 启动图形界面 (推荐新用户)
echo   %~n0 "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
echo   %~n0 "https://www.bilibili.com/video/BV1xx411c7mu"
echo   %~n0 --config
echo.
pause
goto :eof

:: 主函数
:main
call :show_banner

:: 检查参数
if "%~1"=="" (
    echo 🎮 启动交互模式...
    call :check_python
    call :check_venv
    call :activate_venv
    python main.py
    goto :end
)

if /I "%~1"=="--help" goto :show_help
if /I "%~1"=="-h" goto :show_help

if /I "%~1"=="--gui" (
    echo 🖥️ 启动图形界面...
    call :check_python
    call :check_venv
    call :activate_venv
    python run_gui.py
    goto :end
)

if /I "%~1"=="--config" (
    echo 🔧 运行配置向导...
    call :check_python
    call :check_venv
    call :activate_venv
    python main.py --config
    goto :end
)

if /I "%~1"=="--test" (
    echo 🧪 运行系统测试...
    call :check_python
    call :check_venv
    call :activate_venv
    python main.py --test
    goto :end
)

if /I "%~1"=="--interactive" (
    echo 🎮 进入交互模式...
    call :check_python
    call :check_venv
    call :activate_venv
    python main.py
    goto :end
)

if /I "%~1"=="--build" (
    echo 🏗️ 构建可执行文件...
    call :check_python
    call :check_venv
    call :activate_venv
    python build.py
    goto :end
)

:: 检查是否为URL
echo %1 | findstr /b "http" >nul
if %errorlevel% equ 0 (
    echo 🎯 开始转录: %1
    call :check_python
    call :check_venv
    call :activate_venv
    python main.py %*
    goto :end
)

echo ⚠️ 未知参数: %1
call :show_help
exit /b 1

:end
echo.
echo ✅ 操作完成
pause
exit /b 0

:: 执行主函数
call :main %*