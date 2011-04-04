{# Note: if you remove a parameter in the MAC configuration file thinking
         that the value in the common configuration file will apply, you
         are wrong. You'll get this behaviour only after changing the name
         of the common configuration file (and updating the .inf file).
-#}

[ipp]
LanguageType={{ XX_language_type }}

[net]
{% if vlan -%}
VLAN=1
{% else -%}
VLAN=0
{% endif %}

[sip]
{% for line_no in range(1, 5) -%}
{% set line_no = line_no|string -%}
{% if line_no in sip['lines'] -%}
{% set line = sip['lines'][line_no] -%}
DisplayNumFlag{{ line_no }}=1
DisplayNum{{ line_no }}={{ line['number'] }}
DisplayName{{ line_no }}={{ line['display_name'] }}
ProxyServerMP{{ line_no }}={{ line['proxy_ip'] or sip['proxy_ip'] }}
ProxyServerBK{{ line_no }}={{ line['backup_proxy_ip'] or sip['backup_proxy_ip'] }}
regid{{ line_no }}={{ line['auth_username'] }}
regpwd{{ line_no }}={{ line['password'] }}
TEL{{ line_no }}Number={{ line['username'] }}
TEL0{{ line_no }}Use=1
{% else -%}
DisplayNumFlag{{ line_no }}=0
DisplayNum{{ line_no }}=
DisplayName{{ line_no }}=
ProxyServerMP{{ line_no }}=
ProxyServerBK{{ line_no }}=
regid{{ line_no }}=
regpwd{{ line_no }}=
TEL{{ line_no }}Number=
TEL0{{ line_no }}Use=0
{% endif %}
{% endfor %}

{% if exten['voicemail'] -%}
VoiceMailTelNum={{ exten['voicemail'] }}
{% else -%}
VoiceMailTelNum=
{% endif -%}

{% if sip['subscribe_mwi'] -%}
subscribe_event=1
{% else -%}
subscribe_event=0
{% endif %}

[sys]
config_sn={{ XX_config_sn }}
CountryCode={{ XX_country_code }}
dtmf_mode_flag={{ XX_dtmf_mode_flag }}
{% if X_xivo_phonebook_ip -%}
Phonebook1_url=https://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/search/?name=#SEARCH
{% else -%}
Phonebook1_url=
{% endif -%}
Phonebook1_name={{ XX_phonebook_name }}

{% for fkey_no in range(1, 66) -%}
{% set fkey_no_s = fkey_no|string -%}
{% if fkey_no_s in XX_function_keys -%}
FeatureKeyExt{{ '{0:02d}'.format(fkey_no) }}={{ XX_function_keys[fkey_no_s] }}
{% else -%}
FeatureKeyExt{{ '{0:02d}'.format(fkey_no) }}=L/<sip:>
{% endif -%}
{% endfor -%}

{% if user_username is defined -%}
UserID={{ user_username }}
{% endif -%}
{% if user_password is defined -%}
UserPWD={{ user_password }}
{% endif -%}
{% if admin_username is defined -%}
TelnetID={{ admin_username }}
{% endif -%}
{% if admin_password is defined -%}
TelnetPWD={{ admin_password }}
WebPWD={{ admin_password }}
{% endif %}

[qos]
{% if vlan -%}
VLANid1={{ vlan['id'] }}
{% if vlan['pc_port_id'] -%}
VLANid2={{ vlan['pc_port_id'] }}
{% endif -%}
{% if vlan['priority'] is defined -%}
VLANTag1={{ vlan['priority'] }}
{% endif %}
{% endif %}

[ntp]
{% if ntp_server_ip -%}
NTPFlag=1
NtpIP={{ ntp_server_ip }}
{% else -%}
NTPFlag=0
{% endif -%}
NtpZoneNum={{ XX_ntp_zone_num }}
