<?xml version="1.0" encoding="UTF-8" ?>
<settings>
  <phone-settings>
    {% if vlan -%}
    <vlan perm="R">{{ vlan['id'] }} {{ vlan['priority']|d('0') }}</vlan>
    {% endif -%}
    
    {% if admin_password -%}
    <admin_mode_password perm="R">{{ admin_password|e }}</admin_mode_password>
    <http_pass perm="R">{{ admin_password|e }}</http_pass>
    {% endif -%}
    {% if admin_username -%}
    <http_user perm="R">{{ admin_username|e }}</http_user>
    {% endif -%}
    {% if ntp_server_ip -%}
    <ntp_server perm="R">{{ ntp_server_ip }}</ntp_server>
    {% endif -%}
    
    {% for line_no, line in sip['lines'].iteritems() %}
    <user_active idx="{{ line_no }}" perm="R">on</user_active>
    <user_idle_text idx="{{ line_no }}" perm="R">{{ line['display_name']|e }}</user_idle_text>
    <user_host idx="{{ line_no }}" perm="R">{{ line['proxy_ip'] or sip['proxy_ip'] }}</user_host>
    <user_name idx="{{ line_no }}" perm="R">{{ line['username']|e }}</user_name>
    <user_pass idx="{{ line_no }}" perm="R">{{ line['password']|e }}</user_pass>
    <user_realname idx="{{ line_no }}" perm="R">{{ line['display_name']|e }}</user_realname>
    <user_mailbox idx="{{ line_no }}" perm="R">{{ line['voicemail'] or exten['voicemail'] }}</user_mailbox>
    <user_dtmf_info idx="{{ line_no }}" perm="R">{{ line['XX_user_dtmf_info'] }}</user_dtmf_info>
    {% endfor -%}
    
    {% if X_xivo_phonebook_ip -%}
    <dkey_directory perm="R">url http://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/search/</dkey_directory>
    {% endif -%}
    
    {% if XX_lang -%}
    <language perm="R">{{ XX_lang[0] }}</language>
    <web_language perm="R">{{ XX_lang[0] }}</language>
    <tone_scheme perm="R">{{ XX_lang[1] }}</tone_scheme>
    {% endif -%}
    
{{ XX_timezone }}
  </phone-settings>
  {% if XX_fkeys -%}
  <functionKeys>
{{ XX_fkeys }}
  </functionKeys>
  {% endif -%}
</settings>
