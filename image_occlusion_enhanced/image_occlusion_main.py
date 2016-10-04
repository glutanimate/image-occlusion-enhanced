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

import os

from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import QUrl

from aqt import mw, webview, deckchooser, tagedit
from aqt.editor import Editor
from aqt.utils import tooltip, openLink, showWarning, saveGeom, restoreGeom
from aqt.qt import *
from anki.hooks import wrap, addHook



import etree.ElementTree as etree
import re
import tempfile
import urlparse, urllib

from notegen import ImgOccNoteGenerator, ImgOccNoteGeneratorHiding

from config import *
import svgutils
from dialogs import ImgOccEdit, ImgOccOpts
from resources import *

io_help_link = "https://github.com/Glutanimate/image-occlusion-enhanced/wiki"

# SVG-Edit configuration
svg_edit_dir = os.path.join(os.path.dirname(__file__),
                            'svg-edit',
                            'svg-edit-2.6')
svg_edit_path = os.path.join(svg_edit_dir,
                            'svg-editor.html')
svg_edit_ext = "ext-image-occlusion.js,ext-arrows.js,ext-markers.js,ext-shapes.js,ext-eyedropper.js"
svg_edit_queryitems = [('initStroke[opacity]', '1'),
                       ('initStroke[color]', '2D2D2D'),
                       ('initStroke[width]', '0'),
                       ('initTool', 'rect'),
                       ('text[font_family]', "'Helvetica LT Std', Arial, sans-serif"),
                       ('extensions', svg_edit_ext)]

def path2url(path):
    return urlparse.urljoin(
      'file:', urllib.pathname2url(path.encode('utf-8')))

class ImgOccAdd(object):
    def __init__(self, ed):
        self.ed = ed
        self.mw = mw
        self.dialog = None
        self.mode = "add"
        self.onote = {}

        # load preferences
        load_prefs(self)

    def getImage(self, mode=None):
        self.mode = mode
        note = self.ed.note
        onote = self.onote
        for i in IO_FLDS.keys():
            onote[i] = None

        # always preserve tags and sources if available
        onote["tags"] = self.ed.tags.text()
        if IO_FLDS["sources"] in note:
            onote["sources"] = note[IO_FLDS["sources"]]

        if mode == "add":
            clip = QApplication.clipboard()
            if clip.mimeData().imageData():
                handle, image_path = tempfile.mkstemp(suffix='.png')
                clip.image().save(image_path)
                clip.clear()
            else:
                # retrieve last used image directory
                prev_image_dir = self.prefs["prev_image_dir"]
                if not os.path.isdir(prev_image_dir):
                    prev_image_dir = IO_HOME

                image_path = QFileDialog.getOpenFileName(self.ed.parentWindow,
                             "Choose Image", prev_image_dir, 
                             "Image Files (*.png *jpg *.jpeg *.gif)")

                if os.path.isfile(image_path):
                    self.prefs["prev_image_dir"] = os.path.dirname( image_path )
                    save_prefs(self)
        else:
            if note.model()["name"] != IO_MODEL_NAME:
                tooltip("Not an IO card")
                return
            imgpatt = r"""<img.*?src=(["'])(.*?)\1"""
            imgregex = re.compile(imgpatt, flags=re.I|re.M|re.S)  
            invalfile = False
            for i in onote.keys():
                if i == "tags":
                    continue
                fld = IO_FLDS[i]
                if i in ["uuid", "qmask", "amask"]:
                    onote[i] = note[fld]
                elif i in ["image", "fmask"]:
                    html = note[fld]
                    fname = imgregex.search(html)
                    if fname:
                        fpath = os.path.join(mw.col.media.dir(),fname.group(2))
                        if os.path.isfile(fpath):
                            onote[i] = fpath
                        else:
                            invalfile = True
                else:
                    onote[i] = note[fld].replace('<br />', '\n')
            if invalfile or onote["uuid"]:
                showWarning("IO card not configured properly for editing")
                return
            image_path = onote["image"] 

        if not image_path:
            return
        elif not os.path.isfile(image_path):
            tooltip("Not a valid image file.")
            return

        self.image_path = image_path
        self.call_ImgOccEdit()

    def call_ImgOccEdit(self):
        self.dialog = ImgOccEdit(self, mw)
        dialog = self.dialog
        onote = self.onote

        width, height = svgutils.imageProp(self.image_path)
        initFill_color = self.mw.col.conf['image_occlusion_conf']['initFill[color]']
        url = QUrl.fromLocalFile(svg_edit_path)
        url.setQueryItems(svg_edit_queryitems)
        url.addQueryItem('initFill[color]', initFill_color)
        url.addQueryItem('dimensions', '{0},{1}'.format(width, height))
        url.addQueryItem('bkgd_url', path2url(self.image_path))
            
        if self.mode != "add":
            dialog.header_edit.setPlainText(onote["header"])
            dialog.footer_edit.setPlainText(onote["footer"])
            dialog.remarks_edit.setPlainText(onote["remarks"])
            dialog.extra1_edit.setPlainText(onote["extra1"])
            dialog.extra2_edit.setPlainText(onote["extra2"])
            svg_b64 = svgutils.svgToBase64(onote["fmask"])
            url.addQueryItem('source', svg_b64)

        dialog.tags_edit.setText(onote["tags"])
        dialog.tags_edit.setCol(self.mw.col)
        dialog.sources_edit.setPlainText(onote["sources"])

        dialog.svg_edit.load(url)
        dialog.show()
        dialog.exec_()
        

    def onAddNotesButton(self, choice):
        svg_edit = self.dialog.svg_edit
        svg_contents = svg_edit.page().mainFrame().evaluateJavaScript(
            "svgCanvas.svgCanvasToString();"
            )
        # svg = etree.fromstring(svg_contents.encode('utf-8'))
        svg = svg_contents
        
        mask_fill_color = self.mw.col.conf['image_occlusion_conf']['mask_fill_color']
        (did, tags, header, footer, remarks, sources, 
            extra1, extra2) = self.getUserInputs()

        # Add notes to the current deck of the collection:
        if choice in ["nonoverlapping", "overlapping"]:
            # add_notes_non_overlapping(svg, mask_fill_color,
            #           tags, self.image_path,
            #           header, footer, remarks, sources, 
            #           extra1, extra2, did)
            gen = ImgOccNoteGeneratorHiding(self.ed, self.image_path, svg, tags, header, footer, remarks, sources, extra1, extra2, did)
            gen.generate_notes()
            if self.ed.note:
                # Update Editor with modified tags and sources field
                self.ed.tags.setText(" ".join(tags))
                self.ed.saveTags()
                if IO_FLDS["sources"] in self.ed.note:
                    self.ed.note[IO_FLDS["sources"]] = sources
                    self.ed.loadNote()
        else:
            update_notes(choice, svg, mask_fill_color,
                          tags, self.image_path,
                          header, footer, remarks, sources, 
                          extra1, extra2, did)
        if self.ed.note:
            self.ed.loadNote()
        self.mw.reset()

    def getUserInputs(self):
        header = self.dialog.header_edit.toPlainText().replace('\n', '<br />')
        footer = self.dialog.footer_edit.toPlainText().replace('\n', '<br />')
        remarks = self.dialog.remarks_edit.toPlainText().replace('\n', '<br />')
        sources = self.dialog.sources_edit.toPlainText().replace('\n', '<br />')
        extra1 = self.dialog.extra1_edit.toPlainText().replace('\n', '<br />')
        extra2 = self.dialog.extra2_edit.toPlainText().replace('\n', '<br />')
        did = self.dialog.deckChooser.selectedId()
        tags = self.dialog.tags_edit.text().split()
        return (did, tags, header, footer, remarks, sources, extra1, extra2)


