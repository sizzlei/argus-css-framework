# 기존 어드민 디자인 리뉴얼 — Claude Code 프롬프트 키트

Tailwind CDN 이나 Bootstrap 으로 제각각 만들어진 Go + html/template 어드민을 **Argus CSS Framework** 로 갈아입힐 때 쓰는 프롬프트 모음. 세 가지가 들어 있다.

1. **서비스 저장소에 넣을 `CLAUDE.md` 조각** — 모든 세션에 자동으로 붙는 규칙
2. **리뉴얼 착수 프롬프트** — 세션을 시작할 때 한 번 붙여넣는 작업 지시
3. **클래스 매핑표** — Tailwind / Bootstrap → `ag-` 치환 기준

---

## 1. 서비스 저장소 `CLAUDE.md` 에 추가할 조각

> 각 서비스 루트의 `CLAUDE.md` 에 아래 섹션을 그대로 붙여넣는다. `{{COLOR}}` (테마 색 이름) 만 채운다.

```markdown
## UI / 디자인 시스템

이 서비스의 화면은 **Argus CSS Framework** (`web/public/vendor/argus.min.css`, 원본은 `$AG` (= 프레임워크 저장소 경로)) 로 그린다.

- 새 화면·수정 화면은 모두 `ag-` 클래스로 작성한다. Tailwind 유틸, Bootstrap 클래스, 인라인 style 색상은 **새로 추가하지 않는다.** (기존 코드에 남아 있는 것은 그 화면을 손볼 때 함께 치환한다.)
- 색상·간격·라운드는 CSS 변수(`--ag-*`)만 쓴다. hex/rgb 리터럴 금지. 이 서비스의 메인 색은 `argus-css/dist/themes/{{COLOR}}.min.css` 가 정의한다 — `argus.min.css` 다음 줄에 `<link>` 한다. 색을 바꾸고 싶으면 그 파일(원본은 `css/themes/`)만 고친다.
- 컴포넌트 카탈로그: `$AG/examples/components.html` (클래스 목록은 README.md). 필요한 컴포넌트가 없으면 **이 저장소에서 CSS 를 즉흥으로 만들지 말고** argus-css 에 추가한 뒤 가져온다. 그 전까지는 기본 스타일 그대로 둔다. 보고할 때는 **클래스명 · 어떤 화면 몇 곳 · 지금 어떻게 보이는지**를 한 문단으로 (예: "`.ag-toast--info` 가 components.css 에 없음 — 3곳에서 사용, 아이콘 색만 기본값"). 임시로 꼭 필요하면 서비스 자체 CSS 에 `ag-x-` 접두사로 넣고 TODO 주석을 단다.
- 레이아웃은 6개 모드 중 하나: `ag-app`(top) · `ag-app--sidebar` · `ag-app--rail` · `ag-app--tabs` · `ag-app--focus` · `ag-app--dual`. 같은 마크업에 모드 클래스만 다르다 (`examples/layouts.html` 에서 전환 비교). 사이드바 접힘은 `is-collapsed`, 모바일 열림은 `is-open`, 상태 저장은 `argus.js` 가 처리한다.
- 사용자 프로필/로그아웃/테마는 **상단 바 우측** `.ag-topbar__actions` 의 `.ag-user` 드롭다운에 둔다. 사이드바 하단 프로필은 쓰지 않는다 (모드가 바뀌어도 자리가 같아야 하므로).
- 외부 로그인(Google Workspace, Slack, SSO)은 `.ag-provider--google/--slack/--sso`. 구조는 `__logo` + `__label` (+ 선택 `__hint`) — 라벨은 반드시 `<span class="ag-provider__label">` 로 감싼다(줄바꿈 방지·말줄임). 제공자 로고는 공식 브랜드 에셋을 `web/public/img/` 에 두고 `<img>` 로 넣는다. 연결된 계정 화면은 `.ag-account`.
- 아이콘은 Phosphor (`<i class="ph-bold ph-database">`) 를 그대로 쓴다 (`ag-icon` 을 같이 붙일 필요 없음 — 접힌 사이드바에서도 살아남는다). `argus.js` 는 `<body>` 끝(또는 `<head>` + `defer`)에서 로드한다. 프레임워크가 `.ag-btn`, `.ag-sidebar__item` 안의 Phosphor 크기를 맞춘다.
- 차트: ApexCharts 는 `AG.charts.apex(options)` 로 감싸고 `AG.charts.register(chart)` 한다. Chart.js 는 `AG.charts.chartjsDefaults(Chart)` 를 먼저 호출한다. 시리즈 색을 직접 지정하지 않는다 (`AG.charts.palette()` 사용). 히트맵은 `AG.charts.apex({chart:{type:'heatmap'}})` 그대로 쓰거나(series 범위로 `--ag-seq-1..5` 램프 자동) `AG.charts.sequential(n)` / `AG.charts.heatRanges(min,max)` 를 쓴다 — `enableShades` 로 직접 램프를 만들지 않는다. CSS 히트맵 셀은 `.ag-heat--1..5`. 상태색(good/warn/crit)은 차트 시리즈로 쓰지 않는다.
- 테마: 다크 기본. 라이트 전환은 `<html data-theme="light">` + `[data-ag-theme-toggle]` 버튼. 서비스 자체 테마 로직(쿠키 등)이 있으면 `data-theme` 속성을 세팅하는 쪽으로 맞춘다.
- 화면 전체를 감싸는 `<div x-data="…">` 래퍼에는 **`class="ag-page"`** 를 붙인다 (`.ag-main` 의 블록 간격이 래퍼 안으로 이어지도록. 클래스 없는 div / x-data 래퍼는 프레임워크가 자동으로 같은 스택으로 처리하지만, 명시가 안전하다).
- 모달·드로어를 Alpine `x-show` 로 제어하는 화면은 그대로 둔다 — `argus.js` 는 자기가 `data-ag-open` 으로 연 오버레이만 바깥 클릭·ESC 로 닫으므로 충돌하지 않는다. ESC 로 Alpine 모달을 닫고 싶으면 Alpine 쪽 `@keydown.escape.window` 로 처리. 프레임워크 닫기를 조건부로 막아야 하면 `ag:overlay-close` 에서 `preventDefault()`.
- Alpine.js / htmx 는 그대로 유지한다. 리뉴얼은 **마크업과 클래스만** 바꾸는 작업이고, `x-data`, `@click`, `hx-*` 바인딩과 Go 템플릿 로직(`{{if}}`, `{{range}}`, 권한 체크)은 건드리지 않는다.
- 프레임워크 업데이트: `cp $AG/dist/{argus.min.css,argus.js,argus.charts.js} web/public/vendor/ && cp $AG/dist/themes/{{COLOR}}.min.css web/public/vendor/themes/ && cp $AG/dist/VERSION web/public/vendor/argus.VERSION` (AG=~/Desktop/develop/argus-css). 변경 내역은 `$AG/CHANGELOG.md`.
- 디자인 판단이 갈리면 `$AG/docs/principles.md` 가 기준이다.
- 화면을 바꾼 뒤에는 반드시 Playwright 스크린샷(1440px 다크/라이트, 400px)으로 확인하고, 변경 전 스크린샷과 나란히 비교한다.
```

