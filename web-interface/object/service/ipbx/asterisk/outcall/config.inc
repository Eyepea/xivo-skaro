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

$array = array();
$array['element'] = array();

$array['element']['name'] = array();
$array['element']['name']['default'] = '';

$array['element']['context'] = array();
$array['element']['context']['default'] = '';

$array['element']['routing'] = array();
$array['element']['routing']['default'] = '';

$array['element']['useenum'] = array();
$array['element']['useenum']['value'] = array(0,1);
$array['element']['useenum']['default'] = 0;
$array['element']['useenum']['set'] = true;

$array['element']['internal'] = array();
$array['element']['internal']['value'] = array(0,1);
$array['element']['internal']['default'] = 0;
$array['element']['internal']['set'] = true;

$array['element']['preprocess_subroutine'] = array();
$array['element']['preprocess_subroutine']['default'] = '';
$array['element']['preprocess_subroutine']['null'] = true;

$array['element']['description'] = array();
$array['element']['description']['default'] = '';

$array['element']['hangupringtime'] = array();
$array['element']['hangupringtime']['value'] = array(0,15,30,45,60,75,90,
						     105,120,135,150,165,180,195,
						     210,225,240,255,270,285,300);
$array['element']['hangupringtime']['default'] = 0;
$array['element']['hangupringtime']['setdef'] = true;

$array['element']['commented'] = array();
$array['element']['commented']['value'] = array(0,1);
$array['element']['commented']['default'] = 0;
$array['element']['commented']['set'] = true;

$array['filter'] = array();
$array['filter']['name'] = array('maxlen' => 128,'regexp' => '/^[a-z0-9_-]+$/i');
$array['filter']['context'] = array('callback' => 'xivo_service_asterisk::chk_context');
$array['filter']['routing'] = array('set' => false,'chk' => 2,'maxlen' => 64,'regexp' => '/^[a-z0-9_-]+$/i');
$array['filter']['useenum'] = array('bool' => true);
$array['filter']['internal'] = array('bool' => true);
$array['filter']['preprocess_subroutine'] = array('set' => false,'chk' => 2,'callback' => 'xivo_service_asterisk::chk_context');
$array['filter']['description'] = array('set' => false,'chk' => 2,'maxlen' => 1000,'cast' => 'sgraph_crlf_tab','eol' => true);
$array['filter']['hangupringtime'] = array('set'	=> false,
					   'chk'	=> 2,
					   'key' => array(0,15,30,45,60,75,90,
							  105,120,135,150,165,180,
							  210,225,240,255,270,285,300));
$array['filter']['commented'] = array('bool' => true);

?>
