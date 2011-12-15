{% extends 'base.tpl' %}
{% block encoding %}ISO-8859-1{% endblock %}
{% block upgrade_rule %}
<Upgrade_Rule>http://{{ ip }}:{{ http_port }}/firmware/spa941-5-1-8.bin</Upgrade_Rule>
{% endblock %}
