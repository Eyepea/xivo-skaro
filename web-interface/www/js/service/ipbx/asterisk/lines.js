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


function map_autocomplete_line_free_to(obj,list,exept)
{
	$(obj).show();
	if (list === null || (nb = list.length) === 0)
		return false;
	if(!exept)
		exept = 0;
	$(obj).find('option').each(function(){
		if(exept != $(this).val()
		&& dwho_in_array($(this).val(),list))
			$(this).remove();
	});
}

//get available line for a device
function xivo_http_search_line_from_provd(obj,config,exept)
{
	if (config == ''){
		obj.hide();
		return;
	}
	$.ajax({
		url: '/xivo/configuration/ui.php/provisioning/config?act=getbydeviceid&id='+config,
		async: false,
		dataType: 'json',
		success: function(data) {
			map_autocomplete_line_free_to(obj,data,exept);
		}
	});
}

//get available extensions
function map_autocomplete_extension_to(obj,context)
{
	$.getJSON('/service/ipbx/ui.php/pbx_settings/extension/search/?obj=user&format=jquery&context='+context, function(data) {
		if (data === null || (nb = data.length) === 0)
			return false;
	    obj.autocomplete({
	    	source: data.split('\n')
	    });
	});
}

//get available number pool
function xivo_http_search_numpool(context,helper)
{
	var rs = '';
	$.ajax({
		url: '/service/ipbx/ui.php/pbx_settings/extension/search/?context='+context+'&obj=user&getnumpool=1',
		async: false,
		dataType: 'json',
		success: function(data) {
			if (data === null || (nb = data.length) === 0)
				return false;
		    for (var i = 0; i< nb; i++)
		    	rs += data[i]['numberbeg']+' - '+data[i]['numberend']+'<br>';
		    $(helper).html(rs);
		}
	});
}

//get list context available for a entity
function xivo_http_search_context_from_entity(entityid)
{
	$.ajax({
		url: '/xivo/configuration/ui.php/manage/entity?act=get&id='+entityid+'&contexttype=internal',
		async: false,
		dataType: 'json',
		success: function(data) {
			if (data === null || (nb = data.length) === 0) {
				$('#box-lines_free').hide('slow');
				$('#list_linefeatures').hide();
				$('#box-no_context').show();
				return false;
			}
			$('#box-no_context').hide();
			//$('#box-lines_free').show();
			$('#list_linefeatures').show();
			$('#list_linefeatures').find("#linefeatures-context").each(function(){
				$(this).find('option').remove();
			    for (var i = 0; i< nb; i++)
			    	$(this).append("<option value=" + data[i]['name'] + ">" + data[i]['displayname'] + "</option>");
		    });
			$('#ex-linefeatures').find("#linefeatures-context").each(function(){
				$(this).find('option').remove();
			    for (var i = 0; i< nb; i++)
			    	$(this).append("<option value=" + data[i]['name'] + ">" + data[i]['displayname'] + "</option>");
		    });
			update_row_infos();
			xivo_http_search_linefree_by_entity(entityid);
		}
	});		
}

//get list line free available for a entity
function xivo_http_search_linefree_by_entity(entityid)
{
	$.ajax({
		url: '/service/ipbx/ui.php/pbx_settings/lines/?act=contexts&entityid='+entityid+'&contexttype=internal&free=1',
		async: false,
		dataType: 'json',
		success: function(data) {
			if (data === null || data.length === 0){
				$('#box-lines_free').hide('slow');
				return false;
			}
			$('#box-lines_free').show();
		    $("#list_lines_free").each(function(){
				$(this).find('option').remove();
			    for (var i = 0; i< data.length; i++)
			    	$(this).append("<option value=" + data[i]['id'] + ">" + data[i]['identity'] + "</option>");
		    });
		}
	});
}

function lnkdroprow(obj)
{	
    $(obj).parents('tr').fadeTo(400, 0, function () {
        $(this).remove();
    });    
    
    setTimeout(update_row_infos, 420);
	
    it_id = $(obj).parents('tr').find('#linefeatures-id');
	
	if (it_id.val() == 0)
		return false;
    
    it_protocol = $(obj).parents('tr').find('#linefeatures-protocol');
    it_name = $(obj).parents('tr').find('#linefeatures-name');
    
	$('#list_lines_free').append("<option value=" + it_id.val() + ">" + it_protocol.val()+'/'+it_name.val() + "</option>");
	
    if ($('#list_lines_free option').length > 0)
    	$('#box-lines_free').show();
    
    return false;
}

function get_entityid_val()
{
	it_userfeatures_entityid = $('#it-userfeatures-entityid');
	it_cache_entityid = $('#it-cache_entityid');	
	 
	if ((entityid_val = it_userfeatures_entityid.val()) === false)
		entityid_val = it_cache_entityid.val();
	
	if (!entityid_val)
		return false;
	
	return(entityid_val);
}

function update_row_time(time,group)
{
	var groupval = '';
	$('#list_linefeatures > tbody').find('tr').each(function() {
		if($(this).attr('id') == 'tr-rules_group')
			groupval = $(this).find('#td_rules_group_name').text();
		else{
			if(groupval == group)
				$(this).find('#linefeatures-rules_time').val(time);
		}
	});
}

