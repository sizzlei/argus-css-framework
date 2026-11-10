/* glide(1.18): 선택 알약 미끄러짐 — .ag-nav · .ag-segmented · .ag-tabs 의 활성 항목 위치를 호스트 변수(--_glide-x/-y/-w/-h)와 data-ag-glide 로 알린다.
   그리는 쪽은 유리 스킨 CSS(skins.css) 뿐 — 스킨을 끄거나 이 파일이 없으면 활성 항목이 제자리에서 바뀐다.
   클릭(10-core) · 방향키(30-keyboard) · Alpine 의 class 변경을 속성 관찰 하나로 받는다 */
(function () {
  'use strict';
  if (!window.MutationObserver || !window.requestAnimationFrame) return;
  var HOST = '.ag-nav, .ag-segmented, .ag-tabs';
  var ITEM = '.ag-nav__item, .ag-segmented__item, .ag-tabs__item';
  var ACTIVE = '.is-active, [aria-current="page"], [aria-pressed="true"], [aria-checked="true"], [aria-selected="true"]';
  var dirty = [], raf = 0, seen = new WeakSet();
  var ro = window.ResizeObserver ? new ResizeObserver(function (es) { es.forEach(function (e) { queue(e.target); }); }) : null;

  /* 크기는 offsetWidth/Height(변형 영향 없음), 위치는 사각형 중심에서 — 누름 scale 은 중심 기준이라 눌린 채 재도 같은 값 */
  function place(host) {
    var on = null;
    for (var i = 0; i < host.children.length; i++) {
      var c = host.children[i];
      if (c.matches(ITEM) && c.matches(ACTIVE)) { on = c; break; }
    }
    if (!on || !on.offsetWidth) { host.removeAttribute('data-ag-glide'); return; }
    var hr = host.getBoundingClientRect(), r = on.getBoundingClientRect(), w = on.offsetWidth, h = on.offsetHeight;
    var s = host.style;
    s.setProperty('--_glide-x', (r.left + r.width / 2 - hr.left - host.clientLeft + host.scrollLeft - w / 2) + 'px');
    s.setProperty('--_glide-y', (r.top + r.height / 2 - hr.top - host.clientTop + host.scrollTop - h / 2) + 'px');
    s.setProperty('--_glide-w', w + 'px');
    s.setProperty('--_glide-h', h + 'px');
    host.setAttribute('data-ag-glide', '');
  }
  function flush() {
    raf = 0;
    var list = dirty; dirty = [];
    list.forEach(function (h) { if (h.isConnected) place(h); });
  }
  function queue(host) {
    if (dirty.indexOf(host) < 0) dirty.push(host);
    if (!raf) raf = requestAnimationFrame(flush);
  }
  function adopt(root) {
    var list = root.matches && root.matches(HOST) ? [root] : [];
    if (root.querySelectorAll) list = list.concat(Array.prototype.slice.call(root.querySelectorAll(HOST)));
    list.forEach(function (h) {
      if (!seen.has(h)) { seen.add(h); if (ro) ro.observe(h); }
      queue(h);
    });
  }
  /* 직접 쓰는 style · data-ag-glide 는 관찰 대상이 아니라 되먹임이 없다 */
  var mo = new MutationObserver(function (ms) {
    ms.forEach(function (m) {
      if (m.type === 'childList') { m.addedNodes.forEach(function (n) { if (n.nodeType === 1) adopt(n); }); return; }
      var t = m.target, p = t.parentElement;
      if (p && t.matches(ITEM) && p.matches(HOST)) queue(p);
    });
  });
  function start() {
    adopt(document.body);
    mo.observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['class', 'aria-current', 'aria-pressed', 'aria-checked', 'aria-selected'] });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { document.querySelectorAll(HOST).forEach(queue); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
