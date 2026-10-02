/*! Argus CSS Framework v1.0.0 — 선택 JS 헬퍼 (js/modules 합본, 각 IIFE 독립) */
(function () {
'use strict';
'use strict';
var root = document.documentElement;
var KEY = 'ag-theme';
function applyTheme(t) {
if (t === 'light') root.setAttribute('data-theme', 'light');
else root.removeAttribute('data-theme');
document.querySelectorAll('[data-ag-theme-toggle]').forEach(function (b) {
b.setAttribute('aria-pressed', t === 'light' ? 'true' : 'false');
});
}
try { applyTheme(localStorage.getItem(KEY) || 'dark'); } catch (e) { applyTheme('dark'); }
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
var trig = e.target.closest('[data-ag-dropdown]');
document.querySelectorAll('.ag-dropdown.is-open').forEach(function (d) {
if (owned.has(d) && !d.contains(e.target)) { d.classList.remove('is-open'); owned.delete(d); }
});
if (trig) { var dd = trig.closest('.ag-dropdown'); if (dd) { if (dd.classList.toggle('is-open')) owned.add(dd); else owned.delete(dd); } }
var open = e.target.closest('[data-ag-open]');
if (open) openOverlay(document.getElementById(open.getAttribute('data-ag-open')));
var close = e.target.closest('[data-ag-close]');
if (close) closeOverlay(close.closest('dialog, .ag-drawer, .ag-modal-overlay'), 'button');   
if (e.target.classList.contains('ag-modal-overlay') && owned.has(e.target) && !e.target.hasAttribute('data-ag-static')) closeOverlay(e.target, 'backdrop');
var dOpen = e.target.closest('[data-ag-detail-open]');
if (dOpen) { var da = dOpen.closest('.ag-app--dual'); if (da) da.classList.add('is-detail'); }
var dClose = e.target.closest('[data-ag-detail-close]');
if (dClose) { var db = dClose.closest('.ag-app--dual'); if (db) db.classList.remove('is-detail'); }
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
var tClose = e.target.closest('[data-ag-toast-close]');
if (tClose) { var tt = tClose.closest('.ag-toast'); if (tt) tt.remove(); }
var exp = e.target.closest('[data-ag-expand]');
if (exp) {
var row = exp.closest('tr'); var next = row && row.nextElementSibling;
if (next && next.classList.contains('ag-tr--expand')) { row.classList.toggle('is-expanded'); next.hidden = !next.hidden; }
}
});
})();
(function () {
'use strict';
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
var ov = window.AG && AG.overlay;
document.querySelectorAll('.ag-dropdown.is-open, .ag-drawer.is-open, .ag-modal-overlay.is-open, .ag-modal-overlay:not([hidden])').forEach(function (o) {
if (!ov || !ov.owns(o)) return;
if (o.classList.contains('ag-modal-overlay') && o.hasAttribute('data-ag-static')) return;
ov.close(o, 'escape');
});
document.querySelectorAll('.ag-combobox.is-open').forEach(function (c) { if (c.__agOwned) { c.classList.remove('is-open'); c.__agOwned = false; } });
}
if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
var ck = document.querySelector('[data-ag-cmdk]');
if (ck) { e.preventDefault(); if (window.AG && AG.overlay) AG.overlay.open(ck); else ck.hidden = false; var inp = ck.querySelector('input'); if (inp) { inp.value = ''; inp.focus(); } }
}
});
document.addEventListener('focusin', function (e) { var cb = e.target.closest && e.target.closest('.ag-combobox'); if (cb && !cb.hasAttribute('data-ag-manual')) { cb.classList.add('is-open'); cb.__agOwned = true; } });
document.addEventListener('click', function (e) {
document.querySelectorAll('.ag-combobox.is-open').forEach(function (c) { if (c.__agOwned && !c.contains(e.target)) { c.classList.remove('is-open'); c.__agOwned = false; } });
var opt = e.target.closest('.ag-combobox__option');
if (opt) { var cb2 = opt.closest('.ag-combobox'); if (cb2 && !cb2.hasAttribute('data-ag-multi')) { opt.parentElement.querySelectorAll('.is-selected').forEach(function (o) { o.classList.remove('is-selected'); }); } opt.classList.toggle('is-selected'); if (cb2 && !cb2.hasAttribute('data-ag-multi')) cb2.classList.remove('is-open'); }
});
})();
(function () {
'use strict';
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
if (wrap.hasAttribute('data-ag-chart-default')) show(+wrap.getAttribute('data-ag-chart-default'));
});
})();
(function () {
'use strict';
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
