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

function dyntable(name) {

	var name 		= name;
	var count_row 	= 0;
	
    this.__init 	= __init;
    this.addrow 	= addrow;
    this.delrow 	= delrow;
    this.update 	= update;
    
    function __init() {
    	$('#list_'+name).find('a:#lnk-add-row').click(addrow);
    	$('#list_'+name).find('#lnk-del-row').click(delrow);
    	$('#list_'+name+' > tbody').sortable({
    		helper: fixHelper,
    		cursor: 'crosshair',
    		update: update
    	});
		update();
    }
	
	function addrow() {
		$(this).parents('table').find('tbody:last').
		fadeIn(400, function() {
	        $(this).append( $('#ex-row').html() );
	        $(this).find('#lnk-del-row').click(delrow);
	    });
		update();
	}

	function delrow() {
	    $(this).parents('tr').
	    fadeTo(400, 0, function() {
	        $(this).remove();
	    });
	    setTimeout(update, 420);
	}
    
    function update() {
    	count_row = 0;
    	$('#list_'+name).find('tbody > tr').
		each(function() {
			count_row++;
			$(this).find('#box-order').text(count_row);
		});

		if (count_row > 0)
			$('#no-row').hide('fast');
		else
			$('#no-row').show('fast');
	}

	__init();
}
