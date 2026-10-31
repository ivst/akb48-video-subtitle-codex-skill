# AKB48 视频字幕 Codex Skill

[English](README.md) · [Русский](README.ru.md) · [한국어](README.ko.md) · [Español (LatAm)](README.es-419.md) · [Bahasa Indonesia](README.id.md) · [ไทย](README.th.md) · [简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md)

**本中文文档为翻译初稿，正式使用前建议由中文母语者审校。**


用于翻译和制作 AKB48 及 48 Group 视频字幕的可复用工作流程。它帮助 Codex 区分对白、说话人标注、歌曲和画面文字，核对姓名拼写，并检查字幕与渲染后的视频。

仓库包含 Codex Skill、语言配置初稿、基础 SRT 检查器、部署说明，以及两张近期俄语翻译视频的效果示例。俄语配置基于完整节目制作流程；韩语配置仍是草稿，需要韩语母语者审核；其他语言配置是供贡献者完善的起点。

## 预览

**第 12 期——说话人标签与紧凑字幕条**（[源视频](https://www.youtube.com/watch?v=aPznmLtjedw)）

![第 12 期字幕示例](examples/preview-episode-12.jpg)

**第 13 期——最终握手环节中的紧凑字幕条**（[源视频](https://www.youtube.com/watch?v=mHF3TEk6lwQ)）

![第 13 期字幕示例](examples/preview-episode-13.jpg)

这些是节目画面的示例帧。原始视频、标志和出演者均归各自权利人所有。本仓库不提供视频或整集字幕文件。

## 在 Codex 中使用

克隆仓库并在 Codex 中打开目录。Skill 位于 `.agents/skills/akb48-video-subtitles/`，可作为项目 Skill 被发现。若要在其他项目中使用，请将该目录复制到 Codex 用户 Skill 目录（Windows 通常为 `%USERPROFILE%\.codex\skills\akb48-video-subtitles`；设置了 `CODEX_HOME` 时为 `$CODEX_HOME/skills/akb48-video-subtitles`）。安装后重新启动一个 Codex 会话。

使用 `$akb48-video-subtitles` 调用，或要求 Codex 翻译/审校 AKB48 视频，并注明目标语言和所需文件。提供本地视频或已获授权的来源、成员/姓名清单（如有）以及输出格式。本文档所述流程不需要 API 密钥。

## 快速配置

需要 Python 3.11 或更新版本、FFmpeg 和 FFprobe。渲染 ASS 需要包含 libass 的 FFmpeg 构建版本。通过操作系统的包管理器安装 FFmpeg，并确保 `ffmpeg` 与 `ffprobe` 已加入 `PATH`。

```powershell
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py
python .agents/skills/akb48-video-subtitles/scripts/check_srt.py path\to\dialogue.srt
```

所含脚本仅使用 Python 标准库，无需 `pip install`。机器配置和可选 ASR/下载工具见[资源要求](.agents/skills/akb48-video-subtitles/references/resources.md)。

## 工作流程

1. 核对日语对白，并分别整理标牌、标题、规则和结果文字。
2. 使用所选语言配置及经过审校的单集词汇表进行翻译。
3. 只有证据充分时才标注说话人；无法确定的反应使用中性标签。
4. 按需求生成通用 SRT、带样式的 ASS 和/或 MP4。
5. 抽查整集不同位置的画面，并检查最终渲染文件；适用时检查解码、时间轴、压缩包和音频保留情况。

详见[工作流程说明](.agents/skills/akb48-video-subtitles/references/workflow.md)和[语言配置](.agents/skills/akb48-video-subtitles/references/languages/README.md)。

## 资源要求

对于常见的 1080p、20–40 分钟视频，8 GB 内存和较新的 4 核 CPU 可作为起点；本地 ASR 使用 16 GB 内存和 6–8 核会更舒适。建议为源文件、中间文件、成片和备份预留约 10 GB 空间。GPU 加速为可选项。4K 或高码率视频可能需要更多磁盘和内存。这些只是规划估算，实际占用取决于编码格式、ASR 模型和编码器。

## 权利与隐私

仅处理和发布你有权使用的材料。未经再分发许可，不要在公开 Pull Request 中提交单集转录、完整字幕、凭据、Cookie 或私人词汇表。示例帧仅用于展示字幕布局；节目内容的权利仍归其所有者。

## 许可证

原创文档和脚本采用 MIT 许可证。示例图片及其中展示的节目内容不包含在该许可证内，详见 [NOTICE](NOTICE) 和 [LICENSE](LICENSE)。
