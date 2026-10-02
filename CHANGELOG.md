# Changelog

## 1.0.0 — 2026-10-02 · 공개 첫 릴리스
- 이름을 **Argus CSS Framework** 로, 접두사를 `ka-` → **`ag-`** 로 (클래스·토큰 `--ag-*`·data 속성·JS 전역 `AG`·localStorage 키 `ag-theme`). 배포 파일명 `argus.*`.
- 컬러 테마를 색 이름 7종으로: `red` `orange` `yellow` `green` `blue` `indigo` `violet` — 원색을 한 톤 눌러 자연스럽게, 다크·라이트 각각, 액센트 위 글자 대비 확인.
- 사내 전용 문서·템플릿을 걷어내고 Go html/template 적용 예시만 일반화해 남김. MIT 라이선스.
- 샘플 페이지 프로필을 Andy 로.

### 공개 전 이력 (요약)
- 0.6 경량화: dist 는 minified 만, 전체 / core / patterns / charts / auth-landing 번들, JS minify.
- 0.5 백로그 전수 구현: 날짜 범위·배너·알림 센터·승인 카드·⌘K·마법사·콤보박스·JSON 트리·인라인 편집·스켈레톤·밀도 토글·인쇄·forced-colors·키보드 조작, 대비 복구, 리터럴 색 린트, 시각 회귀 스크립트, 디자인 원칙 문서.
- 0.4 표면 깊이·타이포 스케일·폰트 self-host 키트. 0.3 레이아웃 모드 6종, 상단 바 사용자 메뉴, 외부 인증 버튼, Slack 미리보기, 아코디언, 컬러 테마, 인증 페이지 표준화. 0.2 차트·패턴·JS 프리셋. 0.1 최초.
