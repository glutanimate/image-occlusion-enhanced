# Image Occlusion 2.0 Enhanced

## Table of Contents

<!-- MarkdownTOC -->

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Changes compared to Image Occlusion 2.0](#changes-compared-to-image-occlusion-20)
    - [Enhancements to the user interface](#enhancements-to-the-user-interface)
    - [Enhancements to the core functionality of the add-on](#enhancements-to-the-core-functionality-of-the-add-on)
    - [Smaller tweaks and bug fixes](#smaller-tweaks-and-bug-fixes)
- [Installation](#installation)
- [Customization](#customization)
    - [DOs and DO NOTs](#dos-and-do-nots)
- [Tips](#tips)
    - [Making full use of SVG-Edit](#making-full-use-of-svg-edit)
    - [Using all available fields to their full extent](#using-all-available-fields-to-their-full-extent)
    - [Consistency across different note types](#consistency-across-different-note-types)
- [Development status](#development-status)
- [Credits](#credits)
- [License and Warranty](#license-and-warranty)

<!-- /MarkdownTOC -->


## Overview

This repository hosts a custom version of the [Image Occlusion 2.0](https://github.com/tmbb/image-occlusion-2) add-on for Anki with a number of improvements and additions.

Please note that this is a highly customized release and as such might contain modifications that are adapted to my note types and usage. The code in this repo is also much more experimental than my [other fork of image occlusion](https://github.com/Glutanimate/image-occlusion-2). You might want to check that one out instead if you're only looking for some smaller fixes and tweaks to I/O.

## Screenshots

![Screenshot of the Masks Editor](/screenshots/screenshot-io-editor-1.png?raw=true)

![Screenshot of the field entry tab](/screenshots/screenshot-io-editor-2.png?raw=true)

![Screenshot of the reviewer](/screenshots/screenshot-io-reviewer.png?raw=true)

## Changes compared to Image Occlusion 2.0

*Image Occlusion 2.0 Enhanced* comes with the following new features, some of which were already part of [my first fork](https://github.com/Glutanimate/image-occlusion-2):

### Enhancements to the user interface

- **Tabbed interface**
    - one tab for the Masks Editor, the other for the remaining fields. Gives you more room to work with larger images.
- **Multi-line entry fields**
    - entry fields now support multiple lines of plain text (no HTML preview)
- **New buttons for adding notes**
    - These replace the old controls which were placed inside the SVG-Edit element
* **Dynamic field labels**
    - Changes to field names now get propagated to the UI. If you rename the *Header* field, *Footer* field, etc. you will see the labels being updated.
- **Enhanced keyboard navigation**
    + Added/Modified hotkeys:
        * <kbd>Alt</kbd> + <kbd>O</kbd>: Add overlapping notes
        * <kbd>Alt</kbd> + <kbd>N</kbd>: Add non-overlapping notes
        * <kbd>Ctrl</kbd>+<kbd>F</kbd> (global) / <kbd>C</kbd> (when SVG-Edit is active): Fit image to canvas
        * <kbd>Alt</kbd> + <kbd>E</kbd>: Switch to Masks Editor tab
        * <kbd>Alt</kbd> + <kbd>F</kbd>: Switch to entry fields tab
        * <kbd>Ctrl</kbd> + <kbd>Tab</kbd>: Switch between tabs
        * <kbd>Ctrl</kbd> + <kbd>1-4</kbd>: switch focus to field 1-4 (including switching tabs if SVG-Editor is active)
        * <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>T</kbd>: Focus tags field
        * <kbd>Ctrl</kbd> + <kbd>SHIFT</kbd> + <kbd>R</kbd>: Reset all fields
        * <kbd>Ctrl</kbd> + <kbd>R</kbd>: Reset all fields aside from *Sources*, *Tags*, and *Deck*
        * <kbd>Alt</kbd> + <kbd>C</kbd>: Close window (replaces <kbd>Esc</kbd> which was too easy to hit by accident)
- **Improvements to the Masks Editor**
    + Images are now automatically fit to the canvas, making for a much better experience when working with larger images
    + Additionally, SVG-Edit is now resized automatically to fit the window size (thanks to @jameskraus)
    + You can now use <kbd>Ctrl</kbd> + <kbd>Mousewheel</kbd> to change the zoom on the canvas
- **Updated toolbar button**
    - the icon is now more in line with rest of the toolbar and comes with a tooltip

### Enhancements to the core functionality of the add-on

- **New image occlusion note type**
    + the new note type comes with 5 additional fields, 2 out of which can be updated via the image occlusion dialog.
        * the new fields are called `Remarks`, `Sources`, `TempField3-5`. 
        * only the first two can be updated via the image occlusion dialog. The remaining 3 are there as a reserve for possible changes in the future. I'd advise against using them as they won't work properly with some of the add-on's features (e.g. reusing field contents on existing I/O notes)
    + in order not to interfere with existing I/O notes the new note type is called `Image Q/A - 2.0 Enhanced`. You can transfer your old notes to this note type via the "Change note type" dialog in the Browser if you want.
    + the new note type also comes with a simpler card template
        * this new template uses CSS instead of inline styles for easier customization
        * the new *Remarks* and *Sources* fields are placed on the answer side
- **Ability to reuse existing image occlusion notes**
    + invoking image occlusion on an existing `Image Q/A - 2.0 Enhanced` note will now launch a new instance of I/O pre-loaded with all the data in your old note (excluding `TempField3-5`). You can use this feature to quickly create new I/O notes based on older ones
        + please note that there's still no way to update existing I/O notes. Finding a reasonable way to update the SVG masks and preserve scheduling information are things I still need to figure out
- **Synchronization between I/O Editor and Anki's editor window**
    + when creating a new I/O note, the add-on will now try to keep some fields synchronized with Anki's note editor. This makes it easier to alternate between I/O and other note types.
        * The following fields are currently synchronized: *Tags*, *Sources*
        * In practice this means that if your regular note type (e.g. basic) has a *Sources* field, then I/O will copy the value of that field over and copy it back when new I/O notes have been generated
- **Remember last used directory**
    + I/O will now try to set the file selection directory based on the last used directory

### Smaller tweaks and bug fixes

- drastically reduced add-on size by trimming down local version of PIL
- removed SVG-edit 2.7 from the repository
    + in my experience, SVG-Edit 2.7 was too slow and buggy to be used properly with I/O. I removed it to reduce development overhead and confusion. I might give more recent versions of SVG-Edit a try in the future, but for now 2.6 remains the most performant release for I/O.
- fixed a few issues with SVG-edit 2.6
    + fixed mousewheel zoom on the canvas
    + fixed a few confusing warnings and error messages that would appear in Anki's stdout
- use a proper SVG namespace, so that the resulting images can be read by any image viewer
- fix a bug that would create the wrong SVG masks when changing the z-index of added layers
    + this means that you can now create as many additional layers as you want and arrange them in whatever way you want
    + you could, for instance, create a new layer and use it to add new labels to an image. In order to occlude them you would then simply have to move the layer below the Shapes layer. The add-on will take care of using the right layer for the SVG masks automatically. See [Making full use of SVG-Edit](#making-full-use-of-svg-edit).
- removed duplicate SVG-Edit hotkeys (1, 2)
- assign `question-element` IDs to SVG question shapes
    + at some point in the future this might make it possible to target the question shapes via javascript or CSS
- added tooltips to most UI elements to make things easier for new users
- disabled a note type upgrade check that would revert any changes applied via the card template editor
    + any modifications to your I/O card templates will now be preserved across upgrades of the add-on
- changed sort field of I/O notes to the header. This makes it easier to identify specific notes in the card browser.
- changed default shape colour from white to dark-turquoise to make recognition of occlusions on white backgrounds easier
- remember size and position of editor window 

## Installation

It will probably be a while before I publish this add-on to AnkiWeb. There's still a lot of testing to be done; but if you want to help out or feel particularly adventurous you can install *Image Occlusion 2.0 Enhanced* by following these steps:

- Grab the latest release of the add-on from the [releases page](https://github.com/Glutanimate/image-occlusion-2-enhanced/releases)
- Extract the zip file
- Launch Anki and open the add-on directory by going to *Tools* → *Add-ons* → *Open add-on directory*
- If Image Occlusion 2.0 is installed you will have to remove it first by finding and deleting the `image_occlusion_2` folder and `Image Occlusion 2.py` file
- Having done that, proceed to copy `image_occlusion_2` and `Image Occlusion 2.py` from the extracted zip file into your add-on directory
- Restart Anki
- *Image Occlusion 2.0 Enhanced* should now be installed

## Customization

*Image Occlusion 2.0 Enhanced* can be customized, but only to a certain degree

### DOs and DO NOTs

**What you really should not do**:

- delete or rename the `Image Q/A - 2.0 Enhanced` note type
    + deleting the note type should restore it to default next time I/O is launched, but doing so will remove all notes associated with it
- re-order the fields of the note-type
- add new fields or remove existing ones
- rename the following fields: *Question*, *Answer*, *SVG*, *Original Image*

**What you can do**:

- rename the following fields: *Header*, *Footer*, *Remarks*, *Sources*, *TempField3*, *TempField4*, *TempField5*
- modify the card template and CSS
    + be careful, though: the right styling and layout is essential for layering the original image and SVG mask over each other

## Tips

Please check out tmbb's [comprehensive manual](http://tmbb.bitbucket.org/image-occlusion-2/) for a full tutorial on using image occlusion. Most of the instructions there still apply to this modified version of I/O.

What follows are a few additional tips to help you get the most out of *Image Occlusion 2.0 Enhanced*.

### Making full use of SVG-Edit

SVG-Edit ships with a lot of very useful **hotkeys**. Make sure to use them! E.g.:

- hold down <kbd>Shift</kbd> while clicking to select multiple shapes
- <kbd>G</kbd> to group items and mark them as one single mask
- <kbd>V</kbd> for the selection tool
- <kbd>R</kbd> for the rectangle tool
- <kbd>E</kbd> for the ellipse tool
- <kbd>T</kbd> for the text tool
- <kbd>C</kbd> to fit the image to the canvas

Use the **layers dialog** to add labels to your images before occluding them. Here's how:

- click on the right-sided labels side pane in SVG-Edit; a panel with all active layers will appear
- click on the 'new layer' button on the top-left; name the layer however you want (e.g. *Labels*)
- select the new layer by left-clicking on it in the labels list
- in order to occlude items on this new layer you will have to move it below the shapes layer first. To do so go back to the layers side panel, select your *Labels* layer, and use the down arrow button to to move it below the *Shapes* layer (but still above the *Picture* layer)
- any shapes or texts you now draw while the layer is active will be part of the background
- when you want to draw the occlusion masks again, simply re-select the *Shapes* layer

### Using all available fields to their full extent

This version of image occlusion comes with two new fields, *Remarks* and *Sources*. In total, you now have four different fields to choose from when adding additional information to your I/O notes (plus 3 more that are somewhat hidden, see above).

So what should you use these fields for? Well, you can customize and rename them however you please, but here are some suggestions:

- *Header* field: appears both on the front and back of your cards. I would use this for short titles that put your image in the right context. Notes in the browser can be sorted by this field, so make sure to choose a descriptive title.
- *Footer*: appears both on the front and back of your cards. You could use this for hints, mnemonics, recall prompts, etc.
- *Remarks* fields: Only appears on the back. Best suited for additional information, trivia, etc. Use this to nourish a big-picture understanding of the subject.
- *Sources*: Only appears on the back. Self-explanatory name. The best place to put references, links to your sources, lecturers etc. Very important if you ever want to go back and read up on the topic at hand.

### Consistency across different note types

Consider supplementing your other note types with a *Remarks* and a *Sources* field. Not only does it make for a more consistent experience, it also enables *Image Occlusion 2.0 Enhanced* to sync your sources between the I/O Editor and Anki's note editor. See [Enhancements to the core functionality of the add-on](#enhancements-to-the-core-functionality-of-the-add-on) for more information.

## Development status

This add-on is still very much in its early stages. It has not gone through the testing and cross-platform use that the original add-on has. So far it has only been tested on Linux. I have no clue if it will work properly on OS X, Windows, etc. In theory it should, but I/O has always suffered from issues on OS X.

If you use this add-on do not be surprised if you run into bugs, weird behaviour or other issues. You probably should not deploy this add-on in a production environment if you do not know what you're doing. I am not responsible for any data loss or problems with your note collection you might encounter.

With that said, I have been using this version of the add-on in my own studies for the past couple of months and it has not given me any kind of trouble. As always, your mileage might vary.

Bug reports and suggestions are always welcome, but it might take me a while to get to them. If you know how to code please feel free to improve this project, file pull requests, etc. The code could definitely benefit from some refactoring as I am not very adept in Python.

## Credits

- [tmbb](https://github.com/tmbb) for creating Image Occlusion
- [Abdolmadi Saravi, MD](https://bitbucket.org/amsaravi/) for patching Image Occlusion to reuse existing images in the media collection and on notes
- [Ank_U](https://bitbucket.org/Ank_U/) for patching Image Occlusion to support more fields

## License and Warranty

*Copyright © 2012-2015 tmbb*

*Copyright © 2016 Glutanimate*

*Image Occlusion 2.0 Enhanced* is licensed under the simplified BSD license.

Third-party open-source software shipped with *Image Occlusion 2.0 Enhanced*:

- [Python Imaging Library](http://www.pythonware.com/products/pil/) (PIL) 1.1.7. Copyright (c) 1997-2011 by Secret Labs AB, Copyright (c) 1995-2011 by Fredrik Lundh. Licensed under the [PIL license](http://www.pythonware.com/products/pil/license.htm)
 
- [SVG Edit](https://github.com/SVG-Edit/svgedit) 2.6. Copyright (c) 2009-2012 by SVG-edit authors. Licensed under the [MIT license](https://github.com/SVG-Edit/svgedit/blob/master/LICENSE)

- Python [ElementTree toolkit](http://effbot.org/zone/element-index.htm). Copyright (c) 1999-2008 by Fredrik Lundh. See header in `ElementTree.py` for licensing information.

All software in this repository is provided  "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. 