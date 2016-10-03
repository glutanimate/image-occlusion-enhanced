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
import sys
import re
import tempfile

from PyQt4 import QtCore, QtGui

from aqt import mw, webview, deckchooser, tagedit
from aqt.editor import Editor
from aqt.utils import tooltip, openLink, showWarning, saveGeom, restoreGeom
from aqt.qt import *
from anki.hooks import wrap, addHook
from anki.utils import json

import etree.ElementTree as etree

import svgutils
from notes_from_svg import add_notes_non_overlapping, add_notes_overlapping
# import the icons
from resources import *

io_help_link = "https://github.com/Glutanimate/image-occlusion-enhanced/wiki"

# get default file system encoding
encoding = sys.getfilesystemencoding()

# set various paths
os_home_dir = os.path.expanduser('~').decode(encoding)
addons_folder = mw.pm.addonFolder().encode('utf-8')
prefs_path = os.path.join(addons_folder, "image_occlusion_enhanced", 
                          ".image_occlusion_prefs").decode('utf-8')

svg_edit_dir = os.path.join(os.path.dirname(__file__),
                            'svg-edit',
                            'svg-edit-2.6')
svg_edit_path = os.path.join(svg_edit_dir,
                            'svg-editor.html')

#Add all configuration options we know at this point:
svg_edit_ext = "ext-image-occlusion.js,ext-arrows.js,ext-markers.js,ext-shapes.js,ext-eyedropper.js"
svg_edit_queryitems = [('initStroke[opacity]', '1'),
                       ('initStroke[color]', '2D2D2D'),
                       ('initStroke[width]', '0'),
                       ('initTool', 'rect'),
                       ('text[font_family]', "'Helvetica LT Std', Arial, sans-serif"),
                       ('extensions', svg_edit_ext)]

IO_MODEL_NAME = "Image Occlusion Enhanced"

default_conf = {'initFill[color]': '00AA7F',
                'mask_fill_color': 'FF0000',
                'io-version': 'enhanced-0.5'}

default_prefs = {"prev_image_dir": os_home_dir}

IO_FLDS = {
    'uuid': "ID (hidden)",
    'header': "Header",
    'image': "Image",
    'footer': "Footer",
    'remarks': "Anmerkungen",
    'sources': "Quellen",
    'extra1': "Extra 1",
    'extra2': "Extra 2",
    'qmask': "Question Mask",
    'amask': "Answer Mask",
    'fmask': "Full Mask"
}

def load_prefs(self):

    # check if synced configuration exists
    if not 'image_occlusion_conf' in mw.col.conf:
        self.mw.col.conf['image_occlusion_conf'] = default_conf

    # upgrade from Image Occlusion 2.0
    self.io_conf = mw.col.conf['image_occlusion_conf']
    if not 'io-version' in self.io_conf:
        # set io version
        self.io_conf['io-version'] = default_conf['io-version']
        # change default colours
        if self.io_conf['initFill[color]'] == "FFFFFF":
            self.io_conf['initFill[color]'] = default_conf['initFill[color]']
            self.io_conf['mask_fill_color'] = default_conf['mask_fill_color']

    # load local preferences
    self.prefs = None
    try:
        with open(prefs_path, "r") as f:
            self.prefs = json.load(f)
    except:
        # file does not exist or is corrupted: fall back to default
        with open(prefs_path, "w") as f:
            self.prefs = default_prefs
            json.dump(self.prefs, f)

def save_prefs(self):
    # save local preferences to disk
    with open(prefs_path, "w") as f:
        json.dump(self.prefs, f)


