/*! Argus CSS Framework — 차트 라이브러리 프리셋 (ApexCharts / Chart.js)
    CSS 토큰(--ag-chart-1..4, --ag-text-3 …)을 읽어 라이브러리 옵션으로 변환한다.
    테마가 바뀌면 AG.charts.refresh() 를 호출하거나, data-theme 변경을 자동 감지해 등록된 차트를 다시 그린다.

    사용:
      const chart = new ApexCharts(el, AG.charts.apex({ chart:{type:'donut',height:280}, series:[58,33,9], labels:['MySQL','PostgreSQL','Oracle'] }));
      chart.render(); AG.charts.register(chart);           // 테마 전환 시 자동 updateOptions

      AG.charts.chartjsDefaults(Chart);                     // Chart.js 전역 기본값 주입
      new Chart(ctx, { type:'bar', data:{ datasets:[{ data, backgroundColor: AG.charts.palette() }] } });

      AG.charts.sequential(5)                               // 히트맵용 순차 램프 — CSS 토큰 --ag-seq-1..5 와 같은 색 (rgb 문자열)
      AG.charts.apex({ chart:{type:'heatmap'}, series, plotOptions:{ heatmap:{ colorScale:{ ranges: AG.charts.heatRanges(0, 400) } } } })
*/
(function (global) {
  'use strict';
  var AG = global.AG = global.AG || {};

  function token(name, el) {
    return getComputedStyle(el || document.documentElement).getPropertyValue(name).trim();
  }
  /* color-mix()/oklab() 같은 함수형 색을 라이브러리가 먹는 #rrggbb 로 푼다 — 1px 캔버스에 칠해 픽셀을 읽는다 (어떤 CSS 색이든 sRGB 로 떨어짐).
     이미 #hex / rgb() 면 그대로. 캔버스를 못 쓰면 원문 반환 */
  var _ctx;
  function resolve(color) {
    if (!color || /^#|^rgba?\(/.test(color)) return color;
    try {
      if (!_ctx) _ctx = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
      _ctx.clearRect(0, 0, 1, 1); _ctx.fillStyle = color; _ctx.fillRect(0, 0, 1, 1);
      var d = _ctx.getImageData(0, 0, 1, 1).data;
      if (d[3] === 0) return color;
      return '#' + [d[0], d[1], d[2]].map(function (v) { return ('0' + v.toString(16)).slice(-2); }).join('');
    } catch (e) { return color; }
  }
  function tokens() {
    return {
      c: [token('--ag-chart-1'), token('--ag-chart-2'), token('--ag-chart-3'), token('--ag-chart-4')],
      good: token('--ag-good'), warn: token('--ag-warn'), crit: token('--ag-crit'), info: token('--ag-info'),
      accent: token('--ag-accent'), accent2: token('--ag-accent-2'),
      text: token('--ag-text'), text2: token('--ag-text-2'), text3: token('--ag-text-3'),
      grid: token('--ag-chart-grid') || 'rgba(128,128,128,.15)',
      surface: token('--ag-surface'), elevated: token('--ag-bg-elevated'), border: token('--ag-border-strong'),
      font: token('--ag-font-sans') || 'sans-serif', mono: token('--ag-font-mono') || 'monospace',
      dark: document.documentElement.getAttribute('data-theme') !== 'light'
    };
  }

  /* 깊은 병합 (사용자 옵션이 우선) */
  function merge(base, over) {
    if (!over) return base;
    var out = Array.isArray(base) ? base.slice() : Object.assign({}, base);
    Object.keys(over).forEach(function (k) {
      var b = out[k], o = over[k];
      out[k] = (b && o && typeof b === 'object' && typeof o === 'object' && !Array.isArray(o)) ? merge(b, o) : o;
    });
    return out;
  }

  var registry = [];

  AG.charts = {
    tokens: tokens,
    /* 범주색 n개. 5개 이상은 "기타"로 묶기를 권장하지만, 필요하면 소프트 톤으로 반복한다. */
    palette: function (n) {
      var t = tokens(), out = [];
      for (var i = 0; i < (n || 4); i++) out.push(t.c[i % 4]);
      return out;
    },
    status: function () { var t = tokens(); return { good: t.good, warn: t.warn, crit: t.crit, info: t.info }; },

    /* ---- 순차 램프 (히트맵·밀도) ----
       sequential(n, base): 연한 → 진한 n색. n=5 (기본) 는 CSS 토큰 --ag-seq-1..5 와 정확히 같은 값.
       base 는 토큰 이름('--ag-crit') 또는 색 문자열. 기본은 --ag-chart-1. 다른 n 은 같은 식(15%→100%)을 등분해 계산.
       Apex 는 enableShades 로 자기 램프를 만들려 하므로, 이 색을 colorScale.ranges 로 넘기고 enableShades 는 끈다 (apex() 가 heatmap 일 때 자동). */
    sequential: function (n, base) {
      n = n || 5;
      var top = base ? (base.charAt(0) === '-' ? token(base) : base) : token('--ag-chart-1');
      var floor = token('--ag-surface-2'), out = [];
      if (n === 5 && !base) { for (var k = 1; k <= 5; k++) out.push(resolve(token('--ag-seq-' + k))); return out; }
      for (var i = 0; i < n; i++) {
        var pct = n === 1 ? 100 : 15 + (85 * i) / (n - 1);
        out.push(pct >= 100 ? resolve(top) : resolve('color-mix(in oklab, ' + top + ' ' + pct.toFixed(1) + '%, ' + floor + ')'));
      }
      return out;
    },
    /* Apex heatmap colorScale.ranges 생성. 0 이하 = 비어 있음(--ag-surface-2), 그 위 max 까지 n 등분(기본 5) */
    heatRanges: function (min, max, n, base) {
      n = n || 5; var cols = AG.charts.sequential(n, base), out = [];
      var lo = Math.max(min, 0);
      if (min <= 0) out.push({ from: -1e12, to: 0, color: resolve(token('--ag-surface-2')), name: '없음' });   /* 0 = 비어 있음 */
      var step = (max - lo) / n;
      for (var i = 0; i < n; i++) {
        var from = lo + step * i, to = i === n - 1 ? max : lo + step * (i + 1) - 1e-9;
        out.push({ from: i === 0 && lo === 0 ? 1e-9 : from, to: to, color: cols[i], name: Math.ceil(from) + '–' + Math.round(to) });
      }
      return out;
    },

    /* ---- ApexCharts 옵션 프리셋 ---- */
    apex: function (userOptions) {
      var t = tokens();
      var type = (userOptions && userOptions.chart && userOptions.chart.type) || 'line';
      var base = {
        chart: {
          background: 'transparent',
          fontFamily: t.font,
          foreColor: t.text3,
          toolbar: { show: false },
          zoom: { enabled: false },
          animations: { speed: 400, animateGradually: { enabled: false } }
        },
        theme: { mode: t.dark ? 'dark' : 'light' },
        colors: t.c,
        stroke: { width: type === 'line' || type === 'area' ? 2 : 0, curve: 'smooth', lineCap: 'round' },
        fill: type === 'area' ? { type: 'gradient', gradient: { shadeIntensity: 0, opacityFrom: .22, opacityTo: 0, stops: [0, 100] } } : { opacity: 1 },
        dataLabels: { enabled: false },
        grid: {
          borderColor: t.grid, strokeDashArray: 0,
          xaxis: { lines: { show: false } }, yaxis: { lines: { show: true } },
          padding: { left: 4, right: 4 }
        },
        xaxis: {
          axisBorder: { show: false }, axisTicks: { show: false },
          labels: { style: { colors: t.text3, fontSize: '12px', fontFamily: t.font } },
          tooltip: { enabled: false }
        },
        yaxis: { labels: { style: { colors: t.text3, fontSize: '12px', fontFamily: t.font } } },
        legend: {
          position: 'bottom', horizontalAlign: 'left',
          fontSize: '13px', fontFamily: t.font,
          labels: { colors: t.text2 },
          markers: { size: 5, shape: 'circle', strokeWidth: 0, offsetX: -2 },
          itemMargin: { horizontal: 10, vertical: 4 }
        },
        tooltip: {
          theme: t.dark ? 'dark' : 'light',
          style: { fontSize: '12px', fontFamily: t.font },
          marker: { show: true },
          x: { show: true }
        },
        markers: { size: 0, hover: { size: 6, sizeOffset: 0 }, strokeColors: t.surface, strokeWidth: 2 },
        plotOptions: {
          bar: { borderRadius: 4, borderRadiusApplication: 'end', columnWidth: '55%', barHeight: '60%' },
          pie: {
            expandOnClick: false,
            donut: {
              size: '72%',
              labels: {
                show: true,
                name: { fontSize: '12px', color: t.text3, offsetY: 18 },
                value: { fontSize: '26px', fontWeight: 500, color: t.text, offsetY: -12, fontFamily: t.font },
                total: { show: true, label: '합계', color: t.text3, fontSize: '12px', formatter: function (w) { return w.globals.seriesTotals.reduce(function (a, b) { return a + b; }, 0).toLocaleString(); } }
              }
            }
          },
          radialBar: {
            hollow: { size: '62%' },
            track: { background: token('--ag-surface-3') || t.grid, strokeWidth: '100%' },
            dataLabels: { name: { color: t.text3, fontSize: '12px' }, value: { color: t.text, fontSize: '24px', fontWeight: 500 } }
          },
          treemap: { distributed: false, enableShades: true, shadeIntensity: .4, useFillColorAsStroke: false },
          heatmap: { radius: 3, enableShades: false, useFillColorAsStroke: false, colorScale: { inverse: false } }
        },
        states: { hover: { filter: { type: 'lighten', value: .06 } }, active: { filter: { type: 'none' } } },
        noData: { text: '데이터 없음', style: { color: t.text3, fontSize: '13px', fontFamily: t.font } }
      };
      if (type === 'donut' || type === 'pie') { base.stroke = { width: 2, colors: [t.surface] }; base.legend.position = 'right'; base.legend.horizontalAlign = 'center'; }
      if (type === 'treemap' || type === 'heatmap') { base.dataLabels = { enabled: true, style: { fontSize: '12px', fontFamily: t.font, fontWeight: 500 } }; }
      if (type === 'heatmap') {
        /* 단일 색 + 토큰 램프. 셀 경계는 --ag-chart-grid (표면색으로 그리면 라이트에서 셀이 사라진다).
           colorScale.ranges 를 직접 주지 않았으면 series 의 최소~최대를 5등분한 heatRanges 를 넣는다 (Apex 자체 shade 램프는 라이트에서 흰색으로 흐려짐) */
        base.colors = [t.c[0]];
        base.stroke = { width: 1, colors: [t.grid] };
        var hm = userOptions && userOptions.plotOptions && userOptions.plotOptions.heatmap;
        if (!(hm && hm.colorScale && hm.colorScale.ranges)) {
          var vals = [];
          (userOptions && userOptions.series || []).forEach(function (sr) { (sr.data || []).forEach(function (d) { var v = d && typeof d === 'object' ? d.y : d; if (typeof v === 'number' && isFinite(v)) vals.push(v); }); });
          if (vals.length) {
            var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
            base.plotOptions.heatmap.colorScale.ranges = AG.charts.heatRanges(lo, hi === lo ? lo + 1 : hi);
          } else { base.plotOptions.heatmap.enableShades = true; base.plotOptions.heatmap.shadeIntensity = .85; }
        }
      }
      var out = merge(base, userOptions || {});
      /* 테마 전환 refresh 가 사용자 옵션(dataLabels, legend, plotOptions …)을 잃지 않도록 원본을 숨겨 둔다 */
      try { Object.defineProperty(out, '__agUser', { value: userOptions || {}, enumerable: false }); } catch (e) { /* ignore */ }
      return out;
    },

    /* ---- Chart.js 전역 기본값 ---- */
    chartjsDefaults: function (Chart) {
      if (!Chart || !Chart.defaults) return;
      var t = tokens();
      var d = Chart.defaults;
      d.font.family = t.font; d.font.size = 12;
      d.color = t.text3;
      d.borderColor = t.grid;
      d.plugins.legend.position = 'bottom';
      d.plugins.legend.align = 'start';
      d.plugins.legend.labels.usePointStyle = true;
      d.plugins.legend.labels.pointStyle = 'circle';
      d.plugins.legend.labels.boxWidth = 6;
      d.plugins.legend.labels.color = t.text2;
      d.plugins.tooltip.backgroundColor = t.elevated;
      d.plugins.tooltip.borderColor = t.border;
      d.plugins.tooltip.borderWidth = 1;
      d.plugins.tooltip.titleColor = t.text;
      d.plugins.tooltip.bodyColor = t.text2;
      d.plugins.tooltip.padding = 10;
      d.plugins.tooltip.cornerRadius = 10;
      d.plugins.tooltip.displayColors = true;
      d.plugins.tooltip.boxPadding = 4;
      d.elements.line.borderWidth = 2;
      d.elements.line.tension = .35;
      d.elements.point.radius = 0;
      d.elements.point.hoverRadius = 5;
      d.elements.bar.borderRadius = 4;
      d.elements.arc.borderColor = t.surface;
      d.elements.arc.borderWidth = 2;
      if (d.scales && d.scales.linear) { d.scales.linear.grid = { color: t.grid }; }
      if (d.scales && d.scales.category) { d.scales.category.grid = { display: false }; }
      d.backgroundColor = t.c[0];
    },

    /* ---- 테마 전환 시 다시 그리기 ---- */
    register: function (chart) { registry.push(chart); return chart; },
    refresh: function () {
      registry.forEach(function (ch) {
        try {
          if (ch && typeof ch.updateOptions === 'function') {            /* ApexCharts */
            var cur = ch.w && ch.w.config || ch.opts || {};
            var user = ch.opts && ch.opts.__agUser ? merge(ch.opts.__agUser, {}) : { chart: { type: cur.chart && cur.chart.type } };
            if (cur.series) user.series = cur.series;                   /* 현재 데이터 기준 (heatmap 램프는 series 범위로 재계산) */
            ch.updateOptions(AG.charts.apex(user), false, true);
          } else if (ch && ch.config && typeof ch.update === 'function') { /* Chart.js */
            AG.charts.chartjsDefaults(ch.constructor);
            ch.update();
          }
        } catch (e) { /* 파괴된 차트는 무시 */ }
      });
    }
  };

  /* data-theme 변경 자동 감지 */
  if (global.MutationObserver) {
    new MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) if (muts[i].attributeName === 'data-theme') { AG.charts.refresh(); break; }
    }).observe(document.documentElement, { attributes: true });
  }
})(window);
