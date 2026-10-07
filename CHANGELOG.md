# Changelog

## 1.1.0 — 2026-10-03 · 첫 서비스(Harpoon) 적용 후 보강
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
