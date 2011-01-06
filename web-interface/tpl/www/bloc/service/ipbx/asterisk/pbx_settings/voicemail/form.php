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

$form = &$this->get_module('form');
$url = &$this->get_module('url');

$info = $this->get_var('info');
$element = $this->get_var('element');
$context_list = $this->get_var('context_list');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>

<div id="sb-part-first" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_voicemail_fullname'),
				  'name'	=> 'voicemail[fullname]',
				  'labelid'	=> 'voicemail-fullname',
				  'size'	=> 15,
				  'default'	=> $element['voicemail']['fullname']['default'],
				  'value' => $info['voicemail']['fullname'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','voicemail','fullname')))),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail_mailbox'),
				  'name'	=> 'voicemail[mailbox]',
				  'labelid'	=> 'voicemail-mailbox',
				  'size'	=> 10,
				  'default'	=> $element['voicemail']['mailbox']['default'],
				  'value' => $info['voicemail']['mailbox'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','voicemail','mailbox')))),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail_password'),
				  'name'	=> 'voicemail[password]',
				  'labelid'	=> 'voicemail-password',
				  'size'	=> 10,
				  'default'	=> $element['voicemail']['password']['default'],
				  'value' => $info['voicemail']['password'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','voicemail','password')))),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail_email'),
				  'name'	=> 'voicemail[email]',
				  'labelid'	=> 'voicemail-email',
				  'size'	=> 15,
				  'default'	=> $element['voicemail']['email']['default'],
				  'value' => $info['voicemail']['email'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','voicemail','email'))));

if($context_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_voicemail_context'),
				    'name'	=> 'voicemail[context]',
				    'labelid'	=> 'voicemail-context',
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['voicemail']['context']['default'],
				    'selected'	=> $info['voicemail']['context']),
			      $context_list);
else:
	echo	'<div id="fd-voicemail-context" class="txt-center">',
			$url->href_htmln($this->bbf('create_context'),
					'service/ipbx/system_management/context',
					'act=add'),
		'</div>';
endif;

if(($tz_list = $this->get_var('tz_list')) !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_voicemail_tz'),
				    'name'	=> 'voicemail[tz]',
				    'labelid'	=> 'voicemail-tz',
				    'key'	=> 'name',
				    'default'	=> $element['voicemail']['tz']['default'],
				    'selected'	=> $info['voicemail']['tz']),
			      $tz_list);
endif;

	echo	$form->select(array('desc'	=> $this->bbf('fm_voicemail_language'),
				    'name'	=> 'voicemail[language]',
				    'labelid'	=> 'voicemail-language',
				    'empty'	=> true,
				    'key'	=> false,
				    'default'	=> $element['voicemail']['language']['default'],
				    'selected'	=> $info['voicemail']['language']),
			      $element['voicemail']['language']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemailfeatures_skipcheckpass'),
				      'name'	=> 'voicemailfeatures[skipcheckpass]',
				      'labelid'	=> 'voicemailfeatures-skipcheckpass',
				      'default'	=> $element['voicemailfeatures']['skipcheckpass']['default'],
				      'checked'	=> $info['voicemailfeatures']['skipcheckpass'])),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_maxmsg'),
				    'name'	=> 'voicemail[maxmsg]',
				    'labelid'	=> 'voicemail-maxmsg',
				    'empty'	=> true,
				    'key'	=> false,
				    'selected'	=> $info['voicemail']['maxmsg'],
				    'default'	=> $element['voicemail']['maxmsg']['default']),
			      $element['voicemail']['maxmsg']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_attach'),
				    'name'	=> 'voicemail[attach]',
				    'labelid'	=> 'voicemail-attach',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> $info['voicemail']['attach'],
				    'default'	=> $element['voicemail']['attach']['default']),
			      $element['voicemail']['attach']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail_deletevoicemail'),
				      'name'	=> 'voicemail[deletevoicemail]',
				      'labelid'	=> 'voicemail-deletevoicemail',
				      'default'	=> $element['voicemail']['deletevoicemail']['default'],
				      'checked'	=> $info['voicemail']['deletevoicemail']));
?>
</div>

