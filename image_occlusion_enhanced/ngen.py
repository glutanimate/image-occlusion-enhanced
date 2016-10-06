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
##  --------------------------------------------  ##
##                                                ##
##            Notegen.py is based on              ##
##           Simple Picture Occlusion             ##
##                   which is                     ##
##          Copyright (c) 2013 SteveAW            ##
##             (steveawa@gmail.com)               ##
##                                                ##
####################################################

import os

from aqt.qt import *
from aqt import mw
from aqt.utils import tooltip
from anki.notes import Note

from xml.dom import minidom
from Imaging.PIL import Image 
import uuid
import shutil
import base64

from config import *
import template

# Explanation of some of the variables:
#
# nid:          Note ID set by Anki
# note_id:      Image Occlusion Note ID set as the first field of each IO note
# uniq_id:      Unique sequence of random characters. First part of the note_id
# occl_tp:      Two-letter code that signifies occlusion type. Second part of
#               the note_id
# occl_id:      Combination of uniq_id + occl_tp - unique identifier shared 
#               by all notes created in one IO session
# note_nr:      Third part of the note_id

stripattr = ['opacity', 'stroke-opacity', 'fill-opacity']

def imageProp(image_path):
    image = Image.open(image_path)
    width, height = image.size
    return width, height

def svgToBase64(svg_path):
    doc = minidom.parse(svg_path)
    svg_node = doc.documentElement
    svg_content = svg_node.toxml()
    svg_b64 = "data:image/svg+xml;base64," + base64.b64encode(svg_content)
    return svg_b64

def genByKey(key):
    if key in ["ao", "All Hidden, One Revealed"]:
        return IoGenAllHideOneReveal
    elif key in ["aa", "All Hidden, All Revealed"]:
        return IoGenAllHideAllReveal
    elif key in ["oa", "One Hidden, All Revealed"]:
        return IoGenOneHideAllReveal

