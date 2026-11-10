# Argus CSS Framework — Claude Code 작업 규칙

이 저장소는 여러 어드민 페이지가 공유하는 **순수 CSS 디자인 시스템**이다. 여기서 작업할 때 지켜야 할 것.

## 구조

```
css/            소스. 빌드 순서 = tokens → base → layout → components → charts → patterns → skins → utilities (core = tokens base layout components skins utilities)
dist/           build.sh 산출물(전부 minified). 직접 수정 금지. argus.min.css(전체) / core·patterns·charts·auth-landing.min.css(골라 쓰기) / themes/*.min.css / *.js
js/modules/     선택 헬퍼 소스. 10-core(테마·스킨·사이드바·탭) 15-glide(선택 알약 위치) 20-overlay(드롭다운·모달·배너·날짜·토스트닫기·확장행) 30-keyboard 40-chart-hover 50-toast. build 가 합친다
js/argus.charts.js  ApexCharts/Chart.js 프리셋
tools/          check.py 값 단언 회귀(236항목 + axe 접근성 게이트 + 클래스 커버리지, 실패 시 exit 1) · shots.py 시각 회귀 · gen_matrix.py 조합 매트릭스 생성
examples/src/   예시 페이지 소스. <!--@icons--> 는 _icons.html 스프라이트로 치환됨
examples/       build_examples.py 산출물. 직접 수정 금지. GitHub Pages 가 main 브랜치 루트를 그대로 서빙하므로 커밋 전 반드시 빌드 (루트 index.html 은 examples/ 로 리다이렉트, .nojekyll 로 _icons.html 등 밑줄 파일 유지)
docs/           디자인 원칙, 기존 어드민 리뉴얼용 Claude Code 프롬프트 키트
```

빌드: `sh build.sh && python3 tools/gen_matrix.py && python3 build_examples.py && python3 tools/check.py`. 변형(modifier)을 추가·수정했으면 `tools/gen_matrix.py` 의 해당 목록에도 넣어 매트릭스에 나오게 한다 — 조합 버그는 매트릭스에서만 보인다. css/ 에 정의한 클래스가 예시(examples/src · 매트릭스)·templates·js 어디에도 없으면 check.py 커버리지 단언이 실패한다. README 컴포넌트 목록은 **번들별 표**(core 레이아웃 / core 컴포넌트 / charts / patterns / extras)라서, 새 클래스는 그 CSS 파일이 들어가는 번들의 표에 적는다. 둘 다 돌린 뒤 커밋한다. build.sh 는 리터럴 색 린트를 먼저 돌리고 실패하면 멈춘다 (허용 목록은 build.sh 안). `npm i` 로 esbuild·lightningcss-cli 를 받으면 CSS·JS 둘 다 제대로 minify 되고, 없으면 sed 간이 압축으로 떨어진다 (둘 다 유효하지만 커밋하는 dist 는 minify 된 것으로).

## 어디에 무엇을 넣나

| 넣을 것 | 파일 |
|---|---|
| 색·간격·라운드·폰트 값 | `tokens.css` 만. 다른 파일에 리터럴 색상(hex, rgb) 쓰지 않는다. 예외: `#fff` 를 액센트 위 텍스트에 쓰는 경우 |
| 요소 리셋, 타이포 기본 | `base.css` |
| 앱 셸, 6개 레이아웃 모드(top/sidebar/rail/tabs/focus/dual), 그리드, 네비, 사이드바, 목록 패널 | `layout.css` |
| 범용 UI 조각 (버튼·카드·테이블·폼·배지…) | `components.css` |
| CSS 전용 차트, 차트 라이브러리 보정 | `charts.css` |
| 어드민 화면에서 반복되는 조합 패턴 (인증, 로그 뷰어, 스테퍼, diff…) | `patterns.css`. 거의 안 쓰는 선택 변형은 `extras/` (별도 번들) |
| 스킨(`<html data-skin="…">`) — 어느 컴포넌트에 재질을 입힐지 | `skins.css`. 셀렉터는 `:where(:root[data-skin="x"]) .ag-…` (특이도 0), 값은 tokens.css 의 `--ag-glass-*` 같은 스킨 토큰 |
| 한 줄짜리 유틸 | `utilities.css` — **최소한만.** 컴포넌트 클래스로 풀 수 있으면 유틸을 만들지 않는다 |

