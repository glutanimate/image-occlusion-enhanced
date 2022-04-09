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
Add notes.
"""

import os
import tempfile

from anki.config import Config
from aqt import mw
from aqt.qt import QApplication, QFileDialog, Qt, QUrl, QUrlQuery
from aqt.utils import showWarning, tooltip

from .config import *
from .consts import SUPPORTED_EXTENSIONS
from .dialogs import ioCritical, ioInfo
from .editor import ImgOccEdit
from .lang import _
from .ngen import *
from .utils import get_image_dimensions, img_element_to_path, path_to_url

# SVG-Edit configuration
svg_edit_dir = os.path.join(os.path.dirname(__file__), "svg-edit", "editor")
svg_edit_path = os.path.join(svg_edit_dir, "svg-editor.html")
svg_edit_ext = "ext-image-occlusion.js,ext-arrows.js,ext-markers.js,ext-shapes.js,ext-eyedropper.js,ext-panning.js,ext-snapping.js"
svg_edit_fonts = "'Helvetica LT Std', Arial, sans-serif"
svg_edit_queryitems = [
    ("initStroke[opacity]", "1"),
    ("showRulers", "false"),
    ("extensions", svg_edit_ext),
]


class ImgOccAdd(object):
    def __init__(self, editor, origin, oldimg=None):
        self.ed = editor
        self.image_path = oldimg
        self.mode = "add"
        self.origin = origin
        self.opref = {}  # original io session preference
        loadConfig(self)

    def occlude(self, image_path=None):

        note = self.ed.note
        isIO = note and note.model() == getOrCreateModel()

        if not image_path:
            if self.origin == "addcards":
                image_path = self.getNewImage(parent=self.ed.parentWindow)
                if not image_path:
                    return False
            elif isIO:
                msg, image_path = self.getIONoteData(note)
                self.mode = "edit"
                if not image_path:
                    tooltip(msg)
                    return False
            else:
                image_path = self.getImageFromFields(note.fields)
                if image_path:
                    tooltip(
                        _("Non-editable note.<br>Using image to create new IO note.")
                    )

        if not image_path:
            tooltip(
                (
                    _(
                        "This note cannot be edited, nor is there<br>"
                        "an image to use for an image occlusion."
                    )
                )
            )
            return False

        self.setPreservedAttrs(note)
        self.image_path = image_path

        try:
            width, height = get_image_dimensions(image_path)
        except ValueError as e:
            showWarning(
                _(
                    "<b>Unsupported image</b> in file <i>{image_path}</i>:"
                    "<br><br>{error}"
                ).format(image_path=image_path, error=str(e))
            )
            return False

        self.callImgOccEdit(width, height)

    def setPreservedAttrs(self, note):
        # FIXME: Not necessarily up-to-date with new tag edit contents
        self.opref["tags"] = note.tags
        if self.origin == "addcards":
            self.opref["did"] = self.ed.parentWindow.deckChooser.selectedId()
        else:
            self.opref["did"] = mw.col.db.scalar(
                "select did from cards where id = ?", note.cards()[0].id
            )

    def getIONoteData(self, note):
        """Select image based on mode and set original field contents"""

        note_id = note[self.ioflds["id"]]
        image_path = img_element_to_path(note[self.ioflds["im"]])
        omask = img_element_to_path(note[self.ioflds["om"]])

        if note_id is None or note_id.count("-") != 2:
            msg = _("Editing unavailable: Invalid image occlusion Note ID")
            return msg, None
        elif not omask or not image_path:
            msg = _("Editing unavailable: Missing image or original mask")
            return msg, None

        note_id_grps = note_id.split("-")
        self.opref["note_id"] = note_id
        self.opref["uniq_id"] = note_id_grps[0]
        self.opref["occl_tp"] = note_id_grps[1]
        self.opref["image"] = image_path
        self.opref["omask"] = omask

        return None, image_path

    def getImageFromFields(self, fields):
        """Parse fields for valid images"""
        image_path = None
        for fld in fields:
            image_path = img_element_to_path(fld)
            if image_path:
                break
        return image_path

    def getNewImage(self, parent=None, noclip=False):
        """Get image from file selection or clipboard"""
        if noclip:
            clip = None
        else:
            clip = QApplication.clipboard()
        if clip and clip.mimeData().imageData():
            if mw.col.get_config_bool(Config.Bool.PASTE_IMAGES_AS_PNG):
                handle, image_path = tempfile.mkstemp(suffix=".png")
            else:
                handle, image_path = tempfile.mkstemp(suffix=".jpg")
            clip.image().save(image_path)
            clip.clear()
            if os.stat(image_path).st_size == 0:
                # workaround for a clipboard bug
                return self.getNewImage(noclip=True)
            else:
                return str(image_path)

        # retrieve last used image directory
        prev_image_dir = self.lconf["dir"]
        if not prev_image_dir or not os.path.isdir(prev_image_dir):
            prev_image_dir = IO_HOME

        image_path = QFileDialog.getOpenFileName(
            parent,
            _("Select an Image"),
            prev_image_dir,
            _("""Image Files ({file_glob_list})""").format(
                file_glob_list=" ".join("*." + ext for ext in SUPPORTED_EXTENSIONS)
            ),
        )
        if image_path:
            image_path = image_path[0]

        if not image_path:
            return None
        elif not os.path.isfile(image_path):
            tooltip(_("Invalid image file path"))
            return False
        else:
            self.lconf["dir"] = os.path.dirname(image_path)
            return image_path

    def callImgOccEdit(self, width, height):
        """Set up variables, call and prepare ImgOccEdit"""
        ofill = self.sconf["ofill"]
        scol = self.sconf["scol"]
        swidth = self.sconf["swidth"]
        fsize = self.sconf["fsize"]
        font = self.sconf["font"]

        bkgd_url = path_to_url(self.image_path)
        opref = self.opref
        onote = self.ed.note
        flds = self.mflds

        dialog = ImgOccEdit(self, self.ed.parentWindow)
        dialog.setupFields(flds)
        dialog.switchToMode(self.mode)
        self.imgoccedit = dialog
        logging.debug("Launching new ImgOccEdit instance")

        url = QUrl.fromLocalFile(svg_edit_path)
        items = QUrlQuery()
        items.setQueryItems(svg_edit_queryitems)
        items.addQueryItem("initFill[color]", ofill)
        items.addQueryItem("dimensions", "{0},{1}".format(width, height))
        items.addQueryItem("bkgd_url", bkgd_url)
        items.addQueryItem("initStroke[color]", scol)
        items.addQueryItem("initStroke[width]", str(swidth))
        items.addQueryItem("text[font_size]", str(fsize))
        items.addQueryItem("text[font_family]", "'%s', %s" % (font, svg_edit_fonts))

        if self.mode != "add":
            items.addQueryItem("initTool", "select"),
            for i in flds:
                fn = i["name"]
                if fn in self.ioflds_priv:
                    continue
                dialog.tedit[fn].setPlainText(onote[fn].replace("<br />", "\n"))
            svg_url = path_to_url(opref["omask"])
            items.addQueryItem("url", svg_url)
        else:
            items.addQueryItem("initTool", "rect"),

        url.setQuery(items)
        dialog.svg_edit.setUrl(url)
        dialog.deckChooser.selected_deck_id = opref["did"]
        dialog.tags_edit.setCol(mw.col)
        dialog.tags_edit.setText(" ".join(opref["tags"]))

        if onote:
            for i in self.ioflds_prsv:
                if i in onote:
                    dialog.tedit[i].setPlainText(onote[i])

        if self.mode == "add":
            dialog.setModal(False)

            def onSvgEditLoaded():
                dialog.showSvgEdit(True)
                # TODO: find better solution
                dialog.fitImageCanvas()
                dialog.fitImageCanvas(delay=200)

        else:
            # modal dialog when editing
            dialog.setModal(True)

            def onSvgEditLoaded():
                # Handle obsolete "aa" occlusion mode:
                if self.opref["occl_tp"] == "aa":
                    ioInfo("obsolete_aa", parent=dialog)
                dialog.showSvgEdit(True)
                dialog.fitImageCanvas()
                dialog.fitImageCanvas(delay=200)

        dialog.svg_edit.runOnLoaded(onSvgEditLoaded)
        dialog.visible = True
        dialog.show()
        # Workaround for window intermittently spawning below AddCards on 2.1.50+:
        dialog.activateWindow()
        dialog.setWindowState(Qt.WindowState.WindowActive)

    def onChangeImage(self):
        """Change canvas background image"""
        image_path = self.getNewImage()
        if not image_path:
            return False
        try:
            width, height = get_image_dimensions(image_path)
        except ValueError as e:
            showWarning(
                _(
                    "<b>Unsupported image</b> in file <i>{image_path}</i>:"
                    "<br><br>{error}"
                ).format(image_path=image_path, error=str(e))
            )
            return False
        bkgd_url = path_to_url(image_path)
        self.imgoccedit.svg_edit.eval(
            """
                        svgCanvas.setBackground('#FFF', '%s');
                        svgCanvas.setResolution(%s, %s);
                    """
            % (bkgd_url, width, height)
        )
        self.image_path = image_path

    def onAddNotesButton(self, choice, close):
        dialog = self.imgoccedit
        # If the user is in in-group editing mode (i.e. editing a shape that
        # is grouped with other shapes) svgCanvasToString() doesn't work and
        # the callback gets called with `None` (might be a bug in svg-edit).
        # Calling leaveContext() first fixes this.
        dialog.svg_edit.evalWithCallback(
            "svgCanvas.leaveContext(); svgCanvas.svgCanvasToString();",
            lambda val, choice=choice, close=close: self._onAddNotesButton(
                choice, close, val
            ),
        )

    def _onAddNotesButton(self, choice, close, svg):
        """Get occlusion settings in and pass them to the note generator (add)"""
        dialog = self.imgoccedit

        r1 = self.getUserInputs(dialog)
        if r1 is False:
            return False
        (fields, tags) = r1
        did = dialog.deckChooser.selected_deck_id

        noteGenerator = genByKey(choice)
        gen = noteGenerator(
            self.ed, svg, self.image_path, self.opref, tags, fields, did
        )
        r = gen.generateNotes()
        if r is False:
            return False

        if self.origin == "addcards" and self.ed.note:
            # Update Editor with modified tags and sources field
            for i in self.ioflds_prsv:
                if i in self.ed.note:
                    self.ed.note[i] = fields[i]
            self.ed.note.tags = tags
            self.ed.loadNote()

        if close:
            dialog.close()

        mw.reset()

    def onEditNotesButton(self, choice):
        dialog = self.imgoccedit
        # See the comment above in addNotesButton() about
        # the call to `leaveContext()`.
        dialog.svg_edit.evalWithCallback(
            "svgCanvas.leaveContext(); svgCanvas.svgCanvasToString();",
            lambda val, choice=choice: self._onEditNotesButton(choice, val),
        )

    def _onEditNotesButton(self, choice, svg):
        """Get occlusion settings and pass them to the note generator (edit)"""
        dialog = self.imgoccedit

        r1 = self.getUserInputs(dialog, edit=True)
        if r1 is False:
            return False
        (fields, tags) = r1
        did = self.opref["did"]
        old_occl_tp = self.opref["occl_tp"]

        noteGenerator = genByKey(choice, old_occl_tp)
        gen = noteGenerator(
            self.ed, svg, self.image_path, self.opref, tags, fields, did
        )
        r = gen.updateNotes()
        if r is False:
            return False

        if r != "reset":
            # no media cache/collection reset required
            dialog.close()

        else:
            # Refresh image cache. We need to do this in order to refresh image
            # display across all web views the images could be presented in.
            # (i.e. cache-busting IO images in the reviewer alone via JS is not
            # sufficient)
            mw.web.page().profile().clearHttpCache()
            dialog.close()

            # write a dummy file to update collection.media modtime and
            # force sync
            media_dir = mw.col.media.dir()
            fpath = os.path.join(media_dir, "syncdummy.txt")
            if not os.path.isfile(fpath):
                with open(fpath, "w") as f:
                    f.write("io sync dummy")
            os.remove(fpath)

        def refresh_editor():
            # FIXME: Incredibly ugly hack to refresh editor web view in order to make
            # changes to images visible
            self.ed.outerLayout.removeWidget(self.ed.web)
            self.ed.web.reload()
            self.ed.web.stdHtml("")
            self.ed.setupWeb()
            self.ed.loadNote()

        refresh_editor()

        def refresh_reviewer():
            # FIXME: Incredibly ugly hack to refresh reviewer web view in  order to make
            # changes to images visible. Other solutions like
            # reviewer._initWeb(); reviewer._showQuestion() do not seem to work reliably
            mw.moveToState("overview")
            mw.progress.single_shot(100, lambda: mw.moveToState("review"))

        mw.reset()

        if mw.state == "review":
            mw.progress.single_shot(100, refresh_reviewer)

    def getUserInputs(self, dialog, edit=False):
        """Get fields and tags from ImgOccEdit while checking note type"""
        fields = {}
        # note type integrity check:
        io_model_fields = mw.col.models.fieldNames(self.model)
        if not all(x in io_model_fields for x in list(self.ioflds.values())):
            ioCritical("model_error", help="notetype", parent=dialog)
            return False
        for i in self.mflds:
            fn = i["name"]
            if fn in self.ioflds_priv:
                continue
            if edit and fn in self.sconf["skip"]:
                continue
            text = dialog.tedit[fn].toPlainText().replace("\n", "<br />")
            fields[fn] = text
        tags = dialog.tags_edit.text().split()
        return (fields, tags)
