# -*- coding: utf-8 -*-
####################################################
##                                                ##
##           Image Occlusion Enhanced             ##
##                                                ##
##      Copyright (c) Glutanimate 2016-2017       ##
##       (https://github.com/Glutanimate)         ##
##                                                ##
##         Based on Image Occlusion 2.0           ##
##         Copyright (c) 2012-2015 tmbb           ##
##           (https://github.com/tmbb)            ##
##                                                ##
####################################################

"""
Handles all minor utility dialogs
"""

import logging, sys

from aqt.qt import *
from anki.errors import AnkiError

from aqt import mw, webview, deckchooser, tagedit
from aqt.utils import saveGeom, restoreGeom

from .config import *


def ioError(text, title="Image Occlusion Enhanced Error",
                                    parent=None, help=None):
    msgfunc = QMessageBox.critical
    btns = None
    if help:
        btns = QMessageBox.Help | QMessageBox.Ok
    while 1:
        r = ioInfo(text, title, parent, buttons=btns, msgfunc=msgfunc)
        if r == QMessageBox.Help:
            ioHelp(help, parent=parent)
        else:
            break
    return r

def ioAskUser(text, title="Image Occlusion Enhanced", parent=None,
                            help="", defaultno=False, msgfunc=None):
    """Show a yes/no question. Return true if yes.
    based on askUser by Damien Elmes"""

    msgfunc = QMessageBox.question
    btns = QMessageBox.Yes | QMessageBox.No
    if help:
        btns |= QMessageBox.Help
    while 1:
        if defaultno:
            default = QMessageBox.No
        else:
            default = QMessageBox.Yes
        r = ioInfo(text, title, parent, btns, default, msgfunc)
        if r == QMessageBox.Help:
            ioHelp(help)
        else:
            break
    return r == QMessageBox.Yes

def ioInfo(text, title="Image Occlusion Enhanced", parent=None,
                        buttons=None, default=None, msgfunc=None):
    if not parent:
        parent = mw.app.activeWindow()
    if not buttons:
        buttons = QMessageBox.Ok
    if not default:
        default = QMessageBox.Ok
    if not msgfunc:
        msgfunc = QMessageBox.information
    return msgfunc(parent, title, text, buttons, default)


io_link_wiki = "https://github.com/Glutanimate/image-occlusion-enhanced/wiki"
io_link_tut = "https://www.youtube.com/playlist?list=PL3MozITKTz5YFHDGB19ypxcYfJ1ITk_6o"
io_link_thread = ("https://anki.tenderapp.com/discussions/add-ons/"
                  "8295-image-occlusion-enhanced-official-thread")
help_text = {}
help_text["add"] = """
    <p><strong>Basic Instructions</strong></p>
    <ol>
    <li>With the rectangle tool or any other shape tool selected, cover the areas of the image you want to be tested on</li>
    <li>(Optional): Fill out additional information about your cards by switching to the <em>Fields</em> tab</li>
    <li>Click on one of the <em>Add Cards</em> buttons at the bottom of the window to add the cards to your collection</li>
    </ol>
    <p><strong>Drawing Custom Labels</strong></p>
    <ol>
    <li>Draw up the layers sidepanel by clicking on the <em>Layers</em> button at the right edge of the editor</li>
    <li>Switch to the <em>Labels</em> layer by left-clicking on it. You can also switch to the labels layer directly by using <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>L</kbd>.</li>
    <li>Anything you draw in this layer – be it text, lines, or shapes – will appear above the image, but still below your masks. All of the painting tools in the left sidebar are at your disposal.</li>
    <li>Switch back to the masks layer, either via the <em>Layers</em> sidepanel, or by using the <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>M</kbd> hotkey.</li>
    </ol>
    <p><strong>Grouping Shapes</strong></p>
    <ol>
    <li>Select multiple shapes, either by drawing a selection rectangle with the selection tool active (<kbd>S</kbd>), or by shift-clicking on multiple shapes</li>
    <li>Either use the <kbd>G</kbd> hotkey or the <em>Group Elements</em> tool in the top-bar to group your items</li>
    </ol>
    <p>Grouped shapes will form a single card.</p>
    <p><strong>More Information</strong></p>
    <p>For more information please refer to the following resources:</p>
    <ul>
    <li><a href="{}">Image Occlusion Enhanced Wiki</a></li>
    <li><a href="{}">YouTube Tutorials</a></li>
    <li><a href="{}">Official support thread</a></li>
    </ul>
    """.format(io_link_wiki, io_link_tut, io_link_thread)
