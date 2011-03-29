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

//get available extensions
var url_http_search_extension = '/service/ipbx/ui.php/pbx_settings/extension/search/';

$(document).ready(function(){ 
	$('#lnk-add-row').click(function(){
		$('#no-linefeatures').hide('fast');
	    row = $('#ex-linefeatures').html();
		$('#list_linefeatures > tbody:last').fadeIn(400, function () {
	        $(this).append(row);
	    });
		context = $('#list_linefeatures > tbody:last > tr > td:nth-child(2)').find("select");
		
		$('#it-userfeatures-entityid').attr('disabled','disabled');
		
	/*
		//$(context).parent().parent().find('#linefeatures-number').val(context.val());
	    
		$(context).parent().parent().find('#linefeatures-number')
	    .autocomplete(url_http_search_extension, {
	    	width: 70, 
	    	extraParams: {
	    		context: $(this).val(),
	    		obj: 'user',
	    		format: 'jquery'
	    		//function() { return $(this).val(); }
	    	}
	    });
	 */
		
		context.change(function(){
		    var number = $(this).parent().parent().find('#linefeatures-number');
		    
		    $(number).autocomplete(url_http_search_extension, {
		    	width: 70, 
		    	extraParams: {
		    		context: $(this).val(),
		    		obj: 'user',
		    		format: 'jquery'
		    	}
		    }); 
		});
		return false;
	});

	$('#lnk-add-row-line_free').click(function(){
		$('#no-linefeatures').hide('fast');
	    row = $('#ex-linefeatures').html();
	    
	    idlinefeatures = $('#list_lines_free').val();
		input = '<input type="hidden" name="linefeatures[id][]" value="'+idlinefeatures+'" />';
	    
	    $('#list_lines_free option[value='+idlinefeatures+']').remove();
		
	    $('#list_linefeatures > tbody:last').fadeIn(400, function () {
	        row = $(this).append(row);
	        row.append(input);
	    });
		
		context = $('#list_linefeatures > tbody:last > tr > td:nth-child(2)').find("select");
		
		context.change(function(){
		    var number = $(this).parent().parent().find('#linefeatures-number');
		    
		    $(number).autocomplete(url_http_search_extension, {
		    	width: 70, 
		    	extraParams: {
		    		context: $(this).val(),
		    		obj: 'user',
		    		format: 'jquery'
		    	}
		    }); 
		});
		return false;
	});
});

function lnkdroprow(obj) {
    $(obj).parent().parent().fadeTo(400, 0, function () {
        $(this).remove();
    });
	nb_row = $('#list_linefeatures > tbody > tr').length;
	if (nb_row == 1)
		$('#it-userfeatures-entityid').removeAttr('disabled');
    return false;
}
