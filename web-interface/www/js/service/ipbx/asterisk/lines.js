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

// Return a helper with preserved width of cells
var fixHelper = function(e, ui) {
	ui.children().each(function() {
		$(this).width($(this).width());
	});
	return ui;
};

function map_autocomplete_extension_to(obj,context)
{    
    $(obj).autocomplete(url_http_search_extension, {
    	width: 70, 
    	extraParams: {
    		context: context,
    		obj: 'user',
    		format: 'jquery'
    	}
    });
}

function update_rules_group_val()
{
	var groupval = '';
	var count = 0;
	$('#list_linefeatures > tbody').find('tr').each(function() {				
		if($(this).attr('id') == 'tr-rules_group') {	
			count = 0;
			groupval = $(this).find('#td_rules_group_name').text();
		}
		count++;
		$(this).find('#linefeatures-rules_group').val(groupval);			
		$(this).find('#linefeatures-rules_order').val(count-1);
	});
}

$(document).ready(function(){ 
	/*
	$(".up,.down").click(function(){
        var row = $(this).parents("tr:first");
        if ($(this).is(".up")) {
            row.insertBefore(row.prev());
        } else {
            row.insertAfter(row.next());
        }
    });
	*/

	$("#list_linefeatures tbody").sortable({
		helper: fixHelper,
		cursor: 'crosshair',
		update: update_rules_group_val
	}).disableSelection();
	
	$('#lnk-add-row').click(function(){
		
		$('#no-linefeatures').hide('fast');
	    row = $('#ex-linefeatures').html();
	    
		$('#list_linefeatures > tbody:last').fadeIn(400, function () {
	        $(this).append(row);
	    });
		
		context = $('#list_linefeatures > tbody:last > tr').find("#linefeatures-context");

		$('#it-userfeatures-entityid').attr('disabled','disabled');
		$('#it-userfeatures-entityid').addClass('it-disabled');
		context.change(function(){
		    number = $(this).parents('tr').find('#linefeatures-number');		    
		    map_autocomplete_extension_to(number,$(this).val());
		});

	    update_rules_group_val();
		return false;
	});

	$('#lnk-add-row-rules_group').click(function(){
		
		groupval = $('#it-rules_group').val();
		
		if (groupval === '' || groupval === null)
			return false;
		
		exist = false;
		$('#list_linefeatures').find('#td_rules_group_name').each(function () {
			if ($(this).text() == groupval)
				exist = true;
		});
		
		if (exist === true)
			return false;

		groupval = groupval.replace(/[^a-z0-9_\.-]+/g,'');
		groupval = groupval.toLowerCase();
		
		td_rules_group = $('#ex-rules_group').find('#td_rules_group_name');
	    td_rules_group.text(groupval);
		
		row = $('#ex-rules_group').html();
		
	    $('#list_linefeatures > tbody:last').fadeIn(400, function () {
	        $(this).append(row);
	    });
	    
	    td_rules_group.text('');
	    update_rules_group_val();
	
		return false;
	});

	$('#lnk-add-row-line_free').click(function(){
		
		$('#no-linefeatures').hide('fast');
	    
	    idlinefeatures = $('#list_lines_free').val();
	    $('#ex-linefeatures').find('#linefeatures-id').val(idlinefeatures);        
	    row = $('#ex-linefeatures').html();
		
	    $('#list_linefeatures > tbody:last').fadeIn(400, function () {
	        $(this).append(row);
	    });

		$('#it-userfeatures-entityid').attr('disabled','disabled');
		$('#it-userfeatures-entityid').addClass('it-disabled');

	    $('#ex-linefeatures').find('#linefeatures-id').val(0);
		
		it_context = $('#list_linefeatures > tbody:last > tr').find("#linefeatures-context");		
	    it_number = it_context.parents('tr:last').find('#linefeatures-number');  
	    
	    td_protocol = it_context.parents('tr:last').find('#td_ex-linefeatures-protocol');
	    td_name = it_context.parents('tr:last').find('#td_ex-linefeatures-name');	    	  

	    it_context.parents('tr:last').find('#linefeatures-protocol').remove();
	    it_context.parents('tr:last').find('#linefeatures-name').remove();

	    protoname = $('#list_lines_free option[value='+idlinefeatures+']').text();
	    
	    if (protoname.indexOf('/') == -1) {
		    td_protocol.append( 'error: undefined protoco' );
			td_name.append( 'error: undefined peer' );
	    }
	    else {
		    str_protocol = protoname.substring(0, protoname.indexOf('/')).toLowerCase();
		    str_name = protoname.substring(protoname.indexOf('/')+1);
		    
		    td_protocol.append( str_protocol.toUpperCase() );
			it_proto = '<input type="hidden" id="linefeatures-protocol" name="linefeatures[protocol][]" value="'+str_protocol+'" />';
		    td_protocol.append( it_proto );
		    
		    td_name.append( str_name );
			it_name = '<input type="hidden" id="linefeatures-name" name="linefeatures[name][]" value="'+str_name+'" />';
			td_name.append( it_name );
	    }
	    
	    $('#list_lines_free option[value='+idlinefeatures+']').remove();
	    
	    if ($('#list_lines_free option').length == 0)
	    	$('#box-lines_free').hide('slow');
	    
	    map_autocomplete_extension_to(it_number,it_context.val());
		
	    it_context.change(function(){
		    number = $(this).parents('tr').find('#linefeatures-number');
		    map_autocomplete_extension_to(number,$(this).val());
		});
	    update_rules_group_val();
		
		return false;
	});
	
});

function lnkdroprow(obj) {
	
    $(obj).parents('tr').fadeTo(400, 0, function () {
        $(this).remove();
    });
    
    setTimeout(update_rules_group_val, 420);
    
	nb_row = $('#list_linefeatures > tbody > tr').length;
	if (nb_row == 1) {
		$('#it-userfeatures-entityid').removeAttr('disabled');
		$('#it-userfeatures-entityid').removeClass('it-disabled');
	}
	
    it_id = $(obj).parents('tr').find('#linefeatures-id');
	
	if (it_id.val() == 0)
		return false;
    
    td_protocol = $(obj).parents('tr').find('#td_ex-linefeatures-protocol');
    td_name = $(obj).parents('tr').find('#td_ex-linefeatures-name');
    
	$('#list_lines_free').append("<option value=" + it_id.val() + ">" + td_protocol.text()+'/'+td_name.text() + "</option>");
	
    if ($('#list_lines_free option').length > 0)
    	$('#box-lines_free').show();
    
    return false;
}
