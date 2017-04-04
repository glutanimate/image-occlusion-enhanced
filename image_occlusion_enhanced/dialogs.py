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
Handles all major dialogs
"""

import logging, sys

from PyQt4 import QtCore, QtGui
from aqt.qt import *
from anki.errors import AnkiError

from aqt import mw, webview, deckchooser, tagedit
from aqt.utils import saveGeom, restoreGeom

from config import *
from resources import *

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

        self.occl_tp_select = QComboBox()
        self.occl_tp_select.addItems(["Don't Change", "Hide All, Reveal One",
            "Hide All, Reveal All", "Hide One, Reveal All"])

        self.edit_btn = button_box.addButton("&Edit Cards",
           QDialogButtonBox.ActionRole)
        self.new_btn = button_box.addButton("&Add New Cards",
           QDialogButtonBox.ActionRole)
        self.ao_btn = button_box.addButton(u"Hide &All, Reveal One",
           QDialogButtonBox.ActionRole)
        self.aa_btn = button_box.addButton(u"Hide All, &Reveal All",
           QDialogButtonBox.ActionRole)
        self.oa_btn = button_box.addButton(u"Hide &One, Reveal All",
           QDialogButtonBox.ActionRole)
        close_button = button_box.addButton("&Close",
            QDialogButtonBox.RejectRole)

        image_tt = "Switch to a different image while preserving all of \
            the shapes and fields"
        dc_tt = "Preserve existing occlusion type"
        edit_tt = "Edit all cards using current mask shapes and field entries"
        new_tt = "Create new batch of cards without editing existing ones"
        ao_tt = ("Generate cards with nonoverlapping information, where all<br>"
                "labels are hidden on the front and just one is revealed on the back")
        aa_tt = ("Generate cards with partial overlapping information, where<br>"
                "all labels are hidden on the front and all are revealed on the back")
        oa_tt = ("Generate cards with overlapping information, where just one<br>"
                "label is hidden on the front and all are revealed on the back")
        close_tt = "Close Image Occlusion Editor without generating cards"

        image_btn.setToolTip(image_tt)
        self.edit_btn.setToolTip(edit_tt)
        self.new_btn.setToolTip(new_tt)
        self.ao_btn.setToolTip(ao_tt)
        self.aa_btn.setToolTip(aa_tt)
        self.oa_btn.setToolTip(oa_tt)
        close_button.setToolTip(close_tt)
        self.occl_tp_select.setItemData(0, dc_tt, Qt.ToolTipRole)
        self.occl_tp_select.setItemData(1, ao_tt, Qt.ToolTipRole)
        self.occl_tp_select.setItemData(2, aa_tt, Qt.ToolTipRole)
        self.occl_tp_select.setItemData(3, oa_tt, Qt.ToolTipRole)

        for btn in [image_btn, self.edit_btn, self.new_btn, self.ao_btn, 
                    self.aa_btn, self.oa_btn, close_button]:
            btn.setFocusPolicy(Qt.ClickFocus)

        self.connect(self.edit_btn, SIGNAL("clicked()"), self.edit_note)
        self.connect(self.new_btn, SIGNAL("clicked()"), self.new)
        self.connect(self.ao_btn, SIGNAL("clicked()"), self.addAO)
        self.connect(self.aa_btn, SIGNAL("clicked()"), self.addAA)
        self.connect(self.oa_btn, SIGNAL("clicked()"), self.addOA)
        self.connect(close_button, SIGNAL("clicked()"), self.close)

        # Set basic layout up

        ## Button row
        bottom_hbox = QHBoxLayout()
        bottom_hbox.addWidget(image_btn)
        bottom_hbox.insertStretch(1, stretch=1)
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
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Alt+Return"), self),
            QtCore.SIGNAL('activated()'), lambda: self.addAA(True))
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
            self.edit_note()
    def addAO(self, close=False):
        mw.ImgOccAdd.onAddNotesButton("ao", close)
    def addAA(self, close=False):
        mw.ImgOccAdd.onAddNotesButton("aa", close)
    def addOA(self, close=False):
        mw.ImgOccAdd.onAddNotesButton("oa", close)
    def new(self, close=False):
        choice = self.occl_tp_select.currentText()
        mw.ImgOccAdd.onAddNotesButton(choice, close)
    def edit_note(self):
        choice = self.occl_tp_select.currentText()
        mw.ImgOccAdd.onEditNotesButton(choice)

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
        hide_on_edit = [self.ao_btn, self.aa_btn, self.oa_btn]
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

class ImgOccOpts(QDialog):
    """Main Image Occlusion Options dialog"""
    def __init__(self, mw):
        QDialog.__init__(self, parent=mw)
        loadConfig(self)
        self.ofill = self.sconf['ofill']
        self.qfill = self.sconf['qfill']
        self.scol = self.sconf['scol']
        self.swidth = self.sconf['swidth']
        self.font = self.sconf['font']
        self.fsize = self.sconf['fsize']
        self.setupUi()
        self.setupValues(self.sconf)

    def setupValues(self, config):
        """Set up widget data based on provided config dict"""
        self.changeButtonColor(self.ofill_btn, config['ofill'])
        self.changeButtonColor(self.qfill_btn, config['qfill'])
        self.changeButtonColor(self.scol_btn, config['scol'])
        self.swidth_sel.setValue(int(config['swidth']))
        self.fsize_sel.setValue(int(config['fsize']))
        self.swidth_sel.setValue(int(config['swidth']))
        self.font_sel.setCurrentFont(QFont(config['font']))
        self.skipped.setText(','.join(config["skip"]))

    def setupUi(self):
        """Set up widgets and layouts"""

        # Top section
        qfill_label = QLabel('Question mask')
        ofill_label = QLabel('Other masks')
        scol_label = QLabel('Lines')
        colors_heading = QLabel("<b>Colors</b>")
        fields_heading = QLabel("<b>Custom Field Names</b>")
        other_heading = QLabel("<b>Other Editor Settings</b>")

        self.qfill_btn = QPushButton()
        self.ofill_btn = QPushButton()
        self.scol_btn = QPushButton()
        self.qfill_btn.connect(self.qfill_btn, SIGNAL("clicked()"),
            lambda a="qfill", b=self.qfill_btn: self.getNewColor(a, b))
        self.ofill_btn.connect(self.ofill_btn, SIGNAL("clicked()"),
            lambda a="ofill", b=self.ofill_btn: self.getNewColor(a, b))
        self.scol_btn.connect(self.scol_btn, SIGNAL("clicked()"),
            lambda a="scol", b=self.scol_btn: self.getNewColor(a, b))

        swidth_label = QLabel("Line width")
        font_label = QLabel("Label font")
        fsize_label = QLabel("Label size")

        self.swidth_sel = QSpinBox()
        self.swidth_sel.setMinimum(0)
        self.swidth_sel.setMaximum(20)
        self.font_sel = QFontComboBox()
        self.fsize_sel = QSpinBox()
        self.fsize_sel.setMinimum(5)
        self.fsize_sel.setMaximum(300)

        # Horizontal lines
        rule1 = self.create_horizontal_rule()
        rule2 = self.create_horizontal_rule()

        # Bottom section and grid assignment

        fields_text = ("Changing any of the entries below will rename "
        "the corresponding default field of the IO Enhanced note type. "
        "This is the only way you can rename any of the default fields. "
        "<br><br><i>Renaming these fields through Anki's regular dialogs "
        "will cause the add-on to fail. So please don't do that.</i>")

        fields_description = QLabel(fields_text)
        fields_description.setWordWrap(True)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(colors_heading, 0, 0, 1, 3)
        grid.addWidget(qfill_label, 1, 0, 1, 1)
        grid.addWidget(self.qfill_btn, 1, 1, 1, 2)
        grid.addWidget(ofill_label, 2, 0, 1, 1)
        grid.addWidget(self.ofill_btn, 2, 1, 1, 2)
        grid.addWidget(scol_label, 3, 0, 1, 1)
        grid.addWidget(self.scol_btn, 3, 1, 1, 2)

        grid.addWidget(other_heading, 0, 3, 1, 3)
        grid.addWidget(swidth_label, 1, 3, 1, 1)
        grid.addWidget(self.swidth_sel, 1, 4, 1, 2)
        grid.addWidget(font_label, 2, 3, 1, 1)
        grid.addWidget(self.font_sel, 2, 4, 1, 2)
        grid.addWidget(fsize_label, 3, 3, 1, 1)
        grid.addWidget(self.fsize_sel, 3, 4, 1, 2)

        grid.addWidget(rule1, 4, 0, 1, 6)
        grid.addWidget(fields_heading, 5, 0, 1, 6)
        grid.addWidget(fields_description, 6, 0, 1, 6)

        # Field name entries
        row = 7
        clm = 0
        self.lnedit = {}
        for key in IO_FLDS_IDS:
            if row == 13: # switch to right columns
                clm = 3
                row = 7
            default_name = self.sconf_dflt['flds'][key]
            current_name = self.sconf['flds'][key]
            l = QLabel(default_name)
            l.setTextInteractionFlags(Qt.TextSelectableByMouse)
            t = QLineEdit()
            t.setText(current_name)
            grid.addWidget(l, row, clm, 1, 2)
            grid.addWidget(t, row, clm+1, 1, 2)
            self.lnedit[key] = t
            row = row+1


        # Misc settings

        misc_heading = QLabel("<b>Miscellaneous Settings</b>")

        # Skipped fields:
        skipped_description = QLabel("Comma-separated list of " \
            "fields to hide in Editing mode (in order to preserve manual edits):")
        self.skipped = QLineEdit()

        grid.addWidget(rule2, row+1, 0, 1, 6)
        grid.addWidget(misc_heading, row+2, 0, 1, 6)
        grid.addWidget(skipped_description, row+3, 0, 1, 6)
        grid.addWidget(self.skipped, row+4, 0, 1, 6)

        # Main button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok
                                        | QDialogButtonBox.Cancel)
        defaults_btn = button_box.addButton("Restore &Defaults",
           QDialogButtonBox.ResetRole)
        self.connect(defaults_btn, SIGNAL("clicked()"), self.restoreDefaults)
        button_box.accepted.connect(self.onAccept)
        button_box.rejected.connect(self.onReject)

        # Main layout
        l_main = QVBoxLayout()
        l_main.addLayout(grid)
        l_main.addWidget(button_box)
        self.setLayout(l_main)
        self.setMinimumWidth(800)
        self.setMinimumHeight(640)
        self.setWindowTitle('Image Occlusion Enhanced Options')

    def create_horizontal_rule(self):
        """
        Returns a QFrame that is a sunken, horizontal rule.
        """
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.HLine)
        frame.setFrameShadow(QtGui.QFrame.Sunken)
        return frame

    def getNewColor(self, clrvar, clrbtn):
        """Set color via color selection dialog"""
        dialog = QColorDialog()
        color = dialog.getColor()
        if color.isValid():
            # Remove the # sign from QColor.name():
            color = color.name()[1:]
            if clrvar == "qfill":
                self.qfill = color
            elif clrvar == "ofill":
                self.ofill = color
            elif clrvar == "scol":
                self.scol = color
            self.changeButtonColor(clrbtn, color)

    def changeButtonColor(self, button, color):
        """Generate color preview pixmap and place it on button"""
        pixmap = QPixmap(128,18)
        qcolour = QtGui.QColor(0, 0, 0)
        qcolour.setNamedColor('#' + color)
        pixmap.fill(qcolour)
        button.setIcon(QIcon(pixmap))
        button.setIconSize(QSize(128, 18))

    def restoreDefaults(self):
        """Restore colors and fields back to defaults"""
        for key in self.lnedit.keys():
            self.lnedit[key].setText(IO_FLDS[key])
            self.lnedit[key].setModified(True)
        self.setupValues(self.sconf_dflt)
        self.ofill = self.sconf_dflt["ofill"]
        self.qfill = self.sconf_dflt["qfill"]
        self.scol = self.sconf_dflt["scol"]

    def renameFields(self):
        """Check for modified names and rename fields accordingly"""
        modified = False
        model = mw.col.models.byName(IO_MODEL_NAME)
        flds = model['flds']
        for key in self.lnedit.keys():
            if not self.lnedit[key].isModified():
                continue
            name = self.lnedit[key].text()
            oldname = mw.col.conf['imgocc']['flds'][key]
            if name is None or not name.strip() or name == oldname:
                continue
            idx = mw.col.models.fieldNames(model).index(oldname)
            fld = flds[idx]
            if fld:
                # rename note type fields
                mw.col.models.renameField(model, fld, name)
                # update imgocc field-id <-> field-name assignment
                mw.col.conf['imgocc']['flds'][key] = name
                modified = True
                logging.debug("Renamed %s to %s", oldname, name)
        if modified:
            flds = model['flds']

        return (modified, flds)

    def onAccept(self):
        """Apply changes on OK button press"""
        modified = False
        try:
            (modified, flds) = self.renameFields()
        except AnkiError:
            print "Field rename action aborted"
            return
        if modified and hasattr(mw, "ImgOccEdit"):
            self.resetIoEditor(flds)
        mw.col.conf['imgocc']['ofill'] = self.ofill
        mw.col.conf['imgocc']['qfill'] = self.qfill
        mw.col.conf['imgocc']['scol'] = self.scol
        mw.col.conf['imgocc']['swidth'] = self.swidth_sel.value()
        mw.col.conf['imgocc']['fsize'] = self.fsize_sel.value()
        mw.col.conf['imgocc']['font'] = self.font_sel.currentFont().family()
        mw.col.conf['imgocc']['skip'] = self.skipped.text().split(',')
        mw.col.setMod()
        self.close()

    def resetIoEditor(self, flds):
        """Reset existing instance of IO Editor"""
        dialog = mw.ImgOccEdit
        loadConfig(dialog)
        dialog.resetFields()
        dialog.setupFields(flds)

    def onReject(self):
        """Dismiss changes on Close button press"""
        self.close()


def ioError(text, title="Image Occlusion Enhanced Error",
                                    parent=None, help=None):
    msgfunc = QMessageBox.critical
    btns = None
    if help:
        btns = QMessageBox.Help | QMessageBox.Ok
    while 1:
        r = ioInfo(text, title, parent, buttons=btns, msgfunc=msgfunc)
        if r == QMessageBox.Help:
            ioHelp(help, parent=parent)
        else:
            break
    return r

def ioAskUser(text, title="Image Occlusion Enhanced", parent=None,
                            help="", defaultno=False, msgfunc=None):
    """Show a yes/no question. Return true if yes.
    based on askUser by Damien Elmes"""

    msgfunc = QMessageBox.question
    btns = QMessageBox.Yes | QMessageBox.No
    if help:
        btns |= QMessageBox.Help
    while 1:
        if defaultno:
            default = QMessageBox.No
        else:
            default = QMessageBox.Yes
        r = ioInfo(text, title, parent, btns, default, msgfunc)
        if r == QMessageBox.Help:
            ioHelp(help)
        else:
            break
    return r == QMessageBox.Yes

def ioInfo(text, title="Image Occlusion Enhanced", parent=None,
                        buttons=None, default=None, msgfunc=None):
    if not parent:
        parent = mw.app.activeWindow()
    if not buttons:
        buttons = QMessageBox.Ok
    if not default:
        default = QMessageBox.Ok
    if not msgfunc:
        msgfunc = QMessageBox.information
    return msgfunc(parent, title, text, buttons, default)


def ioHelp(help, title=None, text=None, parent=None):
    """Display an info message or a predefined help section"""
    io_link_wiki = "https://github.com/Glutanimate/image-occlusion-enhanced/wiki"
    io_link_tut = "https://www.youtube.com/playlist?list=PL3MozITKTz5YFHDGB19ypxcYfJ1ITk_6o"
    io_link_thread = ("https://anki.tenderapp.com/discussions/add-ons/"
                      "8295-image-occlusion-enhanced-official-thread")
    help_text = {}
    help_text["editing"] = """<b>Instructions for editing</b>: \
        <br><br> Each mask shape represents a card.\
        Removing any of the existing shapes will remove the corresponding card.\
        New shapes will generate new cards. You can change the occlusion type\
        by using the dropdown box on the left.<br><br>If you click on the \
        <i>Add new cards</i> button a completely new batch of cards will be \
        generated, leaving your originals untouched.<br><br> \
        <b>Actions performed in Image Occlusion's <i>Editing Mode</i> cannot be\
        easily undone, so please make sure to check your changes twice before\
        applying them.</b><br><br>The only exception to this are purely textual\
        changes to fields like the header or footer of your notes. These can\
        be fully reverted by using Ctrl+Z in the Browser or Reviewer view.<br><br>\
        More information: <a href="%s">Wiki: Editing Notes</a>.\
        """ % (io_link_wiki + "/Basic-Use#editing-cards")
    help_text["notetype"] = """<b>Fixing a broken note type:</b>\
        <br><br> The Image Occlusion Enhanced note type can't be edited \
        arbitrarily. If you delete a field that's required by the add-on \
        or rename it outside of the IO Options dialog you will be presented \
        with an error message. <br><br>
        To fix this issue please follow the instructions in <a href="%s">the \
        wiki</a>.""" % (io_link_wiki + "/Troubleshooting#note-type")
    help_text["main"] = u"""<h2>Help and Support</h2>
        <p><a href="%s">Image Occlusion Enhanced Wiki</a></p>
        <p><a href="%s">Official Video Tutorial Series</a></p>
        <p><a href="%s">Support Thread</a></p>
        <h2>Credits and License</h2>
        <p style="font-size:12pt;"><em>Copyright © 2012-2015 \
        <a href="https://github.com/tmbb">Tiago Barroso</a></em></p>
        <p style="font-size:12pt;"><em>Copyright © 2013 \
        <a href="https://github.com/steveaw">Steve AW</a></em></p>
        <p style="font-size:12pt;"><em>Copyright © 2016-2017 \
        <a href="https://github.com/Glutanimate">Aristotelis P.</a></em></p>
        <p><em>Image Occlusion Enhanced</em> is licensed under the GNU AGPLv3.</p>
        <p>Third-party open-source software shipped with <em>Image Occlusion Enhanced</em>:</p>
        <ul><li><p><a href="https://github.com/SVG-Edit/svgedit">SVG Edit</a> 2.6. \
        Copyright (c) 2009-2012 SVG-edit authors. Licensed under the MIT license</a></p></li>
        <li><p><a href="http://www.pythonware.com/products/pil/">Python Imaging Library</a> \
        (PIL) 1.1.7. Copyright (c) 1997-2011 by Secret Labs AB, Copyright (c) 1995-2011 by Fredrik \
        Lundh. Licensed under the <a href="http://www.pythonware.com/products/pil/license.htm">\
        PIL license</a></p></li>
        <li><p><a href="https://github.com/shibukawa/imagesize_py">imagesize.py</a> v0.7.1. \
        Copyright (c) 2016 Yoshiki Shibukawa. Licensed under the MIT license.</p></li>
        </ul>
        """ % (io_link_wiki, io_link_tut, io_link_thread)
    if help != "custom":
        text = help_text[help]
    if not title:
        title = "Image Occlusion Enhanced Help"
    if not parent:
        parent = mw.app.activeWindow()
    QMessageBox.about(parent, title, text)