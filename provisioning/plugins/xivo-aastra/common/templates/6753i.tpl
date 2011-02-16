{% if X_xivo_extensions -%}
{% if exten['voicemail] -%}
prgkey1 type: speeddial
prgkey1 value: {{ exten['voicemail'] }}
{% endif -%}

{% if exten['fwd_unconditional'] -%}
prgkey2 type: speeddial
prgkey2 value: {{ exten['fwd_unconditional'] }}
{% endif -%}

{% if exten['dnd'] -%}
prgkey3 type: speeddial
prgkey3 value: {{ exten['dnd'] }}
{% endif -%}

prgkey4 type: directory

prgkey5 type: callers

prgkey6 type: services
{% endif -%}

{% if X_xivo_phonebook_ip -%}
prgkey7 type: xml
prgkey7 value: https://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/search/
{% endif -%}

{% include 'base.tpl' %}
