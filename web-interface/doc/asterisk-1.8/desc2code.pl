#!/usr/bin/perl
#
use Switch;
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

while (<$fi>) {
	if(/^==/) {
		last;
	}
}

while (<$fi>) {
	if ($_ !~ /^.n /) {
		next;
	}

	#print $_;	
	$_ =~ /^ n (\w+)\s+([\w;,]+)/;
	@2 = split /;/,$2;
	#print "$1 @2\n";

	$smysql .= " `$1` $tmysql{@2[0]};\n";
	$sintl .= "; fm_$1\n";
	$sintl .= " : \n\n";
	$sintl .= "; hlp_fm_$1\n";
	$sintl .= "\n\n";

	switch(@2[0]) {
		case 'bool' {
			$scfg .= "\$array['element']['$1'] = array();\n";
			$scfg .= "\$array['element']['$1']['value'] = array('no','yes');\n";
			$scfg .= "\$array['element']['$1']['default'] = '@2[1]';\n\n";

			$stpl .= "    \$form->checkbox(array('desc'  => \$this->bbf('fm_$1'),\n";
			$stpl .= "              'name'    => '$1',\n";
			$stpl .= "              'labelid' => '$1',\n";
			$stpl .= "              'help'    => \$this->bbf('hlp_fm_$1'),\n";
			$stpl .= "              'checked' => \$this->get_var('info','$1','var_val'),\n";
			$stpl .= "              'default' => \$element['$1']['default'])),\n\n";

		}

		case 'int' {
			$scfg .= "\$array['element']['$1'] = array();\n";
			$scfg .= "\$array['element']['$1']['value'] = range(0,256);\n";
			$scfg .= "\$array['element']['$1']['default'] = @2[1];\n\n"; 

      $stpl .= "    \$form->select(array('desc'  => \$this->bbf('fm_$1'),\n";
			$stpl .= "            'name'     => '$1',\n";
			$stpl .= "            'labelid'  => '$1',\n";
			$stpl .= "            'key'      => false,\n";
			$stpl .= "            'help'     => \$this->bbf('hlp_fm_$1'),\n";
			$stpl .= "            'selected' => \$this->get_var('info','$1','var_val'),\n";
			$stpl .= "            'default'  => \$element['$1']['default']),\n";
			$stpl .= "        \$element['$1']['value']),\n\n";
    
		}

		case 'str' {
			$scfg .= "\$array['element']['$1'] = array();\n";
			$scfg .= "\$array['element']['$1']['default'] = '@2[1]';\n";
			$scfg .= "\$array['element']['$1']['null'] = true;\n\n";

			$stpl .= "    \$form->text(array('desc'  => \$this->bbf('fm_$1'),\n";
			$stpl .= "            'name'     => '$1',\n";
			$stpl .= "            'labelid'  => '$1',\n";
			$stpl .= "            'size'     => 25,\n";
			$stpl .= "            'help'     => \$this->bbf('hlp_fm_$1'),\n";
			$stpl .= "            'required' => false,\n";
			$stpl .= "            'value'    => \$this->get_var('info','$1','var_val'),\n";
			$stpl .= "            'default'  => \$element['$1']['default'],\n";
			$stpl .= "            'error'    => \$this->bbf_args('error',\n";
			$stpl .= "        \$this->get_var('error', '$1')) )),\n\n";

		}

		case 'lint' {
			$scfg .= "\$array['element']['$1'] = array();\n";                                                                             
			$scfg .= "\$array['element']['$1']['value'] = array(@2[2]);\n";                                                                                 
			$scfg .= "\$array['element']['$1']['default'] = @2[1];\n\n";

			$stpl .= "     \$form->select(array('desc'  => \$this->bbf('fm_$1'),\n";
			$stpl .= "            'name'    => '$1',\n";
			$stpl .= "            'labelid' => '$1',\n";
			$stpl .= "            'key'   => false,\n";
			$stpl .= "            'bbf'   => 'fm_$1-opt',\n";
			$stpl .= "            'bbfopt'  => array('argmode' => 'paramvalue'),\n";
			$stpl .= "            'help'    => \$this->bbf('hlp_fm_$1'),\n";
			$stpl .= "            'selected'  => \$this->get_var('info','$1','var_val'),\n";
			$stpl .= "            'default' => \$element['$1']['default']),\n";
			$stpl .= "         \$element['$1']['value']),\n\n";

			foreach (split /,/,@2[2]) {
				$sintl .= "; fm_$1-opt($_)\n\n\n";
			}
		}
	}

}

print $smysql;
print $scfg;
print $stpl;
print $sintl;
