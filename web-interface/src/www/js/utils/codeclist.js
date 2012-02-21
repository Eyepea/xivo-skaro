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

function update_codeclist() {
	var it_protocol_disallow = $('#it-protocol-disallow');
	var it_protocol_allow = $('#it-protocol-allow');
	var codeclist = $('#codeclist');

	xivo_fm_disabled(it_protocol_disallow);
	xivo_fm_disabled(it_protocol_allow);
	codeclist.css('display', 'none');

	var it_codec_active_val = $('#it-codec-active').attr('checked');

	if (it_codec_active_val) {
		xivo_fm_enabled(it_protocol_disallow);
		xivo_fm_enabled(it_protocol_allow);
		codeclist.css('display', 'block');
	}
}

$(function() {
	var codeclist = $('#codeclist');
	var cnt = 0;
	codeclist.find('option:selected').each(function(i, selected) {
		cnt++;
	});

	if (cnt > 1) {
		$('#it-codec-active').attr('checked', 'checked');
	} else {
		$('#it-codec-active').removeAttr('checked');
	}
	update_codeclist();
	$('#it-codec-active').change(update_codeclist);
});
