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

$form    = &$this->get_module('form');
$dhtml   = &$this->get_module('dhtml');

$info     = $this->get_var('info');
//var_dump($info);
$status   = $this->get_var('status');
$netifaces = $this->get_var('netifaces');

if(($fm_save = $this->get_var('fm_save')) === true):
	$dhtml->write_js('xivo_form_result(true,\'' .$dhtml->escape($this->bbf('fm_success-save')).'\');');
elseif($fm_save === false):
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>
<div class="b-infos b-form">
<h3 class="sb-top xspan">
	<span class="span-left">&nbsp;</span>
	<span class="span-center"><?=$this->bbf('title_content_name');?></span>
	<span class="span-right">&nbsp;</span>
</h3>

<div class="sb-smenu">
	<ul>
		<li id="dwsm-tab-1"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-first');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center"><a href="#first"><?=$this->bbf('smenu_status');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-2"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-network');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center"><a href="#network"><?=$this->bbf('smenu_network');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-3"
		    class="dwsm-blur-last"
		    onclick="dwho_submenu.select(this,'sb-part-services',1);"
		    onmouseout="dwho_submenu.blur(this,1);"
		    onmouseover="dwho_submenu.focus(this,1);">
			<div class="tab">
				<span class="span-center"><a href="#services"><?=$this->bbf('smenu_services');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
	</ul>
</div>

<div class="sb-content">
<form action="#" method="post" accept-charset="utf-8">

<div id="sb-part-first" class="b-nodisplay">
<?php
  echo $form->checkbox(array('desc'		=> $this->bbf('fm_ha_activate'),
				      'name'		=> 'ha[active]',
				      'labelid'		=> 'ha_active',
				      'checked'		=> $info['ha']['active'],
						)),
		
	$form->text(array('desc'	=> $this->bbf('fm_ha_netaddr'),
				  'name'	=> 'ha[netaddr]',
				  'labelid'	=> 'netaddr',
				  'size'	=> 15,
			    //'help'    => $this->bbf('fm_help-ha_netaddr'),
				  'value'	=> $this->get_var('info', 'ha', 'netaddr'))),

	$form->text(array('desc'	=> $this->bbf('fm_ha_netmask'),
				  'name'	=> 'ha[netmask]',
				  'labelid'	=> 'netmask',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info', 'ha', 'netmask'))),
				  
	$form->text(array('desc'	=> $this->bbf('fm_ha_mcast'),
				  'name'	=> 'ha[mcast]',
				  'labelid'	=> 'mcast',
				  'size'	=> 15,
					'value'	=> $this->get_var('info', 'ha', 'mcast')));
?>
	<fieldset id="fld-node1">
		<legend><?=$this->bbf('fld-node1');?></legend>

<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_ha_node1_name'),
				  'name'	=> 'ha[node1_name]',
				  'labelid'	=> 'node1_name',
				  'size'	=> 15,
			    'help'    => $this->bbf('fm_help-ha_node1_name'),
				  'value'	=> $this->get_var('info', 'ha', 'node1_name'))),

	$form->text(array('desc'	=> $this->bbf('fm_ha_node1_ip'),
				  'name'	=> 'ha[node1_ip]',
				  'labelid'	=> 'node1_ip',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info', 'ha', 'node1_ip')));
?>		  
	</fieldset>
	<fieldset id="fld-node2">
		<legend><?=$this->bbf('fld-node2');?></legend>

<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_ha_node2_name'),
				  'name'	=> 'ha[node2_name]',
				  'labelid'	=> 'node2_name',
				  'size'	=> 15,
			    'help'    => $this->bbf('fm_help-ha_node2_name'),
				  'value'	=> $this->get_var('info', 'ha', 'node2_name'))),

	$form->text(array('desc'	=> $this->bbf('fm_ha_node2_ip'),
				  'name'	=> 'ha[node2_ip]',
				  'labelid'	=> 'node2_ip',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info', 'ha', 'node2_ip')));
?>		  
	</fieldset>


</div>

<div id="sb-part-services" class="b-nodisplay">
<?php
	echo	$form->hidden(array('name'	=> DWHO_SESS_NAME,
				    'value'	=> DWHO_SESS_ID)),

		$form->hidden(array('name'	=> 'fm_send',
				    'value'	=> 1));


		foreach($info['service'] as $k => $svc) {
			echo $form->checkbox(array('desc'		=> $this->bbf("fm_ha_service_$k"),
				      'name'		=> "service[$k][active]",
							'labelid'		=> "ha_$k",
				      'checked'		=> $svc['active'],
						)),
			"<fieldset id=\"fld-svc-$k\">",
			$form->text(array(
	        'desc'    => $this->bbf("fm_ha_service_monitor"),
					'name'		=> "service[$k][monitor]",
					'size'	  => 4,
					'value'   => $this->get_var('info', 'service',$k,'monitor'))),
			$form->text(array(
	        'desc'    => $this->bbf("fm_ha_service_timeout"),
					'name'		=> "service[$k][timeout]",
					'size'	  => 4,
					'value'   => $this->get_var('info', 'service',$k,'timeout'))),
			'</fieldset>';
		}

?>
</div>

<div id="sb-part-network" class="b-nodisplay">
<?php
		echo $form->text(array(
	        'desc'    => $this->bbf('fm_ha_cluster_name'),
					'name'		=> 'ha[cluster_name]',
					'size'	  => 25,
					'value'   => $this->get_var('info','ha','cluster_name'))),

		$form->checkbox(array('desc'		=> $this->bbf('fm_ha_cluster_group'),
				      'name'		=> 'ha[cluster_group]',
				      'labelid'		=> 'ha_cluster_group',
				      'checked'		=> $info['ha']['cluster_group'],
						)),
		
		$form->select(array(
					'desc'    => $this->bbf('fm_ha_cluster_itf_data'),
					'name'		=> 'ha[cluster_itf_data]',
					'id'		  => "it-pf-ha-cluster_itf_data",
					'help'    => $this->bbf('hlp_fm_cluster_itf_data'),
					'empty'		=> true,
					'key'  		=> false,
					'selected'	=> $info['ha']['cluster_itf_data']),
				$netifaces),

		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_cluster_monitor'),
					'name'		=> 'ha[cluster_monitor]',
					'help'    => $this->bbf('hlp_fm_cluster_monitor'),
//					'error'  	=> $this->bbf_args('error_pf_ha_com_mode', 
					'size'	  => 5,
					'value'   => $this->get_var('info','ha','cluster_monitor'))),

		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_cluster_timeout'),
					'name'		=> 'ha[cluster_timeout]',
					'help'    => $this->bbf('hlp_fm_cluster_timeout'),
					'size'	  => 5,
					'value'   => $this->get_var('info','ha','cluster_timeout'))),

		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_cluster_mailto'),
					'name'		=> 'ha[cluster_mailto]',
					'help'    => $this->bbf('hlp_fm_cluster_mailto'),
					'size'	  => 25,
					'value'   => $this->get_var('info','ha','cluster_mailto'))),

		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_cluster_pingd'),
					'name'		=> 'ha[cluster_pingd]',
					'size'	  => 25,
					'value'   => $this->get_var('info','ha','cluster_pingd')));

    $this->file_include('bloc/xivo/configuration/network/ha/peer');
?>
</div>

</div>
<?php
echo	$form->submit(array('name'	=> 'submit',
			    'id'	=> 'it-submit',
			    'value'	=> $this->bbf('fm_bt-save')));

?>
</form>
	</div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
