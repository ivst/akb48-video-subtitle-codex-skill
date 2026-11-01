# Codex용 AKB48 영상 자막 Skill

[English](README.md) · [Русский](README.ru.md) · [한국어](README.ko.md) · [Español (LatAm)](README.es-419.md) · [Bahasa Indonesia](README.id.md) · [ไทย](README.th.md) · [简体中文](README.zh-Hans.md) · [繁體中文](README.zh-Hant.md)

**한국어 안내문은 초안이며, 배포 전에 한국어 모어 화자의 검토가 필요합니다.**


AKB48 및 48 Group 영상의 번역과 자막 작업을 위한 재사용 가능한 워크플로입니다. 대사, 화자 표시, 노래, 화면 속 문구를 구분하고, 확인된 이름 표기를 사용하며, 자막과 렌더링 결과를 점검하도록 Codex를 안내합니다.

저장소에는 Codex Skill, 언어 프로필 초안, 기본 SRT 검사기, 설치 안내와 최근 러시아어 번역 영상의 예시 화면 두 장이 포함되어 있습니다. 러시아어 프로필은 전체 영상 작업에 사용한 절차를 바탕으로 합니다. 한국어 프로필은 아직 초안이므로 실제 사용 전에 한국어 모어 화자의 검토가 필요합니다. 다른 프로필도 기여자가 다듬을 시작점입니다.

## 빠른 설치

Git, Python 3.11 이상, libass를 지원하는 FFmpeg/FFprobe 및 Codex 이용 환경이 필요합니다. 아래 명령은 저장소를 복제하고 도구를 검사하며 필수 프로그램을 설치하지는 않습니다. 복제한 폴더를 Codex에서 열고 새 채팅을 시작하세요.

```sh
git clone https://github.com/ivst/akb48-video-subtitle-codex-skill.git
cd akb48-video-subtitle-codex-skill
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py --require-ass
```

## 프롬프트 예시

```text
$akb48-video-subtitles를 사용해 [로컬 영상 경로 또는 사용 권한이 있는 URL]을 화면 문구까지 한국어로 번역해 주세요.
별도 SRT와 ASS, 자막이 삽입된 영상, 검사 보고서를 만들어 주세요. 화면 하단의 최신 간결한 레이아웃을 사용하고, 서로 다른 사람의 대사는 확인된 이름이나 중립적인 역할로 구분해 주세요. 불명확한 화자를 합치지 마세요.
배경 음악과 노래 가사는 제외해 주세요. 이름, 대사의 의미, 화면 문구와 최종 영상 프레임을 확인하고 미해결 부분을 기록해 주세요. 아무것도 공개하지 마세요.
```

## 미리보기

