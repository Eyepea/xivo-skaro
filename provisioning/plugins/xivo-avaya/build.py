# -*- coding: UTF-8 -*-

# Depends on the following external programs:
#  -rsync

from subprocess import check_call


@target('4.1.13', 'xivo-avaya-4.1.13')
def build_4_1_13(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '4.1.13/', path])
