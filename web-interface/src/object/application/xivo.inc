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

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'application','abstract.inc'));

class xivo_application_xivo_object_abstract extends xivo_application_abstract
{
	var $_xobj	= null;

	public function __construct(&$xobj)
	{
		if(dwho_is_instance($xobj,'xivo_object') === false)
			trigger_error('Invalid XIVO Object in '.__CLASS__,E_USER_ERROR);

		$this->_xobj = &$xobj;
	}
}

?>
