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
Add notes.
"""

import os
import tempfile

from aqt.qt import *

from aqt import mw
from aqt.utils import tooltip, showWarning

from .ngen import *
from .config import *

from .editor import ImgOccEdit
from .dialogs import ioCritical, ioInfo
from .utils import imageProp, img2path, path2url

from .consts import SUPPORTED_EXTENSIONS

# SVG-Edit configuration
svg_edit_dir = os.path.join(os.path.dirname(__file__),
                            'svg-edit',
                            'editor')
svg_edit_path = os.path.join(svg_edit_dir,
                             'svg-editor.html')
svg_edit_ext = "ext-image-occlusion.js,ext-arrows.js,\
ext-markers.js,ext-shapes.js,ext-eyedropper.js,ext-panning.js,\
ext-snapping.js"
svg_edit_fonts = "'Helvetica LT Std', Arial, sans-serif"
svg_edit_queryitems = [('initStroke[opacity]', '1'),
                       ('showRulers', 'false'),
                       ('extensions', svg_edit_ext)]


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
        isIO = (note and note.model() == getOrCreateModel())

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
                    tooltip("Non-editable note.<br>"
                            "Using image to create new IO note.")

        if not image_path:
            tooltip(("This note cannot be edited, nor is there<br>"
                     "an image to use for an image occlusion."))
            return False

        self.setPreservedAttrs(note)
        self.image_path = image_path

        try:
            width, height = imageProp(image_path)
        except ValueError as e:
            showWarning(
                f"<b>Unsupported image</b> in file <i>{image_path}</i>:"
                f"<br><br>{str(e)}")
            return False

        self.callImgOccEdit(width, height)

    def setPreservedAttrs(self, note):
        self.opref["tags"] = self.ed.tags.text()
        if self.origin == "addcards":
            self.opref["did"] = self.ed.parentWindow.deckChooser.selectedId()
        else:
            self.opref["did"] = mw.col.db.scalar(
                "select did from cards where id = ?", note.cards()[0].id)

    def getIONoteData(self, note):
        """Select image based on mode and set original field contents"""

        note_id = note[self.ioflds['id']]
        image_path = img2path(note[self.ioflds['im']])
        omask = img2path(note[self.ioflds['om']])

        if note_id is None or note_id.count("-") != 2:
            msg = "Editing unavailable: Invalid image occlusion Note ID"
            return msg, None
        elif not omask or not image_path:
            msg = "Editing unavailable: Missing image or original mask"
            return msg, None

        note_id_grps = note_id.split('-')
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
            image_path = img2path(fld)
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
            handle, image_path = tempfile.mkstemp(suffix='.png')
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
            "Select an Image", prev_image_dir,
            f"""Image Files ({" ".join("*." + ext for ext in SUPPORTED_EXTENSIONS)})"""
        )
        if image_path:
            image_path = image_path[0]

        if not image_path:
            return None
        elif not os.path.isfile(image_path):
            tooltip("Invalid image file path")
            return False
        else:
            self.lconf["dir"] = os.path.dirname(image_path)
            return image_path

    def callImgOccEdit(self, width, height):
        """Set up variables, call and prepare ImgOccEdit"""
        ofill = self.sconf['ofill']
        scol = self.sconf['scol']
        swidth = self.sconf['swidth']
        fsize = self.sconf['fsize']
        font = self.sconf['font']

        bkgd_url = path2url(self.image_path)
        opref = self.opref
        onote = self.ed.note
        flds = self.mflds
        deck = mw.col.decks.nameOrNone(opref["did"])

        dialog = ImgOccEdit(self, self.ed.parentWindow)
        dialog.setupFields(flds)
        dialog.switchToMode(self.mode)
        self.imgoccedit = dialog
        logging.debug("Launching new ImgOccEdit instance")

        url = QUrl.fromLocalFile(svg_edit_path)
        items = QUrlQuery()
        items.setQueryItems(svg_edit_queryitems)
        items.addQueryItem('initFill[color]', ofill)
        items.addQueryItem('dimensions', '{0},{1}'.format(width, height))
        items.addQueryItem('bkgd_url', bkgd_url)
        items.addQueryItem('initStroke[color]', scol)
        items.addQueryItem('initStroke[width]', str(swidth))
        items.addQueryItem('text[font_size]', str(fsize))
        items.addQueryItem('text[font_family]', "'%s', %s" %
                           (font, svg_edit_fonts))

        if self.mode != "add":
            items.addQueryItem('initTool', 'select'),
            for i in flds:
                fn = i["name"]
                if fn in self.ioflds_priv:
                    continue
                dialog.tedit[fn].setPlainText(
                    onote[fn].replace('<br />', '\n'))
            svg_url = path2url(opref["omask"])
            items.addQueryItem('url', svg_url)
        else:
            items.addQueryItem('initTool', 'rect'),

        url.setQuery(items)
        dialog.svg_edit.setUrl(url)
        dialog.deckChooser.deck.setText(deck)
        dialog.tags_edit.setCol(mw.col)
        dialog.tags_edit.setText(opref["tags"])

        if onote:
            for i in self.ioflds_prsv:
                if i in onote:
                    dialog.tedit[i].setPlainText(onote[i])

        if self.mode == "add":
            dialog.setModal(False)

            def onSvgEditLoaded():
                dialog.showSvgEdit(True)
                dialog.fitImageCanvas()
        else:
            # modal dialog when editing
            dialog.setModal(True)

            def onSvgEditLoaded():
                # Handle obsolete "aa" occlusion mode:
                if self.opref["occl_tp"] == "aa":
                    ioInfo("obsolete_aa", parent=dialog)
                dialog.showSvgEdit(True)
                dialog.fitImageCanvas()

        dialog.svg_edit.runOnLoaded(onSvgEditLoaded)
        dialog.visible = True
        dialog.show()

    def onChangeImage(self):
        """Change canvas background image"""
        image_path = self.getNewImage()
        if not image_path:
            return False
        try:
            width, height = imageProp(image_path)
        except ValueError as e:
            showWarning(
                f"<b>Unsupported image</b> in file <i>{image_path}</i>:"
                f"<br><br>{str(e)}")
            return False
        bkgd_url = path2url(image_path)
        self.imgoccedit.svg_edit.eval("""
                        svgCanvas.setBackground('#FFF', '%s');
                        svgCanvas.setResolution(%s, %s);
                    """ % (bkgd_url, width, height))
        self.image_path = image_path

    def onAddNotesButton(self, choice, close):
        dialog = self.imgoccedit
        dialog.svg_edit.evalWithCallback(
            "svgCanvas.svgCanvasToString();",
            lambda val, choice=choice, close=close: self._onAddNotesButton(choice, close, val))

    def _onAddNotesButton(self, choice, close, svg):
        """Get occlusion settings in and pass them to the note generator (add)"""
        dialog = self.imgoccedit

        r1 = self.getUserInputs(dialog)
        if r1 is False:
            return False
        (fields, tags) = r1
        did = dialog.deckChooser.selectedId()

        noteGenerator = genByKey(choice)
        gen = noteGenerator(self.ed, svg, self.image_path,
                            self.opref, tags, fields, did)
        r = gen.generateNotes()
        if r is False:
            return False

        if self.origin == "addcards" and self.ed.note:
            # Update Editor with modified tags and sources field
            self.ed.tags.setText(" ".join(tags))
            self.ed.saveTags()
            for i in self.ioflds_prsv:
                if i in self.ed.note:
                    self.ed.note[i] = fields[i]
            self.ed.loadNote()
            deck = mw.col.decks.nameOrNone(did)
            self.ed.parentWindow.deckChooser.deck.setText(deck)

        if close:
            dialog.close()

        mw.reset()

    def onEditNotesButton(self, choice):
        dialog = self.imgoccedit
        dialog.svg_edit.evalWithCallback(
            "svgCanvas.svgCanvasToString();",
            lambda val, choice=choice: self._onEditNotesButton(choice, val))

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
        gen = noteGenerator(self.ed, svg, self.image_path,
                            self.opref, tags, fields, did)
        r = gen.updateNotes()
        if r is False:
            return False

        if r != "reset":
            # no media cache/collection reset required
            dialog.close()

        else:
            # Refresh image cache
            dialog.svg_edit.page().profile().clearHttpCache()
            dialog.close()

            # Force EditCurrent and Browser editor instances reload
            # in order to make use of refreshed image cache
            if not self.origin == "addcards":
                def onToHtmlCallback(html):
                    if self.ed.web:
                        self.ed.web.reload()
                        self.ed.web.setHtml(html)
                        self.ed.loadNote()
                self.ed.web.page().toHtml(onToHtmlCallback)  # async execution

            # write a dummy file to update collection.media modtime and
            # force sync
            media_dir = mw.col.media.dir()
            fpath = os.path.join(media_dir, "syncdummy.txt")
            if not os.path.isfile(fpath):
                with open(fpath, "w") as f:
                    f.write("io sync dummy")
            os.remove(fpath)

        mw.reset()  # FIXME: causes glitches in editcurrent mode

    def getUserInputs(self, dialog, edit=False):
        """Get fields and tags from ImgOccEdit while checking note type"""
        fields = {}
        # note type integrity check:
        io_model_fields = mw.col.models.fieldNames(self.model)
        if not all(x in io_model_fields for x in list(self.ioflds.values())):
            ioCritical("model_error", help="notetype", parent=dialog)
            return False
        for i in self.mflds:
            fn = i['name']
            if fn in self.ioflds_priv:
                continue
            if edit and fn in self.sconf["skip"]:
                continue
            text = dialog.tedit[fn].toPlainText().replace('\n', '<br />')
            fields[fn] = text
        tags = dialog.tags_edit.text().split()
        return (fields, tags)
