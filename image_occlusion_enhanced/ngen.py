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
import random
import string
import copy
from aqt import mw
from xml.dom import minidom
from anki.notes import Note
from aqt.utils import tooltip, showInfo, showWarning, saveGeom, restoreGeom

from config import *
import tempfile
import sys
import uuid
import shutil

stripattr = ['opacity', 'stroke-opacity', 'fill-opacity']

def genByKey(key):
    if key in ["ao", "All Hidden, One Revealed"]:
        return IoGenAllHideOneReveal
    elif key in ["aa", "All Hidden, All Revealed"]:
        return IoGenAllHideAllReveal
    elif key in ["oa", "One Hidden, All Revealed"]:
        return IoGenOneHideAllReveal

class ImgOccNoteGenerator(object):
    def __init__(self, image, svg, tags, header, footer, remarks, sources, 
                      extra1, extra2, did):
        self.image_path = image
        self.masks_svg = svg
        #self.fields = fields
        self.oid = str(uuid.uuid4()).replace("-","")
        self.tags = tags
        self.header = header
        self.footer = footer
        self.remarks = remarks
        self.sources = sources
        self.extra1 = extra1
        self.extra2 = extra2
        self.did = did
        self.omask_path = None
        self.uniq = '%s-%s' % (self.oid, self.otype)
        self.qfill = '#' + mw.col.conf['imgocc']['qfill']

    def generate_notes(self):
        qmasks = self._generate_mask_svgs("Q")
        if not qmasks:
            tooltip("No cards generated.<br>\
                Are you sure you set your masks?")
            return
        amasks = self._generate_mask_svgs("A")
        col_image = self.add_image_to_col()
        self.omask_path = self._save_mask(self.masks_svg, self.uniq, "O")
        for i in range(len(qmasks)):
            card_id = '%s-%s' % (self.uniq, i+1) # start from 1
            self._save_mask_and_write_note(qmasks[i], amasks[i], col_image, card_id)
        tooltip(("Cards added: %s" % len(qmasks) ), period=1500)

    def add_image_to_col(self):
        media_dir = mw.col.media.dir()
        fn = os.path.basename(self.image_path)
        name, ext = os.path.splitext(fn)
        short_name = name[:75] if len(name) > 75 else name
        unique_fn = self.oid + '_' + short_name + ext
        new_path = os.path.join(media_dir, unique_fn)
        shutil.copyfile(self.image_path, new_path)
        return new_path

    def modify_fill_recursively(self, node):
        if (node.nodeType == node.ELEMENT_NODE):
            if node.hasAttribute("fill"):
                node.setAttribute("fill", self.qfill)
            map(self.modify_fill_recursively, node.childNodes)

    def remove_attrs_recursively(self, node, attrs):
        if (node.nodeType == node.ELEMENT_NODE):
            for i in attrs:
                if node.hasAttribute(i):
                    node.removeAttribute(i)
            map(self.modify_fill_recursively, node.childNodes)

    def _generate_mask_svgs(self, side):
        #Note this gets reimplemented by ImgOccNoteGeneratorSingle
        #which returns the original mask unmodified
        mask_doc = minidom.parseString(self.masks_svg)
        svg_node = mask_doc.documentElement
        #layer_nodes = self._layer_nodes_from(svg_node)
        #assume all masks are on a single layer
        layer_node = self._layer_nodes_from(svg_node)
        mask_node_indexes = []
        #todo: iter
        for i in range(len(layer_node.childNodes)):
            node = layer_node.childNodes[i]
            if (node.nodeType == node.ELEMENT_NODE) and (node.nodeName != 'title'):
                # mask_node_indexes contains the indexes of the childNodes that are elements:
                mask_node_indexes.append(i)
                # set IDs for each element childNote in the masks layer:
                layer_node.childNodes[i].setAttribute("id", self.uniq + '-' + str(len(mask_node_indexes)))
                # remove attributes that could cause issues later on:
                self.remove_attrs_recursively(layer_node.childNodes[i], stripattr)
        # write changes to masks_svg:
        self.masks_svg = svg_node.toxml()
        masks = self._generate_mask_svgs_for(side, mask_node_indexes)
        return masks

    def _generate_mask_svgs_for(self, side, mask_node_indexes):
        masks = [self._create_mask(side, node_index, mask_node_indexes) for node_index in mask_node_indexes]
        return masks

    def _create_mask(self, side, mask_node_index, all_mask_node_indexes):
        mask_doc = minidom.parseString(self.masks_svg)
        svg_node = mask_doc.documentElement
        #layer_nodes = self._layer_nodes_from(svg_node)
        #layer_node = layer_nodes[0]
        layer_node = self._layer_nodes_from(svg_node)
        #This methods get implemented different by subclasses
        self._create_mask_at_layernode(side, mask_node_index, all_mask_node_indexes, layer_node)
        return svg_node.toxml()

    def _create_mask_at_layernode(self, mask_node_index, all_mask_node_indexes, layer_node):
        raise NotImplementedError

    def _layer_nodes_from(self, svg_node):
        #TODO: understand this better
        assert (svg_node.nodeType == svg_node.ELEMENT_NODE)
        assert (svg_node.nodeName == 'svg')
        layer_nodes = [node for node in svg_node.childNodes if node.nodeType == node.ELEMENT_NODE]
        # layer_notes = layer_nodes[1]
        # print layer_nodes[1]
        # assert (len(layer_nodes) == 1)
        # assert (layer_nodes[0].nodeName == 'g')
        return layer_nodes[1]

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
        model['did'] = self.did
        new_note = Note(mw.col, model)

        def fname2img(path):
            return '<img src="%s" />' % os.path.split(path)[1]

        new_note.fields = [
                    note_id,
                    self.header,
                    fname2img(col_image),
                    self.footer,
                    self.remarks,
                    self.sources,
                    self.extra1,
                    self.extra2,
                    fname2img(qmask_path),
                    fname2img(amask_path),
                    fname2img(self.omask_path)
                    ]

        for tag in self.tags:
            new_note.addTag(tag)

        mw.col.addNote(new_note)

