#!/usr/bin/env python3
"""값 단언 회귀 — 스크린샷(shots.py)·매트릭스(눈)로는 못 잡는 것을 숫자로 확인한다.
   서비스 적용에서 들어온 버그마다 여기에 단언을 하나씩 남긴다. 실패하면 exit 1.
   python3 tools/check.py        (playwright 필요: pip install playwright && playwright install chromium)
   python3 tools/check.py -v     (통과한 항목도 출력)"""
import asyncio, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT.joinpath("examples").as_uri() + "/"
VERBOSE = "-v" in sys.argv
results = []

def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    if VERBOSE or not ok:
        print(("  ok   " if ok else "  FAIL ") + name + (f"  — {detail}" if detail else ""))

async def page(b, path, width=1440, height=900, light=False):
    pg = await b.new_page(viewport={"width": width, "height": height})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.goto(BASE + path)
    if light:
        await pg.evaluate("document.documentElement.dataset.theme='light'")
    await pg.wait_for_timeout(350)
    pg._errs = errs
    return pg


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

        # ── 1. 모든 페이지: JS 에러 0, 400px 가로 스크롤 0 ─────────────────────────
        for name in ["index", "resources", "detail", "login", "layouts", "components", "matrix"]:
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
            v = await pg.evaluate("""()=>{let inf=0;for(const el of document.querySelectorAll('*')){const a=getComputedStyle(el).animationIterationCount;if(a&&a.split(',').some(x=>x.trim()==='infinite')&&el.offsetParent!==null&&!el.closest('.ag-skeleton,.ag-skeleton-rows,.ag-table--loading,.ag-spinner,.is-loading,.ag-log__cursor')&&!el.classList.contains('ag-spinner')&&!el.classList.contains('ag-skeleton'))inf++;}
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

        # ── A11Y. axe-core (npm i 로 받으면 실행, 없으면 건너뜀): 전 페이지 × 다크·라이트, serious/critical 위반 0 ──
        axe_path = ROOT / "node_modules/axe-core/axe.min.js"
        if axe_path.exists():
            axe_src = axe_path.read_text(encoding="utf-8")
            worst = []
            for name in ["index", "resources", "detail", "login", "layouts", "components"]:
                for light in (False, True):
                    pg = await page(b, name + ".html", light=light)
                    await pg.add_script_tag(content=axe_src)
                    vs = await pg.evaluate("""async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return r.violations.filter(v=>['serious','critical'].includes(v.impact)).map(v=>v.id+'×'+v.nodes.length+' ('+v.nodes[0].target[0].slice(0,40)+')')}""")
                    if vs: worst.append(f"{name}{'-L' if light else ''}: " + ", ".join(vs[:4]))
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