<div id="sb-part-email" class="b-nodisplay">
<?php
		echo $form->select(array('desc'	=> $this->bbf('fm_voicemail-attachfmt'),
				    'name'     => 'voicemail[attachfmt]',
				    'labelid'  => 'voicemail-attachfmt',
				    'empty'    => true,
				    'key'      => false,
						'help'     => $this->bbf('hlp_fm_voicemail-attachfmt'),
				    'bbf'      => 'ast_format_name_info',
				    'bbfopt'   => array('argmode' => 'paramvalue'),
				    'selected' => $info['voicemail']['attachfmt'],
				    'default'	 => $element['voicemail']['attachfmt']['default']),
			      $element['voicemail']['attachfmt']['value']),

     $form->select(array('desc'  => $this->bbf('fm_voicemail-volgain'),
            'name'     => 'voicemail[volgain]',
            'labelid'  => 'voicemail-volgain',
            'key'      => false,
            'empty'    => true,
            'help'     => $this->bbf('hlp_fm_voicemail-volgain'),
            'selected' => $info['voicemail']['volgain'],
            'default'  => $element['voicemail']['volgain']['default']),
         $element['voicemail']['volgain']['value']),

    $form->text(array('desc'  => $this->bbf('fm_voicemail-emailsubject'),
            'name'     => 'voicemail[emailsubject]',
            'labelid'  => 'voicemail-emailsubject',
            'size'     => 25,
            'help'     => $this->bbf('hlp_fm_voicemail-emailsubject'),
            'required' => false,
            'value'    => $info['voicemail']['emailsubject'],
            'default'  => $element['voicemail']['emailsubject']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'emailsubject')) ));
?>
	<div class="fm-paragraph fm-description">
    <?= $form->textarea(array('paragraph' => false,
						'desc'     => $this->bbf('fm_voicemail-emailbody'),
            'label'    => false,
            'name'     => 'voicemail[emailbody]',
            'id'       => 'voicemail-emailbody',
            'cols'     => 60,
            'rows'     => 5,
            'help'     => $this->bbf('hlp_fm_voicemail-emailbody'),
            'default'  => $element['voicemail']['emailbody']['default'],
            'error'    => $this->bbf_args('error',
               $this->get_var('error', 'emailbody'))),
          $info['voicemail']['emailbody']);
	  ?>
	</div>
	<br/><br/>
<?php

echo    $form->text(array('desc'  => $this->bbf('fm_voicemail-imapuser'),
            'name'     => 'voicemail[imapuser]',
            'labelid'  => 'voicemail-imapuser',
            'size'     => 15,
            'help'     => $this->bbf('hlp_fm_voicemail-imapuser'),
            'required' => false,
            'value'    => $info['voicemail']['imapuser'],
            'default'  => $element['voicemail']['imapuser']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'imapuser')) )),

    $form->text(array('desc'  => $this->bbf('fm_voicemail-imappassword'),
            'name'     => 'voicemail[imappassword]',
            'labelid'  => 'voicemail-imappassword',
            'size'     => 15,
            'help'     => $this->bbf('hlp_fm_voicemail-imappassword'),
            'required' => false,
            'value'    => $info['voicemail']['imappassword'],
            'default'  => $element['voicemail']['imappassword']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'imappassword')) )),

    $form->text(array('desc'  => $this->bbf('fm_voicemail-imapfolder'),
            'name'     => 'voicemail[imapfolder]',
            'labelid'  => 'voicemail-imapfolder',
            'size'     => 15,
            'help'     => $this->bbf('hlp_fm_voicemail-imapfolder'),
            'required' => false,
            'value'    => $info['voicemail']['imapfolder'],
            'default'  => $element['voicemail']['imapfolder']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'imapfolder')) )),

    $form->text(array('desc'  => $this->bbf('fm_voicemail-imapvmsharedid'),
            'name'     => 'voicemail[imapvmsharedid]',
            'labelid'  => 'voicemail-imapvmsharedid',
            'size'     => 15,
            'help'     => $this->bbf('hlp_fm_voicemail-imapvmsharedid'),
            'required' => false,
            'value'    => $info['voicemail']['imapvmsharedid'],
            'default'  => $element['voicemail']['imapvmsharedid']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'imapvmsharedid')) )),

    $form->text(array('desc'  => $this->bbf('fm_voicemail-serveremail'),
            'name'     => 'voicemail[serveremail]',
            'labelid'  => 'voicemail-serveremail',
            'size'     => 15,
            'help'     => $this->bbf('hlp_fm_voicemail-serveremail'),
            'required' => false,
            'value'    => $info['voicemail']['serveremail'],
            'default'  => $element['voicemail']['serveremail']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'serveremail')) ));


?>
</div>

