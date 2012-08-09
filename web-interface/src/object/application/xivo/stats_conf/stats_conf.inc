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

dwho_file::required(array(XIVO_PATH_OBJECT,'application','xivo.inc'),true);

class xivo_application_xivo_object_stats_conf extends xivo_application_xivo_object_abstract
{
	var $_stats_conf		= false;
	var $_queuefeatures		= false;
	var $_groupfeatures		= false;
	var $_agentfeatures		= false;
	var $_userfeatures		= false;
	var $_incall			= false;
	var $_stats_conf_queue	= false;
	var $_stats_conf_group	= false;
	var $_stats_conf_agent	= false;
	var $_stats_conf_user	= false;
	var $_stats_conf_incall	= false;
	var $_stats_conf_xivouser	= false;

	public function __construct(&$xobj,&$dso,$param=null,$components=true)
	{
		parent::__construct(&$xobj);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_stats_conf = &$this->_xobj->get_module('stats_conf')) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	public function update_date_genercache($id)
	{
		return($this->_stats_conf->update_date_genercache($id));
	}

	public function load_components()
	{
		$this->_components = true;

		if(($_SRE = &dwho_gct::get('xivo_service')) === false
		|| ($this->_queuefeatures = &$_SRE->get_module('ipbx','queuefeatures')) === false
		|| ($this->_groupfeatures = &$_SRE->get_module('ipbx','groupfeatures')) === false
		|| ($this->_agentfeatures = &$_SRE->get_module('ipbx','agentfeatures')) === false
		|| ($this->_userfeatures = &$_SRE->get_module('ipbx','userfeatures')) === false
		|| ($this->_incall = &$_SRE->get_module('ipbx','incall')) === false
		|| ($this->_stats_conf_queue = &$this->_xobj->get_module('stats_conf_queue')) === false
		|| ($this->_stats_conf_group = &$this->_xobj->get_module('stats_conf_group')) === false
		|| ($this->_stats_conf_agent = &$this->_xobj->get_module('stats_conf_agent')) === false
		|| ($this->_stats_conf_user = &$this->_xobj->get_module('stats_conf_user')) === false
		|| ($this->_stats_conf_incall = &$this->_xobj->get_module('stats_conf_incall')) === false
		|| ($this->_stats_conf_xivouser = &$this->_xobj->get_module('stats_conf_xivouser')) === false)
			return(false);

		return(true);
	}

	public function get($id,$disable=null)
	{
		if(($r = $this->_dso->get($id)) === false)
			return(false);

		if(empty($r) === true)
			return(false);

		$this->_info['stats_conf'] = $this->_stats_conf->_prepare($r);

		#$this->_get_incall();
		$this->_get_queue();
		#$this->_get_group();
		$this->_get_agent();
		#$this->_get_user();
		$this->_get_xivouser();

		return($this->_info);
	}

	public function get_nb($arr=null,$disable=null)
	{
		return($this->_stats_conf->get_nb($arr,$disable));
	}

	private function _get_incall()
	{
		$this->_info['incall'] = false;
		$this->_origin['incall'] = false;

		$where = array();
		$where['stats_conf_id'] = (int) $this->_info['stats_conf']['id'];

		if($this->_stats_conf_incall === false
		|| ($rs = $this->_stats_conf_incall->get_all_where($where)) === false)
			return(false);

		$tmp = array();
		foreach($rs as $qid)
			array_push($tmp,$qid['incall_id']);

		if($this->_incall === false
		|| ($this->_info['incall'] = $this->_incall->get_all_wherein('id',$tmp)) === false
		|| empty($this->_info['incall']) === true)
			return(false);

		return($this->_info['incall']);
	}

