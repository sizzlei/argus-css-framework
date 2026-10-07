/* overlay: 드롭다운, 모달/드로어/오버레이, dual 모바일, 배너, 날짜 프리셋, 토스트 닫기, 확장 행 */
(function () {
  'use strict';
  /* 소유권 원칙: argus.js 는 자기가 연 것만 닫는다. Alpine/Vue/React 가 x-show 등으로 제어하는 오버레이·드로어·드롭다운은
     data-ag-open 으로 열리지 않았으므로 바깥 클릭·ESC 에서 건드리지 않는다 (hidden !important 교착 방지).
     닫기 직전에는 cancelable 'ag:overlay-close' 를 보내므로 서비스가 preventDefault() 로 막을 수 있다. */
  var AG = window.AG = window.AG || {};
  var owned = new WeakSet();
  function closeOverlay(el, reason) {
    if (!el) return false;
    var ev = new CustomEvent('ag:overlay-close', { bubbles: true, cancelable: true, detail: { reason: reason } });
    if (!el.dispatchEvent(ev)) return false;
    if (el.tagName === 'DIALOG') { if (el.open) el.close(); }
    else if (el.classList.contains('ag-modal-overlay')) { el.classList.remove('is-open'); el.hidden = true; }
    else el.classList.remove('is-open');
    owned.delete(el);
    el.dispatchEvent(new CustomEvent('ag:overlay-closed', { bubbles: true, detail: { reason: reason } }));
    return true;
  }
  function openOverlay(el) {
    if (!el) return;
    owned.add(el);
    if (el.tagName === 'DIALOG') el.showModal();
    else if (el.classList.contains('ag-modal-overlay')) { el.hidden = false; el.classList.add('is-open'); }
    else el.classList.add('is-open');
    el.dispatchEvent(new CustomEvent('ag:overlay-open', { bubbles: true }));
  }
  AG.overlay = { open: openOverlay, close: closeOverlay, owns: function (el) { return owned.has(el); }, _owned: owned };

  document.addEventListener('click', function (e) {
    /* ---- 드롭다운 (argus.js 가 연 것만 바깥 클릭으로 닫음) ---- */
    var trig = e.target.closest('[data-ag-dropdown]');
    document.querySelectorAll('.ag-dropdown.is-open').forEach(function (d) {
      if (owned.has(d) && !d.contains(e.target)) { d.classList.remove('is-open'); owned.delete(d); }
    });
    if (trig) { var dd = trig.closest('.ag-dropdown'); if (dd) { if (dd.classList.toggle('is-open')) owned.add(dd); else owned.delete(dd); } }

    /* ---- 모달 / 드로어 ---- */
    var open = e.target.closest('[data-ag-open]');
    if (open) openOverlay(document.getElementById(open.getAttribute('data-ag-open')));
    var close = e.target.closest('[data-ag-close]');
    if (close) closeOverlay(close.closest('dialog, .ag-drawer, .ag-modal-overlay'), 'button');   /* 명시적 닫기 버튼은 소유와 무관 (마크업이 곧 opt-in) */
    /* 오버레이 바깥(어두운 영역) 클릭 — argus.js 가 연 것만, data-ag-static 이면 안 닫음 */
    if (e.target.classList.contains('ag-modal-overlay') && owned.has(e.target) && !e.target.hasAttribute('data-ag-static')) closeOverlay(e.target, 'backdrop');

    /* ---- dual 레이아웃 모바일: 목록 ↔ 상세 ---- */
    var dOpen = e.target.closest('[data-ag-detail-open]');
    if (dOpen) { var da = dOpen.closest('.ag-app--dual'); if (da) da.classList.add('is-detail'); }
    var dClose = e.target.closest('[data-ag-detail-close]');
    if (dClose) { var db = dClose.closest('.ag-app--dual'); if (db) db.classList.remove('is-detail'); }

    /* ---- 시크릿 드러내기/가리기: 같은 .ag-secret-field 안의 .is-masked 토글 (input·textarea 공통) ---- */
    var rev = e.target.closest('[data-ag-reveal]');
    if (rev) {
      var sf = rev.closest('.ag-secret-field');
      var tgt = sf && sf.querySelector('.ag-input, .ag-textarea');
      if (tgt) {
        var masked = tgt.classList.toggle('is-masked');
        rev.setAttribute('aria-pressed', String(!masked));
        if (!masked && rev.classList.contains('ag-secret-field__reveal')) tgt.focus();
        tgt.dispatchEvent(new CustomEvent('ag:secret-toggle', { bubbles: true, detail: { masked: masked } }));
      }
    }

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