---

## 2. 리뉴얼 착수 프롬프트

> Claude Code 세션 첫 메시지로 붙여넣는다. `[ ]` 부분을 채운다. 한 세션에 한 서비스, 가능하면 한 세션에 2–4개 화면씩.

```
[서비스명] 의 UI 를 Argus CSS Framework 로 리뉴얼한다. 디자인 시스템 원본은 $AG 이고, 규칙은 이 저장소 CLAUDE.md 의 "UI / 디자인 시스템" 섹션에 있다. 먼저 그 섹션과 $AG/README.md, docs/renewal-prompt.md 의 매핑표를 읽어라.

## 범위
- 이번 세션: [web/views/layouts/main.html, web/views/dashboard.html] (레이아웃 → 대시보드 순)
- 다음 세션으로 미룰 것: [목록 화면들, 폼 화면들]
- 건드리지 않는 것: Go 코드, 라우팅, 템플릿 변수/권한 로직, Alpine/htmx 바인딩, 외부 라이브러리 버전

## 순서
1. 현황 파악: 대상 템플릿을 읽고 ① 사용 중인 Tailwind/Bootstrap 클래스 패턴, ② 커스텀 CSS, ③ 차트/에디터 같은 외부 라이브러리 호출, ④ 테마 로직을 표로 정리해 보고한다. 아직 코드를 바꾸지 않는다.
2. 매핑 계획: 각 화면 블록을 어떤 ag- 컴포넌트로 바꿀지 적는다. 매핑표에 없는 UI 가 나오면 "프레임워크에 없음 — argus-css 에 추가 필요" 로 따로 모은다. 내가 확인하면 진행한다.
3. 셸부터: 레이아웃(main.html)에 argus.min.css 와 argus.js 를 연결하고 상단 바/사이드바를 ag-app 구조로 바꾼다. Tailwind CDN 스크립트는 **아직 제거하지 않는다** (다른 화면이 쓰고 있음). 폰트 @import 는 유지하되 Manrope/Noto Sans KR 로 교체.
4. 화면별 치환: 한 화면씩. 바꾼 뒤 Playwright 로 1440px 다크·라이트, 400px 스크린샷을 찍어 /tmp/renewal/[화면]-after-*.png 로 저장하고 before 와 비교해 보고한다. 데이터가 필요한 화면은 로컬 서버를 띄우거나 (go run), 불가능하면 템플릿에 더미 데이터를 넣은 정적 HTML 로 확인한다.
5. 정리: 더 이상 쓰이지 않는 커스텀 CSS 규칙과 vendor 파일을 목록으로 보고한다. 삭제는 내가 승인한 뒤.

## 품질 기준
- 기존 기능(필터, 정렬, 모달 열기/닫기, 폼 제출, SSE 로그 갱신)이 전부 동작해야 한다. 바인딩이 걸린 요소의 id / x-ref / name 은 유지한다.
- 색상 리터럴 0개. `grep -nE "#[0-9a-fA-F]{3,8}|rgb\(" web/views` 결과가 비어야 한다 (svg 아이콘 제외).
- 400px 에서 가로 스크롤 없음. 테이블은 .ag-table-wrap 안에서만 스크롤.
- 상태(정상/주의/장애)는 색만이 아니라 점·아이콘·텍스트로도 구분된다.
- 한 화면에 액센트 카드(.ag-card--accent)는 최대 1개.
- 대시보드 첫 화면(스크롤 전)에는 카드 7개 이하. 핵심 지표 3~4 + 차트 1 + 보조 2. 나머지는 아래로 내리거나 목록 화면으로.
- 폰트는 `fonts/` self-host (fonts/README.md). Google Fonts 링크를 서비스에 그대로 두지 않는다.
- 모든 변경은 화면 단위 커밋. 메시지는 "ui(dashboard): migrate to argus-css" 형식.

## 보고 형식
각 단계가 끝나면 (1) 바꾼 파일, (2) 매핑표에 없어서 임시 처리한 것, (3) 스크린샷 경로, (4) 다음 단계 제안을 짧게 적는다. 질문은 한 번에 모아서.
```

