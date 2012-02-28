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

$form = &$this->get_module('form');
$url = &$this->get_module('url');
$dhtml = &$this->get_module('dhtml');

$element = $this->get_var('element');
$pager = $this->get_var('pager');

$result = $this->get_var('result');
$info = $this->get_var('info');
$context_list = $this->get_var('context_list');

if(($dcontext_custom = (string) $this->get_var('dcontext-custom')) !== ''):
	$dcontext = 'custom';
else:
	$dcontext = (string) $info['dcontext'];
endif;

if(dwho_has_len($info['amaflags']) === false):
	$amaflags = null;
else:
	$amaflags = dwho_uint($info['amaflags']);
endif;

$page = $exportcsv = '';

if($result === false):
	$dhtml->write_js('dwho_submenu.set_option(\'onload_last\',true);');
else:
	$dhtml->write_js('dwho_submenu.set_options({
		\'onload_tab\':		"dwsm-tab-2",
		\'onload_part\':	"sb-part-result"});');

	if($info !== null):
		$page_query = $info;
		$page_query['search'] = 1;
		$page_query['act'] = 'search';
		$page = $url->pager($pager['pages'],
							$pager['page'],
							$pager['prev'],
							$pager['next'],
							'',
							$page_query);
	endif;

	$exportcsv_query = $info;
	$exportcsv_query['search'] = 1;
	$exportcsv_query['act'] = 'exportcsv';
endif;

?>
<div id="sr-cel" class="b-infos b-form">
	<h3 class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('title_content_name');?></span>
		<span class="span-right">&nbsp;</span>
	</h3>

<div class="sb-smenu">
	<ul>
<?php
	if($result === false):
?>
		<li id="dwsm-tab-1"
		    class="dwsm-blur-last"
		    onclick="dwho_submenu.select(this,'sb-part-first',1);"
		    onmouseout="dwho_submenu.blur(this,1);"
		    onmouseover="dwho_submenu.focus(this,1);">
			<div class="tab">
				<span class="span-center"><a href="#" onclick="return(false);"><?=$this->bbf('smenu_search');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
<?php
	else:
?>
		<li id="dwsm-tab-1"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-first');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center"><a href="#" onclick="return(false);"><?=$this->bbf('smenu_search');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-2"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-result');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center"><a href="#" onclick="return(false);"><?=$this->bbf('smenu_result');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-3"
		    class="dwsm-blur-last"
		    onclick="dwho_submenu.select(this,'sb-part-result',1);
			     location.href = dwho.dom.node.firstchild(
						dwho.dom.node.firstchild(
							dwho.dom.node.firstchild(this)));"
		    onmouseout="dwho_submenu.blur(this,1);" onmouseover="dwho_submenu.focus(this,1);">
			<div class="tab">
				<span class="span-center"><?=$url->href_html($this->bbf('smenu_exportcsv'),
										'',
										$exportcsv_query,
										'onclick="return(false);"');?></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
<?php
	endif;
?>
	</ul>
</div>

<div class="sb-content">

<div id="sb-part-first"<?=($result !== false ? ' class="b-nodisplay"' : '')?>>
<form action="#" method="post" accept-charset="utf-8">
<?=$form->hidden(array('name' => DWHO_SESS_NAME,'value' => DWHO_SESS_ID))?>
<?=$form->hidden(array('name' => 'act','value' => 'search'))?>
<?=$form->hidden(array('name' => 'fm_send','value' => 1))?>
<div class="fm-paragraph fm-desc-inline">
	<div class="fm-multifield">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_dbeg'),
				  'paragraph'	=> false,
				  'name'	=> 'dbeg',
				  'labelid'	=> 'dbeg',
				  'default'	=> dwho_i18n::strftime_l('%Y-%m-%d',null),
				  'value'	=> $info['dbeg']));
?>
	</div>
	<div class="fm-multifield">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_dend'),
				  'paragraph'	=> false,
				  'name'	=> 'dend',
				  'labelid'	=> 'dend',
				  'value'	=> $info['dend']));
