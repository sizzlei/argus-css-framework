# Argus CSS Framework

어드민 페이지용 순수 CSS 디자인 시스템. 빌드 도구 없이 `<link>` 한 줄, 다크 테마 기본 + 라이트, 컬러 테마 7종, 레이아웃 모드 6종, CSS 전용 차트.
Go `html/template` 같은 서버 렌더링 어드민을 염두에 두고 만들었지만 어떤 스택에서든 쓸 수 있다. JS 는 전부 선택 사항.

A pure-CSS design system for admin pages — dark-first with a light theme, 7 color themes, 6 layout modes, CSS-only charts, optional data-attribute JS helpers. Korean docs; class names are English (`ag-` prefix). MIT.

**라이브 데모 (GitHub Pages):** https://sizzlei.github.io/argus-css-framework/

| 페이지 | 내용 |
|---|---|
| [대시보드](https://sizzlei.github.io/argus-css-framework/examples/index.html) | 스탯·CSS 차트·알림·배너·사용자 메뉴 |
| [리소스 목록](https://sizzlei.github.io/argus-css-framework/examples/resources.html) | 필터·테이블·벌크바·페이지네이션·사이드바 레이아웃 |
| [상세](https://sizzlei.github.io/argus-css-framework/examples/detail.html) | 탭·KV·타임라인·폼·모달·드로어 |
| [로그인](https://sizzlei.github.io/argus-css-framework/examples/login.html) | 2단 인증 레이아웃·OTP·외부 로그인·컬러 테마 전환 |
| [레이아웃 모드](https://sizzlei.github.io/argus-css-framework/examples/layouts.html) | 6개 모드를 같은 콘텐츠로 전환 |
| [컴포넌트 카탈로그](https://sizzlei.github.io/argus-css-framework/examples/components.html) | 전체 컴포넌트·패턴·토큰 |
| [조합 매트릭스](https://sizzlei.github.io/argus-css-framework/examples/matrix.html) | 모든 변형 × 조합 (회귀 확인용 — 어긋난 셀을 찾는 페이지) |

로컬에서는 저장소를 받아 `examples/index.html` 을 그냥 열면 된다 (빌드 불필요). 페이지 하단 왼쪽 네비로 이동, 우상단 버튼으로 다크/라이트 전환.

```
dist/argus.min.css              ← 가장 단순한 선택: 이것 하나만 <link> (134KB, gzip 23KB)
  — 또는 골라 쓰기 —
dist/argus.core.min.css         ← 토큰·베이스·레이아웃·컴포넌트·유틸 (62KB, gzip 12KB). 최소 세트
dist/argus.patterns.min.css     ← 인증·사이드바·로그·Slack·배너·알림·승인·⌘K·트리… (61KB, gzip 11KB)
dist/argus.charts.min.css       ← CSS 차트(도넛·바·히트맵·게이지…) + Apex/Chart.js 보정 (11KB, gzip 3KB). 차트 있는 페이지만
dist/argus.auth-landing.min.css ← 랜딩형 인증 변형 (선택, 2KB)
dist/themes/<color>.min.css     ← 컬러 테마 red / orange / yellow / green / blue / indigo / violet. css 다음에 한 줄 더 <link>
dist/argus.js                   ← 선택. 테마 토글·탭·사이드바·드롭다운·모달(소유권)·토스트·키보드·콤보박스·차트 호버 (11KB, gzip 3KB)
dist/argus.charts.js            ← 선택. ApexCharts / Chart.js 에 토큰 주입 (AG.charts.apex / chartjsDefaults / sequential / heatRanges, 8KB)
dist/VERSION
css/ js/                        ← 소스. 읽을 땐 여기. js/modules/ 가 argus.js 로 합쳐진다 (사람이 읽는 합본이 필요하면 `sh build.sh --readable`)
fonts/                          ← 폰트 self-host 키트 (fetch-fonts.sh → woff2 + fonts.css)
index.html                      ← GitHub Pages 진입점 (examples/ 로 리다이렉트)
examples/                       ← 예시 사이트 (= 라이브 데모 소스). components.html 이 전체 카탈로그
                                   index(대시보드) / resources(목록) / detail(상세) / login(인증) / layouts(6모드 + 컬러 전환) / matrix(변형 조합 매트릭스, tools/gen_matrix.py 가 생성)
templates/                      ← Go html/template + Alpine 적용 예시 (인증 레이아웃, 3단계 로그인)
tools/                          ← check.py(값 단언 회귀 62항목) · shots.py(스크린샷) · gen_matrix.py(매트릭스 생성)
docs/                           ← 디자인 원칙, 기존 어드민을 Claude Code 로 리뉴얼할 때의 프롬프트 키트
CLAUDE.md                       ← 이 저장소에서 Claude Code 로 작업할 때의 규칙
```

## 빠른 시작

```html
<!doctype html>
<html lang="ko">                      <!-- 라이트 테마: <html lang="ko" data-theme="light"> -->
<head>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/argus.min.css">
  <link rel="stylesheet" href="/static/themes/blue.min.css">   <!-- 선택: 컬러 테마 -->
</head>
<body>
  <div class="ag-app">
    <header class="ag-topbar">
      <a class="ag-topbar__brand" href="/"><span class="ag-dot ag-dot--accent"></span>Service Name</a>
      <nav class="ag-topbar__center"><div class="ag-nav">
        <a class="ag-nav__item" aria-current="page" href="/">개요</a>
        <a class="ag-nav__item" href="/list">목록</a>
      </div></nav>
      <div class="ag-topbar__actions">
        <button class="ag-btn ag-btn--icon ag-btn--outline" data-ag-theme-toggle aria-label="테마">…</button>
      </div>
    </header>
    <main class="ag-main">
      <div class="ag-grid">
        <section class="ag-card ag-col-8">…</section>
        <section class="ag-card ag-card--accent ag-col-4">…</section>
      </div>
    </main>
  </div>
  <script src="/static/argus.js"></script>  <!-- 선택. body 끝에서 로드 (또는 <head> 에 defer) — 사이드바 상태 복원·차트 호버가 DOM 을 찾는다 -->
</body>
</html>
```

Go `html/template` 앱이라면 `embed.FS` 로 `dist/` 파일 몇 개만 포함시키면 됩니다. **폰트는 self-host 를 권장합니다** — 폐쇄망에서 Google Fonts 가 막히면 시스템 폰트로 떨어져 인상이 달라집니다. `fonts/fetch-fonts.sh` 로 woff2 를 받아 `fonts/fonts.css` 를 static 에 두세요 (fonts/README.md).

## 브라우저 요구사항

`color-mix()`, `:has()`, `dvh`, 컨테이너 쿼리, `oklab` 를 폴백 없이 씁니다. **Chrome / Edge 111+, Safari 16.4+, Firefox 128+** (2023년 3월 이후 에버그린). 사내 어드민이라 구형 브라우저를 고려하지 않았고, IE·구형 Safari 는 지원하지 않습니다. 지원 범위를 넓혀야 하면 `build.sh` 의 lightningcss `--targets` 를 낮추되, `:has()` 와 `color-mix()` 는 변환되지 않으므로 해당 규칙(`.ag-provider:has(…)`, 모든 soft 색)을 직접 손봐야 합니다.

## 설계 원칙

- **접두사 `ag-`**: 기존 페이지의 Bootstrap / 자체 CSS와 충돌 없이 점진 적용. BEM 변형(`block__element--modifier`), 상태는 `is-active`, `is-selected`, `is-invalid`.
- **토큰 우선**: 색·간격·라운드·그림자는 전부 `--ag-*` 변수. 앱별 커스터마이즈는 테마 파일 한 장 또는 `:root { --ag-accent: … }` 한 줄로.
- **다크 기본, 라이트는 `data-theme="light"`**: 컴포넌트는 토큰만 참조하므로 테마 블록을 건드릴 일이 없습니다.
- **상태색은 예약색**: `good / warn / crit / info` 는 상태 표시 전용. 엔진·태그·팀 같은 **범주**는 `--cat1~4`(배지·태그·점), 차트 시리즈는 `--ag-chart-1~4` — 같은 네 가지 색이라 화면 어디서든 범주 1 은 같은 색입니다 (두 테마 모두 색각이상 분리도 검증 완료). 다섯 번째 범주는 만들지 않습니다 → "기타".
- **변형 선언 순서 = 우선순위**: 한 블록 안에서 모양(`--sm` `--count` `--stack`) → 톤(상태·액센트·범주) → 조합(`--solid`) 순으로 선언해 `:not()` 체인 없이 어떤 조합이든 예측 가능하게. 모양 변형은 색을 건드리지 않습니다. 폴백 규칙(컨테이너 없는 카드·버튼 간격)은 `:where()` 로 특이도 0.
- **JS 는 자기가 연 것만 닫는다**: `argus.js` 의 바깥 클릭·ESC 는 `data-ag-open` 으로 연 오버레이에만 — Alpine/Vue 가 제어하는 것은 건드리지 않습니다 (아래 JS 헬퍼).
- **유틸리티는 최소한**: 컴포넌트 클래스로 못 푸는 예외에만 `ag-mt-4`, `ag-text-3`, `ag-text-left/center/right`, `ag-scroll-y(--sm/--md/--lg)` 같은 유틸을 씁니다. Tailwind처럼 쓰려고 만든 게 아닙니다.

## 앱에 배포하기 (버전 관리)

npm 패키지가 아니라 **각 앱 저장소에 dist 를 복사**하는 방식을 권장합니다. 동기화는 수작업이지만 단순하고, 앱마다 올리는 시점을 고를 수 있습니다.

```sh
# 앱 저장소에서
AG=~/path/to/argus-css
cp $AG/dist/argus.min.css $AG/dist/argus.js $AG/dist/argus.charts.js web/public/vendor/
cp $AG/dist/themes/blue.min.css web/public/vendor/themes/
cp $AG/dist/VERSION web/public/vendor/argus.VERSION
git add web/public/vendor && git commit -m "chore(ui): argus-css $(cat $AG/dist/VERSION)"
```

`dist/VERSION` 이 현재 버전이고, 변경 내역은 `CHANGELOG.md`. 앱 `CLAUDE.md` 의 UI 섹션에 위 명령을 "프레임워크 업데이트" 로 적어두면 Claude Code 세션이 그대로 씁니다.

## 디자인 원칙

`docs/principles.md` — 한 화면에 하나만 강조, 첫 화면 카드 7개 이하, 상태는 색만으로 말하지 않기, 메뉴 수가 레이아웃을 정함, 쓰지 말 것 목록.

## 컬러 테마

메인 색은 앱마다 다르게 가져갈 수 있습니다. 공통인 것은 표면·텍스트·간격·컴포넌트 모양·상태색·차트 범주색이고, 액센트와 브랜드 그라데이션만 테마 파일이 바꿉니다.

```html
<link rel="stylesheet" href="/static/argus.min.css">
<link rel="stylesheet" href="/static/themes/green.min.css">   <!-- red / orange / yellow / green / blue / indigo / violet -->
```

7종 모두 원색 그대로가 아니라 한 톤 눌러 자연스럽게 맞춘 값이고, 다크·라이트 각각 정의돼 있습니다. 밝은 색(yellow·green)은 위에 올라가는 글자가 자동으로 어둡게 바뀝니다. 새 색은 `css/themes/_template.css` 를 복사해 채우세요. `examples/layouts.html` · `examples/login.html` 하단에서 바꿔볼 수 있습니다.

## 레이아웃 모드

같은 마크업(`.ag-topbar` / `.ag-sidebar` / `.ag-main`)에 모드 클래스만 바꿉니다. `examples/layouts.html` 에서 전환해 볼 수 있습니다.

| 클래스 | 모드 | 쓰임 |
|---|---|---|
| `.ag-app` | top | 상단 바 + 캡슐 네비 (기본) |
| `.ag-app--sidebar` | sidebar | 좌측 사이드바, `is-collapsed` 접힘, 그룹 아코디언 |
| `.ag-app--rail` | rail | 84px 아이콘 레일, 모바일은 `.ag-sidebar--bottom-tabs` 로 하단 탭 |
| `.ag-app--tabs` | tabs | 2단 상단 바 (`.ag-topbar__row--main` + `--nav`) |
| `.ag-app--focus` | focus | 네비 없는 좁은 중앙 컬럼 (설정·마법사) |
| `.ag-app--dual` | dual | 사이드바 + `.ag-pane` 목록 + 상세 |

사용자 프로필은 모드와 무관하게 상단 바 우측 `.ag-user` 드롭다운에 둡니다.

## 기존 어드민에 적용할 때 (Claude Code)

`docs/renewal-prompt.md` 에 ① 앱 저장소 `CLAUDE.md` 에 붙일 규칙 조각, ② 리뉴얼 착수 프롬프트, ③ Tailwind/Bootstrap → `ag-` 매핑표가 있습니다.

## 서비스에 적용하며 생기는 변경 (피드백 루프)

실제 서비스를 이 프레임워크로 갈아입히다 보면 "변형이 없다", "스크립트가 깨진다" 같은 건이 계속 나옵니다. 처리 원칙:

1. **서비스 저장소에서 즉흥 CSS 를 만들지 않는다.** 없는 것은 그대로 두고(읽는 데 지장 없는 수준이면 기본 스타일로), 프레임워크에 "무엇이 어디서 몇 곳에 필요한지" 를 보고한다.
2. 프레임워크에서 고친다 — CSS(`css/`) + **카탈로그 예시**(`examples/src/components.html`) + **README 컴포넌트 목록** + `CHANGELOG.md` 네 군데를 한 커밋에. 변형을 추가했으면 `tools/gen_matrix.py` 목록에도, 서비스에서 들어온 버그면 `tools/check.py` 에 단언 하나. 예시 없이 CSS 만 추가하지 않는다 (예시가 곧 회귀 테스트이자 문서).
3. `sh build.sh && python3 tools/gen_matrix.py && python3 build_examples.py && python3 tools/check.py` 통과 후 1440/400px 다크·라이트 확인, 커밋.
4. 서비스는 `dist/` 를 다시 복사한다 (위 "앱에 배포하기").

지금까지 이 루프로 들어온 것 (전부 `CHANGELOG.md` 에 있음):

- 1.0.0: `.ag-toast--warn/--info`, `.ag-provider__label`, `fonts/fetch-fonts.sh` 블록 파싱 두 건, 모바일 상단 바 넘침, `.ag-qr` 예시 누락
- 1.1.0: `.ag-badge--count` 가 톤을 덮던 것, `.ag-toast-stack--static` z-index, `a/button.ag-card` 의 display·`align-items`, `.ag-tile--stack`, `.ag-form-grid--2/--3/--4` + `--span2/--span3`, `.ag-input-group--end` 패딩, `.ag-text-left` `.ag-scroll-y`, 범주 아바타, 레이아웃 간격 토큰과 `.ag-page`, `--tabs` 초광폭, `.ag-glow` 복원, argus.js 오버레이 소유권·`<head>` 로드·Phosphor 아이콘, 히트맵 순차 램프 `--ag-seq-1..5` / `AG.charts.sequential`, `.ag-list__item.is-active`

## 토큰 요약

| 그룹 | 변수 | 비고 |
|---|---|---|
| 표면 | `--ag-bg` `--ag-surface` `--ag-surface-2` `--ag-surface-3` `--ag-inverse` | 바닥 → 카드 → 카드 안 타일 → 강조 |
| 잉크 | `--ag-text` `--ag-text-2` `--ag-text-3` | 본문 / 보조 / 메타 |
| 액센트 | `--ag-accent` (바이올렛) `--ag-accent-2` (핑크) | `*-soft` 는 투명 배경용 |
| 상태 | `--ag-good` `--ag-warn` `--ag-crit` `--ag-info` | `*-soft` 동반 |
| 차트 | `--ag-chart-1..4` `--ag-chart-hatch` `--ag-chart-grid` | 범주색 고정 순서 |
| 순차 램프 | `--ag-seq-1..5` | 히트맵·밀도용 단일 색 5단계 (`--ag-chart-1` → `--ag-surface-2`). `.ag-heat--1..5` 와 `AG.charts.sequential(5)` 가 같은 값 |
| 범주 | `--ag-cat-1..4` + `*-soft` `*-text` | 배지·태그·점에서 종류 구분. 차트 범주색과 같은 네 가지, 라이트는 글자색을 한 단계 깊게 |
| 간격 | `--ag-space-1..12` | 4px 기준 |
| 레이아웃 간격 | `--ag-gap-grid`(24) `--ag-gap-main`(32) `--ag-gap-section`(20) | 카드 사이 · 본문 블록 사이 · 섹션 헤드↔본문. 서비스가 `:root` 에서 한 번에 조정 |
| 라운드 | `--ag-radius-sm/md/lg/xl/pill` | 8 / 12 / 18 / 24 / 999 |
| 타이포 | `--ag-text-xs..4xl` `--ag-font-sans` `--ag-font-mono` | 본문 14px |

## 컴포넌트 목록

레이아웃 `ag-app` `ag-app--sidebar` `ag-topbar` `ag-nav` `ag-sidebar` `ag-main` `ag-page` (x-data 같은 본문 래퍼에 — 블록 간격 이어받음, `--tight`) `ag-page-header` `ag-section` `ag-grid` + `ag-col-N` `ag-stack` `ag-cluster` `ag-row` `ag-breadcrumb`

차트 (CSS 전용) `ag-donut` `ag-donut-legend` `ag-bars` `ag-cols` `ag-heatmap` (`--crit`) / `ag-heat` (`--l` 연속 또는 `--1…--5` = `--ag-seq-1..5`, `--empty`) `ag-heat-scale` `ag-gauge` `ag-ring` `ag-spark` `ag-stat-card` `ag-treemap` + ApexCharts 보정 (`.ag-chart .apexcharts-*`)

패턴 `ag-daterange` `ag-banner` `ag-notif` `ag-meter-row--compact` `ag-approval` `ag-cmdk` `ag-wizard` `ag-combobox` `ag-tree` `ag-td--editable` `ag-skeleton-rows` · `data-density="compact"` · `@media print` (`.ag-print-header`) `ag-auth` (표준 인증: 어두운 표면 패널 + 점 격자 · `__logo-box` `__name` `__version` `__status` `__mobile-head` `__mobile-foot` · 폼 쪽 `__glass` `__email-chip` `__qr` `__qr-icon` `__foot`; `--landing` 은 그라데이션 패널 변형. 3단계 로그인 전체는 `templates/go-html-template/login.html`) `ag-accordion` (details / `__toggle`+`is-open` / `--plain` / `--cards`) `ag-sidebar__node` (2단계 메뉴) `ag-modal-overlay` `ag-slack` (Block Kit 미리보기 전체) `ag-provider` `ag-account` `ag-user` `ag-pane` / `ag-pane-item` `ag-otp` (칸 분리 `__cell`) / `ag-otp-input` (한 칸 6자리) `ag-qr` (흰 패딩 박스 180px, QR 자체는 img/svg/canvas 로 · 생성 전 `__pending` 플레이스홀더) `ag-secret` `ag-status-screen` `ag-brand-mark` `ag-session` `ag-stepper` `ag-log` `ag-code` `ag-code-block` `ag-tok-*` `ag-editor` `ag-diff` `ag-compare` `ag-tag` (`--cat1~4`) `ag-tags` `ag-tag-input` `ag-dropzone` `ag-file` `ag-popover` `ag-accordion` `ag-bulkbar` `ag-tr--expand` `ag-table--sticky-col` `ag-spinner` `ag-loading-overlay` `ag-msg` `ag-health` `ag-glow` (`.ag-app` 배경 글로우, 선택) `ag-scrollbar-hide` · 사이드바 `is-collapsed` / `is-open` / `ag-sidebar-backdrop` / `ag-sidebar__group-toggle`

컴포넌트 `ag-btn` (`--primary/--outline/--ghost/--inverse/--danger/--accent2` · `--sm/--lg/--icon/--block` · 조합 `--ghost.--danger` 는 평소 중립 → hover 시 crit, `--outline.--danger` 는 crit 테두리 — 테이블 행의 삭제 버튼용) `ag-btn-group` `ag-segmented` `ag-chip` `ag-meter-chips` `ag-badge` (`--good/--warn/--crit/--info` 상태 · `--cat1~4` 범주 · `--solid` · `--count` — count 는 모양만이라 어떤 톤과도 조합) `ag-dot` (`--cat1~4` 포함) `ag-delta` `ag-card` (`a.ag-card` / `button.ag-card` 는 정렬·밑줄·폰트·안쪽 행 전체 폭 자동 처리, `is-selected`) `ag-tile` (가로 라벨↔값 · `--stack` 세로 · `--inverse`) `ag-list` (`a/button.ag-list__item` + `is-active` 선택 목록 · `--divided` · `__item--meter`) `ag-stat` `ag-avatar` (`--good/--warn/--crit/--info/--accent2/--cat1~4/--neutral` · `--sm/--lg` · `--ring`) `ag-person` `ag-table` `ag-table-foot` `ag-pagination` `ag-field` `ag-input` `ag-select` `ag-textarea` `ag-check` `ag-switch` `ag-input-group` (앞 아이콘 · `--end` 뒤 버튼 · 둘 다 조합 가능) `ag-form-grid` (auto-fit 기본 · `--2/--3/--4` 열 고정 — `--full` 섞을 때는 고정 · 필드 `--span2/--span3/--full`) `ag-tabs` `ag-progress` `ag-meter-row` `ag-alert` `ag-insight` `ag-toast` (`--good` `--warn` `--crit` `--info`, 왼쪽 톤 바) `ag-dropdown` / `ag-menu` `ag-modal` `ag-drawer` `[data-tip]` `ag-empty` `ag-skeleton` `ag-kv` `ag-timeline` `ag-chart` `ag-legend` `ag-bubble` `ag-quick-actions` / `ag-quick-action` (`__icon--1~4` · 2줄 라벨 `__body` > `__title` + `__meta` · `__end`)

전체 모양과 조합 예시는 `examples/components.html` 에서 확인하세요.

## JS 헬퍼 (선택)

`dist/argus.js` 는 data 속성으로만 동작합니다. **`<body>` 끝에서 로드하거나 `<head>` 에서 `defer` 로** — 1.1 부터는 `<head>` 에 그냥 넣어도 DOM 준비 후 초기화하지만, 클릭 위임은 로드 즉시 걸리므로 위치는 body 끝이 기본입니다. 아이콘은 `<svg class="ag-icon">` 과 Phosphor `<i class="ph-…">` 둘 다 같은 대우를 받습니다 — 위치(입력칸 선행 아이콘)·색(사이드바·알림·토스트)·크기(로고 박스·드롭존) 규칙이 전부 `:is(.ag-icon, [class*="ph-"])` 라서 `<i>` 에 `ag-icon` 을 붙일 필요가 없고, 접힌 사이드바·rail·dual 에서도 살아남습니다.

| 속성 | 동작 |
|---|---|
| `data-ag-theme-toggle` | 클릭 시 다크 ↔ 라이트, `localStorage('ag-theme')` 에 저장. 버튼 안의 해·달 아이콘은 `.ag-only-dark` / `.ag-only-light` 로 하나만 보이게 (svg 든 Phosphor `<i>` 든) |
| `.ag-segmented__item` `.ag-tabs__item` | 형제 중 하나만 `is-active` |
| `data-ag-tabs` + `data-ag-tab="x"` + `data-ag-panel="x"` | 탭 패널 전환 |
| `data-ag-dropdown` | 부모 `.ag-dropdown` 에 `is-open` 토글, 바깥 클릭 시 닫힘 |
| `data-ag-open="id"` / `data-ag-close` | `<dialog class="ag-modal">`, `.ag-modal-overlay`, `.ag-drawer` 열고 닫기. **소유권 원칙:** 바깥 클릭·ESC 는 argus.js 가 `data-ag-open`(또는 ⌘K)으로 연 것만 닫는다 — Alpine `x-show` / Vue `v-show` 가 제어하는 오버레이·드로어·드롭다운은 건드리지 않음. `data-ag-static` 은 바깥 클릭·ESC 차단. 닫기 직전 cancelable `ag:overlay-close`(detail.reason = button/backdrop/escape), 닫힌 뒤 `ag:overlay-closed`, 연 뒤 `ag:overlay-open` 이벤트. 코드에서는 `AG.overlay.open(el)` / `.close(el)` / `.owns(el)` |
| `AG.toast(message, type?, ms?)` | 우하단 토스트. type = good/warn/crit/info, ms=0 이면 수동 닫기 |
| `data-ag-expand` (tr 안 버튼) | 다음 `tr.ag-tr--expand` 펼치기/접기 |
| `data-ag-detail-open` / `data-ag-detail-close` | dual 레이아웃 모바일에서 목록 ↔ 상세 |
| `.ag-accordion__toggle`, `.ag-sidebar__item--parent` | 토글형 아코디언 / 2단계 메뉴 (상태 저장: `data-ag-node`) |
| `data-ag-banner-close` / `.ag-daterange__presets .ag-chip[data-ag-days]` | 배너 닫기 / 날짜 프리셋이 두 date 입력을 채움 |
| `[data-ag-cmdk]` | ⌘K / Ctrl+K 로 열리는 오버레이. 방향키·ESC 지원 |
| 키보드 | 세그먼트·탭 ←→, 메뉴·cmdk·콤보박스·알림 ↑↓, ESC 로 모든 오버레이 닫기 |
| `.ag-chart[data-ag-chart='[{x,y,label,value}]']` | 라인 차트 호버 툴팁 + 커서. 동적으로 추가한 차트는 `AG.chartHover()` 로 다시 붙임 |
| `data-ag-sidebar-toggle` / `data-ag-sidebar-open` | 사이드바 접기(저장) / 모바일 열기 |
| `.ag-sidebar__group[data-ag-group]` > `.ag-sidebar__group-toggle` | 그룹 접기(저장) |

차트 라이브러리를 쓰는 화면은 `dist/argus.charts.js` 를 추가로 로드합니다.
```js
const chart = new ApexCharts(el, AG.charts.apex({ chart:{type:'donut',height:280}, series:[108,61,17], labels:['MySQL','PostgreSQL','Oracle'] }));
chart.render(); AG.charts.register(chart);   // data-theme 바뀌면 자동 재렌더
AG.charts.chartjsDefaults(Chart);             // Chart.js 전역 기본값

// 히트맵: 단일 색 순차 램프. CSS 토큰 --ag-seq-1..5 (= .ag-heat--1..5) 와 같은 색이라 CSS 셀과 Apex 셀이 맞고, 라이트에서 셀이 사라지지 않음
new ApexCharts(el, AG.charts.apex({ chart:{type:'heatmap'}, series })).render();   // ranges 생략 → series 최소~최대 5등분, 셀 경계 --ag-chart-grid
AG.charts.sequential(5)                       // ['#2f2f49', …] 연한→진한 (#hex). sequential(n, '--ag-crit') 처럼 기준색 변경 가능
AG.charts.heatRanges(0, 400)                  // Apex plotOptions.heatmap.colorScale.ranges 직접 지정할 때
```

첫 페인트 깜빡임을 막으려면 `<head>` 에 다음을 넣습니다.
```html
<script>try{if(localStorage.getItem('ag-theme')==='light')document.documentElement.setAttribute('data-theme','light')}catch(e){}</script>
```

## 빌드

```sh
npm i                       # 선택: esbuild + lightningcss-cli (없어도 빌드는 됨 — sed 간이 압축으로)
sh build.sh                 # css/*.css → dist/*.min.css + themes + js. 저장소 node_modules/.bin → PATH → npx 순으로 minifier 탐색
python3 tools/gen_matrix.py # examples/src/matrix.html 재생성 (변형을 추가했으면)
python3 build_examples.py   # examples/src/*.html → examples/*.html (아이콘 스프라이트 인라인)
python3 tools/check.py      # 값 단언 회귀 62항목 (Playwright, 실패 시 exit 1). shots.py 는 스크린샷 (1440 다크/라이트 · 400 · 3400 tabs)
```

## 기존 어드민에 적용하는 순서

1. `dist/argus.min.css` 를 static 에 추가하고 `<link>` 만 걸어둔다. `ag-` 접두사라 기존 화면은 깨지지 않는다.
2. 페이지 셸부터 바꾼다: `ag-app` / `ag-topbar` / `ag-main`. 이것만으로 톤이 맞춰진다.
3. 테이블 → `ag-table-wrap > ag-table`, 버튼 → `ag-btn`, 상태 텍스트 → `ag-badge` 순으로 치환한다.
4. 폼과 모달은 마지막에. 기존 JS 바인딩이 많은 곳이라 클래스만 바꾸고 동작은 그대로 둔다.

## 라이선스

MIT — `LICENSE`. 폰트(Manrope · Noto Sans KR · JetBrains Mono)와 아이콘(Phosphor)은 각자의 라이선스를 따르며 저장소에 포함돼 있지 않습니다.
