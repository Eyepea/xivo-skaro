#!/usr/bin/perl
#
use Switch;
use List::Util qw(reduce);
#
open my $fi, "< @ARGV[0]" or die $@;

%tmysql = (
	'bool' => 'tinyint(1)',
	'int'  => 'integer unsigned NOT NULL DEFAULT 0',
	'lint' => 'integer unsigned NOT NULL DEFAULT 0',
	'str'  => "varchar(1024) NOT NULL DEFAULT ''",
	'lstr' => "varchar(1024) NOT NULL DEFAULT ''",
	'txt'  => "text NOT NULL DEFAULT ''"
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
#	if ($_ !~ /^.n /) {
#		next;
#	}

	print $_;	
	$_ =~ /^ [nc] ([\w-]+)\s+([\w;,]+)?/;

	$fld = $1;
	@2 = split /;/,$2;
	#$fld =~ s/-/_/g;

	print "$fld @2\n";

	$smysql .= " `$fld` $tmysql{@2[0]};\n";
#	$sintl .= "; fm_$hprefix$fld\n";
#	$sintl .= " : \n\n";
	$sintl .= "; hlp_fm_$hprefix$fld\n";
	$sintl .= "Config asterisk: $fld\n";
	$sintl .= "\n";

	switch(@2[0]) {
		case 'bool' {
			$scfg .= "\$array['element']['$fld'] = array();\n";
			$scfg .= "\$array['element']['$fld']['value'] = array('no','yes');\n";
			$scfg .= "\$array['element']['$fld']['default'] = '@2[1]';\n";
			$scfg .= "\$array['element']['$fld']['set'] = true;\n\n";

			$stpl .= "    \$form->checkbox(array('desc'  => \$this->bbf('fm_$hprefix$fld'),\n";
			$stpl .= "              'name'    => '$xprefix$fld$yprefix',\n";
			$stpl .= "              'labelid' => '$lprefix$fld',\n";
			$stpl .= "              'help'    => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
			$stpl .= "              'checked' => \$this->get_var('$prefix','$fld','var_val'),\n";
			$stpl .= "              'default' => \$element$bprefix\['$fld'\]\['default'\])),\n\n";

			$sflt .= "\$array['filter']['$fld'] = array('bool' => true);\n";
		}

		case 'int' {
			$scfg .= "\$array['element']['$fld'] = array();\n";
			$scfg .= "\$array['element']['$fld']['value'] = range(0,256);\n";
			$scfg .= "\$array['element']['$fld']['default'] = @2[1];\n\n"; 

      $stpl .= "    \$form->select(array('desc'  => \$this->bbf('fm_$hprefix$fld'),\n";
			$stpl .= "            'name'     => '$xprefix$fld$yprefix',\n";
			$stpl .= "            'labelid'  => '$lprefix$fld',\n";
			$stpl .= "            'key'      => false,\n";
			$stpl .= "            'help'     => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
			$stpl .= "            'selected' => \$this->get_var('$prefix','$fld','var_val'),\n";
			$stpl .= "            'default'  => \$element$bprefix\['$fld'\]\['default'\]),\n";
			$stpl .= "        \$element:$bprefix\['$fld'\]\['value'\]),\n\n";
    
			$sflt .= "\$array['filter']['$fld'] = array('cast' => 'uint','between' => array(1,256));\n";
		}

		case 'str' {
			$scfg .= "\$array['element']['$fld'] = array();\n";
			$scfg .= "\$array['element']['$fld']['default'] = '@2[1]';\n";
			$scfg .= "\$array['element']['$fld']['null'] = true;\n\n";

			$stpl .= "    \$form->text(array('desc'  => \$this->bbf('fm_$hprefix$fld'),\n";
			$stpl .= "            'name'     => '$xprefix$fld$yprefix',\n";
			$stpl .= "            'labelid'  => '$lprefix$fld',\n";
			$stpl .= "            'size'     => 25,\n";
			$stpl .= "            'help'     => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
			$stpl .= "            'required' => false,\n";
			$stpl .= "            'value'    => \$this->get_var('$prefix','$fld','var_val'),\n";
			$stpl .= "            'default'  => \$element$bprefix\['$fld'\]\['default'\],\n";
			$stpl .= "            'error'    => \$this->bbf_args('error',\n";
			$stpl .= "        \$this->get_var('error', '$fld')) )),\n\n";

			$sflt .= "\$array['filter']['$fld'] = array('set' => false,'chk' => 2,'maxlen' => 1024);\n";
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
			$stpl .= "            'default' => \$element$bprefix\['$fld'\]\['default'\]),\n";
			$stpl .= "         \$element$bprefix\['$fld'\]\['value'\]),\n\n";

			foreach (split /,/,@2[2]) {
				$sintl .= "; fm_$hprefix$fld-opt($_)\n\n\n";
			}

			$sflt .= "\$array['filter']['$fld'] = array('key' => array(@2[2]));\n";
  	}

		case 'time' {
			my $interval = reduce { $b <= @2[3] ? "$a,$b":"$a" } map { $_ * @2[4] } @2[2]..@2[3];
			
			$scfg .= "\$array['element']['$fld'] = array();\n";                                                                             
			$scfg .= "\$array['element']['$fld']['value'] = array($interval);\n";                                                                                 
			$scfg .= "\$array['element']['$fld']['default'] = @2[1];\n\n";

			$stpl .= "     \$form->select(array('desc'  => \$this->bbf('fm_$hprefix$fld'),\n";
			$stpl .= "            'name'    => '$xprefix$fld$yprefix',\n";
			$stpl .= "            'labelid' => '$lprefix$fld',\n";
			$stpl .= "            'key'     => false,\n";
			$stpl .= "            'bbf'     => 'time-opt',\n";
			$stpl .= "            'bbfopt'  => array('argmode' => 'paramvalue',\n";
			$stpl .= "                 'time' => array('from'=>'second', 'format'=>'%M%s')),\n";
			$stpl .= "            'help'    => \$this->bbf('hlp_fm_$hprefix$fld'),\n";
			$stpl .= "            'selected'  => \$this->get_var('$prefix','$fld','var_val'),\n";
			$stpl .= "            'default' => \$element$bprefix\['$fld'\]\['default'\]),\n";
			$stpl .= "         \$element$bprefix\['$fld'\]\['value'\]),\n\n";

			$sflt .= "\$array['filter']['$fld'] = array('cast' => 'uint','between' => array(@2[2],@2[3],@2[4]));\n";
		}
  }
}

print $smysql;
print $scfg;
print $sflt;
print $stpl;
print $sintl;