?>
	</div>
</div>

<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_channel'),
				    'name'	=> 'channel',
				    'labelid'	=> 'channel',
				    'empty'	=> true,
				    'bbf'	=> 'fm_channel-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['channel']['default'],
				    'selected'	=> $info['channel']),
			      $element['channel']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_amaflags'),
				    'name'	=> 'amaflags',
				    'labelid'	=> 'amaflags',
				    'empty'	=> true,
				    'bbf'	=> 'ast_amaflag_name_info',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['amaflags']['default'],
				    'selected'	=> $amaflags),
			      $element['amaflags']['value']);

if($context_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_dcontext'),
				    'name'	=> 'dcontext',
				    'labelid'	=> 'dcontext',
				    'empty'	=> true,
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'bbf'	=> 'fm_dcontext-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> $dcontext),
			      $context_list);
else:
	echo	$form->text(array('desc'	=> $this->bbf('fm_dcontext'),
				  'name'	=> 'dcontext',
				  'labelid'	=> 'dcontext',
				  'default'	=> $element['dcontext']['default'],
				  'value'	=> $info['dcontext']));
endif;
?>


<div class="fm-paragraph fm-multifield">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_src'),
				  'paragraph'	=> false,
				  'name'	=> 'src',
				  'labelid'	=> 'src',
				  'size'	=> 15,
				  'default'	=> $element['src']['default'],
				  'value'	=> $info['src'])),

		$form->select(array('paragraph'	=> false,
				    'name'	=> 'srcformat',
				    'labelid'	=> 'srcformat',
				    'key'	=> false,
				    'bbf'	=> 'fm_search-format',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['srcformat']['default'],
				    'selected'	=> $info['srcformat']),
			      $element['srcformat']['value']);
?>
</div>

<div class="fm-paragraph fm-multifield">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_dst'),
				  'paragraph'	=> false,
				  'name'	=> 'dst',
				  'labelid'	=> 'dst',
				  'size'	=> 15,
				  'default'	=> $element['dst']['default'],
				  'value'	=> $info['dst'])),

		$form->select(array('paragraph'	=> false,
				    'name'	=> 'dstformat',
				    'labelid'	=> 'dstformat',
				    'key'	=> false,
				    'bbf'	=> 'fm_search-format',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['dstformat']['default'],
				    'selected'	=> $info['dstformat']),
			      $element['dstformat']['value']);
?>
</div>

<div class="fm-paragraph fm-multifield">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_accountcode'),
				  'paragraph'	=> false,
				  'name'	=> 'accountcode',
				  'labelid'	=> 'accountcode',
				  'size'	=> 15,
				  'default'	=> $element['accountcode']['default'],
				  'value'	=> $info['accountcode'])),

		$form->select(array('paragraph'	=> false,
				    'name'	=> 'accountcodeformat',
				    'labelid'	=> 'accountcodeformat',
				    'key'	=> false,
				    'bbf'	=> 'fm_search-format',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['accountcodeformat']['default'],
				    'selected'	=> $info['accountcodeformat']),
			      $element['accountcodeformat']['value']);
?>
</div>

<div class="fm-paragraph fm-multifield">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_userfield'),
				    'paragraph'	=> false,
				    'name'	=> 'userfield',
				    'labelid'	=> 'userfield',
				    'size'	=> 15,
				    'default'	=> $element['userfield']['default'],
				    'value'	=> $info['userfield'])),

		$form->select(array('paragraph'	=> false,
				    'name'	=> 'userfieldformat',
				    'labelid'	=> 'userfieldformat',
				    'key'	=> false,
				    'bbf'	=> 'fm_search-format',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['userfieldformat']['default'],
				    'selected'	=> $info['userfieldformat']),
			      $element['userfieldformat']['value']);
?>
</div>
<?=$form->submit(array('name' => 'submit','id' => 'it-submit','value' => $this->bbf('fm_bt-search')))?>

</form>
</div>


<?php
	if($result !== false):
