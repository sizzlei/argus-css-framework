# Changelog

## 1.0.0 — 2026-10-02 · 공개 첫 릴리스
- 이름을 **Argus CSS Framework** 로, 접두사를 `ka-` → **`ag-`** 로 (클래스·토큰 `--ag-*`·data 속성·JS 전역 `AG`·localStorage 키 `ag-theme`). 배포 파일명 `argus.*`.
- 컬러 테마를 색 이름 7종으로: `red` `orange` `yellow` `green` `blue` `indigo` `violet` — 원색을 한 톤 눌러 자연스럽게, 다크·라이트 각각, 액센트 위 글자 대비 확인.
- 사내 전용 문서·템플릿을 걷어내고 Go html/template 적용 예시만 일반화해 남김. MIT 라이선스.
- 샘플 페이지 프로필을 Andy 로. 컬러 테마 선택은 하단 데모 네비에서 (모든 페이지).
- 범주색 `--ag-cat-1~4` (+ `-soft` / `-text`) 토큰과 `.ag-badge--cat1~4`(+ `--solid`), `.ag-tag--cat1~4`, `.ag-dot--cat1~4` 추가 — 엔진·태그·팀 같은 "종류" 를 상태색 없이 구분. 차트 범주색과 같은 네 가지, 라이트는 글자색을 한 단계 깊게 (4.5:1).
- `.ag-toast-stack--static` 이 모달 위로 올라오던 버그 수정 — flex 아이템은 `position: static` 이어도 `z-index` 가 살아 쌓임 맥락을 만든다 (90 > 모달 80). `z-index: auto` 로 해제.
- `.ag-toast--warn` / `--info` 추가 (기존 good/crit 만 있었음). 4종 모두 왼쪽 3px 톤 바로 구분. `AG.toast(msg,'info')` 도 그대로 동작.
- 컴포넌트 카탈로그 `.ag-qr` 예시에 실제 QR(otpauth 데모 URL, SVG) 추가. 720px 이하 상단 바 브랜드 축소·말줄임(좁은 화면 가로 스크롤 방지).
- `fonts/fetch-fonts.sh` 수정: `awk | while read` 가 @font-face 블록을 줄 단위로 끊어 `src` 만 남던 버그. 블록을 한 줄로 펴서 처리, 파일명 `NotoSansKR-400-12.woff2` 꼴, 결과 검증(블록·src 수 일치), BSD sed/awk 호환, `GOOGLE_CSS=` 드라이런. 2차 수정: 주석 없는 블록(Noto Sans KR 한글 서브셋 480개)이 `IFS=탭 read` 의 선행 탭 처리에 밀려 통째로 빠지던 문제 — 줄을 통째로 읽어 직접 쪼개고, 검증을 원본 블록 수 일치 + 한글(U+D55C) 담당 블록 ≥ 굵기 수로 강화.

### 공개 전 이력 (요약)
- 0.6 경량화: dist 는 minified 만, 전체 / core / patterns / charts / auth-landing 번들, JS minify.
- 0.5 백로그 전수 구현: 날짜 범위·배너·알림 센터·승인 카드·⌘K·마법사·콤보박스·JSON 트리·인라인 편집·스켈레톤·밀도 토글·인쇄·forced-colors·키보드 조작, 대비 복구, 리터럴 색 린트, 시각 회귀 스크립트, 디자인 원칙 문서.
- 0.4 표면 깊이·타이포 스케일·폰트 self-host 키트. 0.3 레이아웃 모드 6종, 상단 바 사용자 메뉴, 외부 인증 버튼, Slack 미리보기, 아코디언, 컬러 테마, 인증 페이지 표준화. 0.2 차트·패턴·JS 프리셋. 0.1 최초.
