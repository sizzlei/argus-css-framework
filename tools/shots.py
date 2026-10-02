import asyncio, sys
from playwright.async_api import async_playwright
import pathlib, sys
"""시각 회귀: examples/*.html 을 1440px 다크/라이트 + 400px 로 찍어 shots/ 에 저장.
   python3 tools/shots.py   (playwright 필요: pip install playwright && playwright install chromium)"""
ROOT = pathlib.Path(__file__).resolve().parent.parent
base = ROOT.joinpath("examples").as_uri() + "/"
pathlib.Path(ROOT / "shots").mkdir(exist_ok=True)
pages=["index","resources","detail","components","login","layouts","matrix"]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for theme in ("dark","light"):
            ctx=await b.new_context(viewport={"width":1440,"height":900},device_scale_factor=1)
            if theme=="light":
                await ctx.add_init_script("try{localStorage.setItem('ag-theme','light')}catch(e){}")
            for name in pages:
                pg=await ctx.new_page()
                errs=[]
                pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
                pg.on("pageerror", lambda e: errs.append(str(e)))
                await pg.goto(base+name+".html")
                await pg.wait_for_timeout(1200)
                sw=await pg.evaluate("document.documentElement.scrollWidth"); cw=await pg.evaluate("document.documentElement.clientWidth")
                await pg.screenshot(path=str(ROOT / f"shots/{name}-{theme}.png"), full_page=True)
                print(name,theme,"scrollW",sw,"clientW",cw,"errors",errs[:3])
                await pg.close()
            await ctx.close()
        # mobile
        ctx=await b.new_context(viewport={"width":400,"height":800})
        pg=await ctx.new_page(); await pg.goto(base+"index.html"); await pg.wait_for_timeout(800)
        print("mobile scrollW",await pg.evaluate("document.documentElement.scrollWidth"))
        await pg.screenshot(path=str(ROOT / "shots/index-mobile.png"), full_page=True)
        await ctx.close()
        # 초광폭 3400px: tabs 모드 상단바 두 행이 한 줄로 붙지 않는지 (3224px 이상에서 터졌던 버그). 행 2개의 top 이 달라야 함
        ctx=await b.new_context(viewport={"width":3400,"height":900})
        pg=await ctx.new_page(); await pg.goto(base+"layouts.html"); await pg.wait_for_timeout(600)
        await pg.click('[data-mode="tabs"]'); await pg.wait_for_timeout(300)
        r=await pg.evaluate("""()=>{const rows=[...document.querySelectorAll('.ag-topbar__row')].filter(e=>!e.hidden);const main=document.querySelector('.ag-main').getBoundingClientRect();return {rows:rows.map(e=>{const b=e.getBoundingClientRect();return [Math.round(b.top),Math.round(b.left),Math.round(b.right)]}),main:[Math.round(main.left),Math.round(main.right)]}}""")
        ok = len(r["rows"])==2 and r["rows"][0][0]!=r["rows"][1][0] and abs(r["rows"][0][1]-r["main"][0])<2
        print("ultrawide 3400 tabs", r, "OK" if ok else "FAIL — 상단바 행이 한 줄로 붙었거나 본문과 어긋남")
        await pg.screenshot(path=str(ROOT / "shots/layouts-tabs-3400.png"), clip={"x":0,"y":0,"width":3400,"height":200})
        await b.close()
asyncio.run(main())