<div id="sb-part-last" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_voicemail_pager'),
				  'name'	=> 'voicemail[pager]',
				  'labelid'	=> 'voicemail-pager',
				  'size'	=> 10,
				  'default'	=> $element['voicemail']['pager']['default'],
				  'value' => $info['voicemail']['pager'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','voicemail','pager')))),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_saycid'),
				    'name'	=> 'voicemail[saycid]',
				    'labelid'	=> 'voicemail-saycid',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> $info['voicemail']['saycid'],
				    'default'	=> $element['voicemail']['saycid']['default']),
			      $element['voicemail']['saycid']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_review'),
				    'name'	=> 'voicemail[review]',
				    'labelid'	=> 'voicemail-review',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> $info['voicemail']['review'],
				    'default'	=> $element['voicemail']['review']['default']),
			      $element['voicemail']['review']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_operator'),
				    'name'	=> 'voicemail[operator]',
				    'labelid'	=> 'voicemail-operator',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> $info['voicemail']['operator'],
				    'default'	=> $element['voicemail']['operator']['default']),
			      $element['voicemail']['operator']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_envelope'),
				    'name'	=> 'voicemail[envelope]',
				    'labelid'	=> 'voicemail-envelope',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> $info['voicemail']['envelope'],
				    'default'	=> $element['voicemail']['envelope']['default']),
			      $element['voicemail']['envelope']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_sayduration'),
				    'name'	=> 'voicemail[sayduration]',
				    'labelid'	=> 'voicemail-sayduration',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> $info['voicemail']['sayduration'],
				    'default'	=> $element['voicemail']['sayduration']['default']),
			      $element['voicemail']['sayduration']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_saydurationm'),
				    'name'	=> 'voicemail[saydurationm]',
				    'labelid'	=> 'voicemail-saydurationm',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_voicemail_saydurationm-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> $info['voicemail']['saydurationm'],
				    'default'	=> $element['voicemail']['saydurationm']['default']),
			      $element['voicemail']['saydurationm']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_sendvoicemail'),
				    'name'	=> 'voicemail[sendvoicemail]',
				    'labelid'	=> 'voicemail-sendvoicemail',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> $info['voicemail']['sendvoicemail'],
				    'default'	=> $element['voicemail']['sendvoicemail']['default']),
			      $element['voicemail']['sendvoicemail']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_forcename'),
				    'name'	=> 'voicemail[forcename]',
				    'labelid'	=> 'voicemail-forcename',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> $info['voicemail']['forcename'],
				    'default'	=> $element['voicemail']['forcename']['default']),
			      $element['voicemail']['forcename']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_forcegreetings'),
				    'name'	=> 'voicemail[forcegreetings]',
				    'labelid'	=> 'voicemail-forcegreetings',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> $info['voicemail']['forcegreetings'],
				    'default'	=> $element['voicemail']['forcegreetings']['default']),
			      $element['voicemail']['forcegreetings']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail_hidefromdir'),
				      'name'	=> 'voicemail[hidefromdir]',
				      'labelid'	=> 'voicemail-hidefromdir',
				      'default'	=> $element['voicemail']['hidefromdir']['default'],
				      'checked' => $info['voicemail']['hidefromdir']));

if($context_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_voicemail_dialout'),
				    'name'	=> 'voicemail[dialout]',
				    'labelid'	=> 'voicemail-dialout',
				    'empty'	=> true,
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['voicemail']['dialout']['default'],
				    'selected'	=> $info['voicemail']['dialout']),
			      $context_list),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_callback'),
				    'name'	=> 'voicemail[callback]',
				    'labelid'	=> 'voicemail-callback',
				    'empty'	=> true,
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['voicemail']['callback']['default'],
				    'selected'	=> $info['voicemail']['callback']),
			      $context_list),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_exitcontext'),
				    'name'	=> 'voicemail[exitcontext]',
				    'labelid'	=> 'voicemail-exitcontext',
				    'empty'	=> true,
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['voicemail']['exitcontext']['default'],
				    'selected'	=> $info['voicemail']['exitcontext']),
			      $context_list);
endif;


  // asterisk 1.8 options

