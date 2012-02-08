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



function update_host() {
	var fd_protocol_host_static = $('#fd-protocol-host-static');
	var it_protocol_host_type = $('#it-protocol-host-type');

	fd_protocol_host_static.css('display', 'none');

	if (it_protocol_host_type.val() == 'static') {
		fd_protocol_host_static.css('display', 'block');
	}
}

$(function() {
	update_host();
	$('#it-protocol-host-type').change(update_host);
});