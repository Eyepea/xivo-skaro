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

xivo_service_asterisk::required(array('abstract','datastorage','abstract','sql.inc'),true);

class xivo_service_asterisk_attachment_sql extends xivo_service_asterisk_abstract_sql
{
	var $_autoincrement	= true;
	var $_disable		= null;

	private function _prepare_file_to_import($filepath)
	{
		if (dwho_file::is_f_r($filepath) === false)
			return(false);

		if (($file = $this->_normalize_img($filepath)) === false)
		{
			$fh = fopen($filepath,'r');
			$file = fread($fh, filesize($filepath));
			fclose($fh);
		}

		$file = $this->_dso->escape_bytea($file);

		return($file);
	}

	private function _prepare_file_to_export($filebin)
	{
		return($this->_dso->unescape_bytea($filebin));
	}

	private function _normalize_img($file)
	{
		$source_pic = $file;
		$max_width = 150;
		$max_height = 150;

		list($width, $height, $image_type) = getimagesize($file);

		switch ($image_type)
		{
			case 1: $src = imagecreatefromgif($file); break;
			case 2: $src = imagecreatefromjpeg($file);  break;
			case 3: $src = imagecreatefrompng($file); break;
			default: return(false);  break;
		}

		$x_ratio = $max_width / $width;
		$y_ratio = $max_height / $height;

		if( ($width <= $max_width) && ($height <= $max_height) )
		{
			$tn_width = $width;
			$tn_height = $height;
		}
		elseif (($x_ratio * $height) < $max_height)
		{
			$tn_height = ceil($x_ratio * $height);
			$tn_width = $max_width;
		}
		else
		{
			$tn_width = ceil($y_ratio * $width);
			$tn_height = $max_height;
		}

		$tmp = imagecreatetruecolor($tn_width,$tn_height);

		/* Check if this image is PNG or GIF, then set if Transparent*/
		if(($image_type == 1) || ($image_type==3))
		{
			imagealphablending($tmp, false);
			imagesavealpha($tmp,true);
			$transparent = imagecolorallocatealpha($tmp, 255, 255, 255, 127);
			imagefilledrectangle($tmp, 0, 0, $tn_width, $tn_height, $transparent);
		}
		imagecopyresampled($tmp,$src,0,0,0,0,$tn_width, $tn_height,$width,$height);

		/*
		 * imageXXX() only has two options, save as a file, or send to the browser.
		* It does not provide you the oppurtunity to manipulate the final GIF/JPG/PNG file stream
		* So I start the output buffering, use imageXXX() to output the data stream to the browser,
		* get the contents of the stream, and use clean to silently discard the buffered contents.
		*/
		ob_start();

		switch ($image_type)
		{
			case 1: imagegif($tmp); break;
			case 2: imagejpeg($tmp, NULL, 100);  break; // best quality
			case 3: imagepng($tmp, NULL, 0); break; // no compression
			default: echo ''; break;
		}

		$final_image = ob_get_contents();

		ob_end_clean();

		return($final_image);
	}

	function get($arr,$disable=null,$primary=false,$exists=false)
	{
		$this->_dso->set_bytea_output();
		if (($attachment = parent::get($arr,$disable,$primary,$exists)) === false)
			return(false);

		$attachment['file'] = $this->_prepare_file_to_export($attachment['file']);

		return($attachment);
	}

	function get_where($arr,$disable=null,$primary=false,$exists=false)
	{
		$this->_dso->set_bytea_output();
		if (($attachment = parent::get($arr,$disable,$primary,$exists)) === false)
			return(false);

		$attachment['file'] = $this->_prepare_file_to_export($attachment['file']);

		return($attachment);
	}

	function add($arr,$id=0)
	{
		if(is_array($arr) === false
		|| isset($arr['file']) === false)
			return(false);
		else if(isset($arr['name']) === true)
			$arr['name'] = strtolower($arr['name']);

		$arr['file'] = $this->_prepare_file_to_import($arr['file']);

		return(parent::add($arr,$id));
	}

	function edit($id,$arr)
	{
		if(is_array($arr) === false)
			return(false);
		else if(isset($arr['name']) === true)
			$arr['name'] = strtolower($arr['name']);

		$arr['file'] = $this->_prepare_file_to_import($arr['file']);

		return(parent::edit($id,$arr));
	}
}

?>
