{% if X_xivo_extensions -%}
{% if exten['voicemail] -%}
topsoftkey1 type: speeddial
topsoftkey1 value: {{ exten['voicemail'] }}
topsoftkey1 label: "{{ XX_dict['voicemail'] }}"
{% endif -%}

{% if exten['fwd_unconditional'] -%}
topsoftkey2 type: speeddial
topsoftkey2 value: {{ exten['fwd_unconditional'] }}
topsoftkey2 label: "{{ XX_dict['fwd_unconditional'] }}"
{% endif -%}

{% if exten['dnd'] -%}
topsoftkey3 type: speeddial
topsoftkey3 value: {{ exten['dnd'] }}
topsoftkey3 label: "{{ XX_dict['dnd'] }}"
{% endif -%}

topsoftkey4 type: directory
topsoftkey4 label: "{{ XX_dict['local_directory'] }}"

topsoftkey5 type: callers
topsoftkey5 label: "{{ XX_dict['callers'] }}"

topsoftkey6 type: services
topsoftkey6 label: "{{ XX_dict['services'] }}"

{% if exten['pickup_call'] -%}
topsoftkey7 type: speeddial
topsoftkey7 value: {{ exten['pickup_call'] }}
topsoftkey7 label: "{{ XX_dict['pickup_call'] }}"
{% endif -%}
{% endif -%}

{% if X_xivo_phonebook_ip -%}
softkey1 type: xml
softkey1 value: https://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/search/
softkey1 label: "{{ XX_dict['remote_directory'] }}"
{% endif -%}

{% include 'base.tpl' %}
