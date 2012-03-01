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

var xivo_fm_method = {
	'fd-address' : {
		'style' : [ {
			display : 'none'
		}, {
			display : 'block'
		} ],
		'link' : 'it-address'
	},
	'it-address' : {
		'property' : [ {
			disabled : true
		}, {
			disabled : false
		} ],
		'link' : 'fd-netmask'
	},
	'fd-netmask' : {
		'style' : [ {
			display : 'none'
		}, {
			display : 'block'
		} ],
		'link' : 'it-netmask'
	},
	'it-netmask' : {
		'property' : [ {
			disabled : true
		}, {
			disabled : false
		} ],
		'link' : 'fd-gateway'
	},
	'fd-gateway' : {
		'style' : [ {
			display : 'none'
		}, {
			display : 'block'
		} ],
		'link' : 'it-gateway'
	},
	'it-gateway' : {
		'property' : [ {
			disabled : true
		}, {
			disabled : false
		} ]
	}
};

xivo_attrib_register('fm_method', xivo_fm_method);

function xivo_network_chg_method() {
	if ((method = dwho_eid('it-method')) !== false)
		xivo_chg_attrib('fm_method', 'fd-address',
				Number(method.value === 'static'));
}

function xivo_network_onload() {
	xivo_network_chg_method();

	dwho.dom.add_event('change', dwho_eid('it-method'), xivo_network_chg_method);
}

dwho.dom.set_onload(xivo_network_onload);

function metwork_chk_type() {
	var it_networktype = $('#it-networktype');

	if (it_networktype.val() == 'voip') {
		$('#it-method').val('static');
		xivo_network_chg_method();
		xivo_fm_disabled($('#it-method'));
	} else {
		xivo_fm_enabled($('#it-method'));
	}
}

function metwork_chk_disable() {
	var it_disable = $('#it-disable');

	if (it_disable.attr('checked')) {
		$('#it-networktype').val('data');
		xivo_fm_disabled($('#it-networktype'));
		metwork_chk_type();
	} else {
		xivo_fm_enabled($('#it-networktype'));
		metwork_chk_type();
	}
}

$(function() {
	metwork_chk_type();
	metwork_chk_disable();
	$('#it-disable').change(metwork_chk_disable);
	$('#it-networktype').change(metwork_chk_type);
});
