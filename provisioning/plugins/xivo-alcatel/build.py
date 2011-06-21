# -*- coding: UTF-8 -*-

# Depends on the following external programs:
#  -rsync

from subprocess import check_call


@target('2.01.10', 'xivo-alcatel-2.01.10')
def build_2_01_10(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '2.01.10/', path])
