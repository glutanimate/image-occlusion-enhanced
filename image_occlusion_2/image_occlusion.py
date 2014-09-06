# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui, QtWebKit
from aqt import mw, utils, webview
from aqt.qt import *
from anki import hooks
from aqt import deckchooser
from aqt import tagedit
import aqt.forms

import os
import base64
import tempfile
import socket
import sys


def addons_folder(): return mw.pm.addonFolder() 

import etree.ElementTree as etree

import svgutils
import notes_from_svg
# import the icons
from resources import *

image_occlusion_help_link = "http://tmbb.bitbucket.org/image-occlusion-2.html"

svg_edit_dir = os.path.join(addons_folder(),
                             'image_occlusion_2',
                             'svg-edit')

ext_image_occlusion_js_path = os.path.join(svg_edit_dir,
                                           'extensions',
                                           'ext-image-occlusion.js')

unedited_svg_basename = "-IMAGE-OCCLUSION-SVG-.svg"

unedited_svg_path = os.path.join(svg_edit_dir,
                             'images',
                             unedited_svg_basename)

unedited_svg_url = 'images/' + unedited_svg_basename

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

class ImageOcc_Add(QtCore.QObject):
    def __init__(self, ed):
        super(QtCore.QObject, self).__init__()
        self.ed = ed
        self.mw = mw
        if not 'image_occlusion_conf' in mw.col.conf: # If addon has never been run
            self.mw.col.conf['image_occlusion_conf'] = default_conf
    
    
    def add_notes(self):
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
                image_path = QtGui.QFileDialog.getOpenFileName(None, # parent
                                                      FILE_DIALOG_MESSAGE,
                                                      os.path.expanduser('~'),
                                                      FILE_DIALOG_FILTER)
        
        else:
            image_path = QtGui.QFileDialog.getOpenFileName(None, # parent
                                                       FILE_DIALOG_MESSAGE,
                                                       os.path.expanduser('~'),
                                                       FILE_DIALOG_FILTER)
        
        # The following code is common to both branches of the 'if'
        if image_path:
            self.mw.image_occlusion2_image_path = image_path
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
            set_svg_content = 'svg_content = \'%s\'; ' % svg.replace('\n','')
            set_canvas = 'svgCanvas.setSvgString(svg_content);'
            
            command = select_rect_tool + set_svg_content + set_canvas
            
            mw.ImageOcc_Editor.svg_edit.eval(command)
            mw.ImageOcc_Editor.show()

        except:
            initFill_color = mw.col.conf['image_occlusion_conf']['initFill[color]']
            url = svg_edit_url
            url.addQueryItem('initFill[color]', initFill_color)
            url.addQueryItem('dimensions', '{0},{1}'.format(width,height))
            url.addQueryItem('source', svg_b64)
            
            tags = self.ed.note.tags
            mw.ImageOcc_Editor = ImageOcc_Editor(tags)
            
            mw.ImageOcc_Editor.svg_edit.page().mainFrame().addToJavaScriptWindowObject("pyObj", self)
            mw.ImageOcc_Editor.svg_edit.load(url)            
            mw.ImageOcc_Editor.show()

    
    @QtCore.pyqtSlot(str)
    def add_notes_non_overlapping(self, svg_contents):
        svg = etree.fromstring(svg_contents.encode('utf-8'))
        mask_fill_color, did, tags, header, footer = get_params_for_add_notes()
        # Add notes to the current deck of the collection:
        notes_from_svg.add_notes_non_overlapping(svg, mask_fill_color,
                                                 tags, self.mw.image_occlusion2_image_path,
                                                 header, footer, did)
    
    @QtCore.pyqtSlot(str)
    def add_notes_overlapping(self, svg_contents):
        svg = etree.fromstring(svg_contents.encode('utf-8'))
        mask_fill_color, did, tags, header, footer = get_params_for_add_notes()
        # Add notes to the current deck of the collection:
        notes_from_svg.add_notes_overlapping(svg, mask_fill_color,
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
            key="Alt+o", size=False, #text=_("Image Occlusion"),
            native=True, canDisable=False)

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
        
        self.setWindowTitle('Image Occlusion Editor')
        self.show()

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