function update_row_infos()
{
	if ((entityid_val = get_entityid_val()) === false)
		return(false);
		
	nb_row = $('#list_linefeatures > tbody > tr').length;
	if (nb_row == 0) {
		$('#box-entityid').text('');
		it_userfeatures_entityid.removeAttr('disabled');
		it_userfeatures_entityid.removeClass('it-disabled');
		return false;
	}
	else {
		$('#box-entityid').html('<input type="hidden" id="it-cache_entityid" name="userfeatures[entityid]" value="'+entityid_val+'" />');
		it_userfeatures_entityid.attr('disabled','disabled');
		it_userfeatures_entityid.addClass('it-disabled');
	}
	
	var groupval = '';
	var grouporder = 0;
	var line_num = 0;
	var idx = 0;
	$('#list_linefeatures > tbody').find('tr').each(function() {	
		tr_group = false;
		
		if($(this).attr('id') == 'tr-rules_group') {
			grouporder = 0;
			if (idx > 0)
				line_num++;
			groupval = $(this).find('#td_rules_group_name').text();
			tr_group = true;
		} else
			grouporder++;
		
		$(this).find('#box-grouporder').html(grouporder);		
		
		if(tr_group === false) {
			
			context = $(this).find("#linefeatures-context");
			$(this).find('#linefeatures-rules_group').val(groupval);
			$(this).find('#linefeatures-line_num').val(line_num);
			$(this).find('#linefeatures-rules_order').val(grouporder);

			context_selected = context.parents('tr').find('#context-selected').val();
			if (context_selected !== null)
				context.find("option[value='"+context_selected+"']").attr("selected","selected");
			
			if (context.val() !== null) {				
				devicenumline = $(context).parents('tr').find("#linefeatures-num");
				config = $(context).parents('tr').find('#linefeatures-device').val();
				xivo_http_search_line_from_provd(devicenumline,config,devicenumline.val());

				$(context).parents('tr').find('#linefeatures-rules_time').
				change(function(){
					update_row_time($(this).val(),
							$(this).parents('tr').find('#linefeatures-rules_group').val());
				});
				/*
				timepicker({
					timeFormat: 's',
					showHour: false,
					showMinute: false,
					showSecond: true,
					onClose: function(a){
						update_row_time(a,group);
					}
				});
				*/
				
				var number = context.parents('tr').find('#linefeatures-number');
				number.focus(function(){
					helper = $(this).parent().find('#numberpool_helper');
					context = $(this).parents('tr').find("#linefeatures-context");
					xivo_http_search_numpool(context.val(),helper);
					helper.show('slow');
					map_autocomplete_extension_to($(this),context.val());
				});
				number.blur(function(){
					$(this).parent().find('#numberpool_helper').hide('slow');
				});
				device = $(this).find('#linefeatures-device').val();
				devicenumline = $(this).find("#linefeatures-num");
				if (device == '')
					devicenumline.hide();
				
				$(this).find('#linefeatures-device').change(function() {
					devicenumline = $(this).parents('tr').find("#linefeatures-num");
					$(devicenumline).each(function(){
						$(this).find('option').remove();
					    for (var i=1; i<=12; i++)
							$(this).append("<option value="+i+">"+i+"</option>");
					});
					xivo_http_search_line_from_provd(devicenumline,$(this).val());
				});
			}
		}
		idx++;
	});
}

$(document).ready(function() {
	
	xivo_http_search_context_from_entity(get_entityid_val());
	
	$('#it-userfeatures-entityid').change(function() {
		xivo_http_search_context_from_entity($(this).val());
	});

	$("#list_linefeatures tbody").sortable({
		helper: fixHelper,
		cursor: 'crosshair',
		update: update_row_infos
	});
	
	$('#lnk-add-row').click(function(){		
		$('#no-linefeatures').hide('fast');
	    row = $('#ex-linefeatures').html();
	    
		$('#list_linefeatures > tbody:last').fadeIn(400, function () {
	        $(this).append(row);
	    });

	    update_row_infos();
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
	    update_row_infos();	
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

	    $('#ex-linefeatures').find('#linefeatures-id').val(0);
		
		it_context = $('#list_linefeatures > tbody:last > tr').find("#linefeatures-context");
		
	    td_protocol = it_context.parents('tr:last').find('#td_ex-linefeatures-protocol');
	    td_name = it_context.parents('tr:last').find('#td_ex-linefeatures-name');	    	  

	    it_context.parents('tr:last').find('#linefeatures-protocol').remove();
	    it_context.parents('tr:last').find('#linefeatures-name').remove();

	    protoname = $('#list_lines_free option[value='+idlinefeatures+']').text();
	    
	    if (protoname.indexOf('/') == -1) {
		    td_protocol.append('fatal error: undefined protocol');
			td_name.append('fatal error: undefined peer');
	    }
	    else {
		    str_protocol = protoname.substring(0, protoname.indexOf('/')).toLowerCase();
		    str_name = protoname.substring(protoname.indexOf('/')+1);
		    
		    td_protocol.append(str_protocol.toUpperCase());
			it_proto = '<input type="hidden" id="linefeatures-protocol" name="linefeatures[protocol][]" value="'+str_protocol+'" />';
		    td_protocol.append(it_proto);
		    
		    td_name.append(str_name);
			it_name = '<input type="hidden" id="linefeatures-name" name="linefeatures[name][]" value="'+str_name+'" />';
			td_name.append(it_name);
	    }
	    
	    $('#list_lines_free option[value='+idlinefeatures+']').remove();
	    
	    if ($('#list_lines_free option').length == 0)
	    	$('#box-lines_free').hide('slow');
	    
	    update_row_infos();		
		return false;
	});
	
});
