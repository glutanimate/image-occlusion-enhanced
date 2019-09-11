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
Common reusable utilities
"""

import os
import re

from aqt import mw

from xml.dom import minidom
import urllib.parse
import urllib.request
import urllib.parse
import urllib.error

from ._vendor import imghdr
from ._vendor.imagesize import imagesize

from .consts import *



def path2url(path):
    """URL-encode local path"""
    if ANKI21:
        return urllib.parse.urljoin(
            'file:', urllib.request.pathname2url(path))
    else:
        return urllib.parse.urljoin(
            'file:', urllib.request.pathname2url(path.encode('utf-8')))


def fname2img(path):
    """Return HTML img element for given path"""
    fname = os.path.split(path)[1]
    return '<img src="%s" />' % fname


def img2path(img, nameonly=False):
    """Extract path or file name out of HTML img element"""
    imgpatt = r"""<img.*?src=(["'])(.*?)\1"""
    imgregex = re.compile(imgpatt, flags=re.I | re.M | re.S)
    fname = imgregex.search(img)
    if not fname:
        return None
    if nameonly:
        return fname.group(2)
    fpath = os.path.join(mw.col.media.dir(), fname.group(2))
    if not os.path.isfile(fpath):
        return None
    return fpath


def imageProp(image_path):
    """Get image width and height"""
    # Vector graphics
    if image_path.endswith(".svg"):
        try:
            with open(image_path, 'r') as svg_file:
                doc = svg_file.read()
                mask_doc = minidom.parseString(doc.encode('utf-8'))
        except Exception as e:
            print(str(e))
            raise ValueError("Invalid SVG file.")
        
        svg_node = mask_doc.documentElement
        cheight = svg_node.attributes["height"].value
        cwidth = svg_node.attributes["width"].value
        height = _svg_convert_size(cheight)
        width = _svg_convert_size(cwidth)
        
        return width, height
    
    # Bitmap graphics
    img_fmt = imghdr.what(image_path)
    if img_fmt not in SUPPORTED_BITMAP_FORMATS:
        raise ValueError("Unrecognized raster image format.")
    
    width, height = imagesize.get(image_path)
    if width < 0 or height < 0:
        raise ValueError("Image has invalid dimensions.")

    return width, height


def _svg_convert_size(size):
    """
    Convert svg size to the px version
    :param size: String with the size
    """

    # https://www.w3.org/TR/SVG/coords.html#Units
    conversion_table = {
        "pt": 1.25,
        "pc": 15,
        "mm": 3.543307,
        "cm": 35.43307,
        "in": 90
    }
    if len(size) > 3:
        if size[-2:] in conversion_table:
            return round(float(size[:-2]) * conversion_table[size[-2:]])

    return round(float(size))
