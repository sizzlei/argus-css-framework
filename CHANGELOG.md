# Changelog

## 1.6.0 — 2026-10-14 · 사이드바 남은 높이

사이드바가 `100dvh` 고정인데 메뉴 아래가 비어 있었다(Andy). 구조 셋으로 남은 높이를 쓴다.
- `.ag-sidebar__nav` — 메뉴 그룹 묶음. 남은 높이를 채우고 길면 **여기만** 스크롤(머리·패널·푸터 고정, `overscroll-behavior: contain`). 없이 그룹을 바로 두면 예전처럼 사이드바 전체 스크롤.
- `.ag-sidebar__panel` — 바닥 패널(`--accent`/`--warn` 톤): 상태 요약 `.ag-sidebar__status`(점 + 숫자 셋), 용량 미터, 환경 전환 셀렉트, 점검 공지. `__panel__head`(소제목 + 링크). 접힌 사이드바·레일에서는 숨김. 권장 1~2개, 합쳐서 160px 안 — 900px 창에서 메뉴가 스크롤로 밀리지 않게.
- `.ag-sidebar__footer` 는 그대로(`margin-top: auto`는 nav/panel 이 있으면 0).
- **드로어도 같은 구조** — `.ag-drawer__body`(남은 높이 채우고 스크롤) + `.ag-drawer__foot`(액션, 바닥 고정, 왼쪽 보조 문구 자리). `.ag-modal__head` 는 고정. `__body` 없이 쓰면 예전처럼 전체 스크롤.
- 예시: resources(상태 + 스토리지 미터), layouts(환경 셀렉트 + 상태, 푸터 추가). check.py 135항목(사이드바 푸터 바닥 정렬·nav 만 스크롤·520px 창, 드로어 푸터 바닥·본문만 스크롤).

## 1.5.1 — 2026-10-13 · 라이트 카드 그림자 복구 (argus-server 보고 ⑩)

- 라이트 테마 `--ag-card-edge: none` → `0 0 #0000`. `box-shadow: var(--ag-card-edge), var(--ag-card-shadow)` 목록에 `none` 이 끼면 선언 전체가 무효가 되어 **라이트에서 모든 카드의 1px 그림자와 엔진색 띠(`--engine-stripe/-glow`)가 사라지고 있었다**. 1.2 에서 "라이트 카드 그림자 제거(보더만, 1px 만 남김)" 라고 적어 두고 실제로는 1px 까지 지워진 상태 — 감사 때 "라이트가 창백하다" 던 원인. 규칙을 CLAUDE.md 에: 쉼표 목록에서 쓰는 토큰은 `none` 금지, 빈 값은 `0 0 #0000`. check.py 가 라이트 카드 box-shadow ≠ none 과 stripe inset 을 단언(130항목).

## 1.5.0 — 2026-10-12 · 엔진 고유색

"어느 엔진인가" 를 브랜드색으로 — 상태색(good/warn/crit/info)·범주색(cat-1..4)과 별개의 세 번째 색 축. 카드는 배경만이 아니라 제목·테두리·띠·윗선·옅은 배경·그림자·단색 중 고른다. Andy 결정: DocumentDB 는 MongoDB 초록, MS-SQL 은 SQL Server 빨강·Oracle 은 와인으로 떨어뜨림, 차트까지 전부 엔진색.

