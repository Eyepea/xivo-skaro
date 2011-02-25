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

abstract class dwho_date
{

	static private	$_counter			= 0;
	static private	$_regex		 	= array('datetime'	=> '/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',
											'unixtime'	=> '/^(\d{10})$/',
											'date'		=> '/^(\d{4})-(\d{2})-(\d{2})$/',
											'time'		=> '/^(\d{2}):(\d{2}):(\d{2})$/',
											'strtotime'	=> '/^[+-]?[0-9]+ (((sec|second|min|minute|hour|day|fortnight|forthnight|month|year)s?)|weeks|daytext)$/');	
	static private	$_listday		= array('monday','tuesday','wednesday','thursday','friday','saturday','sunday');
	static private	$_listmonth		= array('january','february','march','april','may','june','july','august','september','october','november','december');
	static private 	$_infocal		= array('dbeg' => null,'dend' => null, 'dday' => null, 'dweek' => null, 'dmonth' => null, 'dyear' => null);
	static public	$_listaxetype	= array('period','day','week','month','year');
	
	public static function init_infocal($interval=null)
	{			
		$dbeg = self::all_to_unixtime(self::$_infocal['dbeg']);
		$dend = self::all_to_unixtime(self::$_infocal['dend']);
		
		if(is_null($interval) === false)
			$dbeg = strtotime($interval, $dend);
		
		$infocal = array();
		$infocal['dbeg'] 	= date('Y-m-d',$dbeg);
		$infocal['dend'] 	= date('Y-m-d',$dend);
		$infocal['dday'] 	= date('Y-m-d',$dbeg);
		$infocal['dweek'] 	= date('Y-m-d',$dbeg);
		$infocal['dmonth'] 	= date('Y-m',$dbeg);
		$infocal['dyear'] 	= date('Y',$dbeg);
		
		return($infocal);
	}
	
	public static function get_infocal()
	{
		return(self::$_infocal);
	}
	
	private static function isvalid_interval($dip)
	{
		if (is_array($dip) === true
		&& isset($dip['beg']) === true
		&& isset($dip['end']) === true
		&& preg_match(self::$_datetime,$dip['beg']) === 1
		&& preg_match(self::$_datetime,$dip['end']) === 1)
			return(true);
			
		return(false);
	}
		
	public static function build_full_date_interval($dbeg,$dend)
	{
		$rs = array();
					
		$hour_start = '00:00:01';
		$hour_end = '23:59:59';
		
		$listday = self::get_listday_for_interval($dbeg,$dend);
		$listidx = array_keys($listday);
		while($listidx)
		{
			$index = array_shift($listidx);
			$key = $listday[$index]['key'];
			$day_process = $listday[$index]['time'];
			$dip = array();
			$dip['beg'] = strtotime(date('Y-m-d',$day_process).' '.$hour_start);
			$dip['end'] = strtotime(date('Y-m-d',$day_process).' '.$hour_end);
			$rs[$key] = $dip;
		}		
		return($rs);
	}
		
	public static function set_infocal($axtetype,$arr)
	{
		$infocal = self::init_infocal();
	
		switch ($axtetype)
		{
			case 'day':
				if (isset($arr['dday']) === true)
				{
					$infocal['dday'] = $arr['dday'];
					$time = strtotime($infocal['dday']);
					$dbeg = mktime(0,0,1,date('m',$time),date('d',$time),date('Y',$time));
					$dend = mktime(23,59,59,date('m',$time),date('d',$time),date('Y',$time));
					$infocal['dbeg'] = date('Y-m-d',$dbeg);
					$infocal['dend'] = date('Y-m-d',$dend);
				}
				break;
			case 'week':
				if (isset($arr['dweek']) === true)
				{
					$infocal['dweek'] = $arr['dweek'];
					$time = self::all_to_unixtime($infocal['dweek']);
					$date = self::get_week_range($time);
					$infocal['dbeg'] = date('Y-m-d',$date['beg']);
					$infocal['dend'] = date('Y-m-d',$date['end']);
				}
				break;
			case 'month':
				if (isset($arr['dmonth']) === true)
				{
					$infocal['dmonth'] = $arr['dmonth'];
					$time = self::all_to_unixtime($infocal['dmonth']);
					$date = self::get_month_range($time);
					$infocal['dbeg'] = date('Y-m-d',$date['beg']);
					$infocal['dend'] = date('Y-m-d',$date['end']);
				}
				break;
			case 'year':
				if (isset($arr['dyear']) === true)
				{
					$infocal['dyear'] = $arr['dyear'];
					$time = self::all_to_unixtime($infocal['dyear']);
					$date = self::get_year_range($time);
					$infocal['dbeg'] = date('Y-m-d',$date['beg']);
					$infocal['dend'] = date('Y-m-d',$date['end']);
				}
				break;
			case 'period':
			default:		
				if (isset($arr['dbeg']) === true
				&& isset($arr['dend']) === true)
				{
					$infocal['dbeg'] = $arr['dbeg'];
					$infocal['dend'] = $arr['dend'];
				}
		}
		
		self::$_infocal = $infocal;
		return($infocal);
	}
	
