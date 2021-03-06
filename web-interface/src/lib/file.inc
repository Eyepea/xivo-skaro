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

if(defined('UPLOAD_ERR_NO_TMP_DIR') === false)
    define('UPLOAD_ERR_NO_TMP_DIR',6);

if(defined('UPLOAD_ERR_CANT_WRITE') === false)
    define('UPLOAD_ERR_CANT_WRITE',7);

if(defined('FILE_USE_INCLUDE_PATH') === false)
    define('FILE_USE_INCLUDE_PATH',1);

if(defined('FILE_APPEND') === false)
    define('FILE_APPEND',8);

define('FILE_F_OK',0);
define('FILE_X_OK',1);
define('FILE_W_OK',2);
define('FILE_R_OK',4);

abstract class dwho_file
{
    public static function fileinfo($file)
    {
        static $mime_cim = null;

        if(dwho::load_extension('fileinfo') === false)
            return(false);

        if($mime_cim === null)
        {
            if(dwho::load_class('dwho_mime_cim',
                        array('mime','abstract'),
                        'cim') === false)
                return(($mime_cim = false));

            $mime_cim = new dwho_mime_cim();
        }

        if(is_object($mime_cim) === false
        || ($fileinfo = finfo_open(FILEINFO_MIME)) === false)
            return(false);

        $r = $mime_cim->parse_content_type(finfo_file($fileinfo,$file));

        finfo_close($fileinfo);

        return($r);
    }

    public static function get_mime($file)
    {
        if(($file = self::is_f($file)) === false)
            return(false);
        else if(($fileinfo = self::fileinfo($file)) !== false)
            $r = $fileinfo['type'].'/'.$fileinfo['subtype'];
        else if(dwho::load_extension('mime_magic') !== false)
            $r = mime_content_type($file);
        else
            $r = false;

        return($r);
    }

    public static function get_charset($file=null)
    {
        if(($file = self::is_f($file)) !== false
        && ($fileinfo = self::fileinfo($file)) !== false
        && dwho_issa('parameters',$fileinfo) === true
        && isset($fileinfo['parameters']['charset']) === true)
            return($fileinfo['parameters']['charset']);

        return(false);
    }

    public static function get_time($file)
    {
        $r = false;

        if(($file = self::is_f($file)) !== false)
            $r = filemtime($file);

        return($r);
    }

    public static function get_info($file)
    {
        if(($file = self::is_f($file)) === false)
            return(false);

        $pinfo = pathinfo($file);

        if(isset($pinfo['extension']) === false)
            $pinfo['extension'] = '';

        $info = array();
        $info['path']    = $file;
        $info['dir']    = $pinfo['dirname'];
        $info['name']    = $pinfo['basename'];
        $info['ext']    = $pinfo['extension'];

        if(($extlen = strlen($pinfo['extension'])) > 0)
            $info['filename'] = substr($pinfo['basename'],0,-($extlen + 1));
        else
            $info['filename'] = $info['name'];

        $info['pathnoext']    = $pinfo['dirname'].DIRECTORY_SEPARATOR.$info['filename'];
        $info['mime']        = self::get_mime($info['path']);
        $info['charset']    = self::get_charset($info['path']);
        $info['mtime']        = filemtime($info['path']);
        $info['size']        = filesize($info['path']);

        if($info['size'] < 0)
            $info['size'] = sprintf('%u',$info['size']);

        return($info);
    }

    public static function load_file($file,$dir='',$once=false,$verif=true)
    {
        $path = '';

        if(preg_match('/^[a-z0-9\-_\.]+$/i',$file) !== 1)
            return(false);
        else if(is_array($dir) === true)
            $dir = self::list_to_path($dir);

        $dir = (string) $dir;

        if($dir === '')
        {
            $path = $file;
            $verif = false;
        }
        else if(is_readable($dir) === true && is_dir($dir) === true)
            $path = rtrim($dir,DIRECTORY_SEPARATOR).DIRECTORY_SEPARATOR.$file;
        else
            return(false);

        if((bool) $verif === true
        && (is_file($path) === false || is_readable($path) === false) === true)
            return(false);
        else if($once === false)
            return((bool) require($path));

        return((bool) require_once($path));
    }

    public static function is_includable($file,$verif=true)
    {
        if((bool) $verif === true
        && (is_file($file) === false || is_readable($file) === false) === true)
            return(false);
        else if(($r = is_resource(($f = fopen($file,'r',true)))) === true)
            fclose($f);

        return(true);
    }

    public static function required($arr,$once=false,$includable=false)
    {
        $path = self::list_to_path($arr);

        if($path === false
        || ($path = self::is_f_r($path)) === false
        || ((bool) $includable === true
           && self::is_includable($path) === false) === true)
            return(false);
        else if((bool) $once === false)
            return((bool) require($path));
        else
            return((bool) require_once($path));
    }

