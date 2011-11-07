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

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'abstract','libdatastorage.inc'));

abstract class xivo_stats_abstract extends xivo_libdatastorage_abstract
{
	protected	$_conf	= array();
	protected	$_stats	= null;

	public function __construct(&$stats)
	{
		if(dwho_is_instance($stats,'xivo_stats') === false)
			trigger_error('Invalid STATS Object in '.__CLASS__,E_USER_ERROR);

		$this->_stats = &$stats;

		$this->_load_config();
	}

	function get_name()
	{
		return($this->_name);
	}

	function _load_config($merge_abstract=false)
	{
		if(empty($this->_conf) === false)
			return(null);

		$dir = dwho_file::joinpath(XIVO_PATH_OBJECT,
					   'stats',
					   $this->_name,
					   'config');

		if(($this->_conf = dwho_gat::get_file($dir)) === false)
			$this->_conf = array();

		if ($merge_abstract === true
		&& ($conf = $this->_get_config_abstract()) !== false)
			$this->_conf = array_merge($this->_conf,$conf);
	}

	private function _get_config_abstract()
	{
		$dir = dwho_file::joinpath(XIVO_PATH_OBJECT,
					   'stats',
					   'abstract',
					   'config');

		if(($conf = dwho_gat::get_file($dir)) === false)
			$conf = false;

		return($conf);
	}
}

?>
