# -*- coding: utf-8 -*-
####################################################
##                                                ##
##           Image Occlusion Enhanced             ##
##                                                ##
##        Copyright (c) Glutanimate 2016          ##
##       (https://github.com/Glutanimate)         ##
##                                                ##
##     Original Image Occlusion 2.0 add-on is     ##
##         Copyright (c) 2012-2015 tmbb           ##
##           (https://github.com/tmbb)            ##
##                                                ##
####################################################

import os
import sys

from aqt import mw

global IO_FLDS, IO_FLDS_IDS, IO_FLDS_PRIV, IO_FLDS_PRSV
global IO_MODEL_NAME, IO_CARD_NAME, IO_HOME

IO_MODEL_NAME = "Image Occlusion Enhanced"
IO_CARD_NAME = "IO Card"

IO_FLDS = {
    'id': u"ID (hidden)",
    'hd': u"Header",
    'im': u"Image",
    'ft': u"Footer",
    'rk': u"Anmerkungen",
    'sc': u"Quellen",
    'e1': u"Extra 1",
    'e2': u"Extra 2",
    'qm': u"Question Mask",
    'am': u"Answer Mask",
    'om': u"Original Mask"
}

IO_FLDS_IDS = ["id", "hd", "im", "ft", "rk", "sc", 
                "e1", "e2", "qm", "am", "om"]

# fields that aren't user-editable
IO_FLDS_PRIV = [IO_FLDS['id'], IO_FLDS['im'], IO_FLDS['qm'], 
                IO_FLDS['am'], IO_FLDS['om']]

# fields that are synced between an IO Editor session and Anki's Editor
IO_FLDS_PRSV = [IO_FLDS['sc']]



# variables for local preference handling
sys_encoding = sys.getfilesystemencoding()
IO_HOME = os.path.expanduser('~').decode(sys_encoding)

# default configurations
default_conf_local = {"dir": IO_HOME}
default_conf_syncd = {'ofill': 'FFEBA2',
                      'qfill': 'FF7E7E',
                      'version': 0.7,
                      'flds': IO_FLDS}

def loadConfig(self):
    """load and/or create add-on preferences"""
    # Synced preferences
    if not 'imgocc' in mw.col.conf:
        # create initial configuration
        mw.col.conf['imgocc'] = default_conf_syncd
        
        # upgrade from earlier IO versions:
        if 'image_occlusion_conf' in mw.col.conf:
            old_conf = mw.col.conf['image_occlusion_conf']
            mw.col.conf['imgocc']['ofill'] = old_conf['initFill[color]']
            mw.col.conf['imgocc']['qfill'] = old_conf['mask_fill_color']
            # insert other upgrade actions here

    if mw.col.conf['imgocc']['version'] < default_conf_syncd['version']:
        print "updating synced config db from earlier IO release"
        # insert other update actions here
        mw.col.conf['imgocc']['flds'] = IO_FLDS
        mw.col.conf['imgocc']['version'] = default_conf_syncd['version']

    # Local preferences
    if not 'imgocc' in mw.pm.profile:
        mw.pm.profile["imgocc"] = default_conf_local

    self.sconf_d = default_conf_syncd
    self.sconf = mw.col.conf['imgocc']
    self.ioflds = mw.col.conf['imgocc']['flds']
    self.lconf = mw.pm.profile["imgocc"]
