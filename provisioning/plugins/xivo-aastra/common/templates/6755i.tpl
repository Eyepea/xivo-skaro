prgkey1 type: speeddial
prgkey1 value: {{ exten['voicemail'] }}

prgkey2 type: speeddial
prgkey2 value: {{ exten['fwdunc'] }}

prgkey3 type: speeddial
prgkey3 value: {{ exten['dnd'] }}

prgkey4 type: directory

prgkey5 type: callers

prgkey6 type: services

{% if X_xivo_phonebook_ip %}
softkey1 type: xml
softkey1 value: https://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/search/
softkey1 label: "{{ XX_dict['remote_directory'] }}"
{% else %}
softkey1 type: none
{% endif %}

softkey3 type: speeddial
softkey3 label: "{{ XX_dict['pickup'] }}"
softkey3 value: {{ exten['pickup'] }}


{% include 'base.tpl' %}
