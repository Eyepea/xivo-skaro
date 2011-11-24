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

class xivo_stats
{
	var $_conf			= array();
	var $_identity		= array();

	public function __construct()
	{
	}

	public function load_ressource($ressource)
	{
		$this->_load_ressource_abstract();

		$ressource = (string) $ressource;

		$file = $ressource.'.inc';

		$dir = dwho_file::joinpath(XIVO_PATH_OBJECT,
								  'stats',
								  '_ressource');

		$class = 'stats_ressource_'.$ressource;

		if(dwho_file::load_file($file,$dir,true) !== false && class_exists($class) === true)
			return($class);

		return(false);
	}

	function _load_ressource_abstract()
	{
		$dir = dwho_file::joinpath(XIVO_PATH_OBJECT,
								  'stats',
								  '_ressource',
								  'abstract');

		$class = 'xivo_stats_ressource_abstract';

		if(dwho_file::load_file('abstract.inc',$dir,true) !== false && class_exists($class) === true)
			return($class);

		return(false);
	}
}

?>
