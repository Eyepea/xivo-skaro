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


function xivo_ast_incall_chg_dialaction_answer(obj)
{
    xivo_ast_chg_dialaction('answer',obj);
}

function xivo_ast_incall_chg_dialaction_actionarg_answer_application()
{
    xivo_ast_chg_dialaction_actionarg('answer','application');
}

function xivo_ast_incall_onload()
{
    xivo_ast_build_dialaction_array('answer');
    xivo_ast_dialaction_onload();
}

dwho.dom.set_onload(xivo_ast_incall_onload);

