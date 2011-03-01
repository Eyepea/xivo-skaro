# -*- coding: UTF-8 -*-

# Depends on the following external programs:
#  -rsync
#  -sed

import os.path
from subprocess import check_call


@target('9.0.3', 'xivo-cisco-sccp-9.0.3')
def build_9_0_3(path):
    MODELS=[('7906G', '11'),
            ('7911G', '11'),
            ('7931G', '31'),
            ('7941G', '41'),
            ('7942G', '42'),
            ('7945G', '45'),
            ('7961G', '41'),
            ('7962G', '42'),
            ('7965G', '45'),
            ('7970G', '70'),
            ('7971G', '70'),
            ('7975G', '75')]
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '--exclude', '/templates/*.mtpl',
                'common/', path])
    
    for model, no in MODELS:
        model_tpl = os.path.join(path, 'templates', model + '.tpl')
        sed_script = 's/#LOAD_INFORMATION#/SCCP%s.9-0-3S/' % no
        with open(model_tpl, 'wb') as f:
            check_call(['sed', sed_script, 'common/templates/model.mtpl'],
                        stdout=f)
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '9.0.3/', path])


@target('legacy', 'xivo-cisco-sccp-legacy')
def build_legacy(path):
    MODELS=[('7902G', 'CP7902080002SCCP060817A'), 
            ('7905G', 'CP7905080003SCCP070409A'),
            ('7910G', 'P00405000700'),
            ('7912G', 'CP7912080004SCCP080108A'),
            ('7940G', 'P00308010200'),
            ('7960G', 'P00308010200')]
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '--exclude', '/templates/*.mtpl',
                'common/', path])
    
    for model, no in MODELS:
        model_tpl = os.path.join(path, 'templates', model + '.tpl')
        sed_script = 's/#LOAD_INFORMATION#/%s/' % no
        with open(model_tpl, 'wb') as f:
            check_call(['sed', sed_script, 'common/templates/model.mtpl'],
                        stdout=f)
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                'legacy/', path])
