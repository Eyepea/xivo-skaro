<?xml version="1.0" encoding="UTF-8" ?>
<settings>
  <phone-settings>
    {% if vlan %}
    <vlan perm="R">{{ vlan['id'] }} {{ vlan['prio'] }}</vlan>
    {% else %}
    <vlan perm="R"></vlan>
    {% endif %}
    
    <admin_mode_password perm="R">{{ admin_passwd|d('65535')|e }}</admin_mode_password>
    <ntp_server perm="R">{{ ntp_server }}</ntp_server>
    
    {% for line_no, line in sip['lines'].iteritems() %}
    <user_idle_text idx="{{ line_no }}" perm="R">{{ line['display_name']|e }}</user_idle_text>
    <user_host idx="{{ line_no }}" perm="R">{{ line['proxy_ip'] }}</user_host>
    <user_name idx="{{ line_no }}" perm="R">{{ line['user_id']|e }}</user_name>
    <user_pass idx="{{ line_no }}" perm="R">{{ line['passwd']|e }}</user_pass>
    <user_realname idx="{{ line_no }}" perm="R">{{ line['display_name']|e }}</user_realname>
    {% endif %}
    
    {% if X_xivo_phonebook_ip %}
    <dkey_directory perm="R">url http://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/search/</dkey_directory>
    {% endif %}
    
    {% if XX_lang %}
    <language perm="R">{{ XX_lang[0] }}</language>
    <web_language perm="R">{{ XX_lang[0] }}</language>
    <tone_scheme perm="R">{{ XX_lang[1] }}</tone_scheme>
    {% endif %}
    
{{ XX_timezone }}
  </phone-settings>
  <functionKeys>
{{ XX_fkeys }}
  </functionKeys>
</settings>
