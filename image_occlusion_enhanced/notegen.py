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

class ImgOccNoteGenerator(object):
    def __init__(self, ed, image, svg, tags, header, footer, remarks, sources, 
                      extra1, extra2, did):
        #image_path  is fully qualified path + filename
        self.image_path = image
        self.current_editor = ed
        self.masks_svg = svg
        #self.fields = fields
        self.uniq = str(uuid.uuid4()).replace("-","")
        self.tags = tags
        self.header = header
        self.footer = footer
        self.remarks = remarks
        self.sources = sources
        self.extra1 = extra1
        self.extra2 = extra2
        self.did = did

    def generate_notes(self):
        masks = self._generate_mask_svgs()
        #todo: if no notes, delete the image?
        self.image_path = self.add_image_to_col()
        for i in range(len(masks)):
            self._save_mask_and_write_note(i, masks[i])
        tooltip(("Cards added: %s" % len(masks) ), period=1500, parent=self.current_editor.parentWindow)

    def add_image_to_col(self):
        tmp_media_dir = tempfile.mkdtemp(prefix="imgocc")
        media_dir = mw.col.media.dir()
        fn = os.path.basename(self.image_path)
        unique_fn = self.uniq + '_' + fn
        new_path = os.path.join(media_dir, unique_fn)
        shutil.copyfile(self.image_path, new_path)
        return new_path
        # shutil.copy(self.image_path, tmp_media_dir)
        # os.rename(os.path.join(tmp_media_dir, bname),
        #           os.path.join(tmp_media_dir, hash_bname))
        # new_path = os.path.join(tmp_media_dir, hash_bname)
        # mw.col.media.addFile(path.decode(IO_ENCODING))

    def _generate_mask_svgs(self):
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
                mask_node_indexes.append(i)
                # mask_node_indexes contains the indexes of the childNodes that are elements
            # assume that all are masks. Different subclasses do different things with them
        masks = self._generate_mask_svgs_for(mask_node_indexes)
        return masks

    def _generate_mask_svgs_for(self, mask_node_indexes):
        masks = [self._create_mask(node_index, mask_node_indexes) for node_index in mask_node_indexes]
        return masks

    def _create_mask(self, mask_node_index, all_mask_node_indexes):
        mask_doc = minidom.parseString(self.masks_svg)
        svg_node = mask_doc.documentElement
        #layer_nodes = self._layer_nodes_from(svg_node)
        #layer_node = layer_nodes[0]
        layer_node = self._layer_nodes_from(svg_node)
        #This methods get implemented different by subclasses
        self._create_mask_at_layernode(mask_node_index, all_mask_node_indexes, layer_node)
        return svg_node.toxml()

    def _create_mask_at_layernode(self, mask_node_index, all_mask_node_indexes, layer_node):
        raise NotImplementedError

    def _layer_nodes_from(self, svg_node):
        assert (svg_node.nodeType == svg_node.ELEMENT_NODE)
        assert (svg_node.nodeName == 'svg')
        layer_nodes = [node for node in svg_node.childNodes if node.nodeType == node.ELEMENT_NODE]
        print layer_nodes[1].toxml()
        # layer_notes = layer_nodes[1]
        # print layer_nodes[1]
        # assert (len(layer_nodes) == 1)
        # assert (layer_nodes[0].nodeName == 'g')
        return layer_nodes[1]

    def _save_mask(self, mask, note_number):
        otype = "no"
        mtype = "q"
        mask_path = '%s-%s-%s-%s.svg' % (self.uniq, otype, note_number, mtype)
        mask_file = open(mask_path, 'w')
        mask_file.write(mask)
        mask_file.close()
        return mask_path

    def _save_mask_and_write_note(self, note_number, mask):
        mask_path = self._save_mask(mask, note_number)
        #see anki.collection._Collection#_newCard
        model = mw.col.models.byName(IO_MODEL_NAME)
        model['did'] = self.did
        new_note = Note(mw.col, model)

        def fname2img(path):
            return '<img src="%s" />' % os.path.split(path)[1]

        new_note.fields = [
                    self.uniq,
                    self.header,
                    fname2img(self.image_path),
                    self.footer,
                    self.remarks,
                    self.sources,
                    self.extra1,
                    self.extra2,
                    fname2img(mask_path),
                    "",
                    fname2img(mask_path)
                    ]

        for tag in self.tags:
            new_note.addTag(tag)

        mw.col.addNote(new_note)


class ImgOccNoteGeneratorSeparate(ImgOccNoteGenerator):
    """Each top level element of the layer becomes a separate mask"""

    def __init__(self, ed, image, svg, tags, header, footer, remarks, sources, 
                      extra1, extra2, did):
        ImgOccNoteGenerator.__init__(self, ed, image, svg, tags, header, footer, remarks, sources, 
                      extra1, extra2, did)

    def _create_mask_at_layernode(self, mask_node_index, all_mask_node_indexes, layer_node):
        #Delete all child nodes except for mask_node_index
        for i in reversed(all_mask_node_indexes):
            if not i == mask_node_index:
                layer_node.removeChild(layer_node.childNodes[i])


class ImgOccNoteGeneratorHiding(ImgOccNoteGenerator):
    """Each top level element of the layer becomes a separate mask
    + the other elements are hidden"""

    def __init__(self, ed, image, svg, tags, header, footer, remarks, sources, 
                      extra1, extra2, did):
        ImgOccNoteGenerator.__init__(self, ed, image, svg, tags, header, footer, remarks, sources, 
                      extra1, extra2, did)

    def _create_mask_at_layernode(self, mask_node_index, all_mask_node_indexes, layer_node):
        def modify_fill_recursively(node):
            if (node.nodeType == node.ELEMENT_NODE):
                if node.hasAttribute("fill"):
                    node.setAttribute("fill", "#aaffff")
                map(modify_fill_recursively, node.childNodes)

        for i in all_mask_node_indexes:
            if not i == mask_node_index:
                modify_fill_recursively(layer_node.childNodes[i])


class ImgOccNoteGeneratorProgressive(ImgOccNoteGenerator):
    def __init__(self, path, ed, kbd, svg):
        ImgOccNoteGenerator.__init__(self, path, ed, kbd, svg)

    def _create_mask_at_layernode(self, mask_node_index, all_mask_node_indexes, layer_node):
        showWarning("Not yet implemented")
        #todo: do this (when needed)


class ImgOccNoteGeneratorSingle(ImgOccNoteGenerator):
    def __init__(self, path, ed, kbd, svg):
        ImgOccNoteGenerator.__init__(self, path, ed, kbd, svg)

    def _generate_mask_svgs(self):
        return [self.masks_svg]