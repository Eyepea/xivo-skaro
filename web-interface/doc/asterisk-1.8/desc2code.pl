#!/usr/bin/perl
#
# Supported items:
#
# ====
#    end of comments, start of fields. appears once at max
#
# =prefix:xxx
#    prefix fieldname with xxx (in template)
#    can be place anywhere (and changed) in fields list
#
# n field str;dtf;len;null
#    string field. 
#      dft  = default value
#      len  = field max length
#      null = 0,1 (default 1), means set to NULL when empty string
#
# n field lstr;dft;values;null
#    list-of string values field
#      values = '-' separated values
#      null   = 0,1, means NULL allowed
#
# n field bool;dft;null
#    boolean field
#      dft  = true,false ; default value 
#      null = 0,1 ; null allowed
#
# n field int;dft;min;max;step;null
#    integer field
#
# n field double;dft;min;max;step;null
#    double field
#
# n field time;dft;min;max;step;null
#   time field
#      dft  = default value (integer)
#      min,max,step = in seconds
#      null = 0,1, (default 0) allow empty value
#      
#
#
use Switch;
use List::Util qw(reduce);
#
open my $fi, "< @ARGV[0]" or die $@;

%tmysql = (
	'bool' => 'tinyint(1) NOT NULL DEFAULT 0',
	'int'  => 'integer unsigned NOT NULL DEFAULT 0',
	'lint' => 'integer unsigned NOT NULL DEFAULT 0',
	'str'  => "varchar(1024) NOT NULL DEFAULT ''",
	'lstr' => "varchar(1024) NOT NULL DEFAULT ''",
	'txt'  => "text NOT NULL DEFAULT ''",
	'double' => "float NOT NULL DEFAULT 0",
	'time' => 'integer unsigned NOT NULL DEFAULT 0',
);
$smysql = "=== mysql\n";
$stpl   = "=== tpl\n";
$sintl  = "=== l10n\n";
$scfg   = "=== cfg\n";
$sflt   = "=== filter\n";

$prefix = "info";
$hprefix = "";
$bprefix = "";
$lprefix = "";
$xprefix = "";
$yprefix = "";

while (<$fi>) {
	if(/^==/) {
		last;
	}

	if(/^=prefix:(.*)$/) {
		$prefix  = $1;
		$hprefix = "$1_";
		$bprefix = "\['$1'\]";
		$lprefix = "$1-";
		$xprefix = "$1\[";
		$yprefix = "]";
		}
}

