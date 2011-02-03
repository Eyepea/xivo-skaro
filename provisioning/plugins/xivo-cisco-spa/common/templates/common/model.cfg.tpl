<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<flat-profile>

<Provision_Enable>Yes</Provision_Enable>
<Resync_Periodic>10</Resync_Periodic>
<Resync_Random_Delay>1</Resync_Random_Delay>
<Profile_Rule>http://{{ ip }}:{{ http_port }}/spa.xml</Profile_Rule>
<Profile_Rule_B>http://{{ ip }}:{{ http_port }}/$MA.xml</Profile_Rule_B>

</flat-profile>
