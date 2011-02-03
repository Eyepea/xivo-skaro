{# Can use an IP address or a FQDN #}
http server: {{ ip }}
http port: {{ http_port }}

admin password: {{ admin_passwd|d('65535') }}

{# VLAN settings #}
{% if vlan and vlan['enabled'] %}
tagging enabled: 1
vlan id: {{ vlan['id'] }}
vlan id port 1: 4095
{% else %}
tagging enabled: 0
{% endif %}

{# NTP settings #}
{% if ntp_server %}
time server disabled: 0
time server1: {{ ntp_server }}
{% else %}
time server disabled: 1
{% endif %}

{# SIP settings #}
{% for line_no, line in sip['lines'].iteritems() %}
sip line{{ line_no }} proxy ip: {{ line['proxy_ip'] }}
sip line{{ line_no }} proxy port: 5060
sip line{{ line_no }} registrar ip: {{ line['registrar_ip'] }}
sip line{{ line_no }} registrar port: 5060
sip line{{ line_no }} backup proxy ip: {{ line['backup_proxy_ip']|d('0.0.0.0') }}
sip line{{ line_no }} backup proxy port: 5060
sip line{{ line_no }} backup registrar ip: {{ line['backup_registrar_ip']|d('0.0.0.0') }}
sip line{{ line_no }} backup registrar port: 5060
sip line{{ line_no }} screen name: {{ line['display_name'] }}
sip line{{ line_no }} screen name 2: {{ line['number'] }}
sip line{{ line_no }} auth name: {{ line['auth_id'] }}
sip line{{ line_no }} password: {{ line['passwd'] }}
sip line{{ line_no }} user name: {{ line['user_id'] }}
sip line{{ line_no }} display name: {{ line['display_name'] }}
{% endfor %}

sip explicit mwi subscription: {{ subscribe_mwi|int }}
sip vmail: {{ exten['voicemail'] }}

directed call pickup prefix: {{ exten['pickup_prefix'] }}

{% if locale == 'de_DE' %}
language: 1
language 1: i18n/lang_de.txt
tone set: Germany
input language: German
{% elif locale == 'es_ES' %}
language: 1
language 1: i18n/lang_es.txt
tone set: Europe
input language: Spanish
{% elif locale == 'fr_FR' %}
language: 1
language 1: i18n/lang_fr.txt
tone set: France
input language: French
{% elif locale == 'fr_CA' %}
language: 1
language 1: i18n/lang_fr_ca.txt
tone set: US
input language: French
{% else %}
language: 0
tone set: US
input language: English
{% endif %}

{{ XX_timezone }}
{{ XX_fkeys }}
