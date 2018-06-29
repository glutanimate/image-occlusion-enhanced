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
Handles all minor utility dialogs
"""

from aqt.qt import *
from aqt import mw

from anki.hooks import addHook, remHook

from .config import *

# Help and support resource links

io_link_wiki = "https://github.com/glutanimate/image-occlusion-enhanced/wiki"
io_link_tut = "https://www.youtube.com/playlist?list=PL3MozITKTz5YFHDGB19ypxcYfJ1ITk_6o"
io_link_thread = ("https://anki.tenderapp.com/discussions/add-ons/"
                  "8295-image-occlusion-enhanced-official-thread")
io_link_obsolete_aa = "https://github.com/glutanimate/image-occlusion-enhanced/wiki/ADD_LINK_HERE"

# Predefiend dialog messages

dialog_msg = {}

dialog_msg["add"] = """
<p><strong>Basic Instructions</strong></p>
<ol>
<li>With the rectangle tool or any other shape tool selected, cover the areas of the image you want to be tested on</li>
<li>(Optional): Fill out additional information about your cards by switching to the <em>Fields</em> tab</li>
<li>Click on one of the <em>Add Cards</em> buttons at the bottom of the window to add the cards to your collection</li>
</ol>
<p><strong>Drawing Custom Labels</strong></p>
<ol>
<li>Draw up the layers sidepanel by clicking on the <em>Layers</em> button at the right edge of the editor</li>
<li>Switch to the <em>Labels</em> layer by left-clicking on it. You can also switch to the labels layer directly by using <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>L</kbd>.</li>
<li>Anything you draw in this layer – be it text, lines, or shapes – will appear above the image, but still below your masks. All of the painting tools in the left sidebar are at your disposal.</li>
<li>Switch back to the masks layer, either via the <em>Layers</em> sidepanel, or by using the <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>M</kbd> hotkey.</li>
</ol>
<p><strong>Grouping Shapes</strong></p>
<ol>
<li>Select multiple shapes, either by drawing a selection rectangle with the selection tool active (<kbd>S</kbd>), or by shift-clicking on multiple shapes</li>
<li>Either use the <kbd>G</kbd> hotkey or the <em>Group Elements</em> tool in the top-bar to group your items</li>
</ol>
<p>Grouped shapes will form a single card.</p>
<p><strong>More Information</strong></p>
<p>For more information please refer to the following resources:</p>
<ul>
<li><a href="{}">Image Occlusion Enhanced Wiki</a></li>
<li><a href="{}">YouTube Tutorials</a></li>
<li><a href="{}">Official support thread</a></li>
</ul>
""".format(io_link_wiki, io_link_tut, io_link_thread)

dialog_msg["edit"] = """
<b>Instructions for editing</b>:
<br><br> Each mask shape represents a card.
Removing any of the existing shapes will remove the corresponding card.
New shapes will generate new cards. You can change the occlusion type
by using the dropdown box on the left.<br><br>If you click on the
<i>Add new cards</i> button a completely new batch of cards will be
generated, leaving your originals untouched.<br><br>
<b>Actions performed in Image Occlusion's <i>Editing Mode</i> cannot be
easily undone, so please make sure to check your changes twice before
applying them.</b><br><br>The only exception to this are purely textual
changes to fields like the header or footer of your notes. These can
be fully reverted by using Ctrl+Z in the Browser or Reviewer view.<br><br>
More information: <a href="{}">Wiki: Editing Notes</a>.
""".format(io_link_wiki + "/Basic-Use#editing-cards")

dialog_msg["notetype"] = """
<b>Fixing a broken note type:</b
<br><br> The Image Occlusion Enhanced note type can't be edited
arbitrarily. If you delete a field that's required by the add-on
or rename it outside of the IO Options dialog you will be presented
with an error message. <br><br>
To fix this issue please follow the instructions in <a href="{}">the
wiki</a>.""".format(io_link_wiki + "/Troubleshooting#note-type")

dialog_msg["main"] = """
<h2>Help and Support</h2>
<p><a href="{}">Image Occlusion Enhanced Wiki</a></p>
<p><a href="{}">Official Video Tutorial Series</a></p>
<p><a href="{}">Support Thread</a></p>
<h2>Credits and License</h2>
<p style="font-size:12pt;"><em>Copyright © 2012-2015
<a href="https://github.com/tmbb">Tiago Barroso</a></em></p>
<p style="font-size:12pt;"><em>Copyright © 2013
<a href="https://github.com/steveaw">Steve AW</a></em></p>
<p style="font-size:12pt;"><em>Copyright © 2016-2017
<a href="https://github.com/Glutanimate">Aristotelis P.</a></em></p>
<p><em>Image Occlusion Enhanced</em> is licensed under the GNU AGPLv3.</p>
<p>Third-party open-source software shipped with <em>Image Occlusion Enhanced</em>:</p>
<ul><li><p><a href="https://github.com/SVG-Edit/svgedit">SVG Edit</a> 2.6.
Copyright (c) 2009-2012 SVG-edit authors. Licensed under the MIT license</a></p></li>
<li><p><a href="http://www.pythonware.com/products/pil/">Python Imaging Library</a>
(PIL) 1.1.7. Copyright (c) 1997-2011 by Secret Labs AB, Copyright (c) 1995-2011 by Fredrik
Lundh. Licensed under the <a href="http://www.pythonware.com/products/pil/license.htm"
PIL license</a></p></li>
<li><p><a href="https://github.com/shibukawa/imagesize_py">imagesize.py</a> v0.7.1.
Copyright (c) 2016 Yoshiki Shibukawa. Licensed under the MIT license.</p></li>
</ul>
""".format(io_link_wiki, io_link_tut, io_link_thread)

dialog_msg["obsolete_aa"] = """
<b>Important</b><br><br>
The "Hide All, Reveal All" image occlusion mode used by this card
is no longer supported by the add-on. You can still review it just like
you would with any other card, but if you proceed with editing the note,
it will automatically be converted to the "Hide All, Guess One" type.<br><br>
For more information on why this occlusion mode was removed and how to
replicate its functionality please see here:<br><br>
<a href="{}">Wiki: Hide All, Reveal All</a>
""".format(io_link_obsolete_aa)

dialog_msg["model_error"] = (
    "<b>Error</b>: Image Occlusion note type "
    "not configured properly. Please make sure you did not "
    "manually delete or rename any of the default fields."
)

dialog_msg["question_nconvert"] = """\
This is a purely <b>experimental</b> feature that is meant to update older
IO notes to be compatible with the new editing feature-set in IO Enhanced.
Clicking on 'Yes' below will prompt the add-on to go through all selected
notes and change their Note ID and mask files in a way that should make it
possible to edit them in the future.
<br><br>Please note that this will only work for notes
that have already been switched to the <i>Image Occlusion Enhanced</i> note type.
If you are coming from IO 2.0 or an older version of IO Enhanced you will
first have to switch the note type of your notes manually by going to <i>Edit →
Change Note Type.</i><br><br>
<b>WARNING</b>: There is no guarantee that this feature will actually succeed in
updating your notes properly. To convert legacy notes the add-on will have to
make a few assumptions which in some rare instances might turn out to be wrong
and lead to broken notes. Notes that can't be parsed for the information needed
to convert into an editable state (e.g. a valid "Original Mask" field) will usually
be skipped by the add-on, but there might be some corner cases where that won't work.
<br><br>A checkpoint will be set to revert to if needed,
but even with that safety measure in place you should still only use this
function if you know what you are doing.
<br><br><b>Continue anyway?</b><br><i>(Depending on the number of notes this might
take a while)</i>
"""

# Message dialog utility functions


def ioCritical(msgkey, title="Image Occlusion Enhanced Error", text="",
               parent=None, help=None):
    msgfunc = QMessageBox.critical
    if help:
        buttons = QMessageBox.Help | QMessageBox.Ok
    else:
        buttons = None
    while 1:
        r = ioInfo(msgkey, title=title, text=text,
                   parent=parent, buttons=buttons, msgfunc=msgfunc)
        if r == QMessageBox.Help:
            ioHelp(help, parent=parent)
            return False
        else:
            break
    return r


def ioAskUser(msgkey, title="Image Occlusion Enhanced", parent=None, text="",
              help="", defaultno=False, msgfunc=None):
    """Show a yes/no question. Return true if yes.
    based on askUser by Damien Elmes"""
    msgfunc = QMessageBox.question
    buttons = QMessageBox.Yes | QMessageBox.No
    if help:
        buttons |= QMessageBox.Help
    while 1:
        if defaultno:
            default = QMessageBox.No
        else:
            default = QMessageBox.Yes
        r = ioInfo(msgkey, title=title, text=text, parent=parent,
                   buttons=buttons, default=default, msgfunc=msgfunc)
        if r == QMessageBox.Help:
            ioHelp(help, parent=parent)
            return False
        else:
            break
    return r == QMessageBox.Yes


def ioInfo(msgkey, title="Image Occlusion Enhanced", text="", parent=None,
           buttons=None, default=None, msgfunc=None):
    if not parent:
        parent = mw.app.activeWindow()
    if not buttons:
        buttons = QMessageBox.Ok
    if not default:
        default = QMessageBox.Ok
    if not msgfunc:
        msgfunc = QMessageBox.information
    if msgkey != "custom":
        text = dialog_msg[msgkey]
    return msgfunc(parent, title, text, buttons, default)


def ioHelp(msgkey, title="Image Occlusion Enhanced Help",
           text="", parent=None):
    """Display an info message or a predefined help section"""
    if not parent:
        parent = mw.app.activeWindow()
    if msgkey != "custom":
        text = dialog_msg[msgkey]
    mbox = QMessageBox(parent)
    mbox.setAttribute(Qt.WA_DeleteOnClose)
    mbox.setStandardButtons(QMessageBox.Ok)
    mbox.setWindowTitle(title)
    mbox.setText(text)
    mbox.setWindowModality(Qt.NonModal)

    def onProfileUnload():
        if not sip.isdeleted(mbox):
            mbox.close()

    addHook("unloadProfile", onProfileUnload)
    mbox.finished.connect(lambda: remHook("unloadProfile", onProfileUnload))
    mbox.show()
