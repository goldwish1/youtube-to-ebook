# YouTube 转电子书

将你关注的 YouTube 频道最新视频，整理成排版精美的 EPUB 电子书。

## 功能

- 拉取 YouTube 频道最新视频（自动过滤 Shorts）
- 提取视频字幕/转写文本
- 使用 Claude AI 将转写润色为杂志风格长文
- 生成可在任意设备上阅读的 EPUB
- 可选：邮件发送并附带电子书附件
- 可选：Web 控制台便于管理

## 快速开始

1. **克隆并安装依赖：**
   ```bash
   git clone https://github.com/YOUR_USERNAME/youtube-to-ebook.git
   cd youtube-to-ebook
   pip install -r requirements.txt
   ```

2. **配置 API 密钥：**
   ```bash
   cp .env.example .env
   # 在 .env 中填入你的密钥
   ```

3. **添加频道：**
   ```bash
   # 在 channels.txt 中填写 YouTube 频道 handle
   @mkbhd
   @veritasium
   @3blue1brown
   ```

4. **生成电子书：**
   ```bash
   python main.py
   ```

## 获取 API 密钥

### YouTube Data API（免费）

1. 打开 [Google Cloud Console](https://console.cloud.google.com/)
2. 新建项目
3. 启用「YouTube Data API v3」
4. 凭据 → 创建 API 密钥
5. 将密钥写入 `.env`

### Anthropic API

1. 打开 [Anthropic Console](https://console.anthropic.com/)
2. 创建 API 密钥
3. 将密钥写入 `.env`

## Web 控制台

启动图形化界面：

```bash
pip install streamlit
python -m streamlit run dashboard.py
```

## 自动化（Mac）

每周自动运行：

```bash
# 将 plist 复制到 LaunchAgents
cp com.youtube.newsletter.plist ~/Library/LaunchAgents/

# 加载任务
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.youtube.newsletter.plist
```

## 故障排查

### 自动化运行时出现「ModuleNotFoundError」

Mac 上可能装有多个 Python。自动化脚本使用 `python3`，但依赖可能装在别的 Python 里。

**处理：** 查到你实际使用的 Python 路径后，更新脚本中的解释器路径：

```bash
# 查看 python3 位置
which python3

# 在 run_newsletter.sh 和 dashboard.py 中改为完整路径
# 例如：/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
```

## 已知问题与对策

本项目记录了一些 YouTube API 的坑：

| 问题 | 对策 |
|------|------|
| 无法按时长过滤 Shorts | 检查 `/shorts/` URL 模式 |
| 搜索 API 结果不按时间排序 | 改用「上传」播放列表 |
| 字幕 API 用法变更 | 使用实例方法 `ytt_api.fetch()` |
| 云端被拦截 | 在本地运行，不要用 GitHub Actions |
| 转写中人名拼错 | 把视频简介一并交给 Claude 作上下文 |
| 文章在句中被截断 | 在 write_articles.py 中增大 `max_tokens` |

详细说明见 [SKILL.md](SKILL.md)。

## 项目结构

```
├── main.py              # 完整流水线入口
├── get_videos.py        # 从 YouTube 拉取视频
├── get_transcripts.py   # 提取视频字幕
├── write_articles.py    # 用 Claude 写成文章
├── send_email.py        # 生成 EPUB 并发送邮件
├── dashboard.py         # Streamlit Web 控制台
├── video_tracker.py     # 记录已处理视频
├── channels.txt         # 频道列表
├── .env                 # API 密钥（勿提交）
└── newsletters/         # 已生成电子书归档
```

## 许可

MIT — 可自由使用并按需修改。

---

由 Claude AI 辅助构建
