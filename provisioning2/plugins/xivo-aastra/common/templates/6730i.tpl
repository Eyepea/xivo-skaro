{# There's actually no guarantee that neither 'exten' or 'exten["voicemail"]
   will be defined in the context; we need to handle the case (and for every
   others parameter. This is a TODO.
#}
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
prgkey7 type: xml
prgkey7 value: https://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/search/
{% else %}
prgkey7 type: none
{% endif %}


{% include 'base.tpl' %}
