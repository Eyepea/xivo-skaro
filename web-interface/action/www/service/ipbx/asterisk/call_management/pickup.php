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

$act = isset($_QR['act']) === true ? $_QR['act'] : '';
$page = isset($_QR['page']) === true ? dwho_uint($_QR['page'],1) : 1;

$apppickup = &$ipbx->get_application('pickup');
$info = array();

$param = array();
$param['act'] = 'list';


switch($act)
{
	case 'add':
		$fm_save = $error = null;
		$result = array();

		if(isset($_QR['fm_send']) === true && dwho_issa('pickup',$_QR) === true)
		{
			$_QR['pickup']['members'] = array();
			foreach(array('group','queue','user') as $type)
				if(array_key_exists("member-".$type."s", $_QR))
					foreach($_QR["member-".$type."s"] as $mbid)
						$_QR['pickup']['members'][] = array(
							'category'   => 'member', 
							'membertype' => $type, 
							'memberid'   => $mbid
						);

			foreach(array('group','queue','user') as $type)
				if(array_key_exists("pickup-".$type."s", $_QR))
					foreach($_QR["pickup-".$type."s"] as $mbid)
						$_QR['pickup']['members'][] = array(
							'category'   => 'pickup',
							'membertype' => $type,
							'memberid'   => $mbid
						);

			if($apppickup->set_add($_QR) === false
			|| $apppickup->add() === false)
			{
				$fm_save = false;
				$result  = $apppickup->get_result_for_display();
				$error   = $apppickup->get_error();
			}
			else
			{
				$ipbx->discuss(array('sip reload'));
				$_QRY->go($_TPL->url('service/ipbx/call_management/pickup'),$param);
			}
		}

		$dtsource = array(
			'groups' => array(),
			'users'  => array(),
			'queues' => array()
		);

		$appgroup = &$ipbx->get_application('group');
		if(($groups = $appgroup->get_groups_list()) !== false)			
			foreach($groups as $_grp)
				$dtsource['groups'][$_grp['id']] = $_grp;

		$appuser = &$ipbx->get_application('user');
		if(($users = $appuser->get_users_list()) !== false)
			foreach($users as $_usr)
				$dtsource['users'][$_usr['id']] = $_usr;

		$appqueue = &$ipbx->get_application('queue');
		if(($queues = $appqueue->get_queues_list()) !== false)
			foreach($queues as $_que)
				$dtsource['queues'][$_que['id']] = $_que;

		$mbsource = $dtsource;
		$members  = array('groups' => array(), 'queues' => array(), 'users' => array());
		if(array_key_exists('members',$result))
		{
			foreach($result['members'] as $_mb)
			{
				$members[$_mb['membertype'].'s'][] = $mbsource[$_mb['membertype'].'s'][$_mb['memberid']];
				unset($mbsource[$_mb['membertype'].'s'][$_mb['memberid']]);
			}
			$result['members'] = $members;
		}

		$pksource = $dtsource;
		$pickups  = array('groups' => array(), 'queues' => array(), 'users' => array());
		if(array_key_exists('pickups',$result))
		{
			foreach($result['pickups'] as $_mb)
			{
				$pickups[$_mb['membertype'].'s'][] = $pksource[$_mb['membertype'].'s'][$_mb['memberid']];
				unset($pksource[$_mb['membertype'].'s'][$_mb['memberid']]);
			}
			$result['pickups'] = $pickups;
		}

		$_TPL->set_var('info',$result);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$apppickup->get_elements());
		$_TPL->set_var('member',$mbsource);
		$_TPL->set_var('pickup',$pksource);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_css('/extra-libs/multiselect/css/ui.multiselect.css', true);
		$dhtml->set_css('css/xivo.multiselect.css');
		$dhtml->set_js('/extra-libs/multiselect/js/plugins/localisation/jquery.localisation-min.js', true);
		$dhtml->set_js('/extra-libs/multiselect/js/plugins/scrollTo/jquery.scrollTo-min.js', true);
		$dhtml->set_js('/extra-libs/multiselect/js/ui.multiselect.js', true);

		$dhtml->set_css('css/service/ipbx/pickup.css');

		$dhtml->set_js('js/dwho/uri.js');
		$dhtml->set_js('js/dwho/http.js');
		$dhtml->set_js('js/dwho/submenu.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/pickup.js');
		break;

	case 'edit':
		if(isset($_QR['id']) === false
		|| ($info = $apppickup->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('service/ipbx/call_management/pickup'),$param);

		$result = $fm_save = $error = null;
		$return = &$info;

		if(isset($_QR['fm_send']) === true && dwho_issa('pickup',$_QR) === true)
		{
			$return = &$result;

			$_QR['pickup']['members'] = array();
			foreach(array('group','queue','user') as $type)
				foreach($_QR["member-".$type."s"] as $mbid)
					$_QR['pickup']['members'][] = array(
						'category'   => 'member', 
						'membertype' => $type, 
						'memberid'   => $mbid
					);

			foreach(array('group','queue','user') as $type)
				foreach($_QR["pickup-".$type."s"] as $mbid)
					$_QR['pickup']['members'][] = array(
						'category'   => 'pickup',
						'membertype' => $type,
						'memberid'   => $mbid
					);

			if($apppickup->set_edit($_QR) === false
			|| $apppickup->edit() === false)
			{
				$fm_save = false;
				$result = $apppickup->get_result_for_display();
				$error = $apppickup->get_error();
				$result['dialaction'] = $apppickup->get_dialaction_result();
			}
			else
			{
				$ipbx->discuss(array('sip reload'));
				$_QRY->go($_TPL->url('service/ipbx/call_management/pickup'),$param);
			}
		}

		$dtsource = array(
			'groups' => array(),
			'users'  => array(),
			'queues' => array()
		);

		$appgroup = &$ipbx->get_application('group');
		if(($groups = $appgroup->get_groups_list()) !== false)
			foreach($groups as $_grp)
				$dtsource['groups'][$_grp['id']] = $_grp;

		$appuser = &$ipbx->get_application('user');
		if(($users = $appuser->get_users_list()) !== false)
			foreach($users as $_usr)
				$dtsource['users'][$_usr['id']] = $_usr;

		$appqueue = &$ipbx->get_application('queue');
		if(($queues = $appqueue->get_queues_list()) !== false)
			foreach($queues as $_que)
				$dtsource['queues'][$_que['id']] = $_que;

		$mbsource = $dtsource;
		$members  = array('groups' => array(), 'queues' => array(), 'users' => array());
		foreach($return['members'] as $_mb)
			$members[$_mb['membertype'].'s'][] = $_mb['memberid'];
		$return['members'] = $members;

		$pksource = $dtsource;
		$pickups  = array('groups' => array(), 'queues' => array(), 'users' => array());
		foreach($return['pickups'] as $_mb)
			$pickups[$_mb['membertype'].'s'][] = $_mb['memberid'];
		$return['pickups'] = $pickups;

		$_TPL->set_var('id',$info['pickup']['id']);
		$_TPL->set_var('info',$return);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$apppickup->get_elements());
		$_TPL->set_var('member',$mbsource);
		$_TPL->set_var('pickup',$pksource);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_css('/extra-libs/multiselect/css/ui.multiselect.css', true);
		$dhtml->set_css('css/xivo.multiselect.css');
		$dhtml->set_js('/extra-libs/multiselect/js/plugins/localisation/jquery.localisation-min.js', true);
		$dhtml->set_js('/extra-libs/multiselect/js/plugins/scrollTo/jquery.scrollTo-min.js', true);
		$dhtml->set_js('/extra-libs/multiselect/js/ui.multiselect.js', true);

		$dhtml->set_css('css/service/ipbx/pickup.css');

		$dhtml->set_js('js/dwho/uri.js');
		$dhtml->set_js('js/dwho/http.js');
		$dhtml->set_js('js/dwho/submenu.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/pickup.js');
		break;

	case 'delete':
		$param['page'] = $page;

		$apppickup = &$ipbx->get_application('pickup');

		if(isset($_QR['id']) === false || $apppickup->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('service/ipbx/call_management/pickup'),$param);

		$apppickup->delete();
		$ipbx->discuss(array('sip reload'));

		$_QRY->go($_TPL->url('service/ipbx/call_management/pickup'),$param);
		break;

	case 'deletes':
		$param['page'] = $page;

		if(($values = dwho_issa_val('pickups',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/call_management/pickup'),$param);

		$apppickup = &$ipbx->get_application('pickup');

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($apppickup->get($values[$i]) !== false)
				$apppickup->delete();
		}
			
		$ipbx->discuss(array('sip reload'));
		$_QRY->go($_TPL->url('service/ipbx/call_management/pickup'),$param);
		break;

	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('pickups',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/call_management/pickup'),$param);

		$apppickup = &$ipbx->get_application('pickup');

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($apppickup->get($values[$i]) === false)
				continue;
			else if($act === 'disables')
				$apppickup->disable();
			else
				$apppickup->enable();
		}

		$ipbx->discuss(array('sip reload'));
		$_QRY->go($_TPL->url('service/ipbx/call_management/pickup'),$param);
		break;

	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$order = array();
		$order['name'] = SORT_ASC;
		$order['context'] = SORT_ASC;

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		$list = $apppickup->get_pickups_list(null,$order,$limit);
		$total = $apppickup->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('service/ipbx/call_management/pickup'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
}

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());
$menu->set_toolbar('toolbar/service/ipbx/'.$ipbx->get_name().'/call_management/pickup');

$menu = &$_TPL->get_module('menu');
$_TPL->set_var('timezones', array_keys(dwho_i18n::get_timezone_list()));
$_TPL->set_var('act',$act);
$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/call_management/pickup/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
