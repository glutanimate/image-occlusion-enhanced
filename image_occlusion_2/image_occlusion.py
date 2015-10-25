# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from aqt import mw, utils, webview
from aqt.qt import *
from anki import hooks
from aqt import deckchooser
from aqt import tagedit
from anki.utils import json

import os
import tempfile

import etree.ElementTree as etree

import svgutils
from notes_from_svg import add_notes_non_overlapping, add_notes_overlapping
from config import SVG_EDIT_VERSION
# import the icons
from resources import *

image_occlusion_help_link = "http://tmbb.bitbucket.org/image-occlusion-2.html"

# set various paths
os_home_dir = os.path.expanduser('~')

addons_folder = mw.pm.addonFolder()

prefs_path = os.path.join(addons_folder, "image_occlusion_2", ".image_occlusion_2_prefs")

svg_edit_dir = os.path.join(os.path.dirname(__file__),
                            'svg-edit',
                            SVG_EDIT_VERSION)

#ext_image_occlusion_js_path = os.path.join(svg_edit_dir,
#                                           'extensions',
#                                           'ext-image-occlusion.js')

#unedited_svg_basename = "-IMAGE-OCCLUSION-SVG-.svg"

#unedited_svg_path = os.path.join(svg_edit_dir,
#                             'images',
#                             unedited_svg_basename)

#unedited_svg_url = 'images/' + unedited_svg_basename

svg_edit_path = os.path.join(svg_edit_dir,
                             'svg-editor.html')


svg_edit_url = QtCore.QUrl.fromLocalFile(svg_edit_path)
svg_edit_url_string = svg_edit_url.toString()

#Add all configuration options we know at this point:
svg_edit_url.setQueryItems([('initStroke[opacity]', '0'),
                            ('initStroke[width]', '0'),
                            ('initTool', 'rect'),
                            ('extensions', 'ext-image-occlusion.js')])

FILE_DIALOG_MESSAGE = "Choose Image"
FILE_DIALOG_FILTER = "Image Files (*.png *jpg *.jpeg *.gif)"

default_conf = {'initFill[color]': 'FFFFFF',
                'mask_fill_color': 'FF0000'}

default_prefs = {"prev_image_dir": os_home_dir}


def load_prefs(self):
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


class ImageOcc_Add(QtCore.QObject):
    def __init__(self, ed):
        super(QtCore.QObject, self).__init__()
        self.ed = ed
        self.mw = mw

        # check if config exists
        if not 'image_occlusion_conf' in mw.col.conf:
            # If addon has never been run
            self.mw.col.conf['image_occlusion_conf'] = default_conf

        # load preferences
        load_prefs(self)

    def add_notes(self):

        # retrieve last used image directory
        prev_image_dir = self.prefs["prev_image_dir"]
        # if directory not valid or empty use system home directory
        if not os.path.isdir(prev_image_dir):
            prev_image_dir = os_home_dir   

        clip = QApplication.clipboard()
        if clip.mimeData().imageData():
            handle, image_path = tempfile.mkstemp(suffix='.png')
            clip.image().save(image_path)
            self.mw.image_occlusion2_image_path = image_path
            clip.clear()
            #  Simple hack to catch an error. I still don't know
            # the cause of the error.
            try:
                self.call_ImageOcc_Editor(self.mw.image_occlusion2_image_path)
            except:
                image_path = QtGui.QFileDialog.getOpenFileName(None,  # parent
                                                      FILE_DIALOG_MESSAGE,
                                                      prev_image_dir,
                                                      FILE_DIALOG_FILTER)

        else:
            image_path = QtGui.QFileDialog.getOpenFileName(None,  # parent
                                                       FILE_DIALOG_MESSAGE,
                                                       prev_image_dir,
                                                       FILE_DIALOG_FILTER)

        # The following code is common to both branches of the 'if'
        if image_path:
            self.mw.image_occlusion2_image_path = image_path
            # store image directory in local preferences
            self.prefs["prev_image_dir"] = os.path.dirname( image_path )
            save_prefs(self)
            self.call_ImageOcc_Editor(self.mw.image_occlusion2_image_path)

    def call_ImageOcc_Editor(self, path):
        d = svgutils.image2svg(path)
        svg = d['svg']
        svg_b64 = d['svg_b64']
        height = d['height']
        width = d['width']

        try:
            mw.ImageOcc_Editor is not None
            select_rect_tool = "svgCanvas.setMode('rect'); "
            set_svg_content = 'svg_content = \'%s\'; ' % svg.replace('\n', '')
            set_canvas = 'svgCanvas.setSvgString(svg_content);'
            set_zoom = "svgCanvas.zoomChanged('', 'canvas');"

            command = select_rect_tool + set_svg_content + set_canvas + set_zoom

            mw.ImageOcc_Editor.svg_edit.eval(command)
            mw.ImageOcc_Editor.show()

        except:
            initFill_color = mw.col.conf['image_occlusion_conf']['initFill[color]']
            url = svg_edit_url
            url.addQueryItem('initFill[color]', initFill_color)
            url.addQueryItem('dimensions', '{0},{1}'.format(width, height))
            url.addQueryItem('source', svg_b64)

            tags = self.ed.note.tags
            mw.ImageOcc_Editor = ImageOcc_Editor(tags)

            mw.ImageOcc_Editor.svg_edit.\
                               page().\
                               mainFrame().\
                               addToJavaScriptWindowObject("pyObj", self)
            mw.ImageOcc_Editor.svg_edit.load(url)
            mw.ImageOcc_Editor.show()

    @QtCore.pyqtSlot(str)
    def add_notes_non_overlapping(self, svg_contents):
        svg = etree.fromstring(svg_contents.encode('utf-8'))
        mask_fill_color, did, tags, header, footer = get_params_for_add_notes()
        # Add notes to the current deck of the collection:
        add_notes_non_overlapping(svg, mask_fill_color,
                                  tags, self.mw.image_occlusion2_image_path,
                                  header, footer, did)

    @QtCore.pyqtSlot(str)
    def add_notes_overlapping(self, svg_contents):
        svg = etree.fromstring(svg_contents.encode('utf-8'))
        mask_fill_color, did, tags, header, footer = get_params_for_add_notes()
        # Add notes to the current deck of the collection:
        add_notes_overlapping(svg, mask_fill_color,
                              tags, self.mw.image_occlusion2_image_path,
                              header, footer, did)