    public static function is_r($file)
    {
        return(is_readable($file));
    }

    public static function is_w($file)
    {
        return(is_writeable($file));
    }

    public static function is_x($file)
    {
        return(is_executable($file));
    }

    public static function is_rw($file)
    {
        return((is_readable($file) === true && is_writeable($file) === true));
    }

    public static function is_rx($file)
    {
        return((is_readable($file) === true && is_executable($file) === true));
    }

    public static function is_wx($file)
    {
        return((is_writeable($file) === true && is_executable($file) === true));
    }

    public static function is_rwx($file)
    {
        return((is_readable($file) === true && is_writeable($file) === true && is_executable($file) === true));
    }

    public static function list_to_path($list)
    {
        if(is_array($list) === false)
            return(false);

        return(implode(DIRECTORY_SEPARATOR,$list));
    }

    public static function joinpath()
    {
        $arr = func_get_args();

        return(dwho_implode(DIRECTORY_SEPARATOR,$arr));
    }

    public static function abspath($str)
    {
        $str = (string) $str;

        if(isset($str{0}) === false)
            return(false);
        else if(strpos($str,DIRECTORY_SEPARATOR) !== 0)
            $str = getcwd().DIRECTORY_SEPARATOR.$str;

        $lstr = preg_split('@'.preg_quote(DIRECTORY_SEPARATOR).'+@',$str,-1,PREG_SPLIT_NO_EMPTY);

        if(($nb = count($lstr)) === 0)
            return($str);

        $r = array();

        $nb = count($lstr);

        for($i = 0;$i < $nb;$i++)
        {
            if(($c = $lstr[$i]) === '.')
                continue;
            else if($c !== '..')
                $r[] = $c;
            else if(isset($r[0]) === true)
                array_pop($r);
        }

        return(DIRECTORY_SEPARATOR.self::list_to_path($r));
    }

    public static function is_f($file,$mode=1)
    {
        static $pathcache = array();

        if(is_file($file) === false)
            return(false);
        else if(($mode = intval($mode)) === 0)
            return($file);
        else if(isset($pathcache[$file]) === false)
        {
            if($mode !== 2)
                $pathcache[$file] = self::abspath($file);
            else
                $pathcache[$file] = realpath($file);
        }

        return($pathcache[$file]);
    }

    public static function is_f_r($file,$mode=1)
    {
        if(is_readable($file) === true)
            return(self::is_f($file,$mode));

        return(false);
    }

    public static function is_f_w($file,$mode=1)
    {
        if(is_writeable($file) === true)
            return(self::is_f($file,$mode));

        return(false);
    }

    public static function is_f_x($file,$mode=1)
    {
        if(is_executable($file) === true)
            return(self::is_f($file,$mode));

        return(false);
    }

    public static function is_f_rw($file,$mode=1)
    {
        if(self::is_rw($file) === true)
            return(self::is_f($file,$mode));

        return(false);
    }

    public static function is_f_rx($file,$mode=1)
    {
        if(self::is_rx($file) === true)
            return(self::is_f($file,$mode));

        return(false);
    }

    public static function is_f_wx($file,$mode=1)
    {
        if(self::is_wx($file) === true)
            return(self::is_f($file,$mode));

        return(false);
    }

    public static function is_f_rwx($file,$mode=1)
    {
        if(self::is_rwx($file) === true)
            return(self::is_f($file,$mode));

        return(false);
    }

    public static function is_d($dir,$dirname=false,$mode=1)
    {
        static $pathcache = array();

        if((bool) $dirname === true)
            $dir = dirname($dir);

        if(is_dir($dir) === false)
            return(false);
        else if(($mode = intval($mode)) === 0)
                return($dir);
        else if(isset($pathcache[$dir]) === false)
        {
            if($mode !== 2)
                $pathcache[$dir] = self::abspath($dir);
            else
                $pathcache[$dir] = realpath($dir);
        }

        return($pathcache[$dir]);
    }

    public static function is_d_r($dir,$dirname=false,$mode=1)
    {
        if((bool) $dirname === true)
            $dir = dirname($dir);

        if(is_readable($dir) === true)
            return(self::is_d($dir,false,$mode));

        return(false);
    }

    public static function is_d_w($dir,$dirname=false,$mode=1)
    {
        if((bool) $dirname === true)
            $dir = dirname($dir);

        if(is_writeable($dir) === true)
            return(self::is_d($dir,false,$mode));

        return(false);
    }

