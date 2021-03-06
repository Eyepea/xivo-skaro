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
$err = $this->get_var('error');

$context_list = $this->get_var('context_list');
$format = $this->get_var('voicemail','format','var_val');
$zonemessages = $this->get_var('zonemessages');
$zonenames = array();
foreach($zonemessages as $k => $v)
{ $zonenames[] = $v['name']; }

if(is_array($zonemessages) === true && ($zmsg_nb = count($zonemessages)) > 0):
	$dhtml->write_js('dwho.dom.set_table_list(\'timezone\','.$zmsg_nb.');');
else:
	$zmsg_nb = 0;
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
					<a href="#first"><?=$this->bbf('smenu_general');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-2"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-voicemenu');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#voicemenu"><?=$this->bbf('smenu_voicemenu');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-3"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-email');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#email"><?=$this->bbf('smenu_email');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-4"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-pager');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#pager"><?=$this->bbf('smenu_pager');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-5"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-timezone');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#timezones"><?=$this->bbf('smenu_timezones');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-6"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-adsi');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#adsi"><?=$this->bbf('smenu_adsi');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-7"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-advanced');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#advanced"><?=$this->bbf('smenu_advanced');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-8"
		    class="dwsm-blur-last"
		    onclick="dwho_submenu.select(this,'sb-part-exchange',1);"
		    onmouseout="dwho_submenu.blur(this,1);"
		    onmouseover="dwho_submenu.focus(this,1);">
			<div class="tab">
				<span class="span-center">
					<a href="#exchange"><?=$this->bbf('smenu_exchange');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
	</ul>
</div>

<div class="sb-content">
<form action="#" method="post" accept-charset="utf-8" onsubmit="dwho.form.select('it-voicemail-format');">

<?php
	echo	$form->hidden(array('name'	=> DWHO_SESS_NAME,
				    'value'	=> DWHO_SESS_ID)),

		$form->hidden(array('name' => 'fm_send',
				    'value'	=> 1));
?>

<div id="sb-part-first" class="b-nodisplay">

<?php

	echo	$form->select(array('desc'	=> $this->bbf('fm_voicemail-maxmsg'),
				    'name'	=> 'voicemail[maxmsg]',
				    'labelid'	=> 'voicemail-maxmsg',
				    'key'	=> false,
				    'help'	=> $this->bbf('hlp_fm_voicemail-maxmsg'),
				    'selected'	=> $this->get_var('voicemail','maxmsg','var_val'),
				    'default'	=> $element['voicemail']['maxmsg']['default']),
			      $element['voicemail']['maxmsg']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail-silencethreshold'),
				    'name'	=> 'voicemail[silencethreshold]',
				    'labelid'	=> 'voicemail-silencethreshold',
				    'key'	=> false,
				    'help'	=> $this->bbf('hlp_fm_voicemail-silencethreshold'),
				    'selected'	=> $this->get_var('voicemail','silencethreshold','var_val'),
				    'default'	=> $element['voicemail']['silencethreshold']['default']),
			      $element['voicemail']['silencethreshold']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail-minsecs'),
				    'name'	=> 'voicemail[minsecs]',
				    'labelid'	=> 'voicemail-minsecs',
				    'key'	=> false,
				    'bbf'	=> 'fm_voicemail-message-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%M%s')),
				    'help'	=> $this->bbf('hlp_fm_voicemail-minsecs'),
				    'selected'	=> $this->get_var('voicemail','minsecs','var_val'),
				    'default'	=> $element['voicemail']['minsecs']['default']),
			      $element['voicemail']['minsecs']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail-maxsecs'),
				    'name'	=> 'voicemail[maxsecs]',
				    'labelid'	=> 'voicemail-maxsecs',
				    'key'	=> false,
				    'bbf'	=> 'fm_voicemail-message-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%M%s')),
				    'help'	=> $this->bbf('hlp_fm_voicemail-maxsecs'),
				    'selected'	=> $this->get_var('voicemail','maxsecs','var_val'),
				    'default'	=> $element['voicemail']['maxsecs']['default']),
			      $element['voicemail']['maxsecs']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail-maxsilence'),
				    'name'	=> 'voicemail[maxsilence]',
				    'labelid'	=> 'voicemail-maxsilence',
				    'key'	=> false,
				    'bbf'	=> 'fm_voicemail-maxsilence-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'help'	=> $this->bbf('hlp_fm_voicemail-maxsilence'),
				    'selected'	=> $this->get_var('voicemail','maxsilence','var_val'),
				    'default'	=> $element['voicemail']['maxsilence']['default']),
			      $element['voicemail']['maxsilence']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-review'),
				      'name'	=> 'voicemail[review]',
				      'labelid'	=> 'voicemail-review',
				      'help'	=> $this->bbf('hlp_fm_voicemail-review'),
				      'checked'	=> $this->get_var('voicemail','review','var_val'),
				      'default'	=> $element['voicemail']['review']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-operator'),
				      'name'	=> 'voicemail[operator]',
				      'labelid'	=> 'voicemail-operator',
				      'help'	=> $this->bbf('hlp_fm_voicemail-operator'),
				      'checked'	=> $this->get_var('voicemail','operator','var_val'),
				      'default'	=> $element['voicemail']['operator']['default']));

