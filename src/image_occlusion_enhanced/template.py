# -*- coding: utf-8 -*-
####################################################
##                                                ##
##           Image Occlusion Enhanced             ##
##                                                ##
##      Copyright (c) Glutanimate 2016-2017       ##
##       (https://github.com/Glutanimate)         ##
##                                                ##
##         Based on Image Occlusion 2.0           ##
##         Copyright (c) 2012-2015 tmbb           ##
##           (https://github.com/tmbb)            ##
##                                                ##
####################################################

"""
Handles the IO note type and card template
"""

from .config import *

# DEFAULT CARD TEMPLATES

iocard_front = """\
{{#%(src_img)s}}
<div id="io-header">{{%(header)s}}</div>
<div id="io-wrapper">
  <div id="io-overlay">{{%(que)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>
<div id="io-footer">{{%(footer)s}}</div>

<script>
// Prevent original image from loading before mask
aFade = 50, qFade = 0;
var mask = document.querySelector('#io-overlay>img');
function loaded() {
    var original = document.querySelector('#io-original');
    original.style.visibility = "visible";
}
if (mask === null || mask.complete) {
    loaded();
} else {
    mask.addEventListener('load', loaded);
}
</script>
{{/%(src_img)s}}
""" % \
    {'que': IO_FLDS['qm'],
     'ans': IO_FLDS['am'],
     'svg': IO_FLDS['om'],
     'src_img': IO_FLDS['im'],
     'header': IO_FLDS['hd'],
     'footer': IO_FLDS['ft'],
     'remarks': IO_FLDS['rk'],
     'sources': IO_FLDS['sc'],
     'extraone': IO_FLDS['e1'],
     'extratwo': IO_FLDS['e2']}

iocard_back = """\
{{#%(src_img)s}}
<div id="io-header">{{%(header)s}}</div>
<div id="io-wrapper">
  <div id="io-overlay">{{%(ans)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>
{{#%(footer)s}}<div id="io-footer">{{%(footer)s}}</div>{{/%(footer)s}}
<button id="io-revl-btn" onclick="toggle();">Toggle Masks</button>
<div id="io-extra-wrapper">
  <div id="io-extra">
    {{#%(remarks)s}}
      <div class="io-extra-entry">
        <div class="io-field-descr">%(remarks)s</div>{{%(remarks)s}}
      </div>
    {{/%(remarks)s}}
    {{#%(sources)s}}
      <div class="io-extra-entry">
        <div class="io-field-descr">%(sources)s</div>{{%(sources)s}}
      </div>
    {{/%(sources)s}}
    {{#%(extraone)s}}
      <div class="io-extra-entry">
        <div class="io-field-descr">%(extraone)s</div>{{%(extraone)s}}
      </div>
    {{/%(extraone)s}}
    {{#%(extratwo)s}}
      <div class="io-extra-entry">
        <div class="io-field-descr">%(extratwo)s</div>{{%(extratwo)s}}
      </div>
    {{/%(extratwo)s}}
  </div>
</div>

<script>
// Toggle answer mask on clicking the image
var toggle = function() {
  var amask = document.getElementById('io-overlay');
  if (amask.style.display === 'block' || amask.style.display === '')
    amask.style.display = 'none';
  else
    amask.style.display = 'block'
}

// Prevent original image from loading before mask
aFade = 50, qFade = 0;
var mask = document.querySelector('#io-overlay>img');
function loaded() {
    var original = document.querySelector('#io-original');
    original.style.visibility = "visible";
}
if (mask === null || mask.complete) {
    loaded();
} else {
    mask.addEventListener('load', loaded);
}
</script>
{{/%(src_img)s}}
""" % \
    {'que': IO_FLDS['qm'],
     'ans': IO_FLDS['am'],
     'svg': IO_FLDS['om'],
     'src_img': IO_FLDS['im'],
     'header': IO_FLDS['hd'],
     'footer': IO_FLDS['ft'],
     'remarks': IO_FLDS['rk'],
     'sources': IO_FLDS['sc'],
     'extraone': IO_FLDS['e1'],
     'extratwo': IO_FLDS['e2']}

