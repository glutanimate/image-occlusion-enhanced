# -*- coding: utf-8 -*-

"""
This file is part of the Image Occlusion Enhanced add-on for Anki.

Global variables

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import sys
import os
from anki import version

ANKI21 = version.startswith("2.1.")
SYS_ENCODING = sys.getfilesystemencoding()

if ANKI21:
    ADDON_PATH = os.path.dirname(__file__)
else:
    ADDON_PATH = os.path.dirname(__file__).decode(SYS_ENCODING)

ICONS_PATH = os.path.join(ADDON_PATH, "icons")

SUPPORTED_BITMAP_FORMATS = ("jpeg", "png", "gif")
SUPPORTED_VECTOR_FORMATS = ("svg", )
SUPPORTED_EXTENSIONS = (
    ("jpg", ) +
    SUPPORTED_BITMAP_FORMATS +
    SUPPORTED_VECTOR_FORMATS
)