?>

<div id="formatlist" class="fm-paragraph fm-multilist">
	<p>
		<label id="lb-formatlist" for="it-voicemail-formatlist">
			<?=$this->bbf('fm_voicemail-format');?>
		</label>
	</p>
				<?=$form->input_for_ms('voicemail-formatlist',$this->bbf('ms_seek'))?>
	<div class="slt-outlist">
		<?=$form->select(array('name'		=> 'voicemail[formatlist]',
				       'label'		=> false,
				       'id'		=> 'it-voicemail-formatlist',
#				       'help'	=> $this->bbf('hlp_voicemail-formatlist'),
				       'multiple'	=> true,
				       'size'		=> 5,
				       'paragraph'	=> false,
				       'key'		=> false,
				       'bbf'		=> 'ast_format_name_info',
				       'bbfopt'		=> array('argmode' => 'paramvalue')),
				 $element['voicemail']['format']['value']);?>
	</div>
	<div class="inout-list">
		<a href="#"
		   onclick="xivo_voicemail_format('in'); return(dwho.dom.free_focus());"
		   title="<?=$this->bbf('bt_informat');?>">
			<?=$url->img_html('img/site/button/arrow-left.gif',
					  $this->bbf('bt_informat'),
					  'class="bt-inlist" id="bt-informat" border="0"');?></a><br />
		<a href="#"
		   onclick="xivo_voicemail_format('out'); return(dwho.dom.free_focus());"
		   title="<?=$this->bbf('bt_outformat');?>">
			<?=$url->img_html('img/site/button/arrow-right.gif',
					  $this->bbf('bt_outformat'),
					  'class="bt-outlist" id="bt-outformat" border="0"');?></a>
	</div>
	<div class="slt-inlist">
		<?=$form->select(array('name'		=> 'voicemail[format][]',
				       'label'		=> false,
				       'id'		=> 'it-voicemail-format',
				       'help'	=> $this->bbf('hlp_voicemail-format'),
				       'multiple'	=> true,
				       'size'		=> 5,
				       'paragraph'	=> false,
				       'key'		=> false,
				       'bbf'		=> 'ast_format_name_info',
				       'bbfopt'		=> array('argmode' => 'paramvalue')),
				 $format);?>
	</div>
</div>
<div class="clearboth"></div>
</div>

<div id="sb-part-voicemenu" class="b-nodisplay">
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_voicemail-maxlogins'),
				    'name'	=> 'voicemail[maxlogins]',
				    'labelid'	=> 'voicemail-maxlogins',
				    'key'	=> false,
				    'help'	=> $this->bbf('hlp_fm_voicemail-maxlogins'),
				    'selected'	=> $this->get_var('voicemail','maxlogins','var_val'),
				    'default'	=> $element['voicemail']['maxlogins']['default']),
			      $element['voicemail']['maxlogins']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-envelope'),
				      'name'	=> 'voicemail[envelope]',
				      'labelid'	=> 'voicemail-envelope',
				      'help'	=> $this->bbf('hlp_fm_voicemail-envelope'),
				      'checked'	=> $this->get_var('voicemail','envelope','var_val'),
				      'default'	=> $element['voicemail']['envelope']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-saycid'),
				      'name'	=> 'voicemail[saycid]',
				      'labelid'	=> 'voicemail-saycid',
				      'help'	=> $this->bbf('hlp_fm_voicemail-saycid'),
				      'checked'	=> $this->get_var('voicemail','saycid','var_val'),
				      'default'	=> $element['voicemail']['saycid']['default']));

if($context_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_voicemail-cidinternalcontexts'),
				    'name'	=> 'voicemail[cidinternalcontexts]',
				    'labelid'	=> 'voicemail-cidinternalcontexts',
				    'empty'	=> true,
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['voicemail']['cidinternalcontexts']['default'],
				    'help'	=> $this->bbf('hlp_fm_voicemail-cidinternalcontexts'),
				    'selected'	=> $this->get_var('voicemail','cidinternalcontexts','var_val')),
			      $context_list);
