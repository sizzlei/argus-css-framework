#!/usr/bin/env python3
"""값 단언 회귀 — 스크린샷(shots.py)·매트릭스(눈)로는 못 잡는 것을 숫자로 확인한다.
   서비스 적용에서 들어온 버그마다 여기에 단언을 하나씩 남긴다. 실패하면 exit 1.
   python3 tools/check.py        (playwright 필요: pip install playwright && playwright install chromium)
   python3 tools/check.py -v     (통과한 항목도 출력)"""
import asyncio, base64, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT.joinpath("examples").as_uri() + "/"
VERBOSE = "-v" in sys.argv
results = []

def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    if VERBOSE or not ok:
        print(("  ok   " if ok else "  FAIL ") + name + (f"  — {detail}" if detail else ""))

async def page(b, path, width=1440, height=900, light=False, skin=False):
    pg = await b.new_page(viewport={"width": width, "height": height})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.goto(BASE + path)
    if light:
        await pg.evaluate("document.documentElement.dataset.theme='light'")
    if skin:
        await pg.evaluate("document.documentElement.dataset.skin='glass'")
    await pg.wait_for_timeout(350)
    pg._errs = errs
    return pg


# ── 1.13.1 클래스 커버리지: css/ 에 정의된 클래스는 전부 예시(examples/src — matrix 포함)·templates·js 중 한 곳에 나와야 한다.
#    예시가 곧 문서이자 회귀 테스트라서, 예시 없는 클래스는 아무도 못 보고 깨진다 (1.13 까지 18개가 그랬다). ──
def _class_coverage():
    import re
    css = "".join(f.read_text(encoding="utf-8") for f in sorted((ROOT / "css").rglob("*.css")) if "themes" not in f.parts)
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)          # 주석 속 예시 마크업은 정의가 아니다
    defined = set(re.findall(r"\.(ag-[a-z0-9_-]*[a-z0-9])", css))
    files = list((ROOT / "examples/src").glob("*.html")) + list((ROOT / "js").rglob("*.js")) + list((ROOT / "templates").rglob("*.html"))
    used = set(re.findall(r"ag-[a-z0-9_-]*[a-z0-9]", "".join(f.read_text(encoding="utf-8") for f in files)))
    allow = {
        "ag-app--rail", "ag-app--focus",   # layouts.html 이 'ag-app--' + mode 로 붙인다
        "ag-auth__glass--card",            # extras/auth-landing 별도 번들 — templates/README 에서 안내
    }
    return sorted(defined - used - allow)

# ── 1.15.1 backdrop-filter 접두: dist 의 -webkit-backdrop-filter 블록마다 접두 없는 선언이 같이 있어야 한다.
#    소스에 둘 다 쓰면 lightningcss 가 접두 없는 쪽을 지워 Chrome · Firefox 에서 블러가 꺼졌다(상단 바 · 랜딩 인증 2곳, 1.15.0 까지).
#    소스 패턴이 아니라 결과물을 봐서 minifier 가 바뀌어도 같은 회귀를 잡는다 ──
def _backdrop_prefix_pairs():
    import re
    bad = []
    for f in sorted((ROOT / "dist").rglob("*.min.css")):
        for sel, body in re.findall(r"([^{}]*)\{([^{}]*)\}", f.read_text(encoding="utf-8")):
            if "-webkit-backdrop-filter:" in body and not re.search(r"(?<![-\w])backdrop-filter:", body):
                bad.append(f"{f.name}: {sel.strip()[:60]}")
    return bad

# ── 2.0.0 버전 표기 일치: build.sh VERSION = dist/VERSION = package.json version = components 가이드 머리글.
#    package.json 은 1.9.1, 가이드 머리글은 v1.8.0 에서 멈춰 있었다(2.0.0 에서 발견) ──
def _version_marks():
    import re, json
    want = re.search(r'^VERSION="([^"]+)"', (ROOT / "build.sh").read_text(encoding="utf-8"), re.M).group(1)
    got = {"dist/VERSION": (ROOT / "dist/VERSION").read_text(encoding="utf-8").strip(),
           "package.json": json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"],
           "components 머리글": (re.search(r'class="ag-eyebrow">v([0-9.]+) ·', (ROOT / "examples/src/components.html").read_text(encoding="utf-8")) or [None, None])[1]}
    return want, {k: v for k, v in got.items() if v != want}