	public static function all_to_unixtime($str)
	{
		$rs = time();	
		if (preg_match(self::$_regex['datetime'],$str) === 1)
			$rs = (int) strtotime($str);
		elseif (preg_match(self::$_regex['unixtime'],$str) === 1)
			$rs = (int) $str;
		elseif (preg_match(self::$_regex['date'],$str) === 1)
			$rs = (int) strtotime($str);
		elseif (preg_match('/^(\d{4})-(\d{2})$/',$str) === 1)
			$rs = (int) strtotime($str.'-01');
		elseif (preg_match('/^(\d{4})$/',$str) === 1)
			$rs = (int) strtotime($str.'-01-01');
			
		return($rs);
	}
	
	public static function get_year_range($date)
	{
		$date = self::all_to_unixtime($date);
		$year = date('Y',$date);
		$firstday = mktime(0, 0, 0, 1, 1, $year);
		$lastday = self::get_lastday_for_month($year,12);
		$rs = array();
		$rs['beg'] = $firstday;
		$rs['end'] = $lastday;		
		return($rs);
	}
		
	public static function get_month_range($date)
	{
		$date = self::all_to_unixtime($date);
		$month = date('m',$date);
		$year = date('Y',$date);
		$firstday = mktime(0, 0, 0, $month, 1, $year);
		$lastday = mktime(23, 59, 59, $month + 1, 0, $year);
		$rs = array();
		$rs['beg'] = $firstday;
		$rs['end'] = $lastday;		
		return($rs);
	}
		
	public static function get_week_range($date)
	{
		$date = self::all_to_unixtime($date);
		$week = date('W',$date);
		$year = date('Y',$date);
		$rs = array();
		$rs['beg'] = strtotime("{$year}-W{$week}-1");
		$rs['end'] = strtotime("{$year}-W{$week}-7");		
		return($rs);
	}
	
	public static function get_listhour($start=null,$end=null)
	{		
		$rs = array();
		for ($i=0;$i<=23;$i++)
		{
			if ((!is_null($start) && $i < $start)
			|| (!is_null($end) && $i > $end))
				continue;
				
			$tmp = array();
			$tmp['identity'] = dwho_i18n::babelfish('hour-opt',$i);
			$tmp['name'] = $i;
			$tmp['key'] = $i;
				
			array_push($rs,$tmp);
		}
		return($rs);
	}
	
	public static function get_listday_for_week()
	{
		$rs = array();
		foreach (self::$_listday as $dayname)
		{				
			$tmp = array();
			$tmp['identity'] = dwho_i18n::babelfish($dayname);
			$tmp['name'] = $dayname;
			$tmp['key'] = $dayname;
			$rs[$dayname] = $tmp;
		}
		return($rs);
	}
	
	public static function get_lastday_for_month($year,$month)
	{		
		if (preg_match('/^(\d{4})-(\d{2})$/',"$year-$month") === 1)
			return(mktime(23, 59, 59, $month+1, 0, $year));
			
		return(false);
	}
	
	public static function get_listday_for_month($year,$month)
	{		
		#$lastday = strtotime('-1 day',strtotime('+1 month',strtotime($month.'/01/'.$year)));
		$lastday = mktime(23, 59, 59, $month + 1, 0, $year);
		
		$rs = array();
		for ($i=1;$i<=date('d',$lastday);$i++)
		{
			$time = mktime(0,0,0,$month,$i,$year);
			$daynumber = date('d',$time);
			$monthnumber = date('m',$time);
			$dayname = strtolower(date('l',$time));
				
			$tmp = array();
			$tmp['identity'] = dwho_i18n::babelfish($dayname.'-opt',$i);
			$tmp['index'] = (int) $year.$monthnumber.$daynumber;
			$tmp['dayname'] = $dayname;
			$tmp['day'] = $daynumber;
			$tmp['name'] = $dayname;
			$tmp['key'] = $daynumber;
			$tmp['time'] = (int) $time;
			$rs[$daynumber] = $tmp;
		}
		return($rs);
	}
	
