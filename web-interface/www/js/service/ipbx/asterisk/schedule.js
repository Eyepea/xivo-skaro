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

var dialevent = 0;

function xivo_ast_schedule_add_dyn_dialaction(dialname)	
{
	dialevent += 1;

	xivo_elt_dialaction[dialname] = {};
	xivo_fm_dialaction[dialname]  = {};

	xivo_ast_build_dialaction_array(dialname);
	if((action = dwho_eid('it-dialaction-'+dialname+'-actiontype')) !== false)
		xivo_ast_chg_dialaction(dialname,action);
}

function xivo_ast_schedule_add_closed_action(name, obj)
{

	dialevent  += 1;

//  'onclick="dwho.dom.make_table_list(\'disp2\',this); return(dwho.dom.free_focus());"',
	new dwho.http('http://192.168.1.10/service/ipbx/ui.php/call_management/schedule?act=dialaction&event=' + dialevent,
		{'callbackcomplete':	function(xhr) 
			{ 
				elt = dwho_eid('onclosed-time-dialaction');
				elt.id = 'onclosed-time-dialaction-' + dialevent
				elt.innerHTML = xhr.responseText;

				dwho.dom.make_table_list(name, obj);

				xivo_elt_dialaction[dialevent] = {};
				xivo_fm_dialaction[dialevent]  = {};

				xivo_ast_build_dialaction_array(dialevent);
				if((action = dwho_eid('it-dialaction-'+dialevent+'-actiontype')) !== false)
					xivo_ast_chg_dialaction(dialevent,action);

				// restore model attributes after clone
				elt.id = 'onclosed-time-dialaction';
				elt.innerHTML = '';
			},
      'method':		'post',
      'cache':			false
		},
    {},
		true);

}

function xivo_ast_schedule_onload()
{
	xivo_ast_build_dialaction_array('schedule_fallback');
	xivo_ast_dialaction_onload();
}

dwho.dom.set_onload(xivo_ast_schedule_onload);