class IoGenAllHideOneReveal(ImgOccNoteGenerator):
    """Q: All hidden, A: One revealed ('nonoverlapping')"""

    def __init__(self, image, svg, tags, header, footer, remarks, sources, 
                      extra1, extra2, did):
        self.otype = "ao"
        ImgOccNoteGenerator.__init__(self, image, svg, tags, header, footer, remarks, sources, 
                      extra1, extra2, did)
        

    def _create_mask_at_layernode(self, side, mask_node_index, all_mask_node_indexes, layer_node):
        for i in all_mask_node_indexes:
            if i == mask_node_index:
                if side == "Q":
                    self.modify_fill_recursively(layer_node.childNodes[i])
                    layer_node.childNodes[i].setAttribute("class", "qshape")
                if side == "A":
                    layer_node.removeChild(layer_node.childNodes[i])

class IoGenAllHideAllReveal(ImgOccNoteGenerator):
    """Q: All hidden, A: All revealed"""

    def __init__(self, image, svg, tags, header, footer, remarks, sources, 
                      extra1, extra2, did):
        self.otype = "aa"
        ImgOccNoteGenerator.__init__(self, image, svg, tags, header, footer, remarks, sources, 
                      extra1, extra2, did)
        

    def _create_mask_at_layernode(self, side, mask_node_index, all_mask_node_indexes, layer_node):
        for i in reversed(all_mask_node_indexes):
            if side == "Q":
                if i == mask_node_index:
                    self.modify_fill_recursively(layer_node.childNodes[i])
                    layer_node.childNodes[i].setAttribute("class", "qshape")
            else:
                layer_node.removeChild(layer_node.childNodes[i])

class IoGenOneHideAllReveal(ImgOccNoteGenerator):
    """Q: One hidden, A: All revealed ('overlapping')"""
    def __init__(self, image, svg, tags, header, footer, remarks, sources, 
                      extra1, extra2, did):
        self.otype = "oa"
        ImgOccNoteGenerator.__init__(self, image, svg, tags, header, footer, remarks, sources, 
                      extra1, extra2, did)
        

    def _create_mask_at_layernode(self, side, mask_node_index, all_mask_node_indexes, layer_node):
        for i in reversed(all_mask_node_indexes):
            if i == mask_node_index and side == "Q":
                self.modify_fill_recursively(layer_node.childNodes[i])
                layer_node.childNodes[i].setAttribute("class", "qshape")
            else:
                layer_node.removeChild(layer_node.childNodes[i])
