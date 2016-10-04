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
    'uuid': "ID (hidden)",
    'header': "Header",
    'image': "Image",
    'footer': "Footer",
    'remarks': "Anmerkungen",
    'sources': "Quellen",
    'extra1': "Extra 1",
    'extra2': "Extra 2",
    'qmask': "Question Mask",
    'amask': "Answer Mask",
    'fmask': "Full Mask"
}
IO_FLDORDER = ["uuid", "header", "image", "footer", "remarks", "sources",
                "extra1", "extra2", "qmask", "amask", "fmask"]


IO_DEFAULT_CONF =   {'initFill[color]': '00AA7F',
                    'mask_fill_color': 'FF0000',
                    'io-version': 'enhanced-0.5'}

# get default file system encoding
IO_ENCODING = sys.getfilesystemencoding()
IO_HOME = os.path.expanduser('~').decode(IO_ENCODING)

IO_DEFAULT_PREFS = {"prev_image_dir": IO_HOME}

addons_folder = mw.pm.addonFolder().encode('utf-8')
prefs_path = os.path.join(addons_folder, "image_occlusion_enhanced", 
                          ".image_occlusion_prefs").decode('utf-8')

def load_prefs(self):

    # check if synced configuration exists
    if not 'image_occlusion_conf' in mw.col.conf:
        self.mw.col.conf['image_occlusion_conf'] = IO_DEFAULT_CONF

    # upgrade from Image Occlusion 2.0
    self.io_conf = mw.col.conf['image_occlusion_conf']
    if not 'io-version' in self.io_conf:
        # set io version
        self.io_conf['io-version'] = IO_DEFAULT_CONF['io-version']
        # change default colours
        if self.io_conf['initFill[color]'] == "FFFFFF":
            self.io_conf['initFill[color]'] = IO_DEFAULT_CONF['initFill[color]']
            self.io_conf['mask_fill_color'] = IO_DEFAULT_CONF['mask_fill_color']

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