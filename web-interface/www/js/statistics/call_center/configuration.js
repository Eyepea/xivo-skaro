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
		language: dwho_i18n_lang,
		path: '/extra-libs/multiselect/js/locale/'
	});
	
	$('.multiselect').multiselect();
    $('#it-stats_conf-hour_start').timepicker({});
    $('#it-stats_conf-hour_end').timepicker({});

	setInterval('populateqos(\'it-queue\',\'queue\')',1500);
	setInterval('populateqos(\'it-group\',\'group\')',1500);
	
});

function populateqos(selectid,type)
{
	var input = '';
	input += '<fieldset>';
	input += '<legend>'+translation[type]+'</legend>';
	nb = $('#'+selectid+' option:selected').each(function(){
		var val = $(this).val();
		var text = $(this).text();
		var qos = 0;
		if( val in listqos )
			qos = listqos[val];
		input += '<p id="fd-qos" class="fm-paragraph">';
		input += '<span class="fm-desc clearboth"><label id="lb-qos" for="it-qos">'+text+':</label></span>';
		input += '<input type="text" name="'+type+'_qos['+val+']" value="'+qos+'" size="5" />';
		input += '</p>';
	}).length;
	input += '</fieldset>';
	
	if (nb > 0)
		$('#it-list'+type+'qos').html(input);
	else
		$('#it-list'+type+'qos').html('');
}