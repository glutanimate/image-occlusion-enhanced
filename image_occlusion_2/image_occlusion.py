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

from aqt import mw, utils, webview, deckchooser, tagedit
from aqt.qt import *
from anki import hooks
from anki.utils import json

import etree.ElementTree as etree

import svgutils
from notes_from_svg import add_notes_non_overlapping, add_notes_overlapping
# import the icons
from resources import *

image_occlusion_help_link = "https://github.com/Glutanimate/image-occlusion-enhanced/wiki"

# get default file system encoding
encoding = sys.getfilesystemencoding()

# set various paths
os_home_dir = os.path.expanduser('~').decode(encoding)
addons_folder = mw.pm.addonFolder().encode('utf-8')
prefs_path = os.path.join(addons_folder, "image_occlusion_2", 
                          ".image_occlusion_2_prefs").decode('utf-8')

svg_edit_dir = os.path.join(os.path.dirname(__file__),
                            'svg-edit',
                            'svg-edit-2.6')
svg_edit_path = os.path.join(svg_edit_dir,
                            'svg-editor.html')
svg_edit_url = QtCore.QUrl.fromLocalFile(svg_edit_path)
svg_edit_url_string = svg_edit_url.toString()

#Add all configuration options we know at this point:
svg_edit_extensions = "ext-image-occlusion.js,ext-arrows.js,ext-markers.js,ext-shapes.js,ext-eyedropper.js"
svg_edit_url.setQueryItems([('initStroke[opacity]', '1'),
                            ('initStroke[color]', '2D2D2D'),
                            ('initStroke[width]', '0'),
                            ('initTool', 'rect'),
                            ('text[font_family]', 'sans-serif'),
                            ('extensions', svg_edit_extensions)])

FILE_DIALOG_MESSAGE = "Choose Image"
FILE_DIALOG_FILTER = "Image Files (*.png *jpg *.jpeg *.gif)"

IMAGE_QA_MODEL_NAME = "Image Q/A - 2.0 Enhanced"

default_conf = {'initFill[color]': '00AA7F',
                'mask_fill_color': 'FF0000',
                'io-version': '2.0-enhanced'}

default_prefs = {"prev_image_dir": os_home_dir}


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


