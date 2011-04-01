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

$form      = &$this->get_module('form');
$url       = &$this->get_module('url');
$dhtml     = &$this->get_module('dhtml');

$element   = $this->get_var('element');
$countries = $this->get_var('countries');

$err = $this->get_var('error');

if(($fm_save = $this->get_var('fm_save')) === true):
	$dhtml->write_js('xivo_form_result(true,\''.$dhtml->escape($this->bbf('fm_success-save')).'\');');
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
				<span class="span-center">
					<a href="#first"><?=$this->bbf('smenu_first');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-2"
		    class="dwsm-blur-last"
		    onclick="dwho_submenu.select(this,'sb-part-advanced',1);"
		    onmouseout="dwho_submenu.blur(this,1);"
		    onmouseover="dwho_submenu.focus(this,1);">
			<div class="tab">
				<span class="span-center">
					<a href="#advanced"><?=$this->bbf('smenu_advanced');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
	</ul>
</div>

<div class="sb-content">
<form action="#" method="post" accept-charset="utf-8">

<?php
	echo	$form->hidden(array('name'	=> DWHO_SESS_NAME,
				    'value'	=> DWHO_SESS_ID)),

		$form->hidden(array('name' => 'fm_send',
				    'value'	=> 1));
?>

<div id="sb-part-first" class="b-nodisplay">
<?php
		echo $form->checkbox(array('desc'	=> $this->bbf('fm_general_dundi'),
				  	'name'		  => 'general[dundi]',
						'labelid'	  => 'general-dundi',
					  'help'	  	=> $this->bbf('hlp_fm_general-dundi'),
					  'required'	=> false,
			      'checked'		=> $this->get_var('info','general','dundi'),
			      'default'		=> $element['general']['dundi']['default'])),

    $form->text(array('desc'  => $this->bbf('fm_dundi-department'),
            'name' => 'dundi[department]',
            'labelid'  => 'dundi-department',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_dundi-department'),
            'required' => false,
            'value'    => $this->get_var('info','dundi','department'),
            'default'  => $element['dundi']['department']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error','dundi', 'department')) )),

    $form->text(array('desc'  => $this->bbf('fm_dundi-organization'),
            'name' => 'dundi[organization]',
            'labelid'  => 'dundi-organization',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_dundi-organization'),
            'required' => false,
            'value'    => $this->get_var('info','dundi','organization'),
            'default'  => $element['dundi']['organization']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error','dundi', 'organization')) )),

    $form->text(array('desc'  => $this->bbf('fm_dundi-locality'),
            'name' => 'dundi[locality]',
            'labelid'  => 'dundi-locality',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_dundi-locality'),
            'required' => false,
            'value'    => $this->get_var('info','dundi','locality'),
            'default'  => $element['dundi']['locality']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error','dundi', 'locality')) )),

    $form->text(array('desc'  => $this->bbf('fm_dundi-stateprov'),
            'name' => 'dundi[stateprov]',
            'labelid'  => 'dundi-stateprov',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_dundi-stateprov'),
            'required' => false,
            'value'    => $this->get_var('info','dundi','stateprov'),
            'default'  => $element['dundi']['stateprov']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error','dundi', 'stateprov')) )),

		$form->select(array('desc'	=> $this->bbf('fm_dundi-country'),
				    'name'	=> 'dundi[country]',
				    'labelid'	=> 'dundi-country',
						'empty' => true,
						'size' => 15,
				    'help'	=> $this->bbf('hlp_fm_dundi-country'),
				    'selected'	=> $this->get_var('info','dundi','country'),
				    'default'	=> $element['dundi']['country']['default']),
			      $countries),

    $form->text(array('desc'  => $this->bbf('fm_dundi-email'),
            'name' => 'dundi[email]',
            'labelid'  => 'dundi-email',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_dundi-email'),
            'required' => false,
            'value'    => $this->get_var('info','dundi','email'),
            'default'  => $element['dundi']['email']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error','dundi', 'email')) )),

    $form->text(array('desc'  => $this->bbf('fm_dundi-phone'),
            'name' => 'dundi[phone]',
            'labelid'  => 'dundi-phone',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_dundi-phone'),
            'required' => false,
            'value'    => $this->get_var('info','dundi','phone'),
            'default'  => $element['dundi']['phone']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error','dundi', 'phone')) ));

?>
</div>

<div id="sb-part-advanced" class="b-nodisplay">
<?php
    echo $form->text(array('desc'  => $this->bbf('fm_dundi_bindaddr'),
            'name' => 'dundi[bindaddr]',
            'labelid'  => 'dundi-bindaddr',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_dundi-bindaddr'),
            'required' => false,
            'value'    => $this->get_var('info','dundi','bindaddr'),
            'default'  => $element['dundi']['bindaddr']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error','dundi', 'bindaddr')) )),

    $form->text(array('desc'  => $this->bbf('fm_dundi-port'),
            'name' => 'dundi[port]',
            'labelid'  => 'dundi-port',
            'size'     => 4,
            'help'     => $this->bbf('hlp_fm_dundi-port'),
            'required' => false,
            'value'    => $this->get_var('info','dundi','port'),
            'default'  => $element['dundi']['port']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error','dundi', 'port')) )),

		$form->select(array('desc'	=> $this->bbf('fm_dundi-tos'),
				    'name'	=> 'dundi[tos]',
				    'labelid'	=> 'dundi-tos',
				    'key'	=> false,
						'empty' => true,
				    'help'	=> $this->bbf('hlp_fm_dundi-tos'),
				    'selected'	=> $this->get_var('info','dundi','tos'),
				    'default'	=> $element['dundi']['tos']['default']),
			      $element['dundi']['tos']['value']),

    $form->text(array('desc'  => $this->bbf('fm_dundi-entityid'),
            'name' => 'dundi[entityid]',
            'labelid'  => 'dundi-entityid',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_dundi-entityid'),
            'required' => false,
            'value'    => $this->get_var('info','dundi','entityid'),
            'default'  => $element['dundi']['entityid']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error','dundi', 'entityid')) )),

    $form->text(array('desc'  => $this->bbf('fm_dundi-cachetime'),
            'name' => 'dundi[cachetime]',
            'labelid'  => 'dundi-cachetime',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_dundi-cachetime'),
            'required' => false,
            'value'    => $this->get_var('info','dundi','cachetime'),
            'default'  => $element['dundi']['cachetime']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error','dundi', 'cachetime')) )),

    $form->text(array('desc'  => $this->bbf('fm_dundi-ttl'),
            'name' => 'dundi[ttl]',
            'labelid'  => 'dundi-ttl',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_dundi-ttl'),
            'required' => false,
            'value'    => $this->get_var('info','dundi','ttl'),
            'default'  => $element['dundi']['ttl']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error','dundi', 'ttl')) )),

		$form->select(array('desc'	=> $this->bbf('fm_dundi-autokill'),
				    'name'	=> 'dundi[autokill]',
				    'labelid'	=> 'dundi-autokill',
				    'key'	=> false,
						'empty' => false,
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'help'	=> $this->bbf('hlp_fm_dundi-autokill'),
				    'selected'	=> $this->get_var('info','dundi','autokill'),
				    'default'	=> $element['dundi']['autokill']['default']),
			      $element['dundi']['autokill']['value']),

    $form->text(array('desc'  => $this->bbf('fm_dundi-secretpath'),
            'name' => 'dundi[secretpath]',
            'labelid'  => 'dundi-secretpath',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_dundi-secretpath'),
            'required' => false,
				      'help'	=> $this->bbf('hlp_fm_dundi-secretpath'),
            'value'    => $this->get_var('info','dundi','secretpath'),
            'default'  => $element['dundi']['secretpath']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error','dundi', 'secretpath')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_dundi-storehistory'),
				      'name'	=> 'dundi[storehistory]',
				      'labelid'	=> 'dundi-storehistory',
				      'help'	=> $this->bbf('hlp_fm_dundi-storehistory'),
				      'checked'	=> $this->get_var('info','dundi','storehistory'),
				      'default'	=> $element['dundi']['storehistory']['default']));
?>
</div>

<?php
	echo $form->submit(array('name' => 'submit',
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