## 변형 선언 순서 (소스 순서가 곧 우선순위)

같은 특이도의 변형끼리는 **뒤에 선언된 것이 이긴다.** 그래서 한 블록 안에서 순서를 고정한다: ① 모양(`--sm` `--lg` `--count` `--stack` …) → ② 톤(상태 good/warn/crit/info · 액센트 · 범주 cat1~4 · inverse) → ③ 톤 × `--solid` 같은 조합. 모양 변형이 색을 건드려도 톤이 덮고, 톤은 조합이 덮는다. 이 순서를 지키면 `:not()` 체인으로 순서 문제를 때울 일이 없다 (`.ag-badge` 블록이 기준 예). 폴백 성격의 규칙(형제 간격 등)은 `:where()` 로 특이도를 0 으로 낮춰 어떤 클래스든 덮어쓸 수 있게 한다.

## 네이밍

- 접두사 `ag-`. BEM 변형: `.ag-block`, `.ag-block__element`, `.ag-block--modifier`.
- 상태는 `is-*` (`is-active`, `is-selected`, `is-invalid`, `is-collapsed`, `is-open`, `is-loading`).
- 크기는 `--sm / --md(기본, 생략) / --lg`. 톤은 `--good / --warn / --crit / --info / --accent / --accent2 / --inverse`.
- 차트 시리즈 번호는 `--1 … --4`. 5번째 범주색을 만들지 않는다 (→ "기타"로 묶고 `--ag-chart-other` 중립 회색 / `--other` 변형을 쓴다).
- 아이콘을 문맥으로 잡는 규칙은 `:is(.ag-icon, [class*="ph-"])` 로 쓴다 (svg 와 Phosphor `<i>` 동일 대우). 크기는 width/height 와 함께 `font-size`. 캐럿만 골라야 하면 `[class*="ph-caret"]`.
- 상태는 셋 다 설계한다: 빈(`.ag-empty`) · 실패(`.ag-empty--error` + 재시도) · 로딩(`.ag-table--loading` / `.ag-skeleton`). 모션은 `ag-rise` 하나, 닫힘은 즉시.
- 모양은 도구형: 라운드 토큰 6/10/12/16, 버튼 `--ag-radius-btn` 10. 알약은 칩·배지·세그먼트·네비·사용자 메뉴에만 — 새 컴포넌트에 `--ag-radius-pill` 을 쓸 땐 그 넷 중 하나인지 묻는다. 높이는 `--ag-control-h*`.
- 밀도·크기는 토큰으로: 셀 패딩 `--ag-cell-y/x`, 스탯 `--ag-text-4xl`(40)·`--ag-text-hero`(52). h1 은 28 — 콘솔은 제목보다 내용을 읽는다.
- 숫자가 든 컴포넌트에는 `font-variant-numeric: tabular-nums` 가 상속되는지 확인한다 (`.ag-num`, table, stat, badge 는 이미 적용).
- 모션은 드물게: 늘 보이는 요소(상태 점·live 표시)는 움직이지 않는다. 무한 루프는 `.ag-dot--pulse.is-live` 하나(화면당 1, 진행 중 장애)뿐 — check.py 가 센다. 새 전환은 `--ag-dur/-move/-slow` 셋 중 하나, 리터럴 ms 금지. 닫힘은 즉시. 스프링 곡선 `--ag-ease-spring` 은 유리 스킨 선택 알약 미끄러짐 · 누름 전용(1.18) — 사용자 조작에 대한 반응이라 '늘 보이는 요소는 움직이지 않는다'와 부딪히지 않는다.
- 색은 적게: 카드 아이콘 타일 상태색은 화면당 ≤2, 글자는 11px(`--ag-text-xs`) 아래 금지, `h4~h6` 은 쓰지 않는다(h1·h2·h3 + `.ag-eyebrow`). 예시 마크업에 인라인 스타일(패딩·폭·opacity·절대배치·보더색) 금지 — 필요하면 클래스·토큰을 만든다(check.py 단언).
- 오버레이는 열 때 포커스를 안으로, 닫을 때 연 요소로 돌려준다(`AG.overlay`). `<dialog>` 가 아닌 모달·드로어는 Tab 순환을 argus.js 가 한다.
- 접근성(WCAG 2.2 AA)은 토큰이 책임진다. `color:` 에는 글자 토큰만 — 액센트는 `--ag-accent-text`(채움 `--ag-accent` 는 다크 표면 위 3.9:1), 상태는 `--ag-*-text`, 분홍은 `--ag-accent-2-text`, 범주색 배경 위는 `--ag-text-on-chart`/`--ag-text-on-cat-N`. 새 토큰은 두 테마 모두 4.5:1(11px 메타도)을 토큰 주석에 적고, `opacity` 로 요소를 흐리지 않는다(안쪽 대비가 같이 깨진다). 본문 안 링크는 밑줄. 예시 마크업은 아이콘 버튼 `aria-label`, sr-only `<th>`, 페이지당 h1 하나, `nav aria-label`, 배너 `role="region"`. `tools/check.py` 의 axe 게이트(serious/critical 0, 6페이지 × 2테마)가 회귀를 막는다.

