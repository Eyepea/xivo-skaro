{% if vlan_enabled -%}
[ VLAN ]
path = /config/Network/Network.cfg
ISVLAN = 1
VID = {{ vlan_id }}
{% if vlan_priority -%}
USRPRIORITY = {{ vlan_priority }}
{% endif -%}
{% if vlan_pc_port_id -%}
PC_PORT_VLAN_ENABLE = 1
PC_PORT_VID = {{ vlan_pc_port_id }}
{% endif -%}
{% endif -%}

{% if syslog_enabled -%}
[ SYSLOG ]
path = /config/Network/Network.cfg
SyslogdIP = {{ syslog_ip }}
{% endif -%}

{% if XX_lang -%}
[ Lang ]
path = /config/Setting/Setting.cfg
WebLanguage = {{ XX_lang }}
ActiveWebLanguage = {{ XX_lang }}
{% endif -%}

[ Time ]
path = /config/Setting/Setting.cfg
{% if ntp_enabled -%}
TimeServer1 = {{ ntp_ip }}
{% endif -%}
{{ XX_timezone }}

{% if XX_country -%}
[ Country ]
path = /config/voip/tone.ini
Country = {{ XX_country }}
{% endif -%}

{% if X_xivo_phonebook_ip -%}
[ RemotePhoneBook0 ]
path = /config/Setting/Setting.cfg
URL = http://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/search/?name=#SEARCH
Name = XiVO
{% endif -%}

{% if admin_password -%}
[ AdminPassword ]
path = /config/Setting/autop.cfg
password = {{ admin_password }}
{% endif -%}

{% if user_password -%}
[ UserPassword ]
path = /config/Setting/autop.cfg
password = {{ user_password }}
{% endif -%}

[ UserName ]
path = /config/Advanced/Advanced.cfg
{% if admin_username -%}
Admin = {{ admin_username }}
{% endif -%}
{% if user_username -%}
User = {{ user_username }}
{% endif -%}

{% for line in sip_lines.itervalues() %}
[ account ]
path = /config/voip/sipAccount{{ line['XX_line_no'] }}.cfg
Enable = 1
Label = {{ line['display_name'] }}
DisplayName = {{ line['display_name'] }}
AuthName = {{ line['auth_username'] }}
UserName = {{ line['username'] }}
password = {{ line['password'] }}
SIPServerHost = {{ line['proxy_ip'] }}
{% if line['proxy_port'] -%}
SIPServerPort = {{ line['proxy_port'] }}
{% endif -%}

{% if line['XX_dtmf_inband_transfer'] -%}
[ DTMF ]
path = /config/voip/sipAccount{{ line['XX_line_no'] }}.cfg
DTMFInbandTransfer = {{ line['XX_dtmf_inband_transfer'] }}
{% endif -%}

{% if line['voicemail'] -%}
[ Message ]
path = /config/Features/Message.cfg
VoiceNumber{{ line['XX_line_no'] }} = {{ line['voicemail'] }}
{% endif -%}

{% endfor -%}

{{ XX_fkeys }}
