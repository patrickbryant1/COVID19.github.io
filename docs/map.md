---
title: Maps
layout: page
my_variable1: map_cases.html
my_variable2: map_deaths.html
---

## Deaths per day
{% if page.my_variable2 %}
  {% include {{ page.my_variable2 }} %}
{% endif %}