endif;

	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-sayduration'),
				      'name'	=> 'voicemail[sayduration]',
				      'labelid'	=> 'voicemail-sayduration',
				      'help'	=> $this->bbf('hlp_fm_voicemail-sayduration'),
				      'checked'	=> $this->get_var('voicemail','sayduration','var_val'),
				      'default'	=> $element['voicemail']['sayduration']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail-saydurationm'),
				    'name'	=> 'voicemail[saydurationm]',
				    'labelid'	=> 'voicemail-saydurationm',
				    'key'	=> false,
				    'bbf'	=> 'fm_voicemail-saydurationm-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'help'	=> $this->bbf('hlp_fm_voicemail-saydurationm'),
				    'selected'	=> $this->get_var('voicemail','saydurationm','var_val'),
				    'default'	=> $element['voicemail']['saydurationm']['default']),
			      $element['voicemail']['saydurationm']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-forcename'),
				      'name'	=> 'voicemail[forcename]',
				      'labelid'	=> 'voicemail-forcename',
				      'help'	=> $this->bbf('hlp_fm_voicemail-forcename'),
				      'checked'	=> $this->get_var('voicemail','forcename','var_val'),
				      'default'	=> $element['voicemail']['forcename']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-forcegreetings'),
				      'name'	=> 'voicemail[forcegreetings]',
				      'labelid'	=> 'voicemail-forcegreetings',
				      'help'	=> $this->bbf('hlp_fm_voicemail-forcegreetings'),
				      'checked'	=> $this->get_var('voicemail','forcegreetings','var_val'),
				      'default'	=> $element['voicemail']['forcegreetings']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-tempgreetwarn'),
				      'name'	=> 'voicemail[tempgreetwarn]',
				      'labelid'	=> 'voicemail-tempgreetwarn',
				      'help'	=> $this->bbf('hlp_fm_voicemail-tempgreetwarn'),
				      'checked'	=> $this->get_var('voicemail','tempgreetwarn','var_val'),
				      'default'	=> $element['voicemail']['tempgreetwarn']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail-maxgreet'),
				    'name'	=> 'voicemail[maxgreet]',
				    'labelid'	=> 'voicemail-maxgreet',
				    'key'	=> false,
				    'bbf'	=> 'fm_voicemail-maxgreet-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%M%s')),
				    'help'	=> $this->bbf('hlp_fm_voicemail-maxgreet'),
				    'selected'	=> $this->get_var('voicemail','maxgreet','var_val'),
				    'default'	=> $element['voicemail']['maxgreet']['default']),
			      $element['voicemail']['maxgreet']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail-skipms'),
				    'name'	=> 'voicemail[skipms]',
				    'labelid'	=> 'voicemail-skipms',
				    'key'	=> false,
				    'bbf'	=> 'fm_voicemail-skipms-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'millisecond',
									'format'	=> '%M%s')),
				    'help'	=> $this->bbf('hlp_fm_voicemail-skipms'),
				    'selected'	=> $this->get_var('voicemail','skipms','var_val'),
				    'default'	=> $element['voicemail']['skipms']['default']),
			      $element['voicemail']['skipms']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-sendvoicemail'),
				      'name'	=> 'voicemail[sendvoicemail]',
				      'labelid'	=> 'voicemail-sendvoicemail',
				      'help'	=> $this->bbf('hlp_fm_voicemail-sendvoicemail'),
				      'checked'	=> $this->get_var('voicemail','sendvoicemail','var_val'),
				      'default'	=> $element['voicemail']['sendvoicemail']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-usedirectory'),
				      'name'	=> 'voicemail[usedirectory]',
				      'labelid'	=> 'voicemail-usedirectory',
				      'help'	=> $this->bbf('hlp_fm_voicemail-usedirectory'),
				      'checked'	=> $this->get_var('voicemail','usedirectory','var_val'),
				      'default'	=> $element['voicemail']['usedirectory']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-nextaftercmd'),
				      'name'	=> 'voicemail[nextaftercmd]',
				      'labelid'	=> 'voicemail-nextaftercmd',
				      'help'	=> $this->bbf('hlp_fm_voicemail-nextaftercmd'),
				      'checked'	=> $this->get_var('voicemail','nextaftercmd','var_val'),
				      'default'	=> $element['voicemail']['nextaftercmd']['default'])),

    $form->checkbox(array('desc'  => $this->bbf('fm_messagewrap'),
              'name' => 'voicemail[messagewrap]',
              'labelid' => 'messagewrap',
              'help'    => $this->bbf('hlp_fm_messagewrap'),
              'checked' => $this->get_var('voicemail','messagewrap','var_val'),
              'default' => $element['voicemail']['messagewrap']['default']));