    public static function is_d_x($dir,$dirname=false,$mode=1)
    {
        if((bool) $dirname === true)
            $dir = dirname($dir);

        if(is_executable($dir) === true)
            return(self::is_d($dir,false,$mode));

        return(false);
    }

    public static function is_d_rw($dir,$dirname=false,$mode=1)
    {
        if((bool) $dirname === true)
            $dir = dirname($dir);

        if(self::is_rw($dir) === true)
            return(self::is_d($dir,false,$mode));

        return(false);
    }

    public static function is_d_rx($dir,$dirname=false,$mode=1)
    {
        if((bool) $dirname === true)
            $dir = dirname($dir);

        if(self::is_rx($dir) === true)
            return(self::is_d($dir,false,$mode));

        return(false);
    }

    public static function is_d_wx($dir,$dirname=false,$mode=1)
    {
        if((bool) $dirname === true)
            $dir = dirname($dir);

        if(self::is_wx($dir) === true)
            return(self::is_d($dir,false,$mode));

        return(false);
    }

    public static function is_d_rwx($dir,$dirname=false,$mode=1)
    {
        if((bool) $dirname === true)
            $dir = dirname($dir);

        if(self::is_rwx($dir) === true)
            return(self::is_d($dir,false,$mode));

        return(false);
    }

    public static function put_contents($filename,$data,$flags=0)
    {
        $filename = (string) $filename;
        $flags = dwho_uint($flags);

        if(is_array($data) === true || is_object($data) === true)
            $data = dwho_implode('',$data);

        if(is_scalar($data) === false)
            return(false);

        $dir = dirname($filename);

        if(self::is_d_rwx($dir) === false)
            return(false);
        else if(($flags & FILE_APPEND) !== 0)
            $mode = 'a';
        else if(($filename = self::is_f_rw($filename)) !== false)
            $mode = 'wb';
        else
            return(false);

        $use_inc_path = ($flags & FILE_USE_INCLUDE_PATH) !== 0;
        $use_lock = ($flags & LOCK_EX) !== 0;

        if(($fp = fopen($filename,$mode,$use_inc_path)) === false
        || ($use_lock === true && flock($fp,LOCK_EX) === false) === true)
            return(false);

        $r = false;
        $bytes = 0;

        if(($bytes = fwrite($fp,$data)) !== false)
            $r = $bytes;

        if($use_lock === true)
            flock($fp,LOCK_UN);

        fclose($fp);

        return($r);
    }

    public static function read_d($dir,$type='',$mode=0,$match='',$dirwriteable=false,$stat=false)
    {
        $type = (string) $type;
        $match = (string) $match;
        $stat = (bool) $stat;

        if(($dir = self::is_d_rx($dir)) === false
        || ($open = opendir($dir)) === false
        || ((bool) $dirwriteable === true && self::is_w($dir) === false) === true)
            return(false);

        if($type !== 'file' && $type !== 'dir')
            $type = '';

        $r = array();

        while(($name = readdir($open)) !== false)
        {
            if($name === '.' || $name === '..')
                continue;
            else if($match !== '' && preg_match($match,$name) !== 1)
                continue;

            $file = $dir.DIRECTORY_SEPARATOR.$name;

            if(($mode & FILE_R_OK) !== 0 && self::is_r($file) === false)
                continue;
            else if(($mode & FILE_W_OK) !== 0 && self::is_w($file) === false)
                continue;
            else if(($mode & FILE_X_OK) !== 0 && self::is_x($file) === false)
                continue;

            switch($type)
            {
                case 'file':
                    if(self::is_f($file) === false)
                        continue 2;
                    break;
                case 'dir':
                    if(self::is_d($file) === false)
                        continue 2;
                    break;
            }

            if($stat === false)
                $r[] = $name;
            else
                $r[] = array('name'    => $name,
                         'stat'    => stat($file),
                         'path'    => $dir);
        }

        closedir($open);

        return($r);
    }

    public static function rm($file)
    {
        if(self::is_d_w($file,true) !== false && unlink($file) !== false)
            return(true);

        return(false);
    }

    public static function rmdir($dir)
    {
        if(($dir = self::is_d_rwx($dir)) === false
        || self::is_d_rw(dirname($dir)) === false
        || ($list = self::read_d($dir)) === false
        || is_link($dir) === true)
            return(false);
        else if(isset($list[0]) === false)
            return(rmdir($dir));

        $nb = count($list);

        for($i = 0;$i < $nb;$i++)
        {
            $path = $dir.DIRECTORY_SEPARATOR.$list[$i];

            if(self::is_f($path) !== false)
            {
                unlink($path);
                continue;
            }

            if(self::is_d($path) !== false)
                self::rmdir($path);
        }

        return(rmdir($dir));
    }
}

?>