class ImgOccNoteGenerator(object):
    def __init__(self, ed, svg, image_path, onote, tags, fields, did):
        self.ed = ed
        self.masks_svg = svg
        self.image_path = image_path
        self.onote = onote
        self.tags = tags
        self.fields = fields
        self.did = did
        self.edit = False
        self.qfill = '#' + mw.col.conf['imgocc']['qfill']
        
    def generate_notes(self):
        self.uniq_id = str(uuid.uuid4()).replace("-","") 
        self.occl_id = '%s-%s' % (self.uniq_id, self.occl_tp)
        self._get_mnodes()
        if not self.mnode_ids:
            tooltip("No cards to generate.<br>\
                Are you sure you set your masks correctly?")
            return
        qmasks = self._generate_mask_svgs_for("Q")
        amasks = self._generate_mask_svgs_for("A")
        col_image = self.add_image_to_col()
        self.omask_path = self._save_mask(self.masks_svg, self.occl_id, "O")
        for i in range(len(qmasks)):
            note_id = '%s-%s' % (self.occl_id, i+1) # start from 1
            self._save_mask_and_write_note(qmasks[i], amasks[i], col_image, note_id)
        tooltip("Cards added: %s" % len(qmasks), period=1500)

    def update_notes(self):
        self.uniq_id = self.onote['uniq_id']
        self.occl_id = '%s-%s' % (self.uniq_id, self.occl_tp)
        self.edit = True
        self._find_all_notes()
        ( svg_node, mlayer_node ) = self._get_mnodes()
        if not self.mnode_ids:
            tooltip("No shapes to update.<br>\
                Are you sure you set your masks correctly?")
            return
        self._delete_unused_notes()
        self._prepare_svg(svg_node, mlayer_node)
        qmasks = self._generate_mask_svgs_for("Q")
        amasks = self._generate_mask_svgs_for("A")            
        for i in range(len(qmasks)):
            note_id = '%s-%s' % (self.occl_id, i+1) # start from 1
            self._save_mask_and_write_note(qmasks[i], amasks[i], col_image, note_id)
        parent = self.ed.parentWindow
        QWebSettings.clearMemoryCaches() # refreshes webview image caches
        mw.reset()
        self.ed.loadNote()
        tooltip("Cards updated: %s" % len(qmasks), period=1500, parent=self.ed)

    def _get_mnodes(self):
        self.mnode_indexes = []
        self.mnode_ids = {}
        mask_doc = minidom.parseString(self.masks_svg)
        svg_node = mask_doc.documentElement
        layer_notes = self._layer_notes_from(svg_node)
        mlayer_node = layer_notes[-1] # treat topmost layer as masks layer
        for i, node in enumerate(mlayer_node.childNodes):
            # minidom doesn't offer a childElements method and childNodes
            # also returns whitespace found in the mlayer_node as a child node. 
            # For that reason we use self.mnode_indexes to register all 
            # indexes of mlayer_node children that contain actual elements, 
            # i.e. mask nodes
            if (node.nodeType == node.ELEMENT_NODE) and (node.nodeName != 'title'):
                self.mnode_indexes.append(i)
                self.remove_attribs_recursively(mlayer_node.childNodes[i], stripattr)
                self.mnode_ids[i] = mlayer_node.childNodes[i].attributes["id"].value
        if self.edit:
            return (svg_node, mlayer_node)

    def find_by_noteid(self, note_id):
        query = "'%s':'%s'" % ( IO_FLDS['note_id'], note_id )
        res = mw.col.findNotes(query)
        return res

    def _find_all_notes(self):
        res = self.find_by_noteid(self.occl_id)
        note_cnt = len(res)
        self.nids = {}
        for nid in res:
            note_id = mw.col.getNote(i)[IO_FLDS["note_id"]]
            self.nids[note_id] = nid

    def _delete_unused_notes(self):
        valid_mnode_note_ids = filter (lambda x:x.startswith(self.onote['uniq_id']) , self.mnode_ids.values()) 
        valid_mnode_note_nrs = sorted([i.split('-')[-1] for i in valid_mnode_note_ids()])
        max_mnode_note_nr = valid_mnode_nrs[-1]
        full_range = range(1, max_mnode_note_nr)
        availbl = set(full_range) - set(valid_mnode_note_nrs)


    def _prepare_svg(self, svg_node, mlayer_node):
        ( avlbl_nrs, max_nr) = self._delete_unused_notes() 
        for nr, idx in enumerate(self.mnode_indexes):
            # remove attributes that could cause issues later on:
            self.remove_attribs_recursively(mlayer_node.childNodes[idx], stripattr)
            if not self.edit:
                new_mnode_id = self.occl_id + '-' + str(nr+1)
                mlayer_node.childNodes[i].setAttribute("id", new_mnode_id)
                continue
            mnode_id = self.mnode_ids[i]
            mnode_id_uniq = mnode_id.split('-')[0]
            if mnode_id_uniq == self.onote['uniq_id']:
                # reuse old ID
                new_mnode_id = None
            elif not incrmax:
                # use possibly missing IDs
                # note_nrs = sorted([i.split('-')[-1] for i in self.nids.keys()])
                # max_note_nr = note_nrs[-1]
                # full_range = range(1, max_note_nr)
                # availbl = set(full_range) - set(note_nrs)
                if availbl:
                    new_mnode_id = self.occl_id + '-' + str(availbl)
                else:
                    incrmax = max_note_nr + 1
                    new_mnode_id = self.occl_id + '-' + str(incrmax)
            else:
                pass

            if self.mnode_ids[i] not in self.nids.values():
                self.nids

            if new_mnode_id:
                mlayer_node.childNodes[i].setAttribute("id", new_mnode_id)

        # write changes to masks_svg:
        self.masks_svg = svg_node.toxml()    

    def add_image_to_col(self):
        media_dir = mw.col.media.dir()
        fn = os.path.basename(self.image_path)
        name, ext = os.path.splitext(fn)
        short_name = name[:75] if len(name) > 75 else name
        unique_fn = self.uniq_id + '_' + short_name + ext
        new_path = os.path.join(media_dir, unique_fn)
        shutil.copyfile(self.image_path, new_path)
        return new_path

    def _generate_mask_svgs(self, side):
        masks = self._generate_mask_svgs_for(side)
        return masks

    def _generate_mask_svgs_for(self, side):
        masks = [self._create_mask(side, node_index) for node_index in self.mnode_indexes]
        return masks

    def _create_mask(self, side, mask_node_index):
        mask_doc = minidom.parseString(self.masks_svg)
        svg_node = mask_doc.documentElement
        layer_notes = self._layer_notes_from(svg_node)
        mlayer_node = layer_notes[-1] # treat topmost layer as masks layer
        #This methods get implemented different by subclasses
        self._create_mask_at_layernode(side, mask_node_index, mlayer_node)
        return svg_node.toxml()

    def _create_mask_at_layernode(self, mask_node_index, mlayer_node):
        raise NotImplementedError

    def set_q_attribs(self, node):
        # set element class
        node.setAttribute("class", "qshape")
        # set element color
        if (node.nodeType == node.ELEMENT_NODE):
            if node.hasAttribute("fill"):
                node.setAttribute("fill", self.qfill)
            map(self.set_q_attribs, node.childNodes)

    def remove_attribs_recursively(self, node, attrs):
        if (node.nodeType == node.ELEMENT_NODE):
            for i in attrs:
                if node.hasAttribute(i):
                    node.removeAttribute(i)
            map(self.remove_attribs_recursively, node.childNodes)

    def _layer_notes_from(self, svg_node):
        assert (svg_node.nodeType == svg_node.ELEMENT_NODE)
        assert (svg_node.nodeName == 'svg')
        layer_notes = [node for node in svg_node.childNodes if node.nodeType == node.ELEMENT_NODE]
        assert (len(layer_notes) >= 1)
        assert (layer_notes[0].nodeName == 'g')
        return layer_notes

    def _save_mask(self, mask, id, mtype):
        mask_path = '%s-%s.svg' % (id, mtype)
        mask_file = open(mask_path, 'w')
        mask_file.write(mask)
        mask_file.close()
        return mask_path

    def _save_mask_and_write_note(self, qmask, amask, col_image, note_id):
        qmask_path = self._save_mask(qmask, note_id, "Q")
        amask_path = self._save_mask(amask, note_id, "A")
        model = mw.col.models.byName(IO_MODEL_NAME)
        fields = self.fields
        if not model:
            model = template.add_io_model(mw.col)
        model['did'] = self.did

        if not self.edit:
            note = Note(mw.col, model)
        else:
            res = self.find_by_noteid(note_id)
            print note_id
            print res
            if res:
                note = mw.col.getNote(res[0])
            else:
                note = Note(mw.col, model)

        def fname2img(path):
            return '<img src="%s" />' % os.path.split(path)[1]

        # define fields we just generated
        fields[IO_FLDS['note_id']] = note_id
        fields[IO_FLDS['image']] = fname2img(col_image)
        fields[IO_FLDS['qmask']] = fname2img(qmask_path)
        fields[IO_FLDS['amask']] = fname2img(amask_path)
        fields[IO_FLDS['omask']] = fname2img(self.omask_path)

        # add fields to note
        for i in IO_FLDORDER:
            fldlabel = IO_FLDS[i]
            note[fldlabel] = fields[fldlabel]

        note.tags = self.tags

        if self.edit and res:
            note.flush()
            return

        mw.col.addNote(note)
        if not self.edit:
            deck = mw.col.decks.nameOrNone(self.did)
            self.ed.parentWindow.deckChooser.deck.setText(deck)

