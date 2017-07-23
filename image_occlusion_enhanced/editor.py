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
Image Occlusion editor dialog
"""

from PyQt4 import QtCore, QtGui
from aqt.qt import *

from aqt import mw, webview, deckchooser, tagedit
from aqt.utils import saveGeom, restoreGeom

from dialogs import ioHelp
from config import *

class ImgOccEdit(QDialog):
    """Main Image Occlusion Editor dialog"""
    def __init__(self, mw):
        QDialog.__init__(self, parent=None)
        self.setWindowFlags(Qt.Window)
        self.visible = False
        self.mode = "add"
        loadConfig(self)
        self.setupUi()
        restoreGeom(self, "imgoccedit")

    def closeEvent(self, event):
        if mw.pm.profile is not None:
            self.deckChooser.cleanup()
            saveGeom(self, "imgoccedit")
        self.visible = False
        event.accept()

    def reject(self):
        # Override QDialog Esc key reject
        pass

    def setupUi(self):
        """Set up ImgOccEdit UI"""
        # Main widgets aside from fields
        self.svg_edit = webview.AnkiWebView()
        # required for local href links to work properly (e.g. context menu):
        self.svg_edit.page().setLinkDelegationPolicy(QWebPage.DelegateExternalLinks)
        self.svg_edit.setCanFocus(True) # focus necessary for hotkeys
        self.tags_hbox = QHBoxLayout()
        self.tags_edit = tagedit.TagEdit(self)
        self.tags_label = QLabel("Tags")
        self.tags_label.setFixedWidth(70)
        self.deck_container = QWidget()
        self.deckChooser = deckchooser.DeckChooser(mw,
                        self.deck_container, label=True)
        self.deckChooser.deck.setAutoDefault(False)

        # workaround for tab focus order issue of the tags entry
        # (this particular section is only needed when the quick deck
        # buttons add-on is installed)
        if self.deck_container.layout().children(): # multiple deck buttons
            for i in range(self.deck_container.layout().children()[0].count()):
                try:
                    item = self.deck_container.layout().children()[0].itemAt(i)
                    # remove Tab focus manually:
                    item.widget().setFocusPolicy(Qt.ClickFocus)
                    item.widget().setAutoDefault(False)
                except AttributeError:
                    pass


        # Button row widgets
        self.bottom_label = QLabel()
        button_box = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        button_box.setCenterButtons(False)

        image_btn = QPushButton("Change &Image", clicked=self.changeImage)
        image_btn.setIcon(QIcon(":/icons/new_occlusion.png"))
        image_btn.setIconSize(QSize(16, 16))
        image_btn.setAutoDefault(False)
        help_btn = QPushButton("&Help", clicked=self.onHelp)
        help_btn.setAutoDefault(False)

        self.occl_tp_select = QComboBox()
        self.occl_tp_select.addItems(["Don't Change", "Hide All, Reveal One",
             "Hide One, Reveal All"])

        self.edit_btn = button_box.addButton("&Edit Cards",
           QDialogButtonBox.ActionRole)
        self.new_btn = button_box.addButton("&Add New Cards",
           QDialogButtonBox.ActionRole)
        self.ao_btn = button_box.addButton(u"Hide &All, Reveal One",
           QDialogButtonBox.ActionRole)
        self.oa_btn = button_box.addButton(u"Hide &One, Reveal All",
           QDialogButtonBox.ActionRole)
        close_button = button_box.addButton("&Close",
            QDialogButtonBox.RejectRole)

        image_tt = ("Switch to a different image while preserving all of "
            "the shapes and fields")
        dc_tt = "Preserve existing occlusion type"
        edit_tt = "Edit all cards using current mask shapes and field entries"
        new_tt = "Create new batch of cards without editing existing ones"
        ao_tt = ("Generate cards with nonoverlapping information, where all<br>"
                "labels are hidden on the front and one revealed on the back")
        oa_tt = ("Generate cards with overlapping information, where one<br>"
                "label is hidden on the front and revealed on the back")
        close_tt = "Close Image Occlusion Editor without generating cards"

        image_btn.setToolTip(image_tt)
        self.edit_btn.setToolTip(edit_tt)
        self.new_btn.setToolTip(new_tt)
        self.ao_btn.setToolTip(ao_tt)
        self.oa_btn.setToolTip(oa_tt)
        close_button.setToolTip(close_tt)
        self.occl_tp_select.setItemData(0, dc_tt, Qt.ToolTipRole)
        self.occl_tp_select.setItemData(1, ao_tt, Qt.ToolTipRole)
        self.occl_tp_select.setItemData(2, oa_tt, Qt.ToolTipRole)

        for btn in [image_btn, self.edit_btn, self.new_btn, self.ao_btn, 
                    self.oa_btn, close_button]:
            btn.setFocusPolicy(Qt.ClickFocus)

        self.connect(self.edit_btn, SIGNAL("clicked()"), self.editNote)
        self.connect(self.new_btn, SIGNAL("clicked()"), self.new)
        self.connect(self.ao_btn, SIGNAL("clicked()"), self.addAO)
        self.connect(self.oa_btn, SIGNAL("clicked()"), self.addOA)
        self.connect(close_button, SIGNAL("clicked()"), self.close)

        # Set basic layout up

        ## Button row
        bottom_hbox = QHBoxLayout()
        bottom_hbox.addWidget(image_btn)
        bottom_hbox.addWidget(help_btn)
        bottom_hbox.insertStretch(2, stretch=1)
        bottom_hbox.addWidget(self.bottom_label)
        bottom_hbox.addWidget(self.occl_tp_select)
        bottom_hbox.addWidget(button_box)

        ## Tab 1
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.svg_edit, stretch=1)

        ## Tab 2
        self.vbox2 = QVBoxLayout()
        # vbox2 fields are variable and added by setupFields() at a later point

        ## Main Tab Widget
        tab1 = QWidget()
        self.tab2 = QWidget()
        tab1.setLayout(vbox1)
        self.tab2.setLayout(self.vbox2)
        self.tab_widget = QtGui.QTabWidget()
        self.tab_widget.setFocusPolicy(Qt.ClickFocus)
        self.tab_widget.addTab(tab1,"&Masks Editor")
        self.tab_widget.addTab(self.tab2,"&Fields")
        self.tab_widget.setTabToolTip(1, "Include additional information (optional)")
        self.tab_widget.setTabToolTip(0, "Create image occlusion masks (required)")

        ## Main Window
        vbox_main = QVBoxLayout()
        vbox_main.setMargin(5)
        vbox_main.addWidget(self.tab_widget)
        vbox_main.addLayout(bottom_hbox)
        self.setLayout(vbox_main)
        self.setMinimumWidth(640)
        self.tab_widget.setCurrentIndex(0)
        self.svg_edit.setFocus()

        # Define and connect key bindings

        ## Field focus hotkeys
        for i in range(1,10):
            s = self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+%i" %i), self),
                QtCore.SIGNAL('activated()'),
                lambda f=i-1:self.focusField(f))
        ## Other hotkeys
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Return"), self),
            QtCore.SIGNAL('activated()'), lambda: self.defaultAction(True))
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+Return"), self),
            QtCore.SIGNAL('activated()'), lambda: self.addOA(True))
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Tab"), self),
            QtCore.SIGNAL('activated()'), self.switchTabs)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+r"), self),
            QtCore.SIGNAL('activated()'), self.resetMainFields)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+r"), self),
            QtCore.SIGNAL('activated()'), self.resetAllFields)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+t"), self),
            QtCore.SIGNAL('activated()'), self.focusTags)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+f"), self),
            QtCore.SIGNAL('activated()'), self.fitImageCanvas)


    # Various actions that act on / interact with the ImgOccEdit UI:

    # Note actions

    def changeImage(self):
        mw.ImgOccAdd.onChangeImage()
    def defaultAction(self, close):
        if self.mode == "add":
            self.addAO(close)
        else:
            self.editNote()
    def addAO(self, close=False):
        mw.ImgOccAdd.onAddNotesButton("ao", close)
    def addOA(self, close=False):
        mw.ImgOccAdd.onAddNotesButton("oa", close)
    def new(self, close=False):
        choice = self.occl_tp_select.currentText()
        mw.ImgOccAdd.onAddNotesButton(choice, close)
    def editNote(self):
        choice = self.occl_tp_select.currentText()
        mw.ImgOccAdd.onEditNotesButton(choice)
    def onHelp(self):
        if self.mode == "add":
            ioHelp("add")
        else:
            ioHelp("edit")
        

    # Window state

    def resetFields(self):
        """Reset all widgets. Needed for changes to the note type"""
        layout = self.vbox2
        for i in reversed(range(layout.count())):
            item = layout.takeAt(i)
            layout.removeItem(item)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                sublayout = item.layout()
                sublayout.setParent(None)
                for i in reversed(range(sublayout.count())):
                    subitem = sublayout.takeAt(i)
                    sublayout.removeItem(subitem)
                    subitem.widget().setParent(None)
        self.tags_hbox.setParent(None)

    def resetWindow(self):
        """Fully reset window state"""
        self.resetAllFields()
        self.tab_widget.setCurrentIndex(0)
        self.occl_tp_select.setCurrentIndex(0)
        self.tedit[self.ioflds["hd"]].setFocus()
        self.svg_edit.setFocus()

    def setupFields(self, flds):
        """Setup dialog text edits based on note type fields"""
        self.tedit = {}
        self.tlabel = {}
        self.flds = flds
        for i in flds:
            if i['name'] in self.ioflds_priv:
                continue
            hbox = QHBoxLayout()
            tedit = QPlainTextEdit()
            label = QLabel(i["name"])
            hbox.addWidget(label)
            hbox.addWidget(tedit)
            tedit.setTabChangesFocus(True)
            tedit.setMinimumHeight(40)
            label.setFixedWidth(70)
            self.tedit[i["name"]] = tedit
            self.tlabel[i["name"]] = label
            self.vbox2.addLayout(hbox)

        self.tags_hbox.addWidget(self.tags_label)
        self.tags_hbox.addWidget(self.tags_edit)
        self.vbox2.addLayout(self.tags_hbox)
        self.vbox2.addWidget(self.deck_container)
        # switch Tab focus order of deckchooser and tags_edit (
        # for some reason it's the wrong way around by default):
        self.tab2.setTabOrder(self.tags_edit, self.deckChooser.deck)

    def switchToMode(self, mode):
        """Toggle between add and edit layouts"""
        hide_on_add = [self.occl_tp_select, self.edit_btn, self.new_btn]
        hide_on_edit = [self.ao_btn, self.oa_btn]
        self.mode = mode
        for i in self.tedit.values():
            i.show()
        for i in self.tlabel.values():
            i.show()
        if mode == "add":
            for i in hide_on_add:
                i.hide()
            for i in hide_on_edit:
                i.show()
            dl_txt = "Deck"
            ttl = "Image Occlusion Enhanced - Add Mode"
            bl_txt = "Add Cards:"
        else:
            for i in hide_on_add:
                i.show()
            for i in hide_on_edit:
                i.hide()
            for i in self.sconf['skip']:
                if i in self.tedit.keys():
                    self.tedit[i].hide()
                    self.tlabel[i].hide()
            dl_txt = "Deck for <i>Add new cards</i>"
            ttl = "Image Occlusion Enhanced - Editing Mode"
            bl_txt = "Type:"
        self.deckChooser.deckLabel.setText(dl_txt)
        self.setWindowTitle(ttl)
        self.bottom_label.setText(bl_txt)

    # Other actions

    def switchTabs(self):
        currentTab = self.tab_widget.currentIndex()
        if currentTab == 0:
          self.tab_widget.setCurrentIndex(1)
          if isinstance(QApplication.focusWidget(), QPushButton):
              self.tedit[self.ioflds["hd"]].setFocus()
        else:
          self.tab_widget.setCurrentIndex(0)

    def focusField(self, idx):
        """Focus field in vbox2 layout by index number"""
        self.tab_widget.setCurrentIndex(1)
        target_item = self.vbox2.itemAt(idx)
        if not target_item:
            return
        target_layout = target_item.layout()
        target_widget = target_item.widget()
        if target_layout:
            target = target_layout.itemAt(1).widget()
        elif target_widget:
            target = target_widget
        target.setFocus()

    def focusTags(self):
        self.tab_widget.setCurrentIndex(1)
        self.tags_edit.setFocus()

    def resetMainFields(self):
        """Reset all fields aside from sticky ones"""
        for i in self.flds:
            fn = i['name']
            if fn in self.ioflds_priv or fn in self.ioflds_prsv:
                continue
            self.tedit[fn].setPlainText("")

    def resetAllFields(self):
        """Reset all fields"""
        self.resetMainFields()
        for i in self.ioflds_prsv:
            self.tedit[i].setPlainText("")

    def fitImageCanvas(self):
        command = "svgCanvas.zoomChanged('', 'canvas');"
        self.svg_edit.eval(command)
