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
from dialogs import ioAskUser
from utils import img2path, fname2img

class ImgOccNoteConverter(object):
    def __init__(self, browser):
        self.browser = browser
        self.occl_id_last = None
        loadConfig(self)

    def convertNotes(self, nids):
        (io_nids, skipped) = self.filterByModel(nids)
        for nid in io_nids:
            note = mw.col.getNote(nid)
            (uniq_id, note_nr) = self.getDataFromNamingScheme(note)
            occl_tp = self.getOcclTypeAndMnodes(note)
            occl_id = uniq_id + '-' + occl_tp
            if occl_id == self.occl_id_last:
                print "Skipping note that has already been converted"
                continue
            self.occl_id_last = occl_id
            family_nids = self.findByNoteId(uniq_id)
            self.idAndCorrelateNotes(family_nids, occl_id)
        tooltip("<b>%i</b> notes updated, <b>%i</b> skipped" % (len(io_nids), skipped))

    def filterByModel(self, nids):
        io_nids = []
        skipped = 0
        for nid in nids:
            note = mw.col.getNote(nid)
            if note.model() != self.model:
                print "Skipping note with wrong note type:", nid
                skipped +=1
                continue
            else:
                if not note[self.ioflds['id']]:
                    print "Found IO note in need of update:", nid
                    io_nids.append(nid)
                else:
                    print "Skipping IO note that is already editable:", nid
                    skipped +=1
                
        return (io_nids, skipped)

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

    def idAndCorrelateNotes(self, nids, occl_id):
        nids_by_nr = {}
        self.occl_id_last = occl_id
        for nid in nids:
            note = mw.col.getNote(nid)
            (uniq_id, note_nr) = self.getDataFromNamingScheme(note)
            nids_by_nr[int(note_nr)] = nid

        print "occl_id", occl_id
        print "nids_by_nr", nids_by_nr

        for nr in sorted(nids_by_nr.keys()):
            midx = self.mnode_idxs[nr]
            nid = nids_by_nr[nr]
            print "nr", nr
            print "midx", midx
            print "nid", nid
            note = mw.col.getNote(nid)
            print "note", note
            new_mnode_id =  occl_id + '-' + str(nr+1)
            print "new_mnode_id", new_mnode_id
            self.mnode.childNodes[midx].setAttribute("id", new_mnode_id)
            note[self.ioflds['id']] = new_mnode_id
            note.flush()

        new_svg = self.svg_node.toxml()
        print "new_svg"
        print new_svg
        omask_path = self._saveMask(new_svg, occl_id, "O")
        print "omask_path", omask_path

        for nid in nids_by_nr.values():
            print "nid", nid
            note = mw.col.getNote(nid)
            note[self.ioflds['om']] = fname2img(omask_path)
            note.addTag(".io-converted")
            note.flush()

    def getOcclTypeAndMnodes(self, note):
        nr_of_masks = {}
        mnode_idxs = {}
        svg_mlayer = {}
        for i in ["qm", "om"]:
            svg_file = img2path(note[self.ioflds[i]], True)
            (svg_node, svg_mlayer, midxs) = self.readSvgAndGetMlayer(svg_file)
            nr_of_masks[i] = len(midxs)
        self.svg_node = svg_node
        self.mnode = svg_mlayer
        self.mnode_idxs = midxs
        if nr_of_masks["om"] != nr_of_masks["qm"]:
            occl_tp = "oa"
        else:
            occl_tp = "ao"

        self.svg_node = svg_node
        self.mnode = svg_mlayer
        self.mnode_idxs = midxs

        return occl_tp

    def readSvgAndGetMlayer(self, svg_file):
        svg_doc = minidom.parse(svg_file)
        # ugly workaround for wrong namespace in older IO notes:
        svg_string = svg_doc.toxml().replace('ns0:', '').replace(':ns0','')
        svg_doc = minidom.parseString(svg_string)
        svg_node = svg_doc.documentElement
        svg_mlayer = self.layerNodesFrom(svg_node)[-1]
        mnode_indexes = self.getMaskNodes(svg_mlayer)

        return (svg_node, svg_mlayer, mnode_indexes)

    def getMaskNodes(self, mlayer):
        mnode_indexes = []
        for i, node in enumerate(mlayer.childNodes):
            if (node.nodeType == node.ELEMENT_NODE) and (node.nodeName != 'title'):
                mnode_indexes.append(i)
        return mnode_indexes

    def layerNodesFrom(self, svg_node):
        assert (svg_node.nodeType == svg_node.ELEMENT_NODE)
        assert (svg_node.nodeName == 'svg')
        layer_nodes = [node for node in svg_node.childNodes 
                            if node.nodeType == node.ELEMENT_NODE]
        assert (len(layer_nodes) >= 1)
        assert (layer_nodes[0].nodeName == 'g')
        return layer_nodes

    def _saveMask(self, mask, note_id, mtype):
        print "!saving %s, %s" % (note_id, mtype)
        mask_path = '%s-%s.svg' % (note_id, mtype)
        mask_file = open(mask_path, 'w')
        mask_file.write(mask)
        mask_file.close()
        return mask_path

def onIoConvert(self):
    mw = self.mw
    selected = self.selectedNotes()
    if not selected:
        tooltip("No cards selected.", period=2000)
        return
    question = u"""\
    This is a purely <b>experimental</b> feature that is meant to update older \
    IO notes to be compatible with the new editing feature-set in IO Enhanced. \
    Clicking on 'Yes' below will prompt the add-on to go through all selected \
    notes and change their Note ID and mask files in a way that should make it \
    possible to edit them in the future. \
    <br><br>Please note that this will only work for notes \
    that have already been switched to the <i>Image Occlusion Enhanced</i> note type.\
    If you are coming from IO 2.0 or an older version of IO Enhanced you will \
    first have to switch the note type of your notes manually by going to <i>Edit → \
    Change Note Type.</i><br><br> \
    <b>WARNING</b>: There is no guarantee that this feature will actually succeed in \
    updating your notes properly. To convert legacy notes the add-on will have to \
    make a few assumptions which in some rare instances might turn out to be wrong \
    and lead to broken notes. <br>A checkpoint will be set to revert to if needed, \
    but even with that safety measure in place you should still only use this \
    function if you know what you are doing.\
    <br><br><b>Continue anyway?</b><br><i>(Depending on the number of notes this might \
    take a while)</i>
    """
    ret = ioAskUser(question, "Please confirm action", self, defaultno=True)
    if not ret:
        return False
    mw.progress.start()
    mw.checkpoint("Image Occlusion Note Conversions")
    self.model.beginReset()
    conv = ImgOccNoteConverter(self)
    conv.convertNotes(selected)
    self.model.endReset()
    mw.col.reset()
    mw.reset()
    mw.progress.finish()

def setupMenu(self):
    menu = self.form.menuEdit
    menu.addSeparator()
    a = menu.addAction('Convert to Editable IO &Enhanced Notes')
    self.connect(a, SIGNAL("triggered()"), lambda b=self: onIoConvert(b))

addHook("browser.setupMenus", setupMenu)