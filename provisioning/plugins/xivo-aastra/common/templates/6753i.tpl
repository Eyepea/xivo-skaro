prgkey1 type: speeddial
prgkey1 value: {{ exten['voicemail'] }}

prgkey2 type: speeddial
prgkey2 value: {{ exten['fwdunc'] }}

prgkey3 type: speeddial
prgkey3 value: {{ exten['dnd'] }}

{% if X_xivo_phonebook_ip %}
prgkey4 type: xml
prgkey4 value: https://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/search/
{% else %}
prgkey4 type: none
{% endif %}

prgkey5 type: services

prgkey6 type: xfer


{% include 'base.tpl' %}