## 테마

- **앱마다 메인 색은 다를 수 있다.** 공통인 것은 표면·텍스트·간격·컴포넌트 모양·상태색·차트 범주색이고, 액센트(`--ag-accent*`, `--ag-brand-from/to`, `--ag-text-on-accent`)는 `css/themes/<color>.css` 가 덮어쓴다. 기본 제공 7종(red orange yellow green blue indigo violet)은 원색을 한 톤 눌러 맞춘 값. 새 색은 `_template.css` 를 복사해 다크·라이트 둘 다 채우고 `--ag-text-on-accent` 대비(4.5:1)를 확인한다. 프레임워크 기본 violet 은 "테마 파일이 없을 때"의 값이다.

- 다크가 기본(`:root`). 라이트는 `:root[data-theme="light"]` 블록에서 **토큰만** 재정의한다.
- 컴포넌트 규칙 안에 `[data-theme]` 셀렉터나 `prefers-color-scheme` 를 쓰지 않는다. 테마는 토큰이 처리한다.
- **스킨은 세 번째 축**(1.15, `data-skin="glass"`). 스킨 셀렉터(`[data-skin]`)는 `skins.css` 에만 쓰고 layout · components · patterns 에는 쓰지 않는다. 스킨 토큰(`--ag-glass-*`)도 다크 · 라이트 둘 다 정의하고, 유리 바탕 알파를 바꾸면 check.py 유리 대비 단언(7색 × 2테마, 메타 글자 4.5:1)을 다시 통과시킨다. 스킨을 끈 화면은 바뀌지 않아야 한다(스킨 토큰은 skins.css 에서만 참조).
- 유리 메시 색은 명도를 고정한 상대 색(1.19, `oklch(from var(--ag-brand-from) L min(c, C) h)`)이다. 메시 위에는 페이지 제목 · 브레드크럼 같은 글자가 바로 놓이므로 진하게 하고 싶으면 채도(C)를 올리고 명도(L)는 대비 단언 안에서만 움직인다 — 색 × 투명도로 섞으면 명도가 같이 올라 대비가 깨진다(1.15 ~ 1.18 라이트 4.01, check.py 픽셀 단언으로 막음). 같은 L 이어도 초록 · 파랑은 휘도가 높아 먼저 깨진다.
- 블러(`backdrop-filter`)가 걸린 요소는 ① 안쪽 `position: fixed` 의 기준 상자가 되고 ② backdrop root 가 되어 안쪽 블러가 밖을 못 본다(1.16, Chromium 실측). 그래서 블러 호스트 안에는 fixed 오버레이(모달 · 드로어 · 토스트)를 두지 않고(check.py 단언), 다른 오버레이를 품는 호스트(상단 바 · 오버레이형 모달 막)는 블러를 `::before` 에 둔다 — 단 자체 스크롤 상자(사이드바 · 메뉴 목록 · 드로어)는 `::before` 가 스크롤을 따라가므로 요소 블러.
- 흐름 안에 나란히 놓이는 블록(카드처럼 드롭다운을 품는 것) 자신에는 블러를 걸지 않는다 — 블러가 쌓임 맥락을 만들어 안쪽 메뉴가 다음 형제 밑에 가려진다(1.17 실측, check.py 단언). 뒤를 흐려야 하면 `::before`(position absolute · z-index -1)에 건다 — 블록은 쌓임 맥락이 되지 않고 흐림 층은 부모 맥락의 음수 층에 그려진다(1.20 유리 카드). 흐림이 눈에 보이려면 뒤에 무늬가 있어야 한다(격자선 `--ag-glass-grid`).
- `backdrop-filter` · `mask` · `mask-composite` 는 접두 없이 한 번만 쓴다(`mask-composite: exclude` 는 lightningcss 가 `-webkit-mask-composite: xor` 로 붙인다). lightningcss 가 `-webkit-` 을 붙이는데, 소스에 둘 다 쓰면 접두 없는 쪽이 지워져 Chrome · Firefox 에서 블러가 꺼진다(1.15 에서 확인, 1.15.1 에서 기존 3곳 수정 — check.py 가 dist 의 블록마다 짝을 검사한다).
- 새 토큰은 반드시 다크·라이트 양쪽에 정의한다. 한쪽만 있으면 빌드는 통과하지만 화면이 깨진다.
- 쉼표 목록(`box-shadow: var(--a), var(--b)`, 다중 `background`) 안에서 쓰는 토큰은 한 테마에서 끄더라도 `none` 을 넣지 않는다 — 목록 전체가 무효가 된다. 빈 그림자는 `0 0 #0000`, 빈 배경층은 `linear-gradient(transparent, transparent)` (1.5.1 교훈: `--ag-card-edge: none` 이 라이트 카드 그림자를 전부 지웠다).
- 단색 카드(`--accent/--accent2/--inverse/--cat1~4/--engine-solid`) 안의 텍스트 보정은 개별 클래스가 아니라 카드가 토큰(`--ag-text*`, `--ag-border*`, `--ag-surface-2/3/hover`)을 재정의하는 방식으로 한다. 새 컴포넌트가 토큰만 쓰면 자동으로 따라온다.
- 상태색(good/warn/crit/info)은 상태 표시 전용. 차트 시리즈·장식에 쓰지 않는다.
- 색 축은 셋: 상태(good/warn/crit/info) · 범주(cat-1..4, 엔진이 아닌 종류) · **엔진(`--ag-engine-*`, `data-engine` 훅 + `--engine` 변형)**. 엔진색 요소는 `[data-engine]` 안에서만 의미가 있고, 새 엔진은 tokens.css 다섯 토큰(다크·라이트) + components.css 훅 한 줄 + check.py 팔레트 순서. 엔진 컴포넌트 규칙은 components.css **끝** 블록에 둔다(카드·목록 기본 규칙 뒤에 와야 이긴다).
- 차트 범주색을 바꾸면 dataviz 검증(명도 밴드 다크 0.48–0.67 / 라이트 0.43–0.77, 인접쌍 CVD ΔE ≥ 8)을 두 테마 모두 다시 통과시킨다.

