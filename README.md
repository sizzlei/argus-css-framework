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
| [리포트](https://sizzlei.github.io/argus-css-framework/examples/report.html) | A4 제출 문서 미리 보기·인쇄(`ag-paper`) |
| [조합 매트릭스](https://sizzlei.github.io/argus-css-framework/examples/matrix.html) | 모든 변형 × 조합 (회귀 확인용 — 어긋난 셀을 찾는 페이지) |

로컬에서는 저장소를 받아 `examples/index.html` 을 그냥 열면 된다 (빌드 불필요). 페이지 하단 왼쪽 네비로 이동, 우상단 버튼으로 다크/라이트 전환.

```
dist/argus.min.css              ← 가장 단순한 선택: 이것 하나만 <link> (181KB, gzip 31KB)
  — 또는 골라 쓰기 —
dist/argus.core.min.css         ← 토큰·베이스·레이아웃·컴포넌트·스킨·유틸 (96KB, gzip 17KB). 최소 세트
dist/argus.patterns.min.css     ← 인증·로그·Slack·배너·알림·승인·⌘K·트리·태그·스테퍼·인쇄… (73KB, gzip 13KB) — 아래 컴포넌트 목록의 patterns 표
dist/argus.charts.min.css       ← CSS 차트(도넛·바·히트맵·게이지…) + Apex/Chart.js 보정 (12KB, gzip 3KB). 차트 있는 페이지만 — 스파크·인라인 svg 차트·버블은 core
dist/argus.auth-landing.min.css ← 랜딩형 인증 변형 (선택, 2KB)
dist/themes/<color>.min.css     ← 컬러 테마 red / orange / yellow / green / blue / indigo / violet. css 다음에 한 줄 더 <link>
dist/argus.js                   ← 선택. 테마 · 스킨 토글·탭·사이드바·드롭다운·모달(소유권)·토스트·키보드·콤보박스·차트 호버·선택 알약 미끄러짐 (15KB, gzip 5KB)
dist/argus.charts.js            ← 선택. ApexCharts / Chart.js 에 토큰 주입 (AG.charts.apex / chartjsDefaults / sequential / heatRanges / engine / bubbles, 9KB)
dist/VERSION
css/ js/                        ← 소스. 읽을 땐 여기. js/modules/ 가 argus.js 로 합쳐진다 (사람이 읽는 합본이 필요하면 `sh build.sh --readable`)
fonts/                          ← 폰트 self-host 키트 (fetch-fonts.sh → woff2 + fonts.css)
index.html                      ← GitHub Pages 진입점 (examples/ 로 리다이렉트)
examples/                       ← 예시 사이트 (= 라이브 데모 소스). components.html 이 전체 카탈로그
                                   index(대시보드) / resources(목록) / detail(상세) / login(인증) / layouts(6모드 + 컬러 전환) / report(A4 인쇄 문서) / matrix(변형 조합 매트릭스, tools/gen_matrix.py 가 생성)
templates/                      ← Go html/template + Alpine 적용 예시 (인증 레이아웃, 3단계 로그인)
tools/                          ← check.py(값 단언 회귀 234항목 + axe 접근성 게이트 + 키보드·모션 상한 + 클래스 커버리지) · shots.py(스크린샷) · gen_matrix.py(매트릭스 생성)
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
- **엔진은 고유색**: 세 번째 색 축 — `data-engine="mysql"` 을 달면 그 안의 `--engine` 변형(`.ag-badge--engine` `.ag-dot--engine` `.ag-card--engine-stripe` …)이 MySQL 주황 · PostgreSQL 파랑 · Oracle 와인 · DocumentDB 초록 · MS-SQL 빨강으로. 카드는 제목·테두리·띠·윗선·옅은 배경·그림자·단색 중 고릅니다. 엔진색은 "어느 엔진인가" 만 말합니다 — 상태(good/warn/crit)로 읽지 않도록 범례엔 늘 이름을 같이.
- **상태색은 예약색**: `good / warn / crit / info` 는 상태 표시 전용. 엔진·태그·팀 같은 **범주**는 `--cat1~4`(배지·태그·점), 차트 시리즈는 `--ag-chart-1~4` — 같은 네 가지 색이라 화면 어디서든 범주 1 은 같은 색입니다 (두 테마 모두 색각이상 분리도 검증 완료). 다섯 번째 범주는 만들지 않습니다 → "기타" 는 중립 회색 `--ag-chart-other` (`AG.charts.palette(5)` 의 마지막, `.ag-dot--other`).
- **변형 선언 순서 = 우선순위**: 한 블록 안에서 모양(`--sm` `--count` `--stack`) → 톤(상태·액센트·범주) → 조합(`--solid`) 순으로 선언해 `:not()` 체인 없이 어떤 조합이든 예측 가능하게. 모양 변형은 색을 건드리지 않습니다. 폴백 규칙(컨테이너 없는 카드·버튼 간격)은 `:where()` 로 특이도 0.
- **JS 는 자기가 연 것만 닫는다**: `argus.js` 의 바깥 클릭·ESC 는 `data-ag-open` 으로 연 오버레이에만 — Alpine/Vue 가 제어하는 것은 건드리지 않습니다 (아래 JS 헬퍼).
- **움직임은 드물게, 색은 적게**: 늘 보이는 상태 점은 움직이지 않습니다(`.ag-dot--pulse` 는 3번 깜빡이고 멈춤, 진행 중인 장애 하나에만 `.is-live`). 카드 아이콘 타일의 상태색은 화면당 2개 이하, 나머지는 기본·액센트·범주색. 지속시간은 `--ag-dur`(160) `--ag-dur-move`(260) `--ag-dur-slow`(400) 셋뿐. 글자는 11px 아래로 내려가지 않습니다.
- **접근성은 토큰이 책임진다**: 모든 글자/배경 쌍이 WCAG AA(4.5:1, 11px 메타 포함) — 채움색과 글자색을 분리한 토큰(`--ag-accent` / `--ag-accent-text`, 상태 `*` / `*-text`, `--ag-accent-2-text`, 범주색 위 `--ag-text-on-*`)만 쓰면 서비스가 대비를 계산할 일이 없습니다. 본문 안 링크는 밑줄, 상태는 색 + 점/아이콘/텍스트, 키보드 포커스 링은 어떤 배경에서도 같은 두께. `tools/check.py` 가 axe-core 로 예시 전 페이지 × 두 테마에서 serious/critical 0 을 단언합니다.
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
| `.ag-app--dual` | dual | 사이드바 + `.ag-pane` 목록 + 상세 (본문 상한 없음) |
| + `.ag-app--fluid` | 폭 옵션 | 본문 `.ag-main` 의 1600px 상한(`--ag-content-max`) 해제 — 넓은 모니터에서 전면을 쓰는 대시보드·모니터링·감사 화면. top/sidebar/rail/tabs 와 조합. 서비스 전체는 `:root { --ag-content-max: none }` |

사용자 프로필은 모드와 무관하게 상단 바 우측 `.ag-user` 드롭다운에 둡니다.

## 스킨 (`data-skin`)

색 테마 · 레이아웃 모드와 따로 움직이는 세 번째 축입니다. 마크업은 그대로 두고 `<html>` 속성 하나로 재질을 바꿉니다. 예시 페이지 하단 네비의 **Glass** 버튼으로 모든 페이지를 바꿔 볼 수 있습니다.

```html
<html lang="ko" data-skin="glass">   <!-- Liquid Glass. 빼면 기본(불투명) -->
```

| 값 | 재질 | 적용 범위 |
|---|---|---|
| (없음) | 불투명 표면 (기본) | — |
| `glass` | Liquid Glass — 반투명 바탕 + `blur(24px) saturate(180%)` + 위쪽 밝은 광택 + 하이라이트 테두리, 뒤에 명도를 고정한 테마색 메시(1.19) | 1.15 크롬(상단 바 · 사이드바 · 레일 · 탭 모드 2단 바 · 레일 하단 탭) · 1.16 오버레이(`ag-menu` · `ag-notif` · `ag-combobox__list` · `ag-popover` · `ag-cmdk` · `ag-modal__panel` · `ag-drawer` · `ag-toast` · `ag-wizard__bar`). 1.17 카드 · 패널(`ag-card` 기본 · `--elevated` · `--interactive` · 엔진 변형, `ag-pane`, `ag-sidebar__panel`) · 1.18 알약 컨트롤(`ag-nav` · `ag-segmented` 트랙과 유리 선택 알약, `ag-tabs` 활성 판, `ag-user` hover). 불투명 그대로: 고정 선택 바(`ag-bulkbar--sticky`), 단색 톤 카드(`--accent` `--accent2` `--inverse` `--cat1~4` `--engine-solid`), `ag-card--accent-soft`, `ag-sidebar__panel--accent` |

- **켜고 끄기:** 서비스가 `data-skin` 으로 기본값을 정하고, 사용자에게 고르게 하려면 `<button data-ag-skin-toggle aria-pressed="false">` 를 둡니다(argus.js, `localStorage('ag-skin')` 에 기억, 저장값이 없으면 서비스 기본값). 첫 페인트 깜빡임 방지 스크립트는 아래 JS 헬퍼 절.
- **메시(1.19):** 바닥(`--ag-glass-wash` — 다크는 짙은 테마색, 라이트는 없음) 위에 세 색 덩어리(`--ag-glass-tint-1..3`)를 얹습니다. 색은 명도를 고정한 상대 색(`oklch(from var(--ag-brand-from) .26 min(c, .13) h)` — 다크는 명도 상한, 라이트는 하한)이라 테마는 색상만 바꾸고, 메시 위에 바로 놓인 글자(페이지 제목 · 브레드크럼 · 갱신 시각) 대비는 어느 테마에서도 그대로입니다. 상대 색을 모르는 브라우저(Chrome < 119 · Safari < 16.4 · Firefox < 128)는 메시 없이 평평한 바탕입니다(유리 표면은 그대로).
- **배경 바꾸기:** 메시는 `--ag-glass-backdrop` 한 토큰입니다. 서비스 이미지로 바꾸려면 `:root { --ag-glass-backdrop: url(/static/bg.jpg) center / cover; }` — 이때 위에 바로 놓인 글자 대비는 서비스가 책임집니다.
- **대비:** 유리 바탕 두께는 셋 — 고정 배경 위(`--ag-glass-bg`, 사이드바), 본문이 밑으로 지나가거나 막 위에 뜨는 곳(`--ag-glass-bg-thick`, 상단 바 · 오버레이), 카드(`--ag-glass-bg-card`, 1.19). 유리 안 입력칸은 `--ag-glass-field`(다크는 어둡게 · 라이트는 희게 — placeholder 대비가 오르는 쪽). 7색 × 다크 · 라이트에서 메타 글자(`--ag-text-3`)까지 4.5:1 을 check.py 가 단언합니다 — 메시 위 맨 글자는 실제 화면 픽셀로도(1.19). 알파를 낮추고 싶으면 컴포넌트가 아니라 토큰에서, 단언을 통과하는 범위로.
- **블러 호스트 안에 fixed 오버레이를 두지 않습니다.** `backdrop-filter` 가 걸린 요소(사이드바 · 메뉴 · 모달 패널 · 드로어 · 토스트)는 안쪽 `position: fixed` 의 기준 상자가 되어, 그 안에 둔 모달 · 드로어 · 토스트가 호스트 크기로 갇힙니다. 오버레이는 body 직계나 `<dialog>` 로 둡니다(check.py 가 예시에서 단언).
- **카드는 블러 없이 반투명입니다.** 블러를 걸면 카드마다 쌓임 맥락이 생겨 카드 안 드롭다운이 다음 카드 밑에 가려집니다(실측). 카드는 고정된 부드러운 메시 위에만 놓여 블러가 보이지도 않습니다. 그래서 `--ag-glass-backdrop` 을 사진으로 바꿀 때는 카드 뒤가 흐려지지 않으니 미리 흐린 이미지를 씁니다. 카드 바탕은 `--ag-glass-bg-card`(다크 70 · 라이트 72%, 1.19)라 메시 색이 은은하게 비치고, 안쪽 표 · 고정 열 · 입력칸은 불투명 그대로입니다.
- **선택 알약이 미끄러집니다(1.18).** 네비 · 세그먼트 · 탭의 선택이 바뀌면 유리 알약(탭은 판 + 밑줄)이 새 항목으로 스프링 곡선(`--ag-ease-spring`, 1.0 을 넘는 오버슈트)을 타고 미끄러지고, 누르면 항목이(활성이면 알약도) 살짝 눌렸다 튀어 돌아옵니다. 위치 계산은 argus.js(`15-glide`)가 자동으로 합니다 — 클릭 · 방향키 · Alpine 의 class 변경 모두 따라오고, 따로 붙일 속성은 없습니다. argus.js 가 없으면 선택한 항목이 제자리에서 알약을 받습니다. OS 의 동작 줄이기 설정이면 기존 전역 규칙(base.css)대로 즉시 바뀝니다. 탭 모드 2단 바 네비는 원래 모양(액센트 소프트 · 밑줄 변형) 그대로입니다.
- **사이드바 안 메뉴는 사이드바 밖을 흐리지 못합니다.** 블러가 걸린 요소 안쪽의 블러는 그 요소 밖을 못 봅니다(backdrop root). 그래서 메뉴를 품는 상단 바 · 오버레이형 모달 막은 블러를 `::before` 에 두었고, 사이드바는 자체 스크롤 상자라 요소 블러 그대로입니다.
- **투명도 줄이기:** OS 설정(`prefers-reduced-transparency: reduce`)이면 유리 스킨이어도 불투명 · 블러 없음 · 메시 없음으로 떨어집니다.
- 인쇄 문서(`.ag-paper-desk`)와 인쇄 때는 메시를 깔지 않습니다.

## 기존 어드민에 적용할 때 (Claude Code)

`docs/renewal-prompt.md` 에 ① 앱 저장소 `CLAUDE.md` 에 붙일 규칙 조각, ② 리뉴얼 착수 프롬프트, ③ Tailwind/Bootstrap → `ag-` 매핑표가 있습니다.

## 서비스에 적용하며 생기는 변경 (피드백 루프)

실제 서비스를 이 프레임워크로 갈아입히다 보면 "변형이 없다", "스크립트가 깨진다" 같은 건이 계속 나옵니다. 처리 원칙:

1. **서비스 저장소에서 즉흥 CSS 를 만들지 않는다.** 없는 것은 그대로 두고(읽는 데 지장 없는 수준이면 기본 스타일로), 프레임워크에 "무엇이 어디서 몇 곳에 필요한지" 를 보고한다.
2. 프레임워크에서 고친다 — CSS(`css/`) + **카탈로그 예시**(`examples/src/components.html`) + **README 컴포넌트 목록**(그 CSS 파일이 들어가는 번들의 표) + `CHANGELOG.md` 네 군데를 한 커밋에. 변형을 추가했으면 `tools/gen_matrix.py` 목록에도, 서비스에서 들어온 버그면 `tools/check.py` 에 단언 하나. 예시 없이 CSS 만 추가하지 않는다 (예시가 곧 회귀 테스트이자 문서).
3. `sh build.sh && python3 tools/gen_matrix.py && python3 build_examples.py && python3 tools/check.py` 통과 후 1440/400px 다크·라이트 확인, 커밋.
4. 서비스는 `dist/` 를 다시 복사한다 (위 "앱에 배포하기").

지금까지 이 루프로 들어온 것 — 1.0~1.1 의 예(1.2 이후 argus-server 보고 ⑫②⑦⑧③ · ⓐ⑰⑪⑬⑭ · 엔진색 · 인쇄 문서 · 구성도 · 상태 신호등까지 전부 `CHANGELOG.md`):

- 1.0.0: `.ag-toast--warn/--info`, `.ag-provider__label`, `fonts/fetch-fonts.sh` 블록 파싱 두 건, 모바일 상단 바 넘침, `.ag-qr` 예시 누락
- 1.1.0: `.ag-badge--count` 가 톤을 덮던 것, `.ag-toast-stack--static` z-index, `a/button.ag-card` 의 display·`align-items`, `.ag-tile--stack`, `.ag-form-grid--2/--3/--4` + `--span2/--span3`, `.ag-input-group--end` 패딩, `.ag-text-left` `.ag-scroll-y`, 범주 아바타, 레이아웃 간격 토큰과 `.ag-page`, `--tabs` 초광폭, `.ag-glow` 복원, argus.js 오버레이 소유권·`<head>` 로드·Phosphor 아이콘, 히트맵 순차 램프 `--ag-seq-1..5` / `AG.charts.sequential`, `.ag-list__item.is-active`

## 토큰 요약

| 그룹 | 변수 | 비고 |
|---|---|---|
| 표면 | `--ag-bg` `--ag-surface` `--ag-surface-2` `--ag-surface-3` `--ag-inverse` | 바닥 → 카드 → 카드 안 타일 → 강조. `--ag-shadow-scroll` 은 가로 스크롤 가장자리. `--ag-surface-sheen`(다크 카드 광택, 라이트 none) · `--ag-bg-glow`(페이지 상단 액센트 글로우, `none` 으로 끔) |
| 유리 (1.15 ~ 1.19) | `--ag-glass-bg` `--ag-glass-bg-thick` `--ag-glass-bg-card` `--ag-glass-filter` `--ag-glass-sheen` `--ag-glass-border` `--ag-glass-edge` `--ag-glass-fill` `--ag-glass-field` `--ag-glass-pill` `--ag-glass-pill-shadow` `--ag-glass-tint-1..3` `--ag-glass-wash` `--ag-glass-backdrop` · `--ag-ease-spring` | `data-skin="glass"` 일 때만 쓰임. 바탕(고정 배경 위 / 본문 · 막 위 두꺼운 / 카드 1.19) · 블러+채도 · 위쪽 광택 · 테두리 · 하이라이트 선 · 유리 안 hover(알약 트랙) · 유리 안 입력칸(1.16) · 선택 알약 + 그림자(1.18) · 메시 색 3(명도 고정 상대 색) · 메시 바닥(1.19) · 메시. 스프링 곡선은 알약 미끄러짐 · 누름 전용. 투명도 줄이기면 불투명 |
| 포커스 | `--ag-ring`(입력, 글로우) `--ag-ring-focus`(키보드, 2px 틈 + 실선) · 입력 포커스는 `--ag-field-focus-bg` · `--ag-field-focus-border` · `--ag-field-ring` 을 먼저 읽음(없으면 표면 · 액센트 글자 · `--ag-ring`, 1.9.2) | 어떤 배경 위에서도 같은 두께. 단색 카드는 입력 포커스 셋을 재정의(바탕 그대로 + 글자색 테두리 · 링) |
| 잉크 | `--ag-text` `--ag-text-2` `--ag-text-3` | 본문 / 보조 / 메타 |
| 액센트 | `--ag-accent`(채움) `--ag-accent-text`(글자) — 테마가 공급 · `--ag-accent-2` `--ag-accent-2-text` | 채움 위 글자는 `--ag-text-on-accent`. 글자를 액센트로 칠할 땐 항상 `-text`(다크에서 채움색은 표면 위 대비가 모자람). `*-soft` 는 투명 배경용. accent-2 는 브랜드 그라데이션·범주 2번용 — 버튼·칩·배지 같은 UI 요소에는 쓰지 않는다 (주요 동작이 둘이면 둘 다 아니다) |
| 상태 | `--ag-good` `--ag-warn` `--ag-crit` `--ag-info` | `*-soft`(배경) `*-text`(단독 글자) `*-solid` + `--ag-text-on-*`(solid 배지·칩) 동반 |
| 차트 | `--ag-chart-1..4` `--ag-chart-other` `--ag-chart-hatch` `--ag-chart-grid` `--ag-text-on-chart` `--ag-treemap-base` | 범주색 고정 순서. 범주색을 배경으로 쓰는 버블·트리맵 글자는 `--ag-text-on-chart`(solid 배지·칩은 `--ag-text-on-cat-N`). `other` 는 "기타" 조각용 중립 회색 — 상위 4 + 기타 = 5조각이 1번 색을 반복하지 않음 |
| 순차 램프 | `--ag-seq-1..5` | 히트맵·밀도용 단일 색 5단계 (`--ag-chart-1` → `--ag-surface-2`). `.ag-heat--1..5` 와 `AG.charts.sequential(5)` 가 같은 값 |
| 엔진 | `--ag-engine-{mysql,postgres,oracle,documentdb,mssql,other}` (`data-engine` 은 부분 일치 — `aurora-mysql` `oracle-ee` `sqlserver-se` `docdb` 그대로, 단독 별칭 `pg` `ora` `doc`, 모르는 값은 other; JS `AG.charts.engineKey()`) + `*-text` `*-soft` `*-solid` `--ag-text-on-engine-*` | `data-engine` 훅이 `--ag-engine*` 로 풀어줌. 차트 순서 documentdb → mysql → postgres → oracle → mssql (인접쌍 CVD 검증) |
| 범주 | `--ag-cat-1..4` `--ag-cat-other` + `*-soft` `*-text` | 배지·태그·점에서 종류 구분. 차트 범주색과 같은 네 가지 + 기타(`.ag-badge--other` `.ag-dot--other` `.ag-avatar--other`), 라이트는 글자색을 한 단계 깊게 |
| 간격 | `--ag-space-1..12` | 4px 기준 |
| 본문 폭 | `--ag-content-max`(1600px) `--ag-gutter`(clamp 16–40px) | `.ag-main` 상한과 좌우 여백. 전면은 `.ag-app--fluid` 또는 토큰 `none` |
| 레이아웃 간격 | `--ag-gap-grid`(24) `--ag-gap-main`(32) `--ag-gap-section`(20) | 카드 사이 · 본문 블록 사이 · 섹션 헤드↔본문. 서비스가 `:root` 에서 한 번에 조정 |
| 라운드 | `--ag-radius-sm/md/lg/xl/btn/pill` | 6 / 10 / 12 / 16 / 10(버튼) / 999 — 알약은 칩·배지·세그먼트·네비만 |
| 컨트롤 높이 | `--ag-control-h/-sm/-lg` | 36 / 30 / 44 (터치 44/36/48, compact 32/26). 버튼·입력·셀렉트·사용자 메뉴가 참조 |
| 타이포 | `--ag-text-xs..4xl`(11/13/14/17/20/28/38/40) `--ag-text-hero`(52) `--ag-font-sans` `--ag-font-mono` `--ag-font-brand` `--ag-font-brand-tracking` | 본문 14px · h1 28/600 · 카드 스탯 40 · 히어로 52 · 로고 글자(상단 바 브랜드 · `.ag-auth__name` · 모바일 머리)는 기본 본문 글꼴 / -0.02em, 서비스가 `:root` 에서 자기 글꼴로 덮는다 |
| 밀도 | `--ag-cell-y`(11) `--ag-cell-x`(16) | 테이블 셀 패딩 → 행 ≈44px. `--dense` 8/12, `data-density=compact` 7/12 |

## 컴포넌트 목록

어느 **번들**에 들어 있는지로 나눴습니다. `argus.min.css` 하나를 걸면 전부 들어 있고, 골라 쓸 때(`core` + `patterns` + `charts`)는 이 구분이 곧 "어떤 파일을 걸어야 하는가" 입니다 — 예를 들어 `ag-tag` · `ag-stepper` · `ag-spinner` 는 patterns 에만 있고, `ag-spark` · `ag-chart` · `ag-bubble` 은 차트처럼 보여도 core 에 있습니다. 표기는 `__x` 요소 · `--x` 변형 · `is-x` 상태. 모양은 `examples/components.html`(카탈로그), 모든 변형 × 조합은 `examples/matrix.html` 에서 확인하세요. `tools/check.py` 가 css/ 의 모든 클래스가 예시 어딘가에 나오는지 확인합니다.

### core — 셸 · 레이아웃 (`css/layout.css`)

| 블록 | 요소 · 변형 | 메모 |
|---|---|---|
| `ag-app` | `--sidebar` `--rail` `--tabs` `--focus` (`--focus-wide`) `--dual` (`--dual-nosidebar`) · `--fluid` | 레이아웃 모드(위 표). `--fluid` 는 본문 1600px 상한 해제 |
| `ag-topbar` | `__brand` `__brand-text` `__center` `__search` `__actions` `__back` · `__row` (`--main` `--nav` `--underline`) | `__row` 두 줄은 `--tabs` 모드 |
| `ag-nav` | `__item` (`aria-current="page"`) · `--compact` | 상단 바 캡슐 네비 |
| `ag-sidebar` | `__head` `__toggle` `__hamburger` · `__nav` · `__group` (`--sub`) `__group-toggle` `__label` `__item` (`--parent`) `__caret` `__node` `__sub` · `__panel` (`--accent` `--warn`) `__panel__head` `__status` · `__footer` · `--bottom-tabs` | `__nav` 는 남은 높이를 채우고 여기만 스크롤, `__panel` 은 바닥 패널(상태·용량·환경·공지, 1~2개), `__node`/`__sub` 는 2단계 메뉴. `is-collapsed` 접힘 · `is-open` 모바일. 배경 막 `ag-sidebar-backdrop` 은 patterns |
| `ag-main` `ag-page` | `ag-page--tight` | `ag-page` 는 `x-data` 같은 본문 래퍼 — 블록 간격(`--ag-gap-main`)을 이어받음, 클래스 없는 div 는 자동. `--tight` 는 카드 간격(`--ag-gap-grid`) |
| `ag-page-header` | `__title` `__actions` | |
| `ag-section` | `__head` | |
| `ag-grid` + `ag-col-2…9` `ag-col-12` | `--tight`(12px) `--auto` | 12열, 1200 · 720px 에서 접힘 |
| `ag-stack` `ag-cluster` `ag-row` `ag-spacer` | `ag-stack--sm/--lg` · `ag-cluster--between` | 세로 쌓기 · 가로 묶음 |
| `ag-breadcrumb` | `__sep` | |
| `ag-banners` | | 배너(`ag-banner`, patterns) 묶음. 사이드바 셸의 직계(상단 바 다음)에 두면 상단 바와 본문 사이에 한 줄이 생기고, 비면 높이 0 (1.14) |
| `ag-pane` · `ag-pane-item` | `__head` `__body` `__foot` · `__top` `__title` `__snippet` `__tags` | dual 모드의 목록 패널. 항목 `is-active` |
| `ag-mode-switch` | | 예시 데모의 모드 전환 크롬 (서비스에서는 쓰지 않음) |

### core — 컴포넌트 (`css/components.css`, 타이포 기본은 `base.css`)

| 블록 | 요소 · 변형 | 메모 |
|---|---|---|
| `ag-btn` | `--primary` `--outline` `--ghost` `--inverse` `--danger` `--accent2` · `--sm` `--lg` `--icon` `--square` `--block` `--pill` · 조합 `--ghost.--danger` `--outline.--danger` `--outline.--primary` | 10px 둥근 사각. `--pill` 은 예전 알약(랜딩·인증만). ghost × danger 는 평소 중립 → hover crit (행 삭제 버튼) |
| `ag-btn-group` | | |
| `ag-segmented` | `__item` · `--sm` | 3~4개 선택지용, `role="radiogroup"`. 많으면 `ag-tabs` · `ag-nav` |
| `ag-tabs` | `__item` | `data-ag-tabs` 로 패널 전환 |
| `ag-chip` | `__label` · `--sm` · `--accent` `--accent2` `--inverse` `--outline` `--hatch` · `--good` `--warn` `--crit` `--info` · `--cat1~4` · `--engine` · `--solid` | `button.ag-chip` 필터: `is-active` / `aria-pressed` 가 범주 단색 배경 |
| `ag-badge` | `--sm` `--lg` `--count` `--plain` · `--good` `--warn` `--crit` `--info` `--accent` `--accent2` `--inverse` · `--cat1~4` `--other` · `--engine` · `--solid` | 모양 변형(`--count` `--plain`)은 어떤 톤과도 조합. 종류 표시는 `--plain`(점 + 글자) — 한 행에 알약은 상태 하나 |
| `ag-dot` | `--good` `--warn` `--crit` `--info` `--accent` `--accent2` · `--cat1~4` (= `--c1~4`) `--other` `--engine` · `--pulse` | `--pulse` 는 3번 깜빡이고 멈춤, 무한은 `.is-live` 하나(화면당 1) |
| `ag-avatar` | `--xs` `--sm` `--lg` `--ring` · `--good` `--warn` `--crit` `--info` `--accent2` `--cat1~4` `--other` `--neutral` `--engine` | 묶음 `ag-avatar-group` |
| `ag-person` | `__name` `__meta` | 아바타 + 이름 |
| `ag-delta` | `--up` `--down` `--flat` · `--inline` | 증감 표시 |
| `ag-icon` | `--sm` `--lg` | svg 스프라이트. Phosphor `<i class="ph-…">` 도 같은 대우(아래 JS 헬퍼 참고) |
| `ag-card` | `__head` `__heading` `__icon` `__title` `__subtitle` `__body` `__foot` · `--sm` `--flush` `--elevated` `--interactive` · `--accent` `--accent-soft` `--accent2` `--inverse` `--cat1~4` · `--engine-title` `-border` `-stripe` `-top` `-tint` `-glow` `-solid` | `__icon` 톤 `--accent` `--good` `--warn` `--crit` `--info` `--1~4` `--engine`(상태색은 화면당 2개 이하). 단색 카드(`--accent` `--accent2` `--inverse` `--cat1~4` `--engine-solid`)는 안쪽 글자·테두리·서브표면·입력 포커스 토큰을 재정의. `a.ag-card` / `button.ag-card` 정렬 자동, `is-selected`. 엔진 톤은 `data-engine` 과 함께, 권장 stripe + title |
| `ag-tile` | `__label` · `--stack` `--inverse` | 카드 안 라벨↔값 타일, `--stack` 세로(메트릭 타일) |
| `ag-stat` | `__value` `__label` `__top` · `--sm`(28) `--hero`(52, 화면 한 곳) | 기본 40px. KPI 묶음 `ag-stat-row`(모바일 3열) |
| `ag-list` | `__item` (`--engine` `--meter`) `__label` `__trend` · `--divided` | `a/button.ag-list__item` + `is-active`(선택) · `is-current`(지금 보는 항목) · `disabled` |
| `ag-quick-actions` · `ag-quick-action` | `__icon` (`--1~4`) `__body` `__title` `__meta` `__end` | 빠른 작업 타일 |
| `ag-kv` | `--stack` | `<dl>` 키·값 |
| `ag-timeline` | `__item` `__time` `__title` `__head` `__meta` · `--compact` | |
| `ag-legend` | `__item` | 차트 범례(점 + 이름) |
| `ag-meter-row` · `ag-meter-chips` | `__head` `__keep` · `--compact` | 라벨 + 미터. `--compact` 는 한 줄(표 셀 기본) |
| `ag-progress` | `__bar` (`--engine`) · `--sm` `--lg` `--stacked` · `--good` `--warn` `--crit` `--accent2` | |
| `ag-table-wrap` · `ag-table` | `--dense` `--striped` `--clickable` `--sticky-col` `--sticky-end` `--loading` · `__expander` | wrap 은 가로 스크롤 가장자리 그림자. `--clickable` 행 전체 링크, `--sticky-end` 끝 열 고정(바로 아래 행만), `--loading` 헤더 유지 + 행 shimmer. 행 `is-clickable` `is-selected` `is-muted` `is-crit` `is-warn` |
| 표 셀 | `ag-th--num` `ag-th--actions` · `ag-td--num` `--actions` `--engine` `--truncate` `--query` `--wrap` · `ag-tr--expand` · `ag-sort` | `--truncate` 상한 `--ag-td-max`(240px, 셀 안 `<span title>`), `--query` 블록 코드(`--ag-query-w`), `ag-tr--expand` 는 `data-ag-expand` 로 펼침 |
| `ag-table-foot` · `ag-pagination` | `__item` | `aria-current="page"` |
| `ag-field` | `__error` · `--span2` `--span3` `--full` | `is-invalid` + `__error`(아이콘 + 문구, 색 단독 금지) |
| `ag-label` `ag-req` `ag-hint` | | 라벨 · 필수 표시 · 도움말 |
| `ag-input` | `--sm` `--lg` `--pill` `--mono` `--picker` | `[type=range]` 포함. `--picker` 는 클릭하면 선택기를 여는 읽기 전용 입력 |
| `ag-select` | `--sm` `--pill` `--inline` `--list` | `--list` 는 열린 리스트 박스(`size=N`) |
| `ag-textarea` `ag-check` `ag-switch` | | |
| `ag-input-group` | `__end` · `--end` | 앞 아이콘 · 뒤 버튼, 둘 다 조합 가능 |
| `ag-form-grid` · `ag-form-actions` | `--2` `--3` `--4` | 기본 auto-fit, `--full` 섞을 땐 열 고정 |
| `ag-alert` | `__title` · `--good` `--warn` `--crit` `--info` | |
| `ag-insight` | `__icon` | 한 줄 해석 |
| `ag-toast` · `ag-toast-stack` | `--good` `--warn` `--crit` `--info` · `--static` | `AG.toast()` |
| `ag-empty` | `__icon` `__title` `__actions` · `--error` `--sm` | 빈 상태 · 불러오기 실패 |
| `ag-skeleton` | | 로딩 자리. 표는 `ag-table--loading`, 행 묶음은 patterns 의 `ag-skeleton-rows` |
| `ag-dropdown` · `ag-menu` | `__item` `__label` `__sep` `__user` · `--left` `--wide` | `data-ag-dropdown` |
| `ag-modal` | `__panel` `__head` `__foot` | `<dialog>` |
| `ag-modal-overlay` | `--top` `--lg` `--xl` | `x-show` 형 모달 |
| `ag-drawer` · `ag-drawer-backdrop` | `__head` `__body` `__foot` `__toolbar` · `--lg`(720px) | 머리는 `__head` 또는 `ag-modal__head`(같은 모양). `__body` 만 스크롤 · `__foot` 바닥 고정 · `__toolbar` 본문 위 고정 도구줄. 배경 막은 argus.js 로 열면 자동(`data-ag-modeless` 로 끔), Alpine 은 직접 두고 입력 폼이면 `data-ag-static` |
| `[data-tip]` | | CSS 툴팁 |
| `ag-spark` | `__line` `__area` `__ref` · `--sm` `--lg` · `--1~4` `--good` `--warn` `--crit` `--info` `--engine` | 스파크라인. `__ref` 기준선, 표 셀 안 96px(`--ag-spark-w`) |
| `ag-chart` | `--h-sm` `--h-md` `--h-lg` · `__line` `__area` `__bar` (`--1~4` `--engine`) `__marker` (`--1` `--2` `--engine`) `__grid` `__axis` `__cursor` `__tooltip` `__empty` | 인라인 svg 차트 틀. `data-ag-chart` 로 호버 툴팁 |
| `ag-bubbles` · `ag-bubble` | `--1~3` `--hatch` `--engine` | 지름 `--r = √비율` → 면적이 값에 비례(`AG.charts.bubbles()`), 상한 `--ag-bubble-max` |
| 엔진 훅 | `data-engine="…"` 또는 `ag-engine-{mysql,postgres,oracle,documentdb,mssql,other}` | 안의 `--engine` 변형이 엔진색으로. RDS Engine 값 그대로(부분 일치·대소문자 무시), 모르는 값은 other. 글자는 `ag-text-engine` |
| 글자 | `ag-h-display` `ag-mono` `ag-num` `ag-truncate` | `ag-h-display` 는 랜딩·상태 화면 제목(38/500)만. h4~h6 은 쓰지 않음 |

### charts — CSS 전용 차트 (`css/charts.css`, `argus.charts.min.css`)

| 블록 | 요소 · 변형 | 메모 |
|---|---|---|
| `ag-donut` · `ag-donut-wrap` · `ag-donut-legend` | `__center` · `--sm` `--lg` `--thin` · 범례 `__item` | `--ag-donut` 에 conic 구간 |
| `ag-bars` | `__row` `__label` `__track` `__seg` `__value` · `--thin` `--thick` | 조각 `__seg--1~4` `--other`(기타) `--accent` `--muted` `--hatch` `--engine`, 쌓으면 stacked |
| `ag-cols` | `__col` `__group` `__bar` `__label` | 막대 `__bar--1~4` `--other` `--muted` `--engine`, 높이는 `--v` / `--ag-cols-max` |
| `ag-heatmap` · `ag-heat` · `ag-heat-scale` | `ag-heatmap--crit` · `ag-heat--1…5` `--empty` | 연속은 `--l`, 단계는 `--1…5` = `--ag-seq-1..5` = `AG.charts.sequential(5)` |
| `ag-gauge` | `--sm` · `--good` `--warn` `--crit` | `--p` |
| `ag-ring` | `--good` `--warn` `--crit` | 작은 진행 고리 |
| `ag-stat-card` | `__head` `__icon` `__foot` | 아이콘 톤 `--good` `--warn` `--crit` `--info` `--accent2` `--engine`. 스파크는 core 의 `ag-spark` |
| `ag-treemap` | `__cell` (`--2~4`) | |
| 라이브러리 보정 | `.ag-chart .apexcharts-*` · Chart.js | 색·폰트 주입은 `argus.charts.js` |

### patterns — 반복되는 화면 조각 (`css/patterns.css`, `argus.patterns.min.css`)

| 분류 | 블록 (요소 · 변형) |
|---|---|
| 셸 부속 | `ag-user` (`__text` `__name` `__meta`, `--compact`) 상단 바 사용자 메뉴 · `ag-brand-mark` · `ag-sidebar-backdrop` · `ag-glow` (`.ag-app` 배경 글로우, 선택) · `ag-banner` (`__text` `__close`, `--good` `--warn` `--crit` `--info` `--accent` `--readonly` `--sticky`) · `ag-notif-btn` (`__count` `__count--warn` `__dot`, 상태 신호등 `--good` `--warn` `--crit`) · `ag-notif` (`__head` `__group` `__list` `__item` `__icon--good/--warn/--crit/--info` `__body` `__title` `__meta` `__foot` `__empty`, 항목 `is-unread`) · `ag-cmdk` (`__input` `__list` `__group` `__item` `__label` `__hint` `__foot` `__empty`) ⌘K |
| 인증 | `ag-auth` (`__panel` `__brand` `__logo-box` `__name` `__version` `__headline` `__desc` `__features` `__feature` `__facts` `__fact` `__tiles` `__tile` `__status` `__status-dot` `__card` `__glass` `__title` `__sub` `__divider` `__email-chip` `__qr` `__qr-icon` `__foot` `__copyright` `__mobile-head` `__mobile-foot`) · `ag-provider` (`__logo` `__label` `__hint`, `--google` `--slack` `--sso` `--compact`) + `ag-provider-list` `ag-provider-row` · `ag-account` (`__logo` `__body` `__name` `__meta`) + `ag-account-list` · `ag-otp` (`__cell`, `--sm`) · `ag-otp-input` · `ag-qr` (`__pending`) · `ag-domain-hint` · `ag-session` (`is-warning`) · `ag-status-screen` (`__icon` `__code`, `--inline`) · `ag-stepper` (`__step` `__dot` `__label` `__desc` `__body`, `--sm` `--vertical`, 단계 `is-done` `is-active`) — 3단계 로그인 전체는 `templates/go-html-template/login.html` |
| 비밀 값 | `ag-secret` · `ag-secret-field` (`__reveal`, `--block`; `.ag-input/.ag-textarea.is-masked` 블러, `data-ag-reveal`) |
| 입력 · 선택 | `ag-daterange` (`__inputs` `__sep` `__presets` `__summary`, `--stack`) · `ag-combobox` (`__control` `__list` `__group` `__option` `__empty`, `--static`) · `ag-tag` (`__key` `__val` `__remove`; 범주 `--cat1~4` `--other` `--engine` 는 키만, `--accent` 와 상태 `--good` `--warn` `--crit` `--info` 는 태그 전체) + `ag-tags` `ag-tag-input` · `ag-dropzone` · `ag-file` (`__icon` `__name` `__meta`) · `ag-td--editable` (`ag-td__value` `ag-td__input`, `is-editing`) |
| 목록 · 표 보조 | `ag-table-toolbar` · `ag-bulkbar` (`--sticky`, 위치 `--ag-sticky-top`) · `ag-skeleton-rows` · `ag-skeleton-card` · `ag-spinner` (`--sm` `--lg`) · `ag-loading-overlay` · `ag-scroll-y` (`--sm` `--md` `--lg`) · `ag-scrollbar-hide` |
| 펼침 · 겹침 | `ag-accordion` (`__item` `__toggle` `__body` `__meta`, `--plain` `--cards`; `<details>` 또는 `__toggle` + `is-open`) · `ag-popover` (`__title`) |
| 운영 화면 | `ag-approval` (`__head` `__who` `__kind` `__what` `__reason` `__meta` `__actions` `__result`, `is-pending` `is-approved` `is-rejected`) + `ag-approval-list` · `ag-wizard` (`__progress` `__body` `__summary` `__bar`) · `ag-health` (`__row` `__name` `__meta`) · `ag-topo` (`__root` `__branches` `__branch` `__leaves` `__node` `__name` `__meta` `__sub`, 노드 `--good` `--warn` `--crit` `--off` `--group`, `is-selected`) 구성도 · `ag-tree` (`__key` `__val--str/--num/--bool/--null` `__count` `__count--arr`, `--card`) JSON 뷰어 |
| 코드 · 로그 | `ag-log` (`__head` `__body` `__body--nowrap` `__line` `__ts` `__lvl` `__cursor`, `--live` `--fill`) · `ag-code` (`--readonly`) · `ag-code-block` (`__lang` `__copy`, `--lang`) · `ag-tok-kw` `-str` `-num` `-fn` `-com` · `ag-editor` · `ag-diff` (`__hunk` `__line`, `is-add` `is-del`) · `ag-compare` (`__col` `__label`) |
| Slack 미리보기 | `ag-slack` — Block Kit 전체(`__message` `__header` `__section` `__fields` `__context` `__actions` `__btn--primary/--danger` `__image-block` `__divider` …, `--static`) |
| 인쇄 | `@media print` · `ag-print-header` · `ag-print-only` · `ag-print-break`(쪽 나눔) · `ag-print-flow`(긴 표 잇기) · `ag-paper` (`__cover` `__title` `__subtitle` `__section` `__heading` `__num` `__grid` `--3` `--4` `__foot`) + `ag-paper-desk` `ag-paper-bar` A4 제출 문서(예시 `examples/report.html`) |
| 밀도 | `data-density="compact"` — 루트 속성 하나로 표·목록 패딩 축소 |

### 선택 번들 — `argus.auth-landing.min.css` (`css/extras/`)

`ag-auth--landing`(그라데이션 브랜드 패널) · `ag-auth__glass--card`(유리 카드만 따로). 표준 `ag-auth` 대신 쓸 때만 core·patterns 다음에 한 줄 더.

### core — 스킨 (`css/skins.css`)

클래스가 아니라 루트 속성 `data-skin="glass"` — 위 "스킨" 절. 값은 `--ag-glass-*` 토큰, 규칙은 `:where(:root[data-skin])` 로 특이도 0.

### core — 유틸리티 (`css/utilities.css`)

컴포넌트 클래스로 못 푸는 예외에만. 레이아웃 `ag-flex` `ag-inline-flex` `ag-col` `ag-wrap` `ag-nowrap` `ag-flex-1` `ag-items-*` `ag-justify-*` `ag-gap-1…8` `ag-min-0` `ag-w-full` `ag-h-full` `ag-relative` · 간격 `ag-m-0` `ag-mt-1…6` `ag-mt-auto` `ag-mb-2/4` `ag-ml-auto` `ag-p-0/4/6` · 글자 `ag-text-xs…2xl` `ag-text-1/2/3` `ag-text-accent` `ag-text-accent2` `ag-text-good/warn/crit/info` `ag-text-left/center/right` `ag-fw-400…700` `ag-upper` `ag-eyebrow` `ag-truncate` · 표면 `ag-bg-surface(-2/-3)` `ag-border(-t/-b)` `ag-radius-md/lg/xl/pill` `ag-shadow-md` · 스크롤 `ag-overflow-auto` `ag-overflow-x` `ag-scroll-y(--sm/--md/--lg)` · 보이기 `ag-hidden` `ag-sr-only` `ag-hide-sm/md/lg` `ag-show-sm` `ag-only-dark` `ag-only-light` · `ag-cursor-pointer`

### 상태 클래스

`is-active`(선택) `is-current`(지금 보는 항목) `is-selected` `is-open` `is-collapsed` `is-invalid` `is-loading` `is-masked` `is-unread` `is-done` `is-editing` `is-live` · 행 `is-clickable` `is-muted` `is-crit` `is-warn` · 비활성은 `disabled` 속성(opacity 가 아니라 색 토큰으로 흐림).

## JS 헬퍼 (선택)

`dist/argus.js` 는 data 속성으로만 동작합니다. **`<body>` 끝에서 로드하거나 `<head>` 에서 `defer` 로** — 1.1 부터는 `<head>` 에 그냥 넣어도 DOM 준비 후 초기화하지만, 클릭 위임은 로드 즉시 걸리므로 위치는 body 끝이 기본입니다. 아이콘은 `<svg class="ag-icon">`(stroke 1.75) 과 Phosphor `<i class="ph-…">`(regular/duotone — bold 는 선이 두꺼워 섞이면 티가 남) 둘 다 같은 대우를 받고, 크기는 16/18/20 세 단계만 씁니다 — 위치(입력칸 선행 아이콘)·색(사이드바·알림·토스트)·크기(로고 박스·드롭존) 규칙이 전부 `:is(.ag-icon, [class*="ph-"])` 라서 `<i>` 에 `ag-icon` 을 붙일 필요가 없고, 접힌 사이드바·rail·dual 에서도 살아남습니다.

| 속성 | 동작 |
|---|---|
| `data-ag-theme-toggle` | 클릭 시 다크 ↔ 라이트, `localStorage('ag-theme')` 에 저장. 버튼 안의 해·달 아이콘은 `.ag-only-dark` / `.ag-only-light` 로 하나만 보이게 (svg 든 Phosphor `<i>` 든) |
| `data-ag-skin-toggle` | 클릭 시 유리 스킨 켬 ↔ 끔(`data-skin="glass"`), `localStorage('ag-skin')` 에 `glass` / `flat` 저장, `aria-pressed` 갱신. 저장값이 없으면 서비스가 `<html>` 에 정한 기본값 그대로 (1.15) |
| (자동) `.ag-nav` · `.ag-segmented` · `.ag-tabs` | 1.18: 활성 항목 위치를 호스트 변수(`--_glide-x/-y/-w/-h`)와 `data-ag-glide` 로 알린다 — 유리 스킨이 그 자리에 미끄러지는 알약을 그린다. 크기 변화 · 글꼴 로드 · 추가된 노드까지 따라감, 서비스가 할 일 없음 |
| `.ag-segmented__item` `.ag-tabs__item` | 형제 중 하나만 `is-active` |
| `data-ag-tabs` + `data-ag-tab="x"` + `data-ag-panel="x"` | 탭 패널 전환 |
| `data-ag-dropdown` | 부모 `.ag-dropdown` 에 `is-open` 토글, 바깥 클릭 시 닫힘 |
| `data-ag-open="id"` / `data-ag-close` | `<dialog class="ag-modal">`, `.ag-modal-overlay`, `.ag-drawer` 열고 닫기. **소유권 원칙:** 바깥 클릭·ESC 는 argus.js 가 `data-ag-open`(또는 ⌘K)으로 연 것만 닫는다 — Alpine `x-show` / Vue `v-show` 가 제어하는 오버레이·드로어·드롭다운은 건드리지 않음. `data-ag-static` 은 바깥 클릭·ESC 차단. 닫기 직전 cancelable `ag:overlay-close`(detail.reason = button/backdrop/escape), 닫힌 뒤 `ag:overlay-closed`, 연 뒤 `ag:overlay-open` 이벤트. 코드에서는 `AG.overlay.open(el)` / `.close(el)` / `.owns(el)` |
| `AG.toast(message, type?, ms?)` | 우하단 토스트. type = good/warn/crit/info, ms=0 이면 수동 닫기 |
| `data-ag-reveal` (`.ag-secret-field` 안) | 같은 필드의 `.ag-input/.ag-textarea` 에 `is-masked` 토글, `aria-pressed` 갱신, `ag:secret-toggle` 이벤트 |
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
AG.charts.palette(5)                          // 범주색 4 + 마지막 "기타" 중립 회색(--ag-chart-other). apex() 는 series 수에 맞춰 자동

// 히트맵: 단일 색 순차 램프. CSS 토큰 --ag-seq-1..5 (= .ag-heat--1..5) 와 같은 색이라 CSS 셀과 Apex 셀이 맞고, 라이트에서 셀이 사라지지 않음
new ApexCharts(el, AG.charts.apex({ chart:{type:'heatmap'}, series })).render();   // ranges 생략 → series 최소~최대 5등분, 셀 경계 --ag-chart-grid
AG.charts.sequential(5)                       // ['#2f2f49', …] 연한→진한 (#hex). sequential(n, '--ag-crit') 처럼 기준색 변경 가능
AG.charts.heatRanges(0, 400)                  // Apex plotOptions.heatmap.colorScale.ranges 직접 지정할 때
```

첫 페인트 깜빡임을 막으려면 `<head>` 에 다음을 넣습니다(테마 · 스킨 저장값).
```html
<script>try{var d=document.documentElement,s=localStorage.getItem('ag-skin');if(localStorage.getItem('ag-theme')==='light')d.setAttribute('data-theme','light');if(s==='glass')d.setAttribute('data-skin','glass');else if(s)d.removeAttribute('data-skin')}catch(e){}</script>
```

## 빌드

```sh
npm i                       # 선택: esbuild + lightningcss-cli (없어도 빌드는 됨 — sed 간이 압축으로)
sh build.sh                 # css/*.css → dist/*.min.css + themes + js. 저장소 node_modules/.bin → PATH → npx 순으로 minifier 탐색
python3 tools/gen_matrix.py # examples/src/matrix.html 재생성 (변형을 추가했으면)
python3 build_examples.py   # examples/src/*.html → examples/*.html (아이콘 스프라이트 인라인)
python3 tools/check.py      # 값 단언 회귀 234항목 (Playwright, 실패 시 exit 1). axe-core 가 있으면 접근성(serious/critical 0) 게이트 포함. shots.py 는 스크린샷 (1440 다크/라이트 · 유리 스킨 · 400 · 3400 tabs)
```

## 기존 어드민에 적용하는 순서

1. `dist/argus.min.css` 를 static 에 추가하고 `<link>` 만 걸어둔다. `ag-` 접두사라 기존 화면은 깨지지 않는다.
2. 페이지 셸부터 바꾼다: `ag-app` / `ag-topbar` / `ag-main`. 이것만으로 톤이 맞춰진다.
3. 테이블 → `ag-table-wrap > ag-table`, 버튼 → `ag-btn`, 상태 텍스트 → `ag-badge` 순으로 치환한다.
4. 폼과 모달은 마지막에. 기존 JS 바인딩이 많은 곳이라 클래스만 바꾸고 동작은 그대로 둔다.

## 라이선스

MIT — `LICENSE`. 폰트(Manrope · Noto Sans KR · JetBrains Mono)와 아이콘(Phosphor)은 각자의 라이선스를 따르며 저장소에 포함돼 있지 않습니다.
