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

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'application','abstract','datastorage','sql.inc'));

class xivo_application_service_asterisk_line_sql extends xivo_application_abstract_datastorage_sql
{
	var $_table	= array(
				'linefeatures' => '',
				'usersip'		=> '',
				'useriax'		=> '',
				'usersccp'		=> '',
				'usercustom'	=> '');

	function get_nb($arr=null,$disable=null,$initialized=null)
	{
		if(is_array($arr) === false)
			$arr = array();

		$this->_dso->new_select($this->_table['linefeatures']);
		$this->_dso->leftjoin($this->_table['usersip'],
				      $this->_table['linefeatures'].'.protocolid = '.$this->_table['usersip'].'.id');
		$this->_dso->leftjoin($this->_table['useriax'],
				      $this->_table['linefeatures'].'.protocolid = '.$this->_table['useriax'].'.id');
		$this->_dso->leftjoin($this->_table['usersccp'],
				      $this->_table['linefeatures'].'.protocolid = '.$this->_table['usersccp'].'.id');
		$this->_dso->leftjoin($this->_table['usercustom'],
				      $this->_table['linefeatures'].'.protocolid = '.$this->_table['usercustom'].'.id');

		$this->_dso->where($this->_table['usersip'].'.id IS NOT NULL');
		$this->_dso->orwhere($this->_table['useriax'].'.id IS NOT NULL');
		$this->_dso->orwhere($this->_table['usersccp'].'.id IS NOT NULL');
		$this->_dso->orwhere($this->_table['usercustom'].'.id IS NOT NULL');

		$this->_dso->aggregate_where();

		$sip = $iax = $sccp = $custom = array();
		$sip['category'] = $iax['category'] = $custom['category'] = 'user';

		$arr['internal'] = 0;

		if($disable !== null)
		{
			$disable = intval((bool) $disable);
			$arr['commented'] = $disable;
			$sip['commented'] = $disable;
			$iax['commented'] = $disable;
			$sccp['commented'] = $disable;
			$custom['commented'] = $disable;
		}

		$this->_dso->andwhere($arr,$this->_table['linefeatures']);
		$this->_dso->joinwhere($this->_table['usersip']   ,$sip);
		$this->_dso->joinwhere($this->_table['useriax']   ,$iax);
		$this->_dso->joinwhere($this->_table['usersccp'],$sccp);
		$this->_dso->joinwhere($this->_table['usercustom'],$custom);

		$this->_dso->andjoinwhere($this->_table['usersip'],
					  $this->_table['linefeatures'].'.protocol = '.$this->_table['usersip'].'.protocol');

		$this->_dso->andjoinwhere($this->_table['useriax'],
					  $this->_table['linefeatures'].'.protocol = '.$this->_table['useriax'].'.protocol');

		$this->_dso->andjoinwhere($this->_table['usersccp'],
					  $this->_table['linefeatures'].'.protocol = '.$this->_table['usersccp'].'.protocol');

		$this->_dso->andjoinwhere($this->_table['usercustom'],
					  $this->_table['linefeatures'].'.protocol = '.$this->_table['usercustom'].'.protocol');

		if($initialized !== null)
		{
			if((bool) $initialized === false)
				$this->_dso->andjoinwhere($this->_table['usersip'],
							  'COALESCE('.$this->_table['usersip'].'.fullcontact,\'\') = \'\'');
			else
				$this->_dso->andjoinwherenot($this->_table['usersip'],
							  'COALESCE('.$this->_table['usersip'].'.fullcontact,\'\') = \'\'');
		}

		return(dwho_ulongint($this->_dso->select_count(null,'id',$this->_table['linefeatures'])));
	}

