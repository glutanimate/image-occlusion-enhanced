# -*- coding: utf-8 -*-

# Image Occlusion Enhanced Add-on for Anki
#
# Copyright (C) 2016-2020  Aristotelis P. <https://glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Makes older IO notes editable.
"""

import logging

from anki.hooks import addHook
from aqt.utils import tooltip
from .lang import _

from xml.dom import minidom

from .config import *
from .dialogs import ioAskUser
from .utils import img_element_to_path, path_to_img_element


class ImgOccNoteConverter(object):
    def __init__(self, browser):
        self.browser = browser
        self.occl_id_last = None
        self._media_path = mw.col.media.dir()
        loadConfig(self)

    def convertNotes(self, nids):
        """Main note conversion method"""
        nids_by_nr = {}
        skipped = 0
        (io_nids, filtered) = self.filterSelected(nids)
        for nid in io_nids:
            note = mw.col.getNote(nid)
            (uniq_id, note_nr) = self.getDataFromNamingScheme(note)
            if uniq_id == False:
                logging.debug("Skipping note that couldn't be parsed: %s", nid)
                skipped += 1
                continue
            occl_tp = self.getOcclTypeAndNodes(note)
            occl_id = uniq_id + "-" + occl_tp
            if occl_id == self.occl_id_last:
                logging.debug("Skipping note that we've just converted: %s", nid)
                continue
            self.occl_id_last = occl_id
            for nid in self.findByNoteId(uniq_id):
                note = mw.col.getNote(nid)
                (uniq_id, note_nr) = self.getDataFromNamingScheme(note)
                if uniq_id == False:
                    logging.debug("Skipping note that couldn't be parsed: %s", nid)
                    skipped += 1
                    continue
                nids_by_nr[int(note_nr)] = nid
            self.idAndCorrelateNotes(nids_by_nr, occl_id)
        converted = len(io_nids)
        tooltip(
            _(
                "<b>{number_notes_updated}</b> note(s) updated,"
                " <b>{number_notes_skipped}</b> skipped"
            ).format(
                number_notes_updated=converted - skipped,
                number_notes_skipped=filtered + skipped,
            )
        )

    def filterSelected(self, nids):
        """Filters out notes with the wrong note type and those that are
        valid already"""
        io_nids = []
        filtered = 0
        for nid in nids:
            note = mw.col.getNote(nid)
            if note.model() != self.model:
                logging.debug("Skipping note with wrong note type: %s", nid)
                filtered += 1
                continue
            elif note[self.ioflds["id"]]:
                logging.debug("Skipping IO note that is already editable: %s", nid)
                filtered += 1
                continue
            elif not note[self.ioflds["om"]]:
                logging.debug("Skipping IO note without original SVG mask: %s", nid)
                filtered += 1
                continue
            logging.debug("Found IO note in need of update: %s", nid)
            io_nids.append(nid)
        return (io_nids, filtered)

    def findByNoteId(self, note_id):
        """Search collection for notes with given ID in their omask paths"""
        # need to use omask path because Note ID field is not yet set
        query = '"%s:*%s*"' % (self.ioflds["om"], note_id)
        logging.debug("query: %s", query)
        res = mw.col.findNotes(query)
        return res

    def getDataFromNamingScheme(self, note):
        """Get unique ID and note nr from qmask path"""
        qmask = note[self.ioflds["qm"]]
        path = img_element_to_path(qmask, True)
        if not path:
            return (False, None)
        grps = path.split("_")
        try:
            if len(grps) == 2:
                logging.debug("Extracting data using IO 2.0 naming scheme")
                uniq_id = grps[0]
                note_nr = path.split(" ")[1].split(".")[0]
            else:
                logging.debug("Extracting data using IO Enhanced naming scheme")
                grps = path.split("-")
                uniq_id = grps[0]
                note_nr = int(grps[2]) - 1
            return (uniq_id, note_nr)
        except IndexError:
            return (False, None)

    def idAndCorrelateNotes(self, nids_by_nr, occl_id):
        """Update Note ID fields and omasks of all occlusion session siblings"""
        logging.debug("occl_id %s", occl_id)
        logging.debug("nids_by_nr %s", nids_by_nr)
        logging.debug("mnode_idxs %s", self.mnode_idxs)

        for nr in sorted(nids_by_nr.keys()):
            try:
                midx = self.mnode_idxs[nr]
            except IndexError:
                continue
            nid = nids_by_nr[nr]
            note = mw.col.getNote(nid)
            new_mnode_id = occl_id + "-" + str(nr + 1)
            self.mnode.childNodes[midx].setAttribute("id", new_mnode_id)
            note[self.ioflds["id"]] = new_mnode_id
            note.flush()
            logging.debug("Adding ID for note nr %s", nr)
            logging.debug("midx %s", midx)
            logging.debug("nid %s", nid)
            logging.debug("note %s", note)
            logging.debug("new_mnode_id %s", new_mnode_id)

        new_svg = self.svg_node.toxml()
        omask_path = self._saveMask(new_svg, occl_id, "O")
        logging.debug("omask_path %s", omask_path)

        for nid in list(nids_by_nr.values()):
            note = mw.col.getNote(nid)
            note[self.ioflds["om"]] = path_to_img_element(omask_path)
            note.addTag(".io-converted")
            note.flush()
            logging.debug("Setting om and tag for nid %s", nid)

    def getOcclTypeAndNodes(self, note):
        """Determine oclusion type and svg mask nodes"""
        nr_of_masks = {}
        mnode_idxs = {}
        svg_mlayer = {}
        for i in ["qm", "om"]:  # om second, so that end vars are correct
            svg_file = img_element_to_path(note[self.ioflds[i]], True)
            svg_node = self.readSvg(svg_file)
            svg_mlayer = self.layerNodesFrom(svg_node)[-1]  # topmost layer
            mnode_idxs = self.getMaskNodes(svg_mlayer)
            nr_of_masks[i] = len(mnode_idxs)
        # decide on occl_tp based on nr of mask nodes in omask vs qmask
        if nr_of_masks["om"] != nr_of_masks["qm"]:
            occl_tp = "oa"
        else:
            occl_tp = "ao"
        self.svg_node = svg_node
        self.mnode = svg_mlayer
        self.mnode_idxs = mnode_idxs
        return occl_tp

    def readSvg(self, svg_file):
        """Read and fix malformatted IO 2.0 SVGs"""
        svg_doc = minidom.parse(svg_file)
        # ugly workaround for wrong namespace in older IO notes:
        svg_string = svg_doc.toxml().replace("ns0:", "").replace(":ns0", "")
        svg_string = str(svg_string)
        svg_doc = minidom.parseString(svg_string.encode("utf-8"))
        svg_node = svg_doc.documentElement
        return svg_node

    def getMaskNodes(self, mlayer):
        """Find mask nodes in masks layer"""
        mnode_indexes = []
        for i, node in enumerate(mlayer.childNodes):
            if (node.nodeType == node.ELEMENT_NODE) and (node.nodeName != "title"):
                mnode_indexes.append(i)
        return mnode_indexes

    def layerNodesFrom(self, svg_node):
        """Get layer nodes (topmost group nodes below the SVG node)"""
        assert svg_node.nodeType == svg_node.ELEMENT_NODE
        assert svg_node.nodeName == "svg"
        layer_nodes = [
            node for node in svg_node.childNodes if node.nodeType == node.ELEMENT_NODE
        ]
        assert len(layer_nodes) >= 1
        # last, i.e. top-most element, needs to be a layer:
        assert layer_nodes[-1].nodeName == "g"
        return layer_nodes

    def _saveMask(self, mask, note_id, mtype):
        """Write mask to file in media collection"""
        logging.debug(
            _("!saving %(node_id)s, %(mtype)s"), {"node_id": node_id, "mtype": mtype}
        )
        mask_filename = "%s-%s.svg" % (note_id, mtype)
        mask_path = os.path.join(self._media_path, mask_filename)
        mask_data = mask.encode("utf8")

        with open(mask_path, "wb") as f:
            f.write(mask_data)

        return mask_filename


def onIoConvert(self):
    """Launch initial dialog, set up checkpoint, invoke converter"""
    mw = self.mw
    selected = self.selectedNotes()
    if not selected:
        tooltip(_("No cards selected."), period=2000)
        return
    ret = ioAskUser(
        "question_nconvert",
        title=_("Please confirm action"),
        parent=self,
        defaultno=True,
    )
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


# Set up menus and hooks


def setupMenu(self):
    menu = self.form.menuEdit
    menu.addSeparator()
    a = menu.addAction(_("Convert to Editable IO &Enhanced Notes"))
    a.triggered.connect(lambda _, b=self: onIoConvert(b))


try:
    from aqt.gui_hooks import browser_menus_did_init

    browser_menus_did_init.append(setupMenu)
except (ImportError, ModuleNotFoundError):
    addHook("browser.setupMenus", setupMenu)
