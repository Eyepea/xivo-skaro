# -*- coding: UTF-8 -*-

# Depends on the following external programs:
#  -rsync

import os.path
from subprocess import check_call


@target('sccp-8.5.2', 'xivo-cisco-sccp-8.5.2')
def build_sccp_8_5_2(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'sccp-common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'sccp-8.5.2/', path])


@target('sccp-9.0.3', 'xivo-cisco-sccp-9.0.3')
def build_sccp_9_0_3(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'sccp-common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'sccp-9.0.3/', path])


@target('sccp-9.2.1', 'xivo-cisco-sccp-9.2.1')
def build_sccp_9_2_1(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'sccp-common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'sccp-9.2.1/', path])


@target('sccp-legacy', 'xivo-cisco-sccp-legacy')
def build_sccp_legacy(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'sccp-common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'sccp-legacy/', path])


@target('sip-9.2.1', 'xivo-cisco-sip-9.2.1')
def build_sip_9_2_1(path):
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'sip-common/', path])
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'sip-9.2.1/', path])
