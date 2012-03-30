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

class xivo_application_xivo_object_ha extends xivo_application_xivo_object_abstract
{
	var $_sysconfd = false;
	var $_ha = false;
	var $_provdconfig = false;
	var $_ipbx = false;

	public function __construct(&$xobj)
	{
		parent::__construct(&$xobj);

		if(($this->_sysconfd = &$this->_xobj->get_module('sysconfd')) === false
		|| ($this->_ha = &$this->_xobj->get_module('ha')) === false
		|| ($this->_provdconfig = &$this->_xobj->get_application('provdconfig')) === false
		|| ($_SRE = dwho_gct::get('xivo_service')) === false
		|| ($this->_ipbx = &$_SRE->get('ipbx')) === false)
			return(false);

		return(true);
	}

	public function get()
	{
		if(($res = $this->_sysconfd->request_get('/get_ha_config')) === false
		|| is_array($res) === false)
			return(false);

		return($res);
	}

	public function get_elements()
	{
		return($this->_ha->get_element());
	}

	private function _set_check($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('ha',null);
			$this->_set_error('ha','invalid data');
			return(false);
		}

		if(($rs = $this->_ha->chk_values($arr)) === false)
		{
			$this->_set_result('ha',$this->_ha->get_filter_result());
			$this->_set_error('ha',$this->_ha->get_filter_error());
			return(false);
		}

		$this->_set_result('ha',$rs);

		return(true);
	}

	private function _set_provd_template_line($node_type, $remote_address)
	{
		$info = $this->_provdconfig->get('default');

		$rs = &$info['config'];

		switch($node_type)
		{
			case 'master':
				$rs["registrar_backup"] = $remote_address;
				$rs["proxy_backup"] = $remote_address;
				break;
			case 'slave':
				break;
			case 'disabled':
			default:
				$rs["registrar_backup"] = '';
				$rs["proxy_backup"] = '';
				break;
		}

		if($this->_provdconfig->set_edit($info,'registrar') === false
		|| $this->_provdconfig->edit() === false)
			return(false);

		return(true);
	}

	private function _set_sip_options($node_type)
	{
		$appsip = &$this->_ipbx->get_apprealstatic('sip');
		$appgeneralsip = &$appsip->get_module('general');

		$list = array();
		$list[0]['var_name'] = 'minexpiry';
		$list[1]['var_name'] = 'maxexpiry';
		$list[2]['var_name'] = 'defaultexpiry';

		switch($node_type)
		{
			case 'slave':
			case 'master':
				$list[0]['var_val'] = 20;
				$list[1]['var_val'] = 120;
				$list[2]['var_val'] = 40;
				break;
			case 'disabled':
			default:
				$list[0]['var_val'] = 60;
				$list[1]['var_val'] = 3600;
				$list[2]['var_val'] = 120;
				break;
		}

		$r = array();
		$r['result'] = array();
		$r['error'] = array();
		$err = 0;

		$nb = count($list);
		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$list[$i];

			$ref['commented'] = 0;

			if($appgeneralsip->set($ref) === false
			|| ($pre_save = $appgeneralsip->_chk_pre_save($ref)) === false
			|| ($pre_save !== 1 && $appgeneralsip->save() === false) === true) {
				$err++;
				$r['error'][$i] = $appgeneralsip->get_error();
			}
			$r['result'][$i] = $appgeneralsip->get_result();
		}

		if ($err > 0) {
			dwho_report::push('error', $r['error']);
			dwho_report::push('error', 'Can\'t update SIP Options in staticsip table');
			return(false);
		}

		return(true);
	}

	function _set_save($arr)
	{
		$query = array();
		$query['node_type'] = $arr['node_type'];
		$query['remote_address'] = $arr['remote_address'];

		$this->_set_sip_options($arr['node_type']);
		$this->_set_provd_template_line($arr['node_type'], $arr['remote_address']);

		if(($res = $this->_sysconfd->request_post('/update_ha_config', $query)) === false
		|| $this->_sysconfd->last_status_code() != 200) {
			return(false);
		}
		return($res);
	}

	function set($arr)
	{
		$this->_reset();

		if(!$this->_set_check(&$arr))
			return false;

		if($this->_set_save($arr) === false)
			return false;

		return(true);
	}

	function gen_passphrase($len, $lower=false)
	{
		$pwd = '';
		for($i = 0; $i < $len; $i++)
		{
			$r = mt_rand(0, 35);
			$pwd .= $r < 10?$r:chr($r-10+65);
		}

		if($lower)
			$pwd = strtolower($pwd);

		return $pwd;
	}

}

?>
