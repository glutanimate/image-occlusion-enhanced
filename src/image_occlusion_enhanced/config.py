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

# TODO: move constants to consts.py

import os
import sys

from aqt import mw

global IO_FLDS, IO_FLDS_IDS
global IO_MODEL_NAME, IO_CARD_NAME, IO_HOME, IO_HOTKEY

IO_MODEL_NAME = "Image Occlusion Enhanced"
IO_CARD_NAME = "IO Card"

IO_FLDS = {
    'id': "ID (hidden)",
    'hd': "Header",
    'im': "Image",
    'ft': "Footer",
    'rk': "Remarks",
    'sc': "Sources",
    'e1': "Extra 1",
    'e2': "Extra 2",
    'qm': "Question Mask",
    'am': "Answer Mask",
    'om': "Original Mask"
}

IO_FLDS_IDS = ["id", "hd", "im", "qm", "ft", "rk",
               "sc", "e1", "e2", "am", "om"]

# TODO: Use IDs instead of names to make these compatible with self.ioflds

# fields that aren't user-editable
IO_FIDS_PRIV = ['id', 'im', 'qm', 'am', 'om']

# fields that are synced between an IO Editor session and Anki's Editor
IO_FIDS_PRSV = ['sc']

# variables for local preference handling
sys_encoding = sys.getfilesystemencoding()
IO_HOME = os.path.expanduser('~')
IO_HOTKEY = "Ctrl+Shift+O"

# default configurations
# TODO: update version number before release
default_conf_local = {'version': 1.25,
                      'dir': IO_HOME,
                      'hotkey': IO_HOTKEY}
default_conf_syncd = {'version': 1.25,
                      'ofill': 'FFEBA2',
                      'qfill': 'FF7E7E',
                      'scol': '2D2D2D',
                      'swidth': 3,
                      'font': 'Arial',
                      'fsize': 24,
                      'skip': [IO_FLDS["e1"], IO_FLDS["e2"]],
                      'flds': IO_FLDS}

from . import template


def getSyncedConfig():
    # Synced preferences
    if 'imgocc' not in mw.col.conf:
        # create initial configuration
        mw.col.conf['imgocc'] = default_conf_syncd

        # upgrade from IO 2.0:
        if 'image_occlusion_conf' in mw.col.conf:
            old_conf = mw.col.conf['image_occlusion_conf']
            mw.col.conf['imgocc']['ofill'] = old_conf['initFill[color]']
            mw.col.conf['imgocc']['qfill'] = old_conf['mask_fill_color']
            # insert other upgrade actions here
        mw.col.setMod()

    elif mw.col.conf['imgocc']['version'] < default_conf_syncd['version']:
        print("Updating config DB from earlier IO release")
        for key in list(default_conf_syncd.keys()):
            if key not in mw.col.conf['imgocc']:
                mw.col.conf['imgocc'][key] = default_conf_syncd[key]
        mw.col.conf['imgocc']['version'] = default_conf_syncd['version']
        mw.col.setMod()

    return mw.col.conf['imgocc']


def getLocalConfig():
    # Local preferences
    if 'imgocc' not in mw.pm.profile:
        mw.pm.profile["imgocc"] = default_conf_local
    elif mw.pm.profile['imgocc'].get('version', 0) < default_conf_syncd['version']:
        for key in list(default_conf_local.keys()):
            if key not in mw.col.conf['imgocc']:
                mw.pm.profile["imgocc"][key] = default_conf_local[key]
        mw.pm.profile['imgocc']['version'] = default_conf_local['version']

    return mw.pm.profile["imgocc"]


def getOrCreateModel():
    model = mw.col.models.byName(IO_MODEL_NAME)
    if not model:
        # create model and set up default field name config
        model = template.add_io_model(mw.col)
        mw.col.conf['imgocc']['flds'] = default_conf_syncd['flds']
        return model
    model_version = mw.col.conf['imgocc']['version']
    if model_version < default_conf_syncd['version']:
        return template.update_template(mw.col, model_version)
    return model


def getModelConfig():
    model = getOrCreateModel()
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

    return model, mflds, ioflds, ioflds_priv, ioflds_prsv


def loadConfig(self):
    """load and/or create add-on preferences"""
    # FIXME: return config dictionary instead of this hacky
    # instantiation of instance variables
    self.sconf_dflt = default_conf_syncd
    self.lconf_dflt = default_conf_local
    self.sconf = getSyncedConfig()
    self.lconf = getLocalConfig()

    (self.model, self.mflds, self.ioflds,
     self.ioflds_priv, self.ioflds_prsv) = getModelConfig()
