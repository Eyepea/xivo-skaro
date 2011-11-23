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
 
function xivo_monitoring_get_all()
{
    $.post('/xivo/ui.php/monitoring/?' + dwho_sess_str, 
        {'bloc': 'monitoring'}, 
        function(data) {
            $('#monitoring').html(data);
    });
}

function xivo_monitoring_get_bloc(bloc)
{
    $.post('/xivo/ui.php/monitoring/?' + dwho_sess_str, 
        {'bloc': bloc}, 
        function(data) {
            $('#'+bloc).html(data);
    });
}

function init_action(service,action)
{
    //$('#box_infos').show();
    $.ajax({
        async: false,
        url: '/xivo/ui.php/monit/?' + dwho_sess_str+'&act=request&service='+service+'&action='+action,
        success: function(){
            $('#box_infos').hide();
        }
    });
}

$(function(){
    $('#box_infos').hide();
});