# WARNING: every lines must be less than 80 characters or the phone won't be
# able to read it successfully.

{% if ntp_server_ip -%}
SNTP_ENABLE YES
SNTP_SERVER {{ ntp_server_ip }}
{% endif -%}

{% if admin_password -%}
ADMIN_PASSWORD {{ admin_password }}
{% endif -%}

{{ XX_timezone }}

{% if '1' in sip['lines'] -%}
{% set line = sip['lines']['1'] -%}
{% set proxy_ip = line['proxy_ip'] or sip['proxy_ip'] -%}
SIP_DOMAIN1 {{ proxy_ip }}
SERVER_IP1_1 {{ proxy_ip }}
# SERVER_IP1_2 must be a valid hostname (0.0.0.0 doesn't work) or the
# phone will not be able to register.
SERVER_IP1_2 {{ line['backup_proxy_ip'] or sip['backup_proxy_ip'] or proxy_ip }}
{% set proxy_port = line['proxy_port'] or sip['proxy_port'] or 5060 -%}
SERVER_PORT1_1 {{ proxy_port }}
SERVER_PORT1_2 {{ line['backup_proxy_port'] or sip['backup_proxy_port'] or proxy_port }}

AUTOLOGIN_ENABLE USE_AUTOLOGIN_ID
AUTOLOGIN_AUTHID_KEY01 {{ line['auth_username'] }}
AUTOLOGIN_ID_KEY01 {{ line['username'] }}@{{ proxy_ip }}
AUTOLOGIN_PASSWD_KEY01 {{ line['password'] }}
{% endif -%}

{% if exten['voicemail'] -%}
VMAIL {{ exten['voicemail'] }}
{% endif %}
