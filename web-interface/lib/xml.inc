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

class dwho_xml
{
	function get_header()
	{
		return('Content-Type: application/xml');
	}

	function encode($data)
	{
		return($data);
	}

	function decode($data,$assoc=false)
	{
		if(dwho_has_len($data) === false)
			return(false);
			
		$data = (array) simplexml_load_string($data);
		
		return(json_decode(json_encode($data),1));
	}
}

?>
