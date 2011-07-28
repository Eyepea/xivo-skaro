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

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'abstract','statistics.inc'));

class xivo_statistics_incall extends xivo_statistics_abstract
{

	public		$_field	= array('chanstart'	=> array('type' => 'int'),);
	private		$_cel	= false;

	public function __construct(&$_XS)
	{
		parent::__construct(&$_XS);
		$this->_method = 'DB';
		$this->_table = 'cel';
		$this->_type = 'incall';
		$this->_xs->set_type($this->_type);

		if(($_SRE = &dwho_gct::get('xivo_service')) === false
		|| ($this->_cel = &$_SRE->get_module('ipbx','cel')) === false)
			die('Can\'t load cell object');
	}

	public function cel()
	{
		return $this->_cel;
	}

	public function parse_log($key_data,$key)
	{
		if ($this->_xs->get_conf() === false)
			return(false);
		switch ($this->_xs->_method)
		{
			case 'DB':
				return($this->parse_log_db($key_data,$key));
				break;
			case 'PHP':
			default:
				return(false);
		}
		return(true);
	}

	private function parse_log_db($key_data,$key)
	{
		$this->init_result($key);

		$val = $this->eval_count_data($key_data,'CHAN_START');
		$this->update_result(array($key,'chanstart'),$val);

		$this->_table = 'queue_log';

		$closed = $this->eval_count_data($key_data,'CLOSED');
		$this->update_result(array($key,'deterred_on_close'),$closed);

		$full = $this->eval_count_data($key_data,'FULL');
		$this->update_result(array($key,'deterred_on_saturation'),$full);

		return($this->_result);
	}

}

?>