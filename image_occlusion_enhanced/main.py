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

from anki.lang import _
from aqt.qt import *

from aqt import mw
from aqt.editor import Editor, EditorWebView
from aqt.addcards import AddCards
from aqt.editcurrent import EditCurrent
from aqt.reviewer import Reviewer
from aqt.utils import tooltip
from anki.hooks import wrap, addHook, runHook

from .config import *
from .resources import *
from .add import ImgOccAdd
from .options import ImgOccOpts
from .dialogs import ioHelp, ioError

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


def onImgOccButton(self, origin=None, image_path=None):
    """Launch Image Occlusion Enhanced"""
    origin = origin or getEdParentInstance(self.parentWindow)
    io_model = mw.col.models.byName(IO_MODEL_NAME)
    if io_model:
        io_model_fields = mw.col.models.fieldNames(io_model)
        if "imgocc" in mw.col.conf:
            dflt_fields = list(mw.col.conf['imgocc']['flds'].values())
        else:
            dflt_fields = list(IO_FLDS.values())
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
    mw.ImgOccAdd = ImgOccAdd(self, origin, oldimg)
    mw.ImgOccAdd.occlude(image_path)


def onSetupEditorButtons(self):
    """Add IO button to Editor"""
    conf = mw.pm.profile.get("imgocc")
    if not conf:
        hotkey = IO_HOTKEY
    else:
        hotkey = conf.get("hotkey", IO_HOTKEY)

    origin = getEdParentInstance(self.parentWindow)

    if origin == "addcards":
        tt = "Add Image Occlusion"
        icon = "new_occlusion"
    else:
        tt = "Edit Image Occlusion"
        icon = "new_occlusion"
    
    btn = self._addButton(icon, lambda o=self: onImgOccButton(self, origin),
            _(hotkey), _("{} ({})".format(tt, hotkey)), canDisable=False)


def getEdParentInstance(parent):
    """Determine parent instance of editor widget"""
    if isinstance(parent, AddCards):
        return "addcards"
    elif isinstance(parent, EditCurrent):
        return "editcurrent"
    else:
        return "browser"


def openImage(path):
    """Open path with default system app"""
    import subprocess
    try:
        if sys.platform=='win32':
            os.startfile(path)
        elif sys.platform=='darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
    except OSError:
        QDesktopServices.openUrl(QUrl("file://" + path))


def contextMenuEvent(self, evt):
    """Add custom context menu for images"""
    m = QMenu(self)
    a = m.addAction(_("Cut"))
    a.triggered.connect(self.onCut)
    a = m.addAction(_("Copy"))
    a.triggered.connect(self.onCopy)
    a = m.addAction(_("Paste"))
    a.triggered.connect(self.onPaste)
    ##################################################
    hit = self.page().currentFrame().hitTestContent(evt.pos())
    url = hit.imageUrl()
    if url.isValid():
        image_url = url.toLocalFile()
        a = m.addAction(_("Occlude Image"))
        a.triggered.connect(
            lambda _, u=image_url, s=self.editor: onImgOccButton(
                s, image_path=u))
        a = m.addAction(_("Open Image"))
        a.triggered.connect(lambda _, u=image_url: openImage(u))
    ##################################################
    runHook("EditorWebView.contextMenuEvent", self, m)
    m.popup(QCursor.pos())


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
    if not self.card or not self.card.model()["name"] == IO_MODEL_NAME:
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
EditorWebView.contextMenuEvent = contextMenuEvent
Editor.setNote = wrap(Editor.setNote, onSetNote, "after")
Editor.onImgOccButton = onImgOccButton
Reviewer._keyHandler = wrap(Reviewer._keyHandler, newKeyHandler, "before")
Reviewer._showAnswer = wrap(Reviewer._showAnswer, onShowAnswer, "around")