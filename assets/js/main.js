// Chips and Thoughts — site script
(function () {
  var t = document.getElementById('navToggle'), l = document.getElementById('navLinks');
  if (t && l) {
    t.addEventListener('click', function () { var o = l.classList.toggle('open'); t.setAttribute('aria-expanded', o); });
    document.addEventListener('click', function (e) { if (!t.contains(e.target) && !l.contains(e.target)) l.classList.remove('open'); });
  }
  // "days left" badges anywhere on the site, computed from the visitor's clock
  var today = new Date(); today.setHours(0, 0, 0, 0);
  document.querySelectorAll('[data-deadline]').forEach(function (el) {
    var d = new Date(el.getAttribute('data-deadline') + 'T00:00:00'); if (isNaN(d)) return;
    var days = Math.round((d - today) / 864e5), cls = days <= 14 ? 'crit' : days <= 45 ? 'warn' : 'ok';
    el.querySelectorAll('.days, .conf-pill').forEach(function (p) {
      p.classList.remove('ok', 'warn', 'crit'); p.classList.add(cls);
      if (p.classList.contains('days')) p.textContent = days < 0 ? 'passed' : days === 0 ? 'today' : days + 'd left';
      else p.title = days < 0 ? 'passed' : days === 0 ? 'today' : days + ' days left';
    });
  });
})();