	private function _get_queue()
	{
		$this->_info['queue'] = false;
		$this->_origin['queue'] = false;

		$where = array();
		$where['stats_conf_id'] = (int) $this->_info['stats_conf']['id'];

		if($this->_stats_conf_queue === false
		|| ($rs = $this->_stats_conf_queue->get_all_where($where)) === false)
			return(false);

		$tmp = array();
		$scq = array();
		foreach($rs as $qid)
		{
			array_push($tmp,$qid['queuefeatures_id']);
			$scq[$qid['queuefeatures_id']] = $qid['qos'];
		}

		if($this->_queuefeatures === false
		|| ($this->_info['queue'] = $this->_queuefeatures->get_all_wherein('id',$tmp,array('name' => SORT_ASC))) === false
		|| empty($this->_info['queue']) === true)
			return(false);

		$info = &$this->_info['queue'];
		foreach($info as &$q)
			$q['stats_qos'] = (int) $scq[$q['id']];

		return($this->_info['queue']);
	}

	private function _get_group()
	{
		$this->_info['group'] = false;
		$this->_origin['group'] = false;

		$where = array();
		$where['stats_conf_id'] = (int) $this->_info['stats_conf']['id'];

		if($this->_stats_conf_group === false
		|| ($rs = $this->_stats_conf_group->get_all_where($where)) === false)
			return(false);

		$tmp = array();
		$scq = array();
		foreach($rs as $qid)
		{
			array_push($tmp,$qid['groupfeatures_id']);
			$scq[$qid['groupfeatures_id']] = $qid['qos'];
		}

		if($this->_groupfeatures === false
		|| ($this->_info['group'] = $this->_groupfeatures->get_all_wherein('id',$tmp,array('name' => SORT_ASC))) === false
		|| empty($this->_info['group']) === true)
			return(false);

		$info = &$this->_info['group'];
		foreach($info as &$q)
			$q['stats_qos'] = (int) $scq[$q['id']];

		return($this->_info['group']);
	}

	private function _get_agent()
	{
		$this->_info['agent'] = false;
		$this->_origin['agent'] = false;

		$where = array();
		$where['stats_conf_id'] = (int) $this->_info['stats_conf']['id'];

		if($this->_stats_conf_agent === false
		|| ($rs = $this->_stats_conf_agent->get_all_where($where)) === false)
			return(false);

		$tmp = array();
		foreach($rs as $qid)
			array_push($tmp,$qid['agentfeatures_id']);

		$order = array();
		$order['lastname'] = SORT_ASC;
		$order['firstname'] = SORT_ASC;

		if($this->_agentfeatures === false
		|| ($this->_info['agent'] = $this->_agentfeatures->get_all_wherein('id',$tmp,$order)) === false
		|| empty($this->_info['agent']) === true)
			return(false);

		return($this->_info['agent']);
	}

	private function _get_user()
	{
		$this->_info['user'] = false;
		$this->_origin['user'] = false;

		$where = array();
		$where['stats_conf_id'] = (int) $this->_info['stats_conf']['id'];

		if($this->_stats_conf_user === false
		|| ($rs = $this->_stats_conf_user->get_all_where($where)) === false)
			return(false);

		$tmp = array();
		foreach($rs as $qid)
			array_push($tmp,$qid['userfeatures_id']);

		$order = array();
		$order['lastname'] = SORT_ASC;
		$order['firstname'] = SORT_ASC;

		if($this->_userfeatures === false
		|| ($this->_info['user'] = $this->_userfeatures->get_all_wherein('id',$tmp,$order)) === false
		|| empty($this->_info['user']) === true)
			return(false);

		return($this->_info['user']);
	}

	private function _get_xivouser()
	{
		$this->_info['xivouser'] = false;
		$this->_origin['xivouser'] = false;

		$where = array();
		$where['stats_conf_id'] = (int) $this->_info['stats_conf']['id'];

		if($this->_stats_conf_xivouser === false
		|| ($rs = $this->_stats_conf_xivouser->get_all_where($where)) === false)
			return(false);

		$tmp = array();
		foreach($rs as $qid)
			array_push($tmp,$qid['user_id']);

		$_USR = &dwho_gct::get('_USR');

		if($_USR === false
		|| ($this->_info['xivouser'] = $_USR->get_all_wherein('id',$tmp)) === false
		|| empty($this->_info['xivouser']) === true)
			return(false);

		return($this->_info['xivouser']);
	}

