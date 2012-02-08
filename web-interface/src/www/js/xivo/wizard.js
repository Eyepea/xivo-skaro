/*
 * XiVO Web-Interface
 * Copyright (C) 2006-2011  Avencall
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


function xivo_wizard_ipbximportuser_error(sum) {
	var spansum = dwho.dom.create_element('span', {
		'id' : 'ipbximportuser-tooltips-error',
		'className' : 'fm-txt-error'
	}, sum);

	dwho.dom.create_focus_caption(dwho_eid('tooltips'),
			dwho_eid('ipbximportuser-lines-status'), spansum, 'center');
}

function xivo_wizard_chg_entity_name() {
	if (dwho_eid('it-entity-name') === false
			|| dwho_eid('it-entity-displayname') === false)
		return (false);

	var name = '';
	var displayname = dwho_eid('it-entity-displayname').value;

	if (dwho_is_undef(displayname) === false && displayname.length > 0)
		name = displayname;

	name = name.toLowerCase();
	name = name.replace(/[^a-z0-9_\.-]+/g, '');

	dwho_eid('it-entity-name').value = name;
}

function xivo_wizard_dbconfig_backend_onload() {
	dwho.dom.add_event('change', dwho_eid('it-language'), function() {
		this.form['refresh'].value = 1;
		this.form.submit();
	});
	
	xivo_wizard_chg_entity_name();

	dwho.dom.add_event('change', dwho_eid('it-entity-displayname'),
			xivo_wizard_chg_entity_name);
	
	dwho.dom.add_event('click', dwho_eid('it-previous'), function() {
		this.type = 'submit';
	});
}

dwho.dom.set_onload(xivo_wizard_dbconfig_backend_onload);


var apply_wizard = {

	counter : new Number(1),
	next : '',
	lang : 'en',

	init : function(lang) {
		$('#box_installer').show();
		apply_wizard.lang = lang;
		apply_wizard.request_post(undefined,false,lang);
	},

	request_post : function(step,async,lang) {
		if (async === undefined)
			async = false;
		var me = apply_wizard;
		$.ajax({
			type: 'GET',
			url : '/xivo/wizard/ui.php/wizard?step=' + step + '&hl=' + lang,
			async : async,
			success: function(data) {
				var str = data.split('::');
				if (str.length < 2) {
					me.populate_infos('fatal error',true);
				} else if (str[0] == 'next') {
					me.next = str[1];
					me.populate_infos(str[2]);
				} else if (str[0] == 'uri') {
					me.populate_infos(str[2], true);
					me.send_redirect(str[1]);
				} else if (str[0] == 'nexturi') {
					me.next = str[1];
					me.populate_infos(str[3],'async');
					me.send_redirect(str[2]);
				} else if (str[0] == 'redirecturi') {
					me.next = str[1];
					me.populate_infos('',true);
					me.send_redirect(str[2],str[3]);
				} else if (str[0] == 'redirecturi_on_success') {
					me.send_redirect(str[1]);
				} else {
					me.populate_infos('fatal error',true);
				}
			}
		});
		me.counter++;
	},

	populate_infos : function(msg, last) {
		$('#box_installer').find('div').append(msg + '<br>');
		if (last === 'async')
			apply_wizard.request_post(apply_wizard.next,true,apply_wizard.lang);
		else if (last === undefined)
			apply_wizard.request_post(apply_wizard.next,false,apply_wizard.lang);
	},

	send_redirect : function(url,timeredirect) {
		if (timeredirect == undefined) {
			window.location = url;
		} else {
			window.setTimeout(function() {
				window.location = url;
			}, timeredirect);
		}
	}
};

$(function() {
	$('input[name="validate"]').click(function() {
		apply_wizard.init(dwho_i18n_lang);
		return false;
	});
});
