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

abstract class dwho_report {
	private static $error		= array();
	private static $info		= array();
	private static $warning		= array();
	private static $notice		= array();
	private static $debug		= array();
	private static $_exclude	= array('callback');

	public static function push_generic($type,$data,$key=null) {
		foreach ($data as $key => $value) {
			if (in_array($value, self::$_exclude)) {
				self::push('error', "$key -> generic error");
			} else {
				if (is_array($value)) {
					self::push_generic($type,$value);
				} else {
					self::push('error', "$key -> ".$value);
				}
			}
		}
	}

	public static function push($type,$msg,$key=null) {
		if (isset(self::${$type}) === true && ($self = &self::${$type}) === false) {
			return(false);
		} elseif (is_null($key) === true) {
			if(is_array($msg) === true) {
				while($msg) {
					self::push($type,array_shift($msg));
				}
			}
			elseif(is_scalar($msg) === true
			&& in_array($msg,$self) === false) {
				array_push($self, $msg);
			}
		} elseif (is_null($key) === false) {
			$keyencode = base64_encode($key);
			if (isset($self[$keyencode]) === false) {
				$self[$keyencode] = array();
			}
			if(is_array($msg) === true) {
				while($msg) {
					self::push($type,array_shift($msg),$key);
				}
			}
			elseif(is_scalar($msg) === true
			&& in_array($msg,$self[$keyencode]) === false) {
				array_push($self[$keyencode], $msg);
			}
		}

		return(true);
	}

	public static function get_message($type) {
		if (($enable = dwho_constant('REPORT_'.strtoupper($type))) === null || ((bool) $enable) === false) {
			return(false);
		}

		if (isset(self::${$type}) === true && ($self = self::${$type}) === false && self::has($type) === false) {
			return(false);
		}

		$_I18N = &dwho_gct::get('dwho_i18n');
		$_I18N->load_file('report/common');

		krsort($self);

		$return = '';
		$return .= '<div class="xivo-'.$type.' xivo-messages">';
		$return .= '<ul>';
		foreach($self as $k => $v)
		{
			if (is_string($k) === true
			&& is_array($v) === true)
			{
				$key = base64_decode($k);
				$id = uniqid();
				$query = array();
				$query['type'] = $type;
				$query['bloc'] = $k;
				$query =  http_build_query($query, '', '&amp;');

				$return .= '<a href="#" id="a-'.$id.'" class="xm_toggle">';
				$return .= '<span id="s-'.$id.'" class="ui-icon ui-icon-triangle-1-e"></span>';
				$return .= dwho_i18n::babelfish($key).' </a><div class="clearboth"></div>';
				$return .= '<ul id="'.$id.'" class="b-nodisplay" style="border:1px dotted red;">';
				$return .= '<a href="/exportreport.php?'.$query.'" class="bt_export">'.dwho_i18n::babelfish('report_export').'</a>';
				foreach($v as $submessage) {
					$return .= '<li>'.dwho_i18n::babelfish($submessage).'</li>';
				}
				$return .= '</ul>';

				$return .= "
				<script type='text/javascript'>
				$('#a-$id').click(function() {
					if ($('#$id').css('display') == 'none'){
						$('#s-$id').toggleClass('ui-icon-triangle-1-e');
						$('#s-$id').toggleClass('ui-icon-triangle-1-s');
						$('#$id').show('slow');
					} else {
						$('#s-$id').toggleClass('ui-icon-triangle-1-e');
						$('#s-$id').toggleClass('ui-icon-triangle-1-s');
						$('#$id').hide('slow');
					}
					return false;
				});
				</script>";
			}
			else {
				$return .= '<li>'.dwho_i18n::babelfish($v).'</li>';
			}
		}
		$return .= '</ul>';
		$return .= '</div>';

		return($return);
	}

	public static function has($type) {
		if (isset(self::${$type}) === true && ($self = &self::${ $type}) === false){
			return(false);
		} elseif (empty($self) === true) {
			return(false);
		}

		return(true);
	}

	public static function get($type) {
		if (isset(self::${$type}) === false || ($self = &self::${$type}) === false) {
			return(null);
		}

		return($self);
	}

	public static function get_bloc($type,$bloc) {
		if (($self = &self::get($type)) === false
		|| isset($self[$bloc]) === false) {
			$_sess = $_SESSION['_report_bloc_export'];
			if (isset($_sess[$type]) === true
			&& isset($_sess[$type][$bloc]) === true) {
				return($_sess[$type][$bloc]);
			}

			return(false);
		}

		return($self[$bloc]);
	}

	public static function encode() {
		$listtype = get_class_vars('dwho_report');
		$listtype = array_keys($listtype);

		$rs = array();
		for ($i=0;$i<count($listtype);$i++) {
			$type = $listtype[$i];
			if (self::has($type) === false) {
				continue;
			}
			$rs[$type] = self::get($type);
		}
		return($rs);
	}

	public static function decode() {
		if (isset($_SESSION['_report']) === false
		|| is_array($_SESSION['_report']) === false
		|| empty($_SESSION['_report']) === true) {
			return(null);
		}

		$listtype = get_class_vars('dwho_report');
		$arr = $_SESSION['_report'];

		$_SESSION['_report_bloc_export'] = array();

		foreach($arr as $type => $value) {
			if (isset($listtype[$type]) === false) {
				continue;
			}
			foreach($value as $k => $v) {
				if (is_string($k) === true
				&& is_array($v) === true) {
					$_SESSION['_report_bloc_export'][$type][$k] = $v;
					$key = base64_decode($k);
					foreach($v as $submessage)
					self::push($type,$submessage,$key);
				} else {
					self::push($type,$v);
				}
			}
		}

		$_SESSION['_report'] = array();
	}
}

?>