## 컴포넌트를 추가할 때

1. 먼저 `examples/components.html` 과 `css/` 를 grep 해서 비슷한 것이 없는지 확인한다. 변형(modifier)으로 풀리면 새 블록을 만들지 않는다.
2. 소스 파일 맨 위 섹션 주석 형식(`/* ---- 이름 ---- */` + 사용 예 HTML 한 토막)을 따른다.
3. `examples/src/components.html` 의 해당 섹션에 실제 데이터가 들어간 예시를 추가한다. lorem ipsum, "항목 1/2/3" 금지 — 실제 인스턴스 이름, 실제 지표를 쓴다.
4. 빌드 후 다크·라이트 모두 스크린샷으로 확인한다. 1440px 와 400px.
5. README 의 컴포넌트 목록에 클래스명을 추가한다.
6. `CHANGELOG.md` 에 한 줄.

**변형(modifier) 하나를 추가하거나 버그를 고칠 때도 같은 네 군데(CSS · components.html 예시 · README 목록 · CHANGELOG)를 한 커밋에 반영한다.** 서비스 적용 과정에서 "없다/깨진다" 로 들어오는 건이 많으므로, 고치고 예시·문서를 빠뜨리면 다음 서비스가 같은 문제를 다시 만난다. 서비스 저장소 쪽 Claude Code 세션은 즉흥 CSS 를 만들지 말고 프레임워크로 보고한다 (docs/renewal-prompt.md 의 CLAUDE.md 조각이 그렇게 지시한다).

