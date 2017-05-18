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
Sets up buttons and menus and calls other modules.
"""

import logging, sys

from aqt.qt import *

from aqt import mw
from aqt.editor import Editor
from aqt.addcards import AddCards
from aqt.editcurrent import EditCurrent
from aqt.reviewer import Reviewer
from aqt.utils import tooltip
from anki.hooks import wrap, addHook

from config import *
from resources import *
from add import ImgOccAdd
from options import ImgOccOpts
from dialogs import ioHelp, ioError

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)


def onIoSettings(mw):
    """Call settings dialog if Editor not active"""
    if hasattr(mw, "ImgOccEdit") and mw.ImgOccEdit.visible:
        tooltip("Please close Image Occlusion Editor\
            to access the Options.")
        return
    dialog = ImgOccOpts(mw)
    dialog.exec_()


def onIoHelp():
    """Call main help dialog"""
    ioHelp("main")


def onImgOccButton(ed, mode):
    """Launch Image Occlusion Enhanced"""
    io_model = mw.col.models.byName(IO_MODEL_NAME)
    if io_model:
        io_model_fields = mw.col.models.fieldNames(io_model)
        if "imgocc" in mw.col.conf:
            dflt_fields = mw.col.conf['imgocc']['flds'].values()
        else:
            dflt_fields = IO_FLDS.values()
        # note type integrity check
        if not all(x in io_model_fields for x in dflt_fields):
            ioError("<b>Error</b>: Image Occlusion note type " \
                "not configured properly.Please make sure you did not " \
                "manually delete or rename any of the default fields.",
                help="notetype")
            return False
    try: # allows us to fall back to old image if necessary
        oldimg = mw.ImgOccAdd.image_path
    except AttributeError:
        oldimg = None
    mw.ImgOccAdd = ImgOccAdd(ed, oldimg)
    mw.ImgOccAdd.occlude(mode)


def onSetupEditorButtons(self):
    """Add IO button to Editor"""
    if isinstance(self.parentWindow, AddCards):
        btn = self._addButton("new_occlusion",
                lambda o=self: onImgOccButton(self, "add"),
                _("Alt+a"), _("Add Image Occlusion (Alt+A/Alt+O)"),
                canDisable=False)
    elif isinstance(self.parentWindow, EditCurrent):
        btn = self._addButton("edit_occlusion",
                lambda o=self: onImgOccButton(self, "editcurrent"),
                _("Alt+a"), _("Edit Image Occlusion (Alt+A/Alt+O)"),
                canDisable=False)
    else:
        btn = self._addButton("edit_occlusion",
                lambda o=self: onImgOccButton(self, "browser"),
                _("Alt+a"), _("Edit Image Occlusion (Alt+A/Alt+O)"),
                canDisable=False)

    # secondary hotkey:
    press_action = QAction(self.parentWindow, triggered=btn.animateClick)
    press_action.setShortcut(QKeySequence(_("Alt+o")))
    btn.addAction(press_action)


def onSetNote(self, note, hide=True, focus=False):
    """Customize the editor when IO notes are active"""
    if not (self.note and self.note.model()["name"] == IO_MODEL_NAME):
        return
    # simple hack to hide the ID field if it's the first one
    if self.note.model()['flds'][0]['name'] == IO_FLDS['id']:
        self.web.eval("""
            // hide first fname, field, and snowflake (FrozenFields add-on)
                document.styleSheets[0].addRule(
                    'tr:first-child .fname, #f0, #i0', 'display: none;');
            """)
    # Limit image display height
    self.web.eval("""
            document.styleSheets[0].addRule(
                'img', 'max-width: 90%; max-height: 160px');
        """)


def newKeyHandler(self, evt):
    """Bind mask reveal to a hotkey"""
    if (self.state == "answer" and evt.key() == Qt.Key_G):
        self.web.eval('document.getElementById("io-revl-btn").click();')


def onShowAnswer(self, _old):
    """Retain scroll position across answering the card"""
    if not self.card.model()["name"] == IO_MODEL_NAME:
        return _old(self)
    scroll_pos = self.web.page().mainFrame().scrollPosition()
    ret = _old(self)
    self.web.page().mainFrame().setScrollPosition(scroll_pos)
    return ret


# Set up menus
options_action = QAction("Image &Occlusion Enhanced Options...", mw)
help_action = QAction("Image &Occlusion Enhanced...", mw)
mw.connect(options_action, SIGNAL("triggered()"),
            lambda o=mw: onIoSettings(o))
mw.connect(help_action, SIGNAL("triggered()"),
            onIoHelp)
mw.form.menuTools.addAction(options_action)
mw.form.menuHelp.addAction(help_action)

# Set up hooks
addHook('setupEditorButtons', onSetupEditorButtons)
Editor.setNote = wrap(Editor.setNote, onSetNote, "after")
Reviewer._keyHandler = wrap(Reviewer._keyHandler, newKeyHandler, "before")
Reviewer._showAnswer = wrap(Reviewer._showAnswer, onShowAnswer, "around")