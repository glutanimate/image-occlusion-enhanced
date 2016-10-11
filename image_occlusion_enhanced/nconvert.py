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

"""
Experimental conversion between older IO note types
and Image Occlusion Enhanced
"""

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QKeySequence
from anki.hooks import addHook
from aqt.utils import tooltip

from xml.dom import minidom

from config import *
from utils import img2path


class ImgOccNoteConverter(object):
    def __init__(self, browser):
        self.browser = browser
        self.model = mw.col.models.byName(IO_MODEL_NAME)
        loadConfig(self)

    def convertNotes(self, nids):
        io_notes = self.filterByModel(nids)
        for i in io_notes:
            (uniq_id, note_nr) = self.getDataFromNamingScheme(i)
            (occl_tp, self.mnode_indexes) = self.getOcclTypeAndMnodes(i)
            family_nids = self.findByNoteId(uniq_id)
            self.idAndCorrelateNotes(family_nids, uniq_id, occl_tp)
            print "note:", i
            print "uniq_id", uniq_id
            print "note_nr", note_nr
            print "occl_tp", occl_tp
            print "mnode_indexes", self.mnode_indexes
            print "family nids", family_nids

    def filterByModel(self, nids):
        io_notes = []
        for nid in nids:
            note = mw.col.getNote(nid)
            if note.model() == self.model:
                if not note[self.ioflds['id']]:
                    print "Unconverted IO note:", nid
                    io_notes.append(note)
                else:
                    print "Skipping proper IO note:", nid
            else:
                print "Not an IO note:", nid
        return io_notes

    def findByNoteId(self, note_id):
        query = "'%s':'*%s*'" % ( self.ioflds['om'], note_id )
        print "query:", query
        res = mw.col.findNotes(query)
        return res

    def getDataFromNamingScheme(self, note):
        qmask = note[self.ioflds['qm']]
        path = img2path(qmask, True)
        uniq_id = path.split('_')[0]
        note_nr = path.split(' ')[1].split('.')[0]
        return (uniq_id, note_nr)

    def idAndCorrelateNotes(self, nids, uniq_id, occl_tp):
        pass

    def getOcclTypeAndMnodes(self, note):
        nr_of_masks = {}
        mnode_idxs = {}
        for i in ["om", "qm"]:
            svg_file = img2path(note[self.ioflds[i]], True)
            svg_doc = minidom.parse(svg_file)
            svg_node = svg_doc.documentElement
            svg_mlayer = self.layerNodesFrom(svg_node)[-1]
            (mnode_indexes, mnode_nr) = self.getMaskNodes(svg_mlayer)
            nr_of_masks[i] = mnode_nr
            mnode_idxs[i] = mnode_indexes
        if nr_of_masks["om"] != nr_of_masks["qm"]:
            occl_tp = "oa"
        else:
            occl_tp = "ao"
        return (occl_tp, mnode_idxs["om"])

    def getMaskNodes(self, mlayer):
        mnode_indexes = []
        for i, node in enumerate(mlayer.childNodes):
            if (node.nodeType == node.ELEMENT_NODE) and (node.nodeName != 'title'):
                mnode_indexes.append(i)
        return (mnode_indexes, len(mnode_indexes))

    def layerNodesFrom(self, svg_node):
        assert (svg_node.nodeType == svg_node.ELEMENT_NODE)
        assert (svg_node.nodeName == 'svg')
        layer_nodes = [node for node in svg_node.childNodes 
                            if node.nodeType == node.ELEMENT_NODE]
        assert (len(layer_nodes) >= 1)
        assert (layer_nodes[0].nodeName == 'g')
        return layer_nodes

def onIoConvert(self):
    mw = self.mw
    selected = self.selectedNotes()
    if not selected:
        tooltip("No cards selected.", period=2000)
        return
    conv = ImgOccNoteConverter(self)
    conv.convertNotes(selected)

def setupMenu(self):
    menu = self.form.menuEdit
    menu.addSeparator()
    a = menu.addAction('Convert to IO Enhanced notes (experimental)')
    self.connect(a, SIGNAL("triggered()"), lambda b=self: onIoConvert(b))

addHook("browser.setupMenus", setupMenu)