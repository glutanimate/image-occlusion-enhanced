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

from anki import notes
from aqt import mw, utils

import os
import sys
import uuid

import shutil


def notes_added_message(nrOfNotes):
    if nrOfNotes == 1:
        msg = "<b>1 note</b> was added to your collection"
    else:
        msg = "<b>{0} notes</b> were added to your collection".format(nrOfNotes)
    return msg


def rm_media_dir(media_dir):
    for f in os.listdir(media_dir):
        try:
            os.remove(os.path.join(media_dir, f))
        except:
            pass
    try:
        os.rmdir(media_dir)
    except:
        pass


IO_FLDS = {
    'uuid': "UUID (DO NOT EDIT)",
    'header': "Header",
    'image': "Image",
    'footer': "Footer",
    'remarks': "Anmerkungen",
    'sources': "Quellen",
    'extra1': "Extra 1",
    'extra2': "Extra 2",
    'qmask': "Question Mask",
    'amask': "Answer Mask",
    'fmask': "Full Mask"
}

IO_FLDORDER = ["uuid", "header", "image", "footer", "remarks", "sources",
                "extra1", "extra2", "qmask", "amask", "fmask"]

IO_MODEL_NAME = "Image Occlusion Enhanced"
IO_CARD_NAME = "IO Card"

iocard_front = """\
{{#%(src_img)s}}
<div id="io-title">{{%(header)s}}</div>
<div id="io-wrapper">
  <div id="io-overlay">{{%(que)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>
<div id="io-footer">{{%(footer)s}}</div>
{{/%(src_img)s}}
""" % \
 {'que': IO_FLDS['qmask'],
  'ans': IO_FLDS['amask'],
  'svg': IO_FLDS['fmask'],
  'src_img': IO_FLDS['image'],
  'header': IO_FLDS['header'],
  'footer': IO_FLDS['footer'],
  'remarks': IO_FLDS['remarks'],
  'sources': IO_FLDS['sources'],
  'extra1': IO_FLDS['extra1'],
  'extra2': IO_FLDS['extra2']}

iocard_back = """\
{{#%(src_img)s}}
<div id="io-title">{{%(header)s}}</div>
<div id="io-wrapper">
  <div id="io-overlay">{{%(ans)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>
<div id="io-footer">
  {{#%(footer)s}}
    <div>{{%(footer)s}}</div>
    <hr>
  {{/%(footer)s}}
  {{#%(remarks)s}}
    <div>
      <span class="io-field-descr">Remarks: </span>{{%(remarks)s}}
    </div>
  {{/%(remarks)s}}
    </br>
  {{#%(sources)s}}
    <div>
      <span class="io-field-descr">Sources: </span>{{%(sources)s}}
    </div>
  {{/%(sources)s}}
</div>
{{/%(src_img)s}}
""" % \
 {'que': IO_FLDS['qmask'],
  'ans': IO_FLDS['amask'],
  'svg': IO_FLDS['fmask'],
  'src_img': IO_FLDS['image'],
  'header': IO_FLDS['header'],
  'footer': IO_FLDS['footer'],
  'remarks': IO_FLDS['remarks'],
  'sources': IO_FLDS['sources'],
  'extra1': IO_FLDS['extra1'],
  'extra2': IO_FLDS['extra2']}

iocard_css = """\
.card {
  font-family: "Helvetica LT Std", Helvetica, Arial, Sans;
  font-size: 150%;
  text-align: center;
  color: black;
  background-color: white;
}

.io-field-descr{
  font-weight: bold;
}

#io-title{
  font-size: 1.1em;
}

#io-wrapper {
  position:relative;
  width: 100%;
}

#io-overlay {
  position:absolute;
  top:0;
  width:100%;
  z-index:3
}

#io-original {
  position:relative;
  top:0;
  width:100%;
  z-index:2
}

#io-question{
  margin-top: 0.8em;
}

#io-footer{
  margin-top: 0.8em;
  max-width: 80%;
  margin-left: auto;
  margin-right: auto;
}
"""

def add_image_QA_model(col):
    models = col.models
    iomodel = models.new(IO_MODEL_NAME)
    # Add fields:
    for i in IO_FLDORDER:
      fld = models.newField(IO_FLDS[i])
      if i == "uuid":
        fld['size'] = 0
      models.addField(iomodel, fld)
    # Add template
    template = models.newTemplate(IO_CARD_NAME)
    template['qfmt'] = iocard_front
    template['afmt'] = iocard_back
    iomodel['css'] = iocard_css
    iomodel['sortf'] = 1 # set sortfield to header
    models.addTemplate(iomodel, template)
    models.add(iomodel)
    return iomodel


