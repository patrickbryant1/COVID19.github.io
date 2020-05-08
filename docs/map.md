---
title: Map
layout: page
my_variable: map.html
---

{% if page.my_variable %}
  {% include {{ page.my_variable }} %}
{% endif %}
