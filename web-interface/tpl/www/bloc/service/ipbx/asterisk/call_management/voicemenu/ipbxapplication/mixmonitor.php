<div id="fd-ipbxapplication-mixmonitor" class="b-nodisplay">
<?php

$form = &$this->get_module('form');
$apparg_mixmonitor = $this->get_var('apparg_mixmonitor');

echo	$form->text(array('desc'	=> $this->bbf('fm_ipbxapplication_mixmonitor-filename'),
		          'name'	=> 'ipbxapplication[mixmonitor][filename]',
		          'labelid'	=> 'ipbxapplication-mixmonitor-filename',
		          'size'	=> 10,
		          'default'	=> $apparg_mixmonitor['filename']['default'])),

	$form->select(array('desc'	=> $this->bbf('fm_ipbxapplication_mixmonitor-fileformat'),
			    'name'	=> 'ipbxapplication[mixmonitor][fileformat]',
			    'labelid'	=> 'ipbxapplication-mixmonitor-fileformat',
			    'key'	=> false,
			    'bbf'	=> 'ast_format_name_info-',
			    'default'	=> $apparg_mixmonitor['fileformat']['default']),
		      $apparg_mixmonitor['fileformat']['value']),

	$form->checkbox(array('desc'	=> $this->bbf('fm_ipbxapplication_mixmonitor-a'),
			      'name'	=> 'ipbxapplication[mixmonitor][a]',
			      'labelid'	=> 'ipbxapplication-mixmonitor-a',
			      'default'	=> $apparg_mixmonitor['a']['default'])),

	$form->checkbox(array('desc'	=> $this->bbf('fm_ipbxapplication_mixmonitor-b'),
			      'name'	=> 'ipbxapplication[mixmonitor][b]',
			      'labelid'	=> 'ipbxapplication-mixmonitor-b',
			      'default'	=> $apparg_mixmonitor['b']['default'])),

	$form->checkbox(array('desc'	=> $this->bbf('fm_ipbxapplication_mixmonitor-v'),
			      'name'	=> 'ipbxapplication[mixmonitor][v]',
			      'labelid'	=> 'ipbxapplication-mixmonitor-v',
			      'default'	=> $apparg_mixmonitor['v']['default'])),

	$form->select(array('desc'	=> $this->bbf('fm_ipbxapplication_mixmonitor-v-volume'),
			    'name'	=> 'ipbxapplication[mixmonitor][v_volume]',
			    'labelid'	=> 'ipbxapplication-mixmonitor-v-volume',
			    'key'	=> false,
			    'default'	=> $apparg_mixmonitor['v_volume']['default']),
		      $apparg_mixmonitor['v_volume']['value']),

	$form->checkbox(array('desc'	=> $this->bbf('fm_ipbxapplication_mixmonitor-V'),
			      'name'	=> 'ipbxapplication[mixmonitor][vv]',
			      'labelid'	=> 'ipbxapplication-mixmonitor-vv',
			      'default'	=> $apparg_mixmonitor['V']['default'])),

	$form->select(array('desc'	=> $this->bbf('fm_ipbxapplication_mixmonitor-V-volume'),
			    'name'	=> 'ipbxapplication[mixmonitor][vv_volume]',
			    'labelid'	=> 'ipbxapplication-mixmonitor-vv-volume',
			    'key'	=> false,
			    'default'	=> $apparg_mixmonitor['V_volume']['default']),
		      $apparg_mixmonitor['V_volume']['value']),

	$form->checkbox(array('desc'	=> $this->bbf('fm_ipbxapplication_mixmonitor-W'),
			      'name'	=> 'ipbxapplication[mixmonitor][w]',
			      'labelid'	=> 'ipbxapplication-mixmonitor-w',
			      'default'	=> $apparg_mixmonitor['W']['default'])),

	$form->select(array('desc'	=> $this->bbf('fm_ipbxapplication_mixmonitor-W-volume'),
			    'name'	=> 'ipbxapplication[mixmonitor][w_volume]',
			    'labelid'	=> 'ipbxapplication-mixmonitor-w-volume',
			    'key'	=> false,
			    'default'	=> $apparg_mixmonitor['W_volume']['default']),
		      $apparg_mixmonitor['W_volume']['value']),

	$form->button(array('name'	=> 'add-ipbxapplication-mixmonitor',
			    'id'	=> 'it-add-ipbxapplication-mixmonitor',
			    'value'	=> $this->bbf('fm_bt-add')),
		      'onclick="xivo_ast_application_mixmonitor();"');

?>
</div>
