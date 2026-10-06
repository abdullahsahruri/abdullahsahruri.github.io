---
layout: page
title: Conference Deadlines
subtitle: Paper deadlines for digital VLSI, EDA and FPGA venues
---

{% assign confs = site.data.conferences | sort: "deadline" %}
{% assign today = site.time | date: "%Y-%m-%d" %}

<p class="conf-intro">Upcoming paper deadlines first, soonest at the top; venues whose call for papers is not out yet are listed as TBD, and past deadlines follow below. Built on <a href="https://www.cse.chalmers.se/research/group/vlsi/conference/">the Chalmers VLSI group's list</a>, with FPGA venues added. Last rebuilt {{ site.time | date: "%Y-%m-%d" }}.</p>

<table class="conference-table conf-list" id="conf-list">
  <thead>
    <tr><th>Conference</th><th>Home page</th><th>Paper deadline</th><th>Conference date</th></tr>
  </thead>
  <tbody>
  {%- comment -%} 1. upcoming deadlines, soonest first {%- endcomment -%}
  {% for c in confs %}
    {% if c.deadline == "" or c.deadline < today %}{% continue %}{% endif %}
    <tr data-deadline="{{ c.deadline }}"{% if c.deadline < today %} class="conf-past"{% endif %}>
      <td class="conf-name">{{ c.name }}</td>
      <td class="conf-url"><a href="{{ c.url }}" target="_blank" rel="noopener">{{ c.url | remove: "https://" | remove: "http://" | remove: "www." | split: "/" | first }}</a></td>
      <td class="conf-date">{{ c.deadline }}{% if c.note %} <small>({{ c.note }})</small>{% endif %}</td>
      <td class="conf-date">{{ c.date }}</td>
    </tr>
  {% endfor %}
  {%- comment -%} 2. venues whose CFP is not out yet {%- endcomment -%}
  {% for c in confs %}
    {% if c.deadline != "" %}{% continue %}{% endif %}
    <tr class="conf-tbd">
      <td class="conf-name">{{ c.name }}</td>
      <td class="conf-url"><a href="{{ c.url }}" target="_blank" rel="noopener">{{ c.url | remove: "https://" | remove: "http://" | remove: "www." | split: "/" | first }}</a></td>
      <td class="conf-date">TBD{% if c.note %} <small>({{ c.note }})</small>{% endif %}</td>
      <td class="conf-date">{% if c.date != "" %}{{ c.date }}{% else %}TBD{% endif %}</td>
    </tr>
  {% endfor %}
  {%- comment -%} 3. past deadlines, most recent first {%- endcomment -%}
  <tr class="conf-divider"><td colspan="4">Past deadlines</td></tr>
  {% assign past = confs | reverse %}
  {% for c in past %}
    {% if c.deadline == "" or c.deadline >= today %}{% continue %}{% endif %}
    <tr data-deadline="{{ c.deadline }}"{% if c.deadline < today %} class="conf-past"{% endif %}>
      <td class="conf-name">{{ c.name }}</td>
      <td class="conf-url"><a href="{{ c.url }}" target="_blank" rel="noopener">{{ c.url | remove: "https://" | remove: "http://" | remove: "www." | split: "/" | first }}</a></td>
      <td class="conf-date">{{ c.deadline }}{% if c.note %} <small>({{ c.note }})</small>{% endif %}</td>
      <td class="conf-date">{{ c.date }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>


<div class="conf-approx">
  <h2>Approximate deadlines</h2>
  <p>Typical submission windows, for planning before a call for papers is out. Always confirm on the official site.</p>
  <div class="conf-approx-grid">
    <div>
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
    <div>
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
    <div>
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
</div>

<p class="conf-note">Dates come from each conference's call for papers and can move; check the official site before planning around one. The list is refreshed automatically from the Chalmers page every week.</p>

<style>
  .conf-intro, .conf-note { color: var(--text-light, #6c757d); font-size: .95em; }
  .conf-list { font-size: .95em; }
  .conf-list td.conf-date { font-variant-numeric: tabular-nums; white-space: nowrap; }
  .conf-list td.conf-date small { color: var(--text-light, #6c757d); font-weight: 400; }
  .conf-list tr.conf-past td { color: #9aa0a6; }
  .conf-list tr.conf-past td a { color: #9aa0a6; }
  .conf-list tr.conf-tbd td { font-style: italic; }
  .conf-approx { margin-top: 3rem; padding: 1.5rem 2rem; background: var(--bg-light, #f7f8fa); border-left: 4px solid var(--primary-color, #6c757d); border-radius: 5px; }
  .conf-approx h2 { margin-top: 0; font-size: 1.4em; }
  .conf-approx h3 { font-size: 1.05em; margin-bottom: .5rem; }
  .conf-approx p { color: var(--text-light, #6c757d); font-size: .95em; }
  .conf-approx-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; }
  .conf-approx ul { list-style: none; padding-left: 0; line-height: 1.8; margin: 0; }
  .conf-list tr.conf-divider td { background: var(--bg-light, #f3f4f6); color: var(--text-light, #6c757d); font-size: .8em; text-transform: uppercase; letter-spacing: .06em; padding: 6px 12px; }
  @media (max-width: 600px) {
    .conf-list th:nth-child(2), .conf-list td:nth-child(2) { display: none; }
    .conf-list td, .conf-list th { padding: 8px 6px; }
  }
</style>

<script>
  /* The build marks past deadlines as of build time; refresh the marking against the visitor's clock. */
  (function () {
    var today = new Date().toISOString().slice(0, 10);
    document.querySelectorAll('#conf-list tr[data-deadline]').forEach(function (tr) {
      tr.classList.toggle('conf-past', tr.getAttribute('data-deadline') < today);
    });
  })();
</script>
