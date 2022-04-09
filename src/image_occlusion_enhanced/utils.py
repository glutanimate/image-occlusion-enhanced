# -*- coding: utf-8 -*-

# Image Occlusion Enhanced Add-on for Anki
#
# Copyright (C) 2016-2020  Aristotelis P. <https://glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.
"""
Common reusable utilities
"""

import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional, Tuple
from xml.dom import minidom

from aqt import mw

from ._vendor import imghdr
from ._vendor.imagesize import imagesize
from .consts import SUPPORTED_BITMAP_FORMATS


def path_to_url(path: str) -> str:
    """URL-encode local path"""
    return urllib.parse.urljoin("file:", urllib.request.pathname2url(path))


def path_to_img_element(path: str) -> str:
    """Return HTML img element for given path"""
    fname = os.path.split(path)[1]
    return '<img src="%s" />' % fname


def img_element_to_path(img_element: str, nameonly: bool = False) -> Optional[str]:
    """Extract path or file name out of HTML img element"""
    imgpatt = r"""<img.*?src=(["'])(.*?)\1"""
    imgregex = re.compile(imgpatt, flags=re.I | re.M | re.S)
    fname = imgregex.search(img_element)
    if not fname:
        return None
    if nameonly:
        return fname.group(2)
    fpath = os.path.join(mw.col.media.dir(), fname.group(2))
    if not os.path.isfile(fpath):
        return None
    return fpath


def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """Get image width and height"""
    # Vector graphics
    if image_path.endswith(".svg"):
        try:
            with open(image_path, "r") as svg_file:
                doc = svg_file.read()
                mask_doc = minidom.parseString(doc.encode("utf-8"))
        except Exception as e:
            print(str(e))
            raise ValueError("Invalid SVG file.")

        svg_node = mask_doc.documentElement
        cheight = svg_node.attributes["height"].value
        cwidth = svg_node.attributes["width"].value
        height = _svg_convert_size_to_pixels(cheight)
        width = _svg_convert_size_to_pixels(cwidth)

        return width, height

    # Bitmap graphics
    img_fmt = imghdr.what(image_path)
    if img_fmt not in SUPPORTED_BITMAP_FORMATS:
        raise ValueError("Unrecognized raster image format.")

    width, height = imagesize.get(image_path)
    if width < 0 or height < 0:
        raise ValueError("Image has invalid dimensions.")

    return width, height


def _svg_convert_size_to_pixels(size: str) -> int:
    """
    Convert SVG size in pt, pc, mm, cm, or in into pixels
    """

    # https://www.w3.org/TR/SVG/coords.html#Units
    conversion_table = {"pt": 1.25, "pc": 15, "mm": 3.543307, "cm": 35.43307, "in": 90}
    if len(size) > 3:
        if size[-2:] in conversion_table:
            return round(float(size[:-2]) * conversion_table[size[-2:]])

    return round(float(size))
