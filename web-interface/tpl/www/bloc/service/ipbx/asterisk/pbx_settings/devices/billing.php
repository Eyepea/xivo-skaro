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

$info    = $this->get_var('info');
$error   = $this->get_var('error');
$element = $this->get_var('element');

$listservicesgroup = $this->get_var('listservicesgroup');
$nb = count($listservicesgroup);

if (is_null($listservicesgroup) === false):

	$return = 'var listservicesgroup = new Array();';
	$return .= "\n";
	for($i=0;$i<$nb;$i++):
		$ref = &$listservicesgroup[$i];
		$return .= 'listservicesgroup['.$ref['id'].'] = "'.$ref['accountcode'].'";';
		$return .= "\n";
	endfor;

	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js($return);

endif;

if(isset($info['protocol']) === true):
	$amaflags = (string) dwho_ak('amaflags',$info['protocol'],true);
else:
	$amaflags = '';
endif;

?>
<?php
	echo $form->hidden(array('name'	=> 'protocol[accountcode]',
           		 'id'  	 => 'userfeatures-accountcode',
				 'value'	=> $this->get_var('info','protocol','accountcode'))),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_amaflags'),
				    'name'	=> 'protocol[amaflags]',
				    'labelid'	=> 'sip-protocol-amaflags',
				    'key'	=> false,
				    'bbf'	=> 'ast_amaflag_name_info',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['protocol']['sip']['amaflags']['default'],
				    'selected'	=> $amaflags),
			      $element['protocol']['sip']['amaflags']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_amaflags'),
				    'name'	=> 'protocol[amaflags]',
				    'labelid'	=> 'iax-protocol-amaflags',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'ast_amaflag_name_info',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['protocol']['iax']['amaflags']['default'],
				    'selected'	=> $amaflags),
			      $element['protocol']['iax']['amaflags']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_amaflags'),
				    'name'	=> 'protocol[amaflags]',
				    'labelid'	=> 'sccp-protocol-amaflags',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'ast_amaflag_name_info',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_sccp_amaflags'),
				    'default'	=> $element['protocol']['sccp']['amaflags']['default'],
				    'selected'	=> $amaflags),
			      $element['protocol']['sccp']['amaflags']['value']),

     $form->select(array('desc'  => $this->bbf('fm_userfeatures_servicesgroup'),
            'name'      => 'userfeatures[servicesgroup_id]',
            'labelid'   => 'userfeatures-servicesgroup_id',
            'key'       => 'name',
            'altkey'	=> 'id',
            'empty'     => true,
            'selected'  => $info['userfeatures']['servicesgroup_id'],
            'default'   => $element['userfeatures']['servicesgroup_id']['default']),
         $this->get_var('listservicesgroup'));

?>