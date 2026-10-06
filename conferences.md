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

<p class="conf-note">Dates come from each conference's call for papers and can move; check the official site before planning around one. To add or fix an entry, edit <code>_data/conferences.yml</code>.</p>

<style>
  .conf-intro, .conf-note { color: var(--text-light, #6c757d); font-size: .95em; }
  .conf-list { font-size: .95em; }
  .conf-list td.conf-date { font-variant-numeric: tabular-nums; white-space: nowrap; }
  .conf-list td.conf-date small { color: var(--text-light, #6c757d); font-weight: 400; }
  .conf-list tr.conf-past td { color: #9aa0a6; }
  .conf-list tr.conf-past td a { color: #9aa0a6; }
  .conf-list tr.conf-tbd td { font-style: italic; }
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
