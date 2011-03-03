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

/*
 * EXAMPLES
dwho_report::push('error',array('error'));
dwho_report::push('warning','warning');
dwho_report::push('info','info');
dwho_report::push('notice',array('notice',array('notice1','notice2')));
dwho_report::push('debug','debug');
*/

class dwho_report
{	
	private static $error		= array();
	private static $info		= array();
	private static $warning		= array();
	private static $notice		= array();
	private static $debug		= array();
	
	public static function push($type,$msg,$key=null) 
	{
		if (isset(self::${$type}) === true
		&& ($self = &self::${$type}) === false)
			return(false);
		
		if (is_array($msg) === true)
		{
			$self =  array_merge($self,$msg);
			$self = array_unique($self);
		}
		elseif (is_null($key) === false
		&& is_scalar($msg) === true)
			$self[$key] = $msg;
		elseif(is_null($key) === true
		&& is_scalar($msg) === true)
			array_push($self, $msg);
		else
			return(false);

		return(true);
	}

	public static function has($type) 
	{
		if (isset(self::${$type}) === true
		&& ($self = &self::${$type}) === false)
			return(false);
			
		if (empty($self) === true)
			return(false);

		return(true);
	}

	public static function get($type) 
	{
		if (isset(self::${$type}) === true
		&& ($self = &self::${$type}) === false)
			return(false);
			
		return($self);
	}
	
	public static function get_message($type)
	{		
		if (($enable = dwho_constant('REPORT_'.strtoupper($type))) === null		
		|| ((bool) $enable) === false)
			return(false);
		
		if (isset(self::${$type}) === true
		&& ($self = &self::${$type}) === false
		&& self::has($type) === false)
			return(false);
			
		$return = '';
		$return .= '<div class="xivo-'.$type.' xivo-messages">';
		$return .= '<ul>';
		foreach($self as $k => $v)
		{
			if (is_array($v) === true)
			{
				$return .= '<ul>';
				foreach($v as $k2 => $v2)
					$return .= '<li>&nbsp; '.$v2.'</li>';
				$return .= '</ul>';
			}
			else
			$return .= '<li>&nbsp; '.$v.'</li>';
		}	
		$return .= '</ul>';
		$return .= '</div>';
		
		return($return);
	}

	public static function encode() 
	{
		$listtype = get_class_vars('dwho_report');
		$listtype = array_keys($listtype);
		
		$rs = array();
		for ($i=0;$i<count($listtype);$i++)
		{
			$type = $listtype[$i];
			if (self::has($type) === false)
				continue;
			$rs[$type] = self::get($type);
		}
		$rs = serialize($rs);
		#$rs = base64_encode($rs);	
		$rs = urlencode($rs);
		return($rs);
	}

	public static function decode() 
	{
		if (isset($_SERVER['QUERY_STRING']) === false
		|| empty($_SERVER['QUERY_STRING']) === true)
			return(null);
		
		parse_str($_SERVER['QUERY_STRING'],$out);

		if (array_key_exists('_report',$out) === false)
			return(null);
			
		$_report = $out['_report'];
		
		$str = urldecode($_report);
		#$str = base64_decode($str);
		$arr = unserialize($str);
		
		$listtype = get_class_vars('dwho_report');
		
		foreach($arr as $type => $value)
		{
			if (isset($listtype[$type]) === false)
				continue;
			
			self::push($type,$value);
		}
	}
}

?>