	public function get_elements()
	{
		$r = array();
		$r['stats_conf'] = $this->_stats_conf->get_element();

		return($r);
	}

	public function get_stats_conf_search($search,$disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_stats_conf('search',$search,$disable,$order,$limit,$assoc));
	}

	public function get_stats_conf_list($disable=null,$order=null,$limit=null,$assoc=false,$xivouser=false)
	{
		return($this->_get_stats_conf('list',null,$disable,$order,$limit,$assoc,$xivouser));
	}

	private function _get_stats_conf($action,$search='',$disable=null,$order=null,$limit=null,$assoc=false,$xivouser=false)
	{
		$search = strval($search);

		switch($action)
		{
			case 'search':
				$rs = $this->_dso->search($search,$disable,$order,$limit);
				break;
			case 'list':
			default:
				$rs = $this->_dso->get_all($disable,$order,$limit,null,$xivouser);
		}

		if($rs === false
		|| ($nb = count($rs)) === 0)
			return(false);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$r[$i] = $rs[$i];
			$ref = &$r[$i];
			$ref = $this->_stats_conf->_prepare($ref);
		}

		if(empty($r) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($r));

		return($r);
	}

	public function set_add($arr)
	{
		return($this->_set('add',$arr));
	}

	public function set_edit($arr)
	{
		if(empty($this->_info) === true)
			return(false);

		return($this->_set('edit',$arr));
	}

	private  function _set($action,$arr)
	{
		$this->_reset();

		if(($action !== 'add' && $action !== 'edit') === true
		|| dwho_issa('stats_conf',$arr) === false)
			return(false);

		$this->set_stats_conf($arr['stats_conf']);

		if (dwho_issa('incall',$arr) === true)
			$this->set_incall($arr['incall']);

		if (dwho_issa('queue',$arr) === true)
		{
			$this->set_queue($arr['queue']);
			$this->set_queue_qos($arr['queue_qos']);
		}

		if (dwho_issa('group',$arr) === true)
		{
			$this->set_group($arr['group']);
			$this->set_group_qos($arr['group_qos']);
		}

		if (dwho_issa('agent',$arr) === true)
			$this->set_agent($arr['agent']);

		if (dwho_issa('user',$arr) === true)
			$this->set_user($arr['user']);

		if (dwho_issa('xivouser',$arr) === true)
			$this->set_xivouser($arr['xivouser']);

		return(($this->get_errnb() < 1));
	}

	public function set_stats_conf($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('stats_conf',null);
			$this->_set_error('stats_conf','invalid data');
			return(false);
		}

		$arr['disable'] = false;

		if(($rs = $this->_stats_conf->chk_values($arr)) === false)
		{
			$this->_set_result('stats_conf',$this->_stats_conf->get_filter_result());
			$this->_set_error('stats_conf',$this->_stats_conf->get_filter_error());
			return(false);
		}

		$this->_set_result('stats_conf',$rs);

		return(true);
	}

	private function set_incall($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('incall',null);
			$this->_set_error('incall','invalid data');
			return(false);
		}

		$error = $reslist = array();
		$errnb = 0;

		for($i = 0;$i < count($arr);$i++)
		{
			$ref = &$arr[$i];
			if($this->_incall->get($ref) === false)
			{
				$errnb++;
				$error[$i] = 'bad_incall';
			}
			else
			{
				$rs['id'] = (int) $ref;
				array_push($reslist,$rs);
			}
		}
		$this->_set_result('incall',$reslist);

		if ($errnb >> 0)
		{
			$this->_set_error('incall',$error);
			return(false);
		}

		return(true);
	}

	private function set_queue($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('queue',null);
			$this->_set_error('queue','invalid data');
			return(false);
		}

		$error = $reslist = array();
		$errnb = 0;

		for($i = 0;$i < count($arr);$i++)
		{
			$ref = &$arr[$i];
			if($this->_queuefeatures->get($ref) === false)
			{
				$errnb++;
				$error[$i] = 'bad_queue';
			}
			else
			{
				$rs['id'] = (int) $ref;
				array_push($reslist,$rs);
			}
		}
		$this->_set_result('queue',$reslist);

		if ($errnb >> 0)
		{
			$this->_set_error('queue',$error);
			return(false);
		}

		return(true);
	}

	private function set_queue_qos($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('queue_qos',null);
			$this->_set_error('queue_qos','invalid data');
			return(false);
		}
		$this->_set_result('queue_qos',$arr);

		return(true);
	}

	private function set_group_qos($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('group_qos',null);
			$this->_set_error('group_qos','invalid data');
			return(false);
		}
		$this->_set_result('group_qos',$arr);

		return(true);
	}

	private function set_group($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('group',null);
			$this->_set_error('group','invalid data');
			return(false);
		}

		$error = $reslist = array();
		$errnb = 0;

		for($i = 0;$i < count($arr);$i++)
		{
			$ref = &$arr[$i];
			if($this->_groupfeatures->get($ref) === false)
			{
				$errnb++;
				$error[$i] = 'bad_group';
			}
			else
			{
				$rs['id'] = (int) $ref;
				array_push($reslist,$rs);
			}
		}
		$this->_set_result('group',$reslist);

		if ($errnb >> 0)
		{
			$this->_set_error('group',$error);
			return(false);
		}

		return(true);
	}

	private function set_agent($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('agent',null);
			$this->_set_error('agent','invalid data');
			return(false);
		}

		$error = $reslist = array();
		$errnb = 0;

		for($i = 0;$i < count($arr);$i++)
		{
			$ref = &$arr[$i];
			if($this->_agentfeatures->get($ref) === false)
			{
				$errnb++;
				$error[$i] = 'bad_agent';
			}
			else
			{
				$rs['id'] = (int) $ref;
				array_push($reslist,$rs);
			}
		}
		$this->_set_result('agent',$reslist);

		if ($errnb >> 0)
		{
			$this->_set_error('agent',$error);
			return(false);
		}

		return(true);
	}

	private function set_user($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('user',null);
			$this->_set_error('user','invalid data');
			return(false);
		}

		$error = $reslist = array();
		$errnb = 0;

		for($i = 0;$i < count($arr);$i++)
		{
			$ref = &$arr[$i];
			if($this->_userfeatures->get($ref) === false)
			{
				$errnb++;
				$error[$i] = 'bad_user';
			}
			else
			{
				$rs['id'] = (int) $ref;
				array_push($reslist,$rs);
			}
		}
		$this->_set_result('user',$reslist);

		if ($errnb >> 0)
		{
			$this->_set_error('user',$error);
			return(false);
		}

		return(true);
	}

	private function set_xivouser($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('xivouser',null);
			$this->_set_error('xivouser','invalid data');
			return(false);
		}

		$_USR = &dwho_gct::get('_USR');

		$error = $reslist = array();
		$errnb = 0;

		for($i = 0;$i < count($arr);$i++)
		{
			$ref = &$arr[$i];
			if($_USR->get($ref) === false)
			{
				$errnb++;
				$error[$i] = 'bad_xivouser';
			}
			else
			{
				$rs['id'] = (int) $ref;
				array_push($reslist,$rs);
			}
		}
		$this->_set_result('xivouser',$reslist);

		if ($errnb >> 0)
		{
			$this->_set_error('xivouser',$error);
			return(false);
		}

		return(true);
	}

	public function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();
		$stats_confid = null;

		if(($this->_dso->get_stats_conf_name_already_exist($this->_result['stats_conf']['name'])) === false)
		{
			$r = false;
			$this->_set_error('stats_conf',array('name' => 'already_exist'));
		}
		elseif($this->get_errnb() > 0
		|| ($stats_confid = $this->add_stats_conf()) === false
		#|| $this->add_incall($stats_confid) === false
		|| $this->add_queue($stats_confid) === false
		#|| $this->add_group($stats_confid) === false
		|| $this->add_agent($stats_confid) === false
		#|| $this->add_user($stats_confid) === false
		|| $this->add_xivouser($stats_confid) === false)
		{
			$r = false;
			if($stats_confid !== null)
				$this->_reverse_add();
		}

		$this->_status = '';

		return($r);
	}

	public function add_stats_conf()
	{
		if(($rs = $this->get_result('stats_conf')) === null	|| $rs === false)
			return(false);

		$this->_return['stats_conf'] = $this->_stats_conf->add($rs);

		return($this->_return['stats_conf']);
	}

	private function add_incall($stats_confid)
	{
		if(($rs = $this->get_result('incall')) === null)
			return($rs);

		if($rs === false
		|| $this->_return['stats_conf'] === false)
			return(false);

		$this->_return['incall'] = array();

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_return['stats_conf'];

		foreach ($rs as $qid)
		{
			$arr['incall_id'] = (int) $qid['id'];
			if (($this->_return['incall'][$qid['id']] = $this->_stats_conf_incall->add($arr)) === false)
			{
				dwho_report::push('error','error during create stats incall');
				return(false);
			}
		}

		return($this->_return['incall']);
	}

	private function add_queue($stats_confid)
	{
		if(($rs = $this->get_result('queue')) === null
		|| ($rsqos = $this->get_result('queue_qos')) === null)
			return($rs);

		if($rs === false
		|| $rsqos === false
		|| $this->_return['stats_conf'] === false)
			return(false);

		$this->_return['queue'] = array();

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_return['stats_conf'];

		foreach ($rs as $qid)
		{
			$arr['queuefeatures_id'] = (int) $qid['id'];
			$arr['qos'] = intval($rsqos[$qid['id']]);
			if (($this->_return['queue'][$qid['id']] = $this->_stats_conf_queue->add($arr)) === false)
			{
				dwho_report::push('error','error during create stats queue');
				return(false);
			}
		}

		return($this->_return['queue']);
	}

	private function add_group($stats_confid)
	{
		if(($rs = $this->get_result('group')) === null
		|| ($rsqos = $this->get_result('group_qos')) === null)
			return($rs);

		if($rs === false
		|| $rsqos === false
		|| $this->_return['stats_conf'] === false)
			return(false);

		$this->_return['group'] = array();

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_return['stats_conf'];

		foreach ($rs as $qid)
		{
			$arr['groupfeatures_id'] = (int) $qid['id'];
			$arr['qos'] = (int) ($rsqos[$arr['groupfeatures_id']]);
			if (($this->_return['group'][$qid['id']] = $this->_stats_conf_group->add($arr)) === false)
			{
				dwho_report::push('error','error during create stats group');
				return(false);
			}
		}

		return($this->_return['group']);
	}

	private function add_agent($stats_confid)
	{
		if(($rs = $this->get_result('agent')) === null)
			return($rs);

		if($rs === false
		|| $this->_return['stats_conf'] === false)
			return(false);

		$this->_return['agent'] = array();

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_return['stats_conf'];

		foreach ($rs as $qid)
		{
			$arr['agentfeatures_id'] = (int) $qid['id'];
			if (($this->_return['agent'][$qid['id']] = $this->_stats_conf_agent->add($arr)) === false)
			{
				dwho_report::push('error','error during create stats agent');
				return(false);
			}
		}

		return($this->_return['agent']);
	}

	private function add_user($stats_confid)
	{
		if(($rs = $this->get_result('user')) === null)
			return($rs);

		if($rs === false
		|| $this->_return['stats_conf'] === false)
			return(false);

		$this->_return['user'] = array();

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_return['stats_conf'];

		foreach ($rs as $qid)
		{
			$arr['userfeatures_id'] = (int) $qid['id'];
			if (($this->_return['user'][$qid['id']] = $this->_stats_conf_user->add($arr)) === false)
			{
				dwho_report::push('error','error during create stats user');
				return(false);
			}
		}

		return($this->_return['user']);
	}

	private function add_xivouser($stats_confid)
	{
		if(($rs = $this->get_result('xivouser')) === null)
			return($rs);

		if($rs === false
		|| $this->_return['stats_conf'] === false)
			return(false);

		$this->_return['xivouser'] = array();

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_return['stats_conf'];

		foreach ($rs as $qid)
		{
			$arr['user_id'] = (int) $qid['id'];
			if (($this->_return['xivouser'][$qid['id']] = $this->_stats_conf_xivouser->add($arr)) === false)
			{
				dwho_report::push('error','error during create stats xivouser');
				return(false);
			}
		}

		return($this->_return['xivouser']);
	}

	function _reverse_add()
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'add'
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'stats_conf':
					$this->_stats_conf->delete($val);
					break;
				case 'incall':
					if(is_array($val) === false)
						continue;

					foreach($val as $v)
						$this->_stats_conf_incall->delete($v);
					break;
				case 'queue':
					if(is_array($val) === false)
						continue;

					foreach($val as $v)
						$this->_stats_conf_queue->delete($v);
					break;
				case 'group':
					if(is_array($val) === false)
						continue;

					foreach($val as $v)
						$this->_stats_conf_group->delete($v);
					break;
				case 'agent':
					if(is_array($val) === false)
						continue;

					foreach($val as $v)
						$this->_stats_conf_agent->delete($v);
					break;
				case 'user':
					if(is_array($val) === false)
						continue;

					foreach($val as $v)
						$this->_stats_conf_user->delete($v);
					break;
				case 'xivouser':
					if(is_array($val) === false)
						continue;

					foreach($val as $v)
						$this->_stats_conf_xivouser->delete($v);
					break;
			}
		}

		return(true);
	}

	public function edit()
	{
		$r = true;

		$this->_status = 'edit';
		$this->_return = array();

		if($this->get_errnb() > 0
		|| $this->edit_stats_conf() === false
		#|| $this->edit_incall() === false
		|| $this->edit_queue() === false
		#|| $this->edit_group() === false
		|| $this->_edit_agent() === false
		#|| $this->edit_user() === false
		|| $this->edit_xivouser() === false)
		{
			$r = false;
			$this->_reverse_edit();
		}

		$this->_status = '';

		return($r);
	}

	public function edit_stats_conf()
	{
		if(dwho_issa('stats_conf',$this->_info) === false
		|| ($rs = $this->get_result('stats_conf')) === null
		|| $rs === false)
			return(false);

		if (($return = $this->_stats_conf->edit($this->_info['stats_conf']['id'],$rs)) === false)
			return(false);

		$this->_return['stats_conf'] = (int) $this->_info['stats_conf']['id'];

		return($return);
	}

	private function edit_incall()
	{
		if ($this->_status === 'edit'
		&& $this->_info['incall'] === false
		&& $this->get_result('incall') === null)
			return(true);
		elseif($this->_info['incall'] === false)
			return($this->add_incall());

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_return['stats_conf'];
		$this->_stats_conf_incall->delete_where($arr);

		return($this->add_incall());
	}

	private function edit_queue()
	{
		if ($this->_status === 'edit'
		&& $this->_info['queue'] === false
		&& $this->get_result('queue') === null)
			return(true);
		elseif($this->_info['queue'] === false)
			return($this->add_queue());

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_return['stats_conf'];
		$this->_stats_conf_queue->delete_where($arr);

		return($this->add_queue());
	}

	private function edit_group()
	{
		if ($this->_status === 'edit'
		&& $this->_info['group'] === false
		&& $this->get_result('group') === null)
			return(true);
		elseif($this->_info['group'] === false)
			return($this->add_group());

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_return['stats_conf'];
		$this->_stats_conf_group->delete_where($arr);

		return($this->add_group());
	}

	private function _edit_agent()
	{
		if ($this->_status === 'edit'
		&& $this->_info['agent'] === false
		&& $this->get_result('agent') === null)
			return(true);
		elseif($this->_info['agent'] === false)
			return($this->add_agent());

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_return['stats_conf'];
		$this->_stats_conf_agent->delete_where($arr);

		return($this->add_agent());
	}

	private function edit_user()
	{
		if ($this->_status === 'edit'
		&& $this->_info['user'] === false
		&& $this->get_result('user') === null)
			return(true);
		elseif($this->_info['user'] === false)
			return($this->add_user());

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_return['stats_conf'];
		$this->_stats_conf_user->delete_where($arr);

		return($this->add_user());
	}

	private function edit_xivouser()
	{
		if ($this->_status === 'edit'
		&& $this->_info['xivouser'] === false
		&& $this->get_result('xivouser') === null)
			return(true);
		elseif($this->_info['xivouser'] === false)
			return($this->add_xivouser());

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_return['stats_conf'];
		$this->_stats_conf_xivouser->delete_where($arr);

		return($this->add_xivouser());
	}

	private function _reverse_edit()
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'edit'
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		return;

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'stats_conf':
					if(isset($this->_origin['stats_conf']) === false
					|| $this->_origin['stats_conf'] === false)
						$this->delete();
					else
						$this->_stats_conf->edit_origin($this->_origin['stats_conf']);
					break;
			}
		}

		return(true);
	}

	public function delete()
	{
		$r = true;

		$this->_status = 'delete';
		$this->_return = array();

		if($this->_delete_stats_conf() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	public function delete_all()
	{
		return($this->_dso->delete_all());
	}

	private function _delete_stats_conf()
	{
		if(dwho_issa('stats_conf',$this->_info) === false)
			return(false);

		$r = $this->_stats_conf->delete($this->_info['stats_conf']['id']);

		$arr = array();
		$arr['stats_conf_id'] = (int) $this->_info['stats_conf']['id'];

		#$this->_stats_conf_incall->delete_where($arr);
		$this->_stats_conf_queue->delete_where($arr);
		#$this->_stats_conf_group->delete_where($arr);
		$this->_stats_conf_agent->delete_where($arr);
		#$this->_stats_conf_user->delete_where($arr);
		$this->_stats_conf_xivouser->delete_where($arr);

		if($this->_status === 'delete')
			$this->_return['stats_conf'] = $r;

		return($r);
	}

	public function enable()
	{
		$r = true;

		$this->_status = 'enable';
		$this->_return = array();

		if($this->enable_stats_conf() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	public function disable()
	{
		$r = true;

		$this->_status = 'disable';
		$this->_return = array();

		if($this->disable_stats_conf() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	public function enable_stats_conf()
	{
		return($this->_enable_disable_stats_conf(false));
	}

	public function disable_stats_conf()
	{
		return($this->_enable_disable_stats_conf(true));
	}

	public function _enable_disable_stats_conf($disable=false)
	{
		if(dwho_issa('stats_conf',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_stats_conf->enable($this->_info['stats_conf']['id']);
		else
			$r = $this->_stats_conf->disable($this->_info['stats_conf']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['stats_conf'] = $r;

		return($r);
	}

	public function add_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| $this->set_add($data) === false
		|| $this->add() === false)
			return(false);

		return(true);
	}

	public function edit_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| $this->set_edit($data) === false
		|| $this->edit() === false)
			return(false);

		return(true);
	}
}

?>
