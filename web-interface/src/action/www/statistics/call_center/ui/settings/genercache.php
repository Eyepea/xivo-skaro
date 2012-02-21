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

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'stats','stats.inc'));
$_XS = new xivo_stats_lib();

if(isset($_QR['idconf']) === true
&& isset($_QR['dbeg']) === true
&& isset($_QR['dend']) === true
&& isset($_QR['type']) === true)
{
	$idtype = (isset($_QR['idtype']) && $_QR['idtype'] !== 'all') ? $_QR['idtype'] : null;
	$_XS->generate_cache($_QR['idconf'],$_QR['dbeg'],$_QR['dend'],$_QR['type'],$idtype);
	return;
}

if(isset($_QR['update']) === true)
{
	if (($appstats_conf = &$_XOBJ->get_application('stats_conf')) === false
	|| ($listconf = $appstats_conf->get_stats_conf_list(null,'name')) === false)
		exit;

	while ($listconf)
	{
		$conf = array_shift($listconf);
		$_XS->update_cache($conf);
	}
}

?>