	public static function get_listday_for_interval($dbeg,$dend)
	{
		$dbeg = self::all_to_unixtime($dbeg);
		$dend = self::all_to_unixtime($dend);
		
		$day_process = strtotime('-1 day',$dbeg);
		$listday = array();
		while ($day_process < ((int) $dend))
		{
			$day_process = strtotime('+1 day',$day_process);	
			$dayname = strtolower(date('l',$day_process));
			$daynumber = date('d',$day_process);
			$month = date('m',$day_process);
			$year = date('Y',$day_process);
			
			$tmp = array();
			$tmp['identity'] =  dwho_i18n::babelfish($dayname);
			$tmp['key'] = (int) ($year.$month.$daynumber);
			$tmp['day'] = $daynumber;
			$tmp['dayname'] = $dayname;
			$tmp['time'] = (int) $day_process;
			$listday[$tmp['key']] = $tmp;
		}		
		return($listday);
	}
	
	public static function get_listmonth_for_interval($dbeg,$dend)
	{
		$dbeg = self::all_to_unixtime($dbeg);
		$dend = self::all_to_unixtime($dend);
		
		$month_process = $dbeg;
		#$month_process = strtotime('-1 month',$dbeg);
		#$month_process = mktime(0, 0, 0, date('m',$month_process), 1, date('Y',$month_process));
		$listmonth = array();
		while ($month_process <= ((int) $dend))	
		{
			$dayname = strtolower(date('l',$month_process));
			$month = date('m',$month_process);
			$year = date('Y',$month_process);
			
			$tmp = array();
			$tmp['identity'] = dwho_i18n::babelfish(self::$_listmonth[intval($month)-1]);
			$tmp['key'] = (int) ($year.$month);
			$tmp['time'] = (int) $month_process;					
			array_push($listmonth,$tmp);
			$month_process = strtotime('+1 month',$month_process);	
		}
		return($listmonth);
	}
	
	public static function get_listmonth()
	{
		$rs = array();
		for ($i=0;$i<=11;$i++)
		{
			$tmp = array();
			$tmp['identity'] = dwho_i18n::babelfish(self::$_listmonth[$i]);
			$tmp['name'] = self::$_listmonth[$i];
			$tmp['key'] = $i+1;
				
			array_push($rs,$tmp);
		}		
		return($rs);
	}
	
	public static function get_day_from_week_by_name_day($year,$week,$nameday)
	{
		$from = strtotime("{$year}-W{$week}-1");
		$to = strtotime("{$year}-W{$week}-7");
		
		$rs = array();
		for ($i=$from;$i<=$to;$i=strtotime('+1day',$i))
		{
			if (date('l',$i) === ucfirst($nameday))
				return(date('Y-m-d',$i));
		}
		return(null);
	}

	private static function eval_during_time($key,$eventprocess,$eventstart,$eventend,$time)
	{			
		if (isset(self::$_counter[$key]) === false)
			self::$_counter[$key] = array();
			
		if (isset(self::$_counter[$key][$eventstart]) === false)
		{
			self::$_counter[$key][$eventstart] = array();
			self::$_counter[$key][$eventstart]['start'] = 0;
			self::$_counter[$key][$eventstart]['token'] = 0;
			self::$_counter[$key][$eventstart]['total'] = 0;
		}
					
		$counter = &self::$_counter[$key][$eventstart];
		$timearr = explode('.',$time);
		
		if (preg_match(self::$_regex['datetime'],$timearr[0]) !== 1)
			return(false);
		
		$timeprocess = self::all_to_unixtime($timearr[0]);
		
		$rs = 0;
		switch ($eventprocess)
		{
			case $eventstart:
				if ($counter['token'] === 1
				&& $counter['start'] !== 0)
					$rs = ($timeprocess - $counter['start']);	
				$counter['token'] = 1;
				$counter['start'] = $timeprocess;
				break;
			case $eventend:
				if ($counter['token'] === 0)
					continue;
				$rs = ($timeprocess - $counter['start']);					
				$counter['token'] = 0;
				$counter['start'] = 0;
				break;
			default:
		}
		
		$counter['total'] += $rs;
		
		return($rs);
	}	
}

?>
