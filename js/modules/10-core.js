/* core: 테마 토글, 사이드바(접기·모바일·그룹·2단계), 세그먼트/탭, 아코디언 */
(function () {
  'use strict';
  'use strict';
  var root = document.documentElement;
  var KEY = 'ag-theme';

  /* ---- 테마: 저장된 값 > 기본(dark) ---- */
  function applyTheme(t) {
    if (t === 'light') root.setAttribute('data-theme', 'light');
    else root.removeAttribute('data-theme');
    document.querySelectorAll('[data-ag-theme-toggle]').forEach(function (b) {
      b.setAttribute('aria-pressed', t === 'light' ? 'true' : 'false');
    });
  }
  try { applyTheme(localStorage.getItem(KEY) || 'dark'); } catch (e) { applyTheme('dark'); }

  /* ---- 사이드바 상태 복원 ---- */
  try {
    var appEl = document.querySelector('.ag-app--sidebar');
    if (appEl && localStorage.getItem('ag-sidebar-collapsed') === 'true') appEl.classList.add('is-collapsed');
    var groups = JSON.parse(localStorage.getItem('ag-sidebar-groups') || '{}');
    document.querySelectorAll('.ag-sidebar__group[data-ag-group]').forEach(function (g) {
      if (groups[g.getAttribute('data-ag-group')]) g.classList.add('is-closed');
    });
    var nodes = JSON.parse(localStorage.getItem('ag-sidebar-nodes') || '{}');
    document.querySelectorAll('.ag-sidebar__node[data-ag-node]').forEach(function (n) {
      var k = n.getAttribute('data-ag-node');
      if (k in nodes) n.classList.toggle('is-open', !!nodes[k]);
      else if (n.querySelector('.ag-sidebar__item.is-active')) n.classList.add('is-open');
    });
  } catch (e) {}


  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-ag-theme-toggle]');
    if (t) {
      var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      applyTheme(next);
      try { localStorage.setItem(KEY, next); } catch (err) {}
      return;
    }

    /* ---- 세그먼트 / 탭 / 네비 is-active 토글 (같은 부모 안에서) ---- */
    var seg = e.target.closest('.ag-segmented__item, .ag-tabs__item, .ag-nav__item[href^="#"]');
    if (seg && seg.parentElement) {
      Array.prototype.forEach.call(seg.parentElement.children, function (c) {
        c.classList.remove('is-active');
        if (c.hasAttribute('aria-pressed')) c.setAttribute('aria-pressed', 'false');
        if (c.hasAttribute('aria-selected')) c.setAttribute('aria-selected', 'false');
      });
      seg.classList.add('is-active');
      if (seg.hasAttribute('aria-pressed')) seg.setAttribute('aria-pressed', 'true');
      if (seg.hasAttribute('aria-selected')) seg.setAttribute('aria-selected', 'true');
      /* 탭 패널 전환 */
      var target = seg.getAttribute('data-ag-tab');
      if (target) {
        var panels = seg.closest('[data-ag-tabs]');
        if (panels) {
          panels.querySelectorAll('[data-ag-panel]').forEach(function (p) {
            p.hidden = p.getAttribute('data-ag-panel') !== target;
          });
        }
      }
      if (seg.getAttribute('href') === '#') e.preventDefault();
    }

    /* ---- 사이드바: 접기(데스크톱) / 열기(모바일) / 그룹 아코디언 ---- */
    var sbT = e.target.closest('[data-ag-sidebar-toggle]');
    if (sbT) {
      var app = sbT.closest('.ag-app--sidebar') || document.querySelector('.ag-app--sidebar');
      if (app) {
        app.classList.toggle('is-collapsed');
        try { localStorage.setItem('ag-sidebar-collapsed', app.classList.contains('is-collapsed')); } catch (err) {}
      }
    }
    var sbO = e.target.closest('[data-ag-sidebar-open]');
    if (sbO) { var a2 = document.querySelector('.ag-app--sidebar'); if (a2) a2.classList.toggle('is-open'); }
    if (e.target.classList.contains('ag-sidebar-backdrop')) { e.target.closest('.ag-app--sidebar').classList.remove('is-open'); }
    var grp = e.target.closest('.ag-sidebar__group-toggle');
    if (grp) {
      var g = grp.closest('.ag-sidebar__group');
      g.classList.toggle('is-closed');
      var key = g.getAttribute('data-ag-group');
      if (key) { try { var m = JSON.parse(localStorage.getItem('ag-sidebar-groups') || '{}'); m[key] = g.classList.contains('is-closed'); localStorage.setItem('ag-sidebar-groups', JSON.stringify(m)); } catch (err) {} }
    }

    /* ---- 아코디언 (details 없이 쓰는 변형) / 2단계 사이드바 메뉴 ---- */
    var acc = e.target.closest('.ag-accordion__toggle');
    if (acc) {
      var item = acc.closest('.ag-accordion__item');
      var accRoot = item.closest('.ag-accordion');
      if (accRoot && accRoot.hasAttribute('data-ag-single')) {
        accRoot.querySelectorAll(':scope > .ag-accordion__item.is-open').forEach(function (o) { if (o !== item) o.classList.remove('is-open'); });
      }
      item.classList.toggle('is-open');
    }
    var parent = e.target.closest('.ag-sidebar__item--parent');
    if (parent) {
      var node = parent.closest('.ag-sidebar__node');
      node.classList.toggle('is-open');
      var nk = node.getAttribute('data-ag-node');
      if (nk) { try { var nm = JSON.parse(localStorage.getItem('ag-sidebar-nodes') || '{}'); nm[nk] = node.classList.contains('is-open'); localStorage.setItem('ag-sidebar-nodes', JSON.stringify(nm)); } catch (err) {} }
      e.preventDefault();
    }

  });
})();
