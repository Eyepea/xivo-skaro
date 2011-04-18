# -*- coding: UTF-8 -*-

# Depends on the following external programs:
#  -rsync

from subprocess import check_call


@target('60.0.110', 'xivo-yealink-60.0.110')
def build_60_0_110(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '60.0.110/', path])
