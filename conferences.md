---
layout: page
title: Conference Deadlines
eyebrow: Digital VLSI · EDA · FPGA
subtitle: Paper deadlines I track. Drag the timeline, hover a marker, click it to jump to the row.
permalink: /conferences/
prose: false
description: Upcoming paper submission deadlines for VLSI, EDA and FPGA conferences, with an interactive timeline.
---
{% assign confs = site.data.conferences | sort: "deadline" %}
{% assign today = site.time | date: "%Y-%m-%d" %}
{% assign shown = 10 %}

<div class="tl" id="tl">
  <div class="tl-bar">
    <div class="group">
      <span class="muted" style="font-size:.8rem;font-weight:800;margin-right:.3rem">Range</span>
      <button class="tl-btn" data-months="6">6 mo</button>
      <button class="tl-btn on" data-months="12">12 mo</button>
      <button class="tl-btn" data-months="18">18 mo</button>
      <button class="tl-btn" id="tl-today">Today</button>
      <button class="tl-btn" id="tl-past" aria-pressed="false">Show past</button>
    </div>
    <div class="tl-legend">
      <span><i style="background:var(--crit)"></i>≤ 14 days</span>
      <span><i style="background:var(--warn)"></i>≤ 45 days</span>
      <span><i style="background:var(--ok)"></i>later</span>
      <span><i class="ev"></i>conference</span>
    </div>
  </div>
  <div class="tl-scroll" id="tl-scroll"><div class="tl-canvas" id="tl-canvas"></div></div>
  <div class="tl-tip" id="tl-tip"></div>
</div>

<table class="conf-list" id="conf-list">
  <thead><tr><th>Conference</th><th>Home page</th><th>Paper deadline</th><th>Conference date</th></tr></thead>
  <tbody>
  {%- assign n = 0 -%}
  {%- for c in confs -%}
    {%- assign dl = c.deadline | default: "" -%}
    {%- if dl == "" or dl < today -%}{%- continue -%}{%- endif -%}
    {%- assign n = n | plus: 1 -%}
    <tr class="conf-up{% if n > shown %} conf-more{% endif %}" id="conf-{{ c.name | slugify }}" data-deadline="{{ dl }}">
      <td class="conf-name">{{ c.name }}</td>
      <td class="conf-url"><a href="{{ c.url }}" target="_blank" rel="noopener">{{ c.url | remove: "https://" | remove: "http://" | remove: "www." | split: "/" | first }}</a></td>
      <td class="conf-date"><span class="conf-pill ok">{{ dl }}</span>{% if c.note %}<small>{{ c.note }}</small>{% endif %}</td>
      <td class="conf-date">{{ c.date | default: "TBD" }}</td>
    </tr>
  {%- endfor -%}
  {%- for c in confs -%}
    {%- assign dl = c.deadline | default: "" -%}
    {%- if dl != "" -%}{%- continue -%}{%- endif -%}
    {%- assign n = n | plus: 1 -%}
    <tr class="conf-tbd{% if n > shown %} conf-more{% endif %}" id="conf-{{ c.name | slugify }}">
      <td class="conf-name">{{ c.name }}</td>
      <td class="conf-url"><a href="{{ c.url }}" target="_blank" rel="noopener">{{ c.url | remove: "https://" | remove: "http://" | remove: "www." | split: "/" | first }}</a></td>
      <td class="conf-date">TBD{% if c.note %}<small>{{ c.note }}</small>{% endif %}</td>
      <td class="conf-date">{{ c.date | default: "TBD" }}</td>
    </tr>
  {%- endfor -%}
  {%- assign past = confs | reverse -%}
  {%- for c in past -%}
    {%- assign dl = c.deadline | default: "" -%}
    {%- if dl == "" or dl >= today -%}{%- continue -%}{%- endif -%}
    {%- assign n = n | plus: 1 -%}
    <tr class="conf-past{% if n > shown %} conf-more{% endif %}" id="conf-{{ c.name | slugify }}" data-deadline="{{ dl }}">
      <td class="conf-name">{{ c.name }}</td>
      <td class="conf-url"><a href="{{ c.url }}" target="_blank" rel="noopener">{{ c.url | remove: "https://" | remove: "http://" | remove: "www." | split: "/" | first }}</a></td>
      <td class="conf-date">{{ dl }}{% if c.note %}<small>{{ c.note }}</small>{% endif %}</td>
      <td class="conf-date">{{ c.date | default: "TBD" }}</td>
    </tr>
  {%- endfor -%}
  </tbody>
</table>
{%- assign hidden = n | minus: shown -%}
{%- if hidden > 0 -%}
<button type="button" class="btn conf-toggle" id="conf-toggle" aria-expanded="false" aria-controls="conf-list"><span class="conf-arrow"></span><span class="conf-toggle-text">Show {{ hidden }} more</span></button>
{%- endif -%}

<details class="conf-approx card">
  <summary><span class="conf-arrow"></span>Approximate deadlines, for planning before a CFP is out</summary>
  <div class="conf-approx-grid">
    <div><h3>VLSI design</h3><ul><li>VLSI Symposium – mid January</li><li>ISLPED – mid March</li><li>MWSCAS – mid March</li><li>HEART – mid March</li><li>CICC – early April</li><li>SOCC – early April</li><li>VLSI-SoC – mid April</li><li>ICCD – early May</li><li>ISQED – early October</li><li>ISCAS – early October</li><li>GLSVLSI – December</li></ul></div>
    <div><h3>VLSI CAD</h3><ul><li>ICCAD – mid April</li><li>IWLS – mid April</li><li>ASP-DAC – mid July</li><li>DATE – early September</li><li>ISPD – early October</li><li>DAC – late November</li></ul></div>
    <div><h3>FPGA</h3><ul><li>FCCM – mid January</li><li>FPL – late March</li><li>CODES+ISSS – mid April</li><li>FPT – June</li><li>ISFPGA – early October</li></ul></div>
  </div>
  <p class="muted" style="font-size:.85rem;margin:.8rem 0 .2rem">Typical windows; they move by a few weeks from year to year. Confirm on the official site.</p>
</details>

<script>
window.CONF_DATA = [
{%- for c in confs -%}
  {%- assign dl = c.deadline | default: "" -%}
  {"name": {{ c.name | jsonify }}, "url": {{ c.url | jsonify }}, "deadline": {{ dl | jsonify }}, "date": {{ c.date | default: "" | jsonify }}, "id": {{ c.name | slugify | jsonify }}}{% unless forloop.last %},{% endunless %}
{%- endfor -%}
];
</script>
<script src="{{ '/assets/js/timeline.js' | relative_url }}"></script>
