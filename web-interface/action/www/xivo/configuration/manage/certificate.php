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

$modcert = &$_XOBJ->get_module('certificate');

$act 		  = isset($_QR['act']) === true ? $_QR['act'] : '';
$page 		= isset($_QR['page']) === true ? dwho_uint($_QR['page'],1) : 1;
$search 	= isset($_QR['search']) === true ? strval($_QR['search']) : '';
$context 	= isset($_QR['context']) === true ? strval($_QR['context']) : '';

#$_TPL->load_i18n_file('tpl/www/bloc/service/ipbx/asterisk/dundi/peers/add.i18n', 'global');

// default view mode == list
$param = array('act' => 'list');

if($search !== '')
	$param['search'] = $search;
else if($context !== '')
	$param['context'] = $context;

$contexts = false;
$error    = false;

$language = $_TPL->_i18n->get_language();

switch($act)
{
	case 'add':
		$fm_save = true;

		if(isset($_QR['fm_send']) 	 === true)
		{	
			$now = new DateTime("now");
			$end = DateTime::createFromFormat("Y-m-d", $_QR['validity-end-format']);

			// cleanup
			$cert = array(
				'name'     => $_QR['name'],
				'password' => $_QR['password'],
				'length'   => $_QR['length'],
				'validity' => $end->diff($now)->days
			);

			if(!array_key_exists('CA', $_QR) || $_QR['CA'] != 1)
			{
				$cert['autosigned'] = $_QR['autosigned'] == 1;

				if(array_key_exists('autosigned',$_QR) && $_QR['autosigned'] != 1)
				{ $cert['ca'] = $_QR['ca_authority']; $cert['ca_password'] = $_QR['ca_password']; }
			}

			foreach($_QR['subject'] as $k => $v)
			{ $cert[$k] = $v; }

			// save item
			if(($ret = $modcert->add(array_key_exists('CA',$_QR) && $_QR['CA'] == 1, $cert)) === true)
				$_QRY->go($_TPL->url('xivo/configuration/manage/certificate'), $param);

			$error = $modcert->get_filter_error();
			$_TPL->set_var('info', $_QR);
			$_TPL->set_var('id', $_QR['name']);
			$_TPL->set_var('fm_save' , false);
		}

		function cafilter($cert)
		{
			return $cert['CA'];
		}

		$authorities = array_filter($modcert->get_all(), "cafilter");
		$_TPL->set_var('ca_authorities', $authorities);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_css('extra-libs/jquery-ui/css/ui-lightness/jquery-ui.css', true);

		$dhtml->set_js('extra-libs/jquery-ui/ui/minified/jquery.ui.datepicker.min.js', true);
		$dhtml->set_js('extra-libs/jquery-ui/ui/i18n/jquery.ui.datepicker-'.$language.'.js', true);
		$dhtml->set_js('js/xivo/configuration/manager/certificate.js');
		break;

	case 'edit':
		$_TPL->set_var('info'    , $modcert->get($_QR['id']));
		$_TPL->set_var('id'      , $_QR['id']);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/xivo/configuration/manager/certificate.js');
		break;

	case 'delete':
		if(isset($_QR['id']))
			$modcert->delete($_QR['id']);

		$_QRY->go($_TPL->url('xivo/configuration/manage/certificate'), $param);
		break;

	case 'deletes':
		// delete multiple items
		$param['page'] = $page;

		if(($values = dwho_issa_val('certificates',$_QR)) === false)
			$_QRY->go($_TPL->url('xivo/configuration/manage/certificate'), $param);

		$nb = count($values);
		for($i = 0; $i < $nb; $i++)
			$modcert->delete($values[$i]);

		$_QRY->go($_TPL->url('xivo/configuration/manage/certificate'), $param);
		break;

	case 'export':
		$pubkey = $modcert->get_pubkey($_QR['id']);

		$_TPL->set_var('name', $_QR['id']);
		$_TPL->set_var('pubkey',$pubkey);
		$_TPL->display('/bloc/xivo/configuration/manage/certificate/pubkey');

		$_QRY->go($_TPL->url('xivo/configuration/manage/certificate'), $param);
		break;

	case 'list':
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = 20;

		$order = array();
		$order['macaddr'] = SORT_ASC;

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		$list  = $modcert->get_all(null,$order,$limit);
		$total = count($list);

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('xivo/configuration/manage/certificate'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search'	, $search);
}

$_TPL->set_var('act'      , $act);
$_TPL->set_var('contexts' , $contexts);
$_TPL->set_var('error'    , $error);
$_TPL->set_var('element'  , $modcert->get_element());

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/xivo/configuration');
$menu->set_toolbar('toolbar/xivo/configuration/manage/certificate');

$_TPL->set_bloc('main','xivo/configuration/manage/certificate/'.$act);
$_TPL->set_struct('xivo/configuration');
$_TPL->display('index');

?>