---

## 3. 클래스 매핑표

### 3-1. 레이아웃 (Tailwind → ag-)

| 기존 패턴 | ag- |
|---|---|
| `<body class="... min-h-screen">` + sticky header | `.ag-app` > `.ag-topbar` + `.ag-main` |
| `<body class="h-screen flex overflow-hidden">` + `<aside class="w-64 ...">` | `.ag-app.ag-app--sidebar` > `.ag-sidebar` + `.ag-topbar` + `.ag-main` |
| `aside` 접힘 `lg:w-20` / Alpine `sidebarCollapsed` | `.is-collapsed` on `.ag-app--sidebar`, 버튼 `[data-ag-sidebar-toggle]` |
| 모바일 오버레이 `fixed inset-0 bg-slate-900/80 lg:hidden` | `.ag-sidebar-backdrop` + `.is-open`, 버튼 `[data-ag-sidebar-open]` |
| 사이드바 그룹 아코디언 (`toggleGroup`) | `.ag-sidebar__group[data-ag-group]` > `.ag-sidebar__group-toggle` |
| 접힘 툴팁 (Alpine `showTooltip`) | `.ag-sidebar__item[data-tip="…"]` (CSS 전용) |
| `max-w-7xl mx-auto px-5` | `.ag-main` (자동) |
| `grid grid-cols-12 gap-5` + `col-span-6 lg:col-span-3` | `.ag-grid` + `.ag-col-6` / `.ag-col-3` (반응형 내장) |
| `flex items-center justify-between` | `.ag-cluster.ag-cluster--between` 또는 `.ag-card__head` |
| `space-y-3` | `.ag-stack` |
| 페이지 제목 블록 (h1 + 설명 + 우측 버튼) | `.ag-page-header` > `__title` + `__actions` |
| 가로 탭 네비 `px-3 py-1.5 rounded-lg bg-red-600` | `.ag-nav` > `.ag-nav__item[aria-current=page]` |
| 로그인 2단 `min-h-screen grid md:grid-cols-2` | `.ag-auth` > `.ag-auth__brand` + `.ag-auth__panel` > `.ag-auth__card` |
| 배경 글로우 `.app-bg`, `.bg-grid-pattern` | `.ag-app.ag-glow` (선택) / 인증 화면은 `.ag-auth__brand` 가 내장 |

