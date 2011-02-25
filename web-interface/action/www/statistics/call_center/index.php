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

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

if(xivo::load_class('xivo_statistics_general',XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics','general',false) === false)
	die('Can\'t load xivo_statistics_general object');

$stats_general = new xivo_statistics_general(&$_XS);
$stats_general->parse_log();

$tpl_statistics->set_data_custom('axetype',$axetype);
$tpl_statistics->set_data_custom('listtype',$stats_general->get_list_by_type());

$tpl_statistics->set_name('general');

$tpl_statistics->set_rows('total',array(array('name' => 'total')),'name');

$tpl_statistics->set_data_custom('general',$stats_general->_result);

$tpl_statistics->set_col_struct('total');
$tpl_statistics->add_col('presented',
					'direct',
					'custom:general,total,enterqueue');
$tpl_statistics->add_col('connect',
					'direct',
					'custom:general,total,connect');
$tpl_statistics->add_col('ringnoanswer',
					'direct',
					'custom:general,total,ringnoanswer');
$tpl_statistics->add_col('abandon',
					'direct',
					'custom:general,total,abandon');
$tpl_statistics->add_col('connect',
					'direct',
					'custom:general,total,connect');
$tpl_statistics->add_col('completeagent',
					'direct',
					'custom:general,total,completeagent');
$tpl_statistics->add_col('completecaller',
					'direct',
					'custom:general,total,completecaller');
$tpl_statistics->add_col('transfer',
					'direct',
					'custom:general,total,transfer');

$tpl_statistics->gener_table();
$table_total = $tpl_statistics->render_html(false,false);
$tpl_statistics->reset_col();

$tpl_statistics->set_col_struct('time');
$tpl_statistics->add_col('holdtime',
					'direct',
					'custom:general,total,holdtime');
$tpl_statistics->add_col('calltime',
					'direct',
					'custom:general,total,calltime');
$tpl_statistics->add_col('ringtime',
					'direct',
					'custom:general,total,ringtime');
$tpl_statistics->add_col('pausetime',
					'direct',
					'custom:general,total,pausetime');
$tpl_statistics->add_col('traitmenttime',
					'direct',
					'custom:general,total,traitmenttime');

$tpl_statistics->gener_table();
$table_time = $tpl_statistics->render_html(false,false);
$tpl_statistics->reset_col();

$tpl_statistics->set_col_struct('average');
$tpl_statistics->add_col('av-holdtime',
					'expression',
					'{custom:general,total,holdtime}/{custom:general,total,connect}',
					'time');
$tpl_statistics->add_col('av-calltime',
					'expression',
					'{custom:general,total,calltime}/{custom:general,total,connect}',
					'time');
$tpl_statistics->add_col('av-ringtime',
					'expression',
					'{custom:general,total,ringtime}/{custom:general,total,enterqueue}',
					'time');
$tpl_statistics->add_col('av-pausetime',
					'expression',
					'{custom:general,total,pausetime}/{custom:general,total,enterqueue}',
					'time');
$tpl_statistics->add_col('av-traitmenttime',
					'expression',
					'{custom:general,total,traitmenttime}/{custom:general,total,enterqueue}',
					'time');

$tpl_statistics->gener_table();
$table_average = $tpl_statistics->render_html(false,false);
$tpl_statistics->reset_col();

$tpl_statistics->set_col_struct('percent');
$tpl_statistics->add_col('answered_rated',
					'expression',
					'{custom:general,total,connect}/{custom:general,total,enterqueue}',
					'percent');
$tpl_statistics->add_col('abandon_rated',
					'expression',
					'{custom:general,total,abandon}/{custom:general,total,enterqueue}',
					'percent');
$tpl_statistics->add_col('ringnoanswer_rated',
					'expression',
					'{custom:general,total,ringnoanswer}/{custom:general,total,enterqueue}',
					'percent');
$tpl_statistics->add_col('completeagent_rated',
					'expression',
					'{custom:general,total,completeagent}/{custom:general,total,connect}',
					'percent');
$tpl_statistics->add_col('completecaller_rated',
					'expression',
					'{custom:general,total,completecaller}/{custom:general,total,connect}',
					'percent');

$tpl_statistics->gener_table();
$table_percent = $tpl_statistics->render_html(false,false);
$tpl_statistics->reset_col();

$_TPL->set_var('table_total',$table_total);
$_TPL->set_var('table_time',$table_time);
$_TPL->set_var('table_average',$table_average);
$_TPL->set_var('table_percent',$table_percent);
$_TPL->set_var('xivo_statistics',$tpl_statistics);

$bench_end = microtime(true);
$_TPL->set_var('bench',($bench_end - $bench_start));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics/call_center');

$_TPL->set_bloc('main',"statistics/call_center/index");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
