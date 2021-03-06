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

class dwho_session_abstract_sql
{
    var $_param        = array('table'        => 'session');
    var $_attrib        = array('identifier'    => '');
    var $_dso        = null;
    var $_time        = DWHO_SESS_TIME;
    var $_insert        = false;
    var $_crc        = '';

    function _init(&$dso,$param=array())
    {
        if(is_object($dso) === false)
            trigger_error('Invalid Datastorage object',E_USER_ERROR);

        $this->_dso = &$dso;

        $param = (array) $param;

        if(isset($param['table']) === true)
            $this->_param['table'] = (string) $param['table'];
    }

    function set_attrib($name,$value)
    {
        $name = (string) $name;
        $this->_attrib[$name] = $value;
    }

    function get_attrib($name)
    {
        $name = (string) $name;

        if(isset($this->_attrib[$name]) === true)
            return($this->_attrib[$name]);
        else
            return(null);
    }

    function open($path,$name)
    {
        return(true);
    }

    function close()
    {
        return(true);
    }

    function read($sessid)
    {
        $r = '';

        $this->_insert = true;

        $this->_dso->new_select($this->_param['table'],array('identifier','data','expire'));
        $this->_dso->where(array('sessid' => $sessid));
        $this->_dso->andwhere('expire >= %s',gmstrftime('%s'));
        $this->_dso->limit(2);

        if(($rs = $this->_dso->select_all(null,false)) !== false)
        {
            if($this->_dso->num_rows() === 1)
            {
                $this->_insert = false;

                $r = $rs[0]['data'];
                $this->_attrib['identifier'] = $rs[0]['identifier'];

                if(empty($r) === true)
                    $this->_dso->delete($this->_param['table'],array('sessid' => $sessid));
            }

            $this->_dso->free();
        }

        $this->_crc = sha1($r.$this->_attrib['identifier']);

        return($r);
    }

    function write($sessid,$data)
    {
        $now = gmstrftime('%s');
        $expire = $now + $this->_time;
        $crc = sha1($data.$this->_attrib['identifier']);

        if($this->_insert === false && $this->_crc !== '' && $this->_crc === $crc)
            return(true);

        if($this->_insert === false)
        {
            $this->_dso->new_select($this->_param['table']);
            $this->_dso->where(array('sessid' => $sessid));

            if(($r = $this->_dso->select_count()) !== false)
            {
                if($r > 0)
                {
                    $rs = $this->_dso->update($this->_param['table'],
                                  array('identifier'    => $this->_attrib['identifier'],
                                    'expire'    => $expire,
                                    'data'        => $data),
                                  null,
                                  null,
                                  true);

                    if($rs !== false && $this->_dso->affected_rows() === 0)
                        $this->_insert = true;
                }
                else
                    $this->_insert = true;
            }
        }

        if($this->_insert !== true)
            return(true);

        /* REPLACE is not a standard SQL statement
        $this->_dso->replace($this->_param['table'],
                     array('identifier'    => $this->_attrib['identifier'],
                       'sessid'    => $sessid,
                       'start'    => $now,
                       'expire'    => $expire,
                         'data'    => $data));
         */
        $this->_dso->new_select($this->_param['table']);
        $this->_dso->where(array('sessid' => $sessid));

        if(($r = $this->_dso->select_count()) !== false)
        {
                if($r > 0)
                {
                    $rs = $this->_dso->update($this->_param['table'],
                        array('identifier'    => $this->_attrib['identifier'],
                            'start'  => $now,
                            'expire'    => $expire,
                            'data'        => $data),
                            array('sessid' => $sessid),
                          null,
                          true);

                }    else    {
                    $rs = $this->_dso->insert($this->_param['table'],
                        array('identifier'    => $this->_attrib['identifier'],
                            'sessid'  => $sessid,
                            'start'   => $now,
                            'expire'    => $expire,
                            'data'        => $data));
                }
        }


        return(true);
    }

    function destroy($sessid)
    {
        $this->_dso->delete($this->_param['table'],array('sessid' => $sessid));
        return(true);
    }

    function gc($t=0)
    {
        $this->_dso->delete($this->_param['table'],'expire < %s',gmstrftime('%s'));
        return(true);
    }

    function write_close()
    {
        $this->gc();
        session_write_close();
        return(true);
    }
}

?>
