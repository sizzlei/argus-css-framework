/* chart-hover: .ag-chart[data-ag-chart] 라인 차트 툴팁 */
(function () {
  'use strict';
  /* ---- 라인 차트 호버: data-ag-chart 가 붙은 .ag-chart 안의 <svg> 기준 ---- */
  document.querySelectorAll('.ag-chart[data-ag-chart]').forEach(function (wrap) {
    var svg = wrap.querySelector('svg');
    var tip = wrap.querySelector('.ag-chart__tooltip');
    var cursor = wrap.querySelector('.ag-chart__cursor');
    var markers = wrap.querySelectorAll('.ag-chart__marker');
    var pts;
    try { pts = JSON.parse(wrap.getAttribute('data-ag-chart')); } catch (e) { return; }
    if (!svg || !tip || !pts || !pts.length) return;

    function show(i) {
      var p = pts[i];
      var box = svg.getBoundingClientRect();
      var vb = svg.viewBox.baseVal;
      var sx = box.width / vb.width, sy = box.height / vb.height;
      tip.style.left = (p.x * sx) + 'px';
      tip.style.top = (p.y * sy) + 'px';
      tip.innerHTML = '<strong>' + p.label + '</strong>' + p.value;
      tip.hidden = false;
      if (cursor) { cursor.setAttribute('x1', p.x); cursor.setAttribute('x2', p.x); cursor.style.opacity = 1; }
      markers.forEach(function (m, k) {
        var y = p.ys ? p.ys[k] : p.y;
        m.setAttribute('cx', p.x); m.setAttribute('cy', y); m.style.opacity = 1;
      });
    }
    svg.addEventListener('mousemove', function (e) {
      var box = svg.getBoundingClientRect();
      var vb = svg.viewBox.baseVal;
      var x = (e.clientX - box.left) / box.width * vb.width;
      var best = 0, d = Infinity;
      pts.forEach(function (p, i) { var dd = Math.abs(p.x - x); if (dd < d) { d = dd; best = i; } });
      show(best);
    });
    svg.addEventListener('mouseleave', function () {
      tip.hidden = true;
      if (cursor) cursor.style.opacity = 0;
      markers.forEach(function (m) { m.style.opacity = 0; });
    });
    /* 기본 강조점 */
    if (wrap.hasAttribute('data-ag-chart-default')) show(+wrap.getAttribute('data-ag-chart-default'));
  });
})();
