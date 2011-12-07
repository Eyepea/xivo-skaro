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
	var it_sipsrtpmode = $('#it-config-sip_srtp_mode');
	var it_siptrans_val = $('#it-config-sip_transport').val();

	it_sipsrtpmode.attr('disabled', 'disabled');
	it_sipsrtpmode.addClass('it-disabled');

	if (it_siptrans_val == 'tls') {
		it_sipsrtpmode.removeAttr('disabled');
		it_sipsrtpmode.removeClass('it-disabled');
		it_sipsrtpmode.val('required');
	}
}

$().ready(function() {
	update_sip_srtp_mode();
	$('#it-config-sip_transport').change(update_sip_srtp_mode);
});
