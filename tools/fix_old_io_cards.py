# -*- coding: utf-8 -*-

"""
Anki Add-on: Fix Old Image Occlusion Notes

Notes created with older versions of the image occlusion add-on
contain malformatted SVG files that are no longer supported
by platforms such as iOS and Android. This add-on fixes the
corresponding SVG files.

Largely copied over from image-occlusion-svg-fix by Matt Restko
(https://github.com/mrestko/image-occlusion-svg-fix)

Copyright:  (c) Matt Restko 2015-2016
            (c) Glutanimate 2017
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

import os
import re
from fixiocards import ElementTree as etree

from aqt import mw
from aqt.utils import tooltip, askUser

def get_image_occlusion_files(media_dir):
    files = os.listdir(media_dir)
    img_occ_patt = re.compile(r"_(Q|A)(_|\s)\d*\.svg$")
    target_files = [f for f in files if img_occ_patt.search(f) is not None]
    return target_files

def fix_elem(elem):
    style = elem.get("style")
    styles = style.split(";")
    style_dict = dict(s.split(":") for s in styles)
    fill_color = "#" + style_dict["fill"]
    elem.attrib["fill"] = fill_color
    del elem.attrib["style"]

def fix_file(filename):
    doc = etree.parse(filename)
    root = doc.getroot()
    bad_elems = [elem for elem in root.getiterator()
                    if "style" in elem.attrib]
    if len(bad_elems) == 0:
        return False
    else:
        print("Fixing {}".format(filename))
        map(fix_elem, bad_elems)
        with open(filename, "w") as fp:
            fp.write(etree.tostring(root))
        return True

def fix_files(files):
    return sum(fix_file(fname) for fname in files)

question = """
This will scan your entire media collection for malformatted image \
occlusion masks and fix them. It is recommended that you create a \
<b>backup of your entire collection</b>, media included, before proceeding. \
<br><br>
<b>Are you sure you want to proceed?</b><br>
<i>(This might take a while depending on the number of files)</i>
"""

def on_fix_button():
    if not askUser(question, defaultno=True):
        return
    media_dir = mw.col.media.dir()
    files = get_image_occlusion_files(media_dir)
    fixed = fix_files(files)
    tooltip("Done. {}/{} files needed fixing".format(fixed, len(files)))

menu = mw.form.menuTools
menu.addSeparator()
a = menu.addAction('Fix Old Image Occlusions')
a.triggered.connect(on_fix_button)