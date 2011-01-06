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

include(dirname(__FILE__).'/common.php');

if(xivo::load_class('xivo_statistics_general',XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics','general',false) === false)
	die('Can\'t load xivo_statistics_general object');

$stats_general = new xivo_statistics_general(&$_XOBJ,&$ipbx);
if (isset($_QR['confid']) === true)
	$stats_general->set_idconf($_QR['confid'],true);
$stats_general->parse_log();

$xivo_statistics->set_name('general');

$xivo_statistics->set_rows('total',array(array('name' => 'total')),'name');

$xivo_statistics->set_data_custom('general',$stats_general->_result);

$xivo_statistics->set_col_struct('total');
$xivo_statistics->add_col('presented',
					'direct',
					'custom:general,total,enterqueue');
$xivo_statistics->add_col('answered',
					'direct',
					'custom:general,total,connect');
$xivo_statistics->add_col('ringnoanswer',
					'direct',
					'custom:general,total,ringnoanswer');
$xivo_statistics->add_col('abandoned',
					'direct',
					'custom:general,total,abandon');
$xivo_statistics->add_col('connect',
					'direct',
					'custom:general,total,connect');
$xivo_statistics->add_col('completeagent',
					'direct',
					'custom:general,total,completeagent');
$xivo_statistics->add_col('completecaller',
					'direct',
					'custom:general,total,completecaller');
$xivo_statistics->add_col('transfer',
					'direct',
					'custom:general,total,transfer');

$xivo_statistics->gener();
#$xivo_statistics->render_graph();
$table_total = $xivo_statistics->render_html(false,false);
$xivo_statistics->reset_col();

$xivo_statistics->set_col_struct('time');
$xivo_statistics->add_col('holdtime',
					'direct',
					'custom:general,total,holdtime');
$xivo_statistics->add_col('calltime',
					'direct',
					'custom:general,total,calltime');
$xivo_statistics->add_col('ringtime',
					'direct',
					'custom:general,total,ringtime');
$xivo_statistics->add_col('pausetime',
					'direct',
					'custom:general,total,pausetime');
$xivo_statistics->add_col('traitmenttime',
					'direct',
					'custom:general,total,traitmenttime');

$xivo_statistics->gener();
#$xivo_statistics->render_graph();
$table_time = $xivo_statistics->render_html(false,false);
$xivo_statistics->reset_col();

$xivo_statistics->set_col_struct('average');
$xivo_statistics->add_col('av-holdtime',
					'expression',
					'{custom:general,total,holdtime}/{custom:general,total,connect}',
					'time');
$xivo_statistics->add_col('av-calltime',
					'expression',
					'{custom:general,total,calltime}/{custom:general,total,connect}',
					'time');
$xivo_statistics->add_col('av-ringtime',
					'expression',
					'{custom:general,total,ringtime}/{custom:general,total,enterqueue}',
					'time');
$xivo_statistics->add_col('av-pausetime',
					'expression',
					'{custom:general,total,pausetime}/{custom:general,total,enterqueue}',
					'time');
$xivo_statistics->add_col('av-traitmenttime',
					'expression',
					'{custom:general,total,traitmenttime}/{custom:general,total,enterqueue}',
					'time');

$xivo_statistics->gener();
#$xivo_statistics->render_graph();
$table_average = $xivo_statistics->render_html(false,false);
$xivo_statistics->reset_col();

$xivo_statistics->set_col_struct('percent');
$xivo_statistics->add_col('answered_rated',
					'expression',
					'{custom:general,total,connect}/{custom:general,total,enterqueue}',
					'percent');
$xivo_statistics->add_col('abandon_rated',
					'expression',
					'{custom:general,total,abandon}/{custom:general,total,enterqueue}',
					'percent');
$xivo_statistics->add_col('ringnoanswer_rated',
					'expression',
					'{custom:general,total,ringnoanswer}/{custom:general,total,enterqueue}',
					'percent');
$xivo_statistics->add_col('completeagent_rated',
					'expression',
					'{custom:general,total,completeagent}/{custom:general,total,connect}',
					'percent');
$xivo_statistics->add_col('completecaller_rated',
					'expression',
					'{custom:general,total,completecaller}/{custom:general,total,connect}',
					'percent');

$xivo_statistics->gener();
#$xivo_statistics->render_graph();
$table_percent = $xivo_statistics->render_html(false,false);
$xivo_statistics->reset_col();

$_TPL->set_var('confid',$stats_general->get_idconf());
$_TPL->set_var('table_total',$table_total);
$_TPL->set_var('table_time',$table_time);
$_TPL->set_var('table_average',$table_average);
$_TPL->set_var('table_percent',$table_percent);

$bench_end = microtime(true);
$_TPL->set_var('bench',($bench_end - $bench_start));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics');

$_TPL->set_bloc('main',"statistics/index");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
