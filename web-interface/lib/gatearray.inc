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

abstract class dwho_gatearray
{
    private static $_array 	= array();

    public static function set($name,&$array)
    {
        $name = (string) $name;

        if(is_array($array) === false || $name === '')
            return(false);
        #else if(isset(self::$_array[$name]) === false)
        self::$_array[$name] = &$array;

        return(true);
    }

    public static function load($file,$path='',$name='',$includable=false)
    {
        $file = (string) $file;
        $name = (string) $name;

        if(($pos = strrpos($file,'.')) !== false)
        {
            $file = substr($file,0,$pos);

            if(preg_match('/^[a-z0-9\-_]+$/i',$file) !== 1)
                return(false);
        }

        if($name === '')
            $name = $file;

        if($path === '')
            $path = DWHO_PATH_ROOT.DIRECTORY_SEPARATOR.'gatearray'.DIRECTORY_SEPARATOR.$file.'.inc';
        else if(is_array($path) === true)
            $path = implode(DIRECTORY_SEPARATOR,$path).DIRECTORY_SEPARATOR.$file.'.inc';
        else
            $path = rtrim($path,DIRECTORY_SEPARATOR).DIRECTORY_SEPARATOR.$file.'.inc';

        if((bool) $includable === false)
        {
            if(dwho_file::is_f_r($path) === false)
                return(false);
        }
        else if(dwho_file::is_includable($path) === false)
            return(false);

        if(isset(self::$_array[$name]) === false)
        {
            require_once($path);

            if(isset($array) === false || is_array($array) === false)
                return(false);

            self::$_array[$name] = &$array;
        }

        return($name);
    }

    public static function get_file($path,$once=false,$includable=false)
    {
        if(is_array($path) === true)
            $path = implode(DIRECTORY_SEPARATOR,$path);

        $path = (string) $path.'.inc';

        if((bool) $includable === false)
        {
            if(dwho_file::is_f_r($path) === false)
                return(false);
        }
        else if(dwho_file::is_includable($path) === false)
            return(false);

        if((bool) $once === false)
            require($path);
        else
            require_once($path);

        if(isset($array) === true && is_array($array) === true)
            $r = &$array;
        else
            $r = false;

        return($r);
    }

    public static function &get($name='')
    {
        $name = (string) $name;

        if($name === '')
            $r = &self::$_array;
        else if(dwho_issa($name,self::$_array) === true)
            $r = &self::$_array[$name];
        else
            $r = false;

        return(($ref = &$r));
    }

    public static function &load_get($file,$path='',$name='')
    {
        $r = false;

        if(($name = self::load($file,$path,$name)) !== false)
            $r = &self::get($name);

        return(($ref = &$r));
    }

    public static function &set_get($name,&$array)
    {
        $r = false;

        if(self::set($name,$array) === true)
            $r = &self::get($name);

        return(($ref = &$r));
    }

    public static function is_valid($name)
    {
        $name = (string) $name;

        if(dwho_issa($name,self::$_array) === true)
            return(true);

        return(false);
    }
}

abstract class dwho_gat
{
    public static function set($name,&$array)
    {
        return(dwho_gatearray::set($name,$array));
    }

    public static function load($file,$path='',$name='')
    {
        return(dwho_gatearray::load($file,$path,$name));
    }

    public static function &get($name='')
    {
        return(($ref = &dwho_gatearray::get($name)));
    }

    public static function get_file($path,$once=false)
    {
        return(dwho_gatearray::get_file($path,$once));
    }

    public static function &load_get($file,$path='',$name='')
    {
        return(($ref = &dwho_gatearray::load_get($file,$path,$name)));
    }

    public static function &set_get($name,&$array)
    {
        return(($ref = &dwho_gatearray::set_get($name,$array)));
    }

    public static function is_valid($name)
    {
        return(dwho_gatearray::is_valid($name));
    }
}

?>
