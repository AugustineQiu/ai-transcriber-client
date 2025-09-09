# AI转录器本地客户端 - 用户使用指南
## AI Transcriber Local Client - User Guide

### 📋 目录
1. [快速开始](#快速开始)
2. [安装说明](#安装说明)
3. [基本使用](#基本使用)
4. [高级功能](#高级功能)
5. [配置说明](#配置说明)
6. [故障排除](#故障排除)
7. [支持的平台](#支持的平台)
8. [常见问题](#常见问题)

---

## 🚀 快速开始

### 第一次使用
1. **下载客户端**
   - 从发布页面下载适合你系统的版本
   - Windows: `ai-transcriber-client-windows-x64.zip`
   - macOS: `ai-transcriber-client-macos-x64.tar.gz`
   - Linux: `ai-transcriber-client-linux-x64.tar.gz`

2. **解压和运行**
   ```bash
   # Windows
   解压zip文件，双击 ai-transcriber-client.exe
   
   # macOS/Linux
   tar -xzf ai-transcriber-client-*.tar.gz
   cd ai-transcriber-client-*/
   ./ai-transcriber-client
   ```

3. **初次配置**
   ```bash
   # 运行配置向导
   ./ai-transcriber-client --config
   ```

4. **开始转录**
   ```bash
   ./ai-transcriber-client "https://www.youtube.com/watch?v=VIDEO_ID"
   ```

---

## 💾 安装说明

### 方式1：使用预编译版本（推荐）
1. 前往 [Releases页面](#) 下载最新版本
2. 选择适合你系统的版本：
   - **Windows 64位**: `ai-transcriber-client-windows-x64.zip`
   - **macOS Intel**: `ai-transcriber-client-macos-x64.tar.gz`
   - **macOS Apple Silicon**: `ai-transcriber-client-macos-arm64.tar.gz`
   - **Linux 64位**: `ai-transcriber-client-linux-x64.tar.gz`
3. 解压到任意目录
4. 运行可执行文件

### 方式2：从源码运行
```bash
# 克隆项目
git clone https://github.com/your-repo/ai-transcriber-client.git
cd ai-transcriber-client

# 安装Python依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 方式3：自行编译
```bash
# 安装依赖并构建
python build.py
```

---

## 🎯 基本使用

### 命令行语法
```bash
ai-transcriber-client [URL] [选项]
```

### 最简单的使用方式
```bash
# 转录单个YouTube视频
ai-transcriber-client "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 转录Bilibili视频
ai-transcriber-client "https://www.bilibili.com/video/BV1xx411c7mu"
```

### 常用选项
```bash
# 等待转录完成并显示结果
ai-transcriber-client "VIDEO_URL" --wait

# 指定音频质量
ai-transcriber-client "VIDEO_URL" --quality good

# 保留本地下载文件
ai-transcriber-client "VIDEO_URL" --keep-local

# 指定服务器地址
ai-transcriber-client "VIDEO_URL" --server "https://your-server.com"
```

### 交互模式
```bash
# 进入交互模式（不提供URL参数）
ai-transcriber-client

# 然后按提示输入视频URL
🔗 请输入视频URL: https://www.youtube.com/watch?v=VIDEO_ID
⏳ 是否等待转录完成？[y/N]: y
```

---

## 🔧 高级功能

### 配置管理
```bash
# 运行配置向导
ai-transcriber-client --config

# 显示当前配置
ai-transcriber-client --config --verbose
```

### 批量处理
```bash
# 方式1：使用脚本
for url in "URL1" "URL2" "URL3"; do
    ai-transcriber-client "$url" --wait
done

# 方式2：从文件读取URL列表
while read url; do
    ai-transcriber-client "$url"
done < urls.txt
```

### 不同音频质量选择
- **best**: 最佳质量，文件较大，转录精度最高
- **good**: 良好质量，平衡大小和质量
- **fast**: 快速下载，文件较小，适合网络较慢时使用

```bash
ai-transcriber-client "VIDEO_URL" --quality best   # 最佳质量
ai-transcriber-client "VIDEO_URL" --quality good   # 良好质量  
ai-transcriber-client "VIDEO_URL" --quality fast   # 快速下载
```

### 自定义输出目录
```bash
ai-transcriber-client "VIDEO_URL" --output "/path/to/downloads"
```

---

## ⚙️ 配置说明

### 配置文件位置
- **Windows**: `%USERPROFILE%\.ai-transcriber\config.yaml`
- **macOS**: `~/.ai-transcriber/config.yaml`
- **Linux**: `~/.ai-transcriber/config.yaml`

### 配置文件示例
```yaml
# 服务器配置
server_url: "https://your-server.com"
api_key: null  # 可选的API密钥

# 下载配置  
download_dir: "./downloads"
audio_quality: "best"  # best, good, fast
keep_local_files: false
max_file_size: 524288000  # 500MB限制

# 上传配置
chunk_size: 8388608  # 8MB分片上传
max_retries: 3
timeout: 300  # 5分钟超时

# 界面配置
show_progress: true
use_colors: true
verbose: false

# 高级配置
concurrent_downloads: 1
temp_dir: null
```

### 环境变量支持
```bash
# 设置服务器地址
export AI_TRANSCRIBER_SERVER="https://your-server.com"

# 设置API密钥
export AI_TRANSCRIBER_API_KEY="your-api-key"

# 设置下载目录
export AI_TRANSCRIBER_DOWNLOAD_DIR="/path/to/downloads"
```

---

## 🛠️ 故障排除

### 常见错误及解决方案

#### 1. "yt-dlp not found" 错误
```bash
# 使用pip安装yt-dlp
pip install yt-dlp

# 或升级到最新版本
pip install --upgrade yt-dlp
```

#### 2. "服务器连接失败" 错误
- 检查网络连接
- 验证服务器地址是否正确
- 检查防火墙设置
- 尝试使用 `--test` 选项测试连接

```bash
ai-transcriber-client --test
```

#### 3. "下载失败" 错误
- 检查视频URL是否有效
- 确认视频是否为私有或地区限制
- 尝试不同的音频质量设置
- 检查网络连接

#### 4. "上传失败" 错误
- 检查文件大小是否超过限制
- 验证服务器API是否正常工作
- 尝试减小音频质量以减少文件大小

#### 5. 权限错误
```bash
# Linux/macOS 给予执行权限
chmod +x ai-transcriber-client

# Windows 以管理员身份运行
```

### 调试模式
```bash
# 启用详细输出
ai-transcriber-client "VIDEO_URL" --verbose

# 禁用彩色输出（便于日志记录）
ai-transcriber-client "VIDEO_URL" --no-color
```

### 清理和重置
```bash
# 清理下载目录
rm -rf downloads/*

# 重置配置（删除配置文件）
rm ~/.ai-transcriber/config.yaml

# 重新运行配置向导
ai-transcriber-client --config
```

---

## 🌐 支持的平台

### 视频平台（200+）
- **YouTube** - 最全面支持
- **Bilibili** - B站视频
- **Twitter/X** - 推特视频
- **Vimeo** - 专业视频平台
- **TikTok** - 短视频
- **Instagram** - 社交媒体视频
- **Facebook** - 脸书视频
- **Twitch** - 游戏直播
- **SoundCloud** - 音频平台
- **Spotify** - 播客内容
- **Apple Podcasts** - 苹果播客
- **更多平台...** - 支持yt-dlp的所有平台

### 音频格式
- **输出格式**: MP3 (默认)
- **输入支持**: MP4, WEBM, M4A, OGG等
- **质量选项**: 最佳/良好/快速三档

### 操作系统
- ✅ **Windows** 10/11 (x64)
- ✅ **macOS** 10.15+ (Intel & Apple Silicon)
- ✅ **Linux** (Ubuntu, CentOS, Debian等)

---

## ❓ 常见问题

### Q: 为什么要使用本地下载而不是服务器下载？
**A:** 本地下载可以完全绕过YouTube等平台的反机器人检测系统，提供更高的成功率和稳定性。用户可以使用自己的网络环境和登录状态。

### Q: 下载的文件会保存在哪里？
**A:** 默认保存在当前目录的 `downloads` 文件夹中。可以通过 `--output` 选项或配置文件修改保存位置。转录完成后，文件默认会被删除以节省空间，除非使用 `--keep-local` 选项。

### Q: 支持下载播放列表吗？
**A:** 目前版本专注于单个视频处理。播放列表支持计划在未来版本中添加。

### Q: 如何获取转录结果？
**A:** 有两种方式：
1. 使用 `--wait` 选项等待转录完成并直接显示结果
2. 记录任务ID，稍后通过服务器API查询结果

### Q: 转录需要多长时间？
**A:** 转录时间取决于：
- 音频长度（通常为实际时长的10-20%）
- 音频质量和复杂度
- 服务器负载情况
- 选择的AI模型

### Q: 可以转录非英语内容吗？
**A:** 是的，支持多种语言的转录。AI模型通常能自动检测语言，也可以手动指定语言参数。

### Q: 文件大小有限制吗？
**A:** 默认限制500MB。可以在配置文件中调整 `max_file_size` 参数。

### Q: 如何更新客户端？
**A:** 下载最新版本的可执行文件替换旧版本即可。配置文件会自动保留。

### Q: 是否支持代理？
**A:** 客户端会使用系统代理设置。如需特定代理配置，可以设置环境变量：
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=https://proxy.example.com:8080
```

### Q: 如何报告问题或建议？
**A:** 请在 [GitHub Issues](https://github.com/your-repo/issues) 页面提交问题报告或功能建议。

---

## 📞 获取帮助

- **在线帮助**: `ai-transcriber-client --help`
- **系统测试**: `ai-transcriber-client --test`
- **GitHub Issues**: [报告问题](https://github.com/your-repo/issues)
- **用户社区**: [讨论区](https://github.com/your-repo/discussions)

---

## 📄 版权信息

AI转录器本地客户端 © 2025 AI Transcriber Team  
基于MIT许可证发布

---

*最后更新: 2025-09-09*