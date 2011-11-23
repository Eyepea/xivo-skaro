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

$array = array();

$array['element'] = array();

$array['element']['name'] = array();
$array['element']['name']['default'] = '';

$array['element']['timezone'] = array();
$array['element']['timezone']['default'] = '';

$array['element']['hour_start'] = array();
$array['element']['hour_start']['default'] = '00:00';

$array['element']['hour_end'] = array();
$array['element']['hour_end']['default'] = '00:00';

$_SRE = &dwho_gct::get('xivo_service');
$ipbx = &$_SRE->get('ipbx');
if (($appqueue_log = &$ipbx->get_application('queue_log')) === false
|| ($interval = $appqueue_log->get_min_and_max_time()) === false)
	$dbegcachedefault = null;
else
	$dbegcachedefault = strtotime($interval['min']);

$array['element']['dbegcache'] = array();
$array['element']['dbegcache']['default'] = date('Y-m',$dbegcachedefault);

$array['element']['dendcache'] = array();
$array['element']['dendcache']['default'] = 0;

$array['element']['default_delta'] = array();
$array['element']['default_delta']['default'] = 0;

$array['element']['workhour']['h'] = array();
$array['element']['workhour']['h']['value'] = array('00','01','02','03','04','05','06',
					      '07','08','09',10,11,12,13,14,15,16,17,18,19,20,21,22,23);
$array['element']['workhour']['h']['default'] = '00';

$array['element']['workhour']['m'] = array();
$array['element']['workhour']['m']['value'] = array('00',15,30,45);
$array['element']['workhour']['m']['default'] = '00';

$array['element']['monday'] = array();
$array['element']['monday']['default'] = 0;

$array['element']['tuesday'] = array();
$array['element']['tuesday']['default'] = 0;

$array['element']['wednesday'] = array();
$array['element']['wednesday']['default'] = 0;

$array['element']['thursday'] = array();
$array['element']['thursday']['default'] = 0;

$array['element']['friday'] = array();
$array['element']['friday']['default'] = 0;

$array['element']['saturday'] = array();
$array['element']['saturday']['default'] = 0;

$array['element']['sunday'] = array();
$array['element']['sunday']['default'] = 0;

$array['element']['period1'] = array();
$array['element']['period1']['default'] = '0-20';

$array['element']['period2'] = array();
$array['element']['period2']['default'] = '';

$array['element']['period3'] = array();
$array['element']['period3']['default'] = '';

$array['element']['period4'] = array();
$array['element']['period4']['default'] = '';

$array['element']['period5'] = array();
$array['element']['period5']['default'] = '';

$array['element']['homepage'] = array();
$array['element']['homepage']['value'] = array(0,1);
$array['element']['homepage']['default'] = 0;
$array['element']['homepage']['set'] = true;

$array['element']['disable'] = array();
$array['element']['disable']['value'] = array(0,1);
$array['element']['disable']['default'] = 0;
$array['element']['disable']['set'] = true;

$array['element']['description'] = array();
$array['element']['description']['default'] = '';


$array['filter'] = array();
$array['filter']['name'] = array('regexp' => '/^[a-z0-9_\.-]+$/','minlen' => 1,'maxlen' => 64);
$array['filter']['timezone'] = array('set' => false,'chk' => 2);
$array['filter']['dbegcache'] = array('set' => true,'regexp' => '/^([0-9]{4})-([0-9]{2})$/');
$array['filter']['dendcache'] = array('set' => true,'regexp' => '/^(([0-9]{4})-([0-9]{2}))|0$/');
$array['filter']['hour_start'] = array('set' => true,'regexp' => '/^(([0-1]?[0-9])|([2][0-3])):([0-5]?[0-9])?$/');
$array['filter']['hour_end'] = array('set' => true,'regexp' => '/^(([0-1]?[0-9])|([2][0-3])):([0-5]?[0-9])?$/');
$array['filter']['default_delta'] = array('set' => true,'regexp' => '/^(-([0-9]{1,3}) ([day|week|month])s?)|0$/');
$array['filter']['monday'] = array('bool' => true);
$array['filter']['tuesday'] = array('bool' => true);
$array['filter']['wednesday'] = array('bool' => true);
$array['filter']['thursday'] = array('bool' => true);
$array['filter']['friday'] = array('bool' => true);
$array['filter']['saturday'] = array('bool' => true);
$array['filter']['sunday'] = array('bool' => true);
$array['filter']['period1'] = array('set' => true,'regexp' => '/^[0-9_><-]+$/','minlen' => 1,'maxlen' => 16);
$array['filter']['period2'] = array('set' => false,'chk' => 2,'regexp' => '/^[0-9_><-]+$/','minlen' => 1,'maxlen' => 16);
$array['filter']['period3'] = array('set' => false,'chk' => 2,'regexp' => '/^[0-9_><-]+$/','minlen' => 1,'maxlen' => 16);
$array['filter']['period4'] = array('set' => false,'chk' => 2,'regexp' => '/^[0-9_><-]+$/','minlen' => 1,'maxlen' => 16);
$array['filter']['period5'] = array('set' => false,'chk' => 2,'regexp' => '/^[0-9_><-]+$/','minlen' => 1,'maxlen' => 16);
$array['filter']['homepage'] = array('bool' => true);
$array['filter']['disable'] = array('bool' => true);
$array['filter']['description'] = array('set' => false,'chk' => 2,'maxlen' => 1000,'cast' => 'sgraph_crlf_tab','eol' => true);

?>
