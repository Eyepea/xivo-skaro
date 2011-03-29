	

	if((servicesgroup_id = dwho_eid('it-userfeatures-servicesgroup_id')) !== false
	&& (accountcode = dwho_eid('userfeatures-accountcode')) !== false)
	{
		dwho.dom.add_event('change',
					servicesgroup_id,
				   function()
				   {
					servicesgroup_id_val = servicesgroup_id.value;
						
					if (typeof servicesgroup_id_val  == "undefined")
						accountcode.value = null;
					else
						accountcode.value = listservicesgroup[servicesgroup_id_val];
				   });
	}