### 3-2. 컴포넌트

| 기존 | ag- |
|---|---|
| `bg-white rounded-2xl border border-slate-200 shadow-sm p-5` / Bootstrap `.card` / `.surface-card` | `.ag-card` (+ `__head` `__title` `__subtitle` `__body` `__foot`) |
| 카드 안 작은 박스 `bg-slate-50 rounded-xl p-4` | `.ag-tile` 또는 `.ag-card.ag-card--sm` |
| KPI `text-3xl font-extrabold` + 라벨 / `.kpi` `.kpi-value` | `.ag-stat` (`__value` `__label`) · 아이콘 있으면 `.ag-stat-card` |
| 증감 `text-emerald-600 +12%` / `.kpi-trend-up` | `.ag-delta.ag-delta--up` (원형) / `--inline` (필) |
| 버튼 `px-4 py-2 bg-blue-600 text-white rounded-lg` / `.btn.btn-primary` | `.ag-btn.ag-btn--primary` |
| 보조 버튼 `border border-slate-300` / `.btn-secondary` `.btn-light` | `.ag-btn` 또는 `.ag-btn--outline` |
| 위험 `bg-red-600` / `.btn-outline-danger` | `.ag-btn--danger` |
| 아이콘 버튼 `w-9 h-9 grid place-items-center rounded-lg` / `.icon-btn` | `.ag-btn.ag-btn--icon.ag-btn--ghost` |
| 배지 `px-2 py-0.5 text-xs rounded-full bg-emerald-50 text-emerald-700` / `.badge-soft-success` | `.ag-badge.ag-badge--good` (+ `<span class="ag-dot ag-dot--good">`) |
| ADMIN 뱃지 `bg-red-600 text-white text-[9px] rounded-full` | `.ag-badge.ag-badge--solid.ag-badge--crit.ag-badge--sm` |
| 카운트 `rounded-full bg-slate-100 px-2` | `.ag-badge.ag-badge--count` |
| 상태 점 `w-2 h-2 rounded-full bg-emerald-500` / `.dot-indicator` | `.ag-dot.ag-dot--good` (+ `--pulse`) |
| 테이블 `min-w-full divide-y` / `.table.table-hover` | `.ag-table-wrap` > `.ag-table` (`--dense`, `--striped`, `--sticky-col`) |
| 정렬 헤더 (sortable.js) | `th.is-sorted` > `button.ag-sort` |
| 테이블 하단 "n개 중 1–20" + 페이지 | `.ag-table-foot` + `.ag-pagination` |
| 선택 행 액션 바 | `.ag-bulkbar` |
| 입력 `px-4 py-2.5 border rounded-lg focus:ring-2` / `.form-control` | `.ag-input` (라벨·힌트는 `.ag-field` > `.ag-label` + `.ag-hint`, 오류는 `.is-invalid`) |
| `<select>` / `.form-select` | `.ag-select` (`--pill`, `--sm`, `--inline`) |
| 토글 `relative inline-flex h-6 w-11 rounded-full` / `.form-switch` | `label.ag-switch > input[type=checkbox]` |
| 체크박스 `.form-check-input` | `label.ag-check > input` |
| 검색창 (아이콘 왼쪽) / `.topbar-search` | `.ag-input-group` > `svg.ag-icon` + `.ag-input.ag-input--pill` |
| 폼 2열 그리드 | `.ag-form-grid` (+ `.ag-field--full`) · 하단 버튼 `.ag-form-actions` |
| 탭 `border-b-2 border-blue-600` / `.nav-tabs` | `.ag-tabs` > `.ag-tabs__item[data-ag-tab]` + `[data-ag-panel]` |
| 세그먼트 (기간 선택) | `.ag-segmented` > `__item` |
| 진행률 `bg-slate-100 rounded-full h-1.5` + inner | `.ag-progress(--sm)` > `__bar` · 라벨 포함은 `.ag-meter-row` |
| 알림 박스 `.alert-*` / `bg-amber-50 border-amber-200` | `.ag-alert.ag-alert--warn` |
| Toast (toast.js, notify.js, `.toast-stack`) | 컨테이너 `.ag-toast-stack` > `.ag-toast(--good/--crit)` — JS 는 기존 것 유지, 클래스만 교체 |
| 확인 모달 (confirm.js, Bootstrap `.modal`) | `<dialog class="ag-modal">` > `.ag-modal__panel` — `[data-ag-open]`/`[data-ag-close]` 또는 기존 Alpine 유지 |
| 우측 슬라이드 패널 | `.ag-drawer.is-open` |
| 드롭다운 메뉴 (Alpine `x-show`) | `.ag-dropdown.is-open` > `.ag-menu` > `__item` |
| 툴팁 | `[data-tip="…"]` |
| 빈 상태 `.empty-state` / `text-slate-400 py-16` | `.ag-empty` > `__icon` `__title` |
| 로딩 `animate-pulse` | `.ag-skeleton` · 스피너 `.ag-spinner` · 버튼 `.is-loading` · htmx `.htmx-indicator` (내장) |
| 활동/이력 `.activity-list` `.timeline` | `.ag-timeline` > `__item.is-good` |
| 키-값 정의 `dl.grid.grid-cols-3` | `dl.ag-kv` (`--stack`) |
| 아바타 이니셜 / `.user-chip` `.avatar` | `.ag-avatar` · 이름+메타 `.ag-person` |
| 세션 타이머 칩 (`sessionTimer`) / `.session-warn` | `.ag-session(.is-warning)` / `<dialog class="ag-modal">` |
| 빠른 작업 그리드 `.quick-actions` | `.ag-quick-actions` > `.ag-quick-action` |
| 헬스 체크 행 `.health-list` | `.ag-health` > `__row` |
| 공지 Slack 미리보기 `.sp-*` | `.ag-slack__*` — 3-5 치환표 참고. slack_preview.js 의 클래스 문자열만 바꾸면 됨 |

