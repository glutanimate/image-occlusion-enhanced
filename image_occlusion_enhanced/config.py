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
from anki.utils import json

global IO_FLDS, IO_FLDS_IDS, IO_FLDS_PRIV, IO_FLDS_PRSV
global IO_MODEL_NAME, IO_CARD_NAME, IO_DEFAULT_CONF, IO_HOME

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

IO_DEFAULT_CONF = {'ofill': '00AA7F',
                  'qfill': 'FF0000',
                  'version': 0.5}

# variables for local preference handling
sys_encoding = sys.getfilesystemencoding()
IO_HOME = os.path.expanduser('~').decode(sys_encoding)
default_prefs = {"prev_image_dir": IO_HOME}
addons_folder = mw.pm.addonFolder().encode('utf-8')
prefs_path = os.path.join(addons_folder, "image_occlusion_enhanced", 
                          ".image_occlusion_prefs").decode('utf-8')

def loadPrefs(self):

    if not 'imgocc' in mw.col.conf:
        # create initial configuration
        mw.col.conf['imgocc'] = IO_DEFAULT_CONF
        
        if 'image_occlusion_conf' in mw.col.conf:
            # upgrade from earlier IO versions
            old_conf = mw.col.conf['image_occlusion_conf']
            mw.col.conf['imgocc']['ofill'] = old_conf['initFill[color]']
            mw.col.conf['imgocc']['qfill'] = old_conf['mask_fill_color']
            # insert other upgrade actions here

    self.io_conf = mw.col.conf['imgocc']

    if self.io_conf['version'] < IO_DEFAULT_CONF['version']:
        print "updating from earlier IO release"
        # insert other update actions here
        self.io_conf['version'] = IO_DEFAULT_CONF['version']

    model = mw.col.models.byName(IO_MODEL_NAME)
    self.mflds = model['flds']

    # load local preferences
    self.prefs = None
    try:
        with open(prefs_path, "r") as f:
            self.prefs = json.load(f)
    except:
        # file does not exist or is corrupted: fall back to default
        with open(prefs_path, "w") as f:
            self.prefs = default_prefs
            json.dump(self.prefs, f)

def savePrefs(self):
    # save local preferences to disk
    with open(prefs_path, "w") as f:
        json.dump(self.prefs, f)