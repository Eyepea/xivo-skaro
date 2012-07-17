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

require_once(DWHO_PATH_ROOT.DIRECTORY_SEPARATOR.'file.inc');


function _get_all_graphs($urldir)
{
    $basedir = dwho_file::joinpath(XIVO_PATH_ROOT.DIRECTORY_SEPARATOR.
                                   'www'.
                                   DIRECTORY_SEPARATOR.
                                   $urldir);
    $graphs = dwho_file::read_d($basedir,'file',FILE_R_OK,'/day.png$/');
    sort($graphs);

    return($graphs);
}

function _get_category($graph_id)
{

    $classifier = array('nginx_.*'        => 'nginx',
                        'asterisk_.*'     => 'asterisk',
                        'df.*'            => 'disk',
                        'iostat'          => 'disk',
                        'smart_.*'        => 'disk',
                        'hddtemp_.*'      => 'disk',
                        'if_.*'           => 'network',
                        'netstat'         => 'network',
                        'ip_.*'           => 'network',
                        'vlan_.*'         => 'network',
                        'postfix_.*'      => 'postfix',
                        'forks'           => 'processes',
                        'processes'       => 'processes',
                        'vmstat'          => 'processes',
                        'cpu'             => 'system',
                        'entropy'         => 'system',
                        'interrupts'      => 'system',
                        'irqstats'        => 'system',
                        'load'            => 'system',
                        'memory'          => 'system',
                        'open_.*'         => 'system',
                        'swap'            => 'system',
                        'ntp_.*'          => 'time',
                        'mysql_.*'        => 'mysql',
                        'pg_.*'           => 'postgresql');

    $category = 'other';
    foreach($classifier as $key => $value) {
        if(preg_match("/^$key$/", $graph_id) > 0) {
            $category = $value;
            break;
        }
    }

    return($category);
}

function _get_caption($graph_id)
{
    $caption_id_overrides = array('if_err_(.*)' => array('caption_id' => 'interface_err'),
                                  'if_(.*)' => array('caption_id' => 'interface'),
                                  'ip_(.*)' => array('caption_id' => 'ip_address'),
                                  'vlan_(.*)' => array('caption_id' => 'vlan'),
                                  'smart_(.*)' => array('caption_id' => 'smart'));
    $caption['caption_id'] = $graph_id;
    $caption['caption_argument'] = '';
    foreach($caption_id_overrides as $regexp => $override) {
        $matches = array();
        if(preg_match("/^$regexp$/", $graph_id, &$matches) > 0) {
            $caption['caption_id'] = $override['caption_id'];
            $caption['caption_argument'] = $matches[1];
            break;
        }
    }

    return($caption);
}

function dwho_munin_graphs($urldir, $domain)
{
    $graphs = _get_all_graphs($urldir);

    $captions = array();
    foreach($graphs as $graph)
    {
        list($graph_id, $freq, $fmt) = split("[\.-]", $graph);

        $category = _get_category($graph_id);
        $caption = _get_caption($graph_id);

        if(!array_key_exists($category, $captions)) {
            $captions[$category] = array();
        }

        $captions[$category][$graph_id] = $caption;
    }

    return($captions);
}

?>
