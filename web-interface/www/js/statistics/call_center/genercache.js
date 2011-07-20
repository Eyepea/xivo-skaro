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

    $('#it-conf-type').change(function(){
        $(this).parents('form').submit();
    });
    
});

function xivo_genercache() {
    
    var total = listmonthtimestamp.length;
    var counter = 0;
    var start = (new Date).getTime();
    var start2 = (new Date).getTime();
    var avg = new Array();

    this.init = init;
    this.make = make;

    function init(idtype) {        
        $('#it-cache-success-all').hide();        
        if (idtype == 'all') {
            $('#it-cache-generation-all').show();
            $('#t-list-obj').hide();
        } else {
            $('#it-cache-generation-'+idtype).show();
        }
    }
    
    function make(idtype,data) {
        var pct = ( (counter / total) * 100);
        
        if (counter >= total)
            return on_success(idtype);
    
        if (!listmonthtimestamp[counter])
            return;
        
        var date = listmonthtimestamp[counter].split('-');
        var year = date[0];
        var day = date[2];
        var month = date[1];
        var humandate = year + '-' + month;// + '-' + day;
        var diff = (new Date).getTime() - start;
        var diff2 = (new Date).getTime() - start2;
        
        avg.push(diff2);
        
        var objectProcessing = (idtype == 'all') ? jstxt_object_all : idtype;
        var remaining_time = Math.round((average(avg) * (total - counter)) / 1000);
        
        infos = '';
        infos += '<p>';
        infos += '<b>' + humandate + '</b> ' + jstxt_in_progress;
        infos += '........... ';
        infos += jstxt_process_last_time_traitment + ' ' + Math.round(diff2 / 1000) + 's';
        infos += '</p>';
        infos += jstxt_process_total_time + ' ' + Math.round(diff / 1000) + 's';
        infos += '<br>';
        infos += jstxt_process_remaining_time + ' ' + remaining_time + 's';
        
        if (idtype == 'all') {
            $('#reshttprequest-all').html(nl2br(data));
            $('#rescacheinfos-all').html(infos);
            //$('#restitle-all').html(object_processing + ' ' + objectProcessing);
            $(function() {$('#resprogressbar-all').progressbar({value: pct});});
        } else {
            $('#reshttprequest-'+idtype).html(nl2br(data));
            $('#cache-infos-'+idtype).css('display', 'table-row');
            $('#gcache-'+idtype).html(jstxt_bt_wait_submit);
            //$('#bt-gcache-'+idtype).attr('disabled','disabled');
            //$('#bt-gcache-'+idtype).val(jstxt_bt_wait_submit);
            $('#rescacheinfos-'+idtype).html(infos);
            //$('#restitle-'+idtyp).html(object_processing + ' ' + objectProcessing);
            $(function() {$('#resprogressbar-'+idtype).progressbar({value: pct});});
        }
    
        request_post(jsvar_idconf,listmonthfirstday[counter],listmonthlastday[counter],jsvar_type,idtype);
    
        start2 = (new Date).getTime();
    }

    function request_post(idconf,dbeg,dend,type,idtype) {
        $.ajax({
              type: 'POST',
              url: '/statistics/ui.php/call_center/genercache/',
              data: {
                  'idconf': idconf,
                  'dbeg': dbeg,
                  'dend': dend,
                  'type': type,
                  'idtype': idtype
              },
              success: function(data) {
                  make(idtype,data);
              },
              dataType: 'html'
        });
        counter++;
    }
    
    function on_success(idtype) {
        if (idtype == 'all') {
           var nb = listkeyfile.length;
           var sum = 0;
           for (var i = 0; i < nb;i++) {
              keyfile = listkeyfile[i];
              $('#gcache-'+keyfile).html(jstxt_img_success_submit);
              //$('#bt-gcache-'+keyfile).attr('disabled','disabled');
              //$('#bt-gcache-'+keyfile).val(jstxt_bt_success_submit);
           }
            
           $('#gcache-all').html(jstxt_img_success_submit);
           //$('#bt-gcache-all').attr('disabled','disabled');
           //$('#bt-gcache-all').val(jstxt_bt_success_submit);
           $('#it-cache-generation-all').hide();
           $('#it-cache-success-all').show();
           $('#t-list-obj').show();
           $('#t-list-obj').css('width','100%');
        } else {
            $('#gcache-'+idtype).html(jstxt_img_success_submit);
            //$('#bt-gcache-'+idtype).val(jstxt_bt_success_submit);
            $('#it-cache-generation-'+idtype).hide();
            $('#it-cache-success-'+idtype).show();
            $('#cache-infos-'+idtype).hide();
        }
    }
    
}