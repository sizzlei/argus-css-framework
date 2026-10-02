#!/usr/bin/env python3
"""examples/src/*.html → examples/*.html
   <!--@icons--> 를 _icons.html(아이콘 스프라이트)로 치환하고, </body> 앞에 _demonav.html(예시 페이지 네비)을 끼운다.
   현재 페이지 링크에는 is-here 를 단다."""
import pathlib
root = pathlib.Path(__file__).parent / "examples"
icons = (root / "_icons.html").read_text()
demonav = (root / "_demonav.html").read_text()
for src in (root / "src").glob("*.html"):
    html = src.read_text().replace("<!--@icons-->", icons)
    nav = demonav.replace(f'data-page="{src.stem}"', f'data-page="{src.stem}" class="is-here" aria-current="page"')
    if "</body>" in html and "<!--@icons-->" in src.read_text():
        html = html.replace("</body>", nav + "\n</body>")
    (root / src.name).write_text(html)
    print("wrote", root / src.name)
