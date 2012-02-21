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

class dwho_prefs
{
	var $_section = null;
	var $_QR      = null;

	function dwho_prefs($section)
	{
		if(!array_key_exists('_WEBI', $_SESSION))
			$_SESSION['_WEBI'] = array();
		if(!array_key_exists($section, $_SESSION['_WEBI']))
			$_SESSION['_WEBI'][$section] = array();

		$this->_section = &$_SESSION['_WEBI'][$section];
		$this->_QR = &dwho_gat::get('_QR');

		if (isset($this->_QR['search']))
			$this->_section['page'] = 1;
	}

	function get($name, $default)
	{
		if(isset($this->_QR[$name]))
			$this->_section[$name] = $this->_QR[$name];

		if(isset($this->_section[$name]))
			return $this->_section[$name];

		return $default;
	}

	function set($name, $value)
	{
		$this->_section[$name] = $value;
	}

	function del($name)
	{
		unset($this->_section[$name]);
	}

	function flipflop($name, $default)
	{
		if(isset($this->_QR[$name]))
		{
			$new = array(SORT_ASC, $this->_QR[$name]);

			if(isset($this->_section[$name]) &&    $this->_section[$name][1] == $new[1])
				$new[0] = $this->_section[$name][0] == SORT_ASC?SORT_DESC:SORT_ASC;
		}
		else if(isset($this->_section[$name]))
		{
			$new = $this->_section[$name];
		}
		else
		{
			$new = array(SORT_ASC, $default);
		}

		$this->_section[$name] = $new;
		return $new;
	}
}

?>
