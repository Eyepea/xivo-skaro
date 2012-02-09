
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

dwho::load_class('dwho_network');

$url = &$this->get_module('url');
$form = &$this->get_module('form');
$dhtml = &$this->get_module('dhtml');

$pager = $this->get_var('pager');
$act = $this->get_var('act');

$page = $url->pager($pager['pages'],
		    $pager['page'],
		    $pager['prev'],
		    $pager['next'],
		    'xivo/configuration/network/interface',
		    array('act' => $act));

?>
<div class="b-list">
<?php
	if($page !== ''):
		echo '<div class="b-page">',$page,'</div>';
	endif;
?>
<form action="#" name="fm-netiface-list" method="post" accept-charset="utf-8">
<?php
	echo	$form->hidden(array('name'	=> DWHO_SESS_NAME,
				    'value'	=> DWHO_SESS_ID)),

		$form->hidden(array('name'	=> 'act',
				    'value'	=> $act)),

		$form->hidden(array('name'	=> 'page',
				    'value'	=> $pager['page']));
?>
<table id="table-main-listing">
	<tr class="sb-top">
		<th class="th-left xspan"><span class="span-left">&nbsp;</span></th>
		<th class="th-center"><?=$this->bbf('col_ifname');?></th>
		<th class="th-center"><?=$this->bbf('col_hwaddress');?></th>
		<th class="th-center"><?=$this->bbf('col_networktype');?></th>
		<th class="th-center"><?=$this->bbf('col_method');?></th>
		<th class="th-center"><?=$this->bbf('col_address');?></th>
		<th class="th-center"><?=$this->bbf('col_gateway');?></th>
		<th class="th-center col-action"><?=$this->bbf('col_action');?></th>
		<th class="th-right xspan"><span class="span-right">&nbsp;</span></th>
	</tr>
<?php
	if(($list = $this->get_var('list')) === false || ($nb = count($list)) === 0):
?>
	<tr class="sb-content">
		<td colspan="11" class="td-single"><?=$this->bbf('no_netiface');?></td>
	</tr>
<?php
	else:
		for($i = 0;$i < $nb;$i++):
			$netinfo = &$list[$i]['netinfo'];
			$netiface = &$list[$i]['netiface'];

			$id			= '';
			$gateway	= '-';
			$ifname		= '';
			$hwtype		= '';
			$hwtypeid	= 0;
			$hwaddress	= '-';
			$methodname	= null;
			$method		= '-';
			$address	= '';
			$vlanid		= '-';
			$icon		= 'unavailable';

			$disableable = isset($list[$i]['disableable']) ? $list[$i]['disableable'] : false;

			if(empty($netinfo) === false):
				$ifname = $netinfo['interface'];

				if(dwho_has_len($netinfo,'address') === true):
					$address = $netinfo['address'];
				endif;

				if(dwho_has_len($netinfo,'method') === true):
					$methodname	= $netinfo['method'];
					$method		= $this->bbf('network_method',$netinfo['method']);
				endif;

				if(dwho_has_len($netinfo,'vlan-id') === true):
					$vlanid = $netinfo['vlan-id'];
				endif;

				if($netinfo['hwtype'] !== false):
					$hwtype = $netinfo['hwtype'];
				endif;

				if($netinfo['hwtypeid'] !== false):
					$hwtypeid = dwho_uint($netinfo['hwtypeid']);
				endif;

				if($netinfo['hwaddress'] !== false
				&& dwho_network::valid_macaddr($netinfo['hwaddress']) === true):
					$hwaddress = $netinfo['hwaddress'];
				endif;

				if($netinfo['carrier'] === true && $netinfo['flags']['up'] === true):
					$icon = 'enable';
				endif;
			endif;

			$voip_iface = false;
			$networktype = 'data';
			if(empty($netiface) === false):
				$id			= $netiface['id'];
				$ifname		= $netiface['ifname'];
				$hwtype		= $netiface['hwtype'];
				$hwtypeid	= dwho_uint($netiface['hwtypeid']);
				$methodname	= $netiface['method'];
				$method		= $this->bbf('network_method',$netiface['method']);
				$networktype	= $netiface['networktype'];


				if(dwho_has_len($netiface['address']) === true):
					$address = $netiface['address'];
				endif;

				if(dwho_has_len($netiface['vlanid']) === true):
					$vlanid = $netiface['vlanid'];
				endif;

				if(dwho_has_len($netiface,'gateway') === true):
					$gateway = $netiface['gateway'];
				endif;

				if($netiface['disable'] === true):
					$icon = 'disable';
				endif;

				if ($netiface['networktype'] === 'voip'):
					$voip_iface = true;
				endif;
			endif;

			if(dwho_has_len($address) === false):
				$address = '-';
			endif;
