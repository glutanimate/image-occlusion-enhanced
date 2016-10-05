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

from PyQt4 import QtCore, QtGui
from aqt.qt import *

from aqt import mw, webview, deckchooser, tagedit
from aqt.utils import saveGeom, restoreGeom

from config import *

class ImgOccEdit(QDialog):
    def __init__(self, mw):
        QDialog.__init__(self, parent=None)
        self.mode = mw.ImgOccAdd.mode
        self.setupUi()
        restoreGeom(self, "imageOccEditor")

    def closeEvent(self, event):
        if mw.pm.profile is not None:
            saveGeom(self, "imageOccEditor")
        QWidget.closeEvent(self, event)

    def setupUi(self):
        self.svg_edit = webview.AnkiWebView()
        self.svg_edit.setCanFocus(True) # focus necessary for hotkeys

        editing_text = "<b>Instructions for editing</b>:\
            Each mask shape represents a card.\
            Removing any of the existing shapes will remove the corresponding card.\
            New shapes will generate new cards. You can change the occlusion type\
            by using the dropdown box. If you click on the <i>Add</i> button\
            a completely new batch of cards will be generated, leaving your originals\
            untouched."
        self.edit_label = QLabel(editing_text)
        self.edit_label.setWordWrap(True)

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
        vbox1.addWidget(self.edit_label)
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

        self.bottom_label = QLabel()
        button_box = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        button_box.setCenterButtons(False)

        self.otype_select = QComboBox()
        self.otype_select.addItems(["Don't change", "All Hidden, One Revealed",
            "All Hidden, All Revealed", "One Hidden, All Revealed"])

        self.edit_btn = button_box.addButton("&Edit cards",
                QDialogButtonBox.ActionRole)
        self.new_btn = button_box.addButton("&Add new cards",
                QDialogButtonBox.ActionRole)
        self.allhideonereveal_btn = button_box.addButton(u"All Hidden, &One Revealed",
                QDialogButtonBox.ActionRole)
        self.allhideallreveal_btn = button_box.addButton(u"All Hidde&n, All Revealed",
                QDialogButtonBox.ActionRole)
        self.onehideallreveal_btn = button_box.addButton(u"One Hidden, &All Revealed",
                QDialogButtonBox.ActionRole)
        self.close_button = button_box.addButton("&Close", 
                QDialogButtonBox.RejectRole)

        edit_tt = "Edit all cards using current mask shapes and field entries"
        new_tt = "Create new batch of cards without editing existng ones"
        allhideonereveal_tt = "Formerly known as nonoverlapping.<br>\
            Generate cards where all labels are hidden and just one is revealed<br>\
            on the back"
        allhideallreveal_tt = "A step between nonoverlapping and overlapping.<br>\
            Generate cards where all labels are hidden on the front, but all \
            revealed on the back"
        onehideallreveal_tt = "Formerly known as overlapping.<br>\
            Generate cards where just one label is hidden on the front and all\
            revealed on the back"
        close_tt = "Close Image Occlusion Editor without generating cards"
        self.edit_btn.setToolTip(edit_tt)
        self.new_btn.setToolTip(new_tt)
        self.allhideonereveal_btn.setToolTip(allhideonereveal_tt)
        self.allhideallreveal_btn.setToolTip(allhideallreveal_tt)
        self.onehideallreveal_btn.setToolTip(onehideallreveal_tt)
        self.close_button.setToolTip(close_tt)

        self.connect(self.edit_btn, SIGNAL("clicked()"), self.edit_all)
        self.connect(self.new_btn, SIGNAL("clicked()"), self.new)
        self.connect(self.allhideonereveal_btn, SIGNAL("clicked()"), self.add_allhideonereveal)
        self.connect(self.allhideallreveal_btn, SIGNAL("clicked()"), self.add_allhideallreveal)
        self.connect(self.onehideallreveal_btn, SIGNAL("clicked()"), self.add_onehideallreveal)
        self.connect(self.close_button, SIGNAL("clicked()"), self.close)

        bottom_hbox = QHBoxLayout()
        bottom_hbox.addWidget(self.bottom_label)
        bottom_hbox.addWidget(self.otype_select)
        bottom_hbox.addWidget(button_box)

        # Add all widgets to main window
        ## set widget layout up
        vbox_main = QtGui.QVBoxLayout()
        vbox_main.setMargin(0);
        ## add widgets
        vbox_main.addWidget(self.tab_widget)
        vbox_main.addLayout(bottom_hbox)
        ## apply to main window
        self.setLayout(vbox_main)

        # Set basic window properties
        # self.setMinimumHeight(600)
        self.setWindowTitle('Image Occlusion Enhanced')

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

    ## Note actions
    def add_allhideonereveal(self): 
        mw.ImgOccAdd.onAddNotesButton("ao")
    def add_allhideallreveal(self): 
        mw.ImgOccAdd.onAddNotesButton("aa")
    def add_onehideallreveal(self): 
        mw.ImgOccAdd.onAddNotesButton("oa")
    def new(self):
        mw.ImgOccAdd.onAddNotesButton("new")
        self.close()
    def edit_all(self):
        mw.ImgOccAdd.onAddNotesButton("edit")
        self.close()

    # Modes
    def switch_to_mode(self, mode):
        self.mode = mode
        if mode == "add":
            self.edit_label.hide()
            self.otype_select.hide()
            self.edit_btn.hide()
            self.new_btn.hide()
            self.allhideonereveal_btn.show()
            self.allhideallreveal_btn.show()
            self.onehideallreveal_btn.show()
            self.setWindowTitle('Image Occlusion Enhanced - Add mode')
            self.bottom_label.setText("Add card type:")
        else:
            self.edit_label.show()
            self.otype_select.show()
            self.edit_btn.show()
            self.new_btn.show()
            self.allhideonereveal_btn.hide()
            self.allhideallreveal_btn.hide()
            self.onehideallreveal_btn.hide()
            self.setWindowTitle('Image Occlusion Enhanced - Editing mode')
            self.bottom_label.setText("Choose card type:")

    # Keybindings

    ## Navigation, etc.
    def reset_window(self):
        self.reset_all_fields()
        self.tab_widget.setCurrentIndex(0)
        self.otype_select.setCurrentIndex(0)
        self.header_edit.setFocus()
        self.svg_edit.setFocus()

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

