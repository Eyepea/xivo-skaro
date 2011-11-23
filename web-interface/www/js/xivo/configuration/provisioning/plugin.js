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

$(function() {
	mt = ($('#tb-list-pkgs').height() / 2)
			- ($('#box_installer').find('div').height() / 2);
	$('#box_installer').css('height', $('#tb-list-pkgs').height() + 'px');
	$('#box_installer').css('width', $('#tb-list-pkgs').width() + 'px');
	$('#box_installer').find('div').css('margin-top', mt + 'px');
	$('#box_installer').hide();

	$('input[id="configure-ajax"]').each(
			function() {
				$(this).keyup(
						function() {
							name = $(this).attr('name');
							val = $(this).val();
							href = $('#href-' + name).val();
							uri = $('#uri-' + name).val();
							act = $('#act-' + name).val();
							delay(function() {
								$.post(uri, {
									act : act,
									uri : href,
									value : val
								}, function(data) {
									$('#res-' + name).show().html(data).delay(
											1500).hide('slow');
								});
							}, 900);
						});
			});

});

function init_install_pkgs(plugin, id) {
	var url = '/xivo/configuration/ui.php/provisioning/plugin?act=install-pkgs&plugin='+ plugin + '&id=' + id;
	init_installer(url, plugin);
}

function init_install_plugin(id) {
	var url = '/xivo/configuration/ui.php/provisioning/plugin?act=install_plugin&id=' + id;
	init_installer(url, id);
}

function init_update_plugin() {
	var url = '/xivo/configuration/ui.php/provisioning/plugin?act=update_plugin';
	init_installer(url, null);
}

function init_installer(url, id) {
	$('#box_installer').show();
	$.get(url, function(data) {
				if (data === null)
					return false;
				ajax_request_oip(data, id);
				this.int = setInterval(ajax_request_oip, 1000, data, id);
			});
}

function ajax_request_oip(url, plugin) {
	if (plugin == null) {
		uri = '/xivo/configuration/ui.php/provisioning/plugin?act=request_oip&path=' + url;
	} else {
		uri = '/xivo/configuration/ui.php/provisioning/plugin?act=request_oip&id=' + plugin + '&path=' + url;
	}
	$.get(uri, function(data) {
		var str = data.split('::');
		var box = $('#box_installer').find('div');
		if (str[0] == 'redirecturi') {
			box.hide();
			top.location.href = str[1];
		}
		box.html(data);
	});
}