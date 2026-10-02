/* keyboard: 방향키, ESC, ⌘K, 콤보박스 열기/선택 */
(function () {
  'use strict';
  /* ---- 키보드: 세그먼트·탭 좌우, 메뉴·cmdk·콤보박스 상하, ESC 닫기, ⌘K 열기 ---- */
  document.addEventListener('keydown', function (e) {
    var t = e.target;
    if ((e.key === 'ArrowRight' || e.key === 'ArrowLeft') && t.matches && t.matches('.ag-segmented__item, .ag-tabs__item, .ag-nav__item')) {
      var sib = e.key === 'ArrowRight' ? t.nextElementSibling : t.previousElementSibling;
      if (sib) { sib.focus(); sib.click(); e.preventDefault(); }
    }
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      var box = t.closest && t.closest('.ag-menu, .ag-cmdk, .ag-combobox, .ag-notif');
      if (box) {
        var items = Array.prototype.slice.call(box.querySelectorAll('.ag-menu__item, .ag-cmdk__item, .ag-combobox__option, .ag-notif__item'));
        if (items.length) {
          var cur = items.indexOf(document.activeElement); if (cur < 0) cur = items.findIndex(function (i) { return i.classList.contains('is-active'); });
          var nxt = e.key === 'ArrowDown' ? Math.min(cur + 1, items.length - 1) : Math.max(cur - 1, 0);
          items.forEach(function (i) { i.classList.remove('is-active'); });
          items[nxt].classList.add('is-active'); items[nxt].setAttribute('tabindex', '-1'); items[nxt].focus(); e.preventDefault();
        }
      }
    }
    if (e.key === 'Escape') {
      document.querySelectorAll('.ag-dropdown.is-open').forEach(function (d) { d.classList.remove('is-open'); });
      document.querySelectorAll('.ag-modal-overlay:not([hidden])').forEach(function (o) { if (!o.hasAttribute('data-ag-static')) o.hidden = true; });
      document.querySelectorAll('.ag-drawer.is-open').forEach(function (d) { d.classList.remove('is-open'); });
      document.querySelectorAll('.ag-combobox.is-open').forEach(function (c) { c.classList.remove('is-open'); });
    }
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      var ck = document.querySelector('[data-ag-cmdk]');
      if (ck) { e.preventDefault(); ck.hidden = false; var inp = ck.querySelector('input'); if (inp) { inp.value = ''; inp.focus(); } }
    }
  });
  /* 콤보박스 열기/닫기 (모양 데모용) */
  document.addEventListener('focusin', function (e) { var cb = e.target.closest && e.target.closest('.ag-combobox'); if (cb) cb.classList.add('is-open'); });
  document.addEventListener('click', function (e) {
    document.querySelectorAll('.ag-combobox.is-open').forEach(function (c) { if (!c.contains(e.target)) c.classList.remove('is-open'); });
    var opt = e.target.closest('.ag-combobox__option');
    if (opt) { var cb2 = opt.closest('.ag-combobox'); if (cb2 && !cb2.hasAttribute('data-ag-multi')) { opt.parentElement.querySelectorAll('.is-selected').forEach(function (o) { o.classList.remove('is-selected'); }); } opt.classList.toggle('is-selected'); if (cb2 && !cb2.hasAttribute('data-ag-multi')) cb2.classList.remove('is-open'); }
  });
})();