def get_params_for_add_notes():
    # Get the mask color from mw.col.conf:
    mask_fill_color = mw.col.conf['image_occlusion_conf']['mask_fill_color']

    header = mw.ImageOcc_Editor.header_edit.text()
    footer = mw.ImageOcc_Editor.footer_edit.text()
    # Get deck id:
    did = mw.ImageOcc_Editor.deckChooser.selectedId()
    tags = mw.ImageOcc_Editor.tags_edit.text().split()
    return (mask_fill_color, did, tags, header, footer)


def add_image_occlusion_button(ed):
    ed.image_occlusion = ImageOcc_Add(ed)
    ed._addButton("new_occlusion", ed.image_occlusion.add_notes,
            _("Alt+o"), _("Image Occlusion (Alt+o)"),
            canDisable=False)


class ImageOcc_Editor(QWidget):
    def __init__(self, tags):
        super(ImageOcc_Editor, self).__init__()
        self.initUI(tags)

    def initUI(self, tags):
        ##############################################
        ### From top to bottom:
        ##############################################
        ## header_label # self.header_edit
        ##############################################
        ## self.svg_edit
        ##############################################
        ## footer_label # self.footer
        ##############################################
        ## tags_label # self.tags_edit
        ##############################################
        ## deck_container
        ##  ########################
        ##  # deckChooser          #
        ##  ########################
        ##############################################

        # Header
        self.header_edit = QLineEdit()
        self.header_edit.setPlaceholderText("(optional)")
        header_label = QLabel("Header: ")

        header_hbox = QHBoxLayout()
        header_hbox.addWidget(header_label)
        header_hbox.addWidget(self.header_edit)

        # svg-edit
        self.svg_edit = webview.AnkiWebView()
        self.svg_edit.setCanFocus(True)

        # Footer
        self.footer_edit = QLineEdit()
        self.footer_edit.setPlaceholderText("(optional)")
        footer_label = QLabel("Footer: ")

        footer_hbox = QHBoxLayout()
        footer_hbox.addWidget(footer_label)
        footer_hbox.addWidget(self.footer_edit)

        # Tags
        self.tags_edit = tagedit.TagEdit(self)
        self.tags_edit.setText(" ".join(tags))
        self.tags_edit.setCol(mw.col)
        tags_label = QLabel("Tags: ")

        tags_hbox = QHBoxLayout()
        tags_hbox.addWidget(tags_label)
        tags_hbox.addWidget(self.tags_edit)

        deck_container = QGroupBox("Deck")

        self.deckChooser = deckchooser.DeckChooser(mw, deck_container,
                                                   label=False)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(header_hbox)
        vbox.addWidget(self.svg_edit)
        vbox.addLayout(footer_hbox)
        vbox.addLayout(tags_hbox)
        vbox.addWidget(deck_container)

        self.setLayout(vbox)
        self.setMinimumHeight(600)

        #  Don't focus on the tags.
        #  When the focus is on the tags an ugly autocomplete
        # list appears, taking away screen real estate for no reason.
        self.header_edit.setFocus()

        # define and connect key bindings

        # CTRL+F - fit to canvas
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_F), self), 
            QtCore.SIGNAL('activated()'), self.fit_image_canvas)
        # CTRL+1 - focus header field
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_1), self), 
            QtCore.SIGNAL('activated()'), self.header_edit.setFocus)
        # CTRL+2 - focus footer field
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_2), self), 
            QtCore.SIGNAL('activated()'), self.footer_edit.setFocus)
        # CTRL+I - focus SVG-Edit
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_I), self), 
            QtCore.SIGNAL('activated()'), self.svg_edit.setFocus)
        # CTRL+T - focus tags field
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_T), self), 
            QtCore.SIGNAL('activated()'), self.tags_edit.setFocus)
        # CTRL+R - reset all fields
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_R), self), 
            QtCore.SIGNAL('activated()'), self.reset_all_fields)
        # CTRL + O - add overlapping note
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_O), self), 
            QtCore.SIGNAL('activated()'), self.add_overlapping)
        # CTRL + N - add non-overlapping note
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_N), self), 
            QtCore.SIGNAL('activated()'), self.add_nonoverlapping)
        # Escape - Close Image Occlusion window
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.Key_Escape), self), 
            QtCore.SIGNAL('activated()'), self.close)

        self.setWindowTitle('Image Occlusion Editor')
        self.show()

    # functions related to key-bindings

    def fit_image_canvas(self):
        command = "svgCanvas.zoomChanged('', 'canvas');"
        self.svg_edit.eval(command)
    def add_nonoverlapping(self): 
        command = "var svg_contents = svgCanvas.svgCanvasToString(); pyObj.add_notes_non_overlapping(svg_contents);"
        self.svg_edit.eval(command)
    def add_overlapping(self): 
        command = "var svg_contents = svgCanvas.svgCanvasToString(); pyObj.add_notes_overlapping(svg_contents);"
        self.svg_edit.eval(command) 
    def reset_all_fields(self):
        self.header_edit.setText("")
        self.footer_edit.setText("")


