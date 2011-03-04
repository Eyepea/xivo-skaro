<?php
  $form = &$this->get_module('form');
	$url = &$this->get_module('url');

	$category     = $this->get_var('category');
	$membertype   = $this->get_var('membertype');
	$info         = $this->get_var('info');
	$datasource   = array_values($this->get_var($category,$membertype));

	if(!function_exists("dts_sort")) {
		function dts_sort($a,$b) {
			return strcmp($a['identity'],$b['identity']);
		}
	}
	usort($datasource, "dts_sort"); 

	$type         = $category.'-'.$membertype;

	$typeurl      = array(
		'groups' => 'service/ipbx/pbx_settings/groups',
		'queues' => 'service/ipbx/call_center/queues',
		'users'  => 'service/ipbx/pbx_settings/users'
	);

	if(count($datasource) > 0 || count($info[$category.'s'][$membertype])):
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
				 $datasource);?>
	</div>

	<div class="inout-list">
	<a href="#" onclick="dwho.form.move_selected('it-<?=$type?>list', 'it-<?=$type?>');
		return(dwho.dom.free_focus());" title="<?=$this->bbf('bt_in');?>">
		<?=$url->img_html('img/site/button/arrow-left.gif',  $this->bbf('bt_in'),
		  'class="bt-inlist" id="bt-in" border="0"');?></a><br />
			<a href="#" onclick="dwho.form.move_selected('it-<?=$type?>', 'it-<?=$type?>list');
		     return(dwho.dom.free_focus());" title="<?=$this->bbf('bt_out');?>">
			<?=$url->img_html('img/site/button/arrow-right.gif',
						$this->bbf('bt_out'), 
						"class=\"bt-outlist\" id=\"bt-out-$type\" border=\"0\"");?></a>
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
				 $info[$category.'s'][$membertype]);?>
		</div>
	</div>
	<div class="clearboth"></div>
<?php
	else:
		echo    "<div id=\"fd-create-$type\" class=\"txt-center\">",
			$url->href_htmln($this->bbf('create_'.$membertype),
				$typeurl[$membertype],
				'act=add'),
			'</div>';

	endif;
?>
