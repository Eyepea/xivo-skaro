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

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'application','abstract','datastorage','sql.inc'));

class xivo_application_service_asterisk_queue_sql extends xivo_application_abstract_datastorage_sql
{
	var $_table	= array(
				'queuefeatures'	=> '',
				'queue'		=> '',
				'queuemember'	=> '');

	function get_all($disable=null,$order=null,$limit=null,$value=null)
	{
		$this->_dso->new_select($this->_table['queuefeatures']);

		$this->_dso->innerjoin($this->_table['queue'],
				       $this->_table['queuefeatures'].'.name = '.$this->_table['queue'].'.name',
				       null,
				       array('commented','category'));

		$this->_dso->leftjoin($this->_table['queuemember'],
				      $this->_table['queuefeatures'].'.name = '.$this->_table['queuemember'].'.queue_name',
				      null,
				      array('nb_qmember' => 'COUNT('.$this->_table['queuemember'].'.userid)'));

		if($disable !== null)
		{
			$commented = array('commented' => intval((bool) $disable));
			$this->_dso->andwhere($commented,$this->_table['queue']);
			$this->_dso->andwhere($commented,$this->_table['queuemember']);
		}

		$this->_dso->new_group('name',$this->_table['queuefeatures']);
		$this->_dso->add_group('id', $this->_table['queuefeatures']);
		$this->_dso->add_group('displayname', $this->_table['queuefeatures']);
		$this->_dso->add_group('number', $this->_table['queuefeatures']);
		$this->_dso->add_group('context', $this->_table['queuefeatures']);
		$this->_dso->add_group('data_quality', $this->_table['queuefeatures']);
		$this->_dso->add_group('hitting_callee', $this->_table['queuefeatures']);
		$this->_dso->add_group('hitting_caller', $this->_table['queuefeatures']);
		$this->_dso->add_group('retries', $this->_table['queuefeatures']);
		$this->_dso->add_group('ring', $this->_table['queuefeatures']);
		$this->_dso->add_group('transfer_user', $this->_table['queuefeatures']);
		$this->_dso->add_group('transfer_call', $this->_table['queuefeatures']);
		$this->_dso->add_group('write_caller', $this->_table['queuefeatures']);
		$this->_dso->add_group('write_calling', $this->_table['queuefeatures']);
		$this->_dso->add_group('url', $this->_table['queuefeatures']);
		$this->_dso->add_group('announceoverride', $this->_table['queuefeatures']);
		$this->_dso->add_group('timeout', $this->_table['queuefeatures']);
		$this->_dso->add_group('preprocess_subroutine', $this->_table['queuefeatures']);
		$this->_dso->add_group('commented', $this->_table['queue']);
		$this->_dso->add_group('category', $this->_table['queue']);
		$this->_dso->add_group('announce_holdtime', $this->_table['queuefeatures']);
		$this->_dso->add_group('ctipresence', $this->_table['queuefeatures']);
		$this->_dso->add_group('nonctipresence', $this->_table['queuefeatures']);
		$this->_dso->add_group('waittime', $this->_table['queuefeatures']);
		$this->_dso->add_group('waitratio', $this->_table['queuefeatures']);


		if(dwho_has_len($value) === true)
		{
			$this->_dso->aggregate_where();
			$this->_dso->wherecontain('displayname',$value,true,$this->_table['queuefeatures']);
			$this->_dso->orwherecontain('number',$value,true,$this->_table['queuefeatures']);
			$this->_dso->aggregate_where();
		}

		$this->_dso->new_order($order,null,$this->_table['queuefeatures']);
		$this->_dso->limit($limit);

		$r = $this->_dso->select_all();

		$this->_dso->reset_group();
		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		if(($this->_cnt = $this->_dso->select_distinct_count_singlecolumn(
							null,
							'id',
							$this->_table['queuefeatures'])) === false
		|| isset($r[0]) === false)
			$r = false;

		return($r);
	}

	function search($value,$disable=null,$order=null,$limit=null)
	{
		$this->_cnt = 0;

		if(dwho_has_len($value) === false)
			return(false);

		return($this->get_all($disable,$order,$limit,$value));
	}

	function skills_count($search=null)
	{
		$this->_dso->new_select('queueskillcat', array('count' => (object) 'COUNT(*)'));
		if(!is_null($search) && strlen($search) > 0)
			$this->_dso->orwherecontain("name", $search);

		$res = $this->_dso->select_all(null, true);

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		return($res);
	}

