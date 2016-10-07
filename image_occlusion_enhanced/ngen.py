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
##              ngen.py is based on               ##
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

def genByKey(key, old_occl_tp):
    if key in ["Don't change"]:
        return genByKey(old_occl_tp, None)
    elif key in ["ao", "All Hidden, One Revealed"]:
        return IoGenAllHideOneReveal
    elif key in ["aa", "All Hidden, All Revealed"]:
        return IoGenAllHideAllReveal
    elif key in ["oa", "One Hidden, All Revealed"]:
        return IoGenOneHideAllReveal
    else:
        return IoGenAllHideOneReveal

class ImgOccNoteGenerator(object):
    def __init__(self, ed, svg, image_path, onote, tags, fields, did):
        self.ed = ed
        self.masks_svg = svg
        self.image_path = image_path
        self.onote = onote
        self.tags = tags
        self.fields = fields
        self.did = did
        self.qfill = '#' + mw.col.conf['imgocc']['qfill']
        self.model = mw.col.models.byName(IO_MODEL_NAME)
        if not self.model:
            self.model = template.add_io_model(mw.col)
        
    def generate_notes(self):
        self.uniq_id = str(uuid.uuid4()).replace("-","") 
        self.occl_id = '%s-%s' % (self.uniq_id, self.occl_tp)
        ( svg_node, layer_node ) = self._get_mnodes_and_set_ids()
        if not self.mnode_ids:
            tooltip("No cards to generate.<br>\
                Are you sure you set your masks correctly?")
            return
        self.masks_svg = svg_node.toxml() # write changes to svg
        self.omask_path = self._save_mask(self.masks_svg, self.occl_id, "O")
        qmasks = self._generate_mask_svgs_for("Q")
        amasks = self._generate_mask_svgs_for("A")
        col_image = self.add_image_to_col()
        for nr, idx in enumerate(self.mnode_indexes):
            note_id = self.mnode_ids[idx]
            self._save_mask_and_return_note(qmasks[nr], amasks[nr], 
                                                    col_image, note_id)
        parent = None
        if not self.ed.addMode:
            parent = self.ed.parentWindow
        tooltip("Cards added: %s" % len(qmasks), period=1500, parent=parent)

    def update_notes(self):
        self.uniq_id = self.onote['uniq_id']
        self.occl_id = '%s-%s' % (self.uniq_id, self.occl_tp)
        self._find_all_notes()
        ( svg_node, mlayer_node ) = self._get_mnodes_and_set_ids(True)
        if not self.mnode_ids:
            tooltip("No shapes to update.<br>\
                Are you sure you set your masks correctly?")
            return
        self._delete_and_id_notes(mlayer_node)
        self.masks_svg = svg_node.toxml() # write changes to svg
        self.omask_path = self._save_mask(self.masks_svg, self.occl_id, "O")
        qmasks = self._generate_mask_svgs_for("Q")
        amasks = self._generate_mask_svgs_for("A")
        col_image = self.image_path
        print "mnode_indexes", self.mnode_indexes
        for nr, idx in enumerate(self.mnode_indexes):
            print "nr", nr
            print "idx", idx
            note_id = self.mnode_ids[idx]
            print "note_id", note_id
            print "self.nids", self.nids
            nid = self.nids[note_id]
            print "nid", nid
            self._save_mask_and_return_note(qmasks[nr], amasks[nr],    
                                                col_image, note_id, nid)
        parent = self.ed.parentWindow
        tooltip("Cards updated: %s" % len(qmasks), period=1500, parent=parent)

    def _get_mnodes_and_set_ids(self, edit=False):
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
                if not edit:
                    self.mnode_ids[i] = "%s-%i" %(self.occl_id, len(self.mnode_indexes))
                    mlayer_node.childNodes[i].setAttribute("id", self.mnode_ids[i])
                else:
                    self.mnode_ids[i] = mlayer_node.childNodes[i].attributes["id"].value
        return (svg_node, mlayer_node)

    def find_by_noteid(self, note_id):
        query = "'%s':'%s*'" % ( IO_FLDS['note_id'], note_id )
        print "query", query
        res = mw.col.findNotes(query)
        return res

    def _find_all_notes(self):
        old_occl_id = '%s-%s' % (self.uniq_id, self.onote["occl_tp"])
        res = self.find_by_noteid(old_occl_id)
        print "res", res
        self.nids = {}
        for nid in res:
            print "nid", nid
            note_id = mw.col.getNote(nid)[IO_FLDS["note_id"]]
            self.nids[note_id] = nid

    def _delete_and_id_notes(self, mlayer_node):
        uniq_id = self.onote['uniq_id']
        mnode_ids = self.mnode_ids
        nids = self.nids

        # look for missing shapes by note_id
        valid_mnode_note_ids = filter (lambda x:x.startswith(uniq_id), mnode_ids.values())
        valid_nid_note_ids = filter (lambda x:x.startswith(uniq_id), nids.keys())
        # filter out notes that have already been deleted manually
        exstg_mnode_note_ids = [x for x in valid_mnode_note_ids if x in valid_nid_note_ids]
        exstg_mnode_note_nrs = sorted([int(i.split('-')[-1]) for i in exstg_mnode_note_ids])
        # determine available nrs available for note numbering
        max_mnode_note_nr = int(exstg_mnode_note_nrs[-1])
        full_range = range(1, max_mnode_note_nr+1)
        available_nrs = set(full_range) - set(exstg_mnode_note_nrs)
        available_nrs = sorted(list(available_nrs))

        print '--------------------'
        print "nids", nids
        print "nids.keys", nids.keys()
        print "valid_mnode_note_ids", valid_mnode_note_ids
        print "exstg_mnode_note_nrs", exstg_mnode_note_nrs
        print "max_mnode_note_nr", max_mnode_note_nr
        print "full_range", full_range
        print "available_nrs", available_nrs
        print '--------------------'

        # compare note_ids as present in note collection with masks on svg
        deleted_note_ids = set(valid_nid_note_ids) - set(valid_mnode_note_ids)
        deleted_note_ids = sorted(list(deleted_note_ids))
        del_count = len(deleted_note_ids)
        # set notes of missing masks on svg to be deleted
        deleted_nids = [nids[x] for x in deleted_note_ids]

        print "##########################"
        print "valid_nid_note_ids", valid_nid_note_ids
        print "deleted_note_ids", deleted_note_ids
        print "deleted_nids", deleted_nids
        print "edited nids", nids
        print "##########################"

        # add note_id to missing shapes
        note_nr_max = max_mnode_note_nr
        new_count = 0
        for nr, idx in enumerate(self.mnode_indexes):
            mnode_id = mnode_ids[idx]
            new_mnode_id = None
            if mnode_id not in exstg_mnode_note_ids:
                if available_nrs:
                    # use gap in note_id numbering
                    note_nr = available_nrs.pop(0)
                else:
                    # increment maximum note_id number
                    note_nr_max = note_nr_max +1
                    note_nr = note_nr_max
                new_mnode_id = self.occl_id + '-' + str(note_nr)
                new_count += 1
                nids[new_mnode_id] = None
            if new_mnode_id:
                mlayer_node.childNodes[idx].setAttribute("id", new_mnode_id)
                self.mnode_ids[idx] = new_mnode_id
            print "====================="
            print "nr", nr
            print "idx", idx
            print "mnode_id", mnode_id
            print "available_nrs", available_nrs
            print "note_nr_max", note_nr_max
            print "new_mnode_id", new_mnode_id
            print "====================="


        print "Insert dialog here: This will delete %i card(s) \
                    and create %i new one(s). Proceed?" % (del_count, new_count)

        # no checkpoints available in editcurrent, sadly
        #mw.checkpoint(_("Edit Image Occlusion"))
        #model.beginReset()
        if deleted_nids:
            mw.col.remNotes(deleted_nids)

        return True

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

    def _save_mask(self, mask, note_id, mtype):
        print "saving", note_id, mtype
        mask_path = '%s-%s.svg' % (note_id, mtype)
        mask_file = open(mask_path, 'w')
        mask_file.write(mask)
        mask_file.close()
        return mask_path

    def fname2img(self, path):
        return '<img src="%s" />' % os.path.split(path)[1]

    def _save_mask_and_return_note(self, qmask, amask, col_image, note_id, nid=None):
        qmask_path = self._save_mask(qmask, note_id, "Q")
        amask_path = self._save_mask(amask, note_id, "A")
        omask_path = self.omask_path

        model = self.model
        model['did'] = self.did
        fields = self.fields

        if nid:
            note = mw.col.getNote(nid)
        else:
            note = Note(mw.col, model)

        # define fields we just generated
        fields[IO_FLDS['note_id']] = note_id
        fields[IO_FLDS['image']] = self.fname2img(col_image)
        fields[IO_FLDS['qmask']] = self.fname2img(qmask_path)
        fields[IO_FLDS['amask']] = self.fname2img(amask_path)
        fields[IO_FLDS['omask']] = self.fname2img(omask_path)

        # add fields to note
        note.tags = self.tags
        for i in IO_FLDS.values():
            note[i] = fields[i]

        if nid:
            note.flush()
            print "noteflush", note
        else:
            print "notecreate", note
            mw.col.addNote(note)


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
