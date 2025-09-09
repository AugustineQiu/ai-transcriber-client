# AI转录器 - 本地下载工具
## AI Transcriber - Local Download Client

### 概述 Overview
这是AI转录系统的本地客户端工具，用于在用户本地下载音视频内容，然后自动上传到服务器进行转录。
完全绕过服务器端的反机器人检测问题。

This is a local client tool for the AI Transcription System that downloads audio/video content locally and automatically uploads to the server for transcription. Completely bypasses server-side anti-bot detection issues.

### 主要功能 Key Features
- 🎬 支持YouTube、Bilibili等主流视频平台
- 🎵 自动提取最佳质量音频
- ⚡ 快速下载和上传
- 🔧 简单易用的命令行界面
- 📊 详细的进度显示
- 🚀 一键式操作流程

### 系统要求 System Requirements
- Python 3.8+ 或使用预编译的可执行文件
- 网络连接（用于下载和上传）
- 支持Windows、macOS、Linux

### 快速开始 Quick Start

#### 方式1：使用可执行文件（推荐）
1. 下载对应系统的可执行文件
2. 运行程序：`./ai-transcriber-client`
3. 按提示输入视频URL和配置

#### 方式2：从源代码运行
```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 使用说明 Usage

#### 基本用法
```bash
# 下载并上传单个视频
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"

# 指定服务器地址
python main.py "VIDEO_URL" --server "https://your-server.com"

# 选择音频质量
python main.py "VIDEO_URL" --quality best
```

#### 配置选项
- `--server`：转录服务器地址
- `--quality`：音频质量（best/good/fast）
- `--output`：本地保存目录
- `--keep-local`：保留本地下载文件
- `--config`：配置文件路径

### 工作流程 Workflow
1. 🔗 用户输入视频URL
2. 📥 本地下载音频文件
3. 📤 自动上传到转录服务器
4. 🎯 返回转录任务ID
5. ⏳ 可选：等待并获取转录结果

### 技术架构 Technical Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户输入URL    │───▶│   本地下载音频   │───▶│   上传到服务器   │
│   User Input    │    │  Local Download │    │ Upload to Server│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
┌─────────────────┐    ┌─────────────────┐           │
│   获取转录结果   │◀───│   轮询任务状态   │◀──────────┘
│  Get Results    │    │  Poll Task      │
└─────────────────┘    └─────────────────┘
```

### 开发者信息 Developer Info
- 版本：1.0.0
- 许可证：MIT
- 作者：AI Transcriber Team
- 更新时间：2025-09-09

### 常见问题 FAQ

**Q: 为什么要使用本地下载？**
A: 避免服务器IP被YouTube等平台的反机器人系统检测，提高成功率和稳定性。

**Q: 支持哪些视频平台？**
A: 支持所有yt-dlp支持的平台，包括YouTube、Bilibili、Twitter等数百个平台。

**Q: 如何处理长时间的视频？**
A: 工具会自动处理长视频，支持断点续传和分片上传。

**Q: 是否会保存我的数据？**
A: 本地工具不会保存任何用户数据，只是作为下载和上传的中转工具。