class ImgOccAdd(QtCore.QObject):
    def __init__(self, ed):
        super(QtCore.QObject, self).__init__()
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
            # retrieve last used image directory
            prev_image_dir = self.prefs["prev_image_dir"]
            # if directory not valid or empty use system home directory
            if not os.path.isdir(prev_image_dir):
                prev_image_dir = os_home_dir     

            clip = QApplication.clipboard()
            if clip.mimeData().imageData():
                handle, image_path = tempfile.mkstemp(suffix='.png')
                clip.image().save(image_path)
                clip.clear()
            else:
                image_path = QtGui.QFileDialog.getOpenFileName(self.ed.parentWindow,
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

        width, height = svgutils.imageProp(self.image_path)
        initFill_color = self.mw.col.conf['image_occlusion_conf']['initFill[color]']
        url = QtCore.QUrl.fromLocalFile(svg_edit_path)
        url.setQueryItems(svg_edit_queryitems)
        url.addQueryItem('initFill[color]', initFill_color)
        url.addQueryItem('dimensions', '{0},{1}'.format(width, height))
        url.addQueryItem('bkgd_url', QtCore.QUrl.fromLocalFile(self.image_path).toString())
            
        if self.mode != "add":
            dialog.header_edit.setPlainText(self.onote["header"])
            dialog.footer_edit.setPlainText(self.onote["footer"])
            dialog.remarks_edit.setPlainText(self.onote["remarks"])
            dialog.extra1_edit.setPlainText(self.onote["extra1"])
            dialog.extra2_edit.setPlainText(self.onote["extra2"])
            svg_b64 = svgutils.svgToBase64(self.onote["fmask"])
            url.addQueryItem('source', svg_b64)

        dialog.tags_edit.setText(self.onote["tags"])
        dialog.tags_edit.setCol(self.mw.col)
        dialog.sources_edit.setPlainText(self.onote["sources"])

        dialog.svg_edit.load(url)
        dialog.show()
        dialog.exec_()
        

    def onAddNotesButton(self, choice):
        svg_edit = self.dialog.svg_edit
        svg_contents = svg_edit.page().mainFrame().evaluateJavaScript(
            "svgCanvas.svgCanvasToString();"
            )
        svg = etree.fromstring(svg_contents.encode('utf-8'))
        
        mask_fill_color = self.mw.col.conf['image_occlusion_conf']['mask_fill_color']
        (did, tags, header, footer, remarks, sources, 
            extra1, extra2) = self.getUserInputs()

        # Add notes to the current deck of the collection:
        if choice in ["nonoverlapping", "overlapping"]:
            # add_notes(choice, svg, mask_fill_color,
            #           tags, self.image_path,
            #           header, footer, remarks, sources, 
            #           extra1, extra2, did)
            add_notes_non_overlapping(svg, mask_fill_color,
                      tags, self.image_path,
                      header, footer, remarks, sources, 
                      extra1, extra2, did)
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

class ImgOccEdit(QDialog):
    def __init__(self, ImgOccAdd, mw):
        QDialog.__init__(self, parent=mw)
        self.mw = mw
        self.ImgOccAdd = ImgOccAdd
        self.mode = self.ImgOccAdd.mode
        self.setupUi()
        restoreGeom(self, "imageOccEditor")


    def closeEvent(self, event):
        if mw.pm.profile is not None:
            saveGeom(self, "imageOccEditor")

    def setupUi(self):
        self.svg_edit = webview.AnkiWebView()
        self.svg_edit.setCanFocus(True) # focus necessary for hotkeys

        self.header_edit = QPlainTextEdit()
        self.header_label = QLabel(IO_FLDS["header"])
        header_hbox = QHBoxLayout()
        header_hbox.addWidget(self.header_label)
        header_hbox.addWidget(self.header_edit)

        self.footer_edit = QPlainTextEdit()
        self.footer_label = QLabel(IO_FLDS["footer"])
        footer_hbox = QHBoxLayout()
        footer_hbox.addWidget(self.footer_label)
        footer_hbox.addWidget(self.footer_edit)

        self.remarks_edit = QPlainTextEdit()
        self.remarks_label = QLabel(IO_FLDS["remarks"])
        remarks_hbox = QHBoxLayout()
        remarks_hbox.addWidget(self.remarks_label)
        remarks_hbox.addWidget(self.remarks_edit)

        self.sources_edit = QPlainTextEdit()
        self.sources_label = QLabel(IO_FLDS["sources"])
        sources_hbox = QHBoxLayout()
        sources_hbox.addWidget(self.sources_label)
        sources_hbox.addWidget(self.sources_edit)

        self.extra1_edit = QPlainTextEdit()
        self.extra1_label = QLabel(IO_FLDS["extra1"])
        extra1_hbox = QHBoxLayout()
        extra1_hbox.addWidget(self.extra1_label)
        extra1_hbox.addWidget(self.extra1_edit)

        self.extra2_edit = QPlainTextEdit()
        self.extra2_label = QLabel(IO_FLDS["extra2"])
        extra2_hbox = QHBoxLayout()
        extra2_hbox.addWidget(self.extra2_label)
        extra2_hbox.addWidget(self.extra2_edit)

        self.tags_edit = tagedit.TagEdit(self)
        self.tags_label = QLabel("Tags")
        tags_hbox = QHBoxLayout()
        tags_hbox.addWidget(self.tags_label)
        tags_hbox.addWidget(self.tags_edit)

        deck_container = QGroupBox()
        self.deckChooser = deckchooser.DeckChooser(mw, deck_container,
                                                   label=True) 

        for i in [self.header_edit, self.footer_edit, self.remarks_edit, 
            self.sources_edit, self.extra1_edit, self.extra2_edit]:
            i.setTabChangesFocus(True)

        for i in [self.header_label, self.footer_label, self.remarks_label, 
            self.sources_label, self.extra1_label, self.extra2_label, self.tags_label]:
            i.setFixedWidth(70)        

        # Set layout up

        ## Tab 1
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.svg_edit, stretch=1)

        ## Tab 2
        vbox2 = QVBoxLayout()
        vbox2.addLayout(header_hbox)
        vbox2.addLayout(footer_hbox)
        vbox2.addLayout(remarks_hbox)
        vbox2.addLayout(sources_hbox)
        vbox2.addLayout(extra1_hbox)
        vbox2.addLayout(extra2_hbox)
        vbox2.addLayout(tags_hbox)
        vbox2.addWidget(deck_container)

        # Create tabs, set their layout, add them to the QTabWidget

        ## set Tabs up
        tab1 = QWidget()
        tab2 = QWidget()

        ## set Tab layout
        tab1.setLayout(vbox1)
        tab2.setLayout(vbox2)

        ## set Tab widget up
        self.tab_widget = QtGui.QTabWidget() 

        ## add Tabs to QTabWidget
        self.tab_widget.addTab(tab1,"Masks &Editor")
        self.tab_widget.addTab(tab2,"&Fields")

        self.tab_widget.setTabToolTip(1, "Include additional information (optional)")
        self.tab_widget.setTabToolTip(0, "Create image occlusion masks (required)")

        # Create buttons

        ## Set up buttons

        button_box = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        button_box.setCenterButtons(True)
        if self.mode == "add":
            # Regular mode
            nonoverlapping_button = button_box.addButton("Add &nonoverlapping occlusions",
                    QDialogButtonBox.ActionRole)
            nonoverlapping_button.setToolTip(
                "Generate cards where all labels are hidden on each card")
            overlapping_button = button_box.addButton("Add &overlapping occlusions",
                    QDialogButtonBox.ActionRole)
            overlapping_button.setToolTip(
                "Generate cards where only one label is hidden per card")

        else:
            # Editing mode
            edit1_button = button_box.addButton("&Edit notes",
                    QDialogButtonBox.ActionRole)
            edit2_button = button_box.addButton("Edit and &switch type",
                    QDialogButtonBox.ActionRole)
            nonoverlapping_button = button_box.addButton("New &nonoverlapping notes",
                    QDialogButtonBox.ActionRole)
            overlapping_button = button_box.addButton("New &overlapping notes",
                    QDialogButtonBox.ActionRole)
            self.connect(edit1_button, SIGNAL("clicked()"), self.edit)
            self.connect(edit2_button, SIGNAL("clicked()"), self.edit_and_switch)

        close_button = button_box.addButton("&Close",
                QDialogButtonBox.ActionRole)
        close_button.setToolTip("Close Image Occlusion Editor without generating cards")
        self.connect(nonoverlapping_button, SIGNAL("clicked()"), self.add_nonoverlapping)
        self.connect(overlapping_button, SIGNAL("clicked()"), self.add_overlapping)
        self.connect(close_button, SIGNAL("clicked()"), self.close)

        # Add all widgets to main window
        ## set widget layout up
        vbox_main = QtGui.QVBoxLayout()
        vbox_main.setMargin(0);
        ## add widgets
        vbox_main.addWidget(self.tab_widget)
        vbox_main.addWidget(button_box)
        ## apply to main window
        self.setLayout(vbox_main)

        # Set basic window properties
        # self.setMinimumHeight(600)
        self.setWindowTitle('Image Occlusion Enhanced Editor')

        # Define and connect key bindings
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_Tab), self), 
            QtCore.SIGNAL('activated()'), self.switch_tabs)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_R), self), 
            QtCore.SIGNAL('activated()'), self.reset_main_fields)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_R), self), 
            QtCore.SIGNAL('activated()'), self.reset_all_fields)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_1), self), 
            QtCore.SIGNAL('activated()'), lambda:self.focus_field(self.header_edit))
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_2), self), 
            QtCore.SIGNAL('activated()'), lambda:self.focus_field(self.footer_edit))
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_3), self), 
            QtCore.SIGNAL('activated()'), lambda:self.focus_field(self.remarks_edit))
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_4), self), 
            QtCore.SIGNAL('activated()'), lambda:self.focus_field(self.sources_edit))
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_5), self), 
            QtCore.SIGNAL('activated()'), lambda:self.focus_field(self.extra1_edit))
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_6), self), 
            QtCore.SIGNAL('activated()'), lambda:self.focus_field(self.extra2_edit))
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_D), self), 
            QtCore.SIGNAL('activated()'), deck_container.setFocus)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_T), self), 
            QtCore.SIGNAL('activated()'), lambda:self.focus_field(self.tags_edit))
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_I), self), 
            QtCore.SIGNAL('activated()'), self.svg_edit.setFocus)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_F), self), 
            QtCore.SIGNAL('activated()'), self.fit_image_canvas)

        # Set Focus
        self.tab_widget.setCurrentIndex(0)
        self.svg_edit.setFocus()

    # keybinding related functions

    ## Notes
    def add_nonoverlapping(self): 
        self.ImgOccAdd.onAddNotesButton("nonoverlapping")
    def add_overlapping(self): 
        self.ImgOccAdd.onAddNotesButton("overlapping")
    def edit(self):
        self.ImgOccAdd.onAddNotesButton("edit")
    def edit_and_switch(self):
        self.ImgOccAdd.onAddNotesButton("edit_and_switch")

    ## Navigation, etc.
    def switch_tabs(self):
        currentTab = self.tab_widget.currentIndex()
        if currentTab == 0:
          self.tab_widget.setCurrentIndex(1)
          if isinstance(QApplication.focusWidget(), QPushButton):
              self.header_edit.setFocus()
        else:
          self.tab_widget.setCurrentIndex(0)

    def focus_field(self, target_field):
        self.tab_widget.setCurrentIndex(1)
        target_field.setFocus()

    def reset_main_fields(self):
        for i in [self.header_edit, self.footer_edit, self.remarks_edit, 
          self.extra1_edit, self.extra2_edit]:
            i.setPlainText("")

    def reset_all_fields(self):
        self.reset_main_fields()
        self.sources_edit.setPlainText("")

    def fit_image_canvas(self):
        command = "svgCanvas.zoomChanged('', 'canvas');"
        self.svg_edit.eval(command)
        