class ImgOccOpts(QDialog):
    # Main IO Options dialog
    def __init__(self, mw):
        QDialog.__init__(self, parent=mw)
        self.setupUi()

    def getNewMaskColor(self):
        # Remove the # sign from QColor.name():
        choose_color_dialog = QColorDialog()
        color = choose_color_dialog.getColor()
        if color.isValid():
            color_ = color.name()[1:]
            mw.col.conf['imgocc']['qfill'] = color_
            # notify db of modification
            mw.col.setMod()
            self.changeButtonColor(self.mask_color_button, color_)

    def getNewOfillColor(self):
        # Remove the # sign from QColor.name():
        choose_color_dialog = QColorDialog()
        color = choose_color_dialog.getColor()
        if color.isValid():
            color_ = color.name()[1:]
            mw.col.conf['imgocc']['ofill'] = color_
            # notify db of modification
            mw.col.setMod()
            self.changeButtonColor(self.ofill_button, color_)

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
        qfill_label = QLabel('<b>Question</b> shape color')
        self.mask_color_button = QPushButton()
        self.mask_color_button.connect(self.mask_color_button,
                                  SIGNAL("clicked()"),
                                  self.getNewMaskColor)
        ### initial shape color:
        ofill_label = QLabel('<b>Initial</b> shape color')
        self.ofill_button = QPushButton()
        self.ofill_button.connect(self.ofill_button,
                                SIGNAL("clicked()"),
                                self.getNewOfillColor)

        ### set colors
        ofill = mw.col.conf['imgocc']['ofill']
        qfill = mw.col.conf['imgocc']['qfill']
        self.changeButtonColor(self.ofill_button, ofill)
        self.changeButtonColor(self.mask_color_button, qfill)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        # 1st row:
        grid.addWidget(qfill_label, 0, 0)
        grid.addWidget(self.mask_color_button, 0, 1)
        # 2nd row:
        grid.addWidget(ofill_label, 1, 0)
        grid.addWidget(self.ofill_button, 1, 1)

        self.setLayout(grid)
        self.setMinimumWidth(400)
        self.setWindowTitle('Image Occlusion Enhanced Options')