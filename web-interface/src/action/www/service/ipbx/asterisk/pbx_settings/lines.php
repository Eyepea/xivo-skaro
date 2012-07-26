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

dwho::load_class('dwho_prefs');
$prefs = new dwho_prefs('lines');

$act     = isset($_QR['act']) === true ? $_QR['act'] : '';
$page    = dwho_uint($prefs->get('page', 1));
$search  = strval($prefs->get('search', ''));
$context = strval($prefs->get('context', ''));
$free 	 = strval($prefs->get('free', ''));
$sort    = $prefs->flipflop('sort', 'name');

$param = array();
$param['act'] = 'list';

if($search !== '')
	$param['search'] = $search;
else if($context !== '')
	$param['context'] = $context;
else if($free !== '')
	$param['free'] = $free;

$contexts = false;

switch($act)
{
	case 'add':
		if (isset($_QR['proto']) === false)
			break;
		$appline = &$ipbx->get_application('line');
		//$modpark = &$ipbx->get_module('parkinglot');

		$contexts = $appline->get_all_context();

		$result = $fm_save = $error = null;

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('protocol',$_QR) === true)
		{
			if($appline->set_add($_QR,$_QR['proto']) === false
			|| $appline->add() === false)
			{
				$fm_save = false;
				$result = $appline->get_result();
				$error = $appline->get_error();
			}
			else
				$_QRY->go($_TPL->url('service/ipbx/pbx_settings/lines'),$param);
		}

		$element = $appline->get_elements();

		// AUTOGEN name/secret
		$config  = dwho::load_init(XIVO_PATH_CONF.DWHO_SEP_DIR.'ipbx.ini');
		if (isset($config['user'],$config['user']['readonly-idpwd']))
		{
			$ro = !($config['user']['readonly-idpwd'] == 'false');
			$lol = 1;
			while ($lol === 1)
			{
				$name = $appline->gen_password(6,true);
				$lol = $appline->get_nb(array('name' => $name));
			}
			$element['protocol']['name']   = array(
				'default'  => $name,
				'readonly' => $ro,
				'class'    => 'it-'.($ro?'disabled':'enabled')
			);
			$element['protocol']['secret']   = array(
				'default'  => $appline->gen_password(6),
				'readonly' => $ro,
				'class'    => 'it-'.($ro?'disabled':'enabled')
			);
			$element['linefeatures']['number']   = array(
				'readonly' => $ro,
				'class'    => 'it-'.($ro?'disabled':'enabled')
			);
		}

		$_TPL->set_var('info',$result);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$element);
		$_TPL->set_var('context_list',$appline->get_context_list(null,null,null,false,'internal'));
		//$_TPL->set_var('parking_list', $modpark->get_all());
		$_TPL->set_var('proto',$_QR['proto']);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/dwho/submenu.js');
		$dhtml->set_js('js/utils/codeclist.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/lines.js');
		$dhtml->load_js_multiselect_files();
		break;
	case 'edit':
		$appline = &$ipbx->get_application('line');
		//$modpark = &$ipbx->get_module('parkinglot');

		if(isset($_QR['id']) === false || ($info = $appline->get($_QR['id'],null,null,true)) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/lines'),$param);

		$contexts = $appline->get_all_context();

		$fm_save = $error = null;
		$return = &$info;

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('protocol',$_QR) === true)
		{
			$_QR['linefeatures'] = $return['linefeatures'];

			if($appline->set_edit($_QR,$_QR['proto']) === false
			|| $appline->edit() === false)
			{
				$fm_save = false;
				$result = $appline->get_result();
				$error = $appline->get_error();
			}
			else
				$_QRY->go($_TPL->url('service/ipbx/pbx_settings/lines'),$param);
		}

		$element = $appline->get_elements();

		// AUTOGEN name/secret
		$config  = dwho::load_init(XIVO_PATH_CONF.DWHO_SEP_DIR.'ipbx.ini');
		if (isset($config['user'],$config['user']['readonly-idpwd']))
		{
			$ro = !($config['user']['readonly-idpwd'] == 'false');

			$element['protocol']['name']   = array(
				'readonly' => $ro,
				'class'    => 'it-'.($ro?'disabled':'enabled')
			);
			$element['protocol']['secret']   = array(
				'readonly' => $ro,
				'class'    => 'it-'.($ro?'disabled':'enabled')
			);
			$element['linefeatures']['number']   = array(
				'readonly' => $ro,
				'class'    => 'it-'.($ro?'disabled':'enabled')
			);
		}

		$_TPL->set_var('id',$info['linefeatures']['id']);
		$_TPL->set_var('info',$return);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$element);
		$_TPL->set_var('context_list',$appline->get_context_list(null,null,null,false,'internal'));
		//$_TPL->set_var('parking_list', $modpark->get_all());

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/dwho/submenu.js');
		$dhtml->set_js('js/utils/codeclist.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/lines.js');
		$dhtml->load_js_multiselect_files();
		break;
	case 'delete':
		$param['page'] = $page;

		$appline = &$ipbx->get_application('line');

		if(isset($_QR['id']) === false || $appline->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/lines'),$param);

		$appline->delete();

		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/lines'),$param);
		break;
	case 'deletes':
		$param['page'] = $page;

		if(($values = dwho_issa_val('lines',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/lines'),$param);

		$appline = &$ipbx->get_application('line');

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appline->get($values[$i]) !== false)
				$appline->delete();
		}

		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/lines'),$param);
		break;
	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('lines',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/lines'),$param);

		$appline = &$ipbx->get_application('line',null,false);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appline->get($values[$i]) === false)
				continue;
			else if($act === 'disables')
				$appline->disable();
			else
				$appline->enable();
		}

		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/lines'),$param);
		break;
	case 'list':
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$appline = &$ipbx->get_application('line');

		$contexts = $appline->get_all_context();

		$order = array();
		if($sort[1] == 'name')
			$order['name'] = $sort[0];
		else
			$order[$sort[1]] = $sort[0];

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		if($search !== '')
			$list = $appline->get_lines_search($search,'',null,null,$order,$limit);
		else if($context !== '')
			$list = $appline->get_lines_context($context,null,null,$order,$limit,false,null,$free);
		elseif($free !== '')
			$list = $appline->get_lines_list(null,null,$order,$limit,false,null,$free);
		else
			$list = $appline->get_lines_list(null,null,$order,$limit);

		$total = $appline->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/lines'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search',$search);
		$_TPL->set_var('context',$context);
		$_TPL->set_var('free',$free);
		$_TPL->set_var('sort',$sort);
}

$_TPL->set_var('act',$act);
$_TPL->set_var('contexts',$contexts);
$_TPL->set_var('frees',array(1 => 'yes',0 => 'no'));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());
$menu->set_toolbar('toolbar/service/ipbx/'.$ipbx->get_name().'/pbx_settings/lines');

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/pbx_settings/lines/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