def update_qfmt_afmt(col):
    iomodel = col.models.byName(IO_MODEL_NAME)
    # We are assuming that the template list contains only one element.
    # This will be true as long as no one has been trampling the model.
    template = iomodel['tmpls'][0]
    template['qfmt'] = iocard_front
    template['afmt'] = iocard_back
    template['css'] = iocard_css
    return iomodel

###############################################################


def gen_uniq():
    uniq = str(uuid.uuid4()).replace("-","")
    return uniq

def new_bnames(col, media_dir, original_fname):

    d = {}
    # if the original image is located under the anki collection.media folder
    # there is no nead to copy it again
    original_file_base_name = os.path.basename(original_fname)    
    orig_file_path = os.path.dirname(original_fname)
    if not orig_file_path == col.media.dir():       
        shutil.copy(original_fname,
                    os.path.join(media_dir, original_file_base_name))
    else:
        d[original_file_base_name]=original_file_base_name

    iouuid = gen_uniq()
    d['uuid'] = iouuid

    bnames = os.listdir(media_dir)
    for bname in bnames:
        hash_bname = iouuid + '_' + bname
        os.rename(os.path.join(media_dir, bname),
                  os.path.join(media_dir, hash_bname))

        path = os.path.join(media_dir, hash_bname)

        # The KEY to the dictionary must be in the default file system
        # encoding, because we will write d[filename], where filename
        # is encoded in the same encoding.
        encoding = sys.getfilesystemencoding()
        d[bname.decode(encoding)] = col.media.addFile(path.decode(encoding))

    return d


def fname2img(fname):
    return '<img src="' + fname + '" />'


def add_QA_note(col, uuid, fname_q, fname_a, tags, fname_svg,
                fname_original, header, footer, remarks, sources, 
                extra1, extra2, did):

    model = col.models.byName(IO_MODEL_NAME)
    model['did'] = did
    nnote = notes.Note(col, model=model)



    # for i in IO_FLDS.keys():
    #     fld = IO_FLDS[i]
    #     nnote[fld] = 

    # IO_FLDORDER = ["uuid", "header", "image", "footer", "remarks", "sources",
    #                 "extra1", "extra2", "qmask", "amask", "fmask"]


    # static order, this is temporary
    nnote.fields = [
                uuid,
                header,
                fname2img(fname_original),
                footer,
                remarks,
                sources,
                extra1,
                extra2,
                fname2img(fname_q),
                fname2img(fname_a),
                fname2img(fname_svg)
                ]

    for tag in tags:
        nnote.addTag(tag)

    col.addNote(nnote)

    return nnote


def add_QA_notes(col, fnames_q, fnames_a, tags, media_dir, svg_fname,
                 fname_original, header, footer, remarks, sources, 
                 extra1, extra2, did):
    d = new_bnames(col, media_dir, fname_original)
    nrOfNotes = 0
    for (q, a) in zip(fnames_q, fnames_a):
        uuid = d['uuid'] + '-' + str(nrOfNotes+1)
        add_QA_note(col,
                    uuid,
                    d[os.path.basename(q)],
                    d[os.path.basename(a)],
                    tags,
                    d[os.path.basename(svg_fname)],
                    d[os.path.basename(fname_original)],
                    header,
                    footer,
                    remarks,
                    sources,
                    extra1,
                    extra2,
                    did)
        nrOfNotes += 1
    return nrOfNotes


# Updates the GUI and shows a tooltip
def gui_add_QA_notes(fnames_q, fnames_a, media_dir, tags, svg_fname,
                     fname_original, header, footer, remarks, sources, 
                     extra1, extra2, did):
    col = mw.col
    mm = col.models
    if not mm.byName(IO_MODEL_NAME):  # first time addon is run
        add_image_QA_model(col)
    m = mm.byName(IO_MODEL_NAME)

    nrOfNotes = add_QA_notes(col, fnames_q, fnames_a,
                             tags, media_dir, svg_fname,
                             fname_original, header, footer, remarks, sources, 
                             extra1, extra2, did)
    rm_media_dir(media_dir)  # removes the media and the directory

    #  We must update the GUI so that the user knows that cards have
    # been added.  When the GUI is updated, the number of new cards
    # changes, and it provides the feedback we want.
    # If we want more feedback, we can add a tooltip that tells the
    # user how many cards have been added.
    # The way to update the GUI will depend on the state
    # of the main window. There are four states (from what I understand):
    #  - "review"
    #  - "overview"
    #  - "deckBrowser"
    #  - "resetRequired" (we will treat this one like "deckBrowser)
    if mw.state == "review":
        mw.reviewer.show()
    elif mw.state == "overview":
        mw.overview.refresh()
    else:
        mw.deckBrowser.refresh()  # this shows the browser even if the
          # main window is in state "resetRequired", which in my
          # opinion is a good thing
    utils.tooltip(notes_added_message(nrOfNotes))
