/*
 * XiVO Web-Interface
 * Copyright (C) 2006-2011  Proformatique <technique@proformatique.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

var xivo_ast_users_elt = {'links': {'link': []}};
var xivo_ast_fm_users = {};

var xivo_ast_users_elt_default = {	
	'userfeatures-firstname': {it: true},
	'userfeatures-lastname': {it: true},
	'userfeatures-entity': {it: true},
	'userfeatures-ringseconds': {it: true},
	'userfeatures-simultcalls': {it: true},
	'userfeatures-musiconhold': {it: true},
	'userfeatures-enableclient': {it: true},
	'userfeatures-loginclient': {it: true},
	'userfeatures-passwdclient': {it: true},
	'userfeatures-profileclient': {it: true},
	'userfeatures-enablehint': {it: true},
	'userfeatures-enablexfer': {it: true},
	'userfeatures-enableautomon': {it: true},
	'userfeatures-callrecord': {it: true},
	'userfeatures-incallfilter': {it: true},
	'userfeatures-enablednd': {it: true},
	'userfeatures-enablerna': {it: true},
	'userfeatures-destrna': {it: true},
	'userfeatures-enablebusy': {it: true},
	'userfeatures-destbusy': {it: true},
	'userfeatures-enableunc': {it: true},
	'userfeatures-destunc': {it: true},
	'userfeatures-bsfilter': {it: true},
	'userfeatures-agentid': {it: true},
	'userfeatures-outcallerid-type': {it: true},
	'userfeatures-outcallerid-custom': {it: true},
	'userfeatures-preprocess-subroutine': {it: true},
	'userfeatures-description': {it: true},
	'userfeatures-voicemailtype': {it: true, fd: true},
	'userfeatures-voicemailid': {it: true, fd: false},
	'userfeatures-callerid': {it: true},
	'userfeatures-entityid': {it: true},
	'userfeatures-enablevoicemail': {it: true},

	'voicemail-option': {it: true},
	'voicemail-suggest': {it: false, fd: false},
	'voicemail-fullname': {it: false},
	'voicemail-mailbox': {it: false},
	'voicemail-password': {it: false},
	'voicemail-email': {it: false},
	'voicemail-tz': {it: false},
	'voicemailfeatures-skipcheckpass': {it: false},
	'voicemail-attach': {it: false},
	'voicemail-deletevoicemail': {it: false},

	'grouplist': {it: true},
	'group': {it: true},

	'rightcalllist': {it: true},
	'rightcall': {it: true}};


var xivo_ast_fm_user_enableclient = {
	'it-userfeatures-profileclient':
		{property: [{disabled: true, className: 'it-readonly'},
			    {disabled: false, className: 'it-enabled'}]}};

xivo_attrib_register('ast_fm_user_enableclient',xivo_ast_fm_user_enableclient);

var xivo_ast_fm_user_enablerna = {
	'it-userfeatures-destrna':
		{property: [{readOnly: true, className: 'it-readonly'},
			    {readOnly: false, className: 'it-enabled'}]}};

xivo_attrib_register('ast_fm_user_enablerna',xivo_ast_fm_user_enablerna);

var xivo_ast_fm_user_enablebusy = {
	'it-userfeatures-destbusy':
		{property: [{readOnly: true, className: 'it-readonly'},
			    {readOnly: false, className: 'it-enabled'}]}};

xivo_attrib_register('ast_fm_user_enablebusy',xivo_ast_fm_user_enablebusy);

var xivo_ast_fm_user_enableunc = {
	'it-userfeatures-destunc':
		{property: [{readOnly: true, className: 'it-readonly'},
			    {readOnly: false, className: 'it-enabled'}]}};

xivo_attrib_register('ast_fm_user_enableunc',xivo_ast_fm_user_enableunc);

var xivo_ast_fm_user_voicemailtype = {
 'it-userfeatures-voicemailid':
    {property: [{disabled: true},{disabled: false}],
     link: 'it-voicemail-option'},
 'it-voicemail-option':
    {property: [{disabled: true, className: 'it-disabled'},
          {disabled: false, className: 'it-enabled'}]}};

xivo_attrib_register('ast_fm_user_voicemailtype',xivo_ast_fm_user_voicemailtype);

var xivo_ast_fm_user_voicemailoption = {
	'fd-voicemail-suggest':
		{style: [{display: 'none'}, {display: 'block'}],
		 link: 'it-voicemail-suggest'},
	'it-voicemail-suggest':
		{property: [{disabled: true, className: 'it-disabled'},
			    {disabled: false, className: 'it-enabled'}]}};

xivo_attrib_register('ast_fm_user_voicemailoption',xivo_ast_fm_user_voicemailoption);

var xivo_ast_fm_user_outcallerid = {
	'fd-userfeatures-outcallerid-custom':
		{style: [{display: 'none'}, {display: 'block'}],
		 link: 'it-outcallerid-custom'},
	'it-userfeatures-outcallerid-custom':
		{property: [{disabled: true}, {disabled: false}]}};

xivo_attrib_register('ast_fm_user_outcallerid',xivo_ast_fm_user_outcallerid);

var xivo_ast_fm_user_voicemail = {
	'it-voicemail-fullname':
		{property: [{disabled: false, className: 'it-enabled'},
			    {disabled: true, className: 'it-disabled'}],
		 link: 'it-voicemail-mailbox'},
	'it-voicemail-mailbox':
		{property: [{disabled: false, className: 'it-enabled'},
			    {disabled: true, className: 'it-disabled'}],
		 link: 'it-voicemail-password'},
	'it-voicemail-password':
		{property: [{disabled: false, className: 'it-enabled'},
			    {disabled: true, className: 'it-disabled'}],
		 link: 'it-voicemail-email'},
	'it-voicemail-email':
		{property: [{disabled: false, className: 'it-enabled'},
			    {disabled: true, className: 'it-disabled'}],
		 link: 'it-voicemail-tz'},
	'it-voicemail-tz':
		{property: [{disabled: false, className: 'it-enabled'},
			    {disabled: true, className: 'it-disabled'}],
		 link: 'it-voicemailfeatures-skipcheckpass'},
	'it-voicemailfeatures-skipcheckpass':
		{property: [{disabled: false, className: 'it-enabled'},
			    {disabled: true, className: 'it-disabled'}],
		 link: 'it-voicemail-attach'},
	'it-voicemail-attach':
		{property: [{disabled: false, className: 'it-enabled'},
			    {disabled: true, className: 'it-disabled'}],
		 link: 'it-voicemail-deletevoicemail'},
	'it-voicemail-deletevoicemail':
		{property: [{disabled: false, className: 'it-enabled'},
			    {disabled: true, className: 'it-disabled'}]}
};

xivo_attrib_register('ast_fm_user_voicemail',xivo_ast_fm_user_voicemail);

var xivo_ast_fm_user_enablevoicemail = dwho_clone(xivo_ast_fm_user_voicemail);
xivo_ast_fm_user_enablevoicemail['it-userfeatures-enablevoicemail'] = {property: [{checked: true},{checked: false}]};

xivo_attrib_register('ast_fm_user_enablevoicemail',xivo_ast_fm_user_enablevoicemail);

var xivo_ast_fm_cpy_user_name = {'userfeatures-callerid': false, 'voicemail-fullname': false};

function xivo_ast_user_cpy_name()
{
	if(dwho_eid('it-userfeatures-firstname') === false
	|| dwho_eid('it-userfeatures-lastname') === false
	|| dwho_eid('it-userfeatures-callerid') === false)
		return(false);

	var name = '';
	var firstname = dwho_eid('it-userfeatures-firstname').value;
	var lastname = dwho_eid('it-userfeatures-lastname').value;

	if(dwho_is_undef(firstname) === false && firstname.length > 0)
		name += firstname;

	if(dwho_is_undef(lastname) === false && lastname.length > 0)
		name += name.length === 0 ? lastname : ' '+lastname;

	var callerid = dwho_eid('it-userfeatures-callerid').value;

	if(dwho_is_undef(callerid) === true || callerid.length === 0)
		callerid = '';
	else
		callerid = callerid.replace(/^(?:"(.+)"|([^"]+))\s*<[^<]*>$/,'\$1');

	if(callerid.length === 0 || callerid === name)
		xivo_ast_fm_cpy_user_name['userfeatures-callerid'] = true;
	else
		xivo_ast_fm_cpy_user_name['userfeatures-callerid'] = false;

	if(dwho_eid('it-voicemail-fullname') === false)
		return(false);

	var fullname = dwho_eid('it-voicemail-fullname').value;

	if(dwho_is_undef(fullname) === true || fullname === name || fullname.length === 0)
		xivo_ast_fm_cpy_user_name['voicemail-fullname'] = true;
	else
		xivo_ast_fm_cpy_user_name['voicemail-fullname'] = false;
}

function xivo_ast_user_chg_name()
{
	if(xivo_ast_fm_cpy_user_name['userfeatures-callerid'] === false
	&& xivo_ast_fm_cpy_user_name['voicemail-fullname'] === false)
		return(false);

	var name = '';
	var firstname = dwho_eid('it-userfeatures-firstname').value;
	var lastname = dwho_eid('it-userfeatures-lastname').value;

	if(dwho_is_undef(firstname) === false && firstname.length > 0)
		name += firstname;

	if(dwho_is_undef(lastname) === false && lastname.length > 0)
		name += name.length === 0 ? lastname : ' '+lastname;

	if(xivo_ast_fm_cpy_user_name['userfeatures-callerid'] === true)
		dwho_eid('it-userfeatures-callerid').value = name;

	if(xivo_ast_fm_cpy_user_name['voicemail-fullname'] === true)
		dwho_eid('it-voicemail-fullname').value = name;

	return(true);
}

function xivo_ast_user_chg_enableclient()
{
	if((enableclient = dwho_eid('it-userfeatures-enableclient')) !== false)
		xivo_chg_attrib('ast_fm_user_enableclient',
				Number(enableclient.checked));
}

function xivo_ast_user_chg_enablerna()
{
	if((enablerna = dwho_eid('it-userfeatures-enablerna')) !== false)
		xivo_chg_attrib('ast_fm_user_enablerna',
				'it-userfeatures-destrna',
				Number(enablerna.checked));
}

function xivo_ast_user_chg_enablebusy()
{
	if((enablebusy = dwho_eid('it-userfeatures-enablebusy')) !== false)
		xivo_chg_attrib('ast_fm_user_enablebusy',
				'it-userfeatures-destbusy',
				Number(enablebusy.checked));
}

function xivo_ast_user_chg_enableunc()
{
	if((enableunc = dwho_eid('it-userfeatures-enableunc')) !== false)
		xivo_chg_attrib('ast_fm_user_enableunc',
				'it-userfeatures-destunc',
				Number(enableunc.checked));
}

function xivo_ast_user_ingroup()
{
	dwho.form.move_selected('it-grouplist','it-group');

	if((grouplist = dwho_eid('it-group')) === false || (len = grouplist.length) < 1)
		return(false);

	for(i = 0;i < len;i++)
	{
		if((group = dwho_eid('group-'+grouplist[i].value)) !== false)
			group.style.display = 'table-row';
	}

	if(dwho_eid('it-group').length > 0)
		dwho_eid('no-group').style.display = 'none';

	return(true);
}

function xivo_ast_user_outgroup()
{
	dwho.form.move_selected('it-group','it-grouplist');

	if((grouplist = dwho_eid('it-grouplist')) === false || (len = grouplist.length) < 1)
		return(false);

	for(i = 0;i < len;i++)
	{
		if((group = dwho_eid('group-'+grouplist[i].value)) !== false)
			group.style.display = 'none';
	}

	if(dwho_eid('it-group').length === 0)
		dwho_eid('no-group').style.display = 'table-row';

	return(true);
}

function xivo_ast_user_http_search_voicemail(dwsptr)
{
	new dwho.http('/service/ipbx/ui.php/pbx_settings/users/voicemail/search/?' + dwho_sess_str,
		      {'callbackcomplete':	function(xhr) { dwsptr.set(xhr,dwsptr.get_search_value()); },
		       'method':		'post',
		       'cache':			false},
		      {'search':	dwsptr.get_search_value()},
		      true);
}

var xivo_ast_user_suggest_voicemail = new dwho.suggest({'requestor': xivo_ast_user_http_search_voicemail});

function xivo_ast_user_voicemail_reset_search()
{
	dwho.form.reset_field(dwho_eid('it-userfeatures-voicemailid'),true);

	for(property in xivo_ast_fm_user_voicemail)
		dwho.form.reset_field(dwho_eid(property),true);

	xivo_chg_attrib('ast_fm_user_enablevoicemail',
			'it-voicemail-fullname',
			0);
}

function xivo_ast_user_chg_voicemail(option)
{
	xivo_chg_attrib('ast_fm_user_voicemailoption',
			'fd-voicemail-suggest',
			Number(option === 'search'));

	switch(option)
	{
		case 'add':
			if((voicemail_option = dwho_eid('it-voicemail-option')) !== false)
				reset_field_empty = voicemail_option.defaultValue !== option;
			else
				reset_field_empty = true;

			for(property in xivo_ast_fm_user_voicemail)
				dwho.form.reset_field(dwho_eid(property),reset_field_empty);

			xivo_chg_attrib('ast_fm_user_enablevoicemail',
					'it-voicemail-fullname',
					0);

			if(dwho_eid('it-userfeatures-firstname') === false
			|| dwho_eid('it-userfeatures-lastname') === false
			|| dwho_eid('it-voicemail-fullname') === false)
				break;
		
			$('#it-userfeatures-enablevoicemail').removeAttr('disabled');

			var name = '';
			var firstname = dwho_eid('it-userfeatures-firstname').value;
			var lastname = dwho_eid('it-userfeatures-lastname').value;

			if(dwho_has_len(firstname) === true)
				name += firstname;

			if(dwho_has_len(lastname) === true)
				name += name.length === 0 ? lastname : ' '+lastname;

			dwho_eid('it-voicemail-fullname').value = name;
			break;
		case 'search':
			dwho_eid('it-voicemail-suggest').value = '';
			xivo_ast_user_voicemail_reset_search();
			break;
		case 'exchange':
			dwho.form.reset_field(dwho_eid('it-userfeatures-voicemailid'),false);
		
			$('#it-userfeatures-enablevoicemail').removeAttr('disabled');
			
			for(property in xivo_ast_fm_user_enablevoicemail)
			  dwho.form.reset_field(dwho_eid(property),false);
			
			xivo_chg_attrib('ast_fm_user_enablevoicemail', 'it-voicemail-fullname', 1);
			xivo_chg_attrib('ast_fm_user_enablevoicemail', 'it-userfeatures-enablevoicemail', 0);
			break;
		case 'none':
		default:
			dwho.form.reset_field(dwho_eid('it-userfeatures-voicemailid'),false);
		
			$('#it-userfeatures-enablevoicemail').attr('disabled','disabled');

			for(property in xivo_ast_fm_user_enablevoicemail)
				dwho.form.reset_field(dwho_eid(property),false);

			xivo_chg_attrib('ast_fm_user_enablevoicemail',
					'it-voicemail-fullname',
					Number((option === 'none'
					        || dwho_eid('it-userfeatures-voicemailid').value === '')));
	}
}

function xivo_ast_user_chg_voicemailtype(type)
{
  xivo_chg_attrib('ast_fm_user_voicemailtype',
    'it-userfeatures-voicemailid',
    Number(type === 'asterisk'));

  switch(type)
  {
    case 'asterisk':
      return(xivo_ast_user_chg_voicemail(dwho_eid('it-voicemail-option').value));

    case 'exchange':
      return(xivo_ast_user_chg_voicemail('m$exchangeserver2010'));

		default:
      return(xivo_ast_user_chg_voicemail('none'));
  }
}

function xivo_ast_user_http_get_voicemail(obj)
{
	if(dwho_is_object(obj) === false
	|| dwho_has_len(obj.value) === false)
	{
		xivo_chg_attrib('ast_fm_user_voicemailoption',
				'fd-voicemail-suggest',
				1);

		return(xivo_ast_user_voicemail_reset_search());
	}

	new dwho.http('/service/ipbx/ui.php/pbx_settings/users/voicemail/view/?' + dwho_sess_str,
		      {'callbackcomplete':	function(xhr) { xivo_ast_user_voicemail_set_info(xhr); },
		       'method':		'post',
		       'cache':			false},
		      {'id':		obj.value},
		       true);

	return(true);
}

function xivo_ast_user_suggest_event_voicemail()
{
	xivo_ast_user_suggest_voicemail.set_option(
		'result_field',
		'it-userfeatures-voicemailid');
	xivo_ast_user_suggest_voicemail.set_option(
		'result_onsetfield',
		xivo_ast_user_http_get_voicemail);

	xivo_ast_user_suggest_voicemail.set_field(this.id);
}

function xivo_ast_user_voicemail_set_info(request)
{
	if(dwho_has_len(request.responseText) === false)
		return(null);

	obj = eval('(' + request.responseText + ')');

	if(dwho_is_object(obj.voicemail) === false)
		return(false);

	dwho_eid('it-voicemail-fullname').value			= obj['voicemail']['fullname'];
	dwho_eid('it-voicemail-mailbox').value			= obj['voicemail']['mailbox'];
	dwho_eid('it-voicemail-password').value			= obj['voicemail']['password'];
	dwho_eid('it-voicemail-email').value			= obj['voicemail']['email'];
	dwho_eid('it-voicemail-tz').value				= obj['voicemail']['tz'];
	dwho_eid('it-voicemailfeatures-skipcheckpass').checked	= dwho_bool(obj['voicemailfeatures']['skipcheckpass']);
	dwho_eid('it-voicemail-attach').value			= obj['voicemail']['attach'];
	dwho_eid('it-voicemail-deletevoicemail').checked	= dwho_bool(obj['voicemail']['deletevoicemail']);

	return(true);
}

function xivo_ast_user_onload()
{
	if((firstname = dwho_eid('it-userfeatures-firstname')) !== false)
	{
		dwho.dom.add_event('change',firstname,xivo_ast_user_cpy_name);
		dwho.dom.add_event('focus',firstname,xivo_ast_user_cpy_name);
		dwho.dom.add_event('blur',firstname,xivo_ast_user_chg_name);
	}
	
	if((lastname = dwho_eid('it-userfeatures-lastname')) !== false)
	{
		dwho.dom.add_event('change',lastname,xivo_ast_user_chg_name);
		dwho.dom.add_event('focus',lastname,xivo_ast_user_cpy_name);
		dwho.dom.add_event('blur',lastname,xivo_ast_user_chg_name);
	}

	if((voicemailtype = dwho_eid('it-userfeatures-voicemailtype')) !== false)
	{
		var voicemailtype_fn = function() {
			xivo_ast_user_chg_voicemailtype(voicemailtype.value);
		};
				 
	    xivo_ast_user_chg_voicemailtype(voicemailtype.value);

	    dwho.dom.add_event('change',voicemailtype,voicemailtype_fn);
	}

	if((voicemailoption = dwho_eid('it-voicemail-option')) !== false)
	{
		dwho_eid('it-voicemail-suggest').setAttribute('autocomplete','off');

		dwho.dom.add_event('focus',
				   dwho_eid('it-voicemail-suggest'),
				   xivo_ast_user_suggest_event_voicemail);

		var voicemailoption_fn = function()
					 {
					 	xivo_ast_user_chg_voicemail(voicemailoption.value);
					 };

		dwho.dom.add_event('change',voicemailoption,voicemailoption_fn);
	}

	if((outcallerid_type = dwho_eid('it-userfeatures-outcallerid-type')) !== false)
	{
		var outcallerid_type_fn = function()
					  {
						xivo_chg_attrib('ast_fm_user_outcallerid',
								'fd-userfeatures-outcallerid-custom',
								Number(outcallerid_type.value === 'custom'));
					  };

		outcallerid_type_fn();

		dwho.dom.add_event('change',outcallerid_type,outcallerid_type_fn);
	}

	dwho.dom.add_event('change',
			   dwho_eid('it-userfeatures-enableclient'),
			   xivo_ast_user_chg_enableclient);

	dwho.dom.add_event('change',
			   dwho_eid('it-userfeatures-enablerna'),
			   xivo_ast_user_chg_enablerna);

	dwho.dom.add_event('change',
			   dwho_eid('it-userfeatures-enablebusy'),
			   xivo_ast_user_chg_enablebusy);

	dwho.dom.add_event('change',
			   dwho_eid('it-userfeatures-enableunc'),
			   xivo_ast_user_chg_enableunc);


	xivo_ast_build_dialaction_array('noanswer');
	xivo_ast_build_dialaction_array('busy');
	xivo_ast_build_dialaction_array('congestion');
	xivo_ast_build_dialaction_array('chanunavail');

	xivo_ast_dialaction_onload();
}

dwho.dom.set_onload(xivo_ast_user_onload);
