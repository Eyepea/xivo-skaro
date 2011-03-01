# -*- coding: UTF-8 -*-

# Depends on the following external programs:
#  -rsync

from subprocess import check_call


@target('null', 'null')
def build_null(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'null/', path])


@target('zero', 'zero')
def build_zero(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'zero/', path])
