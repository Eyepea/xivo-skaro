/*
 * XiVO Web-Interface
 * Copyright (C) 2010  Guillaume Bour, Proformatique <technique@proformatique.com>
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

var xivo_ast_fm_tcpbindaddr = {
    'it-tcpbindaddr':
        {property: [{disabled: false, className: 'it-enabled'},
                {disabled: true, className: 'it-disabled'}]}};

xivo_attrib_register('ast_fm_tcpbindaddr',xivo_ast_fm_tcpbindaddr);

var xivo_ast_fm_tlsbindaddr = {
    'it-tlsbindaddr':
        {property: [{disabled: false, className: 'it-enabled'},
                {disabled: true, className: 'it-disabled'}],
         link: 'it-tlscertfile'},
    'it-tlscertfile':
        {property: [{disabled: false, className: 'it-enabled'},
                {disabled: true, className: 'it-disabled'}],
         link: 'it-tlscafile'},
    'it-tlscafile':
        {property: [{disabled: false, className: 'it-enabled'},
                {disabled: true, className: 'it-disabled'}],
         link: 'it-tlsdontverifyserver'},
    'it-tlsdontverifyserver':
        {property: [{disabled: false, className: 'it-enabled'},
                {disabled: true, className: 'it-disabled'}],
         link: 'it-tlscipher'},
    'it-tlscipher':
        {property: [{disabled: false, className: 'it-enabled'},
                {disabled: true, className: 'it-disabled'}]},
    };

xivo_attrib_register('ast_fm_tlsbindaddr',xivo_ast_fm_tlsbindaddr);

function xivo_general_sip_onload()
{
    if((tcpenable = dwho_eid('it-tcpenable')) !== false)
        xivo_chg_attrib('ast_fm_tcpbindaddr',
                'it-tcpbindaddr',
                Number(tcpenable.checked === false));

    if((tlsenable = dwho_eid('it-tlsenable')) !== false)
        xivo_chg_attrib('ast_fm_tlsbindaddr',
                'it-tlsbindaddr',
                Number(tlsenable.checked === false));
}

dwho.dom.set_onload(xivo_general_sip_onload);
