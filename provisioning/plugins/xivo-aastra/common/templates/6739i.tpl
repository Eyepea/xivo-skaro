softkey1 type: speeddial
softkey1 label: "{{ XX_dict['fwdunc'] }}"
softkey1 value: {{ exten['fwdunc'] }}

softkey2 type: speeddial
softkey2 label: "{{ XX_dict['dnd'] }}"
softkey2 value: {{ exten['dnd'] }}

{% if X_xivo_phonebook_ip %}
softkey3 type: xml
softkey3 label: "{{ XX_dict['remote_directory'] }}"
softkey3 value: https://{{ X_xivo_phonebook_ip }}/service/ipbx/web_services.php/phonebook/search/
{% else %}
softkey3 type: none
{% endif %}


{% include 'base.tpl' %}
