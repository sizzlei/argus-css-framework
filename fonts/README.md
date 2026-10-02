# 폰트 self-host

예시 페이지는 Google Fonts 링크를 쓰지만, 폐쇄망에서는 막혀 시스템 폰트로 떨어진다. 그러면 화면 인상이 꽤 달라지므로 **서비스에는 self-host 를 권장**한다 (plotter 가 Phosphor 를 이미 이렇게 쓰고 있다).

1. 인터넷이 되는 PC 에서 `sh fonts/fetch-fonts.sh` → `fonts/*.woff2` 와 `fonts/fonts.css` 생성 (Manrope 400–800, Noto Sans KR 400–700, JetBrains Mono 400–500. 유니코드 범위별로 분할된 파일이라 총 2–3MB, 실제 로드는 필요한 범위만).
2. `fonts/` 폴더째 서비스 `web/public/fonts/` 로 복사.
3. 레이아웃 `<head>` 에서 Google Fonts `<link>` 대신:
   ```html
   <link rel="stylesheet" href="/public/fonts/fonts.css">
   <link rel="stylesheet" href="/public/vendor/argus.min.css">
   ```
   `fonts.css` 의 `url('./…woff2')` 는 상대 경로라 폴더째 옮기면 그대로 동작한다.

폰트 자체를 바꾸고 싶으면 `tokens.css` 의 `--ag-font-sans` / `--ag-font-mono` 만 바꾼다. 한글은 Pretendard 도 좋은 선택이지만 Google Fonts 에 없어 별도 배포가 필요하다.