?>
<div id="sb-part-result">
<div class="sb-list">
<?php
	if($page !== ''):
		echo	'<div class="b-total">',
			$this->bbf('number_cel-result','<b>'.$this->get_var('total').'</b>'),
			'</div>',
			'<div class="b-page">',
			$page,
			'</div>',
			'<div class="clearboth"></div>';
	endif;
?>
	<table>
		<tr class="sb-top">
			<th class="th-left"><?=$this->bbf('col_calldate');?></th>
			<th class="th-center"><?=$this->bbf('col_src');?></th>
			<th class="th-center"><?=$this->bbf('col_dst');?></th>
			<th class="th-right"><?=$this->bbf('col_duration');?></th>
		</tr>
<?php
	if($result === null || ($nb = count($result)) === 0):
?>
		<tr>
			<td colspan="4" class="td-single"><?=$this->bbf('no_cel-result');?></td>
		</tr>
<?
	else:
		for($i = 0;$i < $nb;$i++):
			$ref = &$result[$i];
			$mod = ($i % 2) + 1;

			$ref0 = array_shift($ref);
			$ref1 = array_shift($ref);

			if(!isset($ref0['from']) || dwho_has_len($ref0['from']) === false):
				$src = '-';
			else:
				$src = dwho_htmlen(dwho_trunc($ref0['from'],25,'...'));
			endif;

			if(!isset($ref0['to']) || dwho_has_len($ref0['to']) === false):
				$dst = '-';
			else:
				$dst = dwho_htmlen(dwho_trunc($ref0['to'],25,'...'));
			endif;

			$duration = dwho_calc_duration(null,null,$ref0['duration'],true);

			if(($cnt_duration = count($duration)) === 4):
				$bbf_duration = 'entry_duration-dayhourminsec';
			elseif($cnt_duration === 3):
				$bbf_duration = 'entry_duration-hourminsec';
			elseif($cnt_duration === 2):
				$bbf_duration = 'entry_duration-minsec';
			else:
				$bbf_duration = 'entry_duration-sec';
			endif;

			$ringing = 0;
			if (isset($ref0['ringing']))
				$ringing = $ref0['ringing'];

			$ringingsec = dwho_calc_duration(null,null,$ringing,true);

			if(($cnt_ringing = count($ringingsec)) === 4):
				$bbf_ringing = 'entry_billsec-dayhourminsec';
			elseif($cnt_ringing === 3):
				$bbf_ringing = 'entry_billsec-hourminsec';
			elseif($cnt_ringing === 2):
				$bbf_ringing = 'entry_billsec-minsec';
			else:
				$bbf_ringing = 'entry_billsec-sec';
			endif;

			$billsec = dwho_calc_duration(null,null,$ref0['duration'],true);

			if(($cnt_billsec = count($billsec)) === 4):
				$bbf_billsec = 'entry_billsec-dayhourminsec';
			elseif($cnt_billsec === 3):
				$bbf_billsec = 'entry_billsec-hourminsec';
			elseif($cnt_billsec === 2):
				$bbf_billsec = 'entry_billsec-minsec';
			else:
				$bbf_billsec = 'entry_billsec-sec';
			endif;

			if($ref0['channame'] === XIVO_SRE_IPBX_AST_CHAN_UNKNOWN)
				$ref0['channame'] = $this->bbf('entry_channel','unknown');
