import etree.ElementTree as etree

from anki import notes, consts
from aqt import mw, utils

import os
import copy
import hashlib
import time
import shutil
import string

from PyQt4 import QtGui

def notes_added_message(nrOfNotes):
    if nrOfNotes == 1:
        msg = "<b>1 note</b> was added to your collection"
    else:
        msg = "<b>{0} notes</b> were added to your collection".format(nrOfNotes)
    return msg


def rm_media_dir(media_dir):
    for f in os.listdir(media_dir):
        try: os.remove(os.path.join(media_dir, f))
        except: pass
    try: os.rmdir(media_dir)
    except: pass

IMAGE_QA_MODEL_NAME = "Image Q/A - 2.0"
QUESTION_FIELD_NAME = "Question"
ANSWER_FIELD_NAME = "Answer"
SVG_FIELD_NAME = "SVG"
ORIGINAL_IMAGE_FIELD_NAME = "Original Image"
HEADER_FIELD_NAME = "Header"
FOOTER_FIELD_NAME = "Footer"

HEADER_FIELD_IDX = 4 # index starts at zero

ImageQA_qfmt = """
{{#%(src_img)s}}
{{%(header)s}}
<div style="position:relative; width:100%%">
  <div style="position:absolute; top:0; width:100%%">
    {{%(src_img)s}}
  </div>
  <div style="position:absolute; top:0; width:100%%">
    {{%(que)s}}<br/>
    {{%(footer)s}}
  </div>
</div>
{{%(footer)s}}
<span style="display:none">{{%(svg)s}}</span>
{{/%(src_img)s}}

{{^%(src_img)s}}
{{%(que)s}}
<span style="display:none">{{%(svg)s}}</span>
{{/%(src_img)s}}
""" % \
 {'que': QUESTION_FIELD_NAME,
  'svg': SVG_FIELD_NAME,
  'src_img': ORIGINAL_IMAGE_FIELD_NAME,
  'header': HEADER_FIELD_NAME,
  'footer': FOOTER_FIELD_NAME}

ImageQA_afmt = """
{{#%(src_img)s}}
{{%(header)s}}
<div style="position:relative; width:100%%">
  <div style="position:absolute; top:0; width:100%%">
    {{%(src_img)s}}
  </div>
  <div style="position:absolute; top:0; width:100%%">
    {{%(ans)s}}<br/>
    {{%(footer)s}}
  </div>
</div>
<span style="display:none">{{%(svg)s}}</span>
{{/%(src_img)s}}

{{^%(src_img)s}}
{{%(ans)s}}
<span style="display:none">{{%(svg)s}}</span>
{{/%(src_img)s}}
""" % \
 {'ans': ANSWER_FIELD_NAME,
  'svg': SVG_FIELD_NAME,
  'src_img': ORIGINAL_IMAGE_FIELD_NAME,
  'header': HEADER_FIELD_NAME,
  'footer': FOOTER_FIELD_NAME}

def add_image_QA_model(col):
    mm = col.models
    m = mm.new(IMAGE_QA_MODEL_NAME)
    # Add fields:
    question_field = mm.newField(QUESTION_FIELD_NAME)
    mm.addField(m, question_field)
    answer_field = mm.newField(ANSWER_FIELD_NAME)
    mm.addField(m, answer_field)
    svg_field = mm.newField(SVG_FIELD_NAME)
    mm.addField(m, svg_field)
    original_image_field = mm.newField(ORIGINAL_IMAGE_FIELD_NAME)
    mm.addField(m, original_image_field)
    # Add template   
    t = mm.newTemplate("Image Q/A")
    t['qfmt'] = ImageQA_qfmt
    t['afmt'] = ImageQA_afmt
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
    return m

def update_fields(col):
    mm = col.models
    m = mm.byName(IMAGE_QA_MODEL_NAME)
    # Define the new Fields
    header_field = mm.newField(HEADER_FIELD_NAME)
    footer_field = mm.newField(FOOTER_FIELD_NAME)
    # Add the new fields to the model
    mm.addField(m, header_field)
    mm.addField(m, footer_field)
    mm.setSortIdx(m, HEADER_FIELD_IDX)

###############################################################
def gen_uniq():
    uniq = hashlib.sha1(str(time.clock())).hexdigest()
    return uniq

def new_bnames(col, media_dir, original_fname):
    shutil.copy(original_fname,
                os.path.join(media_dir, os.path.basename(original_fname)))
    
    d = {}
    uniq_prefix = gen_uniq() + "_"
    
    bnames = os.listdir(media_dir)
    for bname in bnames:
        hash_bname = uniq_prefix + bname
        os.rename(os.path.join(media_dir, bname),
                  os.path.join(media_dir, hash_bname))
        
        path = os.path.join(media_dir, hash_bname)

        #  The KEY to the dictionary must be unicode, because we will
        # write d[filename], where filename is encoded in unicode. 
        d[unicode(bname, "UTF-8")] = col.media.addFile(unicode(path, "UTF-8"))

    return d

def fname2img(fname):
    return '<img src="' + fname + '" />'


def add_QA_note(col, fname_q, fname_a, tags, fname_svg,
                fname_original, header, footer, did):
                        
    m = col.models.byName(IMAGE_QA_MODEL_NAME)
    m['did'] = did
    n = notes.Note(col, model=m)
    n.fields = [fname2img(fname_q),
                fname2img(fname_a),
                fname2img(fname_svg),
                fname2img(fname_original),
                header,
                footer]
    
    for tag in tags:
        n.addTag(tag)

    col.addNote(n)
    
    return n



def add_QA_notes(col, fnames_q, fnames_a, tags, media_dir, svg_fname,
                 fname_original, header, footer, did):
    d = new_bnames(col, media_dir, fname_original)
    nrOfNotes = 0
    f = open("/home/tmbb/A.txt", 'w')
    f.write(str(d))
    f.close()
    for (q,a) in zip(fnames_q, fnames_a):
        add_QA_note(col,
                    d[os.path.basename(q)],
                    d[os.path.basename(a)],
                    tags,
                    d[os.path.basename(svg_fname)],
                    d[os.path.basename(fname_original)],
                    header,
                    footer,
                    did)
        nrOfNotes += 1
    return nrOfNotes

# Updates the GUI and shows a tooltip
def gui_add_QA_notes(fnames_q, fnames_a, media_dir, tags, svg_fname,
                     fname_original, header, footer, did):
    col = mw.col
    mm = col.models
    if not mm.byName(IMAGE_QA_MODEL_NAME): # first time addon is run
        add_image_QA_model(col)
    m = mm.byName(IMAGE_QA_MODEL_NAME)
    
    # Upgrading from previous versions:
    if m['tmpls'][0]['qfmt'] != ImageQA_qfmt: # still in version 2.0?
        update_qfmt_afmt(col)
    if len(m['flds']) == 4:
        update_fields(col)
        
    nrOfNotes = add_QA_notes(col, fnames_q, fnames_a,
                             tags, media_dir, svg_fname,
                             fname_original, header, footer, did)
    rm_media_dir(media_dir) # removes the media and the directory
    
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
        mw.deckBrowser.refresh() # this shows the browser even if the
          # main window is in state "resetRequired", which in my
          # opinion is a good thing
    utils.tooltip(notes_added_message(nrOfNotes))
