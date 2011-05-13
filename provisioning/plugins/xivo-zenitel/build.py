# -*- coding: UTF-8 -*-

# Depends on the following external programs:
#  -rsync

from subprocess import check_call


@target('01.11.3.2', 'xivo-zenitel-01.11.3.2')
def build_01_11_3_2(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '01.11.3.2/', path])
