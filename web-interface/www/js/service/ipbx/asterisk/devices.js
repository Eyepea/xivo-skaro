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

function update_sip_srtp_mode() {
	var it_sipsrtpmode_val = $('#it-config-sip_srtp_mode').val();
	var it_siptrans = $('#it-config-sip_transport');

	it_siptrans.attr('disabled', 'disabled');
	it_siptrans.addClass('it-disabled');

	if (it_sipsrtpmode_val == 'preferred' || it_sipsrtpmode_val == 'required') {
		it_siptrans.removeAttr('disabled');
		it_siptrans.removeClass('it-disabled');
	}
}

$(document).ready(function() {
	update_sip_srtp_mode();
	$('#it-config-sip_srtp_mode').change(update_sip_srtp_mode);
});
