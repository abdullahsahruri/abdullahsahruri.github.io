---
layout: page
title: Conference Deadlines
subtitle: Paper deadlines for digital VLSI, EDA and FPGA venues
---

{% assign confs = site.data.conferences | sort: "deadline" %}
{% assign today = site.time | date: "%Y-%m-%d" %}
{% assign shown = 10 %}

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@500;600;700;800&display=swap" rel="stylesheet">

<div class="conf">
<p class="conf-intro">Upcoming paper deadlines first, soonest at the top. Entries whose call for papers is not out yet are listed as TBD; past deadlines sit under the arrow.</p>

<table class="conf-list" id="conf-list">
  <thead>
    <tr><th>Conference</th><th>Home page</th><th>Paper deadline</th><th>Conference date</th></tr>
  </thead>
  <tbody>
  {%- assign n = 0 -%}
  {%- comment -%} 1. upcoming, soonest first {%- endcomment -%}
  {%- for c in confs -%}
    {%- assign dl = c.deadline | default: "" -%}
    {%- if dl == "" or dl < today -%}{%- continue -%}{%- endif -%}
    {%- assign n = n | plus: 1 -%}
    <tr class="conf-up{% if n > shown %} conf-more{% endif %}" data-deadline="{{ dl }}">
      <td class="conf-name">{{ c.name }}</td>
      <td class="conf-url"><a href="{{ c.url }}" target="_blank" rel="noopener">{{ c.url | remove: "https://" | remove: "http://" | remove: "www." | split: "/" | first }}</a></td>
      <td class="conf-date"><span class="conf-pill">{{ dl }}</span>{% if c.note %} <small>{{ c.note }}</small>{% endif %}</td>
      <td class="conf-date">{{ c.date | default: "TBD" }}</td>
    </tr>
  {%- endfor -%}
  {%- comment -%} 2. CFP not out yet {%- endcomment -%}
  {%- for c in confs -%}
    {%- assign dl = c.deadline | default: "" -%}
    {%- if dl != "" -%}{%- continue -%}{%- endif -%}
    {%- assign n = n | plus: 1 -%}
    <tr class="conf-tbd{% if n > shown %} conf-more{% endif %}">
      <td class="conf-name">{{ c.name }}</td>
      <td class="conf-url"><a href="{{ c.url }}" target="_blank" rel="noopener">{{ c.url | remove: "https://" | remove: "http://" | remove: "www." | split: "/" | first }}</a></td>
      <td class="conf-date">TBD{% if c.note %} <small>{{ c.note }}</small>{% endif %}</td>
      <td class="conf-date">{{ c.date | default: "TBD" }}</td>
    </tr>
  {%- endfor -%}
  {%- comment -%} 3. past, most recent first {%- endcomment -%}
  {%- assign past = confs | reverse -%}
  {%- for c in past -%}
    {%- assign dl = c.deadline | default: "" -%}
    {%- if dl == "" or dl >= today -%}{%- continue -%}{%- endif -%}
    {%- assign n = n | plus: 1 -%}
    <tr class="conf-past{% if n > shown %} conf-more{% endif %}" data-deadline="{{ dl }}">
      <td class="conf-name">{{ c.name }}</td>
      <td class="conf-url"><a href="{{ c.url }}" target="_blank" rel="noopener">{{ c.url | remove: "https://" | remove: "http://" | remove: "www." | split: "/" | first }}</a></td>
      <td class="conf-date">{{ dl }}{% if c.note %} <small>{{ c.note }}</small>{% endif %}</td>
      <td class="conf-date">{{ c.date | default: "TBD" }}</td>
    </tr>
  {%- endfor -%}
  </tbody>
</table>
{%- assign hidden = n | minus: shown -%}
{%- if hidden > 0 -%}
<button type="button" class="conf-toggle" id="conf-toggle" aria-expanded="false" aria-controls="conf-list">
  <span class="conf-arrow" aria-hidden="true"></span> <span class="conf-toggle-text">Show {{ hidden }} more</span>
