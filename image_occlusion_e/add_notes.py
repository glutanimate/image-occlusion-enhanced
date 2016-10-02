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
import hashlib
import time
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

IMAGE_QA_MODEL_NAME = "Image Q/A - 2.0 Enhanced"
QUESTION_FIELD_NAME = "Question"
ANSWER_FIELD_NAME = "Answer"
SVG_FIELD_NAME = "SVG"
ORIGINAL_IMAGE_FIELD_NAME = "Original Image"
HEADER_FIELD_NAME = "Header"
FOOTER_FIELD_NAME = "Footer"
REMARKS_FIELD_NAME = "Remarks"
SOURCES_FIELD_NAME = "Sources"
TEMPFIELD3_FIELD_NAME = "TempField3"
TEMPFIELD4_FIELD_NAME = "TempField4"
TEMPFIELD5_FIELD_NAME = "TempField5"

HEADER_FIELD_IDX = 4  # index starts at zero

ImageQA_qfmt = """\
{{#%(src_img)s}}
<div id="io-title">{{%(header)s}}</div>
<div id="io-wrapper">
  <div id="io-overlay">{{%(que)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>
<div id="io-footer">{{%(footer)s}}</div>
{{/%(src_img)s}}
""" % \
 {'que': QUESTION_FIELD_NAME,
  'svg': SVG_FIELD_NAME,
  'src_img': ORIGINAL_IMAGE_FIELD_NAME,
  'header': HEADER_FIELD_NAME,
  'footer': FOOTER_FIELD_NAME,
  'remarks': REMARKS_FIELD_NAME,
  'sources': SOURCES_FIELD_NAME,
  'tempfield3': TEMPFIELD3_FIELD_NAME,
  'tempfield4': TEMPFIELD4_FIELD_NAME,
  'tempfield5': TEMPFIELD5_FIELD_NAME}

ImageQA_afmt = """\
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
 {'ans': ANSWER_FIELD_NAME,
  'svg': SVG_FIELD_NAME,
  'src_img': ORIGINAL_IMAGE_FIELD_NAME,
  'header': HEADER_FIELD_NAME,
  'footer': FOOTER_FIELD_NAME,
  'remarks': REMARKS_FIELD_NAME,
  'sources': SOURCES_FIELD_NAME,
  'tempfield3': TEMPFIELD3_FIELD_NAME,
  'tempfield4': TEMPFIELD4_FIELD_NAME,
  'tempfield5': TEMPFIELD5_FIELD_NAME}

ImageQA_css = """\
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
    mm = col.models
    m = mm.new(IMAGE_QA_MODEL_NAME)
    # Add core fields:
    question_field = mm.newField(QUESTION_FIELD_NAME)
    answer_field = mm.newField(ANSWER_FIELD_NAME)
    svg_field = mm.newField(SVG_FIELD_NAME)
    original_image_field = mm.newField(ORIGINAL_IMAGE_FIELD_NAME)
    mm.addField(m, question_field)
    mm.addField(m, answer_field)
    mm.addField(m, svg_field)
    mm.addField(m, original_image_field)
    # Add other fields
    header_field = mm.newField(HEADER_FIELD_NAME)
    footer_field = mm.newField(FOOTER_FIELD_NAME)
    remarks_field = mm.newField(REMARKS_FIELD_NAME)
    sources_field = mm.newField(SOURCES_FIELD_NAME)
    tempfield3_field = mm.newField(TEMPFIELD3_FIELD_NAME)
    tempfield4_field = mm.newField(TEMPFIELD4_FIELD_NAME)
    tempfield5_field = mm.newField(TEMPFIELD5_FIELD_NAME)
    mm.addField(m, header_field)
    mm.addField(m, footer_field)
    mm.addField(m, remarks_field)
    mm.addField(m, sources_field)
    mm.addField(m, tempfield3_field)
    mm.addField(m, tempfield4_field)
    mm.addField(m, tempfield5_field)
    mm.setSortIdx(m, HEADER_FIELD_IDX)
    # Add template
    t = mm.newTemplate("Image Q/A")
    t['qfmt'] = ImageQA_qfmt
    t['afmt'] = ImageQA_afmt
    m['css'] = ImageQA_css
    # set sortfield to header
    m['sortf'] = 4
    mm.addTemplate(m, t)
    mm.add(m)
    return m


def update_qfmt_afmt(col):
    m = col.models.byName(IMAGE_QA_MODEL_NAME)
    # We are assuming that the template list contains only one element.
    # This will be true as long as no one has been trampling the model.
    t = m['tmpls'][0]
    t['qfmt'] = ImageQA_qfmt
    t['afmt'] = ImageQA_afmt
    t['css'] = ImageQA_css
    return m

###############################################################


def gen_uniq():
    uniq = hashlib.sha1(str(time.clock())).hexdigest()
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

    uniq_prefix = gen_uniq() + "_"

    bnames = os.listdir(media_dir)
    for bname in bnames:
        hash_bname = uniq_prefix + bname
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


def add_QA_note(col, fname_q, fname_a, tags, fname_svg,
                fname_original, header, footer, remarks, sources, 
                tempfield3, tempfield4, tempfield5, did):

    m = col.models.byName(IMAGE_QA_MODEL_NAME)
    m['did'] = did
    n = notes.Note(col, model=m)
    n.fields = [fname2img(fname_q),
                fname2img(fname_a),
                fname2img(fname_svg),
                fname2img(fname_original),
                header,
                footer,
                remarks,
                sources,
                tempfield3,
                tempfield4,
                tempfield5]

    for tag in tags:
        n.addTag(tag)

    col.addNote(n)

    return n


def add_QA_notes(col, fnames_q, fnames_a, tags, media_dir, svg_fname,
                 fname_original, header, footer, remarks, sources, 
                 tempfield3, tempfield4, tempfield5, did):
    d = new_bnames(col, media_dir, fname_original)
    nrOfNotes = 0
    for (q, a) in zip(fnames_q, fnames_a):
        add_QA_note(col,
                    d[os.path.basename(q)],
                    d[os.path.basename(a)],
                    tags,
                    d[os.path.basename(svg_fname)],
                    d[os.path.basename(fname_original)],
                    header,
                    footer,
                    remarks,
                    sources,
                    tempfield3,
                    tempfield4,
                    tempfield5,
                    did)
        nrOfNotes += 1
    return nrOfNotes


# Updates the GUI and shows a tooltip
def gui_add_QA_notes(fnames_q, fnames_a, media_dir, tags, svg_fname,
                     fname_original, header, footer, remarks, sources, 
                     tempfield3, tempfield4, tempfield5, did):
    col = mw.col
    mm = col.models
    if not mm.byName(IMAGE_QA_MODEL_NAME):  # first time addon is run
        add_image_QA_model(col)
    m = mm.byName(IMAGE_QA_MODEL_NAME)

    nrOfNotes = add_QA_notes(col, fnames_q, fnames_a,
                             tags, media_dir, svg_fname,
                             fname_original, header, footer, remarks, sources, 
                             tempfield3, tempfield4, tempfield5, did)
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
