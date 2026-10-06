// Interactive deadline timeline for /conferences. Reads window.CONF_DATA.
(function () {
  var data = (window.CONF_DATA || []).filter(function (c) { return c.deadline; });
  var scroll = document.getElementById('tl-scroll'), canvas = document.getElementById('tl-canvas'), tip = document.getElementById('tl-tip');
  if (!scroll || !canvas) return;
  var today = new Date(); today.setHours(0, 0, 0, 0);
  var months = 12, showPast = false, PX = 120; // px per month at 12-month range
  var M = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function d(s) { return new Date(s + 'T00:00:00'); }
  function days(a) { return Math.round((d(a) - today) / 864e5); }
  function cls(n) { return n < 0 ? 'past' : n <= 14 ? 'crit' : n <= 45 ? 'warn' : 'ok'; }
  function fmt(s) { var x = d(s); return M[x.getMonth()] + ' ' + x.getDate() + ', ' + x.getFullYear(); }

  function render() {
    var start = new Date(today.getFullYear(), today.getMonth() - (showPast ? 9 : 0), 1);
    var end = new Date(today.getFullYear(), today.getMonth() + months + 1, 1);
    var pxm = PX * 12 / months, total = 0, i, m;
    var x = function (date) { // px from start
      var y = date.getFullYear() - start.getFullYear(), mo = date.getMonth() - start.getMonth();
      var dim = new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
      return ((y * 12 + mo) + (date.getDate() - 1) / dim) * pxm;
    };
    var rows = data.filter(function (c) { var dd = d(c.deadline); return dd >= start && dd < end && (showPast || days(c.deadline) >= 0); })
                   .sort(function (a, b) { return d(a.deadline) - d(b.deadline); });
    var html = '<div class="tl-months">';
    for (m = new Date(start); m < end; m.setMonth(m.getMonth() + 1)) {
      html += '<div class="tl-month' + (m.getMonth() === 0 ? ' jan' : '') + '" style="width:' + pxm + 'px">' + M[m.getMonth()] + (m.getMonth() === 0 || total === 0 ? ' ’' + String(m.getFullYear()).slice(2) : '') + '</div>';
      total += pxm;
    }
    html += '</div><div class="tl-rows" style="width:' + total + 'px"><div class="tl-grid">';
    for (i = 1, m = new Date(start.getFullYear(), start.getMonth() + 1, 1); m < end; m.setMonth(m.getMonth() + 1), i++) {
      html += '<i class="' + (m.getMonth() === 0 ? 'jan' : '') + '" style="left:' + (i * pxm) + 'px"></i>';
    }
    html += '</div><div class="tl-today" style="left:' + x(today) + 'px"></div>';
    if (!rows.length) html += '<div class="tl-empty">No deadlines in this range.</div>';
    rows.forEach(function (c, k) {
      var xd = x(d(c.deadline)), n = days(c.deadline), ev = c.date ? d(c.date) : null, xe = ev && ev < end ? x(ev) : null;
      var labelLeft = xd > 140; // put the name on the side with room
      html += '<div class="tl-row" data-k="' + k + '">';
      if (xe !== null && xe > xd) html += '<div class="tl-span" style="left:' + xd + 'px;width:' + (xe - xd) + 'px"></div>';
      html += '<div class="tl-label ' + (labelLeft ? 'left' : 'right') + '" style="left:' + xd + 'px">' + c.name + '</div>';
      html += '<div class="tl-dot ' + cls(n) + '" data-k="' + k + '" style="left:' + xd + 'px" tabindex="0" role="button" aria-label="' + c.name + ' deadline ' + c.deadline + '"></div>';
      if (xe !== null) html += '<div class="tl-ev" data-k="' + k + '" data-ev="1" style="left:' + xe + 'px" title="' + c.name + ' · ' + fmt(c.date) + '"></div>';
      html += '</div>';
    });
    html += '</div>';
    canvas.innerHTML = html;
    canvas._rows = rows; canvas._x = x;
    // scroll so today sits a little in from the left
    scroll.scrollLeft = Math.max(0, x(today) - 90);
  }

  // tooltips
  canvas.addEventListener('mouseover', function (e) {
    var t = e.target.closest('.tl-dot, .tl-ev'); if (!t) return;
    var c = canvas._rows[+t.getAttribute('data-k')], n = days(c.deadline);
    var when = n < 0 ? Math.abs(n) + ' days ago' : n === 0 ? 'today' : 'in ' + n + (n === 1 ? ' day' : ' days');
    tip.innerHTML = '<b>' + c.name + '</b><div class="mono">Deadline ' + fmt(c.deadline) + ' · ' + when + '</div>' + (c.date ? '<div class="mono">Conference ' + fmt(c.date) + '</div>' : '') + '<div class="mono muted">click to jump to the row</div>';
    var r = t.getBoundingClientRect();
    tip.classList.add('show');
    var w = tip.offsetWidth || 200, cx = Math.min(Math.max(r.left + r.width / 2, w / 2 + 8), window.innerWidth - w / 2 - 8);
    tip.style.left = cx + 'px'; tip.style.top = r.top + 'px';
  });
  canvas.addEventListener('mouseout', function (e) { if (e.target.closest('.tl-dot, .tl-ev')) tip.classList.remove('show'); });
  canvas.addEventListener('click', function (e) {
    var t = e.target.closest('.tl-dot, .tl-ev'); if (!t) return;
    var c = canvas._rows[+t.getAttribute('data-k')], row = document.getElementById('conf-' + c.id);
    if (!row) return;
    var list = document.getElementById('conf-list'), btn = document.getElementById('conf-toggle');
    if (row.classList.contains('conf-more') && list && !list.classList.contains('open') && btn) btn.click();
    row.scrollIntoView({ behavior: 'smooth', block: 'center' });
    row.classList.remove('flash'); void row.offsetWidth; row.classList.add('flash');
  });
  canvas.addEventListener('keydown', function (e) { if ((e.key === 'Enter' || e.key === ' ') && e.target.classList.contains('tl-dot')) { e.preventDefault(); e.target.click(); } });

  // drag to pan
  var drag = null;
  scroll.addEventListener('mousedown', function (e) { if (e.target.closest('.tl-dot, .tl-ev')) return; drag = { x: e.pageX, s: scroll.scrollLeft }; scroll.classList.add('dragging'); });
  window.addEventListener('mousemove', function (e) { if (drag) scroll.scrollLeft = drag.s - (e.pageX - drag.x); });
  window.addEventListener('mouseup', function () { drag = null; scroll.classList.remove('dragging'); });

  // controls
  document.querySelectorAll('.tl-btn[data-months]').forEach(function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('.tl-btn[data-months]').forEach(function (o) { o.classList.remove('on'); });
      b.classList.add('on'); months = +b.getAttribute('data-months'); render();
    });
  });
  document.getElementById('tl-today').addEventListener('click', function () { scroll.scrollTo({ left: Math.max(0, canvas._x(today) - 90), behavior: 'smooth' }); });
  document.getElementById('tl-past').addEventListener('click', function () {
    showPast = !showPast; this.classList.toggle('on', showPast); this.setAttribute('aria-pressed', showPast); render();
  });

  // table show-more
  var list = document.getElementById('conf-list'), btn = document.getElementById('conf-toggle');
  if (btn) {
    var hidden = list.querySelectorAll('tr.conf-more').length;
    btn.addEventListener('click', function () {
      var open = list.classList.toggle('open'); btn.setAttribute('aria-expanded', open);
      btn.querySelector('.conf-toggle-text').textContent = open ? 'Show less' : 'Show ' + hidden + ' more';
    });
  }
  render();
})();