if($context_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_voicemail-dialout'),
				    'name'	=> 'voicemail[dialout]',
				    'labelid'	=> 'voicemail-dialout',
				    'empty'	=> true,
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['voicemail']['dialout']['default'],
				    'help'	=> $this->bbf('hlp_fm_voicemail-dialout'),
				    'selected'	=> $this->get_var('voicemail','dialout','var_val')),
			      $context_list),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail-callback'),
				    'name'	=> 'voicemail[callback]',
				    'labelid'	=> 'voicemail-callback',
				    'empty'	=> true,
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['voicemail']['callback']['default'],
				    'help'	=> $this->bbf('hlp_fm_voicemail-callback'),
				    'selected'	=> $this->get_var('voicemail','callback','var_val')),
			      $context_list),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail-exitcontext'),
				    'name'	=> 'voicemail[exitcontext]',
				    'labelid'	=> 'voicemail-exitcontext',
				    'empty'	=> true,
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['voicemail']['exitcontext']['default'],
				    'help'	=> $this->bbf('hlp_fm_voicemail-exitcontext'),
				    'selected'	=> $this->get_var('voicemail','exitcontext','var_val')),
			      $context_list),

    $form->text(array('desc'  => $this->bbf('fm_listen-control-forward-key'),
            'name' => 'voicemail[listen-control-forward-key]',
            'labelid'  => 'listen-control-forward-key',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_listen-control-forward-key'),
            'required' => false,
            'value'    => $this->get_var('voicemail','listen-control-forward-key','var_val'),
            'default'  => $element['voicemail']['listen-control-forward-key']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'listen-control-forward-key')) )),

    $form->text(array('desc'  => $this->bbf('fm_listen-control-reverse-key'),
            'name' => 'voicemail[listen-control-reverse-key]',
            'labelid'  => 'listen-control-reverse-key',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_listen-control-reverse-key'),
            'required' => false,
            'value'    => $this->get_var('voicemail','listen-control-reverse-key','var_val'),
            'default'  => $element['voicemail']['listen-control-reverse-key']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'listen-control-reverse-key')) )),

    $form->text(array('desc'  => $this->bbf('fm_listen-control-pause-key'),
            'name' => 'voicemail[listen-control-pause-key]',
            'labelid'  => 'listen-control-pause-key',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_listen-control-pause-key'),
            'required' => false,
            'value'    => $this->get_var('voicemail','listen-control-pause-key','var_val'),
            'default'  => $element['voicemail']['listen-control-pause-key']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'listen-control-pause-key')) )),

    $form->text(array('desc'  => $this->bbf('fm_listen-control-restart-key'),
            'name' => 'voicemail[listen-control-restart-key]',
            'labelid'  => 'listen-control-restart-key',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_listen-control-restart-key'),
            'required' => false,
            'value'    => $this->get_var('voicemail','listen-control-restart-key','var_val'),
            'default'  => $element['voicemail']['listen-control-restart-key']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'listen-control-restart-key')) )),

    $form->text(array('desc'  => $this->bbf('fm_listen-control-stop-key'),
            'name' => 'voicemail[listen-control-stop-key]',
            'labelid'  => 'listen-control-stop-key',
            'size'     => 10,
            'help'     => $this->bbf('hlp_fm_listen-control-stop-key'),
            'required' => false,
            'value'    => $this->get_var('voicemail','listen-control-stop-key','var_val'),
            'default'  => $element['voicemail']['listen-control-stop-key']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'listen-control-stop-key')) ));
endif;

?>
</div>

<div id="sb-part-email" class="b-nodisplay">
<?php
	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-attach'),
				      'name'	=> 'voicemail[attach]',
				      'labelid'	=> 'voicemail-attach',
				      'help'	=> $this->bbf('hlp_fm_voicemail-attach'),
				      'checked'	=> $this->get_var('voicemail','attach','var_val'),
				      'default'	=> $element['voicemail']['attach']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail-volgain'),
				    'name'	=> 'voicemail[volgain]',
				    'labelid'	=> 'voicemail-volgain',
				    'key'	=> false,
				    'help'	=> $this->bbf('hlp_fm_voicemail-attachformat'),
				    'selected'	=> $this->get_var('voicemail','volgain','var_val'),
				    'default'	=> $element['voicemail']['volgain']['default']),
			      $element['voicemail']['volgain']['value']),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-mailcmd'),
				  'name'	=> 'voicemail[mailcmd]',
				  'labelid'	=> 'voicemail-mailcmd',
				  'size'	=> 15,
				  'help'	=> $this->bbf('hlp_fm_voicemail-mailcmd'),
				  'value'	=> $this->get_var('voicemail','mailcmd','var_val'),
				  'default'	=> $element['voicemail']['mailcmd']['default'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error', 'voicemail', 'mailcmd'))),
			    'class="it-readonly" readonly="readonly"'),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-charset'),
				  'name'	=> 'voicemail[charset]',
				  'labelid'	=> 'voicemail-charset',
				  'size'	=> 15,
				  'help'	=> $this->bbf('hlp_fm_voicemail-charset'),
				  'value'	=> $this->get_var('voicemail','charset','var_val'),
				  'default'	=> $element['voicemail']['charset']['default'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error', 'voicemail', 'charset'))),
			    'class="it-readonly" readonly="readonly"'),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-serveremail'),
				  'name'	=> 'voicemail[serveremail]',
				  'labelid'	=> 'voicemail-serveremail',
				  'size'	=> 15,
				  'help'	=> $this->bbf('hlp_fm_voicemail-serveremail'),
				  'value'	=> $this->get_var('voicemail','serveremail','var_val'),
				  'default'	=> $element['voicemail']['serveremail']['default'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error', 'voicemail', 'serveremail')))),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-fromstring'),
				  'name'	=> 'voicemail[fromstring]',
				  'labelid'	=> 'voicemail-fromstring',
				  'size'	=> 15,
				  'help'	=> $this->bbf('hlp_fm_voicemail-fromstring'),
				  'value'	=> $this->get_var('voicemail','fromstring','var_val'),
				  'default'	=> $element['voicemail']['fromstring']['default'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error', 'voicemail', 'fromstring')))),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-emaildateformat'),
				  'name'	=> 'voicemail[emaildateformat]',
				  'labelid'	=> 'voicemail-emaildateformat',
				  'size'	=> 15,
				  'help'	=> $this->bbf('hlp_fm_voicemail-emaildateformat'),
				  'value'	=> $this->get_var('voicemail','emaildateformat','var_val'),
				  'default'	=> $element['voicemail']['emaildateformat']['default'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error', 'voicemail', 'emaildateformat')))),

    $form->select(array('desc'  => $this->bbf('fm_tz'),
            'name' => 'voicemail[tz]',
            'labelid'  => 'tz',
            'key'      => false,
            'help'     => $this->bbf('hlp_fm_tz'),
            'selected' => $this->get_var('voicemail','tz','var_val'),
            'default'  => $element['voicemail']['tz']['default']),
        $zonenames),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-pbxskip'),
				      'name'	=> 'voicemail[pbxskip]',
				      'labelid'	=> 'voicemail-pbxskip',
				      'help'	=> $this->bbf('hlp_fm_voicemail-pbxskip'),
				      'checked'	=> $this->get_var('voicemail','pbxskip','var_val'),
				      'default'	=> $element['voicemail']['pbxskip']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-emailsubject'),
				  'name'	=> 'voicemail[emailsubject]',
				  'labelid'	=> 'voicemail-emailsubject',
				  'size'	=> 15,
				  'help'	=> $this->bbf('hlp_fm_voicemail-emailsubject'),
				  'value'	=> $this->get_var('voicemail','emailsubject','var_val'),
				  'default'	=> $element['voicemail']['emailsubject']['default'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error', 'voicemail', 'emailsubject'))));
?>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-voicemail-emailbody" for="it-voicemail-emailbody">
				<?=$this->bbf('fm_voicemail-emailbody');?>
			</label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'name'		=> 'voicemail[emailbody]',
					 'label'	=> false,
					 'id'		=> 'it-voicemail-emailbody',
					 'cols'		=> 60,
					 'rows'		=> 10),
				   $this->get_var('voicemail','emailbody','var_val'));?>
	</div>
