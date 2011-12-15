{% extends 'base.tpl' %}
{% block encoding %}ISO-8859-1{% endblock %}
{% block upgrade_rule %}
<Upgrade_Rule>http://{{ ip }}:{{ http_port }}/firmware/spa901-5-1-5.bin</Upgrade_Rule>
{% endblock %}