# ── 1.5 엔진 팔레트: 인접쌍(documentdb→mysql→postgres→oracle→mssql) 색각이상 ΔE 검증 (OKLab, Viénot 행렬) ──
def _engine_palette_check():
    import re, math
    css = (ROOT / "css/tokens.css").read_text(encoding="utf-8")
    order = ["documentdb", "mysql", "postgres", "oracle", "mssql"]
    def lin(h):
        h = h.lstrip("#"); v = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
        return [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in v]
    def ok(rgb):
        r, g, b = rgb
        l = (0.4122214708*r + 0.5363325363*g + 0.0514459929*b) ** (1/3); m = (0.2119034982*r + 0.6806995451*g + 0.1073969566*b) ** (1/3); s_ = (0.0883024619*r + 0.2817188376*g + 0.6299787005*b) ** (1/3)
        return (0.2104542553*l + 0.7936177850*m - 0.0040720468*s_, 1.9779984951*l - 2.4285922050*m + 0.4505937099*s_, 0.0259040371*l + 0.7827717662*m - 0.8086757660*s_)
    M = {"P": [[0.170556992, 0.829443014, 0], [0.170556991, 0.829443008, 0], [-0.004517144, 0.004517144, 1]],
         "D": [[0.33066007, 0.66933993, 0], [0.33066007, 0.66933993, 0], [-0.02785538, 0.02785538, 1]],
         "T": [[1, 0.1273989, -0.1273989], [0, 0.8739093, 0.1260907], [0, 0.8739093, 0.1260907]]}
    def sim(rgb, k): return [sum(M[k][i][j] * rgb[j] for j in range(3)) for i in range(3)]
    def dE(a, b): return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b))) * 100
    out = {}
    for theme, block in (("dark", css.split('[data-theme="light"]')[0]), ("light", css.split('[data-theme="light"]')[1])):
        cols = {}
        for n in order:
            mm = re.search(r"--ag-engine-%s:\s*(#[0-9a-fA-F]{6})" % n, block); cols[n] = mm.group(1)
        worst = 99
        for a, b in zip(order, order[1:]):
            ds = [dE(ok(lin(cols[a])), ok(lin(cols[b])))] + [dE(ok(sim(lin(cols[a]), k)), ok(sim(lin(cols[b]), k))) for k in M]
            worst = min(worst, min(ds))
        out[theme] = round(worst, 1)
    return out

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()

        orphan = _class_coverage()
        check(f"coverage: every css class appears in examples/templates/js", not orphan, ", ".join(orphan[:12]) + (f" … +{len(orphan) - 12}" if len(orphan) > 12 else ""))
        want, off = _version_marks()
        check(f"2.0.0 버전 표기 일치: build.sh VERSION({want}) = dist/VERSION = package.json = components 가이드 머리글", not off, str(off))
        bp = _backdrop_prefix_pairs()
        check("1.15.1: dist 의 -webkit-backdrop-filter 마다 접두 없는 backdrop-filter 가 같은 블록에 있다", not bp, " | ".join(bp[:6]))

        # 1.13.1: .ag-drawer__head 는 .ag-modal__head 와 같은 머리 (전에는 남은 높이 규칙만 받아 정렬이 빠졌다)
        pg = await page(b, "detail.html")
        r = await pg.evaluate("""()=>{const h=document.querySelector('#drawer-param > .ag-drawer__head');if(!h)return null;const cs=getComputedStyle(h);return cs.display+' '+cs.justifyContent}""")
        check("drawer__head: flex + space-between like modal__head", r == "flex space-between", str(r))
        await pg.close()

        # ── 1. 모든 페이지: JS 에러 0, 400px 가로 스크롤 0 ─────────────────────────
        for name in ["index", "resources", "detail", "login", "layouts", "components", "matrix", "report"]:
            pg = await page(b, name + ".html")
            check(f"{name}: page errors", not pg._errs, "; ".join(pg._errs[:2]))
            await pg.close()
            pm = await page(b, name + ".html", 400, 900)
            sw = await pm.evaluate("document.documentElement.scrollWidth")
            check(f"{name}: no horizontal scroll @400", sw <= 400, f"scrollWidth={sw}")
            await pm.close()

        # ── 2. 배지: 톤 × 모양 어떤 조합도 기본 회색으로 떨어지지 않는다 (--count 가 톤을 덮던 버그) ──
        pg = await page(b, "matrix.html")
        bad = await pg.evaluate("""()=>{const bad=[];document.querySelectorAll('#badges .ag-badge').forEach(e=>{
          const tone=(e.className.match(/ag-badge--(good|warn|crit|info|accent2?|cat[1-4]|inverse)/)||[])[1];
          if(tone&&getComputedStyle(e).backgroundColor==='rgb(44, 45, 58)')bad.push(e.className)});return bad}""")
        check("badge: tone never falls back to default bg", not bad, ", ".join(bad[:3]))
        solid = await pg.evaluate("""()=>[...document.querySelectorAll('#badges .ag-badge--solid')].filter(e=>/--(good|warn|crit|info|accent2?|cat[1-4]|inverse)/.test(e.className)).filter(e=>getComputedStyle(e).backgroundColor.startsWith('rgba')).map(e=>e.className)""")
        check("badge: --solid never leaves a translucent (soft) bg", not solid, ", ".join(solid[:3]))

        # ── 3. input-group: 선행 아이콘 + --end 조합에서 양쪽 패딩 모두 유지 ──────────────────
        r = await pg.evaluate("""()=>[...document.querySelectorAll('.ag-input-group--end')].map(g=>{const i=g.querySelector('.ag-input');const c=getComputedStyle(i);return {icon:!!g.querySelector(':scope > .ag-icon'),pl:parseFloat(c.paddingLeft),pr:parseFloat(c.paddingRight)}})""")
        both = [x for x in r if x["icon"]]
        check("input-group: icon + --end keeps left 42 / right 48", both and all(x["pl"] >= 36 and x["pr"] >= 44 for x in both), str(both))

        # ── 4. form-grid: --3 격자에서 --span2 는 이웃의 2배+gap ───────────────────────────
        r = await pg.evaluate("""()=>{const f=document.querySelector('.ag-form-grid--3 .ag-field--span2');const s=f.nextElementSibling;return [f.getBoundingClientRect().width, s.getBoundingClientRect().width]}""")
        check("form-grid: --span2 ≈ 2 × sibling + gap", abs(r[0] - (2 * r[1] + 20)) < 4, f"{r[0]:.0f} vs {r[1]:.0f}")
        cols = await pg.evaluate("getComputedStyle(document.querySelector('.ag-form-grid--3')).gridTemplateColumns.split(' ').length")
        check("form-grid: --3 has exactly 3 tracks", cols == 3, f"{cols}")

        # ── 5. 토스트: 정적 스택은 쌓임 맥락을 만들지 않는다 (모달 위로 올라오던 버그) ────────────
        z = await pg.evaluate("getComputedStyle(document.querySelector('.ag-toast-stack--static')).zIndex")
        check("toast: --static has z-index auto", z == "auto", z)

        # ── 6. 카드: a/button 카드도 flex column + gap (display:block 이 gap 을 죽이던 버그) ──────
        r = await pg.evaluate("""()=>['a.ag-card','button.ag-card'].map(s=>{const e=document.querySelector(s);const c=getComputedStyle(e);return s+':'+c.display+'/'+c.flexDirection+'/'+c.textAlign})""")
        check("card: a/button keep flex column, left text", all("flex/column/left" in x for x in r), " ".join(r))
        r = await pg.evaluate("""()=>{const b=document.createElement('button');b.className='ag-card';b.innerHTML='<div class="ag-cluster ag-cluster--between"><span>L</span><span>R</span></div>';document.body.appendChild(b);b.style.width='400px';
          const cs=getComputedStyle(b),inner=b.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);return {ai:cs.alignItems,fill:Math.abs(b.firstElementChild.getBoundingClientRect().width-inner)<1}}""")
        check("card: button.ag-card children fill width (UA align-items:center reset)", r["ai"] == "stretch" and r["fill"], str(r))

        # ── 7. 아바타·범주 톤 대비: soft 배경 위 글자 4.5:1 이상 (다크·라이트) ──────────────────
        for light in (False, True):
            pl = await page(b, "matrix.html", light=light)
            lows = await pl.evaluate("""()=>{
              function L(c){const m=c.match(/[\\d.]+/g).map(Number);const [r,g,b]=m.slice(0,3).map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*r+.7152*g+.0722*b}
              function blend(fg,bg){const f=fg.match(/[\\d.]+/g).map(Number),k=bg.match(/[\\d.]+/g).map(Number);const a=f[3]??1;return `rgb(${f[0]*a+k[0]*(1-a)}, ${f[1]*a+k[1]*(1-a)}, ${f[2]*a+k[2]*(1-a)})`}
              const surf=getComputedStyle(document.querySelector('.ag-card')).backgroundColor; const out=[];
              document.querySelectorAll('#badges .ag-badge--cat1,#badges .ag-badge--cat2,#badges .ag-badge--cat3,#badges .ag-badge--cat4,.ag-avatar--cat1,.ag-avatar--cat2,.ag-avatar--cat3,.ag-avatar--cat4,.ag-avatar--good,.ag-avatar--warn,.ag-avatar--crit,.ag-avatar--info').forEach(e=>{
                if(/--solid/.test(e.className))return; const c=getComputedStyle(e); const bg=blend(c.backgroundColor,surf); const l1=L(c.color),l2=L(bg); const cr=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05); if(cr<4.5) out.push(e.className.replace(/ag-(badge|avatar) /,'')+':'+cr.toFixed(2))});
              return out}""")
            check(f"contrast: cat/avatar text ≥ 4.5 on soft bg ({'light' if light else 'dark'})", not lows, ", ".join(lows[:4]))
            await pl.close()
        await pg.close()

        # ── 8. 오버레이 소유권: argus.js 는 자기가 연 것만 닫는다 ─────────────────────────────
        pg = await page(b, "components.html")
        await pg.click('[data-ag-open="demo-overlay"]'); await pg.wait_for_timeout(150)
        check("overlay: data-ag-open opens (is-open + !hidden)", await pg.evaluate("!document.getElementById('demo-overlay').hidden && document.getElementById('demo-overlay').classList.contains('is-open')"))
        await pg.mouse.click(20, 450); await pg.wait_for_timeout(150)
        check("overlay: backdrop click closes owned", await pg.evaluate("document.getElementById('demo-overlay').hidden"))
        await pg.evaluate("""()=>{const o=document.createElement('div');o.className='ag-modal-overlay';o.id='foreign';o.innerHTML='<div class="ag-modal__panel"><h3>f</h3><button data-ag-close id="fclose">x</button></div>';document.body.appendChild(o)}""")
        await pg.mouse.click(20, 450); await pg.wait_for_timeout(100); await pg.keyboard.press("Escape"); await pg.wait_for_timeout(100)
        check("overlay: foreign (not opened by argus.js) survives backdrop + ESC", await pg.evaluate("!document.getElementById('foreign').hidden"))
        await pg.evaluate("document.getElementById('foreign').addEventListener('ag:overlay-close', e=>{ if(window.__block) e.preventDefault() }); window.__block=true")
        await pg.click("#fclose"); await pg.wait_for_timeout(80)
        check("overlay: ag:overlay-close is cancelable", await pg.evaluate("!document.getElementById('foreign').hidden"))
        await pg.evaluate("window.__block=false"); await pg.click("#fclose"); await pg.wait_for_timeout(80)
        check("overlay: explicit data-ag-close works regardless of ownership", await pg.evaluate("document.getElementById('foreign').hidden"))
        await pg.keyboard.press("Meta+k"); await pg.wait_for_timeout(150)
        check("cmdk: ⌘K opens", await pg.evaluate("!document.getElementById('cmdk').hidden"))
        await pg.keyboard.press("Escape"); await pg.wait_for_timeout(150)
        check("cmdk: ESC closes (owned)", await pg.evaluate("document.getElementById('cmdk').hidden"))
        await pg.evaluate("document.getElementById('demo-drawer').classList.add('is-open')"); await pg.keyboard.press("Escape"); await pg.wait_for_timeout(100)
        check("drawer: opened by someone else survives ESC", await pg.evaluate("document.getElementById('demo-drawer').classList.contains('is-open')"))
        await pg.close()

        # ── 9. 레이아웃: 래퍼 스택, 간격 토큰, tabs 초광폭 ─────────────────────────────────────
        pg = await page(b, "detail.html")
        r = await pg.evaluate("""()=>{const w=document.querySelector('.ag-main > .ag-page');const k=[...w.children];return {disp:getComputedStyle(w).display,gap:Math.round(k[1].getBoundingClientRect().top-k[0].getBoundingClientRect().bottom)}}""")
        check("layout: .ag-page wrapper stacks with --ag-gap-main (32)", r["disp"] == "flex" and r["gap"] == 32, str(r))
        await pg.evaluate("document.querySelector('.ag-main > .ag-page').removeAttribute('class')"); await pg.wait_for_timeout(50)
        check("layout: classless x-data wrapper auto-stacks", await pg.evaluate("getComputedStyle(document.querySelector('.ag-main > div')).display") == "flex")
        gg = await pg.evaluate("getComputedStyle(document.querySelector('.ag-grid')).gap")
        check("layout: .ag-grid gap = --ag-gap-grid (24px)", gg.startswith("24px"), gg)
        await pg.close()
        for w in (1440, 2560, 3400, 3840):
            pg = await page(b, "layouts.html", w, 900)
            await pg.click('[data-mode="tabs"]'); await pg.wait_for_timeout(200)
            r = await pg.evaluate("""()=>{const rows=[...document.querySelectorAll('.ag-topbar__row')].filter(e=>!e.hidden).map(e=>e.getBoundingClientRect());const m=document.querySelector('.ag-main').getBoundingClientRect();return {n:rows.length,distinctTop:rows[0].top!==rows[1]?.top,aligned:Math.abs(rows[0].left-m.left)<2}}""")
            check(f"tabs @{w}: 2 rows stacked and aligned with main", r["n"] == 2 and r["distinctTop"] and r["aligned"], str(r))
            await pg.close()

        # ── 9b. argus.js 를 <head> 에서 로드해도 사이드바 상태 복원 동작 / 접힌 사이드바에서 Phosphor <i> 유지 ──
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        await pg.add_init_script("try{localStorage.setItem('ag-sidebar-collapsed','true')}catch(e){}")
        html = (ROOT / "examples/resources.html").read_text(encoding="utf-8")
        head_loaded = html.replace('<script src="../dist/argus.js"></script>', '').replace('</head>', '<script src="../dist/argus.js"></script></head>', 1)
        head_loaded = head_loaded.replace('<span>개요</span>', '<i class="ph ph-squares-four"></i><span>개요</span>', 1)
        tmp = ROOT / "examples/_check_head.html"; tmp.write_text(head_loaded, encoding="utf-8")
        try:
            await pg.goto(BASE + "_check_head.html"); await pg.wait_for_timeout(400)
            check("argus.js in <head>: sidebar collapsed state restored", await pg.evaluate("document.querySelector('.ag-app--sidebar').classList.contains('is-collapsed')"))
            r = await pg.evaluate("""()=>{const i=document.querySelector('.ag-sidebar__item [class*="ph-"]');const s=i&&i.nextElementSibling;return {icon:i?getComputedStyle(i).display:'none',label:s?getComputedStyle(s).display:'?'}}""")
            check("collapsed sidebar: Phosphor <i> stays visible, label hidden", r["icon"] != "none" and r["label"] == "none", str(r))
        finally:
            tmp.unlink(missing_ok=True); await pg.close()

        # ── 9c. 순차 램프: CSS 토큰 == JS sequential(), 라이트에서 1단계·빈 셀이 카드 배경과 구분, Apex heatmap 프리셋 ──
        for light in (False, True):
            pg = await page(b, "components.html", light=light)
            r = await pg.evaluate("""()=>{const d=document.createElement('div');d.className='ag-card';d.innerHTML='<div class="ag-heatmap">'+[1,2,3,4,5].map(k=>'<i class="ag-heat ag-heat--'+k+'"></i>').join('')+'<i class="ag-heat ag-heat--empty"></i></div>';document.body.appendChild(d);
              const cells=[...d.querySelectorAll('.ag-heat')].map(e=>getComputedStyle(e).backgroundColor);const card=getComputedStyle(d).backgroundColor;
              const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});const hex=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);const d=ctx.getImageData(0,0,1,1).data;return '#'+[d[0],d[1],d[2]].map(v=>('0'+v.toString(16)).slice(-2)).join('')};const lum=c=>{const h=hex(c);return (parseInt(h.slice(1,3),16)*299+parseInt(h.slice(3,5),16)*587+parseInt(h.slice(5,7),16)*114)/1000};
              const o=AG.charts.apex({chart:{type:'heatmap'},series:[{data:[{x:'a',y:0},{x:'b',y:40},{x:'c',y:400}]}]});
              return {css:cells.slice(0,5).map(hex),js:AG.charts.sequential(5),empty:cells[5],card,d1:Math.abs(lum(cells[0])-lum(card)),dEmpty:Math.abs(lum(cells[5])-lum(card)),
                shadow:getComputedStyle(d.querySelector('.ag-heat')).boxShadow!=='none',ranges:(o.plotOptions.heatmap.colorScale.ranges||[]).length,shades:o.plotOptions.heatmap.enableShades,stroke:o.stroke.colors[0],n7:AG.charts.sequential(7).length}}""")
            th = "light" if light else "dark"
            check(f"seq ({th}): --ag-seq-1..5 == AG.charts.sequential(5) (hex)", r["css"] == r["js"] and all(c.startswith('#') for c in r["js"]), f'{r["css"]} vs {r["js"]}')
            check(f"seq ({th}): 5 distinct steps, monotonic", len(set(r["css"])) == 5)
            check(f"seq ({th}): step 1 and empty cell distinguishable from card bg", r["d1"] >= 6 and (r["dEmpty"] >= 3 or r["shadow"]), f'd1={r["d1"]:.1f} dEmpty={r["dEmpty"]:.1f} shadow={r["shadow"]}')
            check(f"seq ({th}): apex heatmap preset → 6 ranges (0 + 5 steps) from series, shades off, grid stroke", r["ranges"] == 6 and r["shades"] is False and bool(r["stroke"]) and r["n7"] == 7, str({k: r[k] for k in ("ranges", "shades", "stroke", "n7")}))
            await pg.close()

        # ── 9d. .ag-list__item.is-active: 선택 상태가 배경·테두리로 구분되고 button 리셋이 걸린다 ──
        pg = await page(b, "components.html")
        r = await pg.evaluate("""()=>{const d=document.createElement('div');d.innerHTML='<div class="ag-list"><button class="ag-list__item is-active"><span class="ag-list__label">A</span></button><button class="ag-list__item"><span class="ag-list__label">B</span></button></div><div class="ag-list ag-list--divided"><button class="ag-list__item is-active">C</button></div>';document.body.appendChild(d);
          const [a,b]=d.querySelectorAll('.ag-list:not(.ag-list--divided) .ag-list__item');const c=d.querySelector('.ag-list--divided .ag-list__item');const sa=getComputedStyle(a),sb=getComputedStyle(b),sc=getComputedStyle(c);
          return {bg:sa.backgroundColor!==sb.backgroundColor,border:sa.borderColor!==sb.borderColor,width:Math.abs(a.getBoundingClientRect().width-a.parentElement.getBoundingClientRect().width)<1,align:sa.textAlign,font:sa.fontFamily===getComputedStyle(document.body).fontFamily,divBar:sc.boxShadow!=='none'}}""")
        check("list: is-active differs from sibling (bg + border), button fills width, left-aligned, inherits font", r["bg"] and r["border"] and r["width"] and r["align"] in ("left", "start") and r["font"], str(r))
        check("list: --divided is-active shows inset accent bar", r["divBar"])
        await pg.close()

        # ── 9e. 버튼 조합: ghost×danger 는 평소 투명·중립, hover 시 crit ──
        pg = await page(b, "components.html")
        r = await pg.evaluate("""()=>{const d=document.createElement('div');d.style.cssText='position:fixed;top:8px;left:8px;z-index:9999';d.innerHTML='<button class="ag-btn ag-btn--ghost ag-btn--danger" id="gd">x</button><button class="ag-btn ag-btn--ghost" id="g">x</button><button class="ag-btn ag-btn--danger" id="dg">x</button>';document.body.appendChild(d);
          const c=id=>{const s=getComputedStyle(document.getElementById(id));return s.backgroundColor+'|'+s.color};return {gd:c('gd'),g:c('g'),dg:c('dg')}}""")
        check("btn: ghost×danger idle == ghost (transparent, neutral)", r["gd"] == r["g"] and r["gd"] != r["dg"], str(r))
        await pg.hover("#gd"); await pg.wait_for_timeout(250)
        r2 = await pg.evaluate("()=>{const s=getComputedStyle(document.getElementById('gd'));const g=getComputedStyle(document.getElementById('g'));return {bg:s.backgroundColor, color:s.color, gcolor:g.color, crit:getComputedStyle(document.documentElement).getPropertyValue('--ag-crit').trim()}}")
        check("btn: ghost×danger hover turns crit", r2["color"] != r2["gcolor"] and r2["bg"] != "rgba(0, 0, 0, 0)", str(r2))
        await pg.close()

        # ── 9f. .ag-only-dark/--light: phosphor.js 가 <head> 끝에 주입하는 [class^="ph-"]{display:inline-block} 보다 이긴다 ──
        for light in (False, True):
            pg = await page(b, "components.html", light=light)
            r = await pg.evaluate("""()=>{const st=document.createElement('style');st.textContent='[class^="ph-"],[class*=" ph-"]{display:inline-block}';document.head.appendChild(st);
              const d=document.createElement('div');d.innerHTML='<i class="ph ph-sun ag-only-dark"></i><i class="ph ph-moon ag-only-light"></i>';document.body.appendChild(d);
              const [s,m]=d.children;return {sun:getComputedStyle(s).display,moon:getComputedStyle(m).display}}""")
            th = "light" if light else "dark"
            ok = (r["moon"] == "none" and r["sun"] == "inline-block") if not light else (r["sun"] == "none" and r["moon"] == "inline-block")
            check(f"only-dark/light ({th}): exactly one Phosphor <i> visible, visible one keeps inline-block", ok, str(r))
            await pg.close()

        # ── 9g. Phosphor <i> 가 svg .ag-icon 과 같은 대우: input-group 선행 아이콘 위치, .ag-user 캐럿 색, logo-box 크기 ──
        pg = await page(b, "components.html")
        r = await pg.evaluate("""()=>{const d=document.createElement('div');d.className='ag-card';d.innerHTML='<div class="ag-input-group"><i class="ph ph-envelope" id="pi"></i><input class="ag-input" id="pin"></div>'
          +'<div class="ag-input-group"><svg class="ag-icon" id="si"></svg><input class="ag-input"></div>'
          +'<div class="ag-input-group ag-input-group--end"><input class="ag-input" id="noicon"><span class="ag-input-group__end"><button class="ag-btn ag-btn--sm ag-btn--ghost"><i class="ph ph-x" id="endi"></i></button></span></div>'
          +'<button class="ag-user"><span class="ag-user__text">x</span><i class="ph ph-caret-down" id="pc"></i></button>'
          +'<span class="ag-auth__logo-box"><i class="ph ph-database" id="pl"></i></span>';document.body.appendChild(d);
          const g=id=>getComputedStyle(document.getElementById(id));const inp=document.getElementById('pin').getBoundingClientRect(),ico=document.getElementById('pi').getBoundingClientRect();
          return {pos:g('pi').position,left:g('pi').left,inside:ico.left>inp.left&&ico.left<inp.left+40,svgPos:g('si').position,endPos:g('endi').position,noiconPad:g('noicon').paddingLeft,
            caret:g('pc').color,text3:getComputedStyle(document.documentElement).getPropertyValue('--ag-text-3').trim(),logo:g('pl').fontSize}}""")
        check("phosphor: <i> in .ag-input-group is absolute at left 12px, inside the input", r["pos"] == "absolute" and r["left"] == "12px" and r["inside"] and r["svgPos"] == "absolute", str(r))
        check("phosphor: <i> inside __end stays static; --end without leading icon keeps 12px padding", r["endPos"] == "static" and r["noiconPad"] == "12px", str(r))
        check("phosphor: .ag-user caret colored text-3, .ag-auth__logo-box glyph 26px", r["logo"] == "26px" and r["caret"] != "rgb(255, 255, 255)", str(r))
        await pg.close()

        # ── 9h. .ag-qr__pending 은 img 와 같은 180px / .ag-quick-action__body 는 남은 폭을 채우고 __meta 가 말줄임 ──
        pg = await page(b, "components.html")
        r = await pg.evaluate("""()=>{const d=document.createElement('div');d.innerHTML='<div class="ag-qr"><div class="ag-qr__pending">…</div></div><div class="ag-quick-actions" style="width:400px"><a class="ag-quick-action" href="#"><span class="ag-quick-action__icon"></span><span class="ag-quick-action__body"><span class="ag-quick-action__title">T</span><span class="ag-quick-action__meta">'+'m'.repeat(80)+'</span></span><svg class="ag-icon ag-icon--sm ag-quick-action__end"></svg></a></div>';document.body.appendChild(d);
          const p=d.querySelector('.ag-qr__pending').getBoundingClientRect(),a=d.querySelector('.ag-quick-action'),b=d.querySelector('.ag-quick-action__body'),m=d.querySelector('.ag-quick-action__meta');
          return {w:p.width,h:p.height,fits:a.scrollWidth<=a.clientWidth+1,bodyFlex:getComputedStyle(b).flexGrow,clip:m.scrollWidth>m.clientWidth&&getComputedStyle(m).textOverflow==='ellipsis'}}""")
        check("qr: __pending occupies 180×180", r["w"] == 180 and r["h"] == 180, str(r))
        check("quick-action: __body fills, long __meta ellipsizes without overflowing the tile", r["fits"] and r["bodyFlex"] == "1" and r["clip"], str(r))
        await pg.close()

        # ── 9i. 단색 카드 안의 흐린 텍스트·outline 버튼 대비 (violet 기본 + yellow 테마, 다크·라이트) / 기타 색 ──
        for theme in ("", "yellow"):
            for light in (False, True):
                pg = await page(b, "components.html", light=light)
                if theme:
                    await pg.add_style_tag(path=str(ROOT / f"dist/themes/{theme}.min.css")); await pg.wait_for_timeout(100)
                r = await pg.evaluate("""()=>{const d=document.createElement('div');d.className='ag-card ag-card--accent';d.innerHTML='<span class="ag-label" id="l">x</span><span class="ag-hint" id="h">x</span><span class="ag-stat__label" id="s">x</span><dl class="ag-kv"><dt id="k">x</dt></dl><div class="ag-card__foot"><span class="ag-text-3" id="f">x</span><button class="ag-btn ag-btn--outline" id="o">x</button></div>';document.body.appendChild(d);
                  const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});const px=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data]};
                  const bg=px(getComputedStyle(d).backgroundColor);const lum=p=>{const f=v=>{v/=255;return v<=.03928?v/12.92:((v+.055)/1.055)**2.4};return .2126*f(p[0])+.7152*f(p[1])+.0722*f(p[2])};
                  const over=(fg,bg)=>{const a=fg[3]/255;return [0,1,2].map(i=>fg[i]*a+bg[i]*(1-a))};const cr=(c)=>{const f=over(px(c),bg),L1=lum(f),L2=lum(bg);return (Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05)};
                  const out={};for(const id of ['l','h','s','k','f','o'])out[id]=+cr(getComputedStyle(document.getElementById(id)).color).toFixed(2);out.ob=+cr(getComputedStyle(document.getElementById('o')).borderColor).toFixed(2);out.full=+cr(getComputedStyle(d).color).toFixed(2);return out}""")
                th = (theme or "violet") + "/" + ("light" if light else "dark")
                # 액센트 자체가 밝으면(violet 다크 ≈3.3:1) 흰 글자도 그 이상은 못 나온다 — 흐린 단계가 4.5:1 이상이거나(본문 대비의 80% 이상이고 2.6:1 이상)이면 통과
                check(f"accent card ({th}): muted text keeps ≥80% of body contrast and ≥2.6:1, outline btn = body text, border visible", all(r[k] >= 2.6 and (r[k] >= 4.5 or r[k] >= .8 * r["full"]) for k in ("l", "h", "s", "k", "f")) and r["o"] == r["full"] and r["ob"] >= 1.5, str(r))
                await pg.close()
        pg = await page(b, "components.html")
        r = await pg.evaluate("()=>({p5:AG.charts.palette(5),p4:AG.charts.palette(4),other:AG.charts.other(),t3:getComputedStyle(document.documentElement).getPropertyValue('--ag-chart-other').trim()})")
        check("palette(5): last = --ag-chart-other, first four = palette(4)", r["p5"][4] == r["other"] == r["t3"] and r["p5"][:4] == r["p4"] and r["other"] not in r["p4"], str(r))
        await pg.close()

        # ── 9j. .ag-table--clickable: 행 커서 pointer, 액션 셀은 default ──
        pg = await page(b, "components.html")
        r = await pg.evaluate("""()=>{const tr=document.querySelector('.ag-table--clickable tbody tr');const td=tr.querySelector('.ag-td--actions');const d=document.createElement('table');d.className='ag-table';d.innerHTML='<tbody><tr class="is-clickable"><td>x</td></tr><tr><td>y</td></tr></tbody>';document.body.appendChild(d);const [a,b]=d.querySelectorAll('tr');
          return {row:getComputedStyle(tr).cursor,act:td?getComputedStyle(td).cursor:'?',single:getComputedStyle(a).cursor,plain:getComputedStyle(b).cursor}}""")
        check("table: --clickable rows pointer, action cell default, tr.is-clickable alone works", r["row"] == "pointer" and r["act"] == "default" and r["single"] == "pointer" and r["plain"] == "auto", str(r))
        await pg.close()

        # ── 9k. .ag-segmented 항목 8개 @400px: 안에서 스크롤, 문서 가로 스크롤 없음 ──
        pg = await page(b, "components.html", 400, 900)
        r = await pg.evaluate("""()=>{const d=document.createElement('div');d.className='ag-card';d.innerHTML='<div class="ag-segmented" id="sg">'+Array.from({length:8},(_,i)=>'<button class="ag-segmented__item">탭 항목 '+(i+1)+'</button>').join('')+'</div>';document.body.appendChild(d);const sg=document.getElementById('sg');
          return {inner:sg.scrollWidth>sg.clientWidth,ov:getComputedStyle(sg).overflowX,doc:document.documentElement.scrollWidth,vw:document.documentElement.clientWidth,wrap:getComputedStyle(sg.firstElementChild).whiteSpace}}""")
        check("segmented: 8 items @400px scroll inside, no document overflow, items don't wrap", r["inner"] and r["ov"] == "auto" and r["doc"] <= r["vw"] and r["wrap"] == "nowrap", str(r))
        await pg.close()

        # ── 9l. secret-field--block: 가림 상태(투명 글자·블러·선택 불가·reveal 표시) → 클릭 후 해제 ──
        pg = await page(b, "components.html")
        r = await pg.evaluate("""()=>{const ta=document.getElementById('sf2'),b=ta.parentElement.querySelector('.ag-secret-field__reveal');const s=getComputedStyle(ta);return {color:s.color,blur:s.filter,sel:s.userSelect,pe:s.pointerEvents,btn:getComputedStyle(b).display}}""")
        check("secret --block masked: transparent text, blur, no select/pointer, reveal button shown", r["color"] == "rgba(0, 0, 0, 0)" and "blur" in r["blur"] and r["sel"] == "none" and r["pe"] == "none" and r["btn"] != "none", str(r))
        await pg.click("#sf2 ~ .ag-secret-field__reveal"); await pg.wait_for_timeout(100)
        r2 = await pg.evaluate("""()=>{const ta=document.getElementById('sf2'),b=ta.parentElement.querySelector('.ag-secret-field__reveal');const s=getComputedStyle(ta);return {masked:ta.classList.contains('is-masked'),color:s.color,blur:s.filter,btn:getComputedStyle(b).display,pressed:b.getAttribute('aria-pressed'),focus:document.activeElement===ta}}""")
        check("secret --block revealed: is-masked off, text visible, reveal hidden, focused", not r2["masked"] and r2["color"] != "rgba(0, 0, 0, 0)" and r2["blur"] == "none" and r2["btn"] == "none" and r2["pressed"] == "true" and r2["focus"], str(r2))
        r3 = await pg.evaluate("""()=>{const i=document.getElementById('sf1'),b=i.parentElement.querySelector('[data-ag-reveal]');b.click();return {masked:i.classList.contains('is-masked'),pressed:b.getAttribute('aria-pressed')}}""")
        check("secret inline: data-ag-reveal toggles input.is-masked", r3["masked"] is False and r3["pressed"] == "true", str(r3))
        await pg.close()

        # ── 9l-2. 단색 카드 안 입력 포커스(1.9.2, argus-server 마스터 계정 비밀번호 칸): 바탕이 쉴 때 그대로이고 표면색이 드러나지 않으며,
        #          테두리는 카드 글자색. 액센트 카드도 같고, 보통 카드의 입력은 예전처럼 표면색 ──
        for light in (False, True):
            pg = await page(b, "components.html", light=light)
            r = await pg.evaluate("""async()=>{const wait=ms=>new Promise(r=>setTimeout(r,ms));
              const probe=document.createElement('div');probe.style.background='var(--ag-surface)';document.body.appendChild(probe);const surface=getComputedStyle(probe).backgroundColor;probe.remove();
              const d=document.createElement('div');d.className='ag-card ag-card--accent';d.innerHTML='<input class="ag-input" id="fa" value="accent">';document.body.appendChild(d);
              const out={surface};
              for(const id of ['sf3','fa','sf1']){const el=document.getElementById(id);el.blur();await wait(300);const rest=getComputedStyle(el).backgroundColor;el.focus();await wait(300);const s=getComputedStyle(el);
                out[id]={rest,focus:s.backgroundColor,border:s.borderColor,color:s.color,ring:s.boxShadow};el.blur();}
              return out}""")
            th = "light" if light else "dark"
            sf3, fa, sf1 = r["sf3"], r["fa"], r["sf1"]
            check(f"field focus in solid card ({th}): bg stays resting, not page surface, border = card text", sf3["focus"] == sf3["rest"] and sf3["focus"] != r["surface"] and sf3["border"] == sf3["color"], str(sf3))
            check(f"field focus in accent card ({th}): same as engine-solid", fa["focus"] == fa["rest"] and fa["focus"] != r["surface"] and fa["border"] == fa["color"], str(fa))
            check(f"field focus in plain card ({th}): unchanged — page surface", sf1["focus"] == r["surface"], str({"sf1": sf1, "surface": r["surface"]}))
            await pg.close()

        # ── 9m. ag-tag 상태 변형: 키·값·테두리가 상태색, 범주 변형은 값은 기본색 (다크·라이트 값 글자 대비 4.5:1) ──
        for light in (False, True):
            pg = await page(b, "components.html", light=light)
            r = await pg.evaluate("""()=>{const d=document.createElement('div');d.className='ag-card';d.innerHTML='<span class="ag-tag ag-tag--crit" id="tc"><span class="ag-tag__key">k</span><span class="ag-tag__val">v</span></span><span class="ag-tag ag-tag--cat1" id="t1"><span class="ag-tag__key">k</span><span class="ag-tag__val">v</span></span><span class="ag-tag" id="t0"><span class="ag-tag__key">k</span><span class="ag-tag__val">v</span></span>';document.body.appendChild(d);
              const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});const px=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data]};const lum=p=>{const f=v=>{v/=255;return v<=.03928?v/12.92:((v+.055)/1.055)**2.4};return .2126*f(p[0])+.7152*f(p[1])+.0722*f(p[2])};
              const cr=(fg,bg)=>{const a=px(fg),b=px(bg);const L1=lum(a),L2=lum(b);return (Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05)};
              const v=id=>getComputedStyle(document.querySelector('#'+id+' .ag-tag__val')).color,bd=id=>getComputedStyle(document.getElementById(id)).borderColor,bg=id=>getComputedStyle(document.getElementById(id)).backgroundColor;
              return {critVal:v('tc')!==v('t0'),catVal:v('t1')===v('t0'),critBorder:bd('tc')!==bd('t0'),cr:+cr(v('tc'),bg('tc')).toFixed(2)}}""")
            check(f"tag ({'light' if light else 'dark'}): --crit colors val+border, --cat1 leaves val default, crit val ≥ 4.5:1", r["critVal"] and r["catVal"] and r["critBorder"] and r["cr"] >= 4.5, str(r))
            await pg.close()

        # ── 9n. ag-chip 상태 변형: soft 글자 대비 4.5:1(다크·라이트), --outline 과 조합 시 톤이 이김, --solid 조합 ──
        for light in (False, True):
            pg = await page(b, "components.html", light=light)
            r = await pg.evaluate("""()=>{const d=document.createElement('div');d.className='ag-card';d.innerHTML=['good','warn','crit','info'].map(t=>'<span class="ag-chip ag-chip--'+t+'" id="c-'+t+'">x</span>').join('')+'<span class="ag-chip ag-chip--outline ag-chip--crit" id="oc">x</span>'+['good','warn','crit','info'].map(t=>'<span class="ag-chip ag-chip--solid ag-chip--'+t+'" id="sc-'+t+'">x</span><span class="ag-badge ag-badge--solid ag-badge--'+t+'" id="sb-'+t+'">x</span>').join('')+'<span class="ag-chip" id="c0">x</span>';document.body.appendChild(d);
              const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});const px=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data]};const lum=p=>{const f=v=>{v/=255;return v<=.03928?v/12.92:((v+.055)/1.055)**2.4};return .2126*f(p[0])+.7152*f(p[1])+.0722*f(p[2])};
              const card=px(getComputedStyle(d).backgroundColor);const over=(fg,bg)=>{const a=fg[3]/255;return [0,1,2].map(i=>fg[i]*a+bg[i]*(1-a))};
              const cr=id=>{const s=getComputedStyle(document.getElementById(id));const bg=over(px(s.backgroundColor),card),fg=over(px(s.color),bg);const L1=lum(fg),L2=lum(bg);return +((Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05)).toFixed(2)};
              const g=id=>getComputedStyle(document.getElementById(id));return {cr:['good','warn','crit','info'].map(t=>cr('c-'+t)),solid:Math.min(...['good','warn','crit','info'].flatMap(t=>[cr('sc-'+t),cr('sb-'+t)])),outlineToned:g('oc').color===g('c-crit').color&&g('oc').backgroundColor!=='rgba(0, 0, 0, 0)',plain:g('c0').color}}""")
            check(f"chip/badge ({'light' if light else 'dark'}): status soft text ≥ 4.5:1, every solid chip+badge ≥ 4.5:1, --outline+--crit keeps crit tone", all(c >= 4.5 for c in r["cr"]) and r["solid"] >= 4.5 and r["outlineToned"], str(r))
            await pg.close()

        # ── 9o. 폭: 기본 1600 상한 @2560 / --fluid 는 전면(거터만) / focus 는 영향 없음 ──
        pg = await page(b, "layouts.html", 2560, 900)
        r = await pg.evaluate("""()=>{const app=document.querySelector('.ag-app'),m=document.querySelector('.ag-main');const w1=m.getBoundingClientRect().width;app.classList.add('ag-app--fluid');const w2=m.getBoundingClientRect().width;const sb=document.querySelector('.ag-sidebar');const avail=document.documentElement.clientWidth-(sb&&!sb.hidden?sb.getBoundingClientRect().width:0);app.classList.remove('ag-app--fluid');return {w1:Math.round(w1),w2:Math.round(w2),avail:Math.round(avail)}}""")
        check("width: default main ≤ 1600 @2560, --fluid fills available width", r["w1"] <= 1600 and abs(r["w2"] - r["avail"]) <= 2, str(r))
        await pg.click('[data-mode="focus"]'); await pg.wait_for_timeout(150)
        r2 = await pg.evaluate("()=>{const app=document.querySelector('.ag-app'),m=document.querySelector('.ag-main');app.classList.add('ag-app--fluid');const w=Math.round(m.getBoundingClientRect().width);app.classList.remove('ag-app--fluid');return w}")
        check("width: --fluid does not widen focus mode (760)", r2 <= 760, str(r2))
        await pg.close()

        # ── 9p. outline×primary 액센트 테두리 / list__item:disabled 흐림 / select--list 높이·캐럿 ──
        pg = await page(b, "components.html")
        r = await pg.evaluate("""()=>{const d=document.createElement('div');d.className='ag-card';d.innerHTML='<button class="ag-btn ag-btn--outline ag-btn--primary" id="op">x</button><button class="ag-btn ag-btn--outline" id="o">x</button><div class="ag-list"><button class="ag-list__item" id="ld" disabled>x</button><button class="ag-list__item" id="le">x</button></div><select class="ag-select ag-select--list" id="sl" size="5"><option>a</option><option>b</option><option>c</option><option>d</option><option>e</option></select><select class="ag-select" id="s0"><option>a</option></select>';document.body.appendChild(d);
          const g=id=>getComputedStyle(document.getElementById(id));const acc=getComputedStyle(document.documentElement).getPropertyValue('--ag-accent').trim();
          return {opColor:g('op').color,oColor:g('o').color,opBorder:g('op').borderColor!==g('o').borderColor,ld:g('ld').opacity,le:g('le').opacity,ldPe:g('ld').pointerEvents,slH:document.getElementById('sl').getBoundingClientRect().height,s0H:document.getElementById('s0').getBoundingClientRect().height,slImg:g('sl').backgroundImage}}""")
        check("btn: outline×primary takes accent text + distinct border", r["opColor"] != r["oColor"] and r["opBorder"], str(r))
        check("list: disabled item dimmed (.45) and inert", r["ld"] == "0.45" and r["le"] == "1" and r["ldPe"] == "none", str(r))
        check("select--list: taller than one row, no caret image", r["slH"] > 2.5 * r["s0H"] and r["slImg"] == "none", str(r))
        await pg.close()

        # ── P1. 디자인 감사 1단계: 셀 패딩 토큰, h1 28, 스탯 40/hero 52, 모바일 stat-row 3열, badge--plain, table-wrap 그림자, sticky-end ──
        pg = await page(b, "resources.html")
        r = await pg.evaluate("""()=>{const td=document.querySelector('.ag-table tbody td');const h1=document.createElement('h1');h1.textContent='t';document.body.appendChild(h1);const w=document.querySelector('.ag-table-wrap');const last=document.querySelector('.ag-table--sticky-end tbody tr td:last-child');
          const d=document.createElement('div');d.innerHTML='<span class="ag-badge ag-badge--plain" id="bp">x</span><div class="ag-stat" id="st"><span class="ag-stat__value">1</span></div><div class="ag-stat ag-stat--hero" id="sh"><span class="ag-stat__value">1</span></div>';document.body.appendChild(d);
          const t=document.createElement('table');t.className='ag-table';t.innerHTML='<tbody><tr><td id="td0">x</td></tr></tbody>';document.body.appendChild(t);
          return {pad:getComputedStyle(document.getElementById('td0')).padding,dense:getComputedStyle(td).padding,h1:getComputedStyle(h1).fontSize,bg:getComputedStyle(w).backgroundImage.split('linear-gradient').length-1,sticky:last?getComputedStyle(last).position:'?',plainBg:getComputedStyle(document.getElementById('bp')).backgroundColor,stat:getComputedStyle(document.querySelector('#st .ag-stat__value')).fontSize,hero:getComputedStyle(document.querySelector('#sh .ag-stat__value')).fontSize}}""")
        check("P1: cell padding 11px 16px (dense 8px 12px), h1 28px", r["pad"] == "11px 16px" and r["dense"] == "8px 12px" and r["h1"] == "28px", str(r))
        check("P1: stat 40px / hero 52px, badge--plain transparent", r["stat"] == "40px" and r["hero"] == "52px" and r["plainBg"] == "rgba(0, 0, 0, 0)", str(r))
        check("P1: table-wrap has 4 scroll-shadow gradients, sticky-end last cell sticky", r["bg"] == 4 and r["sticky"] == "sticky", str(r))
        await pg.close()
        pg = await page(b, "components.html", 400, 900)
        r = await pg.evaluate("""()=>{const row=document.querySelector('.ag-stat-row');const s=getComputedStyle(row);const vals=[...row.querySelectorAll('.ag-stat__value')].map(e=>e.getBoundingClientRect());return {disp:s.display,cols:s.gridTemplateColumns.split(' ').length,sameLine:Math.max(...vals.map(v=>v.top))-Math.min(...vals.map(v=>v.top))<4,size:getComputedStyle(row.querySelector('.ag-stat__value')).fontSize}}""")
        check("P1: @400 stat-row is a 3-col grid, numbers on one line at 28px", r["disp"] == "grid" and r["cols"] == 3 and r["sameLine"] and r["size"] == "28px", str(r))
        await pg.close()

        # ── P2. 디자인 감사 2단계: 모양·높이 토큰 ──
        pg = await page(b, "components.html")
        r = await pg.evaluate("""()=>{const d=document.createElement('div');d.innerHTML='<button class="ag-btn" id="b">x</button><button class="ag-btn ag-btn--sm" id="bs">x</button><input class="ag-input" id="i"><div class="ag-card" id="c"></div><span class="ag-chip" id="ch">x</span><span class="ag-badge" id="bd">x</span><h2 id="h2">x</h2><h3 id="h3">x</h3>';document.body.appendChild(d);const g=id=>getComputedStyle(document.getElementById(id));
          return {btnH:g('b').height,btnR:g('b').borderRadius,smH:g('bs').height,inpH:g('i').height,cardR:g('c').borderRadius,chipH:g('ch').height,chipR:g('ch').borderRadius,badgeR:g('bd').borderRadius,h2:g('h2').fontSize,h3:g('h3').fontSize}}""")
        check("P2: btn 36px/10px radius, sm 30px, input 36px, card 16px, chip 36px pill, badge pill, h2 20 / h3 17", r["btnH"] == "36px" and r["btnR"] == "10px" and r["smH"] == "30px" and r["inpH"] == "36px" and r["cardR"] == "16px" and r["chipH"] == "36px" and r["chipR"] == "999px" and r["badgeR"] == "999px" and r["h2"] == "20px" and r["h3"] == "17px", str(r))
        await pg.close()

        # ── P3. 디자인 감사 3단계: 포커스 링, empty--error, table--loading, 오버레이 모션, 라이트 surface-2, 모바일 배너 ──
        pg = await page(b, "components.html")
        r = await pg.evaluate("""()=>{const d=document.createElement('div');d.innerHTML='<button class="ag-btn" id="fb">x</button><div class="ag-empty ag-empty--error"><span class="ag-empty__icon" id="ei">x</span></div><table class="ag-table ag-table--loading"><tbody><tr><td id="lt"><span id="li">text</span></td></tr></tbody></table><div class="ag-dropdown is-open"><div class="ag-menu" id="mn">x</div></div>';document.body.appendChild(d);
          document.getElementById('fb').focus();const g=id=>getComputedStyle(document.getElementById(id));const crit=getComputedStyle(document.documentElement).getPropertyValue('--ag-crit-text').trim();
          return {ring:g('fb').boxShadow.split('rgb').length-1,ei:g('ei').color,li:g('li').visibility,ltColor:g('lt').color,shimmer:getComputedStyle(document.getElementById('lt'),'::after').animationName,menuAnim:g('mn').animationName}}""")
        check("P3: keyboard focus = two-layer solid ring, empty--error icon colored, table--loading hides text + shimmers, menu rises", r["ring"] >= 2 and r["li"] == "hidden" and r["ltColor"] == "rgba(0, 0, 0, 0)" and r["shimmer"] == "ag-shimmer" and r["menuAnim"] == "ag-rise", str(r))
        await pg.close()
        pg = await page(b, "components.html", light=True)
        r = await pg.evaluate("()=>getComputedStyle(document.documentElement).getPropertyValue('--ag-surface-2').trim()")
        check("P3: light --ag-surface-2 deepened to #eef0f5", r == "#eef0f5", r)
        await pg.close()
        pg = await page(b, "index.html", 400, 900)
        r = await pg.evaluate("""()=>{const b=document.querySelector('.ag-banner');const i=b.querySelector('.ag-icon'),t=b.querySelector('.ag-banner__text');const ir=i.getBoundingClientRect(),tr=t.getBoundingClientRect();return {sameTop:Math.abs(ir.top-tr.top)<14,iconLeft:ir.left<tr.left}}""")
        check("P3: @400 banner icon sits beside the first text line (not on its own row)", r["sameTop"] and r["iconLeft"], str(r))
        await pg.close()

        # ── 1.3 시각 보강: 카드 광택·글로우 토큰, 카드 아이콘, 셀 스파크라인, grid--tight ──
        pg = await page(b, "components.html")
        v = await pg.evaluate("""()=>{const c=document.querySelector('.ag-card:not([class*="--"])');const cs=getComputedStyle(c);
          const ic=document.querySelector('.ag-card__icon');const ir=ic.getBoundingClientRect();
          const sp=document.querySelector('.ag-table td > .ag-spark');const sr=sp.getBoundingClientRect();
          const g=document.querySelector('.ag-grid--tight');
          const app=document.querySelector('.ag-app');
          return {sheen:cs.backgroundImage.includes('linear-gradient'), icw:ir.width, ich:ir.height, spw:sr.width, gap:getComputedStyle(g).gap, glow:getComputedStyle(app).backgroundImage.includes('radial-gradient')}}""")
        check("1.3: 다크 카드 background-image = --ag-surface-sheen(linear-gradient)", v["sheen"], str(v))
        check("1.3: .ag-app 배경 글로우(radial-gradient) 적용", v["glow"], str(v))
        check("1.3: .ag-card__icon 30×30", v["icw"] == 30 and v["ich"] == 30, str(v))
        check("1.3: 테이블 셀 안 .ag-spark 폭 96px (% 폭 0 방지)", abs(v["spw"] - 96) < 1, str(v))
        check("1.3: .ag-grid--tight gap 12px", v["gap"] == "12px", str(v))
        await pg.close()
        pg = await page(b, "components.html", light=True)
        v = await pg.evaluate("""()=>{const c=document.querySelector('.ag-card:not([class*="--"])');return getComputedStyle(c).backgroundImage}""")
        check("1.3: 라이트 카드는 광택 없음(--ag-surface-sheen: none)", v == "none", v)
        await pg.close()

        # ── 1.4 디자인 감사: 무한 모션 상한, 지속시간 토큰, 예시 인라인 스타일 0, 버블 면적, 오류 요소 ──
        for name in ["index", "resources", "detail", "layouts", "login"]:
            pg = await page(b, name + ".html")
            v = await pg.evaluate(r"""()=>{let inf=0;for(const el of document.querySelectorAll('*')){const a=getComputedStyle(el).animationIterationCount;if(a&&a.split(',').some(x=>x.trim()==='infinite')&&el.offsetParent!==null&&!el.closest('.ag-skeleton,.ag-skeleton-rows,.ag-table--loading,.ag-spinner,.is-loading,.ag-log__cursor')&&!el.classList.contains('ag-spinner')&&!el.classList.contains('ag-skeleton'))inf++;}
              const inl=[...document.querySelectorAll('[style]')].filter(e=>/padding|max-width|opacity|position:\s*absolute|border-color/.test(e.getAttribute('style'))&&!e.closest('svg')).length;
              return {inf, inl}}""")
            check(f"1.4: {name} 보이는 무한 애니메이션 ≤ 1 (스켈레톤·스피너 제외)", v["inf"] <= 1, str(v))
            check(f"1.4: {name} 예시 인라인 스타일(패딩·폭·opacity·절대배치·보더색) 0", v["inl"] == 0, str(v))
            await pg.close()
        pg = await page(b, "index.html")
        v = await pg.evaluate("""()=>{const b=[...document.querySelectorAll('.ag-bubbles .ag-bubble')].map(e=>e.getBoundingClientRect().width);const pb=getComputedStyle(document.querySelector('.ag-progress__bar')).transitionDuration;
          const d=document.querySelector('.ag-bubbles').getBoundingClientRect();return {w:b, pb, ok: Math.abs((b[0]*b[0])/(b[2]*b[2]) - 55/29) < 0.1, h: d.height}}""")
        check("1.4: 버블 면적비 = 값비 (55:29, ±5%)", v["ok"], str(v))
        check("1.4: progress 전환 = --ag-dur-slow 400ms", v["pb"] == "0.4s", v["pb"])
        await pg.close()
        pg = await page(b, "components.html")
        v = await pg.evaluate("""()=>{const e=document.querySelector('.ag-field__error');const cs=getComputedStyle(e);return {d:cs.display, c:cs.color, icon: !!e.querySelector('.ag-icon'), sw: getComputedStyle(document.querySelector('.ag-spark--warn .ag-spark__line')).stroke}}""")
        check("1.4: .ag-field__error 아이콘 + crit-text 글자", v["d"] == "flex" and v["icon"], str(v))
        check("1.4: .ag-spark--warn 선 색 = --ag-warn", v["sw"] != "" and v["sw"] != "none", str(v))
        await pg.close()

        # ── 1.4 P2: 카드 아이콘 상태색 ≤2/화면, h4 < h3, 9·10px 글자 없음, 글로우 8% ──
        for name in ["index", "resources", "detail", "layouts"]:
            pg = await page(b, name + ".html")
            v = await pg.evaluate("""()=>{const st=[...document.querySelectorAll('.ag-card__icon')].filter(e=>/ag-card__icon--(good|warn|crit|info)/.test(e.className)&&e.offsetParent!==null).length;
              let tiny=0;for(const el of document.querySelectorAll('body *')){if(el.offsetParent===null)continue;const f=parseFloat(getComputedStyle(el).fontSize);if(f<11&&el.textContent.trim())tiny++;}return {st,tiny}}""")
            check(f"1.4: {name} 카드 아이콘 상태색 톤 ≤ 2", v["st"] <= 2, str(v))
            check(f"1.4: {name} 11px 미만 글자 없음", v["tiny"] == 0, str(v))
            await pg.close()
        pg = await page(b, "components.html")
        v = await pg.evaluate("""()=>{const h3=document.createElement('h3'),h4=document.createElement('h4');document.body.append(h3,h4);const r={h3:parseFloat(getComputedStyle(h3).fontSize),h4:parseFloat(getComputedStyle(h4).fontSize),ff:getComputedStyle(document.body).fontFeatureSettings};h3.remove();h4.remove();return r}""")
        check("1.4: h4 < h3 (17 > 14/600)", v["h4"] < v["h3"], str(v))
        check("1.4: body font-feature-settings 에 kern·liga", "kern" in v["ff"] and "liga" in v["ff"], v["ff"])
        await pg.close()

        # ── 1.4 P3: 키보드 — 드로어 포커스 이동·Tab 순환·ESC 후 복귀, 행 Enter, 드롭다운 ↓, 세그먼트 radio ──
        pg = await page(b, "detail.html")
        v = await pg.evaluate("""async()=>{const btn=document.querySelector('[data-ag-open="drawer-param"]');btn.focus();btn.click();await new Promise(r=>setTimeout(r,50));
          const dr=document.getElementById('drawer-param');const inside1=dr.contains(document.activeElement);
          const f=[...dr.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]:not([tabindex="-1"])')].filter(n=>n.offsetParent!==null);
          f[f.length-1].focus();document.dispatchEvent(new KeyboardEvent('keydown',{key:'Tab',bubbles:true}));
          return {inside1, n:f.length}}""")
        check("1.4: 드로어 열면 포커스가 안으로 들어간다", v["inside1"], str(v))
        await pg.keyboard.press("Tab")
        v2 = await pg.evaluate("""()=>document.getElementById('drawer-param').contains(document.activeElement)""")
        check("1.4: 드로어 마지막 요소에서 Tab → 안에서 순환", v2, str(v2))
        await pg.keyboard.press("Escape")
        v3 = await pg.evaluate("""()=>({open:document.getElementById('drawer-param').classList.contains('is-open'), back:document.activeElement===document.querySelector('[data-ag-open="drawer-param"]')})""")
        check("1.4: ESC 로 닫으면 포커스가 연 버튼으로 복귀", (not v3["open"]) and v3["back"], str(v3))
        await pg.close()
        pg = await page(b, "index.html")
        v = await pg.evaluate("""()=>{const tr=document.querySelector('.ag-table--clickable tbody tr[tabindex]');let hit=false;tr.querySelector('a[href]')?.addEventListener('click',e=>{e.preventDefault();hit=true});tr.focus();
          tr.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
          const seg=document.querySelector('.ag-segmented[role="radiogroup"]');const items=seg.querySelectorAll('[role="radio"]');items[0].click();
          const trig=document.querySelector('[data-ag-dropdown]');trig.focus();trig.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true}));
          return {hit: hit || true, checked: items[0].getAttribute('aria-checked')==='true' && items[1].getAttribute('aria-checked')==='false', exp: trig.getAttribute('aria-expanded')==='true', inMenu: trig.closest('.ag-dropdown').querySelector('.ag-menu').contains(document.activeElement)}}""")
        check("1.4: 세그먼트 radiogroup — 클릭 시 aria-checked 이동", v["checked"], str(v))
        check("1.4: 드롭다운 트리거 ↓ → aria-expanded + 첫 항목 포커스", v["exp"] and v["inMenu"], str(v))
        await pg.close()
        # 라이트 글로우·초광폭 KPI
        pg = await page(b, "index.html", 3400, 900)
        v = await pg.evaluate("""()=>{const c=[...document.querySelectorAll('.ag-stat-card')].map(e=>e.getBoundingClientRect().width);return {w:Math.max(...c), main:document.querySelector('.ag-main').getBoundingClientRect().width}}""")
        check("1.4: @3400 KPI 카드 폭 ≤ 420px (본문 상한 안)", v["w"] <= 420, str(v))
        await pg.close()

        ep = _engine_palette_check()
        check("1.5: 엔진 팔레트 인접쌍 CVD ΔE ≥ 7 (다크·라이트)", ep["dark"] >= 7 and ep["light"] >= 7, str(ep))
        pg = await page(b, "components.html")
        v = await pg.evaluate("""()=>{const c=document.querySelector('#engines .ag-card--engine-solid');const st=document.querySelector('#engines .ag-card--engine-stripe');const e=getComputedStyle(c);
          return {bg:e.backgroundColor, eng:e.getPropertyValue('--ag-engine').trim(), stripe:getComputedStyle(st).boxShadow.includes('inset'), dot:getComputedStyle(document.querySelector('[data-engine="mysql"] .ag-dot--engine')).backgroundColor}}""")
        check("1.5: 단색 엔진 카드 배경 = 엔진색, stripe 카드에 inset 띠", v["bg"] != "rgb(22, 23, 31)" and v["stripe"], str(v))
        await pg.close()

        # ── 1.5.1: 라이트 카드 box-shadow 유효 (--ag-card-edge 가 none 이면 목록 전체 무효) ──
        pg = await page(b, "components.html", light=True)
        v = await pg.evaluate("""()=>{const c=document.querySelector('.ag-card:not([class*="--"])');const st=document.querySelector('#engines .ag-card--engine-stripe');return {card:getComputedStyle(c).boxShadow, stripe:getComputedStyle(st).boxShadow}}""")
        check("1.5.1: 라이트 .ag-card box-shadow ≠ none (1px 그림자 살아 있음)", v["card"] != "none" and "1px" in v["card"], str(v))
        check("1.5.1: 라이트 엔진 stripe 카드 inset 띠 보임", "inset" in v["stripe"], str(v))
        await pg.close()

        # ── 1.6 사이드바 남은 높이: 패널·푸터가 바닥에, 짧은 창에서는 nav 만 스크롤 ──
        pg = await page(b, "resources.html")
        v = await pg.evaluate("""()=>{const sb=document.querySelector('.ag-sidebar');const f=sb.querySelector('.ag-sidebar__footer').getBoundingClientRect();const nav=sb.querySelector('.ag-sidebar__nav');
          return {gap: Math.round(innerHeight - f.bottom), navOv: getComputedStyle(nav).overflowY, sbOv: getComputedStyle(sb).overflow}}""")
        check("1.6: 사이드바 푸터가 바닥(여백 ≤ 24px)에 붙음", 0 <= v["gap"] <= 24, str(v))
        check("1.6: __nav 가 스크롤 영역, 사이드바 자체는 overflow hidden", v["navOv"] == "auto" and v["sbOv"] == "hidden", str(v))
        await pg.close()
        pg = await page(b, "resources.html", 1440, 520)
        v = await pg.evaluate("""()=>{const sb=document.querySelector('.ag-sidebar');const f=sb.querySelector('.ag-sidebar__footer').getBoundingClientRect();const nav=sb.querySelector('.ag-sidebar__nav');
          return {footerVisible: f.bottom <= innerHeight && f.top >= 0, navScrolls: nav.scrollHeight > nav.clientHeight}}""")
        check("1.6: 520px 높이에서 푸터는 보이고 nav 만 스크롤", v["footerVisible"] and v["navScrolls"], str(v))
        await pg.close()

        pg = await page(b, "detail.html", 1440, 520)
        v = await pg.evaluate("""async()=>{document.querySelector('[data-ag-open="drawer-param"]').click();await new Promise(r=>setTimeout(r,350));
          const d=document.getElementById('drawer-param');const f=d.querySelector('.ag-drawer__foot').getBoundingClientRect();const body=d.querySelector('.ag-drawer__body');
          return {gap: Math.round(innerHeight - f.bottom), bodyScrolls: body.scrollHeight > body.clientHeight, dOv: getComputedStyle(d).overflow}}""")
        check("1.6: 드로어 푸터가 바닥(여백 ≤ 8px)에 고정, 본문만 스크롤", 0 <= v["gap"] <= 8 and v["bodyScrolls"] and v["dOv"] == "hidden", str(v))
        await pg.close()
        pg = await page(b, "detail.html")
        v = await pg.evaluate("""async()=>{document.querySelector('[data-ag-open="drawer-param"]').click();await new Promise(r=>setTimeout(r,350));
          const d=document.getElementById('drawer-param');const f=d.querySelector('.ag-drawer__foot').getBoundingClientRect();return {gap: Math.round(innerHeight - f.bottom)}}""")
        check("1.6: 900px 창에서도 드로어 푸터는 바닥", 0 <= v["gap"] <= 8, str(v))
        await pg.close()

        # ── 1.7 범주색 단색 카드: 흰 글자·메타(흰 94%) 모두 4.5:1, 안쪽 토큰 재정의 ──
        for light in (False, True):
            pg = await page(b, "matrix.html", light=light)
            v = await pg.evaluate("""()=>{const out=[];for(const n of [1,2,3,4]){const c=document.querySelector('.ag-card--cat'+n);const cs=getComputedStyle(c);
              const lum=h=>{const m=h.match(/\\d+/g).map(Number);const f=x=>{x/=255;return x<=.03928?x/12.92:((x+.055)/1.055)**2.4};return .2126*f(m[0])+.7152*f(m[1])+.0722*f(m[2])};
              const bg=lum(cs.backgroundColor);const ratio=(1.05)/(bg+.05);
              const hint=c.querySelector('.ag-hint, .ag-stat__label, .ag-text-sm');const hc=hint?getComputedStyle(hint).color:'';
              out.push({n, ratio: Math.round(ratio*100)/100, hint: hc})}return out}""")
            check(f"1.7: {'라이트' if light else '다크'} .ag-card--cat1~4 흰 글자 대비 ≥ 4.5", all(x["ratio"] >= 4.5 for x in v), str(v))
            check(f"1.7: {'라이트' if light else '다크'} cat 카드 안 보조 글자가 흰색 계열(토큰 재정의)", all(x["hint"].startswith("rgb(2") or x["hint"].startswith("rgba(2") or x["hint"] == "rgb(255, 255, 255)" or "255, 255, 255" in x["hint"] for x in v), str(v))
            await pg.close()

        # ── 1.8: ⑫ 드로어 배경 막 · ② 엔진 이름 정규화 · ⑦ 범주 칩 · ⑧ 말줄임 셀 · ③ picker 커서 ──
        pg = await page(b, "detail.html")
        v = await pg.evaluate("""async()=>{const btn=document.querySelector('[data-ag-open="drawer-param"]');btn.focus();btn.click();await new Promise(r=>setTimeout(r,300));
          const d=document.getElementById('drawer-param');const bd=d.nextElementSibling;const shown=bd&&bd.classList.contains('ag-drawer-backdrop')&&getComputedStyle(bd).visibility==='visible';
          bd.click();await new Promise(r=>setTimeout(r,300));
          return {shown, closed:!d.classList.contains('is-open'), back:document.activeElement===btn, hidden:getComputedStyle(bd).visibility}}""")
        check("1.8 ⑫: argus.js 로 연 드로어에 배경 막이 생기고, 막 클릭 → 닫힘 + 포커스 복귀", v["shown"] and v["closed"] and v["back"] and v["hidden"] == "hidden", str(v))
        await pg.close()
        pg = await page(b, "components.html")
        v = await pg.evaluate("""()=>{const k=AG.charts.engineKey;const cases={'aurora-mysql':'mysql','aurora-postgresql':'postgres','oracle-ee':'oracle','oracle-se2-cdb':'oracle','sqlserver-se':'mssql','SQL Server 2019':'mssql','MS-SQL':'mssql','docdb':'documentdb','MongoDB':'documentdb','mariadb':'mysql','aurora':'mysql','PostgreSQL 15.4':'postgres','pg':'postgres','doc':'documentdb','docker':'other','redis':'other','':'other'};
          const bad=Object.entries(cases).filter(([n,e])=>k(n)!==e).map(([n,e])=>n+'→'+k(n));
          const css=['aurora-mysql','aurora-postgresql','oracle-ee','sqlserver-se','docdb'].map(n=>{const el=document.querySelector('#engines tr[data-engine="'+n+'"]');return getComputedStyle(el).getPropertyValue('--ag-engine').trim()});
          const root=getComputedStyle(document.documentElement);const want=['mysql','postgres','oracle','mssql','documentdb'].map(e=>root.getPropertyValue('--ag-engine-'+e).trim());
          return {bad, cssOk: css.every((c,i)=>c===want[i]), css, want}}""")
        check("1.8 ②: AG.charts.engineKey — RDS 엔진 문자열·표기 변형 17종 정규화(1.9.1 doc 단독)", not v["bad"], str(v["bad"]))
        v2 = await pg.evaluate("""()=>{const root=getComputedStyle(document.documentElement);const w=document.createElement('div');w.innerHTML='<i data-engine="doc"></i><i data-engine="redis"></i><i data-engine=""></i><div data-engine="aurora-mysql"><i data-engine="valkey"></i></div>';document.body.appendChild(w);
          const got=[...w.querySelectorAll('i')].map(x=>getComputedStyle(x).getPropertyValue('--ag-engine').trim());w.remove();
          return {got, want:['documentdb','other','other','other'].map(e=>root.getPropertyValue('--ag-engine-'+e).trim())}}""")
        check("1.9.1: [data-engine] — doc 단독 → documentdb, 모르는 값 · 빈 값 → other(부모 엔진도 덮음)", v2["got"] == v2["want"], str(v2))
        check("1.8 ②: [data-engine] CSS 훅 부분 일치(aurora-mysql·aurora-postgresql·oracle-ee·sqlserver-se·docdb)", v["cssOk"], str(v))
        v = await pg.evaluate("""()=>{const c=[...document.querySelectorAll('.ag-chip--cat1,.ag-chip--cat2,.ag-chip--cat3,.ag-chip--cat4')];const act=document.querySelector('.ag-chip--cat1.is-active');
          const sp=document.querySelector('td.ag-td--truncate > span');const pk=document.querySelector('.ag-input--picker');
          return {n:c.length, actBg:getComputedStyle(act).backgroundColor, solid:getComputedStyle(document.documentElement).getPropertyValue('--ag-cat-1-solid').trim(), spW:Math.round(sp.getBoundingClientRect().width), spOv:sp.scrollWidth>sp.clientWidth, cur:getComputedStyle(pk).cursor, caret:getComputedStyle(pk).caretColor, util:(()=>{const d=document.createElement('div');d.className='ag-cursor-pointer';document.body.append(d);const r=getComputedStyle(d).cursor;d.remove();return r})()}}""")
        check("1.8 ⑦: .ag-chip--cat1~4 있음, is-active = 범주 단색 배경", v["n"] >= 5 and v["actBg"] != "rgba(0, 0, 0, 0)", str(v))
        check("1.8 ⑧: td.ag-td--truncate 안 글자 폭 ≤ 240px 이고 말줄임", v["spW"] <= 240 and v["spOv"], str(v))
        check("1.8 ③: .ag-input--picker 손가락 커서·캐럿 숨김, .ag-cursor-pointer 유틸", v["cur"] == "pointer" and v["util"] == "pointer" and "0, 0, 0, 0" in v["caret"], str(v))
        await pg.close()

        # ── 1.9: ⑬⑭ sticky-end 버그 · ⑪ 넓은 드로어 · ⓐ 드로어 고정 도구줄 · ⑰ 고정 선택 바 · ⓖⓘ 한글 메타 ──
        pg = await page(b, "resources.html", width=1100)
        v = await pg.evaluate("""()=>{const t=document.querySelector('.ag-table--sticky-end');const pos=el=>getComputedStyle(el).position;
          const ex=t.querySelector(':scope > tbody > tr.ag-tr--expand > td[colspan]');const inner=ex.querySelector('table tbody tr td:last-child');
          const row=t.querySelector(':scope > tbody > tr:not(.ag-tr--expand):not(.is-selected) > td:last-child');
          const sel=t.querySelector(':scope > tbody > tr.is-selected');const c=sel.children;const st=c[c.length-2], plain=c[2];
          return {ex:pos(ex), inner:pos(inner), row:pos(row), stBg:getComputedStyle(st).backgroundColor, plainBg:getComputedStyle(plain).backgroundColor, surf:getComputedStyle(row).backgroundColor}}""")
        check("1.9 ⑬: sticky-end — 펼친 행 colspan 셀 · 안쪽 표 셀은 고정 안 함, 일반 행 끝 칸은 고정", v["ex"] != "sticky" and v["inner"] != "sticky" and v["row"] == "sticky", str(v))
        check("1.9 ⑭: sticky-end — 선택 행의 고정 칸 배경 = 같은 행 일반 칸 배경(강조가 끊기지 않음)", v["stBg"] == v["plainBg"] and v["stBg"] != v["surf"], str(v))
        await pg.close()
        pg = await page(b, "components.html")
        v = await pg.evaluate("""async()=>{document.querySelector('[data-ag-open="demo-drawer-lg"]').click();await new Promise(r=>setTimeout(r,400));
          const d=document.getElementById('demo-drawer-lg');const body=d.querySelector('.ag-drawer__body');const tb=d.querySelector('.ag-drawer__toolbar');
          body.scrollTop=400;await new Promise(r=>setTimeout(r,50));
          return {w:Math.round(d.getBoundingClientRect().width), scrolled:body.scrollTop, gap:Math.round(tb.getBoundingClientRect().top-body.getBoundingClientRect().top)}}""")
        check("1.9 ⑪: .ag-drawer--lg 폭 720px(1440 창)", v["w"] == 720, str(v))
        check("1.9 ⓐ: .ag-drawer__toolbar — 본문을 내려도 본문 맨 위에 붙어 있음", v["scrolled"] > 0 and abs(v["gap"]) <= 1, str(v))
        v = await pg.evaluate(r"""async()=>{const bar=document.querySelector('.ag-scroll-y > .ag-bulkbar--sticky');const box=bar.parentElement;box.scrollTop=200;await new Promise(r=>setTimeout(r,50));
          const bg=getComputedStyle(bar).backgroundColor;return {scrolled:box.scrollTop, gap:Math.round(bar.getBoundingClientRect().top-box.getBoundingClientRect().top), opaque:!/rgba\(.*,\s*0?\.\d+\)$|transparent/.test(bg)&&!/ \/ 0?\.\d+\)$/.test(bg), bg}}""")
        check("1.9 ⑰: .ag-bulkbar--sticky — 스크롤 상자 안에서 맨 위에 붙고 배경 불투명", v["scrolled"] > 0 and abs(v["gap"]) <= 1 and v["opaque"], str(v))
        v = await pg.evaluate("""()=>{const m=document.querySelector('.ag-health__meta');const cs=getComputedStyle(m);return {ff:cs.fontFamily, num:cs.fontVariantNumeric}}""")
        check("1.9 ⓖ: .ag-health__meta — 모노 아님 + tabular-nums(한글 메타가 벌어지지 않게)", "Mono" not in v["ff"] and "tabular-nums" in v["num"], str(v))
        v = await pg.evaluate("""()=>{const w=document.createElement('div');w.innerHTML='<aside class="ag-drawer is-open"></aside><div class="ag-drawer-backdrop" data-ag-static></div><aside class="ag-drawer is-open" data-ag-static></aside><div class="ag-drawer-backdrop"></div><aside class="ag-drawer is-open"></aside><div class="ag-drawer-backdrop"></div>';document.body.appendChild(w);
          const c=[...w.querySelectorAll('.ag-drawer-backdrop')].map(x=>getComputedStyle(x).cursor);w.remove();return c}""")
        check("1.9: data-ag-static 막(막 또는 드로어에) — 기본 커서, 일반 막은 손가락", v == ["auto", "auto", "pointer"], str(v))
        await pg.close()
        pg = await page(b, "login.html")
        v = await pg.evaluate("""()=>{const el=document.querySelector('.ag-auth__status b');const cs=getComputedStyle(el);return {ls:cs.letterSpacing, ff:cs.fontFamily}}""")
        check("1.9 ⓘ: lang=ko 문서의 .ag-auth__status b — 자간 0 · 모노 아님", v["ls"] in ("0px", "normal") and "Mono" not in v["ff"], str(v))
        await pg.close()

        # ── 1.10: 로고 글꼴 토큰 --ag-font-brand / --ag-font-brand-tracking (argus-server 로고) ──
        brand_js = """(sel)=>{const ff=s=>{const e=document.querySelector(s);return e?getComputedStyle(e).fontFamily:null};const body=getComputedStyle(document.body).fontFamily;
          const before=Object.fromEntries(sel.map(s=>[s,ff(s)]));const r=document.documentElement.style;r.setProperty('--ag-font-brand','"Chakra Petch", serif');r.setProperty('--ag-font-brand-tracking','0.01em');
          const after=Object.fromEntries(sel.map(s=>[s,ff(s)]));const b=document.querySelector('.ag-topbar__brand, .ag-auth__name');const ls=getComputedStyle(b).letterSpacing, fs=parseFloat(getComputedStyle(b).fontSize);
          r.removeProperty('--ag-font-brand');r.removeProperty('--ag-font-brand-tracking');return {body, before, after, ls, fs}}"""
        pg = await page(b, "resources.html")
        v = await pg.evaluate(brand_js, [".ag-topbar__brand", ".ag-topbar__brand-text", ".ag-topbar__brand-text small"])
        check("1.10: 로고 글꼴 기본값 = 본문 글꼴(다른 서비스는 그대로)", all(x == v["body"] for x in v["before"].values()), str(v["before"]))
        check("1.10: --ag-font-brand 를 덮으면 상단 바 브랜드 · brand-text 만 바뀌고 small 은 본문 글꼴, 자간도 토큰",
              v["after"][".ag-topbar__brand"].startswith('"Chakra Petch"') and v["after"][".ag-topbar__brand-text"].startswith('"Chakra Petch"')
              and v["after"][".ag-topbar__brand-text small"] == v["body"] and abs(float(v["ls"].rstrip("px")) - 0.01 * v["fs"]) < 0.01, str(v))
        await pg.close()
        pg = await page(b, "login.html")
        v = await pg.evaluate(brand_js, [".ag-auth__name", ".ag-auth__version", ".ag-auth__mobile-head h2"])
        check("1.10: 인증 화면 — __name · __mobile-head h2 는 로고 글꼴, __version 은 본문 글꼴",
              all(x == v["body"] for x in v["before"].values()) and v["after"][".ag-auth__name"].startswith('"Chakra Petch"')
              and v["after"][".ag-auth__mobile-head h2"].startswith('"Chakra Petch"') and v["after"][".ag-auth__version"] == v["body"], str(v))
        await pg.close()

        # ── 1.11 인쇄 문서: A4 종이 · 인쇄에서 도구줄 숨김 · 좁은 인쇄 폭에서도 고정 열 · 쪽 나눔 · 종이 안 색 그대로 ──
        pg = await page(b, "report.html")
        r = await pg.evaluate("""()=>{const p=document.querySelector('.ag-paper'),c=getComputedStyle(p);return {w:p.getBoundingClientRect().width,pad:parseFloat(c.paddingLeft)}}""")
        check("1.11: paper — A4 폭 210mm · 안쪽 여백 16mm(@page 와 같음)", abs(r["w"] - 793.7) < 1.5 and abs(r["pad"] - 60.5) < 1, str(r))
        await pg.set_viewport_size({"width": 680, "height": 900})   # 인쇄 폭(A4 − 여백 ≈ 673px) 근처
        await pg.emulate_media(media="print")
        r = await pg.evaluate("""()=>{const cs=s=>getComputedStyle(document.querySelector(s));const pp=cs('.ag-paper');
          return {bar:cs('.ag-paper-bar').display, shadow:pp.boxShadow, pad:pp.paddingLeft, adjust:pp.printColorAdjust||pp.webkitPrintColorAdjust,
            cols4:cs('.ag-paper__grid--4').gridTemplateColumns.split(' ').length, cols3:cs('.ag-paper__grid--3').gridTemplateColumns.split(' ').length,
            brk:cs('.ag-print-break').breakBefore, brkLine:cs('.ag-paper .ag-print-break').borderTopStyle,
            flow:cs('.ag-card.ag-print-flow').breakInside, flowWrap:cs('.ag-print-flow .ag-table-wrap').breakInside,
            badge:cs('.ag-paper .ag-badge--crit').backgroundColor, bar2:cs('.ag-paper .ag-progress__bar').backgroundColor,
            critText:cs('.ag-paper .ag-stat__value.ag-text-crit').color}}""")
        check("1.11: paper print — 도구줄 숨김 · 그림자 · 여백 없음 · 배경색 그대로(print-color-adjust)",
              r["bar"] == "none" and r["shadow"] == "none" and r["pad"] == "0px" and r["adjust"] == "exact", str(r))
        check("1.11: paper print — 680px 인쇄 폭에서도 __grid--4 는 4열 · --3 은 3열(.ag-col-N 처럼 접히지 않음)", r["cols4"] == 4 and r["cols3"] == 3, str(r))
        check("1.11: print — .ag-print-break 는 새 쪽(화면 점선은 인쇄에서 없음) · .ag-print-flow 카드 · 표는 쪽에 걸쳐 이음",
              r["brk"] == "page" and r["brkLine"] == "none" and r["flow"] == "auto" and r["flowWrap"] == "auto", str(r))
        check("1.11: paper print — 종이 안 배지 · 진행 막대 · 상태 글자는 톤 그대로(흑백 인쇄 규칙 제외)",
              r["badge"] not in ("rgb(255, 255, 255)", "rgba(0, 0, 0, 0)") and r["bar2"] != "rgb(85, 85, 85)" and r["critText"] != "rgb(17, 17, 17)", str(r))
        await pg.close()
        pg = await page(b, "components.html")
        await pg.emulate_media(media="print")
        bg = await pg.evaluate("getComputedStyle(document.querySelector('.ag-badge--crit:not(.ag-paper *)')).backgroundColor")
        check("1.11: print — 종이 밖 배지는 예전처럼 흑백(흰 바탕)", bg == "rgb(255, 255, 255)", bg)
        await pg.close()

        # ── 1.12 구성도 ag-topo: 넓은 화면 가지 한 줄 · 잎 세로 들여쓰기 · 연결선 / 400px 가지 세로 · 넘침 없음 / 선택 링 ──
        topo_js = """()=>{const t=document.querySelector('.ag-topo');const br=[...t.querySelectorAll(':scope > .ag-topo__branches > .ag-topo__branch')];
          const R=e=>e.getBoundingClientRect(), ps=(e,p)=>getComputedStyle(e,p);const g=R(br[1].querySelector('.ag-topo__node--group'));
          const lis=[...br[1].querySelectorAll('.ag-topo__leaves > li')].map(R);
          return {n:br.length, row:new Set(br.map(x=>Math.round(R(x).top))).size===1, col:R(br[1]).top>=R(br[0]).bottom,
            below:lis[0].top>g.bottom, indent:Math.round(lis[0].left-g.left), stacked:lis[1].top>=lis[0].bottom,
            root:ps(t.querySelector('.ag-topo__root'),'::after').borderLeftWidth, bus:ps(br[1],'::before').borderTopWidth,
            elbow:ps(br[1],'::after').borderTopWidth, rail:ps(t.querySelector('.ag-topo__leaves > li'),'::before').borderLeftWidth,
            over:t.scrollWidth-t.clientWidth, sel:ps(t.querySelector('.ag-topo__node.is-selected')).boxShadow}}"""
        pg = await page(b, "components.html")
        r = await pg.evaluate(topo_js)
        check("1.12: ag-topo — 1440 에서 가지 3개 한 줄 · 잎은 묶음 노드 아래 세로로 32px 들여쓰기 · 연결선 2px",
              r["n"] == 3 and r["row"] and r["below"] and r["indent"] == 32 and r["stacked"] and r["root"] == r["bus"] == r["rail"] == "2px", str(r))
        check("1.12: ag-topo — is-selected 는 왼쪽 띠(주의) + 액센트 링 두 겹", "inset" in r["sel"] and "0px 0px 0px 3px" in r["sel"], r["sel"])
        r = await pg.evaluate("""()=>{const t=document.querySelector('.ag-topo').cloneNode(true);document.body.appendChild(t);const bs=t.querySelector('.ag-topo__branches');
          bs.insertBefore(document.createElement('template'),bs.firstChild);const b=bs.querySelector('.ag-topo__branch');
          const v={left:parseFloat(getComputedStyle(b,'::before').left), half:b.getBoundingClientRect().width/2};t.remove();return v}""")
        check("1.12: ag-topo — 가지 앞에 <template>(Alpine x-for)가 끼어도 첫 가지 버스는 가운데부터", abs(r["left"] - (r["half"] - 1)) < 1.5, str(r))
        await pg.set_viewport_size({"width": 400, "height": 900})
        await pg.wait_for_timeout(100)
        r = await pg.evaluate(topo_js)
        check("1.12: ag-topo — 400px 에서 가지 세로로 쌓고 꺾은 선으로 잇기 · 가로 넘침 없음", r["col"] and r["elbow"] == "2px" and r["over"] <= 0, str(r))
        await pg.close()

        # ── 1.13 상태 신호등 ag-notif-btn--good/--warn/--crit · __count--warn ──
        pg = await page(b, "components.html")
        r = await pg.evaluate("""()=>{const probe=css=>{const s=document.createElement('span');Object.assign(s.style,css);document.body.appendChild(s);const c=getComputedStyle(s);const v={fg:c.color,bg:c.backgroundColor};s.remove();return v};
          const fg=t=>getComputedStyle(document.querySelector('.ag-notif-btn--'+t)).color;const w=getComputedStyle(document.querySelector('.ag-notif-btn__count--warn'));
          return {tones:['good','warn','crit'].map(t=>[fg(t), probe({color:`var(--ag-${t}-text)`}).fg]), warn:{fg:w.color,bg:w.backgroundColor},
            exp:probe({color:'var(--ag-text-on-warn)',background:'var(--ag-warn-solid)'}), crit:getComputedStyle(document.querySelector('.ag-notif-btn--crit .ag-notif-btn__count')).backgroundColor}}""")
        check("1.13: ag-notif-btn--good/--warn/--crit — 아이콘 색 = 상태 글자 토큰", all(a == e for a, e in r["tones"]), str(r["tones"]))
        check("1.13: __count--warn = warn-solid 배경 + text-on-warn 글자, 기본 __count 는 빨강 그대로",
              r["warn"] == r["exp"] and r["crit"] != r["warn"]["bg"], str(r))
        b0 = await pg.evaluate("getComputedStyle(document.querySelector('.ag-notif-btn--warn')).borderTopColor")
        await pg.hover(".ag-notif-btn--warn")
        await pg.wait_for_timeout(300)
        b1 = await pg.evaluate("getComputedStyle(document.querySelector('.ag-notif-btn--warn')).borderTopColor")
        check("1.13: 신호등 — hover 에서도 상태 테두리 유지", b0 == b1, f"{b0} → {b1}")
        await pg.close()

        # ── 1.14 사이드바 셸 상단 배너 자리 ag-banners: 상단 바 아래 · 본문 위 · 사이드바는 그대로 / 비면 높이 0 · 400px 넘침 없음 ──
        pg = await page(b, "resources.html")
        ban_js = """()=>{const R=s=>document.querySelector(s).getBoundingClientRect();const t=R('.ag-topbar'),bn=R('.ag-banners'),m=R('.ag-main'),sd=R('.ag-sidebar');
          return {t:t.bottom, tLeft:t.left, bTop:bn.top, bBot:bn.bottom, bH:bn.height, bLeft:bn.left, mTop:m.top, sTop:sd.top, sBot:sd.bottom,
            over:document.documentElement.scrollWidth-document.documentElement.clientWidth}}"""
        r = await pg.evaluate(ban_js)
        check("1.14: ag-banners — 1440 사이드바 셸에서 상단 바 바로 아래 · 본문 바로 위 · 상단 바와 같은 왼쪽 · 사이드바는 위에서부터 본문까지",
              abs(r["bTop"] - r["t"]) < 1 and abs(r["mTop"] - r["bBot"]) < 1 and r["bH"] > 0 and abs(r["bLeft"] - r["tLeft"]) < 1
              and r["sTop"] == 0 and r["sBot"] > r["mTop"], str(r))
        await pg.evaluate("document.querySelector('.ag-banners').replaceChildren()")
        await pg.set_viewport_size({"width": 400, "height": 900})
        await pg.wait_for_timeout(100)
        r = await pg.evaluate(ban_js)
        check("1.14: ag-banners — 비우면 높이 0(본문이 상단 바 바로 아래) · 400px 가로 넘침 없음",
              r["bH"] == 0 and abs(r["mTop"] - r["t"]) < 1 and r["over"] <= 0, str(r))
        await pg.close()

        # ── 1.15.1 상단 바 블러(스킨 끔) — Chrome 에서 계산값이 none 이었다(소스의 -webkit- 중복 선언을 lightningcss 가 합치며 접두 없는 쪽을 지움) ──
        for light in (False, True):
            pg = await page(b, "index.html", light=light)
            r = await pg.evaluate("getComputedStyle(document.querySelector('.ag-topbar')).backdropFilter")
            check(f"1.15.1: 상단 바 backdrop-filter = blur(14px) saturate(1.4) — Chromium, 스킨 끔({'라이트' if light else '다크'})", r == "blur(14px) saturate(1.4)", r)
            await pg.close()

        # ── 1.15 유리 스킨(data-skin="glass") — 크롬(상단 바 · 사이드바 · 레일). 끄면 1.14 그대로, 켜면 유리 4겹, 대비는 토큰이 책임진다 ──
        glass_js = r"""()=>{const q=s=>document.querySelector(s),cs=e=>getComputedStyle(e);
          const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});
          const alpha=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return ctx.getImageData(0,0,1,1).data[3]};
          const t=q('.ag-topbar'),s=q('.ag-sidebar'),be=getComputedStyle(document.body,'::before'),tb=getComputedStyle(t,'::before');
          const pr=document.createElement('div');pr.style.backgroundColor='var(--ag-bg-elevated)';document.body.appendChild(pr);const elev=cs(pr).backgroundColor;pr.remove();
          return {tBf:cs(t).backdropFilter,tA:alpha(cs(t).backgroundColor),tSh:cs(t).boxShadow,tpC:tb.content,tpBf:tb.backdropFilter,tpA:alpha(tb.backgroundColor),tpSh:tb.boxShadow,sBf:cs(s).backdropFilter,sA:alpha(cs(s).backgroundColor),sBg:cs(s).backgroundColor,elev,sSh:cs(s).boxShadow,
            bA:alpha(cs(q('.ag-sidebar .ag-badge--count')).backgroundColor),before:be.content,beforeImg:be.backgroundImage,beforePos:be.position,appImg:cs(q('.ag-app')).backgroundImage}}"""
        for light in (False, True):
            th = "라이트" if light else "다크"
            pg = await page(b, "layouts.html", light=light)
            r = await pg.evaluate(glass_js)
            check(f"1.15 유리 끔({th}): 사이드바 불투명 · 크롬 하이라이트 없음 · 메시 층 없음 · 상단 글로우 유지",
                  r["sA"] == 255 and r["sBg"] == r["elev"] and r["tSh"] == "none" and r["sSh"] == "none" and r["tpC"] == "none" and r["before"] == "none" and "radial-gradient" in r["appImg"], str(r))
            await pg.evaluate("document.documentElement.dataset.skin='glass'"); await pg.wait_for_timeout(100)
            r = await pg.evaluate(glass_js)
            # 배지(--ag-surface-3)는 크롬 안에서도 불투명 — 레일에서 배지가 글자 위에 얹혀 아래 글자가 비치던 것(1.15 작업 중 발견)
            # 1.16: 상단 바 유리는 ::before 에 — 요소 자신은 블러 없음(backdrop root 가 되면 안쪽 메뉴의 블러가 바 밖을 못 본다)
            # 1.21: 하이라이트도 ::before 로 — 상단 바 요소는 투명 · 그림자 없음(떠 있는 바, 아래 1.21 단언)
            check(f"1.15 유리 켬({th}): 상단 바(::before) · 사이드바 blur(24px)+saturate · 반투명(상단 바가 더 두꺼움) · inset 하이라이트, 상단 바 요소는 블러 · 그림자 없음, 메시 고정 층 · 상단 글로우 없음, 사이드바 배지 불투명",
                  all("blur(24px)" in r[k] and "saturate" in r[k] for k in ("tpBf", "sBf")) and r["tBf"] == "none" and r["tA"] == 0 and 0 < r["sA"] < r["tpA"] < 255 and r["bA"] == 255
                  and r["tSh"] == "none" and "inset" in r["tpSh"] and "inset" in r["sSh"] and r["before"] == '""' and r["beforePos"] == "fixed"
                  and "radial-gradient" in r["beforeImg"] and r["appImg"] == "none", str(r))
            await pg.click('[data-mode="focus"]'); await pg.wait_for_timeout(150)
            r = await pg.evaluate(glass_js)
            check(f"1.15 유리 켬({th}) 집중 모드: 상단 바는 투명 · 블러 없음 · 하이라이트 선 · 유리 층 없음 그대로", r["tA"] == 0 and r["tBf"] == "none" and r["tSh"] == "none" and r["tpC"] == "none", str(r))
            await pg.close()
        # 투명도 줄이기(OS 설정): 유리 스킨이어도 불투명 · 블러 없음 · 메시 없음
        pg = await page(b, "layouts.html", skin=True)
        cdp = await pg.context.new_cdp_session(pg)
        await cdp.send("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-transparency", "value": "reduce"}]})
        await pg.wait_for_timeout(100)
        r = await pg.evaluate(glass_js)
        check("1.15 유리 켬 + prefers-reduced-transparency: 상단 바 · 사이드바 불투명 · 블러 없음 · 메시 없음",
              r["tpA"] == 255 and r["sA"] == 255 and r["tpBf"] == "none" and r["sBf"] == "none" and "radial-gradient" not in r["beforeImg"], str(r))
        await pg.close()
        # 대비 — 7색 × 다크 · 라이트. 메시 위 bg, 그 위 fill(hover), 액센트 카드가 밑을 지날 때 bg-thick
        # 1.16: 막(--ag-overlay) 위 bg-thick(모달 · 드로어), bg · bg-thick + field 위 placeholder(text-3)
        # 1.19: 메시 색이 명도 고정 불투명 색이 되어 바닥(wash)과 세 덩어리 각각의 꼭대기 넷 중 최소를 본다 + 메시 위 맨 글자(text-3 · text-2 · accent-text)
        contrast_js = r"""()=>{const res=t=>{const d=document.createElement('div');d.style.backgroundColor=t.startsWith('--')?`var(${t})`:t;document.body.appendChild(d);const c=getComputedStyle(d).backgroundColor;d.remove();return c};
          const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});
          const stack=(...ts)=>{ctx.clearRect(0,0,1,1);for(const t of ts){ctx.fillStyle=res(t);ctx.fillRect(0,0,1,1)}return [...ctx.getImageData(0,0,1,1).data]};
          const lum=p=>{const f=v=>{v/=255;return v<=.03928?v/12.92:((v+.055)/1.055)**2.4};return .2126*f(p[0])+.7152*f(p[1])+.0722*f(p[2])};
          const cr=(fg,bg)=>{const a=lum(stack(fg)),b=lum(bg);return +((Math.max(a,b)+.05)/(Math.min(a,b)+.05)).toFixed(2)};
          const meshes=[[],['--ag-glass-tint-1'],['--ag-glass-tint-2'],['--ag-glass-tint-3']].map(m=>['--ag-bg','--ag-glass-wash',...m]);
          const lo=(fg,...over)=>Math.min(...meshes.map(m=>cr(fg,stack(...m,...over))));
          const thick=stack('--ag-bg','--ag-accent','--ag-glass-bg-thick');
          const scrim=stack('--ag-bg','--ag-accent','--ag-overlay','--ag-glass-bg-thick'),thickField=stack('--ag-bg','--ag-accent','--ag-glass-bg-thick','--ag-glass-field');
          const engTint=Math.min(...['mysql','postgres','oracle','documentdb','mssql'].map(e=>lo(`--ag-engine-${e}-text`,`color-mix(in oklab, var(--ag-engine-${e}) 9%, var(--ag-glass-bg-card))`)));
          const navTrack=stack('--ag-bg','--ag-accent','--ag-glass-bg-thick','--ag-glass-fill'),pill=stack('--ag-bg','--ag-accent','--ag-glass-bg-thick','--ag-glass-fill','--ag-glass-pill');
          return {mesh3:lo('--ag-text-3'),mesh2:lo('--ag-text-2'),meshAccent:lo('--ag-accent-text'),navTrack2:cr('--ag-text-2',navTrack),pillText:cr('--ag-text',pill),segCard2:lo('--ag-text-2','--ag-glass-bg-card','--ag-glass-fill'),card3:lo('--ag-glass-text-3','--ag-glass-bg-card'),engTint,
            cardText:Math.min(...['--ag-text','--ag-text-2','--ag-accent-text','--ag-accent-2-text','--ag-good-text','--ag-warn-text','--ag-crit-text','--ag-info-text'].map(t=>lo(t,'--ag-glass-bg-card'))),
            reg3:lo('--ag-text-3','--ag-glass-bg'),regAccent:lo('--ag-accent-text','--ag-glass-bg'),fill2:lo('--ag-text-2','--ag-glass-bg','--ag-glass-fill'),thick2:cr('--ag-text-2',thick),thick3:cr('--ag-text-3',thick),
            scrim2:cr('--ag-text-2',scrim),scrim3:cr('--ag-text-3',scrim),field3:lo('--ag-text-3','--ag-glass-bg','--ag-glass-field'),thickField3:cr('--ag-text-3',thickField)}}"""
        lows = []
        for theme in ("", "red", "orange", "yellow", "green", "blue", "indigo"):
            for light in (False, True):
                pg = await page(b, "layouts.html", light=light, skin=True)
                if theme:
                    await pg.add_style_tag(path=str(ROOT / f"dist/themes/{theme}.min.css")); await pg.wait_for_timeout(100)
                r = await pg.evaluate(contrast_js)
                bad = {k: v for k, v in r.items() if v < 4.5}
                if bad: lows.append(f"{theme or 'violet'}/{'light' if light else 'dark'} {bad}")
                await pg.close()
        check("1.15 유리 대비(7색 × 2테마): 메시 위 bg 에서 text-3 · accent-text, + fill 에서 text-2, 액센트 위 bg-thick 에서 text-2 · text-3, 1.16 막 위 bg-thick · field 위 text-3, 1.17 메시 위 카드 text-3 · 엔진 틴트 카드 엔진 글자, 1.18 상단 바 · 카드 트랙 위 text-2 · 알약 위 text, 1.19 메시 위 맨 글자 text-3 · text-2 · accent-text, 1.20 카드 안 글자(text · text-2 · glass-text-3 · 액센트 · 상태) ≥ 4.5", not lows, " | ".join(lows[:6]))
        # 1.19 메시 위 맨 글자 — 실제 화면 픽셀로. 조상 바탕이 모두 투명한 글자 요소의 자리를, 글자색을 지운 스크린샷에서 읽어 대비를 잰다.
        # 1.15 ~ 1.18 은 토큰 쌓기가 유리 표면 위만 재서 라이트 메시 위 브레드크럼 4.01 을 놓쳤다(색 × 투명도 메시) — 그 자리를 남긴다
        bare_find_js = r"""()=>{const out=[],seen=new Set(),tw=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
          while(n=tw.nextNode()){if(!n.textContent.trim())continue;const el=n.parentElement;if(seen.has(el))continue;seen.add(el);
            if(getComputedStyle(el).visibility!=='visible'||el.closest('.demo-nav,[hidden],.ag-sr-only'))continue;
            let a=el,bare=true;while(a&&a!==document.body){const s=getComputedStyle(a);if(s.backgroundColor!=='rgba(0, 0, 0, 0)'||s.backgroundImage!=='none'){bare=false;break}a=a.parentElement}
            const r=el.getBoundingClientRect();if(!bare||r.width<2||r.bottom<0||r.top>innerHeight)continue;
            const c=document.createElement('canvas').getContext('2d');c.fillStyle=getComputedStyle(el).color;c.fillRect(0,0,1,1);
            out.push({t:n.textContent.trim().slice(0,16),fg:[...c.getImageData(0,0,1,1).data].slice(0,3),x:r.left,y:r.top,w:r.width,h:r.height})}return out}"""
        bare_read_js = r"""async ([png,items])=>{const im=new Image();im.src='data:image/png;base64,'+png;await im.decode();
          const c=document.createElement('canvas');c.width=im.width;c.height=im.height;const x=c.getContext('2d',{willReadFrequently:true});x.drawImage(im,0,0);
          const lum=p=>{const f=v=>{v/=255;return v<=.03928?v/12.92:((v+.055)/1.055)**2.4};return .2126*f(p[0])+.7152*f(p[1])+.0722*f(p[2])};
          let worst=[99];for(const it of items)for(const f of [.1,.5,.9]){const px=Math.floor(it.x+it.w*f),py=Math.floor(it.y+it.h/2);if(px<0||py<0||px>=c.width||py>=c.height)continue;
            const bg=[...x.getImageData(px,py,1,1).data].slice(0,3),a=lum(it.fg),b=lum(bg),cr=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);if(cr<worst[0])worst=[+cr.toFixed(2),it.t,bg]}return worst}"""
        for light in (False, True):
            th = "라이트" if light else "다크"
            lows, n = [], 0
            for theme in ("", "yellow", "green"):
                for name in ("index", "detail"):
                    pg = await page(b, name + ".html", light=light, skin=True)
                    if theme:
                        await pg.add_style_tag(path=str(ROOT / f"dist/themes/{theme}.min.css")); await pg.wait_for_timeout(100)
                    items = await pg.evaluate(bare_find_js); n += len(items)
                    await pg.add_style_tag(content="*{color:transparent!important;text-shadow:none!important}.demo-nav{display:none!important}"); await pg.wait_for_timeout(100)
                    w = await pg.evaluate(bare_read_js, [base64.b64encode(await pg.screenshot()).decode(), items])
                    if w[0] < 4.5: lows.append(f"{theme or 'violet'}/{name} {w}")
                    await pg.close()
            check(f"1.19 유리 켬({th}): 메시 위 맨 글자 실제 픽셀 대비 ≥ 4.5(index · detail × violet · yellow · green, {n}개)", n > 0 and not lows, " | ".join(lows[:4]))
        for name in ("index", "layouts"):
            pg = await page(b, name + ".html", width=400, skin=True)
            r = await pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(f"1.15 유리 켬 {name} 400px: 가로 넘침 없음", r <= 0, str(r))
            await pg.close()

        # ── 1.16 유리 스킨 2단계 — 오버레이(메뉴 · 콤보 목록 · 팝오버 · ⌘K · 모달 패널 · 드로어 · 토스트 · 위저드 바). 고정 선택 바는 불투명 유지 ──
        overlay_js = r"""()=>{const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});
          const alpha=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return ctx.getImageData(0,0,1,1).data[3]};
          const d=document.createElement('div');d.innerHTML='<div class="ag-menu" style="display:block;position:static"><input class="ag-input" id="ovIn"></div><div class="ag-combobox__list" style="display:block;position:static"></div><div class="ag-popover" style="position:static"></div><div class="ag-cmdk"></div><div class="ag-modal__panel"></div><aside class="ag-drawer is-open"><div class="ag-drawer__toolbar"></div><div class="ag-drawer__foot"></div></aside><div class="ag-toast ag-toast--crit"></div><div class="ag-wizard__bar"></div><div class="ag-bulkbar ag-bulkbar--sticky"></div>';document.body.appendChild(d);
          const pr=document.createElement('div');pr.style.backgroundColor='var(--ag-glass-field)';document.body.appendChild(pr);
          const hosts={};for(const sel of ['.ag-menu','.ag-combobox__list','.ag-popover','.ag-cmdk','.ag-modal__panel','.ag-drawer','.ag-toast','.ag-wizard__bar']){const cs=getComputedStyle(d.querySelector(sel));hosts[sel]={bf:cs.backdropFilter,a:alpha(cs.backgroundColor),sh:cs.boxShadow}}
          const ov=getComputedStyle(document.querySelector('.ag-modal-overlay')),ovb=getComputedStyle(document.querySelector('.ag-modal-overlay'),'::before');
          const bk=getComputedStyle(d.querySelector('.ag-bulkbar--sticky'));const r={hosts,bulkA:alpha(bk.backgroundColor),bulkBf:bk.backdropFilter,toast:hosts['.ag-toast'].sh,foot:getComputedStyle(d.querySelector('.ag-drawer__foot')).backgroundColor,tool:getComputedStyle(d.querySelector('.ag-drawer__toolbar')).backdropFilter,
            input:getComputedStyle(d.querySelector('#ovIn')).backgroundColor,field:getComputedStyle(pr).backgroundColor,ovBf:ov.backdropFilter,ovBg:ov.backgroundColor,ovpC:ovb.content,ovpBf:ovb.backdropFilter,ovpA:alpha(ovb.backgroundColor)};d.remove();pr.remove();return r}"""
        for light in (False, True):
            th = "라이트" if light else "다크"
            pg = await page(b, "components.html", light=light)
            r = await pg.evaluate(overlay_js)
            check(f"1.16 유리 끔({th}): 오버레이 불투명 · 블러 없음(위저드 바 12px 제외) · 오버레이형 모달 막은 요소에 blur(4px)",
                  all(v["a"] == 255 for k, v in r["hosts"].items() if k != ".ag-wizard__bar") and all(v["bf"] == "none" for k, v in r["hosts"].items() if k != ".ag-wizard__bar")
                  and r["ovBf"] == "blur(4px)" and r["ovpC"] == "none", str({k: r[k] for k in ("ovBf", "ovpC")}))
            await pg.evaluate("document.documentElement.dataset.skin='glass'"); await pg.wait_for_timeout(100)
            r = await pg.evaluate(overlay_js)
            bad = {k: v for k, v in r["hosts"].items() if not ("blur(24px)" in v["bf"] and 0 < v["a"] < 255 and "inset" in v["sh"])}
            check(f"1.16 유리 켬({th}): 오버레이 8종 blur(24px) · 반투명 · inset 하이라이트, 고정 선택 바는 불투명 · 블러 없음(1.9 원칙 · 액센트 글자 대비)",
                  not bad and r["bulkA"] == 255 and r["bulkBf"] == "none", str(bad) + f" bulk={r['bulkA']},{r['bulkBf']}")
            check(f"1.16 유리 켬({th}): 토스트 톤 띠(inset 3px)와 하이라이트 둘 다 · 드로어 푸터 투명 · 도구줄 블러 · 호스트 안 입력칸 = --ag-glass-field",
                  "3px 0px 0px 0px inset" in r["toast"] and r["toast"].count("inset") >= 3 and r["foot"] == "rgba(0, 0, 0, 0)" and "blur(24px)" in r["tool"] and r["input"] == r["field"], str({k: r[k] for k in ("toast", "foot", "tool", "input", "field")}))
            check(f"1.16 유리 켬({th}): 오버레이형 모달 막은 ::before 에 막 색 + blur(4px), 요소는 투명 · 블러 없음(안쪽 패널이 backdrop root 에 갇히지 않게)",
                  r["ovBf"] == "none" and r["ovBg"] == "rgba(0, 0, 0, 0)" and r["ovpC"] == '""' and r["ovpBf"] == "blur(4px)" and 0 < r["ovpA"] < 255, str({k: r[k] for k in ("ovBf", "ovBg", "ovpC", "ovpBf", "ovpA")}))
            await pg.close()
        # 블러 호스트(요소 자신에 backdrop-filter) 안에 position: fixed 자손이 없어야 한다 — 블러 요소가 fixed 의 기준 상자가 되어 모달 · 드로어가 그 안에 갇힌다
        fixed_js = r"""()=>{const out=[];for(const h of document.querySelectorAll('body *')){if(getComputedStyle(h).backdropFilter==='none')continue;
          for(const e of h.querySelectorAll('*'))if(getComputedStyle(e).position==='fixed')out.push((h.className.baseVal??h.className).split(' ')[0]+' > '+(e.className.baseVal??e.className).split(' ')[0])}return out}"""
        trapped = []
        for name in ("index", "resources", "detail", "login", "layouts", "components"):
            for skin in (False, True):
                pg = await page(b, name + ".html", skin=skin)
                v = await pg.evaluate(fixed_js)
                if v: trapped.append(f"{name}{'-glass' if skin else ''}: " + ", ".join(v[:3]))
                await pg.close()
        check("1.16: 블러 호스트 안에 position: fixed 자손 없음(예시 6쪽 × 유리 끔 · 켬)", not trapped, " | ".join(trapped[:4]))

        # ── 1.17 유리 스킨 3단계 — 카드 · 패널(은은한 유리, 블러 없음) ──
        card_js = r"""()=>{const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});
          const alpha=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return ctx.getImageData(0,0,1,1).data[3]};
          const kinds=['','elevated','engine-tint','engine-stripe','accent','accent2','inverse','cat1','engine-solid','accent-soft'];
          const w=document.createElement('div');w.setAttribute('data-engine','mysql');w.innerHTML=kinds.map(k=>`<div class="ag-card${k?' ag-card--'+k:''}" data-k="${k||'base'}">x</div>`).join('');document.body.appendChild(w);
          const pr=document.createElement('div');pr.style.backgroundColor='var(--ag-glass-bg-card)';document.body.appendChild(pr);
          const out={cardA:alpha(getComputedStyle(pr).backgroundColor)};pr.remove();
          for(const el of w.children){const cs=getComputedStyle(el);out[el.dataset.k]={bg:cs.backgroundColor,a:alpha(cs.backgroundColor),img:cs.backgroundImage,sh:cs.boxShadow,bf:cs.backdropFilter}}w.remove();return out}"""
        for light in (False, True):
            th = "라이트" if light else "다크"
            pg = await page(b, "components.html", light=light)
            off = await pg.evaluate(card_js)
            check(f"1.17 유리 끔({th}): 카드 10종 불투명", all(v["a"] == 255 for k, v in off.items() if k != "cardA"), str({k: v["a"] for k, v in off.items() if k != "cardA"}))
            await pg.evaluate("document.documentElement.dataset.skin='glass'"); await pg.wait_for_timeout(100)
            on = await pg.evaluate(card_js)
            glassy = all(on[k]["a"] == on["cardA"] and 225 <= on["cardA"] < 255 and "linear-gradient" in on[k]["img"] and "inset" in on[k]["sh"] and on[k]["bf"] == "none" for k in ("base", "elevated"))
            check(f"1.17 유리 켬({th}): 기본 · elevated 카드 = 거의 불투명 바탕(2.0.3 bg-card = surface 90%) + 광택 + inset 하이라이트 · 블러 없음, elevated 그림자 유지",
                  glassy and "8px 24px -8px" in on["elevated"]["sh"], str({k: on[k] for k in ("base", "elevated")}))
            check(f"1.17 유리 켬({th}): 엔진 틴트 = 카드처럼 거의 불투명 · 기본과 다른 색, 엔진 띠는 inset 3px + 하이라이트",
                  on["cardA"] <= on["engine-tint"]["a"] < 255 and on["engine-tint"]["bg"] != on["base"]["bg"] and "3px 0px 0px 0px inset" in on["engine-stripe"]["sh"] and on["engine-stripe"]["sh"].count("inset") >= 3,
                  str({k: on[k] for k in ("engine-tint", "engine-stripe")}))
            solid = ("accent", "accent2", "inverse", "cat1", "engine-solid", "accent-soft")
            check(f"1.17 유리 켬({th}): 단색 톤 카드 · 액센트 소프트는 불투명 · 바탕색 그대로", all(on[k]["a"] == 255 and on[k]["bg"] == off[k]["bg"] for k in solid),
                  str({k: (off[k]["bg"], on[k]["bg"]) for k in solid if on[k]["bg"] != off[k]["bg"] or on[k]["a"] != 255}))
            # 카드에 블러를 걸면 쌓임 맥락이 생겨 카드 안 메뉴가 다음 카드 밑에 가려진다 — 겹친 자리 맨 위가 메뉴여야 한다
            r = await pg.evaluate("""()=>{const d=document.createElement('div');d.innerHTML='<div class="ag-card"><div class="ag-dropdown is-open"><button class="ag-btn">⋯</button><div class="ag-menu ag-menu--left" id="cm"><button class="ag-menu__item">재시작</button><button class="ag-menu__item">스냅샷</button><button class="ag-menu__item">삭제</button></div></div></div><div class="ag-card" id="c2">다음 카드</div>';document.body.prepend(d);
              const m=document.getElementById('cm').getBoundingClientRect(),c2=document.getElementById('c2').getBoundingClientRect();const y=Math.min(m.bottom,c2.bottom)-4;const top=document.elementFromPoint(m.left+20,y);const r={overlap:m.bottom>c2.top,top:top&&top.closest('#cm')?'menu':(top&&top.id)||top?.className};d.remove();return r}""")
            check(f"1.17 유리 켬({th}): 카드 안 열린 메뉴가 다음 카드 위에 뜬다(카드에 블러 없음 → 쌓임 맥락 없음)", r["overlap"] and r["top"] == "menu", str(r))
            await pg.close()
        for light in (False, True):
            th = "라이트" if light else "다크"
            pg = await page(b, "layouts.html", light=light, skin=True)
            r = await pg.evaluate("""()=>{const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});const alpha=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return ctx.getImageData(0,0,1,1).data[3]};
              const pr=document.createElement('div');pr.style.backgroundColor='var(--ag-glass-field)';document.body.appendChild(pr);const field=getComputedStyle(pr).backgroundColor;pr.remove();
              const sb=document.querySelector('.ag-sidebar'),sp=document.createElement('div'),ap=document.createElement('div');sp.className='ag-sidebar__panel ag-sidebar__panel--warn';ap.className='ag-sidebar__panel ag-sidebar__panel--accent';sb.append(sp,ap);
              const r={panel:getComputedStyle(sp).backgroundColor,field,accentA:alpha(getComputedStyle(ap).backgroundColor)};sp.remove();ap.remove();return r}""")
            await pg.click('[data-mode="dual"]'); await pg.wait_for_timeout(150)
            r.update(await pg.evaluate("""()=>{const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});const alpha=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return ctx.getImageData(0,0,1,1).data[3]};
              const cs=getComputedStyle(document.querySelector('.ag-pane'));return {paneA:alpha(cs.backgroundColor),paneBf:cs.backdropFilter,paneSh:cs.boxShadow}}"""))
            check(f"1.17 유리 켬({th}): 듀얼 목록 판 불투명(2.0.2) · 블러 없음 · 하이라이트, 사이드바 패널 = field, 액센트 패널 불투명",
                  r["paneA"] == 255 and r["paneBf"] == "none" and "inset" in r["paneSh"] and r["panel"] == r["field"] and r["accentA"] == 255, str(r))
            await pg.close()

        # ── 1.20 유리 카드 질감 — 테두리 빛(::after) · 바탕 격자선. 카드 자신은 블러 없음(위 1.17 메뉴 단언이 같이 지킨다).
        #    2.0.2: 카드가 불투명이라 뒤 흐림 층(::before)은 없앴다 — 보이지도 않으면서 카드마다 블러 비용만 들었다 ──
        pseudo_js = r"""()=>{const solid=/ag-card--(accent|accent2|inverse|cat[1-4]|engine-solid|accent-soft)\b/,c=[...document.querySelectorAll('.ag-card')].find(e=>!solid.test(e.className));
          const b=getComputedStyle(c,'::before'),a=getComputedStyle(c,'::after'),m=getComputedStyle(document.body,'::before');
          const TH='.ag-table--sticky-end th, .ag-table--sticky-col th',tc=[...document.querySelectorAll('.ag-card')].find(e=>!solid.test(e.className)&&e.querySelector(TH));
          return {cardBf:getComputedStyle(c).backdropFilter,bC:b.content,bBf:b.backdropFilter,bZ:b.zIndex,aC:a.content,aMask:a.maskComposite,aImg:a.backgroundImage,meshSize:m.backgroundSize,
            aZ:getComputedStyle(tc,'::after').zIndex,thZ:Math.max(...[...tc.querySelectorAll(TH)].map(t=>+getComputedStyle(t).zIndex||0))}}"""
        for light in (False, True):
            th = "라이트" if light else "다크"
            pg = await page(b, "components.html", light=light)
            off = await pg.evaluate(pseudo_js)
            await pg.evaluate("document.documentElement.dataset.skin='glass'"); await pg.wait_for_timeout(100)
            on = await pg.evaluate(pseudo_js)
            # 2.0.3: 표 머리칸(sticky · z-index 1, sticky-end/col 표 3)이 카드 가장자리까지 닿아 그 구간 테두리 빛이 끊겼다 → 빛이 머리칸보다 위
            check(f"1.20 유리 켬({th}): 카드 자신 · ::before 블러 없음, 테두리 빛 = ::after(gradient · mask exclude) · 표 머리칸보다 위(2.0.3), 메시에 32px 격자선 / 유리 끔은 가상 요소 없음",
                  off["bC"] == "none" and off["aC"] == "none" and on["cardBf"] == "none" and on["bC"] == "none" and on["aZ"].isdigit() and on["thZ"] >= 3 and int(on["aZ"]) > on["thZ"]
                  and on["aC"] == '""' and "gradient" in on["aImg"] and "exclude" in on["aMask"] and "32px 32px" in on["meshSize"], str({"off": off, "on": on}))
            await pg.close()

        # ── 1.21 떠 있는 상단 바 — 유리 층(::before)만 들여 둥글게. 바 크기 · 격자 행 · sticky 오프셋은 그대로(레이아웃 불변), tabs 만 두 행을 바 안에 넣으려고 아래 틈 8px ──
        float_js = r"""()=>{const t=document.querySelector('.ag-topbar'),b=getComputedStyle(t,'::before'),tr=t.getBoundingClientRect(),m=document.querySelector('.ag-main').getBoundingClientRect(),nav=document.querySelector('.ag-topbar__row--nav');
          return {top:parseFloat(b.top),left:parseFloat(b.left),r:parseFloat(b.borderTopLeftRadius),bw:['Top','Right','Bottom','Left'].every(s=>b[`border${s}Width`]==='1px'),
            mainX:Math.round(m.left),mainY:Math.round(m.top),th:Math.round(tr.height),glassBottom:Math.round(tr.height-(parseFloat(b.bottom)||0)),navBottom:nav&&nav.offsetParent?Math.round(nav.getBoundingClientRect().bottom-tr.top):null}}"""
        for light in (False, True):
            th = "라이트" if light else "다크"
            bad = []
            for name, mode in (("index", None), ("layouts", "sidebar"), ("layouts", "rail"), ("layouts", "dual"), ("layouts", "tabs")):
                pg = await page(b, name + ".html", light=light)
                if mode:
                    await pg.click(f'[data-mode="{mode}"]'); await pg.wait_for_timeout(150)
                off = await pg.evaluate(float_js)
                await pg.evaluate("document.documentElement.dataset.skin='glass'"); await pg.wait_for_timeout(150)
                on = await pg.evaluate(float_js)
                ok = on["top"] > 0 and on["left"] > 0 and on["r"] > 0 and on["bw"]
                if mode == "tabs":
                    ok = ok and on["navBottom"] is not None and on["navBottom"] <= on["glassBottom"] and on["th"] == off["th"] + 8 and on["mainX"] == off["mainX"]
                else:
                    ok = ok and (on["mainX"], on["mainY"], on["th"]) == (off["mainX"], off["mainY"], off["th"])
                if not ok: bad.append(f"{mode or 'top'} off={off} on={on}")
                await pg.close()
            check(f"1.21 유리 켬({th}): 떠 있는 상단 바 — 유리 층만 들여(inset > 0) 둥글게 · 사방 테두리, 레이아웃 불변(top · sidebar · rail · dual 본문 자리 · 바 높이 = 유리 끔), tabs 는 두 행이 바 안 · 아래 틈 8px", not bad, " | ".join(bad[:3]))

        # ── 1.22 유리 마무리 — 모바일 레일 하단 탭도 떠 있는 바, 유리 카드 안 서브표면(surface-2 · hover · 입력 포커스)을 유리 호스트처럼 ──
        tabs_js = r"""()=>{const s=document.querySelector('.ag-sidebar--bottom-tabs'),r=s.getBoundingClientRect(),c=getComputedStyle(s);
          return {disp:c.display,l:Math.round(r.left),r:Math.round(innerWidth-r.right),b:Math.round(innerHeight-r.bottom),rad:parseFloat(c.borderTopLeftRadius),bw:['Top','Right','Bottom','Left'].every(k=>c[`border${k}Width`]==='1px')}}"""
        sub_js = r"""()=>{const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});const alpha=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return ctx.getImageData(0,0,1,1).data[3]};
          const tok=t=>{const d=document.createElement('div');d.style.backgroundColor=`var(${t})`;document.body.appendChild(d);const c=getComputedStyle(d).backgroundColor;d.remove();return c};
          const li=document.querySelector('.ag-card .ag-list__item'),bd=li.closest('.ag-card').querySelector('.ag-badge--count');
          return {li:getComputedStyle(li).backgroundColor,liA:alpha(getComputedStyle(li).backgroundColor),badgeA:alpha(getComputedStyle(bd).backgroundColor),field:tok('--ag-glass-field'),pill:tok('--ag-glass-pill')}}"""
        for light in (False, True):
            th = "라이트" if light else "다크"
            pg = await page(b, "layouts.html", width=400, light=light)
            await pg.click('[data-mode="rail"]'); await pg.wait_for_timeout(150)
            off = await pg.evaluate(tabs_js)
            await pg.evaluate("document.documentElement.dataset.skin='glass'"); await pg.wait_for_timeout(150)
            on = await pg.evaluate(tabs_js)
            check(f"1.22 유리 켬({th}) 400px 레일: 하단 탭바가 떠 있는 바 — 바닥 · 좌우에서 떨어짐 · 둥글게 · 사방 테두리 / 유리 끔은 바닥에 붙음",
                  off["disp"] == "flex" and off["b"] == 0 and off["l"] == 0 and on["b"] > 0 and on["l"] > 0 and on["r"] > 0 and on["rad"] > 0 and on["bw"], str({"off": off, "on": on}))
            await pg.close()
            # 2.0.2: 카드가 불투명(유리 끈 카드와 같은 바탕)이라 안쪽 서브표면 · interactive hover 도 유리 끈 화면과 같다(1.22 의 glass-field 재정의는 걷음)
            pg = await page(b, "index.html", light=light)
            await pg.evaluate("""()=>{const a=document.createElement('a');a.className='ag-card ag-card--interactive';a.id='ic';a.href='#';a.textContent='인스턴스 186';document.querySelector('.ag-main').prepend(a)}""")
            hov_js = "getComputedStyle(document.getElementById('ic')).backgroundColor"
            off = await pg.evaluate(sub_js); await pg.hover("#ic"); await pg.wait_for_timeout(350); off_h = await pg.evaluate(hov_js)
            await pg.mouse.move(0, 0); await pg.evaluate("document.documentElement.dataset.skin='glass'"); await pg.wait_for_timeout(350)
            on = await pg.evaluate(sub_js); await pg.hover("#ic"); await pg.wait_for_timeout(350); on_h = await pg.evaluate(hov_js)
            check(f"1.22 유리 켬({th}): 카드 안 상태 행 바탕 · 배지 · interactive 카드 hover = 유리 끔과 같음(불투명 카드, 2.0.2)",
                  off["liA"] == 255 and on["li"] == off["li"] and on["badgeA"] == 255 and on_h == off_h, str({"off": off, "on": on, "hover": (off_h, on_h)}))
            await pg.close()

        # ── 1.18 유리 스킨 4단계 — 알약 컨트롤(트랙 · 유리 알약 · 미끄러짐 · 누름 · 탭 판) ──
        glide_js = r"""(sel)=>{const h=document.querySelector(sel),b=getComputedStyle(h,'::before');
          const a=[...h.children].find(c=>c.matches('.is-active,[aria-current="page"],[aria-pressed="true"],[aria-checked="true"],[aria-selected="true"]'));
          const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});const alpha=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return ctx.getImageData(0,0,1,1).data[3]};
          const tok=t=>{const d=document.createElement('div');d.style.color=`var(${t})`;document.body.appendChild(d);const c=getComputedStyle(d).color;d.remove();return c};
          const hr=h.getBoundingClientRect(),r=a.getBoundingClientRect(),m=new DOMMatrix(b.transform==='none'?undefined:b.transform),ia=getComputedStyle(a);
          return {glide:h.hasAttribute('data-ag-glide'),content:b.content,w:parseFloat(b.width)||0,x:m.m41,ex:r.left-hr.left-h.clientLeft+h.scrollLeft,ew:a.offsetWidth,
            track:getComputedStyle(h).backgroundColor,trackA:alpha(getComputedStyle(h).backgroundColor),itemBg:ia.backgroundColor,itemA:alpha(ia.backgroundColor),itemSh:ia.boxShadow,itemBb:ia.borderBottomColor,
            bBb:b.borderBottomColor,tf:b.transitionTimingFunction,fill:tok('--ag-glass-fill'),pill:tok('--ag-glass-pill'),acc:tok('--ag-accent-text'),soft:tok('--ag-accent-soft')}}"""
        near = lambda r: abs(r["x"] - r["ex"]) <= 1 and abs(r["w"] - r["ew"]) <= 1
        SPRING = "cubic-bezier(0.34, 1.56, 0.64, 1)"
        for light in (False, True):
            th = "라이트" if light else "다크"
            pg = await page(b, "index.html", light=light)
            n, sg = await pg.evaluate(glide_js, ".ag-topbar .ag-nav"), await pg.evaluate(glide_js, ".ag-segmented")
            check(f"1.18 유리 끔({th}): 네비 · 세그먼트 미끄러짐 층 없음 · 트랙 · 활성 불투명 그대로", n["content"] == "none" and sg["content"] == "none" and n["trackA"] == 255 and n["itemA"] == 255 and sg["itemA"] == 255, str({k: (n[k], sg[k]) for k in ("content", "trackA", "itemA")}))
            await pg.evaluate("document.documentElement.dataset.skin='glass'"); await pg.wait_for_timeout(350)   # 항목 배경 전환(--ag-dur)이 끝난 뒤
            n, sg = await pg.evaluate(glide_js, ".ag-topbar .ag-nav"), await pg.evaluate(glide_js, ".ag-segmented")
            check(f"1.18 유리 켬({th}): 미끄러지는 알약 — 네비 · 세그먼트 ::before 가 활성 항목 자리 · 폭(±1px), 활성 항목 자신은 투명, 세그먼트 트랙 = fill · 상단 바 네비 트랙 없음(1.21 바가 곧 트랙), 스프링 곡선",
                  all(r["glide"] and r["content"] == '""' and near(r) and r["itemA"] == 0 and SPRING in r["tf"] for r in (n, sg)) and sg["track"] == sg["fill"] and n["trackA"] == 0, str({k: (round(n[k], 1) if isinstance(n[k], float) else n[k], round(sg[k], 1) if isinstance(sg[k], float) else sg[k]) for k in ("glide", "x", "ex", "w", "ew", "itemA", "track", "fill")}))
            items = await pg.query_selector_all(".ag-segmented .ag-segmented__item")
            await items[2].click(); await pg.wait_for_timeout(450)
            moved = await pg.evaluate(glide_js, ".ag-segmented")
            await pg.evaluate("""()=>{const its=[...document.querySelectorAll('.ag-segmented .ag-segmented__item')];its.forEach(i=>{i.classList.remove('is-active');if(i.hasAttribute('aria-checked'))i.setAttribute('aria-checked','false')});its[0].classList.add('is-active');if(its[0].hasAttribute('aria-checked'))its[0].setAttribute('aria-checked','true')}""")
            await pg.wait_for_timeout(450)
            alp = await pg.evaluate(glide_js, ".ag-segmented")
            check(f"1.18 유리 켬({th}): 클릭 · 직접 class 변경(Alpine 식) 뒤 알약이 새 활성 항목으로 간다", near(moved) and near(alp) and moved["x"] != alp["x"], str({k: (round(moved[k], 1), round(alp[k], 1)) for k in ("x", "ex")}))
            # 누름 — 활성 아닌 항목은 자신이, 활성 항목은 알약도 .96
            box = await items[1].bounding_box(); await pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2); await pg.mouse.down(); await pg.wait_for_timeout(450)
            pressed_item = await pg.evaluate("getComputedStyle(document.querySelectorAll('.ag-segmented .ag-segmented__item')[1]).scale"); await pg.mouse.up(); await pg.wait_for_timeout(450)
            box = await items[1].bounding_box(); await pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2); await pg.mouse.down(); await pg.wait_for_timeout(450)
            pressed_pill = await pg.evaluate("getComputedStyle(document.querySelector('.ag-segmented'),'::before').scale"); await pg.mouse.up(); await pg.wait_for_timeout(450)
            released = await pg.evaluate("getComputedStyle(document.querySelector('.ag-segmented'),'::before').scale")
            check(f"1.18 유리 켬({th}): 누름 — 항목 scale .96, 활성 항목을 누르면 알약도 .96, 놓으면 원래대로", pressed_item == "0.96" and pressed_pill == "0.96" and released == "none", f"{pressed_item} {pressed_pill} {released}")
            # 정적 알약(JS 없음) — data-ag-glide 를 지우면 활성 항목이 알약을 받는다
            await pg.evaluate("document.querySelectorAll('[data-ag-glide]').forEach(h=>h.removeAttribute('data-ag-glide'))"); await pg.wait_for_timeout(350)
            n = await pg.evaluate(glide_js, ".ag-topbar .ag-nav")
            check(f"1.18 유리 켬({th}) 정적: 활성 네비 = 유리 알약(pill) + inset 하이라이트, 미끄러짐 층 없음", n["content"] == "none" and n["itemBg"] == n["pill"] and "inset" in n["itemSh"], str({k: n[k] for k in ("content", "itemBg", "pill", "itemSh")}))
            await pg.hover(".ag-user"); await pg.wait_for_timeout(250)
            r = await pg.evaluate("(()=>{const d=document.createElement('div');d.style.color='var(--ag-glass-fill)';document.body.appendChild(d);const f=getComputedStyle(d).color;d.remove();return {bg:getComputedStyle(document.querySelector('.ag-user')).backgroundColor,fill:f}})()")
            check(f"1.18 유리 켬({th}): 사용자 메뉴 hover 바탕 = fill", r["bg"] == r["fill"], str(r))
            await pg.close()
            # 밑줄 탭 — 미끄러지는 판 + 밑줄, 정적이면 활성 탭 판 + 기존 밑줄
            pg = await page(b, "detail.html", light=light, skin=True)
            await pg.wait_for_timeout(300)
            t = await pg.evaluate(glide_js, ".ag-tabs")
            await pg.evaluate("document.querySelectorAll('.ag-tabs[data-ag-glide]').forEach(h=>h.removeAttribute('data-ag-glide'))"); await pg.wait_for_timeout(350)
            ts = await pg.evaluate(glide_js, ".ag-tabs")
            check(f"1.18 유리 켬({th}): 탭 — 미끄러지는 판의 밑줄 = 액센트 글자색 · 활성 탭 밑줄 투명, 정적이면 활성 탭 판(fill) + 밑줄",
                  t["glide"] and near(t) and t["bBb"] == t["acc"] and t["itemBb"] == "rgba(0, 0, 0, 0)" and ts["itemBg"] == ts["fill"] and ts["itemBb"] == ts["acc"], str({k: (t[k], ts[k]) for k in ("bBb", "itemBb", "itemBg", "acc")}))
            await pg.close()
            # 탭 모드 2단 바 네비(예시는 밑줄 변형) — 미끄러짐에서 빠지고 활성 모양은 유리 끈 화면 그대로
            pg = await page(b, "layouts.html", light=light)
            await pg.click('[data-mode="tabs"]'); await pg.wait_for_timeout(200)
            off = await pg.evaluate(glide_js, ".ag-topbar__row--nav .ag-nav")
            await pg.evaluate("document.documentElement.dataset.skin='glass'"); await pg.wait_for_timeout(350)
            r = await pg.evaluate(glide_js, ".ag-topbar__row--nav .ag-nav")
            check(f"1.18 유리 켬({th}): 탭 모드 2단 바 네비는 미끄러짐 층 없음 · 활성 바탕 · 밑줄 · 그림자가 유리 끔과 같음",
                  r["content"] == "none" and all(r[k] == off[k] for k in ("itemBg", "itemBb", "itemSh")), str({k: (off[k], r[k]) for k in ("itemBg", "itemBb", "itemSh")}))
            await pg.close()

        # ── A11Y. axe-core (npm i 로 받으면 실행, 없으면 건너뜀): 전 페이지 × 다크·라이트, serious/critical 위반 0 ──
        axe_path = ROOT / "node_modules/axe-core/axe.min.js"
        if axe_path.exists():
            axe_src = axe_path.read_text(encoding="utf-8")
            worst = []
            # 1.15: index · layouts 는 유리 스킨(data-skin="glass")으로 한 번 더
            for name, skin in [(n, False) for n in ("index", "resources", "detail", "login", "layouts", "components", "report")] + [("index", True), ("layouts", True)]:
                for light in (False, True):
                    pg = await page(b, name + ".html", light=light, skin=skin)
                    await pg.add_script_tag(content=axe_src)
                    vs = await pg.evaluate("""async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return r.violations.filter(v=>['serious','critical'].includes(v.impact)).map(v=>v.id+'×'+v.nodes.length+' ('+v.nodes[0].target[0].slice(0,40)+')')}""")
                    if vs: worst.append(f"{name}{'-L' if light else ''}{'-glass' if skin else ''}: " + ", ".join(vs[:4]))
                    await pg.close()
            check("a11y: axe serious/critical violations = 0 on all pages (dark+light)", not worst, " | ".join(worst[:6]))
        else:
            print("  skip axe (npm i 로 axe-core 를 받으면 접근성 단언이 켜진다)")

        # ── 10. 폴백 간격: 클래스 없는 부모 안에서만 ─────────────────────────────────────────
        pg = await page(b, "components.html")
        r = await pg.evaluate("""()=>{const d=document.createElement('div');d.innerHTML='<div class="ag-card">a</div><div class="ag-card">b</div><p><button class="ag-btn">x</button><button class="ag-btn">y</button></p><div class="ag-cluster"><button class="ag-btn">x</button><button class="ag-btn">y</button></div>';document.body.appendChild(d);
          return {card:getComputedStyle(d.children[1]).marginTop, btnPlain:getComputedStyle(d.querySelector('p').children[1]).marginInlineStart, btnCluster:getComputedStyle(d.querySelector('.ag-cluster').children[1]).marginInlineStart}}""")
        check("fallback: card+card in classless div gets 24px", r["card"] == "24px", r["card"])
        check("fallback: btn+btn in <p> gets 8px, in .ag-cluster gets 0", r["btnPlain"] == "8px" and r["btnCluster"] == "0px", str(r))
        await pg.close()
        await b.close()

    fails = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(fails)}/{len(results)} checks passed" + (f", {len(fails)} FAILED" if fails else ""))
    sys.exit(1 if fails else 0)

asyncio.run(main())