	function skills_getall($search=null, $limit=null)
	{
		$this->_dso->new_select('queueskillcat',array('id', 'name'));
		if(!is_null($search) && strlen($search) > 0)
			$this->_dso->wherecontain("displayname", $search, true, 'queueskillcat');

		$this->_dso->leftjoin('queueskill',
			'queueskillcat.id = queueskill.catid',
			null,
			array('sum' => (object) 'COUNT(queueskill.id)'));

		$this->_dso->new_group('id', 'queueskillcat');
		$this->_dso->add_group('name', 'queueskillcat');
		$this->_dso->new_order('name', null, 'queueskillcat');
		$this->_dso->limit($limit);

		$res = $this->_dso->select_all(null, true);

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		return($res);
	}

    function skills_json_get($id=null,$filter=null,$limit=null)
	{
		$this->_dso->new_select('queueskill', array('id', 'name', 'description', 'printscreen'));
		$this->_dso->leftjoin('queueskillcat',
    		'queueskillcat.id = queueskill.catid',
    		null,
    		array('category_name' => 'name'));

        // search by ID
        if(!is_null($id))
        {
            $this->_dso->where(array('id' => $id),'queueskill');
        }
        // search by string match (LIKE)
        else if(!is_null($filter))
        {
            $this->_dso->wherecontain('name'	, $filter, true, 'queueskill');
            $this->_dso->orwherecontain('description' , $filter, true, 'queueskill');
            $this->_dso->orwherecontain('printscreen' , $filter, true, 'queueskill');
            $this->_dso->orwherecontain('name'        , $filter, true, 'queueskillcat');
        }

		$this->_dso->new_order('id', null, 'queueskill');
		$this->_dso->limit($limit);

		if(!is_null($id))
		{ $res = $this->_dso->select_single(); }
		else
		{ $res = $this->_dso->select_all(null, true); }

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		return($res);
	}

	function skills_getone($id)
	{
		if(!is_int($id))
		{ return false; }

		// 1. get skill name
		$this->_dso->new_select('queueskillcat');
		$this->_dso->where(array('id' => $id));
		$res = $this->_dso->select_single();
		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		if($res === false || count($res) == 0)
		{ return false; }

		$name = $res['name'];

		// 2. get skill values
		$this->_dso->new_select('queueskill');
		$this->_dso->where(array('catid' => $id));

		$res = $this->_dso->select_all(null, true);
		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		return array('id' => $id, 'name' => $name,  'values' => $res);
	}

	function skills_gettree()
	{
		$this->_dso->new_select('queueskill',array('id','name'));
		$this->_dso->leftjoin('queueskillcat',
			'queueskillcat.id = queueskill.catid',
			null,
			array('category' => 'name'));

		$this->_dso->new_order('name', null, 'queueskillcat');
		$this->_dso->add_order('name', null, 'queueskill');

		$res = $this->_dso->select_all(null, true);

		$this->_dso->reset_order();
		$this->_dso->reset_limit();
		return($res);
	}

	/** skill rules */
	function skillrules_count($search=null)
	{
		$this->_dso->new_select('queueskillrule', array('count' => (object) 'COUNT(*)'));
		if(!is_null($search) && strlen($search) > 0)
			$this->_dso->wherecontain("name", $search);

		$res = $this->_dso->select_all(null, true);

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		return($res);
	}

	function skillrules_getall($search=null, $limit=null, $inrule=false)
	{
		$this->_dso->new_select('queueskillrule');
		if(!is_null($search) && strlen($search) > 0)
		{
			$this->_dso->wherecontain("name", $search);

			if($inrule)
                $this->_dso->orwherecontain('rule' , $search);
		}

		$this->_dso->new_order('name', null, 'queueskillrule');
		$this->_dso->limit($limit);

		$res = $this->_dso->select_all(null, true);

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		return($res);
	}

	function skillrules_getone($id)
	{
		if(!is_int($id))
		{ return false; }

		// 1. get skill name
		$this->_dso->new_select('queueskillrule');
		$this->_dso->where(array('id' => $id));

		$res = $this->_dso->select_single();

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		return $res;
	}


	function userskills_get($id)
	{
		if(!is_int($id))
		{ return false; }

		$this->_dso->new_select('userqueueskill');
		$this->_dso->where(array('userid' => $id));

		$this->_dso->leftjoin('queueskill',
			'queueskill.id = userqueueskill.skillid',
			null,
			null);

		$this->_dso->new_order('name', null, 'queueskill');

		$res = $this->_dso->select_all(null, true);

		$this->_dso->reset_order();
		$this->_dso->reset_limit();
		return($res);
	}

	function agentskills_get($id)
	{
		if(!is_int($id))
		{ return false; }

		$this->_dso->new_select('agentqueueskill');
		$this->_dso->where(array('agentid' => $id));

		$this->_dso->leftjoin('queueskill',
			'queueskill.id = agentqueueskill.skillid',
			null,
			null);

		$this->_dso->new_order('name', null, 'queueskill');

		$res = $this->_dso->select_all(null, true);

		$this->_dso->reset_order();
		$this->_dso->reset_limit();
		return($res);
	}
}

?>
