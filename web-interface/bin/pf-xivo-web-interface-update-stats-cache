<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2011  Proformatique <technique@proformatique.com>
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

$erase = false;
if (isset($GLOBALS['argv']) === true)
{
	foreach ($GLOBALS['argv'] as $argv)
	{
		if ($argv === 'erase')
			$erase = true;
	}
}

require_once('xivo.php');

$ipbx = &$_SRE->get('ipbx');

if(xivo::load_class('xivo_statistics',XIVO_PATH_OBJECT,null,false) === false)
	die('Failed to load xivo_statistics object');

if (($appstats_conf = &$_XOBJ->get_application('stats_conf')) === false
|| ($listconf = $appstats_conf->get_stats_conf_list(null,'name')) === false)
	exit('application stats_conf required or no stats_conf registered');

$base_memory = memory_get_usage();

while ($listconf)
{
	$conf = array_shift($listconf);
	$idconf = (int) $conf['id'];
	
	$_XS = new xivo_statistics(&$_XOBJ,&$ipbx);
	$_XS->set_idconf($idconf,true);
	
	$listype = $_XS->get_listtype();
	$nblt = count($listype);
	for($i=0;$i<$nblt;$i++)
	{
		$type = $listype[$i];
		$_XS->_objectkey = 0;
		$listobject = $_XS->get_list_by_type($type);
		while($listobject)
		{
			$object = array_shift($listobject);
			
			if (empty($object) === true)
				continue;
			
			$_XS->update_cache($idconf,$type,$object,$erase);
			echo "-- memory usage: ", dwho_byte_to(memory_get_usage() - $base_memory), "\n";
		}
	}
}

echo "-- full memory usage: ", dwho_byte_to(memory_get_peak_usage()), "\n";

exit;

?>
