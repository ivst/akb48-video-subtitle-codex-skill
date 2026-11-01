# AKB48 视频字幕 Codex Skill

[English](README.md) · [Русский](README.ru.md) · [한국어](README.ko.md) · [Español (LatAm)](README.es-419.md) · [Bahasa Indonesia](README.id.md) · [ไทย](README.th.md) · [简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md)

**本中文文档为翻译初稿，正式使用前建议由中文母语者审校。**


用于翻译和制作 AKB48 及 48 Group 视频字幕的可复用工作流程。它帮助 Codex 区分对白、说话人标注、歌曲和画面文字，核对姓名拼写，并检查字幕与渲染后的视频。

仓库包含 Codex Skill、语言配置初稿、基础 SRT 检查器、部署说明，以及两张近期俄语翻译视频的效果示例。俄语配置基于完整节目制作流程；韩语配置仍是草稿，需要韩语母语者审核；其他语言配置是供贡献者完善的起点。

## 快速安装

请先准备 Git、Python 3.11+、支持 libass 的 FFmpeg/FFprobe 和 Codex 访问权限。以下命令克隆仓库并检查工具，不会安装前置程序。在 Codex 中打开克隆后的目录并开始新聊天。

```sh
git clone https://github.com/ivst/akb48-video-subtitle-codex-skill.git
cd akb48-video-subtitle-codex-skill
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py --require-ass
```

## 提示词示例

```text
使用 $akb48-video-subtitles，将 [本地视频路径或已获授权的 URL] 翻译为简体中文，包括画面文字。
提供独立的 SRT 和 ASS、内嵌字幕的视频及检查报告。使用靠近画面下边缘的最新紧凑布局，以已核实的姓名或中性角色区分说话人，不要合并身份不明的声音。
省略背景音乐和歌词。核对姓名、对话含义、画面文字及成片帧，记录疑点。不要发布任何内容。
```

## 预览

**第 12 期——说话人标签与紧凑字幕条**（[源视频](https://www.youtube.com/watch?v=aPznmLtjedw)）

![第 12 期字幕示例](examples/preview-episode-12.jpg)

*引用画面来源：AKB48，**AKB48の全力エンタメ学園**，第12期（2026年4月18日），[YouTube 原始视频](https://www.youtube.com/watch?v=aPznmLtjedw)。* 该截图用于技术性说明说话人姓名标签与紧凑型翻译字幕面板的布局，便于评估姓名与对白如何区分，而不只是依靠颜色。

**第 13 期——最终握手环节中的紧凑字幕条**（[源视频](https://www.youtube.com/watch?v=mHF3TEk6lwQ)）

![第 13 期字幕示例](examples/preview-episode-13.jpg)

*引用画面来源：AKB48，**AKB48の全力エンタメ学園**，第13期（2026年4月25日），[YouTube 原始视频](https://www.youtube.com/watch?v=mHF3TEk6lwQ)。* 该截图用于分析握手场景中字幕面板的位置，以及翻译文字与原始画面元素之间的关系；目的不是将节目内容作为娱乐素材重新发布。

以上两张截图是**用于技术性讨论字幕设计且标明来源的画面片段**，并非可自由复用的素材，也不能替代原节目。原始画面、出演者肖像、标志及其他第三方素材的权利仍归相关权利人所有。**MIT 许可证不涵盖这些截图。** 标注来源本身不构成转载授权。来源和日本著作权法引用规则的说明见 [NOTICE](NOTICE)。本仓库不提供原始视频或完整节目字幕。

## 为其他项目安装

若要在其他项目中使用，请将 `.agents/skills/akb48-video-subtitles/` 目录复制到 Codex 用户 Skill 目录（Windows 通常为 `%USERPROFILE%\.codex\skills\akb48-video-subtitles`；设置了 `CODEX_HOME` 时为 `$CODEX_HOME/skills/akb48-video-subtitles`）。安装后重新启动一个 Codex 会话。

## 其他检查

下面的 SRT 命令用于检查已创建的文件，请替换示例路径。

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

## 完整视频检查

视频报告包含源文件和成片的完整软件解码、解码错误检查及实际解码帧数比较（`check_decode.py`）。音频哈希对整个解码过程设置超时，并避免管道死锁。使用 `run_checks.py --media-timeout 1800` 设置每个文件的最长处理秒数。帧数比较假定没有有意改变帧率。

## 可选：日语语音识别与详细流程

**faster-whisper** 可用于生成日语转录草稿或交叉检查已有字幕，翻译和说话人判定仍是独立步骤。它是安装在独立环境中的可选依赖，CPU 模式不需要 WSL 或 GPU。参见[安装和转录示例（英语）](.agents/skills/akb48-video-subtitles/references/transcription.md)及[详细工作流程（英语）](docs/workflow.en.md)。

## 按说话人显示的紧凑字幕（0.5.0）

ASS/视频现在需要经过审核的 `work/presentation.json`。`build_presentation.py` 显示姓名或角色，不自动合并身份不明的声音。默认下边距为逻辑 1080p 画布的 30px，即 720p 的 20px。除非用户明确要求，否则省略歌词。参见[结构与命令](.agents/skills/akb48-video-subtitles/references/presentation.md)和[新的合成示例](examples/compact-preview.jpg)。
