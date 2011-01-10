# -*- coding: UTF-8 -*-

from __future__ import with_statement

# Depends on the following external programs:
#  - rsync
#  - sed

import os.path
from shutil import copy
from subprocess import check_call


@target('8.4.18', 'xivo-snom-8.4.18')
def build_8_4_18(path):
    MODELS = [('300', 'f'),
              ('320', 'f'),
              ('360', 'f'),
              ('370', 'f'),
              ('820', 'r'),
              ('821', 'r'),
              ('870', 'r')]
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '--exclude', '/templates/*.mtpl',
                'common/', path])
    
    for model, fw_suffix in MODELS:
        # generate snom<model>-firmware.xml.tpl from snom-firmware.xml.mtpl
        model_tpl = os.path.join(path, 'templates', 'snom%s-firmware.xml.tpl' % model)
        sed_script = 's/#FW_FILENAME#/snom%s-8.4.18-SIP-%s.bin/' % (model, fw_suffix)
        with open(model_tpl, 'wb') as f:
            check_call(['sed', sed_script, 'common/templates/snom-firmware.xml.mtpl'],
                       stdout=f)
        
        # generate snom<model>.htm.tpl from snom.htm.mtpl
        model_tpl = os.path.join(path, 'templates', 'snom%s.htm.tpl' % model)
        sed_script = 's/#MODEL#/%s/' % model
        with open(model_tpl, 'wb') as f:
            check_call(['sed', sed_script, 'common/templates/snom.htm.mtpl'],
                       stdout=f)
        
        # generate snom<model>.xml.tpl from snom.xml.mtpl
        model_tpl = os.path.join(path, 'templates', 'snom%s.xml.tpl' % model)
        sed_script = 's/#MODEL#/%s/' % model
        with open(model_tpl, 'wb') as f:
            check_call(['sed', sed_script, 'common/templates/snom.xml.mtpl'],
                       stdout=f)
        
        # create <model>.tpl from model.mtpl
        copy('common/templates/model.mtpl', os.path.join(path, 'templates/%s.tpl' % model))
    
    check_call(['rsync', '-rlp', '--exclude', '.*',
                '8.4.18/', path])