class IoGenAllHideOneReveal(ImgOccNoteGenerator):
    """Q: All hidden, A: One revealed ('nonoverlapping')"""
    def __init__(self, ed, svg, image_path, onote, tags, fields, did):
        self.occl_tp = "ao"
        ImgOccNoteGenerator.__init__(self, ed, svg, image_path, 
                                        onote, tags, fields, did)

    def _create_mask_at_layernode(self, side, mask_node_index, mlayer_node):
        for i in self.mnode_indexes:
            if i == mask_node_index:
                if side == "Q":
                    self.set_q_attribs(mlayer_node.childNodes[i])
                if side == "A":
                    mlayer_node.removeChild(mlayer_node.childNodes[i])

class IoGenAllHideAllReveal(ImgOccNoteGenerator):
    """Q: All hidden, A: All revealed"""
    def __init__(self, ed, svg, image_path, onote, tags, fields, did):
        self.occl_tp = "aa"
        ImgOccNoteGenerator.__init__(self, ed, svg, image_path, 
                                        onote, tags, fields, did)

    def _create_mask_at_layernode(self, side, mask_node_index, mlayer_node):
        for i in reversed(self.mnode_indexes):
            if side == "Q":
                if i == mask_node_index:
                    self.set_q_attribs(mlayer_node.childNodes[i])
            else:
                mlayer_node.removeChild(mlayer_node.childNodes[i])

class IoGenOneHideAllReveal(ImgOccNoteGenerator):
    """Q: One hidden, A: All revealed ('overlapping')"""
    def __init__(self, ed, svg, image_path, onote, tags, fields, did):
        self.occl_tp = "oa"
        ImgOccNoteGenerator.__init__(self, ed, svg, image_path, 
                                        onote, tags, fields, did)

    def _create_mask_at_layernode(self, side, mask_node_index, mlayer_node):
        for i in reversed(self.mnode_indexes):
            if i == mask_node_index and side == "Q":
                self.set_q_attribs(mlayer_node.childNodes[i])
                mlayer_node.childNodes[i].setAttribute("class", "qshape")
            else:
                mlayer_node.removeChild(mlayer_node.childNodes[i])
