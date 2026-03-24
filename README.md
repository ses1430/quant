# YouTube to Gemini Helper

유튜브 영상을 우클릭 한 번으로 Google Gemini에게 분석 요청할 수 있는 Chrome 확장 프로그램입니다.

## 소개

YouTube 영상을 시청하다가 내용을 빠르게 파악하고 싶을 때, 영상 URL을 복사하고 Gemini를 열고 프롬프트를 작성하는 과정이 번거롭습니다. **YouTube to Gemini Helper**는 이 과정을 자동화하여, 우클릭 컨텍스트 메뉴 또는 영상 아래 버튼 한 번으로 Gemini가 영상을 상세히 분석해주도록 합니다.

## 주요 기능

**원클릭 Gemini 분석** — 유튜브 영상 위에서 우클릭 → "Gemini로 이 영상 설명하기"를 선택하면, 자동으로 Gemini 탭이 열리고 프롬프트가 입력·전송됩니다.

**커스텀 프롬프트** — 확장 프로그램 설정 페이지에서 Gemini에 전송할 프롬프트를 자유롭게 편집할 수 있습니다. `${url}` 플레이스홀더를 사용하면 영상 URL이 자동으로 삽입됩니다.

**상세한 기본 프롬프트** — 기본 프롬프트는 메타데이터(제목, 업로더, 길이, URL), 타임스탬프 포함 포괄적 내용 분석, 핵심 메시지 및 결론까지 구조화된 출력을 요청하도록 설계되어 있습니다.

**YouTube UI 통합 버튼** — 영상 페이지의 좋아요/싫어요 버튼 옆에 "Gemini" 버튼이 자동으로 추가되어, 우클릭 없이도 바로 사용할 수 있습니다.

## 설치 방법

1. 이 저장소를 클론하거나 [ZIP 파일](youtube-gemini-helper.zip)을 다운로드하여 압축을 해제합니다.
   ```bash
   git clone https://github.com/ses1430/youtube-gemini-helper.git
   ```
2. Chrome 브라우저에서 `chrome://extensions/`로 이동합니다.
3. 우측 상단의 **개발자 모드**를 활성화합니다.
4. **압축해제된 확장 프로그램을 로드합니다** 버튼을 클릭합니다.
5. 다운로드한 폴더(manifest.json이 있는 폴더)를 선택합니다.

## 사용 방법

### 방법 1: 컨텍스트 메뉴 (우클릭)

1. YouTube에서 영상 페이지(`youtube.com/watch?v=...`)를 엽니다.
2. 영상 플레이어 위에서 **마우스 우클릭**합니다.
3. **"Gemini로 이 영상 설명하기"** 메뉴를 클릭합니다.
4. Gemini 탭이 자동으로 열리고, 프롬프트가 입력·전송됩니다.

### 방법 2: Gemini 버튼

1. YouTube 영상 페이지에서 좋아요/싫어요 버튼 옆에 나타나는 **"Gemini"** 버튼을 클릭합니다.
2. 이후 동작은 동일합니다.

### 프롬프트 커스터마이징

1. 확장 프로그램 아이콘을 우클릭 → **옵션**을 선택하거나, `chrome://extensions/`에서 해당 확장 프로그램의 **세부정보 → 확장 프로그램 옵션**을 클릭합니다.
2. 프롬프트를 원하는 대로 수정합니다.
3. `${url}` 자리에 YouTube 영상 URL이 자동 삽입됩니다.
4. **저장** 버튼을 클릭합니다.

## 프로젝트 구조

```
youtube-gemini-helper/
├── manifest.json          # Chrome 확장 프로그램 설정 (Manifest V3)
├── background.js          # 서비스 워커 — 컨텍스트 메뉴 생성 및 클릭 처리
├── gemini_content.js      # Gemini 페이지에 주입되는 콘텐츠 스크립트 — 프롬프트 자동 입력·전송
├── youtube_content.js     # YouTube 페이지에 주입되는 콘텐츠 스크립트 — Gemini 버튼 추가
├── options.html           # 확장 프로그램 설정 페이지 UI
├── options.js             # 설정 페이지 로직 — 프롬프트 저장/초기화
├── styles.css             # YouTube 내 Gemini 버튼 스타일
├── gemini_logo.png        # Gemini 로고 이미지
├── icon*.png              # 확장 프로그램 아이콘 (16/32/48/128px)
└── youtube-gemini-helper.zip  # 배포용 ZIP 파일
```

## 동작 원리

1. **background.js** — 확장 프로그램 설치 시 YouTube 영상 페이지 전용 컨텍스트 메뉴를 등록합니다. 메뉴 클릭 시 현재 영상 URL을 `chrome.storage.local`에 저장한 뒤 Gemini 탭을 엽니다.
2. **gemini_content.js** — `gemini.google.com`에서 실행되는 콘텐츠 스크립트입니다. 저장된 URL과 프롬프트 템플릿을 불러와 Gemini의 입력 필드에 자동으로 프롬프트를 채우고 전송 버튼을 클릭합니다.
3. **youtube_content.js** — YouTube 영상 페이지에서 좋아요/싫어요 버튼 옆에 "Gemini" 버튼을 동적으로 삽입합니다. SPA 내비게이션(`yt-navigate-finish` 이벤트)에도 대응합니다.

## 기술 스택

- **Chrome Extension Manifest V3**
- **Vanilla JavaScript** (프레임워크 없음)
- **Chrome APIs**: `contextMenus`, `storage`, `tabs`, Content Scripts

## 필요 권한

| 권한 | 용도 |
|------|------|
| `contextMenus` | 우클릭 메뉴 항목 생성 |
| `storage` | 영상 URL 및 커스텀 프롬프트 저장 |
| `host_permissions` (youtube.com) | YouTube 페이지 접근 및 버튼 삽입 |
| `host_permissions` (gemini.google.com) | Gemini 페이지에 프롬프트 자동 입력 |

## 알려진 제한사항

- Gemini 웹 UI의 DOM 구조가 변경되면 프롬프트 자동 입력이 동작하지 않을 수 있습니다.
- 전송 버튼 선택자(`aria-label`)가 "메시지 보내기" 또는 "Send message"에 의존하므로, 다른 언어 설정에서는 동작하지 않을 수 있습니다.
- Gemini에 로그인되어 있어야 정상 동작합니다.

## 라이선스

이 프로젝트는 자유롭게 사용할 수 있습니다.
