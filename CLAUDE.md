# Argus CSS Framework — Claude Code 작업 규칙

이 저장소는 여러 어드민 페이지가 공유하는 **순수 CSS 디자인 시스템**이다. 여기서 작업할 때 지켜야 할 것.

## 구조

```
css/            소스. 빌드 순서 = tokens → base → layout → components → charts → patterns → utilities
dist/           build.sh 산출물(전부 minified). 직접 수정 금지. argus.min.css(전체) / core·patterns·charts·auth-landing.min.css(골라 쓰기) / themes/*.min.css / *.js
js/modules/     선택 헬퍼 소스. 10-core(테마·사이드바·탭) 20-overlay(드롭다운·모달·배너·날짜·토스트닫기·확장행) 30-keyboard 40-chart-hover 50-toast. build 가 합친다
js/argus.charts.js  ApexCharts/Chart.js 프리셋
tools/          check.py 값 단언 회귀(72항목, 실패 시 exit 1) · shots.py 시각 회귀 · gen_matrix.py 조합 매트릭스 생성
examples/src/   예시 페이지 소스. <!--@icons--> 는 _icons.html 스프라이트로 치환됨
examples/       build_examples.py 산출물. 직접 수정 금지. GitHub Pages 가 main 브랜치 루트를 그대로 서빙하므로 커밋 전 반드시 빌드 (루트 index.html 은 examples/ 로 리다이렉트, .nojekyll 로 _icons.html 등 밑줄 파일 유지)
docs/           디자인 원칙, 기존 어드민 리뉴얼용 Claude Code 프롬프트 키트
```

빌드: `sh build.sh && python3 tools/gen_matrix.py && python3 build_examples.py && python3 tools/check.py`. 변형(modifier)을 추가·수정했으면 `tools/gen_matrix.py` 의 해당 목록에도 넣어 매트릭스에 나오게 한다 — 조합 버그는 매트릭스에서만 보인다. 둘 다 돌린 뒤 커밋한다. build.sh 는 리터럴 색 린트를 먼저 돌리고 실패하면 멈춘다 (허용 목록은 build.sh 안). `npm i` 로 esbuild·lightningcss-cli 를 받으면 CSS·JS 둘 다 제대로 minify 되고, 없으면 sed 간이 압축으로 떨어진다 (둘 다 유효하지만 커밋하는 dist 는 minify 된 것으로).

## 어디에 무엇을 넣나

| 넣을 것 | 파일 |
|---|---|
| 색·간격·라운드·폰트 값 | `tokens.css` 만. 다른 파일에 리터럴 색상(hex, rgb) 쓰지 않는다. 예외: `#fff` 를 액센트 위 텍스트에 쓰는 경우 |
| 요소 리셋, 타이포 기본 | `base.css` |
| 앱 셸, 6개 레이아웃 모드(top/sidebar/rail/tabs/focus/dual), 그리드, 네비, 사이드바, 목록 패널 | `layout.css` |
| 범용 UI 조각 (버튼·카드·테이블·폼·배지…) | `components.css` |
| CSS 전용 차트, 차트 라이브러리 보정 | `charts.css` |
| 어드민 화면에서 반복되는 조합 패턴 (인증, 로그 뷰어, 스테퍼, diff…) | `patterns.css`. 거의 안 쓰는 선택 변형은 `extras/` (별도 번들) |
| 한 줄짜리 유틸 | `utilities.css` — **최소한만.** 컴포넌트 클래스로 풀 수 있으면 유틸을 만들지 않는다 |

## 변형 선언 순서 (소스 순서가 곧 우선순위)

같은 특이도의 변형끼리는 **뒤에 선언된 것이 이긴다.** 그래서 한 블록 안에서 순서를 고정한다: ① 모양(`--sm` `--lg` `--count` `--stack` …) → ② 톤(상태 good/warn/crit/info · 액센트 · 범주 cat1~4 · inverse) → ③ 톤 × `--solid` 같은 조합. 모양 변형이 색을 건드려도 톤이 덮고, 톤은 조합이 덮는다. 이 순서를 지키면 `:not()` 체인으로 순서 문제를 때울 일이 없다 (`.ag-badge` 블록이 기준 예). 폴백 성격의 규칙(형제 간격 등)은 `:where()` 로 특이도를 0 으로 낮춰 어떤 클래스든 덮어쓸 수 있게 한다.

## 네이밍

- 접두사 `ag-`. BEM 변형: `.ag-block`, `.ag-block__element`, `.ag-block--modifier`.
- 상태는 `is-*` (`is-active`, `is-selected`, `is-invalid`, `is-collapsed`, `is-open`, `is-loading`).
- 크기는 `--sm / --md(기본, 생략) / --lg`. 톤은 `--good / --warn / --crit / --info / --accent / --accent2 / --inverse`.
- 차트 시리즈 번호는 `--1 … --4`. 5번째 범주색을 만들지 않는다 (→ "기타"로 묶고 `--ag-chart-other` 중립 회색 / `--other` 변형을 쓴다).
- 아이콘을 문맥으로 잡는 규칙은 `:is(.ag-icon, [class*="ph-"])` 로 쓴다 (svg 와 Phosphor `<i>` 동일 대우). 크기는 width/height 와 함께 `font-size`. 캐럿만 골라야 하면 `[class*="ph-caret"]`.
- 숫자가 든 컴포넌트에는 `font-variant-numeric: tabular-nums` 가 상속되는지 확인한다 (`.ag-num`, table, stat, badge 는 이미 적용).

## 테마

- **앱마다 메인 색은 다를 수 있다.** 공통인 것은 표면·텍스트·간격·컴포넌트 모양·상태색·차트 범주색이고, 액센트(`--ag-accent*`, `--ag-brand-from/to`, `--ag-text-on-accent`)는 `css/themes/<color>.css` 가 덮어쓴다. 기본 제공 7종(red orange yellow green blue indigo violet)은 원색을 한 톤 눌러 맞춘 값. 새 색은 `_template.css` 를 복사해 다크·라이트 둘 다 채우고 `--ag-text-on-accent` 대비(4.5:1)를 확인한다. 프레임워크 기본 violet 은 "테마 파일이 없을 때"의 값이다.

- 다크가 기본(`:root`). 라이트는 `:root[data-theme="light"]` 블록에서 **토큰만** 재정의한다.
- 컴포넌트 규칙 안에 `[data-theme]` 셀렉터나 `prefers-color-scheme` 를 쓰지 않는다. 테마는 토큰이 처리한다.
- 새 토큰은 반드시 다크·라이트 양쪽에 정의한다. 한쪽만 있으면 빌드는 통과하지만 화면이 깨진다.
- 단색 카드(`--accent/--accent2/--inverse`) 안의 텍스트 보정은 개별 클래스가 아니라 카드가 토큰(`--ag-text*`, `--ag-border*`, `--ag-surface-2/3/hover`)을 재정의하는 방식으로 한다. 새 컴포넌트가 토큰만 쓰면 자동으로 따라온다.
- 상태색(good/warn/crit/info)은 상태 표시 전용. 차트 시리즈·장식에 쓰지 않는다.
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
- [ ] 토큰 외 리터럴 색상 없음 (`grep -nE "#[0-9a-fA-F]{3,8}|rgb\(" css/*.css | grep -v tokens.css` 가 거의 비어 있어야 함)
