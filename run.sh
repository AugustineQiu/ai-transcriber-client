#!/bin/bash
# AI转录器客户端启动脚本
# AI Transcriber Client Launcher Script

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印彩色文本
print_colored() {
    printf "${!1}%s${NC}\n" "$2"
}

# 显示横幅
show_banner() {
    print_colored "CYAN" "╔═══════════════════════════════════════════════════════════╗"
    print_colored "CYAN" "║                  🎤 AI转录器本地客户端                      ║"
    print_colored "CYAN" "║               AI Transcriber Local Client                ║"
    print_colored "CYAN" "║                                                          ║"
    print_colored "CYAN" "║   🎬 支持YouTube、Bilibili等数百个视频平台                  ║"
    print_colored "CYAN" "║   🚀 本地下载，服务器转录，完全绕过反机器人检测               ║"
    print_colored "CYAN" "║   💾 支持多种音频格式和质量选择                             ║"
    print_colored "CYAN" "║                                                          ║"
    print_colored "CYAN" "║                    版本: 1.0.0                          ║"
    print_colored "CYAN" "╚═══════════════════════════════════════════════════════════╝"
    echo
}

# 检查Python环境
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_colored "RED" "❌ 未找到Python，请安装Python 3.8或更高版本"
        exit 1
    fi
}

# 检查虚拟环境
check_venv() {
    if [ ! -d "client-env" ]; then
        print_colored "YELLOW" "🔧 创建Python虚拟环境..."
        $PYTHON_CMD -m venv client-env
        
        print_colored "YELLOW" "📦 安装依赖包..."
        source client-env/bin/activate
        pip install -r requirements.txt
        
        print_colored "GREEN" "✅ 环境配置完成!"
    fi
}

# 激活虚拟环境
activate_venv() {
    source client-env/bin/activate
}

# 显示帮助
show_help() {
    echo "🔧 使用方法:"
    echo "  $0 [视频URL]                    - 转录指定URL"
    echo "  $0 --config                    - 运行配置向导"
    echo "  $0 --test                      - 运行系统测试"
    echo "  $0 --interactive               - 进入交互模式"
    echo "  $0 --build                     - 构建可执行文件"
    echo "  $0 --help                      - 显示此帮助"
    echo
    echo "📋 示例:"
    echo "  $0 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'"
    echo "  $0 'https://www.bilibili.com/video/BV1xx411c7mu'"
    echo "  $0 --config"
    echo
}

# 主函数
main() {
    show_banner
    
    # 检查参数
    if [ $# -eq 0 ]; then
        print_colored "BLUE" "🎮 启动交互模式..."
        check_python
        check_venv
        activate_venv
        python main.py
        return
    fi
    
    case "$1" in
        --help|-h)
            show_help
            ;;
        --config|-c)
            print_colored "BLUE" "🔧 运行配置向导..."
            check_python
            check_venv
            activate_venv
            python main.py --config
            ;;
        --test|-t)
            print_colored "BLUE" "🧪 运行系统测试..."
            check_python
            check_venv
            activate_venv
            python main.py --test
            ;;
        --interactive|-i)
            print_colored "BLUE" "🎮 进入交互模式..."
            check_python
            check_venv
            activate_venv
            python main.py
            ;;
        --build|-b)
            print_colored "BLUE" "🏗️ 构建可执行文件..."
            check_python
            check_venv
            activate_venv
            python build.py
            ;;
        http*|https*)
            print_colored "BLUE" "🎯 开始转录: $1"
            check_python
            check_venv
            activate_venv
            python main.py "$@"
            ;;
        *)
            print_colored "YELLOW" "⚠️ 未知参数: $1"
            show_help
            exit 1
            ;;
    esac
}

# 错误处理
trap 'print_colored "RED" "❌ 脚本执行被中断"' INT TERM

# 执行主函数
main "$@"