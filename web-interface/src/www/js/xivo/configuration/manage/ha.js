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

function ha_chk_type() {
	var it_ha_type = $('#it-type');

	$('#fld-infos').hide();
	
	if (it_ha_type.val() == 'master') {
		$('#fld-infos').show();
		$('#fld-legend_slave').show();
		$('#fld-legend_master').hide();
	} else if (it_ha_type.val() == 'slave') {
		$('#fld-infos').show();
		$('#fld-legend_slave').hide();
		$('#fld-legend_master').show();
	}
}

$(function(){
	ha_chk_type();
	$('#it-type').change(ha_chk_type);
});