	/**
	 *
	 * options:
	 *		- internal: if true, also return internal accounts (*guest* account indeed)
	 *		- free: if true, also return iduserfeatures=0, null = both, false return iduserfeatures != 0
	*/
	function get_all($protocols,$disable=null,$initialized=null,$order=null,$limit=null,$value=null,$context=null,$mode=null,$internal=false,$free=null)
	{
		$this->_cnt = 0;

		if($mode !== 'number')
			$mode = null;

		$arr = array();

		$this->_dso->new_select($this->_table['linefeatures']);

		if(is_array($protocols) === false)
			$use_sip = $use_iax = $use_sccp = $use_custom = true;
		else
		{
			$use_sip  = in_array(XIVO_SRE_IPBX_AST_PROTO_SIP ,$protocols);
			$use_iax  = in_array(XIVO_SRE_IPBX_AST_PROTO_IAX ,$protocols);
			$use_sccp = in_array(XIVO_SRE_IPBX_AST_PROTO_SCCP,$protocols);
			$use_custom = in_array(XIVO_SRE_IPBX_AST_PROTO_CUSTOM,$protocols);
			$this->_dso->wherein('protocol',$protocols,$this->_table['linefeatures']);
		}

		if($use_sip === false && $use_iax === false && $use_sccp === false && $use_custom === false)
			return(false);

		if(!$internal)
			$arr['internal'] = 0;

		if($free === false)
			$this->_dso->andwherenot(array('iduserfeatures' => 0),$this->_table['linefeatures']);
		elseif($free === true)
			$this->_dso->andwhere(array('iduserfeatures' => 0),$this->_table['linefeatures']);

		$sip = $iax = $custom = $sccp = array();
		$sip['category'] = $iax['category'] = $custom['category'] = 'user';

		if($disable !== null)
		{
			$disable = intval((bool) $disable);
			$arr['commented'] = $disable;
			$sip['commented'] = $disable;
			$iax['commented'] = $disable;
			$sccp['commented']   = $disable;
			$custom['commented'] = $disable;
		}

		$this->_dso->andwhere($arr,$this->_table['linefeatures']);

		if($mode === 'number')
			$this->_dso->andwherenot('COALESCE('.$this->_table['linefeatures'].'.number,\'\') = \'\'');

		if($use_sip === true)
		{
			$this->_dso->leftjoin($this->_table['usersip'],
					      $this->_table['linefeatures'].'.protocolid = '.$this->_table['usersip'].'.id',
					      null,
					      '*');

			$this->_dso->joinwhere($this->_table['usersip'],$sip);

			$this->_dso->andjoinwhere($this->_table['usersip'],
						  $this->_table['linefeatures'].'.protocol = '.$this->_table['usersip'].'.protocol');

			if($initialized !== null)
			{
				if((bool) $initialized === false)
					$this->_dso->andjoinwhere($this->_table['usersip'],
								  'COALESCE('.$this->_table['usersip'].'.fullcontact,\'\') = \'\'');
				else
					$this->_dso->andjoinwherenot($this->_table['usersip'],
								  'COALESCE('.$this->_table['usersip'].'.fullcontact,\'\') = \'\'');
			}
		}

		if($use_iax === true)
		{
			$this->_dso->leftjoin($this->_table['useriax'],
					      $this->_table['linefeatures'].'.protocolid = '.$this->_table['useriax'].'.id',
					      null,
					      '*');

			$this->_dso->joinwhere($this->_table['useriax'],$iax);

			$this->_dso->andjoinwhere($this->_table['useriax'],
						  $this->_table['linefeatures'].'.protocol = '.$this->_table['useriax'].'.protocol');
		}

		if($use_sccp === true)
		{
			$this->_dso->leftjoin($this->_table['usersccp'],
					      $this->_table['linefeatures'].'.protocolid = '.$this->_table['usersccp'].'.id',
					      null,
					      '*');

			$this->_dso->joinwhere($this->_table['usersccp'],$sccp);

			$this->_dso->andjoinwhere($this->_table['usersccp'],
						  $this->_table['linefeatures'].'.protocol = '.$this->_table['usersccp'].'.protocol');
		}

		if($use_custom === true)
		{
			$this->_dso->leftjoin($this->_table['usercustom'],
					      $this->_table['linefeatures'].'.protocolid = '.$this->_table['usercustom'].'.id',
					      null,
					      'interface');

			$this->_dso->joinwhere($this->_table['usercustom'],$custom);

			$this->_dso->andjoinwhere($this->_table['usercustom'],
						  $this->_table['linefeatures'].'.protocol = '.$this->_table['usercustom'].'.protocol');
		}

		$this->_dso->aggregate_where();

		if(($has_context = dwho_has_len($context)) === true)
			$this->_dso->where($this->_table['linefeatures'].'.context = %s',$context);

		if(dwho_has_len($value) === true)
		{
			$this->_dso->aggregate_where();
			$this->_dso->orwherecontain('number',$value,true,$this->_table['linefeatures']);
			$this->_dso->orwherecontain('name',$value,true,$this->_table['linefeatures']);

			if($mode === null && $has_context === false && $context !== false)
				$this->_dso->orwherecontain('context',$value,true,$this->_table['linefeatures']);
		}

		$this->_dso->aggregate_where();

		if($use_sip === true)
			$this->_dso->orwhere($this->_table['usersip'].'.id IS NOT NULL');

		if($use_iax === true)
			$this->_dso->orwhere($this->_table['useriax'].'.id IS NOT NULL');

		if($use_sccp === true)
			$this->_dso->orwhere($this->_table['usersccp'].'.id IS NOT NULL');

		if($use_custom === true)
			$this->_dso->orwhere($this->_table['usercustom'].'.id IS NOT NULL');

		$this->_dso->aggregate_where(false,'AND');

		$this->_dso->new_order($order,null,$this->_table['linefeatures']);
		$this->_dso->limit($limit);

		$r = $this->_dso->select_all(null,true,true);

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		if(($this->_cnt = $this->_dso->select_count(null,'id',$this->_table['linefeatures'])) === false
		|| isset($r[0]) === false)
			$r = false;

		return($r);
	}

	function search($value,$context,$protocols,$disable=null,$initialized=null,$order=null,$limit=null,$mode=null)
	{
		$this->_cnt = 0;

		if(dwho_has_len($value) === false && $mode === null)
			return(false);

		return($this->get_all($protocols,$disable,$initialized,$order,$limit,$value,$context,$mode));
	}
}

?>
