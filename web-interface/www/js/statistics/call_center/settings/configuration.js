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

$(function() {

	$.localise('ui-multiselect', {
		language : dwho_i18n_lang,
		path : '/extra-libs/multiselect/js/locale/'
	});

	$('.multiselect').multiselect({
		onUpdate : function() {
			populateqos('it-queue', 'queue');
			populateqos('it-group', 'group');
		}
	});
	$('#it-stats_conf-hour_start').timepicker({});
	$('#it-stats_conf-hour_end').timepicker({});
});

function populateqos(selectid, type) {
	var input = '';
	input += '<fieldset>';
	input += '<legend>' + translation[type] + '</legend>';
	nb = $('#' + selectid + ' option:selected')
			.each(
					function() {

						var val = $(this).val();
						var text = $(this).text();
						var it_qos_obj = $('#it-' + type + '_qos-' + val);

						if (it_qos_obj.val() === undefined) {
							if (val in listqos)
								qos = listqos[val];
							else
								qos = 0;
						} else
							qos = it_qos_obj.val();

						input += '<p id="fd-qos" class="fm-paragraph">';
						input += '<span class="fm-desc clearboth"><label id="lb-qos" for="it-qos">'
								+ text + ':</label></span>';
						input += '<input type="text" id="it-' + type + '_qos-'
								+ val + '" name="' + type + '_qos[' + val
								+ ']" value="' + qos + '" size="5" /> s';
						input += '</p>';
					}).length;
	input += '</fieldset>';

	if (nb > 0)
		$('#it-list' + type + 'qos').html(input);
	else
		$('#it-list' + type + 'qos').html('');
}
