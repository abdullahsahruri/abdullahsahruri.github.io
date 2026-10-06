---
layout: page
title: Research
eyebrow: Threshold logic, from cells to systems
subtitle: My dissertation, "Beyond Boolean", advances threshold logic gates from circuit foundations to system-level applications.
permalink: /research/
prose: false
description: Research areas and publications of Abdullah Sahruri.
---
{% assign pubs = site.data.publications %}

<div class="grid grid-3" style="margin-bottom:2.5rem">
{% for a in site.data.research_areas %}
  <div class="card area"><div class="icon"><i class="fas {{ a.icon }}"></i></div><h3>{{ a.title }}</h3><p>{{ a.text }}</p></div>
{% endfor %}
</div>

<div class="section-head"><div><div class="eyebrow">Peer-reviewed</div><h2>Publications</h2></div><span class="muted">{{ pubs | size }} entries · edit <code>_data/publications.yml</code></span></div>
<div class="card">
{% for p in pubs %}
  <div class="pub">
    <div class="year">{{ p.year }}</div>
    <div>
      <h3>{% if p.doi %}<a href="https://doi.org/{{ p.doi }}">{{ p.title }}</a>{% elsif p.url %}<a href="{{ p.url }}">{{ p.title }}</a>{% else %}{{ p.title }}{% endif %}</h3>
      <p class="authors">{{ p.authors | markdownify | remove: "<p>" | remove: "</p>" }}</p>
      <div class="venue">
        <span class="chip {% if p.type == 'journal' %}violet{% elsif p.type == 'poster' %}amber{% else %}accent{% endif %}">{{ p.type }}</span>
        <span>{{ p.venue }}</span>
        {% if p.doi %}<a href="https://doi.org/{{ p.doi }}">doi:{{ p.doi }}</a>{% endif %}
        {% if p.note %}<span class="chip">{{ p.note }}</span>{% endif %}
      </div>
    </div>
  </div>
{% endfor %}
</div>

<div class="grid grid-2" style="margin-top:2rem">
  <div class="card">
    <div class="eyebrow">Service</div>
    <h3>Reviewing</h3>
    <p class="muted" style="margin:0">Reviewer for IEEE ISCAS (digital IC design and verification, EDA and physical design, low-power logic) and for JETTA. Member of IEEE and ACM.</p>
  </div>
  <div class="card">
    <div class="eyebrow">Tools</div>
    <h3>Stack</h3>
    <p class="muted" style="margin:0">Cadence Virtuoso, Spectre and Liberate · SKY130A open PDK · Verilog, SystemVerilog, VHDL · Vivado and VPR · Python, TCL, PyTorch</p>
  </div>
</div>
