<?php

#
# XiVO Web-Interface
# Copyright (C) 2010  Proformatique <technique@proformatique.com>
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

include(dirname(__FILE__).'/common.php');

/*
// Dataset definition 
 $DataSet = new pData;
 $DataSet->AddPoint(array(1,4,3,4,3,3,2,1,0,7,4,3,2,3,3,5,1,0,7),"Serie1");
 $DataSet->AddPoint(array(1,4,2,6,2,3,0,1,5,1,2,4,5,2,1,0,6,4,2),"Serie2");
 $DataSet->AddAllSeries();
 $DataSet->SetAbsciseLabelSerie();
 $DataSet->SetSerieName("January","Serie1");
 $DataSet->SetSerieName("February","Serie2");

 // Initialise the graph
 $Test = new pChart(700,230);
 $Test->setFixedScale(-2,8);
 $Test->setFontProperties($glibpchart."tahoma.ttf",8);
 $Test->setGraphArea(50,30,585,200);
 $Test->drawFilledRoundedRectangle(7,7,693,223,5,240,240,240);
 $Test->drawRoundedRectangle(5,5,695,225,5,230,230,230);
 $Test->drawGraphArea(255,255,255,TRUE);
 $Test->drawScale($DataSet->GetData(),$DataSet->GetDataDescription(),SCALE_NORMAL,150,150,150,TRUE,0,2);
 $Test->drawGrid(4,TRUE,230,230,230,50);

 // Draw the 0 line
 $Test->setFontProperties($glibpchart."tahoma.ttf",6);
 $Test->drawTreshold(0,143,55,72,TRUE,TRUE);

 // Draw the cubic curve graph
 $Test->drawCubicCurve($DataSet->GetData(),$DataSet->GetDataDescription());

 // Finish the graph
 $Test->setFontProperties($glibpchart."tahoma.ttf",8);
 $Test->drawLegend(600,30,$DataSet->GetDataDescription(),255,255,255);
 $Test->setFontProperties($glibpchart."tahoma.ttf",10);
 $Test->drawTitle(50,22,"Example 2",50,50,50,585);
 #$Test->Stroke();
 $Test->Render($gdir.'example2.png');
*/
 
$rows = array();
$statistics->set_rows($rows);

$appqueue = &$ipbx->get_application('queue');
$list_queue = $appqueue->get_queues_list();

$appqueue_log = &$ipbx->get_application('queue_log');
$queue_log = $appqueue_log->get_queue_logs_list();

$appstats_conf = &$_XOBJ->get_application('stats_conf');
$conf = $appstats_conf->get(5);

$statistics->init_queue($list_queue);

$_TPL->set_var('conf',$conf);
$_TPL->set_var('ls_queue',$list_queue);
$_TPL->set_var('queue_log',$queue_log);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');

$_TPL->set_bloc('main',"statistics/stats1");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>

