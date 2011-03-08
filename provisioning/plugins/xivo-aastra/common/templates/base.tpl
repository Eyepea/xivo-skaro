http server: {{ ip }}
http port: {{ http_port }}

{# VLAN settings -#}
{% if vlan -%}
tagging enabled: 1
vlan id: {{ vlan['id'] }}
{% if vlan['priority'] is defined -%}
priority non-ip: {{ vlan['priority'] }}
{% endif -%}
vlan id port 1: 4095
{% else -%}
tagging enabled: 0
{% endif -%}

{# NTP settings -#}
{% if ntp_server -%}
time server disabled: 0
time server1: {{ ntp_server }}
{% else -%}
time server disabled: 1
{% endif -%}

{% if admin_password -%}
admin password: {{ admin_password }}
{% endif -%}
{% if user_password -%}
user password: {{ user_password }}
{% endif -%}

{{ XX_timezone }}

{% if locale == 'de_DE' -%}
language: 1
language 1: i18n/lang_de.txt
tone set: Germany
input language: German
{% elif locale == 'es_ES' -%}
language: 1
language 1: i18n/lang_es.txt
tone set: Europe
input language: Spanish
{% elif locale == 'fr_FR' -%}
language: 1
language 1: i18n/lang_fr.txt
tone set: France
input language: French
{% elif locale == 'fr_CA' -%}
language: 1
language 1: i18n/lang_fr_ca.txt
tone set: US
input language: French
{% else -%}
language: 0
tone set: US
input language: English
{% endif -%}

{# SIP global settings -#}
{# DTMF -#}
{% if sip['dtmf_mode'] == 'RTP-in-band' -%}
sip out-of-band dtmf: 0
sip dtmf method: 0
{% elif sip['dtmf_mode'] == 'RTP-out-of-band' -%}
sip out-of-band dtmf: 1
sip dtmf method: 0
{% elif sip['dtmf_mode'] == 'SIP-INFO' -%}
sip dtmf method: 1
{% endif -%}

{% if sip['subscribe_mwi'] is defined -%}
sip explicit mwi subscription: {{ sip['subscribe_mwi']|int }}
{% endif -%}

{# SIP per-line settings -#}
{% for line_no, line in sip['lines'].iteritems() %}
sip line{{ line_no }} proxy ip: {{ line['proxy_ip'] }}
sip line{{ line_no }} registrar ip: {{ line['registrar_ip'] }}
{% if line['backup_proxy_ip'] -%}
sip line{{ line_no }} backup proxy ip: {{ line['backup_proxy_ip'] }}
{% endif -%}
{% if line['backup_registrar_ip'] -%}
sip line{{ line_no }} backup registrar ip: {{ line['backup_registrar_ip'] }}
{% endif -%}
sip line{{ line_no }} user name: {{ line['username'] }}
sip line{{ line_no }} auth name: {{ line['auth_username'] }}
sip line{{ line_no }} password: {{ line['password'] }}
sip line{{ line_no }} display name: {{ line['display_name'] }}
sip line{{ line_no }} screen name: {{ line['display_name'] }}
{% if line['number'] -%}
sip line{{ line_no }} screen name 2: {{ line['number'] }}
{% endif -%}
{% endfor -%}

{% if exten['voicemail'] -%}
sip vmail: {{ exten['voicemail'] }}
{% endif -%}

{% if exten['pickup_call'] -%}
directed call pickup prefix: {{ exten['pickup_call'] }}
{% endif -%}

{{ XX_fkeys }}
