topsoftkey1 type: speeddial
topsoftkey1 value: {{ exten['voicemail'] }}
topsoftkey1 label: "{{ XX_dict['voicemail'] }}"

topsoftkey2 type: speeddial
topsoftkey2 value: {{ exten['fwdunc'] }}
topsoftkey2 label: "{{ XX_dict['fwdunc'] }}"

topsoftkey3 type: speeddial
topsoftkey3 value: {{ exten['dnd'] }}
topsoftkey3 label: "{{ XX_dict['dnd'] }}"

topsoftkey4 type: directory
topsoftkey4 label: "{{ XX_dict['local_directory'] }}"

topsoftkey5 type: callers
topsoftkey5 label: "{{ XX_dict['callers'] }}"

topsoftkey6 type: services
topsoftkey6 label: "{{ XX_dict['services'] }}"

topsoftkey7 type: speeddial
topsoftkey7 value: {{ exten['pickup'] }}
topsoftkey7 label: "{{ XX_dict['pickup'] }}"

{% if X_xivo_phonebook_ip %}
softkey1 type: xml
softkey1 value: https://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/search/
softkey1 label: "{{ XX_dict['remote_directory'] }}"
{% else %}
softkey1 type: none
{% endif %}


{% include 'base.tpl' %}