while (<$fi>) {
	if(/^=prefix:(.*)$/) {
		$prefix  = $1;
		$hprefix = "$1-";
		$bprefix = "\['$1'\]";
		$lprefix = "$1-";
		$xprefix = "$1\[";
		$yprefix = "]";
		}

	if ($_ !~ /^.n /) {
		next;
	}

	print $_;	
	$_ =~ /^ . ([\w-]+)\s+(\S+)?\s*$/;
	

	$fld = $1;
	@2 = split /;/,$2;
	#$fld =~ s/-/_/g;

	print ">> $fld @2\n";

	$smysql .= " `$fld` $tmysql{@2[0]},\n";
	$sintl .= "; fm_$hprefix$fld\n";
	$sintl .= " : \n\n";
	$sintl .= "; hlp_fm_$hprefix$fld\n";
	$sintl .= "Config asterisk: $fld\n";
	$sintl .= "\n";

	switch(@2[0]) {
		case 'bool' {
			if(@2[2] == 0) {
				$scfg .= "\$array['element']['$fld'] = array();\n";
				$scfg .= "\$array['element']['$fld']['value'] = array('no','yes');\n";
				$scfg .= "\$array['element']['$fld']['default'] = '@2[1]';\n";
				$scfg .= "\$array['element']['$fld']['set'] = true;\n\n";

				$stpl .= "    \$form->checkbox(array('desc'  => \$this->bbf('fm_$hprefix$fld'),\n";
				$stpl .= "              'name'    => '$xprefix$fld$yprefix',\n";
				$stpl .= "              'labelid' => '$lprefix$fld',\n";
				$stpl .= "              'help'    => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
				$stpl .= "              'checked' => \$this->get_var('$prefix','$fld','var_val'),\n";
				$stpl .= "              'checked' => \$info['$prefix']['$fld'],\n";
				$stpl .= "              'default' => \$element$bprefix\['$fld'\]\['default'\])),\n\n";

				$sflt .= "\$array['filter']['$fld'] = array('bool' => true);\n";
			}
			else
			{
				$scfg .= "\$array['element']['$fld'] = array();\n";                                      
				$scfg .= "\$array['element']['$fld']['value'] = array(1, 0);\n";
				$scfg .= "\$array['element']['$fld']['default'] = '';\n";
				$scfg .= "\$array['element']['$fld']['null']    = true;\n\n";

				$stpl .= "     \$form->select(array('desc'  => \$this->bbf('fm_$hprefix$fld'),\n";
				$stpl .= "            'name'      => '$xprefix$fld$yprefix',\n";
				$stpl .= "            'labelid'   => '$lprefix$fld',\n";
				$stpl .= "            'key'       => false,\n";
				$stpl .= "            'empty'     => true,\n";
				$stpl .= "            'bbf'       => 'fm_bool-opt',\n";
				$stpl .= "            'bbfopt'    => array('argmode' => 'paramvalue'),\n";
				$stpl .= "            'help'      => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
				$stpl .= "            'selected'  => \$this->get_var('$prefix','$fld','var_val'),\n";
				$stpl .= "            'selected'  => \$info['$prefix']['$fld'],\n";
				$stpl .= "            'default'   => \$element$bprefix\['$fld'\]\['default'\]),\n";
				$stpl .= "         \$element$bprefix\['$fld'\]\['value'\]),\n\n";

				$sflt .= "\$array['filter']['$fld'] = array('set' => false, 'chk' => 2, 'bool' => true);\n";
			}
		}

		case 'int' {
			$scfg .= "\$array['element']['$fld'] = array();\n";
			$scfg .= "\$array['element']['$fld']['value'] = range(@2[2],@2[3],@2[4]);\n";
			if(@2[1] == '')
			{	$scfg .= "\$array['element']['$fld']['default'] = '';\n"; }
			else
			{ $scfg .= "\$array['element']['$fld']['default'] = @2[1];\n"; }
			if(@2[5] == 1)
			{ $scfg .= "\$array['element']['$fld']['null'] = true;\n"; }
			$scfg .= "\n";

      $stpl .= "    \$form->select(array('desc'  => \$this->bbf('fm_$hprefix$fld'),\n";
			$stpl .= "            'name'     => '$xprefix$fld$yprefix',\n";
			$stpl .= "            'labelid'  => '$lprefix$fld',\n";
			$stpl .= "            'key'      => false,\n";
			if(@2[5] == 1)
			{ $stpl .= "            'empty'    => true,\n"; }
			$stpl .= "            'help'     => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
			$stpl .= "            'selected' => \$this->get_var('$prefix','$fld','var_val'),\n";
			$stpl .= "            'selected' => \$info['$prefix']['$fld'],\n";
			$stpl .= "            'default'  => \$element$bprefix\['$fld'\]\['default'\]),\n";
			$stpl .= "        \$element$bprefix\['$fld'\]\['value'\]),\n\n";
    
			$sflt .= "\$array['filter']['$fld'] = array(";
			if(@2[5] == 1)
			{ $sflt .= "'set' => false, 'chk' => 2, "; }
			$sflt .= "'cast' => 'uint','between' => array(@2[2],@2[3],@2[4]));\n";
		}

		case 'str' {
			$scfg .= "\$array['element']['$fld'] = array();\n";
			$scfg .= "\$array['element']['$fld']['default'] = '@2[1]';\n";
			$scfg .= "\$array['element']['$fld']['null'] = true;\n\n";

			$stpl .= "    \$form->text(array('desc'  => \$this->bbf('fm_$hprefix$fld'),\n";
			$stpl .= "            'name'     => '$xprefix$fld$yprefix',\n";
			$stpl .= "            'labelid'  => '$lprefix$fld',\n";
			$stpl .= "            'size'     => @2[2],\n";
			$stpl .= "            'help'     => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
			$stpl .= "            'required' => false,\n";
			$stpl .= "            'value'    => \$this->get_var('$prefix','$fld','var_val'),\n";
			$stpl .= "            'value'    => \$info['$prefix']['$fld'],\n";
			$stpl .= "            'default'  => \$element$bprefix\['$fld'\]\['default'\],\n";
			$stpl .= "            'error'    => \$this->bbf_args('error',\n";
			$stpl .= "        \$this->get_var('error', '$fld')) )),\n\n";

			$sflt .= "\$array['filter']['$fld'] = array('set' => false,'chk' => 2,'maxlen' => @2[2]);\n";
		}

		case 'txt' {
			$scfg .= "\$array['element']['$fld'] = array();\n";
			$scfg .= "\$array['element']['$fld']['default'] = '@2[1]';\n";
			$scfg .= "\$array['element']['$fld']['null'] = true;\n\n";

			$stpl .= "    \$form->textarea(array('paragraph' => false,\n";
			$stpl .= "            'label'    => false,\n";
			$stpl .= "            'name'     => '$xprefix$fld$yprefix',\n";
			$stpl .= "            'id'       => '$lprefix$fld',\n";
			$stpl .= "            'cols'     => 60,\n";
      $stpl .= "            'rows'     => 5,\n";
			$stpl .= "            'help'     => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
			$stpl .= "            'default'  => \$element$bprefix\['$fld'\]\['default'\],\n";
			$stpl .= "            'error'    => \$this->bbf_args('error',\n";
			$stpl .= "               \$this->get_var('error', '$fld'))),\n";
			$stpl .= "          \$info['$prefix']['$fld']),\n\n";

			$sflt .= "\$array['filter']['$fld'] = array('set' => false,'chk' => 2,'maxlen' => @2[2]);\n";
		}

		case 'lstr' {
	 		@mstr = join(',', map { "'$_'" } split /,/,@2[2]);
			$scfg .= "\$array['element']['$fld'] = array();\n";
			$scfg .= "\$array['element']['$fld']['value'] = array(@mstr);\n";
			$scfg .= "\$array['element']['$fld']['default'] = '@2[1]';\n";
			if(@2[3] == 1)
			{ $scfg .= "\$array['element']['$fld']['null'] = true;\n"; }
			$scfg .= "\n";

			$stpl .= "     \$form->select(array('desc'  => \$this->bbf('fm_$hprefix$fld'),\n";
			$stpl .= "            'name'    => '$xprefix$fld$yprefix',\n";
			$stpl .= "            'labelid' => '$lprefix$fld',\n";
			$stpl .= "            'key'   => false,\n";
			if(@2[3] == 1)
			{ $stpl .= "            'empty' => true,\n"; }
			$stpl .= "            'bbf'   => 'fm_$hprefix$fld-opt',\n";
			$stpl .= "            'bbfopt'  => array('argmode' => 'paramvalue'),\n";
			$stpl .= "            'help'    => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
			$stpl .= "            'selected'  => \$this->get_var('$prefix','$fld','var_val'),\n";
			$stpl .= "            'selected'  => \$info['$prefix']['$fld'],\n";
			$stpl .= "            'default' => \$element$bprefix\['$fld'\]\['default'\]),\n";
			$stpl .= "         \$element$bprefix\['$fld'\]\['value'\]),\n\n";

			foreach (split /,/,@2[2]) {
				$sintl .= "; fm_$hprefix$fld-opt($_)\n\n\n";
			}

			$sflt .= "\$array['filter']['$fld'] = array(";
			if(@2[3] == 1)
			{ $sflt .= "'set' => false, 'chk' => 2, "; }
			$sflt .= "'key' => array(@mstr));\n";
  	}

		case 'lint' {
			$scfg .= "\$array['element']['$fld'] = array();\n";                                                                             
			$scfg .= "\$array['element']['$fld']['value'] = array(@2[2]);\n";                                                                                 
			$scfg .= "\$array['element']['$fld']['default'] = @2[1];\n\n";

			$stpl .= "     \$form->select(array('desc'  => \$this->bbf('fm_$hprefix$fld'),\n";
			$stpl .= "            'name'    => '$xprefix$fld$yprefix',\n";
			$stpl .= "            'labelid' => '$lprefix$fld',\n";
			$stpl .= "            'key'   => false,\n";
			$stpl .= "            'bbf'   => 'fm_$hprefix$fld-opt',\n";
			$stpl .= "            'bbfopt'  => array('argmode' => 'paramvalue'),\n";
			$stpl .= "            'help'    => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
			$stpl .= "            'selected'  => \$this->get_var('$prefix','$fld','var_val'),\n";
			$stpl .= "            'selected'  => \$info['$prefix']['$fld'],\n";
			$stpl .= "            'default' => \$element$bprefix\['$fld'\]\['default'\]),\n";
			$stpl .= "         \$element$bprefix\['$fld'\]\['value'\]),\n\n";

			foreach (split /,/,@2[2]) {
				$sintl .= "; fm_$hprefix$fld-opt($_)\n\n\n";
			}

			$sflt .= "\$array['filter']['$fld'] = array(";
			if(@2[5] == 1)
			{ $sflt .= "'set' => false, 'chk' => 2, "; }
			$sflt .= "'key' => array(@2[2]));\n";
  	}

		case 'double' {
			my @interval = ();
			for($i = @2[2]; $i <= @2[3]; $i = $i + @2[4])
			{ push @interval, $i; }
			my $interval = reduce { $b <= @2[3] ? "$a,$b":"$a" } @interval;

			$scfg .= "\$array['element']['$fld'] = array();\n";
			$scfg .= "\$array['element']['$fld']['value'] = array($interval);\n";
			if(@2[1] == '')
			{ $scfg .= "\$array['element']['$fld']['default'] = '';\n"; }
			else
			{ $scfg .= "\$array['element']['$fld']['default'] = @2[1];\n"; }
			if(@2[5] == 1)
			{ $scfg .= "\$array['element']['$fld']['null'] = true;\n"; }
			$scfg .= "\n";

			$stpl .= "     \$form->select(array('desc'  => \$this->bbf('fm_$hprefix$fld'),\n";
			$stpl .= "            'name'      => '$xprefix$fld$yprefix',\n";
			$stpl .= "            'labelid'   => '$lprefix$fld',\n";
			$stpl .= "            'key'       => false,\n";
			if(@2[5] == 1)
			{ $stpl .= "            'empty'     => true,\n"; }
			$stpl .= "            'bbf'       => 'fm_$hprefix$fld-opt',\n";
			$stpl .= "            'bbfopt'    => array('argmode' => 'paramvalue'),\n";
			$stpl .= "            'help'      => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
			$stpl .= "            'selected'  => \$this->get_var('$prefix','$fld','var_val'),\n";
			$stpl .= "            'selected'  => \$info['$prefix']['$fld'],\n";
			$stpl .= "            'default'   => \$element$bprefix\['$fld'\]\['default'\]),\n";
			$stpl .= "         \$element$bprefix\['$fld'\]\['value'\]),\n\n";

			foreach (split /,/,@2[2]) {
				$sintl .= "; fm_$hprefix$fld-opt($_)\n\n\n";
			}

			$sflt .= "\$array['filter']['$fld'] = array(";
			if(@2[5] == 1)
			{ $sflt .= "'set' => false, 'chk' => 2, "; }
			$sflt .= "'cast' => 'float', 'key' => array($interval));\n";
  	}

		case 'time' {
			my $interval = reduce { $b <= @2[3] ? "$a,$b":"$a" } map { $_ * @2[4] } @2[2]..@2[3];
			
			$scfg .= "\$array['element']['$fld'] = array();\n";
			$scfg .= "\$array['element']['$fld']['value'] = array($interval);\n";
			$scfg .= "\$array['element']['$fld']['default'] = '@2[1]';\n"; 
			if(@2[5] == 1)
			{ $scfg .= "\$array['element']['$fld']['null'] = true;\n"; }
			$scfg .= "\n";

			$stpl .= "     \$form->select(array('desc'  => \$this->bbf('fm_$hprefix$fld'),\n";
			$stpl .= "            'name'      => '$xprefix$fld$yprefix',\n";
			$stpl .= "            'labelid'   => '$lprefix$fld',\n";
			$stpl .= "            'key'       => false,\n";
			if(@2[1] == 'null')
			{ $stpl .= "            'empty'     => true,\n"; }
			$stpl .= "            'bbf'       => 'time-opt',\n";
			$stpl .= "            'bbfopt'    => array('argmode' => 'paramvalue',\n";
			$stpl .= "            'time'      => array('from'=>'second', 'format'=>'%M%s')),\n";
			$stpl .= "            'help'      => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
			$stpl .= "            'selected'  => \$this->get_var('$prefix','$fld','var_val'),\n";
			$stpl .= "            'selected'  => \$info['$prefix']['$fld'],\n";
			$stpl .= "            'default'   => \$element$bprefix\['$fld'\]\['default'\]),\n";
			$stpl .= "         \$element$bprefix\['$fld'\]\['value'\]),\n\n";

			$sflt .= "\$array['filter']['$fld'] = array(";
			if(@2[5] == 1)
			{ $sflt .= "'set' => false, 'chk' => 2, "; }
			$sflt .= "'cast' => 'uint','between' => array(@2[2],@2[3],@2[4]));\n";
		}
  }
}

print $smysql;
print $scfg;
print $sflt;
print $stpl;
print $sintl;