echo     $form->select(array('desc'  => $this->bbf('fm_voicemail-locale'),
            'name'      => 'voicemail[locale]',
            'labelid'   => 'voicemail-locale',
            'key'       => false,
						'empty'     => true,
            'help'      => $this->bbf('hlp_fm_voicemail-locale'),
            'selected'  => $info['voicemail']['locale'],
            'default'   => $element['voicemail']['locale']['default']),
         $element['voicemail']['locale']['value']),

     $form->select(array('desc'  => $this->bbf('fm_voicemail-tempgreetwarn'),
            'name'      => 'voicemail[tempgreetwarn]',
            'labelid'   => 'voicemail-tempgreetwarn',
            'key'       => false,
            'empty'     => true,
            'bbf'       => 'fm_bool-opt',
            'bbfopt'    => array('argmode' => 'paramvalue'),
            'help'      => $this->bbf('hlp_fm_voicemail-tempgreetwarn'),
            'selected'  => $info['voicemail']['tempgreetwarn'],
            'default'   => $element['voicemail']['tempgreetwarn']['default']),
         $element['voicemail']['tempgreetwarn']['value']),

     $form->select(array('desc'  => $this->bbf('fm_voicemail-messagewrap'),
            'name'      => 'voicemail[messagewrap]',
            'labelid'   => 'voicemail-messagewrap',
            'key'       => false,
            'empty'     => true,
            'bbf'       => 'fm_bool-opt',
            'bbfopt'    => array('argmode' => 'paramvalue'),
            'help'      => $this->bbf('hlp_fm_voicemail-messagewrap'),
            'selected'  => $info['voicemail']['messagewrap'],
            'default'   => $element['voicemail']['messagewrap']['default']),
         $element['voicemail']['messagewrap']['value']),

     $form->select(array('desc'  => $this->bbf('fm_voicemail-moveheard'),
            'name'      => 'voicemail[moveheard]',
            'labelid'   => 'voicemail-moveheard',
            'key'       => false,
            'empty'     => true,
            'bbf'       => 'fm_bool-opt',
            'bbfopt'    => array('argmode' => 'paramvalue'),
            'help'      => $this->bbf('hlp_fm_voicemail-moveheard'),
            'selected'  => $info['voicemail']['moveheard'],
            'default'   => $element['voicemail']['moveheard']['default']),
         $element['voicemail']['moveheard']['value']),

     $form->select(array('desc'  => $this->bbf('fm_voicemail-minsecs'),
            'name'      => 'voicemail[minsecs]',
            'labelid'   => 'voicemail-minsecs',
            'key'       => false,
            'empty'     => true,
            'bbf'       => 'time-opt',
            'bbfopt'    => array('argmode' => 'paramvalue',
            'time'      => array('from'=>'second', 'format'=>'%M%s')),
            'help'      => $this->bbf('hlp_fm_voicemail-minsecs'),
            'selected'  => $this->get_var('voicemail','minsecs','var_val'),
            'selected'  => $info['voicemail']['minsecs'],
            'default'   => $element['voicemail']['minsecs']['default']),
         $element['voicemail']['minsecs']['value']),

     $form->select(array('desc'  => $this->bbf('fm_voicemail-maxsecs'),
            'name'      => 'voicemail[maxsecs]',
            'labelid'   => 'voicemail-maxsecs',
            'key'       => false,
            'empty'     => true,
            'bbf'       => 'time-opt',
            'bbfopt'    => array('argmode' => 'paramvalue',
            'time'      => array('from'=>'second', 'format'=>'%M%s')),
            'help'      => $this->bbf('hlp_fm_voicemail-maxsecs'),
            'selected'  => $this->get_var('voicemail','maxsecs','var_val'),
            'selected'  => $info['voicemail']['maxsecs'],
            'default'   => $element['voicemail']['maxsecs']['default']),
         $element['voicemail']['maxsecs']['value']),

     $form->select(array('desc'  => $this->bbf('fm_voicemail-nextaftercmd'),
            'name'      => 'voicemail[nextaftercmd]',
            'labelid'   => 'voicemail-nextaftercmd',
            'key'       => false,
            'empty'     => true,
            'bbf'       => 'fm_bool-opt',
            'bbfopt'    => array('argmode' => 'paramvalue'),
            'help'      => $this->bbf('hlp_fm_voicemail-nextaftercmd'),
            'selected'  => $info['voicemail']['nextaftercmd'],
            'default'   => $element['voicemail']['nextaftercmd']['default']),
         $element['voicemail']['nextaftercmd']['value']),

    $form->select(array('desc'  => $this->bbf('fm_voicemail-backupdeleted'),
            'name'     => 'voicemail[backupdeleted]',
            'labelid'  => 'voicemail-backupdeleted',
            'key'      => false,
            'empty'    => true,
            'help'     => $this->bbf('hlp_fm_voicemail-backupdeleted'),
            'selected' => $info['voicemail']['backupdeleted'],
            'default'  => $element['voicemail']['backupdeleted']['default']),
        $element['voicemail']['backupdeleted']['value']),

     $form->select(array('desc'  => $this->bbf('fm_voicemail-passwordlocation'),
            'name'     => 'voicemail[passwordlocation]',
            'labelid'  => 'voicemail-passwordlocation',
            'key'      => false,
            'empty'    => true,
            'bbf'      => 'fm_voicemail-passwordlocation-opt',
            'bbfopt'   => array('argmode' => 'paramvalue'),
            'help'     => $this->bbf('hlp_fm_voicemail-passwordlocation'),
            'selected' => $info['voicemail']['passwordlocation'],
            'default'  => $element['voicemail']['passwordlocation']['default']),
         $element['voicemail']['passwordlocation']['value']);
?>
</div>
