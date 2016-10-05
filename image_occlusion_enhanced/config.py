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


global IO_MODEL_NAME, IO_CARD_NAME, IO_FLDS, IO_FLDORDER, IO_DEFAULT_CONF, IO_DEFAULT_PREFS

IO_MODEL_NAME = "Image Occlusion Enhanced"
IO_CARD_NAME = "IO Card"
IO_FLDS = {
    'uuid': u"ID (hidden)",
    'header': u"Header",
    'image': u"Image",
    'footer': u"Footer",
    'remarks': u"Anmerkungen",
    'sources': u"Quellen",
    'extra1': u"Extra 1",
    'extra2': u"Extra 2",
    'qmask': u"Question Mask",
    'amask': u"Answer Mask",
    'omask': u"Original Mask"
}
IO_FLDORDER = ["uuid", "header", "image", "footer", "remarks", "sources",
                "extra1", "extra2", "qmask", "amask", "omask"]


IO_DEFAULT_CONF =   {'ofill': '00AA7F',
                    'qfill': 'FF0000',
                    'version': 0.5}

# get default file system encoding
IO_ENCODING = sys.getfilesystemencoding()
IO_HOME = os.path.expanduser('~').decode(IO_ENCODING)

IO_DEFAULT_PREFS = {"prev_image_dir": IO_HOME}

addons_folder = mw.pm.addonFolder().encode('utf-8')
prefs_path = os.path.join(addons_folder, "image_occlusion_enhanced", 
                          ".image_occlusion_prefs").decode('utf-8')

def load_prefs(self):

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

def save_prefs(self):
    # save local preferences to disk
    with open(prefs_path, "w") as f:
        json.dump(self.prefs, f)