- 토큰 `--ag-engine-{mysql|postgres|oracle|documentdb|mssql|other}` + `-text`(글자, surface·soft 위 4.5:1) + `-soft` + `-solid` + `--ag-text-on-engine-*`. 다크는 밝힌 값(#f5ad45 · #6a9fd8 · #d54f96 · #27ad5c · #ff7060), 라이트는 브랜드값(#c96a00 · #336791 · #8e2449 · #13aa52 · #cc2927) + 깊은 글자색. **MySQL 은 로고의 주황** — 청록(#00758F)은 PostgreSQL 파랑과 색각이상 ΔE 4.6 으로 분리가 안 된다.
- 훅: `data-engine="mysql"`(또는 `.ag-engine-mysql`)을 어느 요소에나 달면 그 안에서 `--ag-engine / -text / -soft / -solid / --ag-text-on-engine` 이 그 엔진 값. 컴포넌트는 `--engine` 변형 하나로 읽는다 — 엔진을 더할 때 토큰 다섯 + 훅 한 줄.
- 카드: `.ag-card--engine-title`(제목·아이콘) · `--engine-border` · `--engine-stripe`(왼쪽 3px) · `--engine-top`(윗선) · `--engine-tint`(9% 배경) · `--engine-glow`(색 그림자) · `--engine-solid`(단색, 안쪽 토큰 재정의 + 엔진색 요소 자동 반전). 조합 가능 — 권장 stripe + title. `.ag-card__icon--engine`.
- `.ag-badge--engine`(`--solid`/`--plain` 조합) · `.ag-dot--engine` · `.ag-chip--engine`(+is-active) · `.ag-avatar--engine` · `.ag-tag--engine` · `.ag-stat-card__icon--engine` · `.ag-list__item--engine`(띠) · `td.ag-td--engine`(띠) · `.ag-text-engine`.
- 차트: `.ag-spark--engine` · `.ag-bars__seg--engine` · `.ag-cols__bar--engine` · `.ag-progress__bar--engine` · `.ag-bubble--engine` · `.ag-chart__line/area/marker--engine`(path 에 data-engine). `AG.charts.engine('mysql')` / `engines([...])` → Apex colors (별칭 aurora·mariadb·pg·docdb·mongo·sqlserver 인식, 모르면 other).
- 팔레트 검증: 여러 엔진을 한 차트에 둘 때 순서 **documentdb → mysql → postgres → oracle → mssql** 로 인접쌍 CVD(P/D/T) ΔE 다크 ≥ 9.8 · 라이트 ≥ 7.4. 브랜드색이라 전체쌍 ≥ 8 은 불가(빨강 둘·초록) — 범례는 늘 점 + 이름, 엔진색을 상태로 읽지 않는다(MySQL 주황 ≠ warn). `tools/check.py` 가 tokens.css 를 읽어 인접쌍 ≥ 7 을 단언.
- 버블: `container-type: inline-size` 로 72px 이하 조각은 숫자만(이름은 범례).
- 예시: resources 표 행 `data-engine` + plain 배지 점, MS-SQL 행·필터 추가, 엔진 stacked 바·범례; index 슬로우 쿼리 라인·버블·범례·행 점; layouts 엔진 바·알림 표 대상 셀 띠; detail 클러스터 카드 stripe+title + Aurora MySQL 배지. 카탈로그 "엔진 고유색" 섹션, 매트릭스 엔진 × 컴포넌트 + 카드 7변형. 예시 엔진 수치 통일: MySQL 102 · PostgreSQL 54 · Oracle 14 · DocumentDB 10 · MS-SQL 4 · 기타 2 = 186.
- `tools/check.py` 128항목.

## 1.4.0 — 2026-10-12 · 디자인 감사 2차 (모션·타이포·색 상한·축소)

1.3 까지의 결과를 design-audit · ui-typography · motion · dataviz · a11y 스킬로 다시 감사(보고서는 프로젝트 문서). 큰 결함이 아니라 "규칙은 있는데 예외가 새는" 자리들 — 반복 모션, 리터럴 지속시간·글자 크기, 예시에 남은 인라인 스타일, 한 화면 색 개수, 버블 면적 왜곡. 새 토큰·클래스가 있어 minor.

### Phase 1 — Critical
- **무한 모션 상한**: `.ag-dot--pulse` 는 기본 3회(`--ag-pulse-loop: 3`) 깜빡이고 멈춤. 진행 중인 장애 하나에만 `.is-live`(= infinite). 로그인 상태 점·`.ag-log--live` 점은 정적으로 — 늘 보이는 요소는 움직이지 않는다(생산성 도구 모션 원칙). 예시 pulse 10 → 화면당 ≤1, check.py 가 "보이는 무한 애니메이션 ≤1" 을 단언(스켈레톤·스피너·커서 제외).
- 지속시간 토큰 `--ag-dur-move`(260ms, 패널·스위치) · `--ag-dur-slow`(400ms, 데이터 바). 리터럴 `.25s/.28s/.4s` 5곳 치환.
- `.ag-field__error`(아이콘 + 문구, `role="alert"`) — 오류를 색만으로 알리지 않는다. 예시에 `aria-invalid` + `aria-describedby`.
- 스파크라인 톤 `--warn/--info/--1..4` 추가, 기준선 `.ag-spark__ref`(점선). 예시의 인라인 `stroke` 제거.
- `.ag-td--query`(한 줄 말줄임, 폭 `--ag-query-w` 300px) · `.ag-card--flush > .ag-table-wrap + .ag-card__foot`(표 아래 요약 푸터) · `.ag-list__item.is-current`(지금 보는 항목, 테두리만) · `.ag-mode-switch` 데모 크롬 CSS 로 — **예시 인라인 스타일(패딩·폭·opacity·절대배치·보더색) 0**, check.py 단언.
- **버블 면적 = 값**: `.ag-bubbles` 컨테이너 + `--r = √비율`(지름 = `--ag-bubble-max` × `--r`). 58:33:9 가 면적비로 정확히. `AG.charts.bubbles(root)` 가 `data-v` 로 `--r` 계산. 예시의 절대 좌표 제거, 범례 추가.

### Phase 2 — Refinement
- **글자 크기 바닥 11px**: 9/10/10.5px 리터럴 13곳(Slack 태그·kbd·스텝 점·버전 배지·브랜드 small·코드 블록 lang·알림 카운트·사용자 메타·트리 카운트·레일 배지…) → `--ag-text-xs`. 버블 라벨은 `max(11px, .45em)`. check.py: 예시 4페이지에서 11px 미만 글자 0.
- `h4` 14/600 · `h5` 13/600·text-2 — `h3`(17) 와 구분. 콘솔은 h1·h2·h3 로 끝내는 것을 권장(CLAUDE.md). `body` 에 `"kern" 1, "liga" 1` + `text-rendering: optimizeLegibility`.
- **색 상한**: 카드 아이콘 타일의 상태색(good/warn/crit/info)은 화면당 2개 이하 — 나머지는 기본(회색)·accent·범주색. 대시보드 9개 → 상태색 2(이벤트 crit·점검 warn). check.py 단언. 페이지 글로우 11 → 8%.
- 공통 disabled: 세그먼트·칩·탭·네비·콤보박스 옵션·퀵액션 `:disabled/[aria-disabled]`. 포커스 링은 전역 outline(2px + offset 2px) 과 `--ag-ring-focus` 가 같은 두께라 유지.
- `.ag-stat-row` ≤720 격자에서 `align-items: start` — 라벨 줄 수가 달라도 숫자가 한 줄에(flex-end 가 격자로 넘어오던 버그).
- 축소: 대시보드 인사말 옆 숫자 3개 제거(KPI 스트립 4장으로 통합 — 인스턴스·복제·스토리지·슬로우 쿼리; 백업은 액센트 카드가, 열린 알림은 종이 이미 말한다), 머리 오른쪽엔 갱신 시각 + 새로고침. 로그인 숫자 띠 "186" 중복 제거. 카드 머리 보조 동작은 ghost 텍스트 버튼 하나로(↗ 아이콘 버튼은 외부 링크 전용). `.ag-mode-switch` 데모 크롬 CSS 로.

### Phase 3 — Polish
- **키보드**: 오버레이를 닫으면 포커스가 연 요소로 복귀(`__agOpener`). `<dialog>` 가 아닌 모달·드로어는 열 때 첫 포커스 요소로 들어가고 Tab 이 안에서 순환(argus.js 가 연 것만). 클릭 가능한 행 Enter/Space → 행의 첫 링크. 드롭다운 트리거 ↓ → 메뉴 첫 항목(+ `aria-expanded`). check.py 가 드로어 열기·순환·ESC 복귀·행 Enter·↓ 를 단언.
- 세그먼트는 `role="radiogroup"` + `role="radio" aria-checked`(선택지 하나) — `aria-pressed` 도 계속 동작. 대시보드 기간 세그먼트가 기준 예시.
- 확인: 라이트 글로우 7% 는 흰 카드 위에서 띠로 보이지 않음. 3400px 에서 KPI 카드 ≤ 420px(본문 상한 1600 안).
- `tools/check.py` 126항목.

### 정정 (1.4.1)
- `docs/renewal-prompt.md` 의 `ph-regular` → `ph` (Phosphor 2.1.x regular 의 weight 클래스는 `ph`; `ph-regular` 는 존재하지 않음). `templates/go-html-template/login.html` 의 `ph-bold` 10곳 → `ph`. `check.py` 의 Phosphor 테스트 마크업도 `ph` 로 — bold 는 가이드에서 금지된 굵기라 검증 대상이 아니다.

## 1.3.0 — 2026-10-12 · 화면 밀도 보강 (예시 + 시각 디테일)

1.2 로 모양이 단정해진 대신 예시 화면이 허전해졌다는 피드백. 두 축으로 보강 — (1) 예시 페이지를 실제 운영 콘솔 밀도로 채우고, (2) 카드·페이지에 조용한 시각 단서 몇 가지를 프레임워크 차원에서 더했다. 새 클래스·토큰이 있어 minor. 서비스는 dist 재복사만으로 (1)의 시각 변화가 따라오고, 새 컴포넌트는 쓰고 싶을 때 쓴다.

### 시각 (프레임워크)
- **카드 광택** `--ag-surface-sheen` — `.ag-card` 의 `background-image`. 다크는 윗부분 2.8% 흰 그라데이션(판처럼 보이게), 라이트는 `none`(평면 유지). 단색 카드(`--accent/--accent2/--inverse`)는 `background:` 단축으로 덮여 영향 없음.
- **페이지 글로우** `--ag-bg-glow` — `.ag-app` 상단에 테마 액센트 11%(라이트 7%)의 큰 radial. 테마 파일이 액센트를 바꾸면 글로우도 따라온다. 끄려면 `--ag-bg-glow: none`.
- **카드 아이콘** `.ag-card__heading` > `.ag-card__icon` (30px 타일, `--accent/--good/--warn/--crit/--info/--1..4`) + 제목(+`__subtitle`). 단색 카드 안에서는 `--_on` 으로 자동 보정. 모양 → 톤 순서.
- `.ag-timeline__head`(제목 왼쪽·시각 오른쪽) + `.ag-timeline__meta`(한 줄 보조) + `.ag-timeline--compact`.
- 테이블 셀 안 스파크라인: `.ag-table td > .ag-spark` 폭 `--ag-spark-w`(96px) — 셀 안에서 % 폭이 0 이 되던 문제.
- `.ag-grid--tight`(12px) 카드 안 타일 격자 · `.ag-tile--stack` 안 `.ag-cluster/.ag-spark/.ag-progress` 는 타일 폭을 채움 — 메트릭 타일 패턴.
- `.ag-avatar--xs`(22px, 테이블 셀 담당자) · `.ag-nowrap` 유틸.
- 로그인 브랜드 패널: `.ag-auth__facts`(숫자 띠) + `.ag-auth__tiles`(계단식 라이브 타일, 글래스) — 빈 가운데를 채우되 폼보다 조용하게.

### 예시 (content)
- index: KPI 스트립 4장(스파크라인) · 리소스 표 7행 + 푸터(비용) · 최근 이벤트(타임라인 6) · 점검 일정 · 스토리지 상위(미터) · 최근 슬로우 쿼리(표 + 셀 스파크라인 + sticky-end) · 빠른 작업 + 온콜. 1,100px → 2,400px.
- resources: 스탯 카드 4장(스파크라인·맥락) · 표 7 → 14행 · 엔진/플랫폼 stacked · 환경/리전 · 최근 변경 타임라인.
- detail: 스탯 카드 스파크라인 · 메트릭 카드(1시간, 타일 5) · 활성 세션 표 · 이벤트 +2 · 태그·담당 · 비용 구성 바.
- layouts(sidebar): 엔진 바 5행 + 푸터 · 열린 알림 표 · 점검 일정. login: 숫자 띠 + 라이브 타일.
- components: 타임라인 head/meta, 셀 스파크라인, grid--tight 타일, avatar xs. matrix: `ag-card__icon` × 톤 + 단색 카드 안.

### 도구
- `tools/check.py` 96항목 (+6: 광택·글로우·카드 아이콘 크기·셀 스파크 폭·grid--tight gap·라이트 광택 없음).

## 1.2.1 — 2026-10-12 · 접근성 감사 (WCAG 2.2 AA)

axe-core 를 `tools/check.py` 게이트로 붙였다 (예시 6페이지 × 다크·라이트, serious/critical 위반 0 — `npm i` 로 axe-core 가 있으면 켜지고 없으면 건너뜀). 걸린 것(거의 전부 색 대비, 몇 개는 이름 없는 아이콘 버튼·제목 구조)을 서비스 쪽 예외가 아니라 토큰으로 풀었으므로 dist 재복사만으로 따라온다. 모양·밀도는 1.2.0 그대로, 색 몇 개가 한 톤 움직인다.

### 색 대비 (1.4.3)
- **액센트 역할 분리**: `--ag-accent` 는 채움(버튼·solid 배지·액센트 카드, 위 글자 `--ag-text-on-accent`), 새 토큰 `--ag-accent-text` 는 글자(링크·활성 탭·아이콘·soft 배지). 다크에서 한 색으로는 둘 다 못 맞춘다 — 다크 채움 #7c6cff → #6a59e8 (흰 글자 3.9 → 5.0:1), 글자는 #9d90ff(표면 위 6.7). 라이트 글자는 hover 톤 #4b3fd1(accent-soft 위에서도 4.5). 테마 7종 + `_template.css` 모두 `--ag-accent-text` 추가, 다크 채움 재조정(blue #3570d6 · indigo #5f67e3 · red #d33a4e), 라이트 orange #b0570f · yellow #8c6700 로 깊게. `color: var(--ag-accent)` 로 글자를 칠하던 자리는 전부 `--ag-accent-text`.
- **accent-2(분홍) 글자 토큰** `--ag-accent-2-text` (다크 #ff7aa8 · 라이트 #b5195a) — soft 배지·아바타·`.ag-tok-num`·`.ag-tree__val--num`·`.ag-text-accent2`·퀵액션/스탯 아이콘. 라이트 `--ag-accent-2`·`--ag-chart-2` #e0266f → #db206a (흰 글자 4.49 → 4.7).
- **범주색 위 글자**: `--ag-text-on-chart`(버블·트리맵), `--ag-text-on-accent-2`, `--ag-text-on-cat-1..4`(solid 배지·칩·버블). 다크 범주색은 밝아 #111, 라이트는 1·2 흰 글자 / 3·4 #111. 트리맵 타일은 `--ag-treemap-base`(다크 `--ag-bg`, 라이트 `--ag-surface-2`) 와 섞고 명도 상한 .7.
- **메타 글자** `--ag-text-3` 다크 #858a9f → #9196ab (surface-3 4.6 · 활성 행 accent-soft 5.1), 라이트 #6b7084 → #626678. 11px 메타·태그 키·Slack 태그·알림 시각·cmdk 힌트가 모두 AA.
- **상태 글자** `*-text` 라이트 한 단계 깊게 (good #096544 · warn #8f4f00 · crit #ad2140 · info #09649a), 다크 crit-text #fd8092 (crit-soft 위 4.9). 단독 글자 사용처를 `*-text` 로: soft 배지·증감·로그 줄·`.ag-tok`·diff·세션·Slack mention/inline-code·태그 제거·`.ag-btn--danger`(글자 `--ag-crit-text`, hover 는 채움)·outline danger. `.ag-tag--accent .ag-tag__key` 배경 24% → 14%.
- **Slack 미리보기 버튼** 실제 Slack 톤으로 (primary #007a5a 5.3:1 · danger #c41e52 5.8:1 — 이전 #2eb67d 는 2.5).
- `.ag-approval.is-rejected` 의 `opacity: .85` 제거 — 안쪽 배지·버튼·아바타 대비가 전부 깨졌다. 반려는 왼쪽 보더 + 결과 아이콘으로만.
- `.ag-provider--google .ag-provider__hint` 다크 Google 버튼(#131314) 위 #a8abaa.
- 단색 카드 안 `--ag-text-2/-3` 97%/94% 로.
- **링크**: 본문 블록(p·li·td·알림·배너·힌트·빈 상태) 안의 링크는 밑줄(색만으로 구분 금지, 1.4.1). 알림·배너·토스트 안 링크는 `color: inherit; font-weight: 600` — 색 배경 위 액센트 글자 대비가 안 나온다.

### 마크업 (예시 수정 — 서비스 리뉴얼도 같은 규칙, `docs/renewal-prompt.md` 품질 기준)
- 아이콘만 있는 버튼·링크는 `aria-label` (또는 `.ag-sr-only` 텍스트). 알림 종 버튼은 보이는 숫자 + sr-only "알림" 으로 (`aria-label` 과 보이는 텍스트 불일치 규칙).
- 체크박스/⋯ 열 `<th>` 는 `.ag-sr-only` 텍스트. 페이지마다 `<h1>` 하나(페이지 제목), 카드 제목은 `<h2>`/`<h3>` 순서대로 (eyebrow 는 `h6` 아님 → `<h3 class="ag-eyebrow">`, 이제 `.ag-eyebrow` 는 h 요소에서도 같은 모양).
- `<nav aria-label="주 메뉴">`, 배너 `role="region" aria-label`, 레이아웃 모드 전환은 `role="region"`. 페이지네이션 `aria-label="페이지"` + 현재 `aria-current="page"`, 날짜 입력 `aria-label`. 스크롤되는 `<pre>` 는 `tabindex="0"`.
- `.ag-secret-field__reveal` 높이 `--ag-control-h-sm` (24px 타깃, 2.5.8).

### 도구
- `tools/check.py` 90항목 (+ axe 게이트). `package.json` devDependency `axe-core`. 대비 값은 전부 토큰 주석에 적어 두었다.
## 1.2.0 — 2026-10-12 · 디자인 감사 (인프라 콘솔 성격으로)

방향: "조용하고 빽빽하고 정확하게". 소비자 앱 인상(큰 라운드·알약 버튼·52px 숫자·분홍 보조색)을 눌러 데이터가 앞으로 나오게 한다. 토큰 위주 변경이라 서비스는 dist 재복사만으로 따라온다 — 모양·밀도가 눈에 띄게 바뀌므로 minor 버전.

### Phase 1 — 위계·가시성·밀도
- `.ag-table-wrap` 가로 스크롤 가장자리 그림자(`--ag-shadow-scroll`, background-attachment 기법) — 잘린 열이 있다는 단서. `.ag-table--sticky-end` 마지막 열(상태·액션) 고정.
- 테이블 셀 패딩 토큰 `--ag-cell-y/--ag-cell-x` 11/16(행 ≈44px, 이전 14/18 ≈50px). `--dense` 8/12, `data-density=compact` 7/12.
- `h1` 38/500 → 28/600 (`--ag-text-2xl`). 큰 제목이 필요한 랜딩·상태 화면은 `.ag-h-display`.
- 스탯 숫자 `--ag-text-4xl` 52 → 40. 52 는 `--ag-text-hero` + `.ag-stat--hero` 로 한 화면 한 곳만. `.ag-stat-row` KPI 묶음은 720px 이하 3열 격자 + 28px 숫자 (2+1 로 꺾이던 모바일).
- `.ag-badge--plain` — 종류(엔진·팀)는 점 + 글자, 알약은 상태 하나만. resources 예시의 엔진·prod 배지를 정리(행당 알약 3 → 1).

### Phase 2 — 모양·크기·색·타이포
- 모양 토큰: `--ag-radius-sm/md/lg/xl` 8/12/18/24 → 6/10/12/16, 버튼은 새 토큰 `--ag-radius-btn` 10px(알약 → 둥근 사각, 예전 모양은 `.ag-btn--pill`). 알약은 칩·배지·세그먼트·네비·사용자 메뉴에만.
- 컨트롤 높이 토큰 `--ag-control-h/-sm/-lg` 36/30/44 (이전 40/32/48) — 버튼·입력·셀렉트·사용자 메뉴·태그 입력·콤보박스가 참조. `pointer: coarse`(터치)에서 44/36/48, `data-density=compact` 32/26. 칩 44 → 36(`--sm` 28), 증감 배지 48 → 40, 네비 항목 패딩 10/22 → 8/18, 입력 패딩 14 → 12.
- 제목 스케일: h2 28 → 20, h3·카드 제목 20 → 17. (h1 은 Phase 1 에서 28)
- 라이트 카드 그림자 제거(보더만, `--ag-card-shadow` 1px 만 남김) — 평면이 더 정확해 보이고 오버레이와 구분.
- 보조색(accent-2 분홍)은 브랜드 그라데이션·범주 2번에만. 대시보드 칩·상세 환경 배지에서 제거(예시). 클래스는 유지하되 UI 요소에는 쓰지 않도록 매핑표에 명시.
- 아이콘 가이드: Phosphor 는 regular(`ph`)/`ph-duotone`(bold 금지), 크기는 16/18/20 셋.

### Phase 3 — 상태·모션·세부
- `.ag-empty--error`(아이콘만 crit, 원인·시각은 설명에) · `.ag-empty--sm` · `.ag-empty__actions`(다시 시도 자리) — 운영 도구는 API 실패가 일상.
- `.ag-table--loading` — 헤더·열 폭 유지, 행만 shimmer(`td::after`). 레이아웃 점프 없이 기다린다. 숫자 열은 오른쪽 정렬 막대, 액션 열은 비움.
- 키보드 포커스 링 `--ag-ring-focus`(배경색 2px 틈 + 액센트 2px 실선) — 버튼·카드·provider. 입력은 기존 `--ag-ring`(부드러운 글로우) 유지.
- 오버레이 등장 모션 1종 `ag-rise`(4px 떠오르며 페이드, 180ms; 메뉴 140ms), `<dialog>` 배경 `ag-fade`. 닫힘은 즉시. reduced-motion 은 기존대로 .01ms.
- 라이트 `--ag-surface-2` #f3f4f8 → #eef0f5, `--ag-surface-3` #e6e8f0 → #e3e6ee — 흰 카드 위 타일 경계가 보이도록.
- 모바일 배너: 아이콘이 혼자 둘째 줄로 떨어지던 것 → 첫 줄 옆에 두고 버튼만 아래 전체 폭.

## 1.1.0 — 2026-10-03 · 첫 서비스(Harpoon) 적용 후 보강
- `.ag-btn--outline.ag-btn--primary`(액센트 테두리, hover accent-soft — 채움 primary 의 outline 짝), `.ag-list__item:disabled`(`.ag-btn` 과 같은 .45 흐림 + pointer-events), `.ag-select--list`(`size=N` 열린 리스트 박스: 고정 높이·캐럿 제거, option 행 패딩·선택 강조). 상세 화면 버튼 짝, 계정 선택 모달, 복구 소스 DB 선택에서 들어온 건.
- `.ag-app--fluid` — 본문 `.ag-main` 의 1600px 상한(`--ag-content-max`) 해제, 거터만 남김. 다른 모드와 조합. 2560px 모니터에서 1600px 로 모이는 게 "좁아졌다" 로 들어온 건 (이전 앱은 상한이 없었음). layouts.html 에 fluid 토글, 매핑표에 `max-w-*`/`container` 제거 규칙.
- `.ag-chip--good/--warn/--crit/--info` 상태 변형(soft 배경·상태 글자·톤 테두리) + `--solid` 조합. solid 는 새 토큰 `--ag-*-solid` / `--ag-text-on-*`(다크: 밝은 상태색 + 어두운 글자, 라이트: 깊은 `*-text` 색 + 흰 글자) — `.ag-badge--solid` 도 같은 토큰으로 바꿔 라이트 crit(4.3:1)·다크 crit 흰 글자(2.7:1) 대비 미달을 해소. 점검 결과 목차 칩에서 쿼리 오류 코드를 구분할 수단이 없던 건 (`.ag-tag` 상태 변형과 같은 건).
- `.ag-tag--good/--warn/--crit/--info` 상태 변형(테두리·키·값 전체에 상태색, 범주 변형은 키만) + `.ag-tag--other`. 태그 키 집계에서 "제거 예약"·"값 N종" 을 색으로 구분할 수단이 없던 건. 색만으로 말하지 않도록 예시는 아이콘·텍스트 동반.
- `.ag-secret-field--block` — 여러 줄 시크릿(YAML·인증서·키)용 `textarea.is-masked`: 글자 투명 + 번진 text-shadow + blur, 선택·복사·포인터 차단, 가운데 `__reveal` 버튼(`:has(.is-masked)` 일 때만). `-webkit-text-security` 가 input 전용이라 textarea 를 가릴 수단이 없던 건. argus.js `data-ag-reveal` 이 input·textarea 공통으로 `is-masked` 토글(`ag:secret-toggle`).
- `.ag-segmented` 에 `max-width: 100%; overflow-x: auto`(스크롤바 숨김) + 항목 `flex: none` — `.ag-nav` 와 같이 항목이 많아도 뷰포트를 밀지 않음. 탭 5개 화면에서 400px 가로 스크롤이 나던 건. 매핑표에 선택 기준(3~4개 segmented / 그 이상 nav·tabs) 추가.
- `.ag-table--clickable` / `tr.is-clickable` — 행 전체가 링크인 목록: `cursor: pointer`, hover 에 액센트 기운, `tr[tabindex]` 포커스 링, `.ag-td--actions` 안은 기본 커서. 커서가 기본값이라 클릭 가능함이 드러나지 않던 건.
- 단색 카드(`.ag-card--accent/--accent2/--inverse`)가 안쪽에서 `--ag-text/-2/-3` `--ag-border(-strong)` `--ag-surface-2/-3/-hover` 토큰을 재정의 — `.ag-text-2/-3` 만 보정하던 것을 토큰 단위로 바꿔 `.ag-label` `.ag-hint` `.ag-stat__label` `.ag-kv dt` `.ag-card__foot` `.ag-btn--outline` 등 토큰을 쓰는 모든 컴포넌트가 배경 위에서 읽힌다 (violet·yellow × 다크·라이트 대비 단언). 액센트 카드를 포기하고 일반 카드로 우회하던 건.
- `--ag-chart-other` / `--ag-cat-other`(+`-soft` `-text`) — "기타" 조각용 중립 회색(다크 #7a7f90, 라이트 #a0a5b8, 명도 밴드 안). `.ag-bars__seg--other` `.ag-cols__bar--other` `.ag-dot--other` `.ag-badge--other` `.ag-avatar--other`. `AG.charts.palette(n)` 은 5번째(마지막)를 기타 회색으로, `apex()` 는 series 수에 맞춰 colors 자동 — 상위 4 + 기타 도넛/stacked bar 에서 기타가 1번 색을 반복하던 건.
- `.ag-qr__pending` — QR 생성 전 180px 플레이스홀더(shimmer, 흰 박스 위라 테마 무관 회색). 템플릿의 인라인 크기·`#666` 우회 제거. `.ag-quick-action__body` > `__title` + `__meta` 2줄 라벨, `__end` 오른쪽 끝 아이콘 — 부제를 `data-tip` 으로 돌리던 건.
- 아이콘을 문맥으로 잡는 규칙 47개(`.ag-input-group` 선행 아이콘 위치, `.ag-user` 캐럿, `.ag-auth__logo-box`·`.ag-brand-mark`·`.ag-dropzone`… 크기, 사이드바·cmdk·토스트·알림·승인 색)를 전부 `:is(.ag-icon, [class*="ph-"])` 로 — Phosphor `<i>` 가 svg 와 같은 대우를 받는다. 크기 규칙에는 `font-size` 동반. `.ag-input-group--end:not(:has(> …))` 도 포함. 로그인 이메일 입력의 Phosphor 아이콘이 입력칸 밖으로 밀리던 건. 템플릿의 `<i class="ph-… ag-icon">` 우회 제거.
- `.ag-only-dark` / `.ag-only-light` 가 Phosphor `<i>` 에서 안 먹던 건 — phosphor.js 가 런타임에 `<head>` 끝에 넣는 `[class^="ph-"] { display: inline-block }` 이 같은 특이도로 뒤에 와서 `display:none` 을 덮음. 숨기는 규칙만 `!important` 로 두고(`:root:not([data-theme=light]) .ag-only-light`, `:root[data-theme=light] .ag-only-dark`) 보이게 하는 규칙은 없애 요소 본래 display 를 유지. 다크에서 해·달이 둘 다 보이던 문제.
- `.ag-btn--ghost.ag-btn--danger` (투명·중립 → hover 시 crit-soft/crit 글자), `.ag-btn--outline.ag-btn--danger` (crit 테두리 → hover 시 crit-soft). 테이블 행의 삭제 버튼처럼 평소엔 조용해야 하는 파괴적 액션 — `--danger` 가 상시 붉게 칠해져 `--ghost` 와 조합이 안 되던 건.
- 문서·카탈로그 정리: README 를 1.1.0 상태로 (dist 크기, 변형 선언 순서·소유권 원칙, 피드백 루프 처리 목록, `--ag-seq` 토큰 행, check.py 53항목, 빌드 체인). 카탈로그에 3단계 로그인 조각(`.ag-auth__email-chip` `.ag-otp-input` `.ag-auth__qr` `__qr-icon` `.ag-auth__foot` `__mobile-foot`) 카드 — CSS 에만 있고 예시가 없던 마지막 셀렉터들. 이제 `css/` 의 모든 클래스가 카탈로그·매트릭스·예시 중 한 곳에 나온다.
- `button.ag-card` 에 `align-items: stretch` — 크로미움 UA 의 `button { align-items: center }` 가 안쪽 행을 shrink-wrap 시켜 `.ag-cluster--between` 오른쪽 정렬과 `.ag-code-block` 전체 폭이 깨지던 건. 서비스의 인라인 `align-items:stretch` 우회 불필요.
- `.ag-list__item.is-active` 선택 상태 (액센트 soft 배경 + 액센트 테두리, count 배지 액센트) + `button.ag-list__item` 리셋(폭·정렬·폰트). `--divided` 안에서는 왼쪽 액센트 바. 팀 필터 같은 선택 목록이 사이드바 밖에서 `.ag-sidebar__item` 을 빌려 쓰던 건.
- 순차 색 램프 토큰 `--ag-seq-1..5` (다크·라이트, `--ag-chart-1` → `--ag-surface-2` color-mix 15/36/57/78/100%) + `.ag-heat--1..5`. `AG.charts.sequential(n, base?)` 가 같은 값을 rgb 로 돌려주고, `AG.charts.heatRanges(min,max)` 가 Apex `colorScale.ranges` 를 만든다. `apex({type:'heatmap'})` 은 enableShades 를 끄고 series 범위로 램프를 자동 적용, 셀 경계는 `--ag-chart-grid` — 라이트에서 Apex 자체 shade 가 흰색으로 흐려져 셀이 사라지던 문제. `.ag-heat` 에 `--ag-chart-grid` 1px 안쪽 테두리를 넣어 값 0 셀도 카드와 구분. `--crit` 안의 `--empty` 가 crit 램프에 덮이던 것 수정.
- **버전 규율**: 동작이 바뀌는 수정(간격·래퍼·소유권)은 minor 를 올린다. `dist/VERSION` 이 서비스가 쓰는 버전의 기준.
- `argus.js` 를 `<head>` 에서 로드해도 사이드바 접힘·그룹·노드 상태 복원과 차트 호버가 동작 (DOM 준비 후 초기화). 권장 위치는 여전히 body 끝(또는 `defer`) — README 스니펫에 명시. `AG.chartHover()` 로 동적 차트에 다시 붙일 수 있음.
- 접힌 사이드바(`is-collapsed`)·dual 모드가 Phosphor `<i class="ph-…">` 아이콘까지 숨기던 모순 — `:not([class*="ph-"])` 추가. 서비스가 `ag-icon` 을 중복 표기할 필요 없음.
- `package.json`(devDependencies: esbuild, lightningcss-cli) — `npm i` 한 번이면 JS 도 제대로 minify (13.4KB → 10.5KB). build.sh 가 저장소 node_modules/.bin → PATH → npx 순으로 찾고, 없으면 기존 sed 폴백.
- `tools/check.py` — 값 단언 회귀 40항목: 페이지 에러·400px 가로 스크롤, 배지 톤×모양·solid, input-group 양끝 패딩, form-grid span·열 수, 토스트 쌓임, a/button 카드 flex, 범주·아바타 대비(다크·라이트), 오버레이 소유권 8시나리오, 래퍼 스택·간격 토큰, tabs 1440~3840, 폴백 간격. 첫 실행에서 라이트 `--ag-warn-text` 대비 4.29 를 잡아 `#9a5600` 으로 조정.
- 변형 선언 순서 원칙(모양 → 톤 → 조합)으로 `.ag-badge` 블록 재정렬 — `--count` 의 `:not()` 7개 체인 제거, 중복 선언 정리. 간격 폴백은 "클래스 없는 부모 안에서만" 으로 범위를 좁혀 컨테이너 목록 자체를 없앰 (`:where()` 특이도 0).
- **argus.js 오버레이 소유권 원칙** — 바깥 클릭·ESC 가 모든 `.ag-modal-overlay` / `.ag-drawer` / `.ag-dropdown` / `.ag-combobox` 를 닫던 설계를 "자기가 `data-ag-open`·⌘K 로 연 것만 닫음" 으로 변경. Alpine/Vue/React 가 제어하는 오버레이를 `hidden !important` 로 잠그던 문제(모르면 조용히 고장) 해소. 표시 토글은 `is-open` 클래스 + `hidden` 병행, 닫기 직전 cancelable `ag:overlay-close`(reason: button/backdrop/escape) · `ag:overlay-closed` · `ag:overlay-open` 이벤트, `AG.overlay.open/close/owns` API. 명시적 `data-ag-close` 버튼은 소유와 무관하게 동작(마크업이 opt-in).
- `.ag-glow` 복원 — 미검증 정리 때 삭제했으나 서비스(`.ag-app.ag-glow`)가 쓰고 있었음. 매트릭스에 데모 추가.
- `.ag-app--tabs` 상단바가 3,224px 이상 초광폭에서 두 행이 한 줄로 나란히 붙던 버그 — wrap flex 에서 `__row` 의 `max-width` 가 flex-basis 가 된 탓. 상단바를 블록으로 쌓도록 변경(행 내부만 flex). `tools/shots.py` 에 3400px 레이아웃 회귀 추가.
- `.ag-page` — 화면 내용을 감싸는 `<div x-data>` 래퍼가 `.ag-main` 직계가 되면 gap 이 래퍼 하나에만 걸려 안쪽 블록이 0px 로 붙던 문제(Harpoon 전 화면). 래퍼에 `.ag-page` 를 붙이면 같은 스택이 되고, 클래스 없는 div / `[x-data]` 래퍼는 자동 적용.
- **기본 간격 상향 + 토큰화**: 카드 사이 `--ag-gap-grid` 20 → 24px, 본문 블록 사이 `--ag-gap-main` 24 → 32px, 섹션 `--ag-gap-section` 16 → 20px (Harpoon 라이트 대시보드에서 카드가 붙어 보인다는 피드백). 서비스는 `:root` 에서 토큰만 바꾸면 됨. 클래스 없는 부모 안에 `.ag-card + .ag-card`, `.ag-btn + .ag-btn` 을 그냥 나란히 두었을 때의 기본 간격 폴백 추가 (부모에 클래스가 있으면 그쪽 gap 에 맡김).

## 1.0.0 — 2026-10-02 · 공개 첫 릴리스
- 이름을 **Argus CSS Framework** 로, 접두사를 `ka-` → **`ag-`** 로 (클래스·토큰 `--ag-*`·data 속성·JS 전역 `AG`·localStorage 키 `ag-theme`). 배포 파일명 `argus.*`.
- 컬러 테마를 색 이름 7종으로: `red` `orange` `yellow` `green` `blue` `indigo` `violet` — 원색을 한 톤 눌러 자연스럽게, 다크·라이트 각각, 액센트 위 글자 대비 확인.
- 사내 전용 문서·템플릿을 걷어내고 Go html/template 적용 예시만 일반화해 남김. MIT 라이선스.
- 샘플 페이지 프로필을 Andy 로. 컬러 테마 선택은 하단 데모 네비에서 (모든 페이지).
- `.ag-avatar` 톤 변형 `--good/--warn/--crit/--info/--accent2/--cat1~4/--neutral` — 카탈로그에 인라인 style 로 14번 반복되던 것 교체. 서비스에서도 아바타 색은 클래스로.
- **조합 매트릭스** `examples/matrix.html` (`tools/gen_matrix.py` 생성): 배지 12톤 × 9모양, 버튼 7변형 × 9상태, 카드·타일·입력·피드백·차트·패턴·유틸 전 변형을 격자로. 여기서 바로 잡힌 누락: `.ag-badge--solid.ag-badge--info / --accent2`, `.ag-banner--info`, `.ag-donut--sm` 중앙 글자 넘침.
- 미검증 셀렉터 정리: 124개 중 쓸 것은 매트릭스/레이아웃 페이지에 예시 추가(focus-wide·dual-nosidebar·underline 탭 토글 포함), 죽은 것 삭제 — `.ag-table--skeleton`, `.ag-auth__logo/__logo-mark/__footer`(구 인증 마크업), `.ag-spark__end`. 남은 미검증 0 (JS 가 문자열로 붙이는 모드 클래스 제외).
- `.ag-input-group--end` 가 `padding-left` 를 덮어 선행 아이콘과 같이 못 쓰던 문제 — 오른쪽 여백만 추가하도록. 아이콘 + `--end` 조합 동작.
- `.ag-field--span2 / --span3` (form-grid 중간 폭, "Host 2칸 : Port 1칸"). 720px 이하 자동 전체 폭.
- `a.ag-card` / `button.ag-card` 기본값(왼쪽 정렬·밑줄 제거·폰트 상속·전체 폭·포커스 링 — `display` 는 건드리지 않아 `.ag-card` 의 flex column·gap 이 그대로 적용) + `.ag-card.is-selected`. 카드를 링크/버튼으로 쓸 때 인라인 style 이 필요 없다. 유틸 `.ag-text-left`, `.ag-scroll-y`(`--sm/--md/--lg`, `--ag-scroll-max`) 추가.
- `.ag-tile--stack` (라벨 위·값 아래 세로 타일) 추가 — 기본 `.ag-tile` 은 가로 space-between 이라 세로 콘텐츠를 넣으면 가운데가 비던 오용 대응. `.ag-form-grid--2/--3/--4` 열 고정 변형 추가 — auto-fit 에 `--full` 이 섞이면 넓은 화면에서 트랙이 쪼개지는 문제의 올바른 사용법. 카탈로그에 예시·주의 문구, principles "쓰지 말 것" 에 추가.
- `.ag-badge--count` 가 뒤에 선언돼 `--accent` 등 톤 배경을 덮던 버그 — count 는 모양만 담당하고 배경은 톤 변형이 정하도록 분리. `--count --accent/--crit/--cat1/--inverse` 조합 전부 동작.
- 범주색 `--ag-cat-1~4` (+ `-soft` / `-text`) 토큰과 `.ag-badge--cat1~4`(+ `--solid`), `.ag-tag--cat1~4`, `.ag-dot--cat1~4` 추가 — 엔진·태그·팀 같은 "종류" 를 상태색 없이 구분. 차트 범주색과 같은 네 가지, 라이트는 글자색을 한 단계 깊게 (4.5:1).
- `.ag-toast-stack--static` 이 모달 위로 올라오던 버그 수정 — flex 아이템은 `position: static` 이어도 `z-index` 가 살아 쌓임 맥락을 만든다 (90 > 모달 80). `z-index: auto` 로 해제.
- `.ag-toast--warn` / `--info` 추가 (기존 good/crit 만 있었음). 4종 모두 왼쪽 3px 톤 바로 구분. `AG.toast(msg,'info')` 도 그대로 동작.
- 컴포넌트 카탈로그 `.ag-qr` 예시에 실제 QR(otpauth 데모 URL, SVG) 추가. 720px 이하 상단 바 브랜드 축소·말줄임(좁은 화면 가로 스크롤 방지).
- `fonts/fetch-fonts.sh` 수정: `awk | while read` 가 @font-face 블록을 줄 단위로 끊어 `src` 만 남던 버그. 블록을 한 줄로 펴서 처리, 파일명 `NotoSansKR-400-12.woff2` 꼴, 결과 검증(블록·src 수 일치), BSD sed/awk 호환, `GOOGLE_CSS=` 드라이런. 2차 수정: 주석 없는 블록(Noto Sans KR 한글 서브셋 480개)이 `IFS=탭 read` 의 선행 탭 처리에 밀려 통째로 빠지던 문제 — 줄을 통째로 읽어 직접 쪼개고, 검증을 원본 블록 수 일치 + 한글(U+D55C) 담당 블록 ≥ 굵기 수로 강화.

### 공개 전 이력 (요약)
- 0.6 경량화: dist 는 minified 만, 전체 / core / patterns / charts / auth-landing 번들, JS minify.
- 0.5 백로그 전수 구현: 날짜 범위·배너·알림 센터·승인 카드·⌘K·마법사·콤보박스·JSON 트리·인라인 편집·스켈레톤·밀도 토글·인쇄·forced-colors·키보드 조작, 대비 복구, 리터럴 색 린트, 시각 회귀 스크립트, 디자인 원칙 문서.
- 0.4 표면 깊이·타이포 스케일·폰트 self-host 키트. 0.3 레이아웃 모드 6종, 상단 바 사용자 메뉴, 외부 인증 버튼, Slack 미리보기, 아코디언, 컬러 테마, 인증 페이지 표준화. 0.2 차트·패턴·JS 프리셋. 0.1 최초.