class ImageOcc_Options(QDialog):
    # Main IO Options dialog
    def __init__(self, mw):
        QDialog.__init__(self, parent=mw)
        self.mw = mw
        self.setupUi()

    def getNewMaskColor(self):
        # Remove the # sign from QColor.name():
        choose_color_dialog = QColorDialog()
        color = choose_color_dialog.getColor()
        if color.isValid():
            color_ = color.name()[1:]
            self.mw.col.conf['image_occlusion_conf']['mask_fill_color'] = color_
            # notify db of modification
            self.mw.col.setMod()
            self.changeButtonColor(self.mask_color_button, color_)

    def getNewInitFillColor(self):
        # Remove the # sign from QColor.name():
        choose_color_dialog = QColorDialog()
        color = choose_color_dialog.getColor()
        if color.isValid():
            color_ = color.name()[1:]
            self.mw.col.conf['image_occlusion_conf']['initFill[color]'] = color_
            # notify db of modification
            self.mw.col.setMod()
            self.changeButtonColor(self.initFill_button, color_)

    def changeButtonColor(self, button, color):
        pixmap = QPixmap(128,18)
        qcolour = QtGui.QColor(0, 0, 0)
        qcolour.setNamedColor("#" + color)
        pixmap.fill(qcolour)
        button.setIcon(QIcon(pixmap))
        button.setIconSize(QSize(128, 18))

    def setupUi(self):
        # load preferences
        load_prefs(self)

        ### shape color for questions:
        mask_color_label = QLabel('<b>Question</b> shape color')
        self.mask_color_button = QPushButton()
        self.mask_color_button.connect(self.mask_color_button,
                                  SIGNAL("clicked()"),
                                  self.getNewMaskColor)
        ### Initial shape color:
        initFill_label = QLabel('<b>Initial</b> shape color')
        self.initFill_button = QPushButton()
        self.initFill_button.connect(self.initFill_button,
                                SIGNAL("clicked()"),
                                self.getNewInitFillColor)

        ### set colors
        initFill_color = self.mw.col.conf['image_occlusion_conf']['initFill[color]']
        mask_fill_color = self.mw.col.conf['image_occlusion_conf']['mask_fill_color']
        self.changeButtonColor(self.initFill_button, initFill_color)
        self.changeButtonColor(self.mask_color_button, mask_fill_color)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        # 1st row:
        grid.addWidget(mask_color_label, 0, 0)
        grid.addWidget(self.mask_color_button, 0, 1)
        # 2nd row:
        grid.addWidget(initFill_label, 1, 0)
        grid.addWidget(self.initFill_button, 1, 1)

        self.setLayout(grid)
        self.setMinimumWidth(400)
        self.setWindowTitle('Image Occlusion Enhanced Options')

def invoke_io_settings(mw):
    dialog = ImageOcc_Options(mw)
    dialog.show()
    dialog.exec_()

def invoke_io_help():
    openLink(io_help_link)

def onImgOccButton(ed, mode):
    ioInstance = ImgOccAdd(ed)
    # note type integrity check
    nm = mw.col.models.byName(IO_MODEL_NAME)
    if nm:
        nm_fields = mw.col.models.fieldNames(nm)
        if not all(x in nm_fields for x in IO_FLDS.values()):
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
    if self.note and self.note.model()["name"] == IO_MODEL_NAME:
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