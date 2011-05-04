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

class dwho_json
{
	public static function load_extension()
	{
		if(dwho::load_extension('json') === false)
			trigger_error('Unable to load json',E_USER_ERROR);
	}

	public static function get_header()
	{
		return('Content-Type: application/json');
	}
	
	public static function encode($data,$options=0)
	{
		dwho_json::load_extension();

		return(json_encode($data,$options));
	}	

	public static function decode($data,$assoc=false)
	{
		if(dwho_has_len($data) === false)
			return(false);

		dwho_json::load_extension();

		return(json_decode($data,(bool) $assoc));
	}
}

?>