?>
	<tr class="sb-content l-infos-<?=$mod?>on2 curpointer"
	    onmouseover="this.tmp = this.className;
			 this.className = 'sb-content l-infos-over curpointer';"
	    onmouseout="this.className = this.tmp;"
	    onclick="this.entryline = dwho_eid('cel-infos-<?=$i?>').style.display;
		     dwho_eid('cel-infos-<?=$i?>').style.display = this.entryline === '' || this.entryline === 'none'
								   ? 'table-row'
								   : 'none';">
		<td class="td-left">
			<a href="#" onclick="return(false);"><?=dwho_i18n::strftime_l(
								$this->bbf('date_format_yymmddhhiiss'),
								null,
								strtotime($ref0['dstart']));?></a>
		</td>
		<td><?=$src?></td>
		<td><?=$dst?></td>
		<td class="td-right"><?=$this->bbf($bbf_duration,$duration);?></td>
	</tr>
	<tr id="cel-infos-<?=$i?>" class="sb-content l-infos-<?=$mod?>on2 b-nodisplay cel-infos">
		<td colspan="4" class="td-single">
		<dl>
		<?php
			if(dwho_has_len($ref0['channame']) === true):
				echo	'<dt>',$this->bbf('entry_channel'),'</dt>',
					'<dd title="',dwho_htmlen($ref0['channame']),'">',
					dwho_htmlen(dwho_trunc($ref0['channame'],35,'...',false)),
					'<br /></dd>';
			endif;

			if(dwho_has_len($ref0['amaflagsmeta']) === true):
				echo	'<dt>',$this->bbf('entry_amaflagsmeta'),'</dt>',
					'<dd>',$this->bbf('ast_amaflag_name_info',$ref0['amaflagsmeta']),'<br /></dd>';
			endif;

			echo	'<dt>',$this->bbf('entry_answer'),'</dt>',
				'<dd title="',dwho_htmlen($ref0['answer']),'">',
				$this->bbf('call_is_answer',(int) $ref0['answer']),
				'<br /></dd>';

			if(dwho_has_len($ref0['accountcode']) === true):
				echo	'<dt>',$this->bbf('entry_accountcode'),'</dt>',
					'<dd title="',dwho_htmlen($ref0['accountcode']),'">',
					dwho_htmlen(dwho_trunc($ref0['accountcode'],20,'...',false)),
					'<br /></dd>';
			endif;

			if(dwho_has_len($ref0['userfield']) === true):
				echo	'<dt>',$this->bbf('entry_userfield'),'</dt>',
					'<dd title="',dwho_htmlen($ref0['userfield']),'">',
					dwho_htmlen(dwho_trunc($ref0['userfield'],20,'...',false)),
					'<br /></dd>';
			endif;
		?>
		</dl>
		<dl>
		<?php
			if(dwho_has_len($ref0['context']) === true):
				echo	'<dt>',$this->bbf('entry_dcontext'),'</dt>',
					'<dd title="',dwho_htmlen($ref0['context']),'">',
					dwho_htmlen(dwho_trunc($ref0['context'],30,'...',false)),
					'<br /></dd>';
			endif;

			if(dwho_has_len($ref1['channame']) === true):
				echo	'<dt>',$this->bbf('entry_dstchannel'),'</dt>',
					'<dd title="',dwho_htmlen($ref1['channame']),'">',
					dwho_htmlen(dwho_trunc($ref1['channame'],20,'...',false)),
					'<br /></dd>';
			endif;

			echo	'<dt>',$this->bbf('entry_billsec'),'</dt>',
				'<dd>',$this->bbf($bbf_billsec,$billsec),'<br /></dd>';

			echo	'<dt>',$this->bbf('entry_ringsec'),'</dt>',
				'<dd>',$this->bbf($bbf_ringing,$ringingsec),'<br /></dd>';

			if(dwho_has_len($ref0['uniqueid']) === true):
				echo	'<dt>',$this->bbf('entry_uniqueid'),'</dt>',
					'<dd title="',dwho_htmlen($ref0['uniqueid']),'">',
					dwho_htmlen(dwho_trunc($ref0['uniqueid'],20,'...',false)),
					'<br /></dd>';
			endif;
		?>
			</dl>
		</td>
	</tr>
<?php
		endfor;
	endif;
?>
	</table>

<?php
	if($page !== ''):
		echo	'<div class="b-total">',
			$this->bbf('number_cel-result','<b>'.$this->get_var('total').'</b>'),
			'</div>',
			'<div class="b-page">',$page,'</div>',
			'<div class="clearboth"></div>';
	endif;
?>
</div>
</div>
<?php
	endif;
?>
	</div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
