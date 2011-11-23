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

function data_iface_change()
{
	if($('#it-pf-ha-cluster_itf_data').val() == "") {
		$('#p_cluster_itf_master_ip').hide();
		$('#p_cluster_itf_slave_ip').hide();
	} else {
		$('#p_cluster_itf_master_ip').show();
		$('#p_cluster_itf_slave_ip').show();
	}
}

dwho.dom.set_onload(data_iface_change);
