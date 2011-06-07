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

$bench_start = microtime(true);
$base_memory = memory_get_usage();

$_I18N->load_file('tpl/www/bloc/statistics/statistics');

require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'date.inc'));
require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'jqplot.inc'));

$xivo_jqplot = new xivo_jqplot;

$listaxetype = array('period','day','week','month');
$listop = array('exact','begin','contain','end');
$listchannel = array(
			XIVO_SRE_IPBX_AST_CHAN_SIP		=> XIVO_SRE_IPBX_AST_CHAN_SIP,
			XIVO_SRE_IPBX_AST_CHAN_IAX		=> XIVO_SRE_IPBX_AST_CHAN_IAX,
			XIVO_SRE_IPBX_AST_CHAN_LOCAL	=> XIVO_SRE_IPBX_AST_CHAN_LOCAL,
			XIVO_SRE_IPBX_AST_CHAN_AGENT	=> XIVO_SRE_IPBX_AST_CHAN_AGENT,
			XIVO_SRE_IPBX_AST_CHAN_ZAP		=> XIVO_SRE_IPBX_AST_CHAN_ZAP,
			XIVO_SRE_IPBX_AST_CHAN_DAHDI	=> XIVO_SRE_IPBX_AST_CHAN_DAHDI,
			XIVO_SRE_IPBX_AST_CHAN_CAPI		=> XIVO_SRE_IPBX_AST_CHAN_CAPI,
			XIVO_SRE_IPBX_AST_CHAN_MISDN	=> XIVO_SRE_IPBX_AST_CHAN_MISDN,
			XIVO_SRE_IPBX_AST_CHAN_MGCP		=> XIVO_SRE_IPBX_AST_CHAN_MGCP,
			XIVO_SRE_IPBX_AST_CHAN_SCCP		=> XIVO_SRE_IPBX_AST_CHAN_SCCP,
			XIVO_SRE_IPBX_AST_CHAN_H323		=> XIVO_SRE_IPBX_AST_CHAN_H323,
			XIVO_SRE_IPBX_AST_CHAN_UNKNOWN	=> 'unknown',
			'others'			=> 'others');

$act = isset($_QR['act']) === true ? $_QR['act'] : '';
$axetype = isset($_QR['axetype']) === false ? 'day' : $_QR['axetype'];
$axetype = empty($axetype) === true ? 'day' : $axetype;

if (in_array($axetype,$listaxetype) === false)
	$axetype = 'day';

// default interval for date
dwho_date::init_infocal('-1 day');

$search = $_QR;
$infocal = dwho_date::set_infocal($axetype,$_QR);
$search['dbeg'] = $infocal['dbeg'];
$search['dend'] = $infocal['dend'];

$cdrinfo = array();
$cdrinfo['src'] = isset($_QR['src']) === false ? '' : $_QR['src'];
$cdrinfo['srcformat'] = isset($_QR['srcformat']) === false ? 'exact' : $_QR['srcformat'];
$cdrinfo['dst'] = isset($_QR['dst']) === false ? '' : $_QR['dst'];
$cdrinfo['dstformat'] = isset($_QR['dstformat']) === false ? 'exact' : $_QR['dstformat'];
$cdrinfo['channel'] = isset($_QR['channel']) === false ? '' : $_QR['channel'];

$_TPL->set_var('infocal',$infocal);
$_TPL->set_var('cdrinfo',$cdrinfo);
$_TPL->set_var('axetype',$axetype);
$_TPL->set_var('listaxetype',$listaxetype);
$_TPL->set_var('listop',$listop);
$_TPL->set_var('listchannel',$listchannel);

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/statistics/common.js');

?>