<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2010  Proformatique <technique@proformatique.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

$array = array();

$array['element'] = array();

$array['element']['endcall'] = array();
$array['element']['endcall']['value'] = array('no','yes');
$array['element']['endcall']['default'] = 'yes';
$array['element']['endcall']['set'] = true;

$array['element']['autologoffunavail'] = array();
$array['element']['autologoffunavail']['value'] = array('no','yes');
$array['element']['autologoffunavail']['default'] = 'no';
$array['element']['autologoffunavail']['set'] = true;

$array['element']['maxlogintries'] = array();
$array['element']['maxlogintries']['value'] = range(0,10);
$array['element']['maxlogintries']['default'] = 3;
$array['element']['maxlogintries']['setdef'] = true;

$array['element']['goodbye'] = array();
$array['element']['goodbye']['default'] = 'vm-goodbye';
$array['element']['goodbye']['setdef'] = true;

$array['element']['updatecdr'] = array();
$array['element']['updatecdr']['value'] = array('no','yes');
$array['element']['updatecdr']['default'] = 'no';
$array['element']['updatecdr']['set'] = true;

$array['element']['recordagentcalls'] = array();
$array['element']['recordagentcalls']['value'] = array('no','yes');
$array['element']['recordagentcalls']['default'] = 'no';
$array['element']['recordagentcalls']['set'] = true;

$array['element']['recordformat'] = array();
$array['element']['recordformat']['value'] = array(XIVO_SRE_IPBX_AST_FORMAT_AUDIO_WAV,
						   XIVO_SRE_IPBX_AST_FORMAT_AUDIO_WAV49,
						   XIVO_SRE_IPBX_AST_FORMAT_AUDIO_GSM);
$array['element']['recordformat']['default'] = XIVO_SRE_IPBX_AST_FORMAT_AUDIO_WAV;
$array['element']['recordformat']['setdef'] = true;

$array['element']['urlprefix'] = array();
$array['element']['urlprefix']['default'] = '';

$array['element']['savecallsin'] = array();
$array['element']['savecallsin']['default'] = '';

$array['element']['custom_beep'] = array();
$array['element']['custom_beep']['default'] = 'beep';
$array['element']['custom_beep']['setdef'] = true;

$array['filter'] = array();
$array['filter']['endcall'] = array('bool' => true);
$array['filter']['autologoffunavail'] = array('bool' => true);
$array['filter']['maxlogintries'] = array('cast' => 'uint','between' => array(0,10));
$array['filter']['goodbye'] = array('set'	=> false,
				    'chk'	=> 2,
				    'maxlen'	=> 255,
				    'regexp'	=> '/^'.XIVO_SRE_IPBX_AST_REGEXP_AUDIO_FILE_PATTERN.'$/');
$array['filter']['updatecdr'] = array('bool' => true);
$array['filter']['recordagentcalls'] = array('bool' => true);
$array['filter']['recordformat'] = array('set'	=> false,
					 'chk'	=> 2,
					 'key'	=> array(XIVO_SRE_IPBX_AST_FORMAT_AUDIO_WAV,
							 XIVO_SRE_IPBX_AST_FORMAT_AUDIO_WAV49,
							 XIVO_SRE_IPBX_AST_FORMAT_AUDIO_GSM));
$array['filter']['urlprefix'] = array('set'	=> false,
				      'chk'	=> 2,
				      'minlen'	=> 3,
				      'maxlen'	=> 255,
							'cast'	=> 'sgraph');
$array['filter']['savecallsin'] = array('set' => false,
					'chk'   => 2,
					'maxlen' => 255);
$array['filter']['custom_beep'] = array('set'		=> false,
					'chk'		=> 2,
					'maxlen'	=> 255,
					'regexp'	=> '/^'.XIVO_SRE_IPBX_AST_REGEXP_AUDIO_FILE_PATTERN.'$/');

?>
