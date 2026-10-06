---
layout: page
title: Blog
eyebrow: Notes
subtitle: Short write-ups on circuits, FPGAs and the tooling around them.
permalink: /blog/
prose: false
---
{% if site.posts.size > 0 %}
<div class="grid grid-2">
{% for post in site.posts %}
  <a class="card post-card" href="{{ post.url | relative_url }}">
    <div class="date">{{ post.date | date: site.date_format }}</div>
    <h3>{{ post.title }}</h3>
    <p>{{ post.excerpt | strip_html | truncatewords: 40 }}</p>
  </a>
{% endfor %}
</div>
{% else %}
<div class="empty">First post coming soon. Posts live in <code>_posts/</code> as <code>YYYY-MM-DD-title.md</code>.</div>
{% endif %}