class ImageOcc_Add(QtCore.QObject):

    def __init__(self, ed):
        super(QtCore.QObject, self).__init__()
        self.ed = ed
        self.mw = mw

        global header_field
        global footer_field
        global remarks_field
        global sources_field

        self.reuse_note = False

        # load preferences
        load_prefs(self)

    def add_notes(self):
        # retrieve field names
        global header_field
        global footer_field
        global remarks_field
        global sources_field
        nm = self.mw.col.models.byName(IMAGE_QA_MODEL_NAME)
        if nm:
            try:
                nm_fields = self.mw.col.models.fieldNames(nm)
                header_field = nm_fields[4]
                footer_field = nm_fields[5]
                remarks_field = nm_fields[6]
                sources_field = nm_fields[7]
            except IndexError:
                utils.showWarning(\
                    'Error: Image Occlusion note type not configured properly.\
                    <br> Please make sure you did not delete or reposition any fields.\
                    <br> More information: \
                    <a href="' + image_occlusion_help_link + '/Customization#fixing-a-broken-note-type-or-template">\
                    Wiki - Note Type Customization</a>')
                return
        else:
            header_field = "Header"
            footer_field = "Footer"
            remarks_field = "Remarks"
            sources_field = "Sources"

        # retrieve last used image directory
        prev_image_dir = self.prefs["prev_image_dir"]
        # if directory not valid or empty use system home directory
        if not os.path.isdir(prev_image_dir):
            prev_image_dir = os_home_dir     

        clip = QApplication.clipboard()

        existing_image = False

        orig_tags = None
        orig_svg = None
        orig_svg_path = None
        orig_image = None
        orig_header = None
        orig_footer = None
        orig_remarks = None
        orig_sources = None
        orig_tempfield3 = None
        orig_tempfield4 = None
        orig_tempfield5 = None

        # preserve tags and sources if available
        orig_tags = self.ed.tags.text()
        if sources_field in self.ed.note:
            orig_sources = self.ed.note[sources_field]

        # if current note is Image Occlusion note try to copy all available fields
        model_name = self.ed.note.model()["name"]
        if model_name == IMAGE_QA_MODEL_NAME:
            orig_svg = self.ed.note.fields[2]
            orig_image = self.ed.note.fields[3]
            orig_header = self.ed.note.fields[4].replace('<br />', '\n')
            orig_footer = self.ed.note.fields[5].replace('<br />', '\n')
            orig_remarks = self.ed.note.fields[6].replace('<br />', '\n')
            orig_sources = self.ed.note.fields[7].replace('<br />', '\n')
            orig_tempfield3 = self.ed.note.fields[8].replace('<br />', '\n')
            orig_tempfield4 = self.ed.note.fields[9].replace('<br />', '\n')
            orig_tempfield5 = self.ed.note.fields[10].replace('<br />', '\n')
            patt = r"""<img.*?src=(["'])(.*?)\1"""
            pattern = re.compile(patt, flags=re.I|re.M|re.S)    
            m = pattern.search(orig_image)
            n = pattern.search(orig_svg)
            image_path = None
            svg_path = None
            if(m):
                imagename = m.group(2)
                valid_ext = imagename.endswith((".jpg",".jpeg",".gif",".png"))
                image_path_old = os.path.join(mw.col.media.dir(),m.group(2))
                if valid_ext and os.path.isfile(image_path_old):
                    image_path = image_path_old
            if(n):
                svgname = n.group(2)
                valid_ext = svgname.endswith(".svg")
                svg_path_old = os.path.join(mw.col.media.dir(),n.group(2))
                if valid_ext and os.path.isfile(svg_path_old):
                    orig_svg_path = svg_path_old

            if image_path and orig_svg_path:
               self.reuse_note = True


        # Decide on what image source to use

        # 1: create new IO note based on existing one
        if self.reuse_note == True:
            pass

        # 2: use first image found in note, regardless of note type
        elif existing_image:
            print "Yet to be implemented"
        
        # 3: use clipboard data for note
        elif clip.mimeData().imageData():
            handle, image_path = tempfile.mkstemp(suffix='.png')
            clip.image().save(image_path)
            self.mw.image_occlusion2_image_path = image_path
            clip.clear()
            #  Simple hack to catch an error. I still don't know
            #  the cause of the error (tmbb).
            try:
                self.call_ImageOcc_Editor(self.mw.image_occlusion2_image_path, orig_tags, 
                                          orig_header, orig_footer, orig_remarks, orig_sources, 
                                          orig_svg_path)
            except:
                image_path = QtGui.QFileDialog.getOpenFileName(None,  # parent
                                                      FILE_DIALOG_MESSAGE,
                                                      prev_image_dir,
                                                      FILE_DIALOG_FILTER)

        # 4: prompt user to select image
        else:
            image_path = QtGui.QFileDialog.getOpenFileName(None,  # parent
                                                       FILE_DIALOG_MESSAGE,
                                                       prev_image_dir,
                                                       FILE_DIALOG_FILTER)
       


        # Call Image Occlusion Editor on path
        if image_path:
            self.mw.image_occlusion2_image_path = image_path
            # store image directory in local preferences,
            # but only if image not in the media collection or temporary directory
            if os.path.dirname(image_path) not in [mw.col.media.dir(), tempfile.gettempdir()]:
                self.prefs["prev_image_dir"] = os.path.dirname( image_path )
                save_prefs(self)

            self.call_ImageOcc_Editor(self.mw.image_occlusion2_image_path, orig_tags,
                                      orig_header, orig_footer, orig_remarks, orig_sources, 
                                      orig_svg_path)

    def call_ImageOcc_Editor(self, path, orig_tags, orig_header, orig_footer, 
                             orig_remarks, orig_sources, orig_svg_path):

        d = svgutils.image2svg(path, orig_svg_path)
        svg = d['svg']
        svg_b64 = d['svg_b64']
        height = d['height']
        width = d['width']

        # existing instance of I/O Editor
        ## TODO: understand why we don't just launch a new instance each time I/O is invoked
        try:
            mw.ImageOcc_Editor is not None
            select_rect_tool = "svgCanvas.setMode('rect'); "
            set_svg_content = 'svg_content = \'%s\'; ' % svg.replace('\n', '')
            set_canvas = 'svgCanvas.setSvgString(svg_content);'
            set_zoom = "svgCanvas.zoomChanged('', 'canvas');"

            command = select_rect_tool + set_svg_content + set_canvas + set_zoom
            mw.ImageOcc_Editor.svg_edit.eval(command)

            # update pyobj with new instance
            ## this is necessary for instance variables (e.g. self.reuse_note) to get 
            ## updated properly in the add_notes_* functions.
            ## TODO: understand what's going on and find a better solution
            mw.ImageOcc_Editor.svg_edit.\
                               page().\
                               mainFrame().\
                               addToJavaScriptWindowObject("pyObj", self)

            # always copy tags over
            mw.ImageOcc_Editor.tags_edit.setText(orig_tags)
            # only copy sources field if not undefined
            if orig_sources is not None:
                mw.ImageOcc_Editor.sources_edit.setPlainText(orig_sources)
            # reuse fields if started from existing i/o note
            if self.reuse_note:
                mw.ImageOcc_Editor.header_edit.setPlainText(orig_header)
                mw.ImageOcc_Editor.footer_edit.setPlainText(orig_footer)
                mw.ImageOcc_Editor.remarks_edit.setPlainText(orig_remarks)
            else:
                mw.ImageOcc_Editor.reset_main_fields()

            # update labels
            mw.ImageOcc_Editor.header_label.setText(header_field)
            mw.ImageOcc_Editor.footer_label.setText(footer_field)
            mw.ImageOcc_Editor.sources_label.setText(sources_field)
            mw.ImageOcc_Editor.remarks_label.setText(remarks_field)
            # set tab index
            mw.ImageOcc_Editor.tab_widget.setCurrentIndex(0)
            # set widget focus
            ## this redundant sequence of setFocus() calls prevents a bug where
            ## SVG-Edit would stop working when the Editor window is closed
            ## before adding I/O notes
            ## TODO: find another solution
            mw.ImageOcc_Editor.svg_edit.setFocus()
            mw.ImageOcc_Editor.header_edit.setFocus()
            mw.ImageOcc_Editor.svg_edit.setFocus()

            mw.ImageOcc_Editor.show()

        # no existing instance of I/O Editor. Launch new one
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

            # always copy tags over
            mw.ImageOcc_Editor.tags_edit.setText(orig_tags)
            # only copy sources field if not undefined
            if orig_sources is not None:
                mw.ImageOcc_Editor.sources_edit.setPlainText(orig_sources)
            # reuse all fields if started from existing i/o note
            if self.reuse_note:
                mw.ImageOcc_Editor.header_edit.setPlainText(orig_header)
                mw.ImageOcc_Editor.footer_edit.setPlainText(orig_footer)
                mw.ImageOcc_Editor.remarks_edit.setPlainText(orig_remarks)

            mw.ImageOcc_Editor.show()
        

    @QtCore.pyqtSlot(str)
    def add_notes_non_overlapping(self, svg_contents):
        svg = etree.fromstring(svg_contents.encode('utf-8'))
        (mask_fill_color, did, tags, header, footer, remarks, sources, 
            tempfield3, tempfield4, tempfield5) = get_params_for_add_notes()
        # Add notes to the current deck of the collection:
        add_notes_non_overlapping(svg, mask_fill_color,
                                  tags, self.mw.image_occlusion2_image_path,
                                  header, footer, remarks, sources, 
                                  tempfield3, tempfield4, tempfield5, did)
        
        if self.ed.note and not self.reuse_note:
            # Update Editor with modified tags and sources field
            self.ed.tags.setText(" ".join(tags))
            self.ed.saveTags()
            if sources_field in self.ed.note:
                self.ed.note[sources_field] = sources
                self.ed.loadNote()
        self.mw.reset()

    @QtCore.pyqtSlot(str)
    def add_notes_overlapping(self, svg_contents):
        svg = etree.fromstring(svg_contents.encode('utf-8'))
        (mask_fill_color, did, tags, header, footer, remarks, sources, 
            tempfield3, tempfield4, tempfield5) = get_params_for_add_notes()
        # Add notes to the current deck of the collection:
        add_notes_overlapping(svg, mask_fill_color,
                              tags, self.mw.image_occlusion2_image_path,
                              header, footer, remarks, sources, 
                              tempfield3, tempfield4, tempfield5, did)

        if self.ed.note and not self.reuse_note:
            # Update Editor with modified tags and sources field
            self.ed.tags.setText(" ".join(tags))
            self.ed.saveTags()
            if sources_field in self.ed.note:
                self.ed.note[sources_field] = sources
                self.ed.loadNote()
        self.mw.reset()

