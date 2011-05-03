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

// get available extensions
function xivo_ast_queue_http_search_extension(dwsptr)
{
	context = dwho_eid('it-queuefeatures-context').value;
	new dwho.http('/service/ipbx/ui.php/pbx_settings/extension/search/?obj=queue&context=' + context,
		{'callbackcomplete':	function(xhr) 
			{	dwsptr.set(xhr,dwsptr.get_search_value()); },
      'method':		'post',
      'cache':			false
		},
    {'startnum':	dwsptr.get_search_value()},
		true);
}

var xivo_ast_queue_suggest_extension = new dwho.suggest({'requestor': xivo_ast_queue_http_search_extension});

function xivo_ast_queue_suggest_event_extension()
{
	xivo_ast_queue_suggest_extension.set_option('result_field', 'it-queuefeatures-numberid');
	xivo_ast_queue_suggest_extension.set_option('result_emptyalert', true);
	xivo_ast_queue_suggest_extension.set_option('result_minlen', 0);
		
	xivo_ast_queue_suggest_extension.set_field(this.id);
}

function xivo_ast_queue_onload()
{
	xivo_ast_build_dialaction_array('noanswer');
	xivo_ast_build_dialaction_array('busy');
	xivo_ast_build_dialaction_array('congestion');
	xivo_ast_build_dialaction_array('chanunavail');
	xivo_ast_build_dialaction_array('qctipresence');
	xivo_ast_build_dialaction_array('qnonctipresence');
	xivo_ast_build_dialaction_array('qwaittime');
	xivo_ast_build_dialaction_array('qwaitratio');
	xivo_ast_dialaction_onload();
	
	if((num = dwho_eid('it-queuefeatures-number')) !== false)
	{
		dwho.dom.add_event('focus', num, xivo_ast_queue_suggest_event_extension);
		num.setAttribute('autocomplete','off');
	}
}

dwho.dom.set_onload(xivo_ast_queue_onload);


$(document).ready(function() {
	$('.multiselect').multiselect();
})
