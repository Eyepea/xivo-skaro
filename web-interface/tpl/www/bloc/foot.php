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

$dhtml = &$this->get_module('dhtml');
$dhtml->load_js('foot');

?>
<script type="text/javascript">
	function clean_ms(input_id,select_from,select_to)
	{
		var box = document.getElementById(input_id);
		var select = document.getElementById(select_from);
		var select2 = document.getElementById(select_to);
		var select_cache = Array();
		
	    this.__init = __init;
	    this.reset = reset;
	    this.build_cache = build_cache;
	    this.populate = populate;
	    
	    function __init()
	    {
		    if (!box || !select || !select2)
			    return false;
	    	box.addEventListener("keyup", populate, false);		
			build_cache(select,select_cache);
	    }
		
		function reset() 
		{
			while (select.hasChildNodes())
			{
	            select.removeChild(select.firstChild);
	        }
	    }
	    
		function build_cache(arr,to) 
		{
			var nb = arr.length;
			for (var i = 0; i < nb; i++) 
			{
				var option = arr.options[i];
				to.push(new Option(option.text, option.value));
			}
		}		
		
		function populate(e)
		{
			update_cache();
			reset();
			var nb = select_cache.length;
			for (var i = 0; i < nb; i++) 
			{
				var option = select_cache[i];
				var expression = new RegExp(this.value.toLowerCase());
				if (expression.exec(option.text.toLowerCase()))
					select.add(option, null);
			}
		}
		
		function update_cache()
		{
			var nb = select2.length;
			for (var i = 0; i < nb; i++) 
			{
				var option2 = select2.options[i];

				var l = select_cache.length;
				for(var c = 0; c < l; c++) {
			        if(select_cache[c]
			        && select_cache[c].value == option2.value)
						select_cache.splice(c,1);
			    }
			}
		}
	}
</script>
		<h6 id="version-copyright">
<?php
		echo	XIVO_SOFT_LABEL,' - ',
			$this->bbf('info_version'),' ',
			XIVO_SOFT_VERSION,' "',XIVO_SOFT_CODENAME,'" | ',
			$this->bbf('visit_for_information',
				   '<a href="http://'.XIVO_SOFT_URL.'" title="'.XIVO_SOFT_LABEL.'" target="_blank">'.XIVO_SOFT_URL.'</a>'),' | ',
			$this->bbf('info_copyright',
				   array(2006,dwho_i18n::strftime_l('%Y',null),
				   '<a href="http://'.XIVO_CORP_URL.'" title="'.XIVO_CORP_LABEL.'" target="_blank">'.XIVO_CORP_LABEL.'</a>'));
?>
		</h6>
	</body>
</html>