def get_params_for_add_notes():
    # Get the mask color from mw.col.conf:
    mask_fill_color = mw.col.conf['image_occlusion_conf']['mask_fill_color']

    header = mw.ImageOcc_Editor.header_edit.toPlainText().replace('\n', '<br />')
    footer = mw.ImageOcc_Editor.footer_edit.toPlainText().replace('\n', '<br />')
    remarks = mw.ImageOcc_Editor.remarks_edit.toPlainText().replace('\n', '<br />')
    sources = mw.ImageOcc_Editor.sources_edit.toPlainText().replace('\n', '<br />')
    tempfield3 = ""
    tempfield4 = ""
    tempfield5 = ""
	
    # Get deck id:
    did = mw.ImageOcc_Editor.deckChooser.selectedId()
    tags = mw.ImageOcc_Editor.tags_edit.text().split()
    return (mask_fill_color, did, tags, header, footer, remarks, sources, 
      tempfield3, tempfield4, tempfield5)


def add_image_occlusion_button(ed):
    ed.image_occlusion = ImageOcc_Add(ed)
    ed._addButton("new_occlusion", ed.image_occlusion.add_notes,
            _("Alt+o"), _("Image Occlusion (Alt+o)"),
            canDisable=False)


class ImageOcc_Editor(QtGui.QWidget):
    def __init__(self, tags):
        super(ImageOcc_Editor, self).__init__()
        self.initUI(tags)
        utils.restoreGeom(self, "imageOccEditor")

    def closeEvent(self, event):
        if mw.pm.profile is not None:
            utils.saveGeom(self, "imageOccEditor")
        QWidget.closeEvent(self, event)

    def initUI(self, tags):

        # Define UI elements

        ## First tab

        # svg-edit
        self.svg_edit = webview.AnkiWebView()
        self.svg_edit.setCanFocus(True)
        # focus is necessary for hotkeys to work

        ## Second Tab

        # Header
        self.header_edit = QPlainTextEdit()
        self.header_edit.setTabChangesFocus(True)
        self.header_label = QLabel(header_field)
        self.header_label.setFixedWidth(70)

        header_hbox = QHBoxLayout()
        header_hbox.addWidget(self.header_label)
        header_hbox.addWidget(self.header_edit)

        # Footer
        self.footer_edit = QPlainTextEdit()
        self.footer_edit.setTabChangesFocus(True)
        self.footer_label = QLabel(footer_field)
        self.footer_label.setFixedWidth(70)

        footer_hbox = QHBoxLayout()
        footer_hbox.addWidget(self.footer_label)
        footer_hbox.addWidget(self.footer_edit)

        # Remarks
        self.remarks_edit = QPlainTextEdit()
        self.remarks_edit.setTabChangesFocus(True)
        self.remarks_label = QLabel(remarks_field)
        self.remarks_label.setFixedWidth(70)

        remarks_hbox = QHBoxLayout()
        remarks_hbox.addWidget(self.remarks_label)
        remarks_hbox.addWidget(self.remarks_edit)

        # Sources
        self.sources_edit = QPlainTextEdit()
        self.sources_edit.setTabChangesFocus(True)
        self.sources_label = QLabel(sources_field)
        self.sources_label.setFixedWidth(70)

        sources_hbox = QHBoxLayout()
        sources_hbox.addWidget(self.sources_label)
        sources_hbox.addWidget(self.sources_edit)

        # Tags
        self.tags_edit = tagedit.TagEdit(self)
        self.tags_edit.setText(" ".join(tags))
        self.tags_edit.setCol(mw.col)
        tags_label = QLabel("Tags")
        tags_label.setFixedWidth(70)

        tags_hbox = QHBoxLayout()
        tags_hbox.addWidget(tags_label)
        tags_hbox.addWidget(self.tags_edit)

        # Deck chooser
        deck_container = QGroupBox()
        self.deckChooser = deckchooser.DeckChooser(mw, deck_container,
                                                   label=True)       

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
        self.tab_widget.setTabToolTip(0, "Create image occlusion SVG masks (required)")

        # Create buttons

        ## Create button layout

        button_box = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        button_box.setCenterButtons(True)
        nonoverlapping_button = button_box.addButton("Add &nonoverlapping occlusions",
                QDialogButtonBox.ActionRole)
        nonoverlapping_button.setToolTip(
            "Generate cards that hide other labels when asking for one")
        overlapping_button = button_box.addButton("Add &overlapping occlusions",
                QDialogButtonBox.ActionRole)
        overlapping_button.setToolTip(
            "Generate cards that don't hide other labels when asking for one")
        close_button = button_box.addButton("&Close",
                QDialogButtonBox.ActionRole)
        close_button.setToolTip("Close Image Occlusion Editor without generating cards")

        ## Connect buttons to actions

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

        # Show window

        self.show()

    # keybinding related functions

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
        self.header_edit.setPlainText("")
        self.footer_edit.setPlainText("")
        self.remarks_edit.setPlainText("")

    def reset_all_fields(self):
        self.reset_main_fields()
        self.sources_edit.setPlainText("")

    def add_nonoverlapping(self): 
        command = """
          var svg_contents = svgCanvas.svgCanvasToString();
          pyObj.add_notes_non_overlapping(svg_contents);
        """
        self.svg_edit.eval(command)

    def add_overlapping(self): 
        command = """
          var svg_contents = svgCanvas.svgCanvasToString();
          pyObj.add_notes_overlapping(svg_contents);
        """
        self.svg_edit.eval(command)

    def fit_image_canvas(self):
        command = "svgCanvas.zoomChanged('', 'canvas');"
        self.svg_edit.eval(command)
        

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
        self.setWindowTitle('Image Occlusion (Options)')
        self.show()

def invoke_ImageOcc_help():
    utils.openLink(image_occlusion_help_link)

mw.ImageOcc_Options = ImageOcc_Options(mw)

options_action = QAction("Image Occlusion (Options)", mw)
help_action = QAction("Image Occlusion (Help)", mw)

mw.connect(options_action,
           SIGNAL("triggered()"),
           mw.ImageOcc_Options.setupUi)

mw.connect(help_action,
           SIGNAL("triggered()"),
           invoke_ImageOcc_help)

mw.form.menuTools.addAction(options_action)
mw.form.menuHelp.addAction(help_action)

hooks.addHook('setupEditorButtons', add_image_occlusion_button)
