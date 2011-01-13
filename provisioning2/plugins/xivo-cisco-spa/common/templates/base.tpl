<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<flat-profile>

<!-- Note that this file is made to be used in conjunction with other files.
     If you believe some parameters are missing, it's probably because they
     are defined in another file (spa.xml, spa$PSN.cfg common file). -->

<Admin_Passwd>{{ admin_passwd|d('65535')|e }}</Admin_Passwd>
<User_Password>{{ admin_passwd|d('65535')|e }}</User_Password>
<Primary_NTP_Server>{{ ntp_server_ip }}</Primary_NTP_Server>

{% if vlan and vlan['enabled'] -%}
<Enable_VLAN>Yes</Enable_VLAN>
<VLAN_ID>{{ vlan['id'] }}</VLAN_ID>
{% else -%}
<Enable_VLAN>No</Enable_VLAN>
{% endif -%}

{% block upgrade_rule -%}
<Upgrade_Rule></Upgrade_Rule>
{% endblock -%}

<Voice_Mail_Number>{{ exten['vmail'] }}</Voice_Mail_Number>
<Call_Pickup_Code>{{ exten['pickup_prefix'] }}</Call_Pickup_Code>
<Attendant_Console_Call_Pickup_Code>{{ exten['pickup_prefix'] }}</Attendant_Console_Call_Pickup_Code>

{% if 1 in sip['lines'] -%}
<Station_Name>{{ sip['lines'][1]['display_name']|e }}</Station_Name>
{% endif -%}

{% block dictionary_server_script -%}
<Dictionary_Server_Script></Dictionary_Server_Script>
{% endblock -%}
<Language_Selection>{{ XX_language }}</Language_Selection>
{{ XX_timezone }}

{% for line_no, line in sip['lines'].iteritems() %}
<Line_Enable_{{ line_no }}_>Yes</Line_Enable_{{ line_no }}_>

<Proxy_{{ line_no }}_>{{ XX_proxies[line_no] }}</Proxy_{{ line_no }}_>
<Use_DNS_SRV_{{ line_no }}_>Yes</Use_DNS_SRV_{{ line_no }}_>
<Proxy_Fallback_Intvl_{{ line_no }}_>120</Proxy_Fallback_Intvl_{{ line_no }}_>
<Display_Name_{{ line_no }}_>{{ line['display_name']|e }}</Display_Name_{{ line_no }}_>
<User_ID_{{ line_no }}_>{{ line['user_id']|e }}</User_ID_{{ line_no }}_>
<Password_{{ line_no }}_>{{ line['passwd']|e }}</Password_{{ line_no }}_>
<Auth_ID_{{ line_no }}_>{{ line['auth_id']|e }}</Auth_ID_{{ line_no }}_>

<DTMF_Tx_Method_{{ line_no }}_>INFO</DTMF_Tx_Method_{{ line_no }}_>
<Voice_Mail_Server_{{ line_no }}_>{{ line['number'] ~ '@' ~ line['proxy'] }}</Voice_Mail_Server_{{ line_no }}_>
{% endfor -%}

<!-- Function keys definition SHOULD go before the line key definition
     if we want to line key def to override the func key def (is it what we want ?) -->
{{ XX_fkeys }}

{% for line_no, line in sip['lines'].iteritems() %}
<Extension_{{ line_no }}_>{{ line_no }}</Extension_{{ line_no }}_>
<Short_Name_{{ line_no }}_>$USER</Short_Name_{{ line_no }}_>
<Extended_Function_{{ line_no }}_></Extended_Function_{{ line_no }}_>    
{% endfor -%}

</flat-profile>
