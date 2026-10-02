/* overlay: 드롭다운, 모달/드로어/오버레이, dual 모바일, 배너, 날짜 프리셋, 토스트 닫기, 확장 행 */
(function () {
  'use strict';
  document.addEventListener('click', function (e) {
    /* ---- 드롭다운 ---- */
    var trig = e.target.closest('[data-ag-dropdown]');
    document.querySelectorAll('.ag-dropdown.is-open').forEach(function (d) {
      if (!d.contains(e.target)) d.classList.remove('is-open');
    });
    if (trig) trig.closest('.ag-dropdown').classList.toggle('is-open');

    /* ---- 모달 / 드로어 ---- */
    var open = e.target.closest('[data-ag-open]');
    if (open) {
      var el = document.getElementById(open.getAttribute('data-ag-open'));
      if (el && el.tagName === 'DIALOG') el.showModal();
      else if (el && el.classList.contains('ag-modal-overlay')) el.hidden = false;
      else if (el) el.classList.add('is-open');
    }
    var close = e.target.closest('[data-ag-close]');
    if (close) {
      var c = close.closest('dialog, .ag-drawer, .ag-modal-overlay');
      if (c && c.tagName === 'DIALOG') c.close();
      else if (c && c.classList.contains('ag-modal-overlay')) c.hidden = true;
      else if (c) c.classList.remove('is-open');
    }
    /* 오버레이 바깥(어두운 영역) 클릭 시 닫기 */
    if (e.target.classList.contains('ag-modal-overlay') && !e.target.hasAttribute('data-ag-static')) e.target.hidden = true;

    /* ---- dual 레이아웃 모바일: 목록 ↔ 상세 ---- */
    var dOpen = e.target.closest('[data-ag-detail-open]');
    if (dOpen) { var da = dOpen.closest('.ag-app--dual'); if (da) da.classList.add('is-detail'); }
    var dClose = e.target.closest('[data-ag-detail-close]');
    if (dClose) { var db = dClose.closest('.ag-app--dual'); if (db) db.classList.remove('is-detail'); }

    /* ---- 배너 닫기 / 날짜 프리셋 칩 ---- */
    var bClose = e.target.closest('[data-ag-banner-close]');
    if (bClose) { var bn = bClose.closest('.ag-banner'); if (bn) bn.remove(); }
    var preset = e.target.closest('.ag-daterange__presets .ag-chip');
    if (preset) {
      Array.prototype.forEach.call(preset.parentElement.children, function (c) { c.classList.remove('is-active'); });
      preset.classList.add('is-active');
      var days = parseInt(preset.getAttribute('data-ag-days'), 10);
      var dr = preset.closest('.ag-daterange');
      if (dr && !isNaN(days)) {
        var ins = dr.querySelectorAll('input[type="date"]');
        if (ins.length === 2) {
          var end = new Date(), start = new Date(); start.setDate(end.getDate() - days + (days ? 1 : 0));
          var f = function (d) { var z = function (n) { return (n < 10 ? '0' : '') + n; }; return d.getFullYear() + '-' + z(d.getMonth() + 1) + '-' + z(d.getDate()); };
          ins[0].value = f(start); ins[1].value = f(end);
        }
      }
    }

    /* ---- 토스트 닫기 ---- */
    var tClose = e.target.closest('[data-ag-toast-close]');
    if (tClose) { var tt = tClose.closest('.ag-toast'); if (tt) tt.remove(); }

    /* ---- 테이블 확장 행 ---- */
    var exp = e.target.closest('[data-ag-expand]');
    if (exp) {
      var row = exp.closest('tr'); var next = row && row.nextElementSibling;
      if (next && next.classList.contains('ag-tr--expand')) { row.classList.toggle('is-expanded'); next.hidden = !next.hidden; }
    }
  });
})();
