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
    /* 1.4: 포커스를 연 요소로 되돌린다 (키보드·스크린리더가 길을 잃지 않게) */
    if (el.__agOpener && document.contains(el.__agOpener)) { try { el.__agOpener.focus({ preventScroll: true }); } catch (err) {} }
    el.__agOpener = null;
    el.dispatchEvent(new CustomEvent('ag:overlay-closed', { bubbles: true, detail: { reason: reason } }));
    return true;
  }
  var FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
  function focusFirst(el) {
    var f = el.querySelector('[autofocus]') || el.querySelector(FOCUSABLE);
    if (f) { try { f.focus({ preventScroll: true }); } catch (err) {} }
  }
  function openOverlay(el) {
    if (!el) return;
    owned.add(el);
    el.__agOpener = document.activeElement;
    if (el.tagName === 'DIALOG') el.showModal();   /* <dialog> 는 포커스 트랩·초기 포커스를 브라우저가 한다 */
    else if (el.classList.contains('ag-modal-overlay')) { el.hidden = false; el.classList.add('is-open'); focusFirst(el); }
    else {
      el.classList.add('is-open');
      if (el.classList.contains('ag-drawer')) {
        /* 1.8: 배경 막이 없으면 넣는다 (드로어 바로 뒤 형제 — CSS 가 is-open 일 때 보여 준다) */
        var nx = el.nextElementSibling;
        if (!el.hasAttribute('data-ag-modeless') && !(nx && nx.classList.contains('ag-drawer-backdrop'))) {
          var bd = document.createElement('div'); bd.className = 'ag-drawer-backdrop'; bd.setAttribute('aria-hidden', 'true');
          el.parentNode.insertBefore(bd, el.nextSibling);
        }
        focusFirst(el);
      }
    }
    el.dispatchEvent(new CustomEvent('ag:overlay-open', { bubbles: true }));
  }
  /* 1.4: <dialog> 가 아닌 모달·드로어 안에서 Tab 순환 (argus.js 가 연 것만) */
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Tab') return;
    var box = e.target.closest && e.target.closest('.ag-modal-overlay.is-open, .ag-drawer.is-open');
    if (!box || !owned.has(box)) return;
    var f = Array.prototype.filter.call(box.querySelectorAll(FOCUSABLE), function (n) { return n.offsetParent !== null; });
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
    else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
  });
  AG.overlay = { open: openOverlay, close: closeOverlay, owns: function (el) { return owned.has(el); }, _owned: owned };

  document.addEventListener('click', function (e) {
    /* ---- 드롭다운 (argus.js 가 연 것만 바깥 클릭으로 닫음) ---- */
    var trig = e.target.closest('[data-ag-dropdown]');
    document.querySelectorAll('.ag-dropdown.is-open').forEach(function (d) {
      if (owned.has(d) && !d.contains(e.target)) { d.classList.remove('is-open'); owned.delete(d); }
    });
    if (trig) { var dd = trig.closest('.ag-dropdown'); if (dd) { if (dd.classList.toggle('is-open')) { owned.add(dd); trig.setAttribute('aria-expanded', 'true'); } else { owned.delete(dd); trig.setAttribute('aria-expanded', 'false'); } } }

    /* ---- 모달 / 드로어 ---- */
    var open = e.target.closest('[data-ag-open]');
    if (open) openOverlay(document.getElementById(open.getAttribute('data-ag-open')));
    var close = e.target.closest('[data-ag-close]');
    if (close) closeOverlay(close.closest('dialog, .ag-drawer, .ag-modal-overlay'), 'button');   /* 명시적 닫기 버튼은 소유와 무관 (마크업이 곧 opt-in) */
    /* 오버레이 바깥(어두운 영역) 클릭 — argus.js 가 연 것만, data-ag-static 이면 안 닫음 */
    if (e.target.classList.contains('ag-modal-overlay') && owned.has(e.target) && !e.target.hasAttribute('data-ag-static')) closeOverlay(e.target, 'backdrop');
    /* 1.8: 드로어 배경 막 클릭 — 바로 앞 드로어가 argus.js 소유일 때만 */
    if (e.target.classList.contains('ag-drawer-backdrop')) {
      var dw = e.target.previousElementSibling;
      if (dw && dw.classList.contains('ag-drawer') && owned.has(dw) && !dw.hasAttribute('data-ag-static')) closeOverlay(dw, 'backdrop');
    }

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