## 하지 않는 것

- Tailwind/Bootstrap 유틸 흉내 (`.ag-p-4` 같은 것은 이미 있는 것만). 이 프레임워크는 컴포넌트 우선이다.
- 사이드바 하단에 사용자 프로필 넣기 — 프로필·테마·로그아웃은 상단 바 `.ag-user` 가 기준이다.
- 제공자(Google 등) 로고를 CSS/SVG 로 직접 그리기 — 공식 에셋을 서비스가 `<img>` 로 넣는다.
- `!important` — 예외: 외부 라이브러리(ApexCharts) 스타일 덮어쓰기, `[hidden]`, 숨김 유틸.
- 폰트 파일·이미지 번들링. 폰트는 서비스가 self-host 하거나 Google Fonts 링크를 건다.
- JS 의존 컴포넌트. CSS 만으로 동작해야 하고, JS 는 편의 기능(토글·탭 전환)에만 쓴다. `argus.js` 없이도 모든 컴포넌트가 정적으로 렌더돼야 한다.
- dist/ 와 examples/*.html 직접 편집.

## 버전

`build.sh` 의 `VERSION` 을 올리고 `CHANGELOG.md` 에 한 줄 적는다. 빌드가 `dist/VERSION` 을 만든다. 쓰는 쪽은 그 파일을 함께 복사해 어떤 버전을 쓰는지 기록한다.

## 커밋 전 체크

- [ ] `sh build.sh` 경고 없음, `python3 build_examples.py` 성공, **`python3 tools/check.py` 전부 통과**. 서비스에서 들어온 버그를 고쳤으면 check.py 에 단언을 하나 남긴다
- [ ] 다크·라이트 스크린샷 확인 (components.html + matrix.html 전체 + 바뀐 예시 페이지). 매트릭스에서 톤이 기본 회색으로 떨어진 셀·겹친 셀이 없어야 한다
- [ ] 400px 폭에서 가로 스크롤 없음
- [ ] 새 클래스는 README 목록 + components.html 예시에 반영
- [ ] `CHANGELOG.md` 갱신, `VERSION` 올림 (CSS 가 바뀌었으면)
- [ ] axe 게이트 통과 (check.py 에 포함 — `npm i` 로 axe-core 가 있어야 켜진다). 대비가 걸리면 컴포넌트에서 예외를 만들지 말고 토큰을 고친다
- [ ] 토큰 외 리터럴 색상 없음 (`grep -nE "#[0-9a-fA-F]{3,8}|rgb\(" css/*.css | grep -v tokens.css` 가 거의 비어 있어야 함)
