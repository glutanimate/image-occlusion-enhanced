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
Main options dialog
"""

import logging

from aqt.qt import *
from aqt.utils import showInfo

from aqt import mw
from anki.errors import AnkiError

from .config import *


class GrabKey(QDialog):
    """
    Grab the key combination to paste the resized image

    Largely based on ImageResizer by searene
    (https://github.com/searene/Anki-Addons)
    """

    def __init__(self, parent):
        QDialog.__init__(self, parent=parent)
        self.parent = parent
        self.key = parent.hotkey
        # self.active is used to trace whether there's any key held now
        self.active = 0
        self.ctrl = False
        self.alt = False
        self.shift = False
        self.extra = None
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        label = QLabel('Please press the new key combination')
        mainLayout.addWidget(label)

        self.setWindowTitle('Grab key combination')

    def keyPressEvent(self, evt):
        self.active += 1
        if evt.key() > 0 and evt.key() < 127:
            self.extra = chr(evt.key())
        elif evt.key() == Qt.Key_Control:
            self.ctrl = True
        elif evt.key() == Qt.Key_Alt:
            self.alt = True
        elif evt.key() == Qt.Key_Shift:
            self.shift = True

    def keyReleaseEvent(self, evt):
        self.active -= 1

        if self.active != 0:
            return
        if not (self.shift or self.ctrl or self.alt):
            showInfo("Please use at least one keyboard "
                     "modifier (Ctrl, Alt, Shift)")
            return
        if (self.shift and not (self.ctrl or self.alt)):
            showInfo("Shift needs to be combined with at "
                     "least one other modifier (Ctrl, Alt)")
            return
        if not self.extra:
            showInfo("Please press at least one key "
                     "that is not a keyboard modifier (not Ctrl/Alt/Shift)")
            return

        combo = []
        if self.ctrl:
            combo.append("Ctrl")
        if self.shift:
            combo.append("Shift")
        if self.alt:
            combo.append("Alt")
        combo.append(self.extra)

        self.parent.updateHotkey("+".join(combo))
        self.close()


class ImgOccOpts(QDialog):
    """Main Image Occlusion Options dialog"""

    def __init__(self):
        QDialog.__init__(self, parent=mw)
        loadConfig(self)
        self.ofill = self.sconf['ofill']
        self.qfill = self.sconf['qfill']
        self.scol = self.sconf['scol']
        self.swidth = self.sconf['swidth']
        self.font = self.sconf['font']
        self.fsize = self.sconf['fsize']
        self.hotkey = self.lconf["hotkey"]
        self.setupUi()
        self.setupValues(self.sconf)

    def setupValues(self, config):
        """Set up widget data based on provided config dict"""
        self.updateHotkey()
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
        self.qfill_btn.clicked.connect(lambda _, t="qfill", b=self.qfill_btn:
                                       self.getNewColor(t, b))
        self.ofill_btn.clicked.connect(lambda _, t="ofill", b=self.ofill_btn:
                                       self.getNewColor(t, b))
        self.scol_btn.clicked.connect(lambda _, t="scol", b=self.scol_btn:
                                      self.getNewColor(t, b))

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

        grid = QGridLayout()
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
            if row == 13:  # switch to right columns
                clm = 3
                row = 7
            default_name = self.sconf_dflt['flds'][key]
            current_name = self.sconf['flds'][key]
            lb = QLabel(default_name)
            lb.setTextInteractionFlags(Qt.TextSelectableByMouse)
            t = QLineEdit()
            t.setText(current_name)
            grid.addWidget(lb, row, clm, 1, 2)
            grid.addWidget(t, row, clm + 1, 1, 2)
            self.lnedit[key] = t
            row += 1

        # Misc settings
        misc_heading = QLabel("<b>Miscellaneous Settings</b>")

        # Skipped fields:
        skipped_description = QLabel("Comma-separated list of "
                                     "fields to hide in Editing mode "
                                     "(in order to preserve manual edits):")
        self.skipped = QLineEdit()

        # Hotkey:
        key_grab_label = QLabel('Invoke IO with the following hotkey:')
        self.key_grabbed = QLabel('')
        key_grab_btn = QPushButton('Change hotkey', self)
        key_grab_btn.clicked.connect(self.showGrabKey)

        grid.addWidget(rule2, row + 1, 0, 1, 6)
        grid.addWidget(misc_heading, row + 2, 0, 1, 6)
        grid.addWidget(skipped_description, row + 3, 0, 1, 6)
        grid.addWidget(self.skipped, row + 4, 0, 1, 6)
        grid.addWidget(key_grab_label, row + 5, 0, 1, 2)
        grid.addWidget(self.key_grabbed, row + 5, 2, 1, 1)
        grid.addWidget(key_grab_btn, row + 5, 3, 1, 3)

        # Main button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok |
                                      QDialogButtonBox.Cancel)
        defaults_btn = button_box.addButton("Restore &Defaults",
                                            QDialogButtonBox.ResetRole)
        defaults_btn.clicked.connect(self.restoreDefaults)
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
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)
        return frame

    def updateHotkey(self, combo=None):
        """Update hotkey label and attribute"""
        key = combo or self.hotkey
        label = "<b>{}</b>".format(key)
        self.key_grabbed.setText(label)
        if combo:
            self.hotkey = combo

    def showGrabKey(self):
        """Invoke key grabber"""
        win = GrabKey(self)
        win.exec_()

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
        pixmap = QPixmap(128, 18)
        qcolour = QColor(0, 0, 0)
        qcolour.setNamedColor('#' + color)
        pixmap.fill(qcolour)
        button.setIcon(QIcon(pixmap))
        button.setIconSize(QSize(128, 18))

    def restoreDefaults(self):
        """Restore colors and fields back to defaults"""
        self.hotkey = self.lconf_dflt["hotkey"]
        for key in list(self.lnedit.keys()):
            self.lnedit[key].setText(IO_FLDS[key])
            self.lnedit[key].setModified(True)
        self.setupValues(self.sconf_dflt)
        self.ofill = self.sconf_dflt["ofill"]
        self.qfill = self.sconf_dflt["qfill"]
        self.scol = self.sconf_dflt["scol"]

    def renameFields(self):
        """Check for modified names and rename fields accordingly"""
        modified = False
        model = getOrCreateModel()
        flds = model['flds']
        for key in list(self.lnedit.keys()):
            if not self.lnedit[key].isModified():
                continue
            name = self.lnedit[key].text()
            oldname = mw.col.conf['imgocc']['flds'][key]
            if (name is None or not name.strip() or name == oldname):
                continue
            fnames = mw.col.models.fieldNames(model)
            if (name in fnames and oldname not in fnames):
                # case: imported cards, fields not corresponding to config
                mw.col.conf['imgocc']['flds'][key] = name
                modified = True
                continue
            idx = fnames.index(oldname)
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
            print("Field rename action aborted")
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
        mw.pm.profile["imgocc"]["hotkey"] = self.hotkey
        mw.col.setMod()
        self.close()

    def resetIoEditor(self, flds):
        """Reset existing instance of IO Editor"""
        # TODO: either delete method or refactor into method that updates running
        # instance of I/O (we no longer reuse old ImgOccEdit instances)
        dialog = mw.ImgOccEdit
        loadConfig(dialog)
        dialog.resetFields()
        dialog.setupFields(flds)

    def onReject(self):
        """Dismiss changes on Close button press"""
        self.close()
