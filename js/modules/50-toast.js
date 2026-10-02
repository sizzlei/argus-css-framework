/* toast: AG.toast(message, type, ms) */
(function () {
  'use strict';
  /* ---- 토스트 API: AG.toast('저장되었습니다', 'good', 4000) ---- */
  var AG = window.AG = window.AG || {};
  AG.toast = function (message, type, ms) {
    var stack = document.querySelector('.ag-toast-stack:not(.ag-toast-stack--static)');
    if (!stack) { stack = document.createElement('div'); stack.className = 'ag-toast-stack'; document.body.appendChild(stack); }
    var t = document.createElement('div');
    t.className = 'ag-toast' + (type ? ' ag-toast--' + type : '');
    t.setAttribute('role', 'status');
    t.innerHTML = '<span class="ag-dot ' + (type ? 'ag-dot--' + type : '') + '" style="margin-top:6px"></span><div class="ag-flex-1">' + message + '</div><button class="ag-btn ag-btn--icon ag-btn--ghost ag-btn--sm" data-ag-toast-close aria-label="닫기">×</button>';
    stack.appendChild(t);
    if (ms !== 0) setTimeout(function () { t.remove(); }, ms || 4000);
    return t;
  };
})();
