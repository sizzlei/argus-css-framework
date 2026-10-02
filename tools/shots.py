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
        await b.close()
asyncio.run(main())

async def extra():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={"width":1440,"height":900})
        pg=await ctx.new_page(); await pg.goto(base+"resources.html"); await pg.wait_for_timeout(500)
        await pg.click("[data-ag-sidebar-toggle]"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=str(ROOT / "shots/resources-collapsed.png"))
        pg2=await ctx.new_page(); await pg2.goto(base+"detail.html"); await pg2.wait_for_timeout(500)
        await pg2.click("[data-ag-open='drawer-param']"); await pg2.wait_for_timeout(400)
        await pg2.screenshot(path=str(ROOT / "shots/detail-drawer.png"))
        ctx2=await b.new_context(viewport={"width":400,"height":800})
        pg3=await ctx2.new_page(); await pg3.goto(base+"resources.html"); await pg3.wait_for_timeout(500)
        await pg3.click("[data-ag-sidebar-open]"); await pg3.wait_for_timeout(400)
        await pg3.screenshot(path=str(ROOT / "shots/resources-mobile-open.png"))
        await b.close()
asyncio.run(extra())
