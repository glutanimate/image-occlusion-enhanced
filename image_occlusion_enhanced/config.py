# -*- coding: utf-8 -*-
####################################################
##                                                ##
##           Image Occlusion Enhanced             ##
##                                                ##
##      Copyright (c) Glutanimate 2016-2017       ##
##       (https://github.com/Glutanimate)         ##
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

IO_FLDS_IDS = ["id", "hd", "im", "qm",  "ft", "rk",
                "sc", "e1", "e2", "am", "om"]

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
                      'swidth': 3,
                      'font': 'Arial',
                      'fsize': 24,
                      'version': 1.00,
                      'skip': [IO_FLDS["e1"], IO_FLDS["e2"]],
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
        for key in default_conf_syncd.keys():
            if key not in mw.col.conf['imgocc']:
                mw.col.conf['imgocc'][key] = default_conf_syncd[key]
        mw.col.conf['imgocc']['version'] = default_conf_syncd['version']
        # insert other update actions here:
        # template.update_template(mw.col) # update card templates
        mw.col.setMod()


    # Local preferences
    if not 'imgocc' in mw.pm.profile:
        mw.pm.profile["imgocc"] = default_conf_local

    model = mw.col.models.byName(IO_MODEL_NAME)
    if not model:
        # create model and set up default field name config
        model = template.add_io_model(mw.col)
        mw.col.conf['imgocc']['flds'] = default_conf_syncd['flds']
    mflds = model['flds']
    ioflds = mw.col.conf['imgocc']['flds']
    ioflds_priv = []
    for i in IO_FIDS_PRIV:
        ioflds_priv.append(ioflds[i])
    # preserve fields if they are marked as sticky in the IO note type:
    ioflds_prsv = []
    for fld in mflds:
        fname = fld['name']
        if fld['sticky'] and fname not in ioflds_priv:
            ioflds_prsv.append(fname)

    self.sconf_dflt = default_conf_syncd
    self.sconf = mw.col.conf['imgocc']
    self.lconf = mw.pm.profile["imgocc"]

    self.ioflds = ioflds
    self.ioflds_priv = ioflds_priv
    self.ioflds_prsv = ioflds_prsv
    self.model = model
    self.mflds = mflds
