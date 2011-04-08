# -*- coding: UTF-8 -*-

# Depends on the following external programs:
#  -rsync

from subprocess import check_call


@target('1', 'xivo-jitsi-1')
def build_1(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '1/', path])