**12화 — 화자 이름과 간결한 자막 패널** ([원본 영상](https://www.youtube.com/watch?v=aPznmLtjedw))

![12화 자막 예시](examples/preview-episode-12.jpg)

*인용 화면 출처: AKB48, **AKB48の全力エンタメ学園**, 제12회(2026년 4월 18일), [YouTube 원본 영상](https://www.youtube.com/watch?v=aPznmLtjedw).* 화자 이름 표시와 간결한 번역 자막 패널의 구성을 기술적으로 설명하기 위한 예시입니다. 이름과 대사가 시각적으로 구분되는 방식, 색상 외의 식별 요소를 검토할 수 있습니다.

**13화 — 악수 장면의 간결한 자막 패널** ([원본 영상](https://www.youtube.com/watch?v=mHF3TEk6lwQ))

![13화 자막 예시](examples/preview-episode-13.jpg)

*인용 화면 출처: AKB48, **AKB48の全力エンタメ学園**, 제13회(2026년 4월 25일), [YouTube 원본 영상](https://www.youtube.com/watch?v=mHF3TEk6lwQ).* 악수 장면에서 번역 자막 패널이 배치되는 방식을 설명하는 예시입니다. 원본 화면의 요소를 고려한 자막 위치와 가독성을 검토하기 위한 것이며, 프로그램을 대체하기 위한 것이 아닙니다.

위 두 이미지는 **자막 디자인에 관한 기술적 설명을 위한 인용 화면**이며 자유롭게 재사용할 수 있는 자료가 아닙니다. 원본 영상, 출연자 이미지, 로고 및 기타 제3자 요소의 권리는 각 권리자에게 있습니다. **MIT 라이선스는 이 이미지들에 적용되지 않습니다.** 출처 표시는 재배포 허가를 의미하지 않습니다. 자세한 출처와 일본 인용 관련 주의사항은 [NOTICE](NOTICE)를 참고하세요. 원본 영상이나 전체 회차 자막은 포함되지 않습니다.

## 다른 프로젝트에 설치하기

다른 프로젝트에서도 사용하려면 `.agents/skills/akb48-video-subtitles/` 폴더를 Codex 사용자 Skill 경로에 복사하세요. Windows의 기본 경로는 보통 `%USERPROFILE%\.codex\skills\akb48-video-subtitles`이고, `CODEX_HOME`을 설정한 경우 `$CODEX_HOME/skills/akb48-video-subtitles`입니다. 설치 후 새 Codex 세션을 시작하세요.

## 추가 검사

아래 SRT 검사는 이미 만든 파일에 사용합니다. 예시 경로를 바꾸세요.

```powershell
python .agents/skills/akb48-video-subtitles/scripts/check_environment.py
python .agents/skills/akb48-video-subtitles/scripts/check_srt.py path\to\dialogue.srt
```

포함된 스크립트는 Python 표준 라이브러리만 사용합니다. 추가 `pip install`은 필요하지 않습니다. 자세한 내용은 [리소스 요구 사항](.agents/skills/akb48-video-subtitles/references/resources.md)을 참고하세요.

## 작업 흐름

1. 일본어 대사를 확인하고 화면 문구, 제목, 규칙, 결과를 별도로 기록합니다.
2. 선택한 언어 프로필과 검토된 회차별 용어집을 사용해 번역합니다.
3. 근거가 충분할 때만 화자를 표시하고, 불확실한 반응은 중립적으로 둡니다.
4. 요청에 따라 SRT, 스타일이 적용된 ASS 및/또는 MP4를 만듭니다.
5. 영상 전체에서 대표 장면을 살펴보고 최종 렌더를 확인합니다. 필요한 경우 디코딩, 타이밍, 패키지와 음성 보존도 점검합니다.

자세한 내용은 [작업 지침](.agents/skills/akb48-video-subtitles/references/workflow.md)과 [언어 프로필](.agents/skills/akb48-video-subtitles/references/languages/README.md)을 확인하세요.

## 컴퓨터 사양

1080p, 20~40분 영상 기준으로 RAM 8GB와 최근 4코어 CPU면 기본 자막 편집 및 CPU 인코딩을 시작할 수 있습니다. 로컬 음성 인식을 함께 사용할 경우 RAM 16GB와 6~8코어가 더 쾌적합니다. 원본, 임시 파일, 출력본과 백업을 위해 약 10GB 이상의 여유 공간을 확보하세요. GPU는 선택 사항입니다. 4K 또는 고비트레이트 영상에는 더 많은 자원이 필요할 수 있습니다. 실제 사용량은 코덱, 인식 모델, 인코더에 따라 달라지는 예상치입니다.

## 권리와 개인정보

사용 및 공개가 허용된 자료만 처리하고 게시하세요. 공개 Pull Request에 권한이 확인되지 않은 회차별 대본, 전체 자막, 인증 정보, 쿠키 또는 개인 용어집을 넣지 마세요. 예시 이미지는 자막 배치를 보여주기 위한 것이며, 원 프로그램의 권리는 각 권리자에게 있습니다.

## 라이선스

직접 작성한 문서와 스크립트는 MIT 라이선스를 따릅니다. 예시 이미지와 그 안의 프로그램 자료는 라이선스에서 제외됩니다. [NOTICE](NOTICE)와 [LICENSE](LICENSE)를 확인하세요.

## 전체 영상 검사

영상 결과 보고서에는 원본과 출력의 전체 디코딩, 디코더 오류 및 실제 디코딩된 프레임 수 비교가 포함됩니다 (`check_decode.py`). 오디오 해시 계산은 전체 디코딩 시간 제한으로 보호됩니다. `run_checks.py --media-timeout 1800`으로 파일당 제한 시간을 초 단위로 지정합니다. 프레임 수 비교는 의도적인 프레임 레이트 변환이 없는 경우를 전제로 합니다.

## 선택 사항: 일본어 음성 인식과 작업 안내

**faster-whisper**는 일본어 대본 초안을 만들거나 기존 자막을 대조하는 선택 도구입니다. 번역과 화자 판별은 별도 단계입니다. 별도 환경에 설치하며 CPU 사용에는 WSL이나 GPU가 필요하지 않습니다. [설치 및 인식 예시(영어)](.agents/skills/akb48-video-subtitles/references/transcription.md)와 [상세 작업 안내(영어)](docs/workflow.en.md)를 참고하세요.

## 화자별 자막과 간결한 배치 (0.5.0)

ASS/영상에는 검토된 `work/presentation.json`이 필요합니다. `build_presentation.py`는 이름/역할을 표시하고 불명확한 화자를 자동 병합하지 않습니다. 기본 하단 여백은 1080p에서 30px, 720p에서 20px입니다. 노래 가사는 명시적 요청이 있을 때만 포함합니다. [스키마와 명령](.agents/skills/akb48-video-subtitles/references/presentation.md), [새 합성 예시](examples/compact-preview.jpg)를 참고하세요.
