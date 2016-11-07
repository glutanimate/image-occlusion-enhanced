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
Common reusable utilities
"""

import os

from aqt import mw

import re
import urlparse, urllib
import base64

from xml.dom import minidom
from Imaging.PIL import Image

def path2url(path):
    """URL-encode local path"""
    return urlparse.urljoin(
      'file:', urllib.pathname2url(path.encode('utf-8')))

def img2path(img, nameonly=False):
    """Extract path or file name out of HTML img element"""
    imgpatt = r"""<img.*?src=(["'])(.*?)\1"""
    imgregex = re.compile(imgpatt, flags=re.I|re.M|re.S)
    fname = imgregex.search(img)
    if not fname:
        return None
    if nameonly:
        return fname.group(2)
    fpath = os.path.join(mw.col.media.dir(),fname.group(2))
    if not os.path.isfile(fpath):
        return None
    else:
        return fpath

def imageProp(image_path):
    """Get image width and height"""
    image = Image.open(image_path)
    width, height = image.size
    return width, height

def svgToBase64(svg_path):
    """Convert SVG string to base64"""
    doc = minidom.parse(svg_path)
    svg_node = doc.documentElement
    svg_content = svg_node.toxml()
    svg_b64 = "data:image/svg+xml;base64," + base64.b64encode(svg_content)
    return svg_b64

def fname2img(path):
    """Return HTML img element for given path"""
    return '<img src="%s" />' % os.path.split(path)[1]