</button>
{%- endif -%}

<details class="conf-approx">
  <summary><span class="conf-arrow" aria-hidden="true"></span> Approximate deadlines, for planning before a CFP is out</summary>
  <div class="conf-approx-grid">
    <div class="conf-col conf-col-a">
      <h3>VLSI design</h3>
      <ul>
        <li>VLSI Symposium – mid January</li>
        <li>ISLPED – mid March</li>
        <li>MWSCAS – mid March</li>
        <li>HEART – mid March</li>
        <li>CICC – early April</li>
        <li>SOCC – early April</li>
        <li>VLSI-SoC – mid April</li>
        <li>ICCD – early May</li>
        <li>ISQED – early October</li>
        <li>ISCAS – early October</li>
        <li>GLSVLSI – December</li>
      </ul>
    </div>
    <div class="conf-col conf-col-b">
      <h3>VLSI CAD</h3>
      <ul>
        <li>ICCAD – mid April</li>
        <li>IWLS – mid April</li>
        <li>ASP-DAC – mid July</li>
        <li>DATE – early September</li>
        <li>ISPD – early October</li>
        <li>DAC – late November</li>
      </ul>
    </div>
    <div class="conf-col conf-col-c">
      <h3>FPGA</h3>
      <ul>
        <li>FCCM – mid January</li>
        <li>FPL – late March</li>
        <li>CODES+ISSS – mid April</li>
        <li>FPT – June</li>
        <li>ISFPGA – early October</li>
      </ul>
    </div>
  </div>
  <p>Typical windows; they move by a few weeks from year to year. Confirm on the official site.</p>
</details>
</div>

