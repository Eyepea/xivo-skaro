<?php
  $form = &$this->get_module('form');
	$url = &$this->get_module('url');

	$type         = $this->get_var('type');
	$info         = $this->get_var('info');
	$ctipresences = $this->get_var($type);

	if($ctipresences !== false):
?>
<div id="<?=$type?>list" class="fm-paragraph fm-multilist">
	<?=$form->input_for_ms($type.'list',$this->bbf('ms_seek'))?>
	<div class="slt-outlist">
		<?=$form->select(array('name'		=> $type.'list',
				       'label'		=> false,
				       'id'		=> 'it-'.$type.'list',
				       'multiple'	=> true,
				       'size'		=> 5,
				       'paragraph'	=> false,
				       'key'		=> 'identity',
				       #'key'		=> 'name',
				       'altkey'		=> 'id'),
				 $ctipresences);?>
	</div>

	<div class="inout-list">
	<a href="#" onclick="dwho.form.move_selected('it-<?=$type?>list', 'it-<?=$type?>');
		return(dwho.dom.free_focus());" title="<?=$this->bbf('bt_in'.$type);?>">
		<?=$url->img_html('img/site/button/arrow-left.gif',  $this->bbf('bt_in'.$type),
		  'class="bt-inlist" id="bt-in'.$type.'" border="0"');?></a><br />
			<a href="#" onclick="dwho.form.move_selected('it-<?=$type?>', 'it-<?=$type?>list');
		     return(dwho.dom.free_focus());" title="<?=$this->bbf('bt_out'.$type);?>">
			<?=$url->img_html('img/site/button/arrow-right.gif',
						$this->bbf('bt_out'.$type), 
						'class="bt-outlist" id="bt-out<?=$type?>" border="0"');?></a>
	</div>

	<div class="slt-inlist">
		<?=$form->select(array('name'		=> $type.'[]',
		       'label'		=> false,
		       'id'		=> 'it-'.$type,
		       'multiple'	=> true,
		       'size'		=> 5,
		       'paragraph'	=> false,
		       'key'		=> 'identity',
		       'altkey'		=> 'id'),
				 $info['queuefeatures'][$type]);?>
		</div>
	</div>
	<div class="clearboth"></div>
<?php
	endif;
?>