class ImageOcc_Options(QtGui.QWidget):
    def __init__(self, mw):
        super(ImageOcc_Options, self).__init__()
        self.mw = mw

    def getNewMaskColor(self):
        # Remove the # sign from QColor.name():
        choose_color_dialog = QColorDialog()
        color = choose_color_dialog.getColor()
        if color.isValid():
            color_ = color.name()[1:]
            self.mw.col.conf['image_occlusion_conf']['mask_fill_color'] = color_

    def getNewInitFillColor(self):
        # Remove the # sign from QColor.name():
        choose_color_dialog = QColorDialog()
        color = choose_color_dialog.getColor()
        if color.isValid():
            color_ = color.name()[1:]
            self.mw.col.conf['image_occlusion_conf']['initFill[color]'] = color_

    def setupUi(self):

        ### Mask color for questions:
        mask_color_label = QLabel('<b>Mask color</b><br>in question')

        mask_color_button = QPushButton(u"Choose Color ▾")

        mask_color_button.connect(mask_color_button,
                                  SIGNAL("clicked()"),
                                  self.getNewMaskColor)
        ### Initial rectangle color:
        initFill_label = QLabel('<b>Initial color</b><br>for rectangle')

        initFill_button = QPushButton(u"Choose Color ▾")

        initFill_button.connect(initFill_button,
                                SIGNAL("clicked()"),
                                self.getNewInitFillColor)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        # 1st row:
        grid.addWidget(mask_color_label, 0, 0)
        grid.addWidget(mask_color_button, 0, 1)
        # 2nd row:
        grid.addWidget(initFill_label, 1, 0)
        grid.addWidget(initFill_button, 1, 1)

        self.setLayout(grid)

        self.setWindowTitle('Image Occlusion 2.0 (options)')
        self.show()


def invoke_ImageOcc_help():
    utils.openLink(image_occlusion_help_link)

mw.ImageOcc_Options = ImageOcc_Options(mw)

options_action = QAction("Image Occlusion 2.0 (options)", mw)
help_action = QAction("Image Occlusion 2.0 (help)", mw)

mw.connect(options_action,
           SIGNAL("triggered()"),
           mw.ImageOcc_Options.setupUi)

mw.connect(help_action,
           SIGNAL("triggered()"),
           invoke_ImageOcc_help)

mw.form.menuTools.addAction(options_action)
mw.form.menuHelp.addAction(help_action)

hooks.addHook('setupEditorButtons', add_image_occlusion_button)


