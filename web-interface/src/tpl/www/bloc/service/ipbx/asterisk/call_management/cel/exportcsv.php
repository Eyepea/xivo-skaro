<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2011  Avencall
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

$url = &$this->get_module('url');

$result = $this->get_var('result');
$info = $this->get_var('info');

if($result === false)
	die();

header('Pragma: no-cache');
header('Cache-Control: private, must-revalidate');
header('Last-Modified: '.
	date('D, d M Y H:i:s',mktime()).' '.
	dwho_i18n::strftime_l('%Z',null));
header('Content-Disposition: attachment; filename=xivo_cel-'.
	dwho_i18n::strftime_l('%Y-%m-%d-%H:%M:%S',null).'.csv');
header('Content-Type: text/csv; charset=UTF-8');



echo	'"',str_replace('"','""',$this->bbf('fm_dbeg')),'";',
	'"',str_replace('"','""',$info['dbeg']),'"',"\n";

if($info['dend'] !== '')
{
	echo	'"',str_replace('"','""',$this->bbf('fm_dend')),'";',
		'"',str_replace('"','""',$info['dend']),'"',"\n";
}

if($info['channel'] !== '')
{
	if($info['channel'] === XIVO_SRE_IPBX_AST_CHAN_UNKNOWN)
		$info['channel'] = $this->bbf('fm_channel-opt','unknown');

	echo	'"',str_replace('"','""',$this->bbf('fm_channel')),'";',
		'"',str_replace('"','""',$info['channel']),'"',"\n";
}

if($info['amaflags'] !== '')
{
	echo	'"',str_replace('"','""',$this->bbf('fm_amaflags')),'";',
		'"',str_replace('"','""',$this->bbf('ast_amaflag_name_info',$info['amaflagsmeta'])),'"',"\n";
}

if($info['dcontext'] !== '')
{
	echo	'"',str_replace('"','""',$this->bbf('fm_dcontext')),'";',
		'"',str_replace('"','""',$info['dcontext']),'"',"\n";
}

if($info['dst'] !== '')
{
	echo	'"',str_replace('"','""',$this->bbf('fm_dst')),'";',
		'"',str_replace('"','""',$info['dst']),'"',"\n";
}


if($info['accountcode'] !== '')
{
	echo	'"',str_replace('"','""',$this->bbf('fm_accountcode')),'";',
		'"',str_replace('"','""',$info['accountcode']),'"',"\n";
}

if($info['userfield'] !== '')
{
	echo	'"',str_replace('"','""',$this->bbf('fm_userfield')),'";',
		'"',str_replace('"','""',$info['userfield']),'"',"\n";
}


echo "\n";

if($result === null || ($nb = count($result)) === 0)
{
	echo	$this->bbf('no_cel-result');
	header('Content-Length: '.ob_get_length());
	ob_end_flush();
	die();
}

echo	'"',str_replace('"','""',$this->bbf('col_calldate')),'";',
	'"',str_replace('"','""',$this->bbf('col_src')),'";',
	'"',str_replace('"','""',$this->bbf('col_dst')),'";',
	'"',str_replace('"','""',$this->bbf('col_duration')),'";',
	'"',str_replace('"','""',$this->bbf('col_channel')),'";',
	'"',str_replace('"','""',$this->bbf('col_amaflags')),'";',
	'"',str_replace('"','""',$this->bbf('col_accountcode')),'";',
	'"',str_replace('"','""',$this->bbf('col_userfield')),'";',
	'"',str_replace('"','""',$this->bbf('col_dcontext')),'";',
	'"',str_replace('"','""',$this->bbf('col_dstchannel')),'";',
	'"',str_replace('"','""',$this->bbf('col_uniqueid')),'"',"\n";

for($i = 0;$i < $nb;$i++)
{
	$ref = &$result[$i];

	$ref0 = array_shift($ref);
	$ref1 = array_shift($ref);

	if(!isset($ref0['from']) || !dwho_has_len($ref0['from']))
		$ref0['from'] = '-';

	if(!isset($ref0['to']) || !dwho_has_len($ref0['to']))
		$ref0['to'] = '-';

	if($ref0['channame'] === XIVO_SRE_IPBX_AST_CHAN_UNKNOWN)
		$ref0['channame'] = $this->bbf('entry_channel','unknown');

	echo	'"',str_replace('"','""',strftime($this->bbf('date_format_yymmddhhiiss'),strtotime($ref0['dstart']))),'";',
		'"',str_replace('"','""',$ref0['from']),'";',
		'"',str_replace('"','""',$ref0['to']),'";',
		'"',str_replace('"','""',$ref0['duration']),'";',
		'"',str_replace('"','""',$ref0['channame']),'";',
		'"',str_replace('"','""',$this->bbf('ast_amaflag_name_info',$ref0['amaflagsmeta'])),'";',
		'"',str_replace('"','""',$ref0['accountcode']),'";',
		'"',str_replace('"','""',$ref0['userfield']),'";',
		'"',str_replace('"','""',$ref0['context']),'";',
		'"',str_replace('"','""',$ref1['channame']),'";',
		'"',str_replace('"','""',$ref0['uniqueid']),'"',"\n";
}

header('Content-Length: '.ob_get_length());
ob_end_flush();
die();

?>
