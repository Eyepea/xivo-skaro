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

$domain     = 'localdomain/localhost.localdomain';
$basename   = ''; //XIVO.$domain

require_once(DWHO_PATH_ROOT.DIRECTORY_SEPARATOR.'munin.inc');

$basedir        = "img/graphs/munin/$domain/";
$graph_captions_by_module = dwho_munin_graphs($basedir, $domain);
$module_graph_captions = $graph_captions_by_module[$module];
$module_graphs = array_keys($module_graph_captions);
sort($module_graphs);

if(isset($_QR['zoom']))
{
    // get previous/next graphs
    list($domain, $zoomod, $zoofreq)    = split('-', $_QR['zoom']);
    $current = array(
        array_search($zoomod , $module_graphs),   // module index
        array_search($zoofreq, $freqs)          // frequency index
     );

    $previous  = array(
        $current[0],
        ($current[1] + count($freqs) - 1) % count($freqs)
    );

    if($previous[1] == count($freqs) - 1)
        $previous[0] = ($current[0] == 0)?null:$current[0] - 1;

    $prev_lnk = is_null($previous[0])?
            null:
            sprintf("%s-%s-%s", $domain, $module_graphs[$previous[0]], $freqs[$previous[1]]);


    $next = array(
        $current[0],
        ($current[1] + 1) % count($freqs)
    );

    if($next[1] == 0)
        $next[0] = ($current[0] == count($module_graphs)-1)?null:$current[0] + 1;

    $next_lnk = is_null($next[0])?
            null:
            sprintf("%s-%s-%s", $domain, $module_graphs[$next[0]], $freqs[$next[1]]);


    $_TPL->set_var('zoom', $_QR['zoom']);
    $_TPL->set_var('prev', $prev_lnk);
    $_TPL->set_var('next', $next_lnk);
}

$_TPL->set_var('basedir', $basedir);
$_TPL->set_var('basename', $basename);
$_TPL->set_var('domain', $domain);
$_TPL->set_var('graphs', $module_graphs);
$_TPL->set_var('graph_captions', $module_graph_captions);
$_TPL->set_var('freqs', $freqs);
$_TPL->set_var('tree', $graph_captions_by_module);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/graphs/graphs');

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_css('css/graphs/graphs.css');

$_TPL->set_bloc('main',"graphs/munin/$module");
$_TPL->set_struct('graphs/index');
$_TPL->display('index');

?>