### 3-3. 화면 유형별 패턴

| 유형 | 화면 | ag- |
|---|---|---|
| 인증 | 로그인 Step 1/2/3 (이메일 → OTP → QR 등록), 좌측 브랜드 그라데이션 패널 | `.ag-auth` + `.ag-stepper--sm` + `.ag-otp-input` + `.ag-auth__qr` (+ 선택 `--landing`). **적용 예시: `templates/go-html-template/login.html`** — 복사해 브랜드 문구만 바꾸면 됨 |
| 작업 진행 | 복구·배치 진행 단계 | `.ag-stepper` (`is-done` / `is-active` / `is-failed`) |
| 로그 | SSE 실시간 로그 | `.ag-log.ag-log--live` > `__head` + `pre.ag-log__body` > `__line.is-info` |
| SQL | 쿼리 textarea (`bg-slate-800 text-green-400`) | `textarea.ag-code` · 결과 코드 `.ag-code-block--lang` |
| 설정 비교 | 변경 전후 diff | `.ag-diff` > `__line.is-add/.is-del/.is-ctx` · 나란히 `.ag-compare` |
| 태그 | 키=값 태그 편집 | `.ag-tags` > `.ag-tag` (`__key` `__val` `__remove`) · 입력 `.ag-tag-input` |
| 대시보드 | Treemap / 도넛 / 주간 바 | ApexCharts + `AG.charts.apex` · JS 없는 대안 `.ag-treemap` `.ag-donut` `.ag-cols` |
| 공통 | 팀·태그·카테고리 필터 목록 (하나 선택) | `.ag-list` + `button.ag-list__item` + `is-active` — 사이드바 밖에서 `.ag-sidebar__item` 을 빌리지 않는다 |
| 대시보드 | 분포 도넛 (ApexCharts) | `AG.charts.apex({chart:{type:'donut'}})` 또는 `.ag-donut` |
| 대시보드 | 상태 bar + 분포 doughnut (Chart.js) | `AG.charts.chartjsDefaults(Chart)` 후 기존 코드 유지 |
| 에디터 | EasyMDE 마크다운 에디터 | 래퍼 `<div class="ag-editor">` 로 감싸기 |
| 첨부 | 파일 첨부 | `.ag-dropzone` + `.ag-file` |
| Slack | Block Kit 미리보기 `.sp-*` | `.ag-slack` (아래 3-5) |
| 목록+상세 | 공지함/알림함 | `.ag-app--dual` + `.ag-pane` / `.ag-pane-item` |
| 헤더 | 2단 헤더 (브랜드 행 + 탭 네비 행) | `.ag-app--tabs` + `.ag-topbar__row--main` / `--nav` |
| 소형 앱 | 메뉴 5개 안팎 | `.ag-app--rail` (모바일 하단 탭 `.ag-sidebar--bottom-tabs`) |
| 전체 | 설정/계정/마법사 화면 | `.ag-app--focus` |
| 전체 | 사이드바 하단 사용자 블록, 상단 `user-chip`, `sessionTimer` | `.ag-user` 드롭다운 (+ `.ag-menu__user`, `.ag-session`) |
| 전체 | Google/Slack 로그인 버튼, 연결된 계정 | `.ag-provider--*`, `.ag-account` |
| 전체 | 날짜 입력 다크 보정 (`::-webkit-calendar-picker-indicator { filter: invert }`) | `.ag-input[type=date]` 내장 — 커스텀 CSS 삭제 |
| 전체 | `[x-cloak]`, `.htmx-indicator`, `.scrollbar-hide` | 내장 (`.ag-scrollbar-hide`) — 레이아웃 인라인 `<style>` 삭제 |

