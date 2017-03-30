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
import os

from aqt.qt import *

from aqt import mw
from aqt.editor import Editor
from aqt.addcards import AddCards
from aqt.editcurrent import EditCurrent
from aqt.reviewer import Reviewer
from aqt.utils import getFile, tooltip, saveGeom, restoreGeom
from anki.hooks import wrap, addHook

import tempfile

from config import *
from resources import *
from ngen import *
from dialogs import ImgOccEdit, ImgOccOpts, ioHelp, ioError
from utils import imageProp, img2path, path2url
import nconvert

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

# SVG-Edit configuration
svg_edit_dir = os.path.join(os.path.dirname(__file__),
                            'svg-edit',
                            'svg-edit-2.6')
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
    def __init__(self, ed, mode):
        self.ed = ed
        self.mode = mode
        self.opref = {} # original io session preference
        loadConfig(self)

    def selImage(self, oldimg=None):
        """Select image and set up variables for the IO Editor"""
        note = self.ed.note
        opref = self.opref

        opref["tags"] = self.ed.tags.text()

        if self.mode != "add":
            note_id = None
            # can only get the deck of the current note/card via a db call:
            opref["did"] = mw.col.db.scalar(
                    "select did from cards where id = ?", note.cards()[0].id)
            note_id = note[self.ioflds['id']]
            note_id_grps = note_id.split('-')
            if note_id == None or len(note_id_grps) != 3:
                tooltip("Editing unavailable: Invalid Image Occlusion Note ID")
                return
            opref["note_id"] = note_id
            opref["uniq_id"] = note_id_grps[0]
            opref["occl_tp"] = note_id_grps[1]
            opref["image"] = img2path(note[self.ioflds['im']])
            opref["omask"] = img2path(note[self.ioflds['om']])
            if None in [opref["omask"], opref["image"]]:
                tooltip("Editing unavailable: Missing Image or Original Mask")
                return
            image_path = opref["image"]
        else:
            opref["did"] = self.ed.parentWindow.deckChooser.selectedId()
            image_path = self.getImage(parent=self.ed.parentWindow)
            if not image_path: # invalid path, fall back to old image or None
                self.image_path = oldimg
                return

        self.image_path = image_path
        self.callImgOccEdit()

    def getImage(self, parent=None, noclip=False):
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
                return self.getImage(noclip=True)
            else:
                return unicode(image_path)

        # retrieve last used image directory
        prev_image_dir = self.lconf["dir"]
        if not prev_image_dir or not os.path.isdir(prev_image_dir):
            prev_image_dir = IO_HOME

        image_path = QFileDialog.getOpenFileName(parent,
                             "Select an Image", prev_image_dir,
                             "Image Files (*.png *jpg *.jpeg *.gif)")
        image_path = unicode(image_path)

        if not image_path:
            return None
        elif not os.path.isfile(image_path):
            tooltip("Invalid image file path")
            return None
        else:
            self.lconf["dir"] = os.path.dirname(image_path)
            return image_path

    def callImgOccEdit(self):
        """Set up variables, call and prepare ImgOccEdit"""
        width, height = imageProp(self.image_path)
        if not width:
            tooltip("Not a valid image file.")
            return False
        ofill = self.sconf['ofill']
        scol = self.sconf['scol']
        swidth = self.sconf['swidth']
        fsize = self.sconf['fsize']
        font = self.sconf['font']

        bkgd_url = path2url(self.image_path)
        opref = self.opref
        onote = self.ed.note
        mode = self.mode
        flds = self.mflds
        deck = mw.col.decks.nameOrNone(opref["did"])

        try:
            mw.ImgOccEdit is not None
            mw.ImgOccEdit.resetWindow()
            # use existing IO instance when available
        except AttributeError:
            mw.ImgOccEdit = ImgOccEdit(mw)
            mw.ImgOccEdit.setupFields(flds)
            logging.debug("Launching new ImgOccEdit instance")
        dialog = mw.ImgOccEdit
        dialog.switchToMode(self.mode)

        url = QUrl.fromLocalFile(svg_edit_path)
        url.setQueryItems(svg_edit_queryitems)
        url.addQueryItem('initFill[color]', ofill)
        url.addQueryItem('dimensions', '{0},{1}'.format(width, height))
        url.addQueryItem('bkgd_url', bkgd_url)
        url.addQueryItem('initStroke[color]', scol)
        url.addQueryItem('initStroke[width]', str(swidth))
        url.addQueryItem('text[font_size]', str(fsize))
        url.addQueryItem('text[font_family]', "'%s', %s" % (font, svg_edit_fonts))

        if mode != "add":
            url.addQueryItem('initTool', 'select'),
            for i in flds:
                fn = i["name"]
                if fn in self.ioflds_priv:
                    continue
                dialog.tedit[fn].setPlainText(onote[fn].replace('<br />', '\n'))
            svg_url = path2url(opref["omask"])
            url.addQueryItem('url', svg_url)
        else:
            url.addQueryItem('initTool', 'rect'),

        dialog.svg_edit.setUrl(url)
        dialog.deckChooser.deck.setText(deck)
        dialog.tags_edit.setCol(mw.col)
        dialog.tags_edit.setText(opref["tags"])

        for i in self.ioflds_prsv:
            if i in onote:
                dialog.tedit[i].setPlainText(onote[i])

        dialog.visible = True
        if mode == "add":
            dialog.show()
        else:
            # modal dialog when editing
            dialog.exec_()


    def onChangeImage(self):
        """Change canvas background image"""
        image_path = self.getImage()
        if not image_path:
            return False
        width, height = imageProp(image_path)
        if not width:
            tooltip("Not a valid image file.")
            return False
        bkgd_url = path2url(image_path)
        mw.ImgOccEdit.svg_edit.eval("""
                        svgCanvas.setBackground('#FFF', '%s');
                        svgCanvas.setResolution(%s, %s);
                        //svgCanvas.zoomChanged('', 'canvas');
                    """ %(bkgd_url, width, height))
        self.image_path = image_path

    def onAddNotesButton(self, choice, close):
        """Get occlusion settings in and pass them to the note generator (add)"""
        dialog = mw.ImgOccEdit
        svg_edit = dialog.svg_edit
        svg = svg_edit.page().mainFrame().evaluateJavaScript(
            "svgCanvas.svgCanvasToString();")
        svg = unicode(svg) # store svg as unicode string

        r1 = self.getUserInputs(dialog)
        if r1 == False:
            return False
        (fields, tags) = r1
        did = dialog.deckChooser.selectedId()

        noteGenerator = genByKey(choice)
        gen = noteGenerator(self.ed, svg, self.image_path,
                                    self.opref, tags, fields, did)
        r = gen.generateNotes()
        if r == False:
            return False

        if self.mode == "add" and self.ed.note:
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
        """Get occlusion settings and pass them to the note generator (edit)"""
        dialog = mw.ImgOccEdit
        svg_edit = dialog.svg_edit
        svg = svg_edit.page().mainFrame().evaluateJavaScript(
            "svgCanvas.svgCanvasToString();")

        r1 = self.getUserInputs(dialog, edit=True)
        if r1 == False:
            return False
        (fields, tags) = r1
        did = self.opref["did"]
        old_occl_tp = self.opref["occl_tp"]

        noteGenerator = genByKey(choice, old_occl_tp)
        gen = noteGenerator(self.ed, svg, self.image_path,
                                    self.opref, tags, fields, did)
        r = gen.updateNotes()
        if r == False:
            return False

        mw.ImgOccEdit.close()

        if r == "reset":
            # modifications to mask require media collection reset
            ## refresh webview image cache
            QWebSettings.clearMemoryCaches()
            ## write a dummy file to update collection.media modtime and force sync
            media_dir = mw.col.media.dir()
            fpath = os.path.join(media_dir, "syncdummy.txt")
            if not os.path.isfile(fpath):
                with open(fpath, "w") as f:
                    f.write("io sync dummy")
            os.remove(fpath)

        mw.reset() # FIXME: causes glitches in editcurrent mode

    def getUserInputs(self, dialog, edit=False):
        """Get fields and tags from ImgOccEdit while checking note type"""
        fields = {}
        # note type integrity check:
        io_model_fields = mw.col.models.fieldNames(self.model)
        if not all(x in io_model_fields for x in self.ioflds.values()):
            ioError("<b>Error</b>: Image Occlusion note type " \
                "not configured properly.Please make sure you did not " \
                "manually delete or rename any of the default fields.",
                help="notetype")
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
    if mode != "add" and ed.note.model() != io_model:
        tooltip("Can only edit notes with the %s note type" % IO_MODEL_NAME)
        return
    try: # allows us to fall back to old image if necessary
        oldimg = mw.ImgOccAdd.image_path
    except AttributeError:
        oldimg = None
    mw.ImgOccAdd = ImgOccAdd(ed, mode)
    mw.ImgOccAdd.selImage(oldimg)

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