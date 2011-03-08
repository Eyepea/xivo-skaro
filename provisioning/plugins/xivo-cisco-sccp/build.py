# -*- coding: UTF-8 -*-

# Depends on the following external programs:
#  -rsync

import os.path
from subprocess import check_call


@target('8.5.2', 'xivo-cisco-sccp-8.5.2')
def build_8_5_2(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '8.5.2/', path])


@target('9.0.3', 'xivo-cisco-sccp-9.0.3')
def build_9_0_3(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '9.0.3/', path])


@target('legacy', 'xivo-cisco-sccp-legacy')
def build_legacy(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'legacy/', path])