### 3-4. 레이아웃 모드 선택 기준

| 모드 | 언제 | 예 |
|---|---|---|
| `ag-app` (top) | 메뉴 4~6개, 대시보드 중심, 가로 공간이 아까울 때 | Argus Console 개요 |
| `ag-app--sidebar` | 그룹이 있는 메뉴 10개 이상, 관리 도구 | DB 관리 콘솔 |
| `ag-app--rail` | 메뉴 5~7개, 아이콘으로 식별 가능, 모바일 사용 많음 | 소형 모니터링 도구 |
| `ag-app--tabs` | 상단에 검색/사용자 행이 필요하고 메뉴는 한 줄 탭으로 충분 | 데이터 추출 도구 |
| `ag-app--focus` | 네비가 방해되는 화면: 설정, 계정, 등록 마법사, 긴 폼 | 모든 서비스의 설정 |
| `ag-app--dual` | 목록을 보면서 하나를 열어보는 화면 | 공지함, 알림함 |

한 서비스 안에서 화면별로 모드를 섞어도 된다 (예: 본문은 sidebar, 설정은 focus). 상단 바와 `.ag-user` 는 항상 같은 자리.

### 3-5. Slack 미리보기 `.sp-*` → `.ag-slack__*` 치환표

규칙: `sp-X` → `ag-slack__X`. 예외 3개만 기억하면 된다.

| sp- | ag- |
|---|---|
| `.sp-preview-wrap` | `.ag-slack` (스티키 패널 포함. 정적 배치는 `.ag-slack--static`) |
| `.sp-preview-title` | `.ag-slack__title` |
| `.sp-preview-hint` | `.ag-slack__hint` |
| `.sp-message` `.sp-avatar` `.sp-bubble` `.sp-meta` `.sp-name` `.sp-tag` `.sp-time` | `.ag-slack__message` `__avatar` `__bubble` `__meta` `__name` `__tag` `__time` |
| `.sp-block` `.sp-section` `.sp-header` `.sp-text` `.sp-divider` `.sp-fields` `.sp-field` | `.ag-slack__block` `__section` `__header` `__text` `__divider` `__fields` `__field` |
| `.sp-context` `.sp-ctx-img` `.sp-ctx-text` `.sp-image-block` `.sp-image-title` `.sp-image` `.sp-accessory` | `.ag-slack__context` `__ctx-img` `__ctx-text` `__image-block` `__image-title` `__image` `__accessory` |
| `.sp-mention` `.sp-placeholder` `.sp-inline-code` `.sp-code` | `.ag-slack__mention` `__placeholder` `__inline-code` `__code` |
| `.sp-actions` `.sp-btn` | `.ag-slack__actions` `__btn` |
| `.sp-btn-primary` `.sp-btn-danger` | `.ag-slack__btn--primary` `.ag-slack__btn--danger` |
| `.sp-empty` `.sp-error` `.sp-unknown` | `.ag-slack__empty` `__error` `__unknown` |

