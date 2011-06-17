# -*- coding: UTF-8 -*-

# Depends on the following external programs:
#  -rsync

from subprocess import check_call


# target(<target_id>, <pg_id>)
# any error raised will be considered a build error
# Pre: pg_dir is initially empty
# Pre: current directory is the one of the bplugin
@target('2.6.0.2019', 'xivo-aastra-2.6.0.2019')
def build_2_6_0_2019(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '--exclude', '/templates/6739i.tpl',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '2.6.0.2019/', path])


@target('3.0.1.2031', 'xivo-aastra-3.0.1.2031')
def build_3_0_1_2031(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '--include', '/templates/6739i.tpl',
                '--include', '/templates/base.tpl',
                '--exclude', '/templates/*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '3.0.1.2031/', path])


@target('3.2.1.1019', 'xivo-aastra-3.2.1.1019')
def build_3_2_1_1019(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '--exclude', '/templates/6751i.tpl',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '3.2.1.1019/', path])
