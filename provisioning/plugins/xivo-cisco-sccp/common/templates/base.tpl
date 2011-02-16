<device>
 <devicePool>
  <dateTimeSetting>
   <dateTemplate>D-M-YA</dateTemplate>
   <timeZone>{{ XX_timezone }}</timeZone>
   <ntps>
{% if ntp_server -%}
    <ntp>
     <name>{{ ntp_server }}</name>
     <ntpMode>Unicast</ntpMode>
    </ntp>
{% endif -%}
   </ntps>
  </dateTimeSetting>
  <callManagerGroup>
   <members>
{% for priority, call_manager in sccp['call_managers'].iteritems() %}
    <member priority="{{ priority }}">
     <callManager>
      <ports>
       <ethernetPhonePort>{{ call_manager['port']|d('2000') }}</ethernetPhonePort>
      </ports>
      <processNodeName>{{ call_manager['ip'] }}</processNodeName>
     </callManager>
    </member>
{% endfor -%}
   </members>
  </callManagerGroup>
 </devicePool>
 <versionStamp>{Dec 17 2010 16:03:58}</versionStamp>
 <loadInformation>{% block loadInformation %}{% endblock %}</loadInformation>
 <addOnModules>{{ XX_addons }}</addOnModules>

{% if XX_lang -%}
 <userLocale>
  <name>i18n/{{ XX_lang['name'] }}</name>
  <langCode>{{ XX_lang['lang_code'] }}</langCode>
 </userLocale>
 <networkLocale>i18n/{{ XX_lang['network_locale'] }}</networkLocale>
{% endif -%}

 <idleTimeout>0</idleTimeout>
 <authenticationURL></authenticationURL>
{% if X_xivo_phonebook_ip -%}
 <directoryURL>http://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/menu</directoryURL>
{% else -%}
 <directoryURL></directoryURL>
{% endif -%}
 <idleURL></idleURL>
 <informationURL></informationURL>
 <messagesURL></messagesURL>
 <proxyServerURL></proxyServerURL>
 <servicesURL></servicesURL>
</device>
