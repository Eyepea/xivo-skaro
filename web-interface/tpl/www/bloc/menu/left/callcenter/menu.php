<?php

#
# XiVO Web-Interface
# Copyright (C) 2010  Proformatique <technique@proformatique.com>
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

$url   = &$this->get_module('url');
$dhtml = &$this->get_module('dhtml');

?>
<dl>
	<dt>
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('mn_left_ti_callcenter');?></span>
		<span class="span-right">&nbsp;</span>
	</dt>
	<dd>
<?php
	if(xivo_user::chk_acl_section('service/callcenter') === true):

		echo '<dl>';

    	if(xivo_user::chk_acl('settings','','service/callcenter') === true):

    		echo	'<dt>',$this->bbf('mn_left_ti_callcenter-settings'),'</dt>';

        	if(xivo_user::chk_acl('settings','agents','service/callcenter') === true):
        		echo	'<dd id="mn-call-center--agents">',
        			$url->href_html($this->bbf('mn_left_callcenter-agents'),
        					'callcenter/settings/agents',
        					'act=list'),
        			'</dd>';
        	endif;

        	if(xivo_user::chk_acl('settings','queues','service/callcenter') === true):
        		echo	'<dd id="mn-call-center--queues">',
        			$url->href_html($this->bbf('mn_left_callcenter-queues'),
        					'callcenter/settings/queues',
        					'act=list'),
        			'</dd>';
        	endif;

        	if(xivo_user::chk_acl('settings','queuepenalty','service/callcenter') === true):
        		echo	'<dd id="mn-call-center--queues-penalties">',
        			$url->href_html($this->bbf('mn_left_callcenter-queues-penalties'),
        					'callcenter/settings/queuepenalty',
        					'act=list'),
        			'</dd>';
        	endif;

        	if(xivo_user::chk_acl('settings','queueskills','service/callcenter') === true):
        		echo	'<dd id="mn-call-center--queueskills">',
        			$url->href_html($this->bbf('mn_left_callcenter-queueskills'),
        					'callcenter/settings/queueskills',
        					'act=list'),
    					'</dd>';
        	endif;

        	if(xivo_user::chk_acl('settings','queueskillrules','service/callcenter') === true):
        		echo	'<dd id="mn-call-center--queueskillrules">',
        			$url->href_html($this->bbf('mn_left_callcenter-queueskillrules'),
        					'callcenter/settings/queueskillrules',
        					'act=list'),
        				'</dd>';
        	endif;

    	endif;

    	if(xivo_user::chk_acl('registrationcampaign','','service/callcenter') === true):

    		echo '<dt>',$this->bbf('mn_left_ti_callcenter-campaigns'),'</dt>';

        	if(xivo_user::chk_acl('registrationcampaign','general','service/callcenter') === true):
        		echo	'<dd id="mn-general">',
        			$url->href_html($this->bbf('mn_left_callcenter-general'),
        				'callcenter/registrationcampaign/general'),
        			'</dd>';
        	endif;
        	if(xivo_user::chk_acl('registrationcampaign','campaigns','service/callcenter') === true):
        		echo	'<dd id="mn-campaigns">',
        			$url->href_html($this->bbf('mn_left_callcenter-campaigns'),
        				'callcenter/registrationcampaign/campaigns'),
        			'</dd>';
        	endif;
        	if(xivo_user::chk_acl('registrationcampaign','tags','service/callcenter') === true):
        		echo	'<dd id="mn-tags">',
        			$url->href_html($this->bbf('mn_left_callcenter-tags'),
        				'callcenter/registrationcampaign/tags'),
        			'</dd>';
        	endif;

    	endif;

		echo	'</dl>';

	endif;
?>
	</dd>
	<dd class="b-nosize">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</dd>
</dl>
