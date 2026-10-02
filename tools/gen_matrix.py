#!/usr/bin/env python3
"""examples/src/matrix.html 생성 — 변형 조합 매트릭스 (회귀용).
   조합 버그(--count × 톤, 정적 토스트 × 모달 …)는 개별 예시로는 안 잡혀서, 모든 변형을 격자로 깔아 둔다.
   python3 tools/gen_matrix.py && python3 build_examples.py"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]

TONES = ["", "good", "warn", "crit", "info", "accent", "accent2", "cat1", "cat2", "cat3", "cat4", "inverse"]
ICON = lambda n, cls="ag-icon": f'<svg class="{cls}"><use href="#i-{n}"/></svg>'

def h(title, sub="", id_=""):
    return f'<section class="ag-section" id="{id_}"><div class="ag-section__head"><h2>{title}</h2>{f"<span class=\"ag-text-sm ag-text-3\">{sub}</span>" if sub else ""}</div>\n'

def card(title, body, cols=12, extra=""):
    return f'<div class="ag-card ag-col-{cols} ag-stack {extra}"><h3 class="ag-card__title">{title}</h3>{body}</div>\n'

def row(label, cells):
    return f'<tr><th>{label}</th>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>'

def table(head, rows, cls=""):
    return f'<div class="ag-table-wrap"><table class="ag-table ag-table--matrix {cls}"><thead><tr><th></th>' + ''.join(f'<th>{x or "기본"}</th>' for x in head) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'

out = []

# ---------- 배지 ----------
def badge(tone, extra="", text="배지", dot=False):
    cls = "ag-badge" + (f" ag-badge--{tone}" if tone else "") + (f" {extra}" if extra else "")
    d = f'<span class="ag-dot{(" ag-dot--"+tone) if tone and tone not in ("inverse","accent2") else (" ag-dot--accent2" if tone=="accent2" else "")}"></span>' if dot else ""
    return f'<span class="{cls}">{d}{text}</span>'
rows = [
    row("soft", [badge(t) for t in TONES]),
    row("+ dot", [badge(t, dot=True) for t in TONES]),
    row("--sm", [badge(t, "ag-badge--sm") for t in TONES]),
    row("--lg", [badge(t, "ag-badge--lg") for t in TONES]),
    row("--solid", [badge(t, "ag-badge--solid") for t in TONES]),
    row("--solid --lg", [badge(t, "ag-badge--solid ag-badge--lg") for t in TONES]),
    row("--count", [badge(t, "ag-badge--count", "12") for t in TONES]),
    row("--count --sm", [badge(t, "ag-badge--count ag-badge--sm", "3") for t in TONES]),
    row("--count --solid", [badge(t, "ag-badge--count ag-badge--solid", "7") for t in TONES]),
]
out.append(h("배지 × 톤 × 모양", "12톤 × 9모양. 셀 하나라도 회색/기본으로 떨어지면 소스 순서 버그", "badges"))
tags = ''.join(f'<span class="ag-tag ag-tag--cat{i}"><span class="ag-tag__key">cat{i}</span><span class="ag-tag__val">값</span></span>' for i in range(1,5)) + '<span class="ag-tag"><span class="ag-tag__key">기본</span><span class="ag-tag__val">값</span><button class="ag-tag__remove" aria-label="제거">×</button></span>'
AV = ["", "good", "warn", "crit", "info", "accent2", "cat1", "cat2", "cat3", "cat4", "neutral"]
av_rows = [row(sz or "기본", [f'<span class="ag-avatar{(" ag-avatar--"+t) if t else ""}{(" "+sz) if sz else ""}">AN</span>' for t in AV]) for sz in ["ag-avatar--sm", "", "ag-avatar--lg", "ag-avatar--ring"]]
out.append('<div class="ag-grid">' + card("ag-badge", table(TONES, rows)) + card("ag-tag × 범주", f'<div class="demo">{tags}</div>', 4) + card("ag-avatar × 톤 × 크기", table(AV, av_rows), 8) + '</div></section>\n')

# ---------- 버튼 ----------
BV = ["", "primary", "outline", "ghost", "inverse", "danger", "accent2"]
def btn(v, extra="", text="버튼", icon=False, dis=False):
    cls = "ag-btn" + (f" ag-btn--{v}" if v else "") + (f" {extra}" if extra else "")
    inner = ICON("refresh") if icon else text
    return f'<button class="{cls}" type="button"{" disabled" if dis else ""}>{inner}</button>'
rows = [
    row("기본", [btn(v) for v in BV]),
    row("--sm", [btn(v, "ag-btn--sm") for v in BV]),
    row("--lg", [btn(v, "ag-btn--lg") for v in BV]),
    row("--icon", [btn(v, "ag-btn--icon", icon=True) for v in BV]),
    row("--icon --sm", [btn(v, "ag-btn--icon ag-btn--sm", icon=True) for v in BV]),
    row("--icon --square", [btn(v, "ag-btn--icon ag-btn--square", icon=True) for v in BV]),
    row("아이콘 + 텍스트", [btn(v, "", ICON("plus", "ag-icon ag-icon--sm") + "추가") for v in BV]),
    row("disabled", [btn(v, dis=True) for v in BV]),
    row("--block", [btn(v, "ag-btn--block") for v in BV]),
]
out.append(h("버튼 × 변형 × 크기 × 상태", "", "buttons"))
out.append('<div class="ag-grid">' + card("ag-btn", table(BV, rows)) +
    card("ag-btn-group · ag-segmented · ag-chip", '''<div class="demo">
<div class="ag-btn-group"><button class="ag-btn ag-btn--outline ag-btn--sm">일</button><button class="ag-btn ag-btn--outline ag-btn--sm is-active">주</button><button class="ag-btn ag-btn--outline ag-btn--sm">월</button></div>
<div class="ag-segmented"><button class="ag-segmented__item is-active">전체</button><button class="ag-segmented__item">prod</button><button class="ag-segmented__item">stg</button></div>
<div class="ag-segmented ag-segmented--sm"><button class="ag-segmented__item is-active">A</button><button class="ag-segmented__item">B</button></div>
<span class="ag-chip">칩</span><span class="ag-chip is-active">선택</span><button class="ag-chip" type="button">버튼 칩 ×</button>
</div>''') + '</div></section>\n')

# ---------- 카드 · 타일 ----------
CV = ["", "accent", "accent2", "inverse", "elevated", "interactive", "sm"]
def cardv(v):
    cls = "ag-card" + (f" ag-card--{v}" if v else "")
    return f'<div class="{cls}"><div class="ag-card__head"><h3 class="ag-card__title">{v or "기본"}</h3><span class="ag-badge ag-badge--sm">탭</span></div><div class="ag-card__body"><p class="ag-text-sm">본문 두 줄. 카드 안 간격은 gap 이 책임진다.</p><div class="ag-stat ag-stat--sm"><span class="ag-stat__label">값</span><span class="ag-stat__value">42</span></div></div></div>'
out.append(h("카드 · 타일", "변형별 head/body/stat 포함. a / button 카드는 섹션 카드와 간격이 같아야 함", "cards"))
out.append('<div class="ag-grid">' + ''.join(f'<div class="ag-col-3">{cardv(v)}</div>' for v in CV) +
    f'<div class="ag-col-3"><a class="ag-card ag-card--interactive" href="#"><div class="ag-card__head"><h3 class="ag-card__title">a.ag-card</h3>{ICON("arrow-up-right")}</div><p class="ag-text-sm">링크 카드 — 밑줄 없음, 왼쪽 정렬</p></a></div>'
    f'<div class="ag-col-3"><button class="ag-card ag-card--interactive is-selected" type="button"><div class="ag-card__head"><h3 class="ag-card__title">button.ag-card</h3><span class="ag-badge ag-badge--sm ag-badge--accent">선택</span></div><p class="ag-text-sm">버튼 카드 is-selected</p></button></div>'
    '<div class="ag-col-12 ag-stack"><h3 class="ag-card__title">ag-tile</h3><div class="ag-grid">'
    '<div class="ag-col-3 ag-stack ag-stack--sm"><div class="ag-tile"><span class="ag-tile__label"><span class="ag-dot ag-dot--good"></span>기본</span><span class="ag-badge ag-badge--count">4</span></div><div class="ag-tile ag-tile--inverse"><span class="ag-tile__label">--inverse</span><span class="ag-badge ag-badge--count">2</span></div></div>'
    '<div class="ag-col-3"><div class="ag-tile ag-tile--stack"><small>--stack</small><strong>35일</strong></div></div>'
    '<div class="ag-col-3"><div class="ag-tile ag-tile--stack ag-tile--inverse"><small>--stack --inverse</small><strong>10/3 02:00</strong></div></div>'
    '<div class="ag-col-3"><div class="ag-tile ag-tile--stack"><small>--stack + progress</small><strong>62%</strong><div class="ag-progress ag-progress--sm ag-w-full"><div class="ag-progress__bar" style="width:62%"></div></div></div></div>'
    '</div></div>'
    + card("ag-quick-actions (빠른 작업 2열 격자)", f'''<div class="ag-quick-actions">
<a class="ag-quick-action" href="#"><span class="ag-quick-action__icon ag-quick-action__icon--1">{ICON("database")}</span>스냅샷 생성</a>
<a class="ag-quick-action" href="#"><span class="ag-quick-action__icon ag-quick-action__icon--2">{ICON("shield")}</span>권한 발급</a>
<a class="ag-quick-action" href="#"><span class="ag-quick-action__icon ag-quick-action__icon--3">{ICON("activity")}</span>슬로우 쿼리</a>
<a class="ag-quick-action" href="#"><span class="ag-quick-action__icon ag-quick-action__icon--4">{ICON("refresh")}</span>파라미터 적용</a>
</div>''', 6)
    + card("ag-grid--auto (자동 채움) · ag-col-9 + ag-col-3 · ag-spacer", '''<div class="ag-grid ag-grid--auto"><div class="ag-tile">auto 1</div><div class="ag-tile">auto 2</div><div class="ag-tile">auto 3</div><div class="ag-tile">auto 4</div></div>
<div class="ag-grid"><div class="ag-tile ag-col-9">col-9</div><div class="ag-tile ag-col-3">col-3</div></div>
<div class="ag-row"><span class="ag-badge">왼쪽</span><span class="ag-spacer"></span><span class="ag-badge">ag-spacer 로 밀린 오른쪽</span></div>''', 6)
    + '</div></section>\n')

# ---------- 입력 ----------
out.append(h("입력 × 크기 × 상태", "", "inputs"))
def field(label, inner, cls=""):
    return f'<div class="ag-field {cls}"><label class="ag-label">{label}</label>{inner}<span class="ag-hint">힌트</span></div>'
inputs = (
    field("기본", '<input class="ag-input" placeholder="placeholder">') +
    field("--sm", '<input class="ag-input ag-input--sm" value="small">') +
    field("--lg", '<input class="ag-input ag-input--lg" value="large">') +
    field("--mono", '<input class="ag-input ag-input--mono" value="db.r6g.4xlarge">') +
    field("--pill", '<input class="ag-input ag-input--pill" value="pill">') +
    field("is-invalid", '<input class="ag-input" value="72G">', "is-invalid") +
    field("disabled", '<input class="ag-input" value="읽기 전용" disabled>') +
    field("select", '<select class="ag-select"><option>MySQL 8.0</option><option>PostgreSQL 15</option></select>') +
    field("select --sm --pill", '<select class="ag-select ag-select--sm ag-select--pill"><option>7일</option></select>') +
    field("input-group (앞 아이콘)", f'<div class="ag-input-group">{ICON("search")}<input class="ag-input" placeholder="검색"></div>') +
    field("input-group--end (뒤 버튼)", f'<div class="ag-input-group ag-input-group--end"><input class="ag-input" value="JBSW Y3DP"><span class="ag-input-group__end"><button class="ag-btn ag-btn--icon ag-btn--ghost ag-btn--sm" type="button" aria-label="복사">{ICON("copy","ag-icon ag-icon--sm")}</button></span></div>') +
    field("input-group 양끝 (아이콘 + --end)", f'<div class="ag-input-group ag-input-group--end">{ICON("search")}<input class="ag-input" placeholder="추출 잡 검색"><span class="ag-input-group__end"><kbd>⌘K</kbd></span></div>') +
    field("secret-field (마스킹)", f'<div class="ag-secret-field"><input class="ag-input is-masked" value="s3cr3t-token-value"><button class="ag-btn ag-btn--icon ag-btn--outline" type="button" aria-label="보기">{ICON("eye")}</button></div>') +
    field("textarea", '<textarea class="ag-textarea" rows="2">여러 줄</textarea>', "ag-field--full")
)
out.append('<div class="ag-grid">' + card("ag-input · ag-select · ag-textarea (form-grid--4)", f'<div class="ag-form-grid ag-form-grid--4">{inputs}</div>') +
    card("form-grid--2 + --full · form-grid--3 + --span2 (Host 2칸 : Port 1칸)", '<div class="ag-form-grid ag-form-grid--2">' + field("A", '<input class="ag-input">') + field("B", '<input class="ag-input">') + field("--full", '<input class="ag-input">', "ag-field--full") + '</div><div class="ag-form-grid ag-form-grid--3 ag-mt-4">' + field("Host (--span2)", '<input class="ag-input ag-input--mono" value="order-db.cluster-abc.ap-northeast-2.rds.amazonaws.com">', "ag-field--span2") + field("Port", '<input class="ag-input ag-input--mono" value="3306">') + field("--span3 = 전체", '<input class="ag-input">', "ag-field--span3") + '</div>', 6) +
    card("체크 · 라디오 · 스위치 × 상태", '''<div class="ag-cluster ag-gap-4">
<label class="ag-check"><input type="checkbox" checked><span>체크</span></label><label class="ag-check"><input type="checkbox"><span>해제</span></label><label class="ag-check"><input type="checkbox" disabled><span>비활성</span></label>
<label class="ag-check"><input type="radio" name="m" checked><span>라디오</span></label><label class="ag-check"><input type="radio" name="m"><span>라디오</span></label>
<label class="ag-switch"><input type="checkbox" checked><span class="ag-switch__track"></span>켜짐</label><label class="ag-switch"><input type="checkbox"><span class="ag-switch__track"></span>꺼짐</label><label class="ag-switch"><input type="checkbox" disabled><span class="ag-switch__track"></span>비활성</label>
</div>''', 6) + '</div></section>\n')

# ---------- 피드백 ----------
FT = ["good", "warn", "crit", "info"]
alerts = ''.join(f'<div class="ag-alert ag-alert--{t}">{ICON("alert")}<div><div class="ag-alert__title">{t}</div>설명 한 줄</div></div>' for t in FT) + f'<div class="ag-alert">{ICON("info")}<div><div class="ag-alert__title">기본</div>톤 없음</div></div>'
toasts = ''.join(f'<div class="ag-toast ag-toast--{t}"><span class="ag-dot ag-dot--{t}" style="margin-top:6px"></span><div class="ag-flex-1"><strong>{t}</strong><br>본문</div><button class="ag-btn ag-btn--icon ag-btn--ghost ag-btn--sm" data-ag-toast-close aria-label="닫기">×</button></div>' for t in FT) + '<div class="ag-toast"><span class="ag-dot" style="margin-top:6px"></span><div class="ag-flex-1"><strong>기본</strong><br>톤 없음</div></div>'
banners = ''.join(f'<div class="ag-banner ag-banner--{t}">{ICON("alert")}<div class="ag-banner__text"><strong>{t}</strong>배너 본문</div><button class="ag-banner__close" aria-label="닫기">×</button></div>' for t in FT) + '<div class="ag-banner ag-banner--accent"><div class="ag-banner__text"><strong>accent</strong></div></div><div class="ag-banner ag-banner--readonly"><div class="ag-banner__text"><strong>readonly</strong> 읽기 전용 모드</div></div>'
progress = ''.join(f'<div class="ag-row"><span class="ag-text-xs ag-text-3" style="width:90px">{v or "기본"}</span><div class="ag-progress ag-w-full{(" ag-progress--"+v) if v else ""}"><div class="ag-progress__bar" style="width:{w}%"></div></div></div>' for v, w in [("", 40), ("sm", 55), ("lg", 70), ("good", 90), ("warn", 62), ("crit", 92), ("accent2", 35)]) + '<div class="ag-row"><span class="ag-text-xs ag-text-3" style="width:90px">stacked</span><div class="ag-progress ag-progress--stacked ag-w-full"><div class="ag-progress__bar" style="width:40%"></div><div class="ag-progress__bar" style="width:25%;background:var(--ag-chart-2)"></div><div class="ag-progress__bar" style="width:15%;background:var(--ag-chart-3)"></div></div></div>'
deltas = f'<span class="ag-delta ag-delta--up">{ICON("trend-up","ag-icon ag-icon--sm")}+12%</span><span class="ag-delta ag-delta--down">{ICON("trend-down","ag-icon ag-icon--sm")}-38%</span><span class="ag-delta ag-delta--flat">0%</span><span class="ag-delta ag-delta--inline ag-delta--up">+3.2%</span><span class="ag-delta ag-delta--inline ag-delta--down">-1.1%</span><span class="ag-delta ag-delta--inline ag-delta--flat">±0</span>'
dots = ''.join(f'<span class="ag-dot ag-dot--{t}"></span>' for t in ["good","warn","crit","info","accent","accent2","cat1","cat2","cat3","cat4"]) + '<span class="ag-dot ag-dot--crit ag-dot--pulse"></span><span class="ag-dot"></span>'
out.append(h("피드백 × 톤", "alert · toast · banner · progress · delta · dot · spinner · skeleton", "feedback"))
out.append('<div class="ag-grid">' + card("ag-alert", f'<div class="ag-stack ag-stack--sm">{alerts}</div>', 6) + card("ag-toast (--static 스택)", f'<div class="ag-toast-stack ag-toast-stack--static">{toasts}</div>', 6) +
    card("ag-banner (--sticky 는 상단 고정이라 여기선 생략)", f'<div class="ag-stack ag-stack--sm">{banners}</div>') +
    card("ag-progress", f'<div class="ag-stack ag-stack--sm">{progress}</div>', 6) +
    card("ag-delta · ag-dot · ag-spinner · ag-skeleton", f'<div class="demo">{deltas}</div><div class="demo">{dots}</div><div class="demo"><span class="ag-spinner ag-spinner--sm"></span><span class="ag-spinner"></span><span class="ag-spinner ag-spinner--lg"></span><button class="ag-btn ag-btn--primary is-loading"><span class="ag-spinner ag-spinner--sm"></span>저장 중</button></div><div class="ag-stack ag-stack--sm"><span class="ag-skeleton" style="width:60%"></span><span class="ag-skeleton" style="width:85%"></span><div class="ag-skeleton-rows" style="--rows:3"></div></div>', 6) +
    card("빈 상태 변형", f'''<div class="ag-grid">
<div class="ag-col-4"><div class="ag-notif" style="position:static;width:100%;max-width:100%;min-width:0"><div class="ag-notif__head"><strong>알림</strong></div><div class="ag-notif__empty">새 알림이 없습니다</div></div></div>
<div class="ag-col-4"><div class="ag-cmdk" style="position:static;transform:none;width:100%"><div class="ag-cmdk__input">{ICON("search")}<input value="zzz" aria-label="검색"><kbd>esc</kbd></div><div class="ag-cmdk__empty">"zzz" 에 맞는 결과 없음</div></div></div>
<div class="ag-col-4"><div class="ag-combobox is-open" style="position:static"><input class="ag-input" value="qqq" aria-label="검색"><div class="ag-combobox__list" style="position:static"><div class="ag-combobox__empty">일치하는 인스턴스 없음</div></div></div></div>
</div>''') + '</div></section>\n')

# ---------- 차트 ----------
spark_d = "M0,20 L10,18 L20,22 L30,12 L40,14 L50,6 L60,10 L70,8 L80,16 L90,18 L100,20"
def spark(cls):
    return f'<svg class="ag-spark {cls}" viewBox="0 0 100 28" preserveAspectRatio="none" aria-hidden="true"><path class="ag-spark__area" d="{spark_d} L100,28 L0,28 Z"/><path class="ag-spark__line" d="{spark_d}"/></svg>'
heat = lambda cls="": f'<div class="ag-heatmap {cls}" style="--ag-heat-cols: 10">' + ''.join(f'<i class="ag-heat{" ag-heat--empty" if i%7==3 else ""}" style="--l: {((i*37)%10)/10:.1f}"></i>' for i in range(30)) + '</div>'
gauges = ''.join(f'<div class="ag-gauge{(" ag-gauge--"+t) if t else ""}" style="--p: {p}"><strong>{p}%</strong><span>{t or "기본"}</span></div>' for t, p in [("", 45), ("good", 32), ("warn", 71), ("crit", 92)])
cols = '<div class="ag-cols" style="--ag-cols-max: 100; --ag-cols-h: 120px">' + ''.join(f'<div class="ag-cols__col" style="--v: {v}"><span class="ag-cols__bar ag-cols__bar--{i%4+1}"></span><span class="ag-cols__label">s{i%4+1}</span></div>' for i, v in enumerate([40, 70, 55, 90, 30, 65, 80, 50])) + '</div>'
bars = lambda cls="": f'<div class="ag-bars {cls}" style="--ag-bars-label: 70px">' + ''.join(f'<div class="ag-bars__row"><span class="ag-bars__label">{l}</span><div class="ag-bars__track"><div class="ag-bars__seg ag-bars__seg--{s}" style="width:{w}%"></div><div class="ag-bars__seg ag-bars__seg--muted" style="width:{100-w-5}%"></div></div><span class="ag-bars__value">{w}</span></div>' for l, s, w in [("seg--1", "1", 62), ("seg--2", "2", 45), ("seg--3", "3", 30), ("seg--4", "4", 78), ("seg--accent", "accent", 50)]) + '</div>'
svgchart = lambda hcls: f'<div class="ag-chart {hcls}"><svg viewBox="0 0 300 100" preserveAspectRatio="none" style="width:100%;height:100%">' + ''.join(f'<rect class="ag-chart__bar ag-chart__bar--{i+1}" x="{10+i*40}" y="{60-i*10}" width="24" height="{40+i*10}"/>' for i in range(4)) + '<path class="ag-chart__area ag-chart__area--1" d="M170,80 L200,50 L230,60 L260,30 L290,45 L290,100 L170,100Z"/><path class="ag-chart__area ag-chart__area--2" d="M170,90 L200,70 L230,75 L260,55 L290,65 L290,100 L170,100Z"/>' + ''.join(f'<path class="ag-chart__line ag-chart__line--{i+1}" d="M170,{80-i*12} L200,{50-i*8} L230,{60-i*10} L260,{30-i*5} L290,{45-i*9}"/>' for i in range(4)) + '</svg></div>'
stat_icons = ''.join(f'<div class="ag-card ag-card--sm ag-stat-card"><div class="ag-stat-card__head"><span class="ag-stat-card__icon{(" ag-stat-card__icon--"+t) if t else ""}">{ICON("activity")}</span><span class="ag-delta ag-delta--inline ag-delta--up">+1%</span></div><div class="ag-stat ag-stat--sm"><span class="ag-stat__value">24</span><span class="ag-stat__label">icon--{t or "기본(accent)"}</span></div><div class="ag-stat-card__foot"><span>최근 24h</span></div></div>' for t in ["", "good", "warn", "crit", "info", "accent2"])
bubbles = ''.join(f'<div class="ag-bubble ag-bubble--{i}" style="width:{w}px;font-size:{w//4}px"><strong>{p}%</strong><span>b{i}</span></div>' for i, w, p in [(1, 110, 58), (2, 90, 33), (3, 70, 9), ("hatch", 60, 4)])
out.append(h("차트 × 시리즈 × 크기 × 톤", "CSS 전용 차트의 모든 시리즈 번호·톤·크기 변형", "charts"))
out.append('<div class="ag-grid">' +
    card("ag-chart 높이 --h-sm / --h-md / --h-lg · bar/line/area 1~4", f'<div class="ag-grid"><div class="ag-col-4">{svgchart("ag-chart--h-sm")}<span class="ag-text-xs ag-text-3">--h-sm 180px</span></div><div class="ag-col-4">{svgchart("ag-chart--h-md")}<span class="ag-text-xs ag-text-3">--h-md</span></div><div class="ag-col-4">{svgchart("ag-chart--h-lg")}<span class="ag-text-xs ag-text-3">--h-lg</span></div></div>') +
    card("ag-donut · --sm / 기본 / --lg", '<div class="demo ag-items-end">' + ''.join(f'<div class="ag-donut {c}" style="--ag-donut: var(--ag-chart-1) 0 57%, transparent 57% 58%, var(--ag-chart-2) 58% 90%, transparent 90% 91%, var(--ag-chart-3) 91% 100%"><div class="ag-donut__center"><strong>186</strong><span>{c or "기본"}</span></div></div>' for c in ["ag-donut--sm", "", "ag-donut--lg"]) + '</div>', 6) +
    card("ag-gauge 톤", f'<div class="demo ag-items-end">{gauges}</div>', 6) +
    card("ag-cols (bar 1~4)", cols, 4) + card("ag-bars (seg 1~4 · accent · muted) + --thin", bars() + '<div class="ag-mt-3">' + bars("ag-bars--thin") + '</div>', 4) +
    card("ag-heatmap 기본 / --crit / heat--empty", heat() + '<div class="ag-mt-3">' + heat("ag-heatmap--crit") + '</div>', 4) +
    card("ag-spark 크기 × 톤 (--sm / 기본 / --lg · --2 / --good / --crit)", '<div class="ag-grid">' + ''.join(f'<div class="ag-col-2">{spark(c)}<span class="ag-text-xs ag-text-3">{c or "기본"}</span></div>' for c in ["ag-spark--sm", "", "ag-spark--lg", "ag-spark--2", "ag-spark--good", "ag-spark--crit"]) + '</div>') +
    card("ag-stat-card 아이콘 톤", f'<div class="ag-grid ag-grid--auto">{stat_icons}</div>') +
    card("ag-bubble 1~3 · hatch", f'<div class="demo ag-items-end">{bubbles}</div>') + '</div></section>\n')

# ---------- 패턴 잔여 변형 ----------
out.append(h("패턴 변형", "개별 카탈로그에 없던 변형들", "patterns"))
out.append('<div class="ag-grid">' +
    card("ag-otp 기본 / --sm", '<div class="ag-otp" aria-label="OTP">' + ''.join(f'<input class="ag-otp__cell{" is-filled" if i<3 else ""}" maxlength="1" value="{"482"[i] if i<3 else ""}" aria-label="자리 {i+1}">' for i in range(6)) + '</div><div class="ag-otp ag-otp--sm ag-mt-3" aria-label="OTP small">' + ''.join(f'<input class="ag-otp__cell" maxlength="1" aria-label="자리 {i+1}">' for i in range(6)) + '</div>', 6) +
    card("ag-daterange 기본 / --stack", '<div class="ag-daterange"><div class="ag-daterange__inputs"><input class="ag-input ag-input--sm" type="date" value="2026-09-01" aria-label="시작"><span class="ag-daterange__sep">–</span><input class="ag-input ag-input--sm" type="date" value="2026-09-30" aria-label="끝"></div><div class="ag-daterange__presets"><button class="ag-chip ag-chip--sm" data-ag-days="7">7일</button><button class="ag-chip ag-chip--sm is-active" data-ag-days="30">30일</button></div></div><div class="ag-daterange ag-daterange--stack ag-mt-4"><div class="ag-daterange__inputs"><input class="ag-input ag-input--sm" type="date" aria-label="시작"><span class="ag-daterange__sep">–</span><input class="ag-input ag-input--sm" type="date" aria-label="끝"></div><div class="ag-daterange__presets"><button class="ag-chip ag-chip--sm" data-ag-days="7">7일</button><button class="ag-chip ag-chip--sm" data-ag-days="30">30일</button></div></div>', 6) +
    card("ag-approval + __meta", f'<div class="ag-approval"><div class="ag-approval__head"><span class="ag-avatar ag-avatar--sm">SO</span><div class="ag-approval__who"><strong>Sophie</strong><span>데이터팀 · 2시간 전</span></div><span class="ag-badge ag-badge--warn ag-badge--sm">대기</span></div><div class="ag-approval__body">analytics-pg-ro 읽기 계정 발급 요청</div><div class="ag-approval__meta"><span>{ICON("database","ag-icon ag-icon--sm")} analytics-pg-ro</span><span>{ICON("clock","ag-icon ag-icon--sm")} 30일</span><span>INFRA-2051</span></div><div class="ag-approval__actions"><button class="ag-btn ag-btn--sm ag-btn--primary">승인</button><button class="ag-btn ag-btn--sm ag-btn--outline">반려</button></div></div>', 6) +
    card("ag-log --fill (부모 높이 채움) · __body--nowrap", '<div style="height:160px;display:flex"><div class="ag-log ag-log--fill" style="flex:1"><div class="ag-log__head"><span class="ag-dot ag-dot--good ag-dot--pulse"></span>backup.log</div><pre class="ag-log__body ag-log__body--nowrap"><span class="ag-log__line is-info">[02:00:01] snapshot start order-db-writer — 이 줄은 길어서 nowrap 이면 가로 스크롤이 생긴다 아주 길게 아주 길게 아주 길게 아주 길게</span>\n<span class="ag-log__line">[02:03:40] 1.2 TiB copied</span>\n<span class="ag-log__line is-warn">[02:05:12] throttled</span>\n<span class="ag-log__line is-good">[02:06:12] done</span></pre></div></div>', 6) +
    card("사이드바 그룹 --sub (3단계)", f'<nav class="ag-sidebar" style="position:static;height:auto;width:240px;border:1px solid var(--ag-border);border-radius:var(--ag-radius-lg)"><div class="ag-sidebar__group" aria-label="메뉴"><a class="ag-sidebar__item is-active" href="#">{ICON("database")}<span>데이터베이스</span></a><div class="ag-sidebar__group ag-sidebar__group--sub"><a class="ag-sidebar__item" href="#"><span>인스턴스</span></a><a class="ag-sidebar__item" href="#"><span>계정 / 권한</span></a><a class="ag-sidebar__item" href="#"><span>백업</span></a></div><a class="ag-sidebar__item" href="#">{ICON("cloud")}<span>EC2</span></a></div></nav>', 4) +
    card("ag-pane-item + __tags", '<div class="ag-pane" style="position:static;width:auto;border:1px solid var(--ag-border);border-radius:var(--ag-radius-lg)"><a class="ag-pane-item is-active" href="#"><div class="ag-pane-item__top"><span class="ag-dot ag-dot--crit"></span>ALM-2037<time>09:48</time></div><div class="ag-pane-item__title">ebs-wms-03 사용률 91%</div><div class="ag-pane-item__snippet">증설 요청 생성됨.</div><div class="ag-pane-item__tags"><span class="ag-badge ag-badge--sm ag-badge--cat2">PostgreSQL</span><span class="ag-badge ag-badge--sm">prod</span><span class="ag-badge ag-badge--sm">tier-0</span></div></a></div>', 4) +
    card("ag-notif-btn __count / __dot", f'<div class="demo"><button class="ag-btn ag-btn--icon ag-btn--outline ag-notif-btn" aria-label="알림 3개">{ICON("bell")}<span class="ag-notif-btn__count">3</span></button><button class="ag-btn ag-btn--icon ag-btn--outline ag-notif-btn" aria-label="새 알림">{ICON("bell")}<span class="ag-notif-btn__dot"></span></button></div>', 4) +
    card("ag-slack 블록 타입 전수", '''<div class="ag-slack ag-slack--static"><div class="ag-slack__title">미리보기</div><div class="ag-slack__channel">#<strong>infra-db-alert</strong><span class="ag-text-3">· 공지 채널</span></div>
<div class="ag-slack__message"><div class="ag-slack__avatar"></div><div class="ag-slack__bubble"><div class="ag-slack__meta"><span class="ag-slack__name">Notifier</span><span class="ag-slack__tag">APP</span><span class="ag-slack__time">14:02</span></div>
<div class="ag-slack__block ag-slack__header">header 블록</div>
<div class="ag-slack__block ag-slack__section">section · <span class="ag-slack__mention">@here</span> · <code class="ag-slack__inline-code">inline</code><img class="ag-slack__accessory" alt="" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 80'%3E%3Crect width='80' height='80' rx='8' fill='%237c6cff'/%3E%3C/svg%3E"></div>
<div class="ag-slack__divider"></div>
<div class="ag-slack__block ag-slack__fields"><div class="ag-slack__field"><strong>대상</strong>order-db</div><div class="ag-slack__field"><strong>시각</strong>02:00</div></div>
<div class="ag-slack__block"><pre class="ag-slack__code">SET GLOBAL innodb_buffer_pool_size = 56G;</pre></div>
<div class="ag-slack__block ag-slack__image-block"><div class="ag-slack__image-title">image 블록</div><img class="ag-slack__image" alt="" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 320 80'%3E%3Crect width='320' height='80' fill='%2321222d'/%3E%3C/svg%3E"></div>
<div class="ag-slack__block ag-slack__context"><span class="ag-slack__ctx-text">context · <span class="ag-slack__placeholder">{{placeholder}}</span></span></div>
<div class="ag-slack__actions"><button class="ag-slack__btn ag-slack__btn--primary">승인</button><button class="ag-slack__btn ag-slack__btn--danger">반려</button><button class="ag-slack__btn">보기</button></div>
<div class="ag-slack__unknown">unknown block type: rich_text_v3</div>
</div></div>
<div class="ag-slack__error">error — <code>blocks[3]</code> 파싱 실패</div>
<div class="ag-slack__empty">empty — 미리볼 블록이 없습니다</div></div>''', 6) +
    card("레이아웃 모드 세부 변형", '<p class="ag-text-sm ag-text-2">모드 전환은 <a href="layouts.html">레이아웃 페이지</a>에서. 여기엔 모드에 붙는 세부 변형만 적어 둔다.</p><div class="ag-table-wrap"><table class="ag-table ag-table--matrix"><tbody><tr><th>ag-app--focus-wide</th><td>focus 모드 본문 폭 720 → 1040px (넓은 폼·비교 화면)</td></tr><tr><th>ag-app--dual-nosidebar</th><td>dual 모드에서 사이드바 없이 목록 패널 + 상세만</td></tr><tr><th>ag-topbar__row--underline</th><td>tabs 모드 네비 행을 캡슐 대신 밑줄 탭으로</td></tr><tr><th>ag-banner--sticky</th><td>배너를 상단 고정 (z 41, 상단 바 바로 위)</td></tr><tr><th>ag-editor</th><td>EasyMDE 같은 외부 에디터 래퍼 — 툴바·테두리를 토큰 색으로</td></tr><tr><th>ag-scrollbar-hide</th><td>스크롤바 숨김 (가로 칩 스크롤 등)</td></tr></tbody></table></div><div class="ag-scrollbar-hide ag-overflow-x ag-mt-3" style="display:flex;gap:8px;width:100%">' + ''.join(f'<span class="ag-chip">칩 {i}</span>' for i in range(1,16)) + '</div>', 6) +
    card("인쇄 전용 · 모달 크기", f'<p class="ag-text-sm ag-text-2"><code>.ag-print-only</code> 는 화면에서 숨고 인쇄에서만 나온다 (아래 줄은 보이면 안 됨): <span class="ag-print-only">인쇄 전용 텍스트</span></p><div class="demo"><button class="ag-btn ag-btn--outline" data-ag-open="mx-lg">overlay --lg (860px)</button><button class="ag-btn ag-btn--outline" data-ag-open="mx-xl">overlay --xl (1100px)</button></div>', 6) +
    '</div></section>\n')

# ---------- 유틸리티 ----------
UT = [("텍스트 크기", ["ag-text-xs","ag-text-sm","ag-text-md","ag-text-lg","ag-text-xl","ag-text-2xl"]),
      ("텍스트 색", ["ag-text-1","ag-text-2","ag-text-3","ag-text-good","ag-text-warn","ag-text-crit","ag-text-info","ag-text-accent","ag-text-accent2"]),
      ("굵기·변형", ["ag-fw-400","ag-fw-500","ag-fw-600","ag-fw-700","ag-upper","ag-eyebrow","ag-nowrap","ag-truncate"]),
      ("정렬", ["ag-text-left","ag-text-center","ag-text-right"]),
      ("표면·보더·라운드", ["ag-bg-surface","ag-bg-surface-2","ag-bg-surface-3","ag-border","ag-border-t","ag-border-b","ag-radius-md","ag-radius-lg","ag-radius-xl","ag-radius-pill","ag-shadow-md"]),
      ("간격", ["ag-m-0","ag-mt-1","ag-mt-2","ag-mt-3","ag-mt-4","ag-mt-6","ag-mb-2","ag-mb-4","ag-p-0","ag-p-4","ag-p-6"])]
ut_rows = ''.join(f'<tr><th>{g}</th><td><div class="demo">' + ''.join(f'<span class="{c}" style="border:1px dashed var(--ag-border);padding:2px 6px">{c}</span>' for c in cs) + '</div></td></tr>' for g, cs in UT)
flex_demo = ('<div class="demo ag-items-start">'
    '<div class="ag-flex ag-items-center ag-gap-2" style="border:1px dashed var(--ag-border);padding:4px"><span class="ag-badge">ag-flex</span><span class="ag-badge">items-center</span><span class="ag-badge">gap-2</span></div>'
    '<div class="ag-inline-flex ag-items-baseline ag-gap-3" style="border:1px dashed var(--ag-border);padding:4px"><span class="ag-text-xl">inline-flex</span><span class="ag-text-xs">baseline gap-3</span></div>'
    '<div class="ag-flex ag-col ag-gap-1" style="border:1px dashed var(--ag-border);padding:4px"><span class="ag-badge">ag-col</span><span class="ag-badge">gap-1</span></div>'
    '<div class="ag-flex ag-justify-center ag-gap-5" style="border:1px dashed var(--ag-border);padding:4px;width:200px"><span class="ag-badge">justify-center</span><span class="ag-badge">gap-5</span></div>'
    '<div class="ag-flex ag-justify-end ag-gap-6" style="border:1px dashed var(--ag-border);padding:4px;width:200px"><span class="ag-badge">justify-end</span></div>'
    '<div class="ag-flex ag-items-start ag-wrap ag-gap-8" style="border:1px dashed var(--ag-border);padding:4px;width:160px"><span class="ag-badge">items-start</span><span class="ag-badge">wrap gap-8</span></div>'
    '<div class="ag-flex ag-justify-between ag-w-full" style="border:1px dashed var(--ag-border);padding:4px"><span class="ag-badge">justify-between</span><span class="ag-badge">w-full</span></div>'
    '<div class="ag-relative ag-overflow-auto ag-h-full" style="border:1px dashed var(--ag-border);padding:4px;height:48px;width:160px"><div style="height:120px"><span class="ag-badge">overflow-auto · h-full · relative</span></div></div>'
    '<div class="ag-overflow-x" style="border:1px dashed var(--ag-border);padding:4px;width:160px"><div style="width:400px"><span class="ag-badge">overflow-x (가로 스크롤)</span></div></div>'
    '<div class="ag-scroll-y ag-scroll-y--sm" style="border:1px dashed var(--ag-border);padding:4px;width:160px"><div style="height:400px"><span class="ag-badge">scroll-y--sm</span></div></div>'
    '<div class="ag-scroll-y ag-scroll-y--md" style="border:1px dashed var(--ag-border);padding:4px;width:120px"><div style="height:600px"><span class="ag-badge">--md</span></div></div>'
    '<div class="ag-scroll-y ag-scroll-y--lg" style="border:1px dashed var(--ag-border);padding:4px;width:120px"><div style="height:900px"><span class="ag-badge">--lg</span></div></div>'
    '<span class="ag-hidden">ag-hidden (보이면 안 됨)</span><span class="ag-sr-only">ag-sr-only (스크린리더 전용)</span>'
    '<span class="ag-badge ag-hide-sm">hide-sm (≤720 숨김)</span><span class="ag-badge ag-hide-md">hide-md (≤960)</span><span class="ag-badge ag-hide-lg">hide-lg (≤1200)</span><span class="ag-badge ag-show-sm">show-sm (≤720 만)</span>'
    '<span class="ag-badge ag-only-dark">only-dark</span><span class="ag-badge ag-only-light">only-light</span><span class="ag-badge ag-ml-auto">ml-auto</span><span class="ag-badge ag-min-0 ag-flex-1">min-0 flex-1</span><span class="ag-badge ag-mt-auto">mt-auto</span>'
    '</div>')
out.append(h("유틸리티 전수", "utilities.css 의 모든 클래스. 점선 상자는 데모용", "utils"))
out.append('<div class="ag-grid">' + card("텍스트·표면·간격", f'<div class="ag-table-wrap"><table class="ag-table ag-table--matrix"><tbody>{ut_rows}</tbody></table></div>') + card("flex · 크기 · 가시성 · 스크롤", flex_demo) + '</div></section>\n')

body = ''.join(out)

HEAD = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Argus CSS Framework — 조합 매트릭스</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../dist/argus.min.css">
<script>try{if(localStorage.getItem('ag-theme')==='light')document.documentElement.setAttribute('data-theme','light')}catch(e){}</script>
<style>
  .demo { display: flex; flex-wrap: wrap; align-items: center; gap: var(--ag-space-3); }
  .ag-table--matrix th:first-child { white-space: nowrap; color: var(--ag-text-3); font-weight: 500; font-family: var(--ag-font-mono); font-size: var(--ag-text-xs); }
  .ag-table--matrix td { vertical-align: middle; }
  .ag-table--matrix thead th { font-family: var(--ag-font-mono); font-size: var(--ag-text-xs); }
</style>
</head>
<body>
<!--@icons-->

<div class="ag-app">
  <header class="ag-topbar">
    <a class="ag-topbar__brand" href="index.html"><span class="ag-dot ag-dot--accent"></span>Argus CSS Framework</a>
    <nav class="ag-topbar__center ag-hide-md">
      <div class="ag-nav ag-nav--compact">
        <a class="ag-nav__item" href="#badges">배지</a><a class="ag-nav__item" href="#buttons">버튼</a><a class="ag-nav__item" href="#cards">카드</a><a class="ag-nav__item" href="#inputs">입력</a><a class="ag-nav__item" href="#feedback">피드백</a><a class="ag-nav__item" href="#charts">차트</a><a class="ag-nav__item" href="#patterns">패턴</a><a class="ag-nav__item" href="#utils">유틸</a>
      </div>
    </nav>
    <div class="ag-topbar__actions">
      <a class="ag-btn ag-btn--outline ag-btn--sm ag-hide-sm" href="components.html">컴포넌트 카탈로그</a>
      <button class="ag-btn ag-btn--icon ag-btn--outline" aria-label="테마 전환" data-ag-theme-toggle><svg class="ag-icon ag-only-dark"><use href="#i-sun"/></svg><svg class="ag-icon ag-only-light"><use href="#i-moon"/></svg></button>
    </div>
  </header>

  <main class="ag-main">
    <div class="ag-page-header"><div class="ag-page-header__title"><h1>조합 매트릭스</h1><p class="ag-text-2">모든 변형 × 모든 조합을 한 화면에. 개별 예시로는 안 잡히는 "조합하면 깨지는" 버그(톤을 덮는 모양 변형, 쌓임 순서, 소스 순서 의존)를 눈으로 잡기 위한 회귀 페이지. 예쁘라고 만든 페이지가 아니라 <strong>어긋난 셀을 찾는</strong> 페이지다 — 컴포넌트를 추가·수정하면 여기도 갱신한다 (<code>tools/gen_matrix.py</code>).</p></div></div>
'''
TAIL = '''  </main>
</div>

<div class="ag-modal-overlay ag-modal-overlay--lg" id="mx-lg" hidden><div class="ag-modal__panel"><div class="ag-modal__head"><h3>--lg 860px</h3><button class="ag-btn ag-btn--icon ag-btn--ghost" data-ag-close aria-label="닫기">×</button></div><p class="ag-text-sm ag-text-2">넓은 모달 — 비교 테이블·diff 용.</p><div class="ag-modal__foot"><button class="ag-btn ag-btn--primary" data-ag-close>닫기</button></div></div></div>
<div class="ag-modal-overlay ag-modal-overlay--xl" id="mx-xl" hidden><div class="ag-modal__panel"><div class="ag-modal__head"><h3>--xl 1100px</h3><button class="ag-btn ag-btn--icon ag-btn--ghost" data-ag-close aria-label="닫기">×</button></div><p class="ag-text-sm ag-text-2">가장 넓은 모달 — 로그 전체 보기 등.</p><div class="ag-modal__foot"><button class="ag-btn ag-btn--primary" data-ag-close>닫기</button></div></div></div>

<script src="../dist/argus.js"></script>
</body>
</html>
'''
(ROOT / "examples/src/matrix.html").write_text(HEAD + body + TAIL, encoding="utf-8")
print("wrote examples/src/matrix.html", len(HEAD + body + TAIL), "bytes")
