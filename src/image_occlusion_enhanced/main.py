# -*- coding: utf-8 -*-

# Image Occlusion Enhanced Add-on for Anki
#
# Copyright (C) 2016-2020  Aristotelis P. <https://glutanimate.com/>
# Copyright (C) 2012-2015  Tiago Barroso <tmbb@campus.ul.pt>
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
Sets up buttons and menus and calls other modules.
"""

import logging
import sys

from anki.lang import _ as __
from aqt.qt import *
from aqt.qt import QMenu

from aqt import mw
from aqt.editor import Editor, EditorWebView
from aqt.addcards import AddCards
from aqt.editcurrent import EditCurrent
from aqt.reviewer import Reviewer
from aqt.utils import tooltip
from aqt.webview import AnkiWebView
from anki.hooks import wrap, addHook, runHook

from .consts import *
from .config import *
from .add import ImgOccAdd
from .options import ImgOccOpts
from .dialogs import ioHelp, ioCritical
from .lang import _

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)


def onIoSettings():
    """Call settings dialog if Editor not active"""
    # TODO: fix ImgOccEdit detection
    if hasattr(mw, "ImgOccEdit") and mw.ImgOccEdit.visible:
        tooltip(_("Please close Image Occlusion Editor" " to access the Options."))
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
            dflt_fields = list(mw.col.conf["imgocc"]["flds"].values())
        else:
            dflt_fields = list(IO_FLDS.values())
        # note type integrity check
        if not all(x in io_model_fields for x in dflt_fields):
            ioCritical("model_error", help="notetype", parent=self.parentWindow)
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
        tt = _("Add Image Occlusion")
        icon_name = "add.png"
    else:
        tt = _("Edit Image Occlusion")
        icon_name = "edit.png"

    icon = os.path.join(ICONS_PATH, icon_name)

    b = editor.addButton(
        icon,
        _("I/O"),
        lambda o=editor: onImgOccButton(o),
        tip="{} ({})".format(tt, hotkey),
        keys=hotkey,
        disables=False,
    )

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
        if sys.platform == "win32":
            subprocess.Popen(["explorer", path])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except OSError as e:
        QDesktopServices.openUrl(QUrl("file://" + path))


def maybe_add_image_menu(webview: AnkiWebView, menu: QMenu):
    # cf. https://doc.qt.io/qt-5/qwebenginepage.html#contextMenuData
    context_data = webview.page().contextMenuData()
    url = context_data.mediaUrl()
    image_name = url.fileName()
    path = os.path.join(mw.col.media.dir(), image_name)
    if url.isValid() and path:
        a = menu.addAction(_("Occlude Image"))
        a.triggered.connect(
            lambda _, u=path, e=webview.editor: onImgOccButton(e, image_path=u)
        )
        a = menu.addAction(_("Open Image"))
        a.triggered.connect(lambda _, u=path: openImage(u))


def legacyEditorContextMenuEvent(self, evt):
    """Legacy: Monkey-patch context menu to add our own entries on Anki releases
    that do not support the 'EditorWebView.contextMenuEvent' hook"""
    m = QMenu(self)
    a = m.addAction(__("Cut"))
    a.triggered.connect(self.onCut)
    a = m.addAction(__("Copy"))
    a.triggered.connect(self.onCopy)
    a = m.addAction(__("Paste"))
    a.triggered.connect(self.onPaste)
    ##################################################
    maybe_add_image_menu(self, m)
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


def js_note_loaded(note) -> str:
    js = []

    # Conditionally set body CSS  class
    if not (note and note.model()["name"] == IO_MODEL_NAME):
        js.append("""$("body").removeClass("ionote");""")
    else:
        # Only hide first field if it's the ID field
        # TODO? identify ID field HTML element automatically
        if note.model()["flds"][0]["name"] == IO_FLDS["id"]:
            js.append("""$("body").addClass("ionote-id");""")
        else:
            js.append("""$("body").removeClass("ionote-id");""")
        js.append("""$("body").addClass("ionote");""")

    return "\n".join(js)


def on_editor_will_load_note(js: str, note, editor):
    """Customize the editor when IO notes are active"""
    if not editor.web:
        # editor is in cleanup TODO: evaluate if check still necessary
        return js
    js_additions = js_note_loaded(note)
    return "\n".join([js, js_additions])


def legacyOnSetNote(self, note, hide=True, focus=False):
    """Legacy: Monkey-patch Editor.onSetNote
    when 'editor_will_load_note' hook unavailable"""
    if self.web is None:  # editor is in cleanup
        return
    js = js_note_loaded(self.note)
    self.web.eval(js)


def on_webview_will_set_content(web_content, context):
    if not isinstance(context, Editor):
        return
    web_content.body += io_editor_style


def on_main_window_did_init():
    """Add our custom user styles to the editor HTML
    Need to delay this to avoid interferences with other add-ons that might
    potentially overwrite editor HTML"""
    try:  # 2.1.22+
        from aqt.gui_hooks import webview_will_set_content

        webview_will_set_content.append(on_webview_will_set_content)
    except (ImportError, ModuleNotFoundError):
        from aqt import editor

        editor._html = editor._html + io_editor_style.replace("%", "%%")


_profile_singleshot_run = False


def on_profile_loaded_singleshot():
    """Legacy single-shot function to delay execution of particular code paths
    until Anki (and other add-ons) loaded"""
    global _profile_singleshot_run
    if _profile_singleshot_run:
        return
    on_main_window_did_init()
    _profile_singleshot_run = True


def on_profile_loaded():
    """Setup add-on config and templates, update if necessary"""
    getSyncedConfig()
    getLocalConfig()
    getOrCreateModel()


# Mask toggle hotkey


def onHintHotkey():
    mw.web.eval(
        """
        var ioBtn = document.getElementById("io-revl-btn");
        if (ioBtn) {ioBtn.click();}
    """
    )


def on_mw_state_shortcuts(state: str, shortcuts: list):
    """Add hint hotkey when in Reviewer"""
    if state != "review":
        return
    shortcuts.append(("G", onHintHotkey))


# Retain scroll position when answering

# TODO: Handle in JS


def onShowAnswer(self, _old):
    """Retain scroll position across answering the card"""
    if not self.card or not self.card.model()["name"] == IO_MODEL_NAME:
        return _old(self)
    scroll_pos = self.web.page().scrollPosition()
    ret = _old(self)
    self.web.eval("window.scrollTo({}, {});".format(scroll_pos.x(), scroll_pos.y()))
    return ret


def setup_menus():
    options_action = QAction(_("Image &Occlusion Enhanced Options..."), mw)
    help_action = QAction(_("Image &Occlusion Enhanced..."), mw)
    options_action.triggered.connect(onIoSettings)
    mw.addonManager.setConfigAction(__name__, onIoSettings)
    help_action.triggered.connect(onIoHelp)
    mw.form.menuTools.addAction(options_action)
    mw.form.menuHelp.addAction(help_action)


def setup_addon():
    setup_menus()

    # Set up hooks and monkey patches

    # Add-on setup at main window load time

    try:  # 2.1.28+
        from aqt.gui_hooks import main_window_did_init

        main_window_did_init.append(on_main_window_did_init)
    except (ImportError, ModuleNotFoundError):
        try:  # 2.1.20+
            from aqt.gui_hooks import profile_did_open

            profile_did_open.append(on_profile_loaded_singleshot)
        except (ImportError, ModuleNotFoundError):
            addHook("profileLoaded", on_profile_loaded_singleshot)

    # Add-on setup at profile load time

    try:  # 2.1.20+
        from aqt.gui_hooks import profile_did_open

        profile_did_open.append(on_profile_loaded)
    except (ImportError, ModuleNotFoundError):
        addHook("profileLoaded", on_profile_loaded)

    # aqt.editor.Editor

    try:  # 2.1.20+
        from aqt.gui_hooks import editor_did_init_buttons

        editor_did_init_buttons.append(onSetupEditorButtons)
    except (ImportError, ModuleNotFoundError):
        addHook("setupEditorButtons", onSetupEditorButtons)

    try:  # 2.1.20+
        from aqt.gui_hooks import editor_will_show_context_menu

        editor_will_show_context_menu.append(maybe_add_image_menu)
    except (ImportError, ModuleNotFoundError):
        EditorWebView.contextMenuEvent = legacyEditorContextMenuEvent

    try:  # 2.1.20+
        from aqt.gui_hooks import editor_will_load_note

        editor_will_load_note.append(on_editor_will_load_note)
    except (ImportError, ModuleNotFoundError):
        Editor.setNote = wrap(Editor.setNote, legacyOnSetNote, "after")

    Editor.onImgOccButton = onImgOccButton

    # aqt.reviewer.Reviewer

    Reviewer._showAnswer = wrap(Reviewer._showAnswer, onShowAnswer, "around")

    try:  # 2.1.20+
        from aqt.gui_hooks import state_shortcuts_will_change

        state_shortcuts_will_change.append(on_mw_state_shortcuts)
    except (ImportError, ModuleNotFoundError):
        addHook(
            "reviewStateShortcuts",
            lambda shortcuts: on_mw_state_shortcuts("review", shortcuts),
        )
