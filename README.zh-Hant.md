# AKB48 影片字幕 Codex Skill

[English](README.md) · [Русский](README.ru.md) · [한국어](README.ko.md) · [Español (LatAm)](README.es-419.md) · [Bahasa Indonesia](README.id.md) · [ไทย](README.th.md) · [简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md)

**本中文文件為翻譯初稿，正式使用前建議由中文母語者審校。**


用於翻譯及製作 AKB48 與 48 Group 影片字幕的可重複工作流程。它協助 Codex 區分對白、說話者標示、歌曲與畫面文字，核對姓名拼法，並檢查字幕及渲染後的影片。

本儲存庫包含 Codex Skill、語言設定初稿、基本 SRT 檢查工具、安裝說明，以及兩張近期俄文翻譯影片的效果示例。俄文設定來自完整節目的製作流程；韓文設定仍是草稿，需要韓語母語者審閱；其他語言設定則是供貢獻者完善的起點。

## 快速安裝

請先準備 Git、Python 3.11+、支援 libass 的 FFmpeg/FFprobe 和 Codex 存取權限。以下命令複製儲存庫並檢查工具，不會安裝必要程式。在 Codex 中開啟複製後的資料夾並開始新聊天。

```sh
git clone https://github.com/ivst/akb48-video-subtitle-codex-skill.git
cd akb48-video-subtitle-codex-skill
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py --require-ass
```

## 提示詞範例

```text
使用 $akb48-video-subtitles，將 [本機影片路徑或已獲授權的 URL] 翻譯為繁體中文，包括畫面文字。
提供獨立的 SRT 與 ASS、內嵌字幕的影片及檢查報告。使用靠近畫面下緣的最新精簡版面，以已核實的姓名或中性角色區分說話者，不要合併身分不明的聲音。
省略背景音樂與歌詞。核對姓名、對話含義、畫面文字及成品影格，記錄疑點。不要發布任何內容。
```

## 預覽

**第 12 集——說話者標籤與精簡字幕面板**（[來源影片](https://www.youtube.com/watch?v=aPznmLtjedw)）

![第 12 集字幕示例](examples/preview-episode-12.jpg)

*引用畫面來源：AKB48，**AKB48の全力エンタメ学園**，第12集（2026年4月18日），[YouTube 原始影片](https://www.youtube.com/watch?v=aPznmLtjedw)。* 此截圖用於技術性說明說話者姓名標籤與精簡翻譯字幕面板的配置，方便評估姓名與對白如何區隔，而不僅依賴顏色。

**第 13 集——最終握手環節的精簡字幕面板**（[來源影片](https://www.youtube.com/watch?v=mHF3TEk6lwQ)）

![第 13 集字幕示例](examples/preview-episode-13.jpg)

*引用畫面來源：AKB48，**AKB48の全力エンタメ学園**，第13集（2026年4月25日），[YouTube 原始影片](https://www.youtube.com/watch?v=mHF3TEk6lwQ)。* 此截圖用來分析握手場景中的字幕面板位置，以及譯文與原始畫面元素之間的關係；目的並非重新發布節目作為娛樂內容。

上述兩張截圖是**為技術性討論字幕設計而引用並標示來源的畫面片段**，並非可以自由重用的素材，也不能取代原節目。原始畫面、演出者肖像、標誌及其他第三方素材的權利仍歸相關權利人所有。**MIT 授權不涵蓋這些截圖。** 標明來源本身不等於取得轉載許可。來源及日本著作權法引用規範的說明請參閱 [NOTICE](NOTICE)。本儲存庫不提供原始影片或整集字幕。

## 為其他專案安裝

若要用於其他專案，請將 `.agents/skills/akb48-video-subtitles/` 資料夾複製到 Codex 使用者 Skill 目錄（Windows 通常是 `%USERPROFILE%\.codex\skills\akb48-video-subtitles`；若設定 `CODEX_HOME`，則是 `$CODEX_HOME/skills/akb48-video-subtitles`）。安裝後請重新啟動 Codex 工作階段。

## 其他檢查

下方 SRT 命令用來檢查已建立的檔案，請替換範例路徑。

```powershell
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py
python .agents/skills/akb48-video-subtitles/scripts/check_srt.py path\to\dialogue.srt
```

內附腳本只使用 Python 標準函式庫，不需 `pip install`。硬體配置及可選 ASR/下載工具請參閱[資源需求](.agents/skills/akb48-video-subtitles/references/resources.md)。

## 工作流程

1. 核對日文對白，並分開整理標牌、標題、規則和結果文字。
2. 依據所選語言設定及已審閱的單集詞彙表翻譯。
3. 只有在證據充分時才標示說話者；不確定的反應使用中性標示。
4. 按需求產生通用 SRT、具樣式的 ASS 和/或 MP4。
5. 抽查整集不同位置的畫面並檢查最終成品；適用時檢查解碼、時間軸、封裝及音訊保留情形。

詳見[工作流程說明](.agents/skills/akb48-video-subtitles/references/workflow.md)及[語言設定](.agents/skills/akb48-video-subtitles/references/languages/README.md)。

## 資源需求

一般 1080p、20–40 分鐘影片可從 8 GB 記憶體及較新的 4 核心 CPU 開始；若要在本機執行 ASR，16 GB 記憶體及 6–8 核心會較舒適。建議預留約 10 GB 空間存放來源、中間檔、成品及備份。GPU 加速為選用。4K 或高位元率影片可能需要更多磁碟與記憶體。以上為規劃估算，實際使用量取決於編碼格式、ASR 模型及編碼器。

## 權利與隱私

只處理及發布你有權使用的素材。未取得再散布許可前，請勿在公開 Pull Request 中加入單集逐字稿、完整字幕、憑證、Cookie 或私人詞彙表。示例影格用於展示字幕版面；節目素材的權利仍屬於其所有者。

## 授權條款

原創文件與腳本採用 MIT 授權。示例圖片及其中呈現的節目素材不包含在此授權內，請參閱 [NOTICE](NOTICE) 與 [LICENSE](LICENSE)。

## 完整影片檢查

影片報告包含來源與成品的完整軟體解碼、解碼錯誤檢查及實際解碼影格數比較（`check_decode.py`）。音訊雜湊對整個解碼過程設定逾時，並避免管線死結。使用 `run_checks.py --media-timeout 1800` 設定每個檔案最長處理秒數。影格數比較假設沒有刻意改變影格率。

## 選用：日語語音辨識與詳細流程

**faster-whisper** 可用於產生日文逐字稿草稿或交叉檢查現有字幕，翻譯與說話者判定仍是獨立步驟。它是安裝於獨立環境的選用依賴，CPU 模式不需要 WSL 或 GPU。請參閱[安裝與轉錄範例（英文）](.agents/skills/akb48-video-subtitles/references/transcription.md)及[詳細工作流程（英文）](docs/workflow.en.md)。

## 依說話者顯示的精簡字幕（0.5.0）

ASS/影片現在需要經過審閱的 `work/presentation.json`。`build_presentation.py` 顯示姓名或角色，不自動合併身分不明的聲音。預設下邊距為邏輯 1080p 畫布的 30px，即 720p 的 20px。除非使用者明確要求，否則省略歌詞。請參閱[結構與命令](.agents/skills/akb48-video-subtitles/references/presentation.md)和[新的合成範例](examples/compact-preview.jpg)。
