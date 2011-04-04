# -*- coding: UTF-8 -*-

# Depends on the following external programs:
#  -rsync

from subprocess import check_call


@target('ST2022-4.69.2', 'xivo-technicolor-ST2022-4.69.2')
def build_ST2022_4_69_2(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '--include', '/templates/base.tpl',
                '--include', '/templates/ST2022.tpl',
                '--exclude', '/templates/*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'ST2022-4.69.2/', path])


@target('ST2030-2.74', 'xivo-technicolor-ST2030-2.74')
def build_ST2030_2_74(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '--include', '/templates/base.tpl',
                '--include', '/templates/ST2030.tpl',
                '--exclude', '/templates/*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'ST2030-2.74/', path])


@target('TB30-1.74.0', 'xivo-technicolor-TB30-1.74.0')
def build_TB30_1_74_0(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '--include', '/templates/base.tpl',
                '--include', '/templates/TB30.tpl',
                '--exclude', '/templates/*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'TB30-1.74.0/', path])
