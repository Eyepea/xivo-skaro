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

{% if exten['pickup_call'] -%}
softkey3 type: speeddial
softkey3 label: "{{ XX_dict['pickup_call'] }}"
softkey3 value: {{ exten['pickup_call'] }}
{% endif -%}
{% endif -%}

{% if X_xivo_phonebook_ip -%}
softkey1 type: xml
softkey1 value: https://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/search/
softkey1 label: "{{ XX_dict['remote_directory'] }}"
{% endif -%}

{% include 'base.tpl' %}