</div>

<div id="sb-part-pager" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_voicemail-pagerfromstring'),
				  'name'	=> 'voicemail[pagerfromstring]',
				  'labelid'	=> 'voicemail-pagerfromstring',
				  'size'	=> 15,
				  'help'	=> $this->bbf('hlp_fm_voicemail-pagerfromstring'),
				  'value'	=> $this->get_var('voicemail','pagerfromstring','var_val'),
				  'default'	=> $element['voicemail']['pagerfromstring']['default'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error', 'voicemail', 'pagerfromstring')))),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-pagersubject'),
				  'name'	=> 'voicemail[pagersubject]',
				  'labelid'	=> 'voicemail-pagersubject',
				  'size'	=> 15,
				  'help'	=> $this->bbf('hlp_fm_voicemail-pagersubject'),
				  'value'	=> $this->get_var('voicemail','pagersubject','var_val'),
				  'default'	=> $element['voicemail']['pagersubject']['default'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error', 'voicemail', 'pagersubject'))));
?>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-voicemail-pagerbody" for="it-voicemail-pagerbody">
				<?=$this->bbf('fm_voicemail-pagerbody');?>
			</label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'name'		=> 'voicemail[pagerbody]',
					 'label'	=> false,
					 'id'		=> 'it-voicemail-pagerbody',
					 'cols'		=> 60,
					 'rows'		=> 10),
				   $this->get_var('voicemail','pagerbody','var_val'));?>
	</div>
</div>

<div id="sb-part-timezone" class="b-nodisplay">
<div class="sb-list">
	<table>
		<thead>
		<tr class="sb-top">
			<th class="th-left"><?=$this->bbf('col_timezone-name');?></th>
			<th class="th-center"><?=$this->bbf('col_timezone-timezone');?></th>
			<th class="th-center"><?=$this->bbf('col_timezone-options');?></th>
			<th class="th-right">
				<?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
								  $this->bbf('col_timezone-add'),
								  'border="0"'),
						   '#',
						   null,
						   'onclick="dwho.dom.make_table_list(\'timezone\',this); return(dwho.dom.free_focus());"',
						   $this->bbf('col_timezone-add'));?>
			</th>
		</tr>
		</thead>
		<tbody id="timezone">
<?php

if($zmsg_nb > 0):
	foreach($zonemessages as $key => $val):

		if(isset($err['zonemessages'][$key]) === true):
			$errdisplay = ' l-infos-error';
		else:
			$errdisplay = '';
		endif;

?>
		<tr class="fm-paragraph<?=$errdisplay?>">
			<td class="td-left">
				<?=$form->text(array('paragraph'	=> false,
						     'name'		=> 'zonemessages[name][]',
						     'id'		=> false,
						     'label'		=> false,
						     'help'	=> $this->bbf('hlp_timezone-name'),
						     'value'		=> $val['name'],
						     'default'		=> $element['zonemessages']['name']['default']));?>
			</td>
			<td>
				<?=$form->select(array('name'		=> 'zonemessages[timezone][]',
							   'paragraph'	=> false,
						       'key'		=> true,
						       'id'		=> false,
						       'label'		=> false,
						       'help'	=> $this->bbf('hlp_timezone-timezone'),
						       'selected'	=> $val['timezone'],
						       'default'	=> $element['zonemessages']['timezone']['default']),
						 $this->get_var('timezone_list'));?>
			</td>
			<td>
				<?=$form->text(array('paragraph'	=> false,
						     'name'		=> 'zonemessages[msg_format][]',
						     'id'		=> false,
						     'label'		=> false,
						     'size'		=> 25,
						     'help'	=> $this->bbf('hlp_timezone-options'),
						     'value'		=> $val['msg_format'],
						     'default'		=> $element['zonemessages']['msg_format']['default']));?>
			</td>
			<td class="td-right">
				<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
								  $this->bbf('opt_delete'),
								  'border="0"'),
						   '#',
						   null,
						   'onclick="dwho.dom.make_table_list(\'timezone\',this,1); return(dwho.dom.free_focus());"',
						   $this->bbf('opt_delete'));?>
			</td>
		</tr>
