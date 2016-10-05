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


# Default card template

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
  'svg': IO_FLDS['omask'],
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
  'svg': IO_FLDS['omask'],
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

def add_io_model(col):
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


def update_template(col):
    iomodel = col.models.byName(IO_MODEL_NAME)
    # We are assuming that the template list contains only one element.
    # This will be true as long as no one has been trampling the model.
    template = iomodel['tmpls'][0]
    template['qfmt'] = iocard_front
    template['afmt'] = iocard_back
    template['css'] = iocard_css
    return iomodel
    