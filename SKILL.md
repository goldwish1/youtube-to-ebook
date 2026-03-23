---
name: youtube-to-ebook
description: 将 YouTube 视频转为带字幕的、排版良好的电子书文章（EPUB）
---

# YouTube to Ebook

从你关注的 YouTube 频道抓取最新长视频，把字幕改写成杂志风长文，并打包成可在各设备阅读的 **EPUB** 电子书（可选邮件发送）。

## 本技能做什么

1. 从 YouTube 频道拉取最新视频（过滤 Shorts）
2. 为视频提取字幕文本
3. 使用大模型（ModelScope / Anthropic 兼容接口等，见 `write_articles.py`）将字幕润色成文章
4. 将文章打包为 EPUB（`ebooklib`）

## 快速开始

可以说：「帮我配置 YouTube 转电子书」

一般会带你完成：

1. 准备项目目录与 Python 环境
2. 开通 YouTube Data API 并配置密钥
3. 在 `channels.txt` 中填写频道 handle
4. 运行 `python main.py` 生成第一本电子书

## 环境要求

- Python 3.8+
- YouTube Data API 密钥（Google Cloud Console，免费额度内可用）
- 字幕：**Supadata API**（`SUPADATA_API_KEY`，见 `get_transcripts.py`）
- 写作模型：**ModelScope**（`MODELSCOPE_API_KEY`）或 **Anthropic 兼容网关**（`ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN` 等，见 `write_articles.py`）

## 常用命令

| 命令 | 说明 |
|------|------|
| `python main.py` | 跑完整流水线：拉视频 → 字幕 → 写文章 → 邮件/EPUB |
| 编辑 `channels.txt` | 维护频道列表（每行一个 `@handle`，`#` 开头为注释） |
| `streamlit run dashboard.py` | 启动 Web 仪表盘（需已安装 `streamlit`） |

## 关键文件

```
youtube-to-ebook/
├── get_videos.py      # 从 YouTube 拉最新长视频
├── get_transcripts.py # 通过 Supadata 取字幕
├── write_articles.py  # 大模型改写文章
├── send_email.py      # 生成 EPUB、可选发邮件
├── main.py            # 串联全流程
├── channels.txt       # 频道列表
├── video_tracker.py   # processed_videos.json 去重
└── .env               # 密钥与配置（勿提交）
```

## 常见坑与对策

### 1. YouTube Shorts 识别

**问题**：按时长过滤不可靠，部分 Shorts 超过 60 秒。

**对策**：请求 `https://www.youtube.com/shorts/{video_id}`，看重定向后 URL 是否仍含 `/shorts/`：

```python
def is_youtube_short(video_id):
    shorts_url = f"https://www.youtube.com/shorts/{video_id}"
    response = requests.head(shorts_url, allow_redirects=True, timeout=5)
    return "/shorts/" in response.url
```

### 2. 视频顺序不是按时间

**问题**：Search API 返回顺序不一定严格按上传时间。

**对策**：用频道 **uploads 播放列表** + `playlistItems`：

```python
channel_info = youtube.channels().list(
    part="contentDetails",
    forHandle=handle
).execute()
uploads_playlist_id = channel_info["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

youtube.playlistItems().list(
    part="snippet",
    playlistId=uploads_playlist_id,
    maxResults=15
).execute()
```

### 3. 字幕拉取方式

**问题**：直连 YouTube 字幕接口在服务器或高频请求下容易被限流或封禁。

**对策**：本仓库默认通过 **Supadata** HTTP API（`get_transcripts.py`）按视频 URL 取纯文本字幕；需在 `.env` 配置 `SUPADATA_API_KEY`。

### 4. API 限流

**问题**：连续请求字幕或 LLM 容易触发限流。

**对策**：在循环中增加间隔（本仓库在 `get_transcripts_for_videos` 中对 Supadata 请求使用约 **1 秒**间隔，可按需要调大）。

### 5. 字幕里的人名、术语不准

**问题**：自动字幕常拼错专名。

**对策**：在提示词里同时传入 **视频标题与简介**（`write_articles.py` 已包含），简介里常有正确拼写。

### 6. 云端自动化被拦

**问题**：GitHub Actions 等云主机访问 YouTube/部分服务可能不稳定。

**对策**：在 **本机 Mac** 用 `launchd` 定时执行 `main.py`；仓库内可参考 `com.youtube.newsletter.plist`（需把路径改成你自己的项目目录）：

```xml
<!-- ~/Library/LaunchAgents/com.youtube.newsletter.plist -->
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.youtube.newsletter</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/你的路径/youtube-to-ebook/main.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>3</integer>
        <key>Hour</key>
        <integer>7</integer>
    </dict>
</dict>
</plist>
```

## 可定制项

### 文风

编辑 `write_articles.py` 中的提示词，例如：

- 杂志长文（默认）
- 学术摘要
- 轻松博客
- 技术文档风

### 邮件发送（可选）

在 `.env` 中配置 Gmail 应用专用密码：

```
GMAIL_ADDRESS=your@gmail.com
GMAIL_APP_PASSWORD=your-app-password
```

## 流水线示意

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐    ┌────────────┐
│  拉取视频   │───▶│  获取字幕    │───▶│  大模型写作   │───▶│ 生成 EPUB  │
│ (YouTube API)│    │  (Supadata)  │    │(ModelScope 等)│    │ (ebooklib) │
└─────────────┘    └──────────────┘    └───────────────┘    └────────────┘
```

## 输出物

生成的 EPUB 通常包含：

- 含各篇文章的目录
- 清晰可读的排版
- 原文视频链接便于回看
- 适合手机阅读的样式