<?php
		endforeach;
	endif;
?>
		</tbody>
		<tfoot>
		<tr id="no-timezone"<?=($zmsg_nb > 0 ? ' class="b-nodisplay"' : '')?>>
			<td colspan="4" class="td-single"><?=$this->bbf('no_timezone');?></td>
		</tr>
		</tfoot>
	</table>
	<table class="b-nodisplay">
		<tbody id="ex-timezone">
		<tr class="fm-paragraph">
			<td class="td-left">
				<?=$form->text(array('paragraph'	=> false,
						     'name'		=> 'zonemessages[name][]',
						     'id'		=> false,
						     'label'		=> false,
						     'disabled'		=> true,
						     'default'		=> $element['zonemessages']['name']['default']));?>
			</td>
			<td>
				<?=$form->select(array('paragraph'	=> false,
						       'name'		=> 'zonemessages[timezone][]',
						       'key'		=> true,
						       'id'		=> false,
						       'label'		=> false,
						       'disabled'	=> true,
						       'default'	=> $element['zonemessages']['timezone']['default']),
						 $this->get_var('timezone_list'));?>
			</td>
			<td>
				<?=$form->text(array('paragraph'	=> false,
						     'name'		=> 'zonemessages[msg_format][]',
						     'id'		=> false,
						     'label'		=> false,
						     'disabled'		=> true,
						     'size'		=> 25,
						     'default'		=> $element['zonemessages']['msg_format']['default']));?>
			</td>
			<td class="td-right">
				<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
								  $this->bbf('opt_delete'),
								  'border="0"'),
						   '#',
						   null,
						   'onclick="dwho.dom.make_table_list(\'timezone\',this,1); return(dwho.dom.free_focus());"',
						   $this->bbf('opt_delete'));?>
			</td>
		</tr>
		</tbody>
	</table>
</div>
</div>

<div id="sb-part-adsi" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_voicemail-adsifdn'),
				  'name'	=> 'voicemail[adsifdn]',
				  'labelid'	=> 'voicemail-adsifdn',
				  'help'	=> $this->bbf('hlp_fm_voicemail-adsifdn'),
				  'value'	=> $this->get_var('voicemail','adsifdn','var_val'),
				  'default'	=> $element['voicemail']['adsifdn']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-adsisec'),
				  'name'	=> 'voicemail[adsisec]',
				  'labelid'	=> 'voicemail-adsisec',
				  'help'	=> $this->bbf('hlp_fm_voicemail-adsisec'),
				  'value'	=> $this->get_var('voicemail','adsisec','var_val'),
				  'default'	=> $element['voicemail']['adsisec']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-adsiver'),
				  'name'	=> 'voicemail[adsiver]',
				  'labelid'	=> 'voicemail-adsiver',
				  'size'	=> 5,
				  'help'	=> $this->bbf('hlp_fm_voicemail-adsiver'),
				  'value'	=> $this->get_var('voicemail','adsiver','var_val'),
				  'default'	=> $element['voicemail']['adsiver']['default']));
?>
</div>