<style>
  .conf { font-family: 'Nunito', -apple-system, "Segoe UI", Roboto, sans-serif; --c-ink: #2d3142; --c-mute: #7c8193; --c-line: #ebe8f3;
          --c-blue: #2f6fb3; --c-violet: #6d5bb5; --c-green: #2e8b6a; --c-rose: #c6485f; --c-amber: #b8862b;
          --c-blue-bg: #e3f0fb; --c-violet-bg: #ece8fa; --c-green-bg: #e1f5ec; --c-rose-bg: #fde6ea; --c-amber-bg: #fff3d6; }
  .conf-intro { color: var(--c-mute); font-weight: 600; font-size: .95em; }
  .conf-list { width: 100%; border-collapse: separate; border-spacing: 0; font-size: .95em; border: 1px solid var(--c-line); border-radius: 14px; overflow: hidden;
               box-shadow: 0 8px 24px -18px rgba(76,64,120,.45); margin: 0; }
  .conf-list th { background: linear-gradient(90deg, var(--c-blue), var(--c-violet)); color: #fff; font-weight: 800; padding: 11px 14px; text-align: left; letter-spacing: .02em; }
  .conf-list td { padding: 10px 14px; border-bottom: 1px solid var(--c-line); color: var(--c-ink); font-weight: 600; vertical-align: middle; }
  .conf-list tr:last-child td { border-bottom: none; }
  .conf-list td.conf-name { border-left: 4px solid var(--c-green); font-weight: 800; }
  .conf-list tr.conf-tbd td.conf-name { border-left-color: var(--c-violet); }
  .conf-list tr.conf-past td.conf-name { border-left-color: #cfd3dc; }
  .conf-list td.conf-date { font-variant-numeric: tabular-nums; white-space: nowrap; }
  .conf-list td.conf-date small { display: block; color: var(--c-mute); font-weight: 600; font-size: .78em; white-space: normal; }
  .conf-list a { color: var(--c-blue); text-decoration: none; font-weight: 700; }
  .conf-list a:hover { text-decoration: underline; }
  .conf-pill { display: inline-block; padding: .1em .6em; border-radius: 999px; background: var(--c-green-bg); color: var(--c-green); font-weight: 800; }
  .conf-pill.soon { background: var(--c-amber-bg); color: var(--c-amber); }
  .conf-pill.now  { background: var(--c-rose-bg);  color: var(--c-rose); }
  .conf-list tr.conf-up:hover td { background: #f8f7fd; }
  .conf-list tr.conf-tbd td { font-style: italic; color: var(--c-violet); }
  .conf-list tr.conf-past td, .conf-list tr.conf-past td a { color: #a3a8b4; }
  .conf-list tr.conf-more { display: none; }
  .conf-list.open tr.conf-more { display: table-row; }
  .conf-toggle { display: inline-flex; align-items: center; gap: .4em; margin: .7rem 0 0; padding: .45em 1em; border: 1.5px solid var(--c-line); border-radius: 999px;
                 background: #fff; color: var(--c-violet); font: inherit; font-weight: 800; font-size: .9em; cursor: pointer; }
  .conf-toggle:hover { background: var(--c-violet-bg); }
  .conf-arrow::before { content: "▸"; color: var(--c-violet); font-size: 1.1em; }
  .conf-toggle[aria-expanded="true"] .conf-arrow::before, .conf-approx[open] .conf-arrow::before { content: "▾"; }
  .conf-approx { margin-top: 2rem; border: 1px solid var(--c-line); border-radius: 14px; padding: .4rem 1.2rem; background: linear-gradient(135deg, #fbfaff, #f4f8fd); }
  .conf-approx summary { cursor: pointer; font-weight: 800; padding: .6rem 0; list-style: none; color: var(--c-ink); }
  .conf-approx summary::-webkit-details-marker { display: none; }
  .conf-approx-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.2rem; padding: .4rem 0 .6rem; }
  .conf-col { border-radius: 10px; padding: .8rem 1rem; }
  .conf-col-a { background: var(--c-blue-bg); }  .conf-col-a h3 { color: var(--c-blue); }
  .conf-col-b { background: var(--c-violet-bg); } .conf-col-b h3 { color: var(--c-violet); }
  .conf-col-c { background: var(--c-green-bg); }  .conf-col-c h3 { color: var(--c-green); }
  .conf-col h3 { font-size: 1em; margin: 0 0 .4rem; font-weight: 800; }
  .conf-col ul { list-style: none; padding: 0; margin: 0; line-height: 1.8; font-weight: 600; font-size: .92em; }
  .conf-approx p { color: var(--c-mute); font-size: .85em; font-weight: 600; margin: 0 0 .6rem; }
  @media (max-width: 600px) {
    .conf-list th:nth-child(2), .conf-list td:nth-child(2) { display: none; }
    .conf-list td, .conf-list th { padding: 8px 8px; }
  }
</style>

<script>
  (function () {
    var list = document.getElementById('conf-list'), btn = document.getElementById('conf-toggle');
    if (btn) {
      var hidden = list.querySelectorAll('tr.conf-more').length;
      btn.addEventListener('click', function () {
        var open = list.classList.toggle('open');
        btn.setAttribute('aria-expanded', open);
        btn.querySelector('.conf-toggle-text').textContent = open ? 'Show less' : 'Show ' + hidden + ' more';
      });
    }
    /* colour upcoming deadlines by how close they are, using the visitor's clock */
    var today = new Date(); today.setHours(0, 0, 0, 0);
    list.querySelectorAll('tr.conf-up').forEach(function (tr) {
      var d = new Date(tr.getAttribute('data-deadline') + 'T00:00:00'), days = Math.round((d - today) / 864e5);
      var pill = tr.querySelector('.conf-pill');
      if (!pill) return;
      if (days <= 14) pill.classList.add('now'); else if (days <= 45) pill.classList.add('soon');
      pill.title = days === 0 ? 'today' : days + ' days left';
    });
  })();
</script>
