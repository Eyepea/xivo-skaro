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

$apppeer = &$ipbx->get_application('dundimapping');
$modctx  = &$ipbx->get_module('context');
$apptrunk = &$ipbx->get_application('trunk');

function ontype($trunk) {
	return $trunk['type'] == 'user' || $trunk['type'] == 'friend';
}
$trunks = array_filter(
	$apptrunk->get_trunks_list(array('sip','iax')),
	"ontype"
);

$act 		  = isset($_QR['act']) === true ? $_QR['act'] : '';
$page 		= isset($_QR['page']) === true ? dwho_uint($_QR['page'],1) : 1;
$search 	= isset($_QR['search']) === true ? strval($_QR['search']) : '';
$context 	= isset($_QR['context']) === true ? strval($_QR['context']) : '';

//$_TPL->load_i18n_file('tpl/www/bloc/service/ipbx/asterisk/dundi/mappings/add.i18n', 'global');

// default view mode == list
$param = array('act' => 'list');

if($search !== '')
	$param['search'] = $search;
else if($context !== '')
	$param['context'] = $context;

$contexts = false;
$error    = false;

switch($act)
{
	case 'add':
		$fm_save = true;

		if(isset($_QR['fm_send']) 	 === true 
		&& dwho_issa('dundimapping', $_QR) === true)
		{	
			// save item
			if($apppeer->set_add($_QR) === true
			&& $apppeer->add() === true)
				$_QRY->go($_TPL->url('service/ipbx/dundi/mappings'), $param);
			
			$error = $apppeer->get_error();
			$_TPL->set_var('info', $_QR);
			$fm_save = false;
		}

		$_TPL->set_var('contexts', $modctx->get_all());
		break;

	case 'edit':
		$fm_save  = true;

		if(isset($_QR['id']) === false || ($info = $apppeer->get($_QR['id'])) === false)
		{ $_QRY->go($_TPL->url('service/ipbx/dundi/mappings'), $param); }
		
		$act = 'edit';
		if(isset($_QR['fm_send']) 		=== true
		&& dwho_issa('dundimapping', $_QR) 	=== true)
		{
			if($apppeer->set_edit($_QR) === true
			&& $apppeer->edit($_QR['id']) === true)
				$_QRY->go($_TPL->url('service/ipbx/dundi/mappings'), $param);

			$fm_save = false;

			// on update error
			$error = $apppeer->get_error();
			$info  = $_QR;
			$info['dundimapping']['id'] = $_QR['id'];
		}

		$_TPL->set_var('id'      , $info['dundimapping']['id']);
		$_TPL->set_var('info'    , $info);
		$_TPL->set_var('contexts', $modctx->get_all());
		$_TPL->set_var('fm_save' , $fm_save);
		break;

	case 'delete':
		if(isset($_QR['id']))
			$apppeer->delete($_QR['id']);

		$_QRY->go($_TPL->url('service/ipbx/dundi/mappings'),$param);
		break;

	case 'deletes':
		// delete multiple items
		$param['page'] = $page;

		if(($values = dwho_issa_val('mappings',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/dundi/mappings'),$param);

		$nb = count($values);
		for($i = 0; $i < $nb; $i++)
			$apppeer->delete($values[$i]);

		$_QRY->go($_TPL->url('service/ipbx/dundi/mappings'), $param);
		break;

	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('mappings',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/dundi/mappings'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($act === 'disables')
				$apppeer->disable($values[$i]);
			else
				$apppeer->enable($values[$i]);
		}

		$_QRY->go($_TPL->url('service/ipbx/dundi/mappings'),$param);
		break;

	case 'list':
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$order = array();
		$order['name'] = SORT_ASC;

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		$list  = $apppeer->get_dundimapping_list(null,$order,$limit);
		$total = $apppeer->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('service/ipbx/dundi/mappings'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search'	, $search);
}

$_TPL->set_var('act'      , $act);
$_TPL->set_var('error'    , $error);
$_TPL->set_var('element'  , $apppeer->get_elements());
$_TPL->set_var('trunks'   , $trunks);

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/uri.js');
$dhtml->set_js('js/dwho/http.js');
$dhtml->set_js('js/dwho/submenu.js');

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());
$menu->set_toolbar('toolbar/service/ipbx/'.$ipbx->get_name().'/dundi/mappings');

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/dundi/mappings/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
