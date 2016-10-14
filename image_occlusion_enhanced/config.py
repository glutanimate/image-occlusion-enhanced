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

"""
Sets up configuration, including constants
"""

import os
import sys

from aqt import mw

global IO_FLDS, IO_FLDS_IDS
global IO_MODEL_NAME, IO_CARD_NAME, IO_HOME

IO_MODEL_NAME = "Image Occlusion Enhanced"
IO_CARD_NAME = "IO Card"

IO_FLDS = {
    'id': u"ID (hidden)",
    'hd': u"Header",
    'im': u"Image",
    'ft': u"Footer",
    'rk': u"Remarks",
    'sc': u"Sources",
    'e1': u"Extra 1",
    'e2': u"Extra 2",
    'qm': u"Question Mask",
    'am': u"Answer Mask",
    'om': u"Original Mask"
}

IO_FLDS_IDS = ["id", "hd", "im", "ft", "rk", "sc", 
                "e1", "e2", "qm", "am", "om"]

# TODO: Use IDs instead of names to make these compatible with self.ioflds

# fields that aren't user-editable
IO_FIDS_PRIV = ['id', 'im', 'qm', 'am', 'om']

# fields that are synced between an IO Editor session and Anki's Editor
IO_FIDS_PRSV = ['sc']

# variables for local preference handling
sys_encoding = sys.getfilesystemencoding()
IO_HOME = os.path.expanduser('~').decode(sys_encoding)

# default configurations
default_conf_local = {"dir": IO_HOME}
default_conf_syncd = {'ofill': 'FFEBA2',
                      'qfill': 'FF7E7E',
                      'scol': '2D2D2D',
                      'swidth': 1,
                      'font': 'Arial',
                      'fsize': 24,
                      'version': 0.92,
                      'flds': IO_FLDS}

import template

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

        mw.col.setMod()

    elif mw.col.conf['imgocc']['version'] < default_conf_syncd['version']:
        print "Updating synced config DB from earlier IO release"
        # insert other update actions here
        for key in default_conf_syncd.keys():
            if key not in mw.col.conf['imgocc']:
                mw.col.conf['imgocc'][key] = default_conf_syncd[key]
        mw.col.conf['imgocc']['version'] = default_conf_syncd['version']
        mw.col.setMod()

    # Local preferences
    if not 'imgocc' in mw.pm.profile:
        mw.pm.profile["imgocc"] = default_conf_local

    ioflds = mw.col.conf['imgocc']['flds']
    ioflds_priv = []
    for i in IO_FIDS_PRIV:
        ioflds_priv.append(ioflds[i])
    model = mw.col.models.byName(IO_MODEL_NAME)
    if not model:
        model = template.add_io_model(mw.col)
    mflds = model['flds']
    ioflds_prsv = []
    for fld in mflds:
        if fld['sticky']:
            ioflds_prsv.append(fld['name'])

    self.sconf_dflt = default_conf_syncd
    self.sconf = mw.col.conf['imgocc']
    self.lconf = mw.pm.profile["imgocc"]
    
    self.ioflds = ioflds
    self.ioflds_priv = ioflds_priv
    self.ioflds_prsv = ioflds_prsv
    self.model = model
    self.mflds = mflds
