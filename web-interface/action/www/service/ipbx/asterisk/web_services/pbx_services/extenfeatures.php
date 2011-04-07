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

$access_category = 'pbx_services';
$access_subcategory = 'extenfeatures';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$appextenfeatures = &$ipbx->get_application('extenfeatures');

$act = $_QRY->get('act');

switch($act)
{
	case 'list':
	default:
		$act = 'list';
		
		$appfeatures = &$ipbx->get_apprealstatic('features');

		$info = array();
		$info['extenfeatures'] = $appextenfeatures->get_all_by_context();
		
		$appgeneralfeatures = &$appfeatures->get_module('general');
		$info['generalfeatures'] = $appgeneralfeatures->get_all_by_category();
		
		$appfeaturemap = &$appfeatures->get_module('featuremap');
		$info['featuremap'] = $appfeaturemap->get_all_by_category();

		$_TPL->set_var('list',$info);
}

$_TPL->set_var('act',$act);
$_TPL->set_var('sum',$_QRY->get('sum'));
$_TPL->display('/service/ipbx/'.$ipbx->get_name().'/generic');

?>
