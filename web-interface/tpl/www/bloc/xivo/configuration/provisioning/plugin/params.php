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
$dhtml = &$this->get_module('dhtml');

$info = $this->get_var('info');
$provd_plugin = $this->get_var('provd_plugin');

if (($params = $info['params']) !== false
&& is_array($params) === true):

	foreach($params as $k => $v):

		if (isset($v['links'][0]) === false
		|| isset($v['links'][0]['href']) === false
		|| ($href = $v['links'][0]['href']) === '')
			continue;

?>
<div id="res-<?=$k?>"></div>
<?php 
	echo	$form->text(array('desc' => $this->bbf('fm_'.$k),
			  'name'	=> $k,
			  'labelid'	=> $k,
			  'size'	=> 15,
			  'help'	=> $v['description']));
?>
	<script type="text/javascript">
		$(function(){
			$.post('/xivo/configuration/ui.php/provisioning/plugin', 
				{ 
					act: 'getparams',
					uri: '<?=$href?>'
				},
				function(data){
					$('#it-<?=$k?>').val(data);
				}
			);
			$('#it-<?=$k?>').keyup(function(){
				delay(function(){
					$.post('/xivo/configuration/ui.php/provisioning/plugin',						
						{ 
							act: 'editparams',
							uri: '<?=$href?>',
							value: $('#it-<?=$k?>').val()
						},
						function(data){
							$('#res-<?=$k?>').show().html(data).delay(1000).hide('slow');
						}
					);
			    }, 600 );
			});
		});
	</script>
<?php 

	endforeach;
endif;

?>