def invoke_io_settings(mw):
    dialog = ImgOccOpts(mw)
    dialog.show()
    dialog.exec_()

def invoke_io_help():
    openLink(io_help_link)

def onImgOccButton(ed, mode):
    ioInstance = ImgOccAdd(ed)
    # note type integrity check
    ioModel = mw.col.models.byName(IO_MODEL_NAME)
    if ioModel:
        ioFields = mw.col.models.fieldNames(ioModel)
        if not all(x in ioFields for x in IO_FLDS.values()):
            showWarning(\
                '<b>Error:</b><br><br>Image Occlusion note type not configured properly.\
                Please make sure you did not delete or rename any of the essential fields.\
                <br><br>You can find more information on this error message here: \
                <a href="' + io_help_link + '/Customization#a-note-of-warning">\
                Wiki - Note Type Customization</a>')
            return
    ioInstance.getImage(mode)

def onSetupEditorButtons(self):
    # Add IO button to Editor
    if self.addMode:
        self._addButton("new_occlusion", lambda o=self: onImgOccButton(self, "add"),
                _("Alt+o"), _("Add Image Occlusion (Alt+O)"), canDisable=False)
    else:
        self._addButton("edit_occlusion", lambda o=self: onImgOccButton(self, "edit"),
                _("Alt+o"), _("Edit Image Occlusion (Alt+O)"), canDisable=False)

def hideIdField(self, node, hide=True, focus=False):
    # simple hack that hides the ID field on IO notes
    if (self.note and self.note.model()["name"] == IO_MODEL_NAME and
            self.note.model()['flds'][0]['name'] == IO_FLDS['uuid']):
        self.web.eval("""
            // hide first fname, field, and snowflake (FrozenFields add-on)
                document.styleSheets[0].addRule(
                    'tr:first-child .fname, #f0, #i0', 'display: none;');
            """ )

# Set up menus
options_action = QAction("Image &Occlusion Enhanced Options...", mw)
help_action = QAction("Image &Occlusion Enhanced Wiki...", mw)
mw.connect(options_action, SIGNAL("triggered()"), 
            lambda o=mw: invoke_io_settings(o))
mw.connect(help_action, SIGNAL("triggered()"),
            invoke_io_help)
mw.form.menuTools.addAction(options_action)
mw.form.menuHelp.addAction(help_action)


# Set up hooks
addHook('setupEditorButtons', onSetupEditorButtons)
Editor.setNote = wrap(Editor.setNote, hideIdField, "after")