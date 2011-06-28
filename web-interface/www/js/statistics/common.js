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
    
    $.datepicker.setDefaults({
        currentText: 'Now',
        changeYear: true,
        firstDay: 1,
        selectOtherMonths: true,
        dayNamesMin: xivo_date_day_min,
        ayNamesShort: xivo_date_day_short,
        dayNames: xivo_date_day,
        monthNames: xivo_date_month,
        monthNamesShort: xivo_date_month_short,
        nextText: xivo_date_next,
        prevText: xivo_date_prev,
        showAnim: 'fold',
        showMonthAfterYear: true,
        showWeek: true,
        weekHeader: 'W',
        minDate: dp_min_date,
        maxDate: dp_max_date
    });

    $("#it-dbeg").datepicker({
        dateFormat: 'yy-mm-dd',
        altFormat: 'yy-mm-dd'
    });
    $("#it-dend").datepicker({
        dateFormat: 'yy-mm-dd',
        altFormat: 'yy-mm-dd'
    });
    $("#it-dday").datepicker({
        dateFormat: 'yy-mm-dd',
        altFormat: 'yy-mm-dd'
    });
    $("#it-dweek").datepicker({
        dateFormat: 'yy-mm-dd',
        altFormat: 'yy-mm-dd'
    });
    $("#it-dmonth").datepicker({
        dateFormat: 'yy-mm-dd',
        altFormat: 'yy-mm'
    });

    $('#it-axetype').change(function() {
        type = $(this).val();
           for(var u=0;u<lsaxetype.length;u++)
           {
               $('#it-cal-'+lsaxetype[u]).hide();
            if (lsaxetype[u] == 'type')
                $('#it-cal-object').hide();
           }
           $('#it-cal-'+type).show();
           if (type != 'type')
               $('#it-cal-object').show();
    });

    for(var u=0;u<lsaxetype.length;u++)    {
        if (lsaxetype[u] == axetype)
            $('#it-cal-'+lsaxetype[u]).show();
    }

    $('#it-confid').change(function(){
        $(this).parents('form').submit();
    });
            
});

function fm_chk() {
    $('#it-submit').attr('disabled', 'disabled');
    $('#it-submit').val(fm_bt_wait_sb);
    $('#it-loading').show();
};