help_text["edit"] = """<b>Instructions for editing</b>: \
    <br><br> Each mask shape represents a card.\
    Removing any of the existing shapes will remove the corresponding card.\
    New shapes will generate new cards. You can change the occlusion type\
    by using the dropdown box on the left.<br><br>If you click on the \
    <i>Add new cards</i> button a completely new batch of cards will be \
    generated, leaving your originals untouched.<br><br> \
    <b>Actions performed in Image Occlusion's <i>Editing Mode</i> cannot be\
    easily undone, so please make sure to check your changes twice before\
    applying them.</b><br><br>The only exception to this are purely textual\
    changes to fields like the header or footer of your notes. These can\
    be fully reverted by using Ctrl+Z in the Browser or Reviewer view.<br><br>\
    More information: <a href="%s">Wiki: Editing Notes</a>.\
    """ % (io_link_wiki + "/Basic-Use#editing-cards")
help_text["notetype"] = """<b>Fixing a broken note type:</b>\
    <br><br> The Image Occlusion Enhanced note type can't be edited \
    arbitrarily. If you delete a field that's required by the add-on \
    or rename it outside of the IO Options dialog you will be presented \
    with an error message. <br><br>
    To fix this issue please follow the instructions in <a href="%s">the \
    wiki</a>.""" % (io_link_wiki + "/Troubleshooting#note-type")
help_text["main"] = """<h2>Help and Support</h2>
    <p><a href="%s">Image Occlusion Enhanced Wiki</a></p>
    <p><a href="%s">Official Video Tutorial Series</a></p>
    <p><a href="%s">Support Thread</a></p>
    <h2>Credits and License</h2>
    <p style="font-size:12pt;"><em>Copyright © 2012-2015 \
    <a href="https://github.com/tmbb">Tiago Barroso</a></em></p>
    <p style="font-size:12pt;"><em>Copyright © 2013 \
    <a href="https://github.com/steveaw">Steve AW</a></em></p>
    <p style="font-size:12pt;"><em>Copyright © 2016-2017 \
    <a href="https://github.com/Glutanimate">Aristotelis P.</a></em></p>
    <p><em>Image Occlusion Enhanced</em> is licensed under the GNU AGPLv3.</p>
    <p>Third-party open-source software shipped with <em>Image Occlusion Enhanced</em>:</p>
    <ul><li><p><a href="https://github.com/SVG-Edit/svgedit">SVG Edit</a> 2.6. \
    Copyright (c) 2009-2012 SVG-edit authors. Licensed under the MIT license</a></p></li>
    <li><p><a href="http://www.pythonware.com/products/pil/">Python Imaging Library</a> \
    (PIL) 1.1.7. Copyright (c) 1997-2011 by Secret Labs AB, Copyright (c) 1995-2011 by Fredrik \
    Lundh. Licensed under the <a href="http://www.pythonware.com/products/pil/license.htm">\
    PIL license</a></p></li>
    <li><p><a href="https://github.com/shibukawa/imagesize_py">imagesize.py</a> v0.7.1. \
    Copyright (c) 2016 Yoshiki Shibukawa. Licensed under the MIT license.</p></li>
    </ul>
    """ % (io_link_wiki, io_link_tut, io_link_thread)

def ioHelp(help, title=None, text=None, parent=None):
    """Display an info message or a predefined help section"""
    if help != "custom":
        text = help_text[help]
    if not title:
        title = "Image Occlusion Enhanced Help"
    if not parent:
        parent = mw.app.activeWindow()
    mbox = QMessageBox(parent)
    mbox.setAttribute(Qt.WA_DeleteOnClose)
    mbox.setStandardButtons(QMessageBox.Ok)
    mbox.setWindowTitle(title)
    mbox.setText(text)
    mbox.setWindowModality(Qt.NonModal)
    mbox.show()