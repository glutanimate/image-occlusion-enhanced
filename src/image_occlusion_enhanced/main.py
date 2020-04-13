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

import logging
import sys

from anki.lang import _
from aqt.qt import *

from aqt import mw
from aqt.editor import Editor, EditorWebView
from aqt.addcards import AddCards
from aqt.editcurrent import EditCurrent
from aqt.reviewer import Reviewer
from aqt.utils import tooltip
from anki.hooks import wrap, addHook, runHook

from .consts import *
from .config import *
from .add import ImgOccAdd
from .options import ImgOccOpts
from .dialogs import ioHelp, ioCritical

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)


def onIoSettings():
    """Call settings dialog if Editor not active"""
    # TODO: fix ImgOccEdit detection
    if hasattr(mw, "ImgOccEdit") and mw.ImgOccEdit.visible:
        tooltip("Please close Image Occlusion Editor\
            to access the Options.")
        return
    dialog = ImgOccOpts()
    dialog.exec_()


def onIoHelp():
    """Call main help dialog"""
    ioHelp("main", parent=mw)


def onImgOccButton(self, origin=None, image_path=None):
    """Launch Image Occlusion Enhanced"""
    origin = origin or getEdParentInstance(self.parentWindow)
    io_model = getOrCreateModel()
    if io_model:
        io_model_fields = mw.col.models.fieldNames(io_model)
        if "imgocc" in mw.col.conf:
            dflt_fields = list(mw.col.conf['imgocc']['flds'].values())
        else:
            dflt_fields = list(IO_FLDS.values())
        # note type integrity check
        if not all(x in io_model_fields for x in dflt_fields):
            ioCritical("model_error", help="notetype",
                       parent=self.parentWindow)
            return False
    try:  # allows us to fall back to old image if necessary
        oldimg = self.imgoccadd.image_path
    except AttributeError:
        oldimg = None
    self.imgoccadd = ImgOccAdd(self, origin, oldimg)
    self.imgoccadd.occlude(image_path)


def onSetupEditorButtons(buttons, editor):
    """Add IO button to Editor"""
    conf = mw.pm.profile.get("imgocc")
    if not conf:
        hotkey = IO_HOTKEY
    else:
        hotkey = conf.get("hotkey", IO_HOTKEY)

    origin = getEdParentInstance(editor.parentWindow)

    if origin == "addcards":
        tt = "Add Image Occlusion"
        icon_name = "add.png"
    else:
        tt = "Edit Image Occlusion"
        icon_name = "edit.png"

    icon = os.path.join(ICONS_PATH, icon_name)

    b = editor.addButton(icon, "I/O",
                         lambda o=editor: onImgOccButton(o),
                         tip=_("{} ({})".format(tt, hotkey)),
                         keys=hotkey, disables=False)

    buttons.append(b)
    return buttons


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
        if sys.platform == 'win32':
            subprocess.Popen(['explorer', path])
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
    except OSError as e:
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
    if not ANKI21:
        hit = self.page().currentFrame().hitTestContent(evt.pos())
        url = hit.imageUrl()
        path = url.toLocalFile()
    else:
        # cf. https://doc.qt.io/qt-5/qwebenginepage.html#contextMenuData
        context_data = self.page().contextMenuData()
        url = context_data.mediaUrl()
        image_name = url.fileName()
        path = os.path.join(mw.col.media.dir(), image_name)
    if url.isValid() and path:
        a = m.addAction(_("Occlude Image"))
        a.triggered.connect(
            lambda _, u=path, e=self.editor: onImgOccButton(e, image_path=u))
        a = m.addAction(_("Open Image"))
        a.triggered.connect(lambda _, u=path: openImage(u))
    ##################################################
    runHook("EditorWebView.contextMenuEvent", self, m)
    m.popup(QCursor.pos())


io_editor_style = """
<style>
/* I/O: limit image display height */
.ionote img {
    max-width: 90%;
    max-height: 160px;
}
/* I/O: hide first fname, field, and snowflake (FrozenFields add-on) */
.ionote.ionote-id tr:first-child .fname, .ionote.ionote-id #f0, .ionote.ionote-id #i0 {
    display: none;
}
</style>
"""


def onSetNote(self, note, hide=True, focus=False):
    """Customize the editor when IO notes are active"""
    if self.web is None:  # editor is in cleanup
        return
    # Conditionally set body CSS  class
    if not (self.note and self.note.model()["name"] == IO_MODEL_NAME):
        self.web.eval("""$("body").removeClass("ionote");""")
    else:
        # Only hide first field if it's the ID field
        # TODO? identify ID field HTML element automatically
        if self.note.model()['flds'][0]['name'] == IO_FLDS['id']:
            self.web.eval("""$("body").addClass("ionote-id");""")
        else:
            self.web.eval("""$("body").removeClass("ionote-id");""")
        self.web.eval("""$("body").addClass("ionote");""")


def onProfileLoaded():
    """Add our custom user styles to the editor DOM
    Need to do this on profile load time to avoid interferences with
    other add-ons that might potentially overwrite editor HTML"""
    from aqt import editor
    editor._html = editor._html + io_editor_style.replace("%", "%%")
    # Setup add-on config and templates, update if necessary
    getSyncedConfig()
    getLocalConfig()
    getOrCreateModel()


# Mask toggle hotkey

def onHintHotkey():
    mw.web.eval("""
        var ioBtn = document.getElementById("io-revl-btn");
        if (ioBtn) {ioBtn.click();}
    """)


def onReviewerStateShortcuts(shortcuts):
    """Add hint hotkey on Anki 2.1.x"""
    shortcuts.append(("G", onHintHotkey))


def newKeyHandler(self, evt):
    """Add hint hotkey on Anki 2.0.x"""
    if (self.state == "answer" and evt.key() == Qt.Key_G):
        onHintHotkey()


# Retain scroll position when answering

def onShowAnswer(self, _old):
    """Retain scroll position across answering the card"""
    if not self.card or not self.card.model()["name"] == IO_MODEL_NAME:
        return _old(self)
    if not ANKI21:
        scroll_pos = self.web.page().mainFrame().scrollPosition()
        ret = _old(self)
        self.web.page().mainFrame().setScrollPosition(scroll_pos)
    else:
        scroll_pos = self.web.page().scrollPosition()
        ret = _old(self)
        self.web.eval("window.scrollTo({}, {});".format(
            scroll_pos.x(), scroll_pos.y()))
    return ret


# Set up menus
options_action = QAction("Image &Occlusion Enhanced Options...", mw)
help_action = QAction("Image &Occlusion Enhanced...", mw)
options_action.triggered.connect(onIoSettings)
mw.addonManager.setConfigAction(__name__, onIoSettings)
help_action.triggered.connect(onIoHelp)
mw.form.menuTools.addAction(options_action)
mw.form.menuHelp.addAction(help_action)

# Set up hooks and monkey patches

# Add-on setup at profile-load time
addHook("profileLoaded", onProfileLoaded)

# aqt.editor.Editor
addHook('setupEditorButtons', onSetupEditorButtons)
EditorWebView.contextMenuEvent = contextMenuEvent
Editor.setNote = wrap(Editor.setNote, onSetNote, "after")
Editor.onImgOccButton = onImgOccButton

# aqt.reviewer.Reviewer
Reviewer._showAnswer = wrap(Reviewer._showAnswer, onShowAnswer, "around")
if not ANKI21:
    Reviewer._keyHandler = wrap(Reviewer._keyHandler, newKeyHandler, "before")
else:
    addHook("reviewStateShortcuts", onReviewerStateShortcuts)