?>
	<tr onmouseover="this.tmp = this.className; this.className = 'sb-content l-infos-over';"
	    onmouseout="this.className = this.tmp;"
	    class="sb-content l-infos-<?=(($i % 2) + 1)?>on2">
		<td class="td-left">
			<?=$form->checkbox(array('name'		=> 'netiface[]',
						 'value'	=> $id,
						 'label'	=> false,
						 'id'		=> 'it-netiface-'.$i,
						 'checked'	=> false,
						 'paragraph'	=> false,
						 'disabled'	=> ($hwtypeid !== 1 || $disableable === false)));?>
		</td>
		<td class="txt-left" title="<?=dwho_alttitle($ifname);?>">
			<label for="it-ifname-<?=$i?>" id="lb-ifname-<?=$i?>">
<?php
				echo	$url->img_html('img/site/flag/'.$icon.'.gif',null,'class="icons-list"'),
					dwho_htmlen(dwho_trunc($ifname,10,'...',false));
?>
			</label>
		</td>
		<td><?=$hwaddress?></td>
		<td><?=$this->bbf('fm_networktype-opt',$networktype)?></td>
		<td><?=$method?></td>
		<td><?=$address?></td>
		<td><?=$gateway;?></td>
		<td class="td-right" colspan="2">
<?php
			if($hwtypeid !== 1 || $list[$i]['actionable'] === false):
				echo	$url->img_html('/z.gif',null,'width="15" height="15"');
			elseif(empty($netiface) === true
			&& is_int($vlanid)):
				echo	$url->href_html($url->img_html('img/site/button/add.gif',
										$this->bbf('opt_add'),
										'border="0"'),
							'xivo/configuration/network/interface',
							array('act'		=> 'add',
								'devname'	=> $ifname),
							null,
							$this->bbf('opt_add'));
			elseif(empty($netiface) === true
			&& $vlanid === '-'):
				echo	$url->href_html($url->img_html('img/site/button/add.gif',
										$this->bbf('opt_add'),
										'border="0"'),
							'xivo/configuration/network/interface',
							array('act'		=> 'add',
								'devname'	=> $ifname,
								'hwtypeid'	=> $hwtypeid),
							null,
							$this->bbf('opt_add'));
			else:
				echo	$url->href_html($url->img_html('img/site/button/edit.gif',
								       $this->bbf('opt_modify'),
								       'border="0"'),
							'xivo/configuration/network/interface',
							array('act'		=> 'edit',
							      'id'		=> $id,
							      'hwtypeid'	=> $hwtypeid),
							null,
							$this->bbf('opt_modify')),"\n";

				if($list[$i]['deletable'] === true):
					echo	$url->href_html($url->img_html('img/site/button/delete.gif',
									       $this->bbf('opt_delete'),
									       'border="0"'),
								'xivo/configuration/network/interface',
								array('act'		=> 'delete',
								      'id'		=> $id,
								      'hwtypeid'	=> $hwtypeid,
								      'page'		=> $pager['page']),
								'onclick="return(confirm(\''.$dhtml->escape($this->bbf('opt_delete_confirm')).'\'));"',
								$this->bbf('opt_delete'));
				endif;
			endif;
?>
		</td>
	</tr>
<?php
		endfor;
	endif;
?>
	<tr class="sb-foot">
		<td class="td-left xspan b-nosize"><span class="span-left b-nosize">&nbsp;</span></td>
		<td class="td-center" colspan="7"><span class="b-nosize">&nbsp;</span></td>
		<td class="td-right xspan b-nosize"><span class="span-right b-nosize">&nbsp;</span></td>
	</tr>
</table>
</form>
<?php
	if($page !== ''):
		echo '<div class="b-page">',$page,'</div>';
	endif;
?>
</div>

<fieldset>
	<legend><?=$this->bbf('network_interfaces-list_legend');?></legend>
	<p>
		<?=$url->img_html('img/site/flag/enable.gif',null,'class="icons-list"');?>
		<?=$this->bbf('network_interfaces-list_legend-opt',array('enable'));?>
		&nbsp;&nbsp;
		<?=$url->img_html('img/site/flag/disable.gif',null,'class="icons-list"');?>
		<?=$this->bbf('network_interfaces-list_legend-opt',array('disable'));?>
		&nbsp;&nbsp;
		<?=$url->img_html('img/site/flag/unavailable.gif',null,'class="icons-list"');?>
		<?=$this->bbf('network_interfaces-list_legend-opt',array('waiting'));?>
	</p>
</fieldset>