iocard_css = """\
/* GENERAL CARD STYLE */
.card {
  font-family: "Helvetica LT Std", Helvetica, Arial, Sans;
  font-size: 150%;
  text-align: center;
  color: black;
  background-color: white;
}

/* OCCLUSION CSS START - don't edit this */
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
  z-index:2;
  visibility: hidden;
}

#io-wrapper {
  position:relative;
  width: 100%;
}
/* OCCLUSION CSS END */

/* OTHER STYLES */
#io-header{
  font-size: 1.1em;
  margin-bottom: 0.2em;
}

#io-footer{
  max-width: 80%;
  margin-left: auto;
  margin-right: auto;
  margin-top: 0.8em;
  font-style: italic;
}

#io-extra-wrapper{
  /* the wrapper is needed to center the
  left-aligned blocks below it */
  width: 80%;
  margin-left: auto;
  margin-right: auto;
  margin-top: 0.5em;
}

#io-extra{
  text-align:center;
  display: inline-block;
}

.io-extra-entry{
  margin-top: 0.8em;
  font-size: 0.9em;
  text-align:left;
}

.io-field-descr{
  margin-bottom: 0.2em;
  font-weight: bold;
  font-size: 1em;
}

#io-revl-btn {
  font-size: 0.5em;
}

/* ADJUSTMENTS FOR MOBILE DEVICES */

.mobile .card, .mobile #content {
  font-size: 120%;
  margin: 0;
}

.mobile #io-extra-wrapper {
  width: 95%;
}

.mobile #io-revl-btn {
  font-size: 0.8em;
}
"""

# INCREMENTAL UPDATES

html_overlay_onload = """\
<script>
// Prevent original image from loading before mask
aFade = 50, qFade = 0;
var mask = document.querySelector('#io-overlay>img');
function loaded() {
    var original = document.querySelector('#io-original');
    original.style.visibility = "visible";
}
if (mask.complete) {
    loaded();
} else {
    mask.addEventListener('load', loaded);
}
</script>\
"""

css_original_hide = """\
/* Anki 2.1 additions */
#io-original {
   visibility: hidden;
}\
"""

# List structure:
# (<version addition was introduced in>,
# (<qfmt_addition>, <afmt_addition>, <css_addition>))
# versions need to be ordered by semantic versioning
additions_by_version = [
    (
        1.30,
        (html_overlay_onload, html_overlay_onload, css_original_hide)
    ),
]


def add_io_model(col):
    models = col.models
    io_model = models.new(IO_MODEL_NAME)
    # Add fields:
    for i in IO_FLDS_IDS:
        fld = models.newField(IO_FLDS[i])
        if i == "note_id":
            fld['size'] = 0
        models.addField(io_model, fld)
    # Add template
    template = models.newTemplate(IO_CARD_NAME)
    template['qfmt'] = iocard_front
    template['afmt'] = iocard_back
    io_model['css'] = iocard_css
    io_model['sortf'] = 1  # set sortfield to header
    models.addTemplate(io_model, template)
    models.add(io_model)
    return io_model


def reset_template(col):
    print("Resetting IO Enhanced card template to defaults")
    io_model = col.models.byName(IO_MODEL_NAME)
    template = io_model['tmpls'][0]
    template['qfmt'] = iocard_front
    template['afmt'] = iocard_back
    io_model['css'] = iocard_css
    col.models.save()
    return io_model


def update_template(col, old_version):
    print("Updating IO Enhanced card template")

    additions = [[], [], []]

    for version, components in additions_by_version:
        if old_version >= version:
            continue
        for lst, addition in zip(additions, components):
            lst.append(addition)

    io_model = col.models.byName(IO_MODEL_NAME)

    if not io_model:
        return add_io_model(col)

    template = io_model['tmpls'][0]
    template['qfmt'] += "\n".join(additions[0])
    template['afmt'] += "\n".join(additions[1])
    io_model['css'] += "\n".join(additions[2])
    col.models.save()
    return io_model