<div id="sb-part-advanced" class="b-nodisplay">
<?php
	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail-searchcontexts'),
				      'name'	=> 'voicemail[searchcontexts]',
				      'labelid'	=> 'voicemail-searchcontexts',
				      'help'	=> $this->bbf('hlp_fm_voicemail-searchcontexts'),
				      'checked'	=> $this->get_var('voicemail','searchcontexts','var_val'),
				      'default'	=> $element['voicemail']['searchcontexts']['default'])),

    $form->select(array('desc'  => $this->bbf('fm_minpassword'),
            'name' => 'voicemail[minpassword]',
            'labelid'  => 'minpassword',
            'key'      => false,
            'help'     => $this->bbf('hlp_fm_minpassword'),
            'selected' => $this->get_var('voicemail','minpassword','var_val'),
            'default'  => $element['voicemail']['minpassword']['default']),
        $element['voicemail']['minpassword']['value']),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-externpass'),
				  'name'	=> 'voicemail[externpass]',
				  'labelid'	=> 'voicemail-externpass',
				  'size'	=> 25,
				  'help'	=> $this->bbf('hlp_fm_voicemail-externpass'),
				  'value'	=> $this->get_var('voicemail','externpass','var_val'),
				  'default'	=> $element['voicemail']['externpass']['default']),
				  'class="it-readonly" readonly="readonly"'),

    $form->text(array('desc'  => $this->bbf('fm_externpassnotify'),
            'name' => 'voicemail[externpassnotify]',
            'labelid'  => 'externpassnotify',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_externpassnotify'),
            'required' => false,
            'value'    => $this->get_var('voicemail','externpassnotify','var_val'),
            'default'  => $element['voicemail']['externpassnotify']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'externpassnotify')) )),

    $form->text(array('desc'  => $this->bbf('fm_externpasscheck'),
            'name' => 'voicemail[externpasscheck]',
            'labelid'  => 'externpasscheck',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_externpasscheck'),
            'required' => false,
            'value'    => $this->get_var('voicemail','externpasscheck','var_val'),
            'default'  => $element['voicemail']['externpasscheck']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'externpasscheck')) )),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-externnotify'),
				  'name'	=> 'voicemail[externnotify]',
				  'labelid'	=> 'voicemail-externnotify',
				  'size'	=> 15,
				  'help'	=> $this->bbf('hlp_fm_voicemail-externnotify'),
				  'value'	=> $this->get_var('voicemail','externnotify','var_val'),
				  'default'	=> $element['voicemail']['externnotify']['default'])),

    $form->checkbox(array('desc'  => $this->bbf('fm_pollmailboxes'),
              'name' => 'voicemail[pollmailboxes]',
              'labelid' => 'pollmailboxes',
              'help'    => $this->bbf('hlp_fm_pollmailboxes'),
              'checked' => $this->get_var('voicemail','pollmailboxes','var_val'),
              'default' => $element['voicemail']['pollmailboxes']['default'])),

    $form->select(array('desc'  => $this->bbf('fm_pollfreq'),
            'name' => 'voicemail[pollfreq]',
            'labelid'  => 'pollfreq',
            'key'      => false,
            'help'     => $this->bbf('hlp_fm_pollfreq'),
            'selected' => $this->get_var('voicemail','pollfreq','var_val'),
            'default'  => $element['voicemail']['pollfreq']['default']),
        $element['voicemail']['pollfreq']['value']),

    $form->checkbox(array('desc'  => $this->bbf('fm_imapgreetings'),
              'name' => 'voicemail[imapgreetings]',
              'labelid' => 'imapgreetings',
              'help'    => $this->bbf('hlp_fm_imapgreetings'),
              'checked' => $this->get_var('voicemail','imapgreetings','var_val'),
              'default' => $element['voicemail']['imapgreetings']['default'])),

    $form->text(array('desc'  => $this->bbf('fm_greetingsfolder'),
            'name' => 'voicemail[greetingsfolder]',
            'labelid'  => 'greetingsfolder',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_greetingsfolder'),
            'required' => false,
            'value'    => $this->get_var('voicemail','greetingsfolder','var_val'),
            'default'  => $element['voicemail']['greetingsfolder']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'greetingsfolder')) )),

    $form->text(array('desc'  => $this->bbf('fm_imapparentfolder'),
            'name' => 'voicemail[imapparentfolder]',
            'labelid'  => 'imapparentfolder',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_imapparentfolder'),
            'required' => false,
            'value'    => $this->get_var('voicemail','imapparentfolder','var_val'),
            'default'  => $element['voicemail']['imapparentfolder']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'imapparentfolder')) )),

    $form->checkbox(array('desc'  => $this->bbf('fm_hidefromdir'),
              'name' => 'voicemail[hidefromdir]',
              'labelid' => 'hidefromdir',
              'help'    => $this->bbf('hlp_fm_hidefromdir'),
              'checked' => $this->get_var('voicemail','hidefromdir','var_val'),
              'default' => $element['voicemail']['hidefromdir']['default'])),

    $form->text(array('desc'  => $this->bbf('fm_directoryintro'),
            'name' => 'voicemail[directoryintro]',
            'labelid'  => 'directoryintro',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_directoryintro'),
            'required' => false,
            'value'    => $this->get_var('voicemail','directoryintro','var_val'),
            'default'  => $element['voicemail']['directoryintro']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'directoryintro')) )),

    $form->text(array('desc'  => $this->bbf('fm_vm-password'),
            'name' => 'voicemail[vm-password]',
            'labelid'  => 'vm-password',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_vm-password'),
            'required' => false,
            'value'    => $this->get_var('voicemail','vm-password','var_val'),
            'default'  => $element['voicemail']['vm-password']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'vm-password')) )),

    $form->text(array('desc'  => $this->bbf('fm_vm-newpassword'),
            'name' => 'voicemail[vm-newpassword]',
            'labelid'  => 'vm-newpassword',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_vm-newpassword'),
            'required' => false,
            'value'    => $this->get_var('voicemail','vm-newpassword','var_val'),
            'default'  => $element['voicemail']['vm-newpassword']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'vm-newpassword')) )),

    $form->text(array('desc'  => $this->bbf('fm_vm-passchanged'),
            'name' => 'voicemail[vm-passchanged]',
            'labelid'  => 'vm-passchanged',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_vm-passchanged'),
            'required' => false,
            'value'    => $this->get_var('voicemail','vm-passchanged','var_val'),
            'default'  => $element['voicemail']['vm-passchanged']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'vm-passchanged')) )),

    $form->text(array('desc'  => $this->bbf('fm_vm-reenterpassword'),
            'name' => 'voicemail[vm-reenterpassword]',
            'labelid'  => 'vm-reenterpassword',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_vm-reenterpassword'),
            'required' => false,
            'value'    => $this->get_var('voicemail','vm-reenterpassword','var_val'),
            'default'  => $element['voicemail']['vm-reenterpassword']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'vm-reenterpassword')) )),

    $form->text(array('desc'  => $this->bbf('fm_vm-mistmatch'),
            'name' => 'voicemail[vm-mistmatch]',
            'labelid'  => 'vm-mistmatch',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_vm-mistmatch'),
            'required' => false,
            'value'    => $this->get_var('voicemail','vm-mistmatch','var_val'),
            'default'  => $element['voicemail']['vm-mistmatch']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'vm-mistmatch')) )),

    $form->text(array('desc'  => $this->bbf('fm_vm-invalid-password'),
            'name' => 'voicemail[vm-invalid-password]',
            'labelid'  => 'vm-invalid-password',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_vm-invalid-password'),
            'required' => false,
            'value'    => $this->get_var('voicemail','vm-invalid-password','var_val'),
            'default'  => $element['voicemail']['vm-invalid-password']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'vm-invalid-password')) )),

    $form->text(array('desc'  => $this->bbf('fm_vm-pls-try-again'),
            'name' => 'voicemail[vm-pls-try-again]',
            'labelid'  => 'vm-pls-try-again',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_vm-pls-try-again'),
            'required' => false,
            'value'    => $this->get_var('voicemail','vm-pls-try-again','var_val'),
            'default'  => $element['voicemail']['vm-pls-try-again']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'vm-pls-try-again')) )),

    $form->text(array('desc'  => $this->bbf('fm_backupdeleted'),
            'name' => 'voicemail[backupdeleted]',
            'labelid'  => 'backupdeleted',
            'size'     => 4,
            'help'     => $this->bbf('hlp_fm_backupdeleted'),
            'required' => false,
            'value'    => $this->get_var('voicemail','backupdeleted','var_val'),
            'default'  => $element['voicemail']['backupdeleted']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'backupdeleted')) )),

    $form->checkbox(array('desc'  => $this->bbf('fm_smdienable'),
              'name' => 'voicemail[smdienable]',
              'labelid' => 'smdienable',
              'help'    => $this->bbf('hlp_fm_smdienable'),
              'checked' => $this->get_var('voicemail','smdienable','var_val'),
              'default' => $element['voicemail']['smdienable']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_smdiport'),
				  'name' => 'voicemail[smdiport]',
				  'labelid'	=> 'smdiport',
				  'help'	=> $this->bbf('hlp_fm_smdiport'),
				  'value'	=> $this->get_var('voicemail','smdiport','var_val'),
				  'default'	=> $element['voicemail']['smdiport']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-odbcstorage'),
				  'name'	=> 'voicemail[odbcstorage]',
				  'labelid'	=> 'voicemail-odbcstorage',
				  'size'	=> 15,
				  'help'	=> $this->bbf('hlp_fm_voicemail-odbcstorage'),
				  'value'	=> $this->get_var('voicemail','odbcstorage','var_val'),
				  'default'	=> $element['voicemail']['odbcstorage']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail-odbctable'),
				  'name'	=> 'voicemail[odbctable]',
				  'labelid'	=> 'voicemail-odbctable',
				  'size'	=> 15,
				  'help'	=> $this->bbf('hlp_fm_voicemail-odbctable'),
				  'value'	=> $this->get_var('voicemail','odbctable','var_val'),
				  'default'	=> $element['voicemail']['odbctable']['default'])),

    $form->checkbox(array('desc'  => $this->bbf('fm_moveheard'),
              'name' => 'voicemail[moveheard]',
              'labelid' => 'moveheard',
              'help'    => $this->bbf('hlp_fm_moveheard'),
              'checked' => $this->get_var('voicemail','moveheard','var_val'),
              'default' => $element['voicemail']['moveheard']['default'])),

    $form->checkbox(array('desc'  => $this->bbf('fm_forward_urgent_auto'),
              'name' => 'voicemail[forward_urgent_auto]',
              'labelid' => 'forward_urgent_auto',
              'help'    => $this->bbf('hlp_fm_forward_urgent_auto'),
              'checked' => $this->get_var('voicemail','forward_urgent_auto','var_val'),
              'default' => $element['voicemail']['forward_urgent_auto']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_userscontext'),
				    'name'	=> 'voicemail[callback]',
				    'labelid'	=> 'userscontext',
				    'empty'	=> true,
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['voicemail']['callback']['default'],
				    'help'	=> $this->bbf('hlp_fm_userscontext'),
				    'selected'	=> $this->get_var('voicemail','userscontext','var_val')),
			      $context_list);

?>
</div>

<div id="sb-part-exchange" class="b-nodisplay">
<?php
   echo $form->select(array('desc'  => $this->bbf('fm_exchange_trunkid'),
            'name' => 'general[exchange_trunkid]',
            'labelid'  => 'exchange_trunkid',
						'key'      => 'name',
						'altkey'   => 'id',
						'empty'    => true,
            'help'     => $this->bbf('hlp_fm_exchange_trunkid'),
            'selected' => $this->get_var('general','exchange_trunkid'),
            'default'  => $element['general']['exchange_trunkid']['default']),
        $this->get_var('siptrunks')),

		$form->text(array('desc'	=> $this->bbf('fm_exchange_exten'),
				  'name'	=> 'general[exchange_exten]',
				  'labelid'	=> 'exchange_exten',
				  'size'	=> 5,
				  'help'	=> $this->bbf('hlp_fm_exchange_exten'),
					'value'	=> $this->get_var('general','exchange_exten'),
					'default'	=> $element['general']['exchange_exten']['default']));
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
