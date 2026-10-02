# 폰트 self-host

예시 페이지는 Google Fonts 링크를 쓰지만, 폐쇄망에서는 막혀 시스템 폰트로 떨어진다. 그러면 화면 인상이 꽤 달라지므로 **서비스에는 self-host 를 권장**한다.

1. 인터넷이 되는 PC 에서 `sh fonts/fetch-fonts.sh` → `fonts/*.woff2` 와 `fonts/fonts.css` 생성. 마지막 줄에 `done: N blocks, N woff2 …` 가 나오고 블록 수 검증을 통과해야 정상 (macOS 기본 sh/awk/sed 로 동작) (Manrope 400–800, Noto Sans KR 400–700, JetBrains Mono 400–500. 유니코드 범위별로 분할된 파일이라 총 2–3MB, 실제 로드는 필요한 범위만).
2. `fonts/` 폴더째 서비스 `web/public/fonts/` 로 복사.
3. 레이아웃 `<head>` 에서 Google Fonts `<link>` 대신:
   ```html
   <link rel="stylesheet" href="/public/fonts/fonts.css">
   <link rel="stylesheet" href="/public/vendor/argus.min.css">
   ```
   `fonts.css` 의 `url('./…woff2')` 는 상대 경로라 폴더째 옮기면 그대로 동작한다.

폰트 자체를 바꾸고 싶으면 `tokens.css` 의 `--ag-font-sans` / `--ag-font-mono` 만 바꾼다. 한글은 Pretendard 도 좋은 선택이지만 Google Fonts 에 없어 별도 배포가 필요하다.

파싱만 확인하려면 받아둔 Google CSS 로 `GOOGLE_CSS=saved.css sh fonts/fetch-fonts.sh` (woff2 는 받지 않음). 생성된 `fonts.css` 는 원본 `@font-face` 블록(font-family / weight / display / unicode-range)을 그대로 두고 `src` 만 `./NotoSansKR-400-12.woff2` 꼴 로컬 파일로 바꾼 것이다.