`slack_preview.js` 에서는 `sed -E "s/sp-btn-(primary|danger)/ag-slack__btn--\1/g; s/\bsp-/ag-slack__/g"` 한 번이면 끝난다. Slack 버튼의 초록/빨강은 Slack 화면을 재현하는 것이므로 토큰 예외로 유지한다.

### 3-6. 색상 치환 기준

| 기존 (서비스마다 다름) | 토큰 |
|---|---|
| 배경 `#020617` `#04090B` `bg-slate-50` | `var(--ag-bg)` |
| 카드 `bg-white` `bg-slate-900` `.card-bg` | `var(--ag-surface)` |
| 보더 `border-slate-200` `border-white/10` | `var(--ag-border)` |
| 본문 `text-slate-800` `text-slate-200` | `var(--ag-text)` |
| 보조 `text-slate-500` `text-white/60` | `var(--ag-text-2)` |
| 메타 `text-slate-400` `text-white/40` `text-[10px]` | `var(--ag-text-3)` + `.ag-text-xs` |
| 브랜드 색 하드코딩 `#DC2626` `#2563EB` `#10B981` … | `var(--ag-accent)` — 값은 `dist/themes/<color>.min.css` 가 공급. 템플릿에 hex 를 쓰지 않는다 |
| 성공 `emerald-*` `green-*` | `--ag-good` / `--ag-good-soft` |
| 경고 `amber-*` `yellow-*` | `--ag-warn` / `--ag-warn-soft` |
| 위험 `red-*` `rose-*` | `--ag-crit` / `--ag-crit-soft` |
| 정보 `blue-*` `sky-*` `cyan-*` | `--ag-info` / `--ag-info-soft` |
| 차트 시리즈 하드코딩 `['#3b82f6','#6366f1','#10b981',…]` | `AG.charts.palette()` |

---

## 4. 컬러 테마

앱마다 메인 색을 가질 수 있다. 기본 7종(red orange yellow green blue indigo violet)은 `dist/themes/<color>.min.css` 를 복사해 로드하고, 새 색이 필요하면 프레임워크 저장소 `css/themes/_template.css` 를 복사해 만든다. 반드시 다크·라이트 둘 다 정의. 아래는 `harpoon.css` 의 실제 내용.

```css
/* red.css — 기본 제공 테마 중 하나 */
:root {
  --ag-accent: #e84c5e; --ag-accent-hover: #f3727f; --ag-accent-soft: rgb(232 76 94 / .16);
  --ag-text-on-accent: #ffffff; --ag-brand-from: #e84c5e; --ag-brand-to: #f59e6b;
}
:root[data-theme="light"] {
  --ag-accent: #d23a4c; --ag-accent-hover: #b82e3e; --ag-accent-soft: rgb(210 58 76 / .12);
  --ag-text-on-accent: #ffffff; --ag-brand-from: #d23a4c; --ag-brand-to: #e8793a;
}
```

`--ag-accent-2`(핑크 보조)와 차트 범주색은 바꾸지 않는다 — 서비스마다 차트 색이 달라지면 팀 전체 대시보드 가독성이 떨어진다. 메인 색은 서비스마다 다른 것이 **기본 방침**이며, 네 서비스의 테마 파일은 `css/themes/` 에 이미 있다 (argus blue · harpoon red · plotter emerald · harbinger purple).

---

## 5. 리뉴얼 완료 판정 (서비스 단위)

- [ ] `tailwindcss.js` / `bootstrap.min.css` 로드 제거됨 (vendor 파일 삭제)
- [ ] 레이아웃 인라인 `<style>` 블록이 비었거나 서비스 자체 CSS 파일로 이동
- [ ] `grep -rnE "class=\"[^\"]*(bg-|text-|border-|rounded-|px-|py-|flex |grid )" web/views | wc -l` → 0
- [ ] 모든 화면 다크·라이트·400px 스크린샷 확인
- [ ] 로그인 → 주요 CRUD → 로그아웃 수동 시나리오 통과
- [ ] `argus-css` 에 추가 요청한 컴포넌트가 머지되어 임시 `ag-x-*` 가 남아 있지 않음
