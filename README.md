# Image Occlusion Enhanced

## Overview

Image Occlusion is an add-on for the spaced repetition flashcard program [Anki](http://ankisrs.net/). It allows you to create flashcards that hide parts of an image and test your knowledge on the hidden information.

This repository hosts a forked version of the [original Image Occlusion](https://github.com/tmbb/image-occlusion-2) add-on with a number of new features.

## Table of Contents

<!-- MarkdownTOC -->

- [Screenshots](#screenshots)
- [Changes compared to the original add-on](#changes-compared-to-the-original-add-on)
    - [Updated user interface](#updated-user-interface)
    - [Updated workflow](#updated-workflow)
    - [Smaller tweaks and bug fixes](#smaller-tweaks-and-bug-fixes)
- [Installation](#installation)
- [Usage](#usage)
- [Development status](#development-status)
- [Credits](#credits)
- [License and Warranty](#license-and-warranty)

<!-- /MarkdownTOC -->

## Screenshots

<p align="center">
    <img src="/screenshots/screenshot-io-editor-1.png?raw=true">
    <img src="/screenshots/screenshot-io-editor-2.png?raw=true">
    <img src="/screenshots/screenshot-io-reviewer.png?raw=true">
</p>

## Changes compared to the original add-on

### Updated user interface

- **Tabs**
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
        * <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>R</kbd>: Reset all fields
        * <kbd>Ctrl</kbd> + <kbd>R</kbd>: Reset all fields aside from *Sources*, *Tags*, and *Deck*
        * <kbd>Alt</kbd> + <kbd>C</kbd>: Close window (replaces <kbd>Esc</kbd> which was too easy to hit by accident)
- **Improvements to the Masks Editor**
    + Images are now automatically fit to the canvas, making for a much better experience when working with larger images
    + Also, SVG-Edit is now resized automatically to fit the window size (thanks to [jameskraus](https://github.com/jameskraus))
    + You can now use <kbd>Ctrl</kbd> + <kbd>Mousewheel</kbd> to zoom
    + The masks editor now comes with a *Labels* layer by default. You can use this to add labels or draw on your image before occluding it. See [Making full use of SVG-Edit](#making-full-use-of-svg-edit).
    + New tools available in the masks editor:
        * eyedropper tool - Transfer colour and other properties from one element to another
        * arrows / markers tool - Add arrow heads to your lines
        * insert shapes tool - Palette of shapes that you can insert into you document
- **Updated toolbar button**
    - the icon is now more in line with rest of the toolbar and comes with a tooltip
- **Updated options window**
    + comes with new colour previews

### Updated workflow

- **New note type**
    + the new note type is called *Image Q/A - 2.0 Enhanced* and comes with five additional fields, two out of which can be updated via the image occlusion dialog.
        * the new fields are called `Remarks`, `Sources`, `TempField3`, `TempField4`, `TempField5`
        * only the first two can be updated via the image occlusion dialog. The remaining three are there as a reserve for possible changes in the future. I'd advise against using them as they won't work properly with some of the add-on's features (e.g. reusing field contents on existing IO notes)
    + you can transfer your old image occlusion notes to this note type via the "Change note type" dialog in the Browser if you want.
- **Simpler card template**
    + now uses CSS instead of inline styles for easier customization
    + includes the new *Remarks* and *Sources* fields
- **Reuse existing image occlusion notes**
    + invoking image occlusion on an existing note of the new note type will now launch a new instance of IO pre-loaded with all the data of your old note. You can use this feature to quickly create new IO notes based on old ones
- **Synchronization between IO Editor and Anki's editor window**
    + when creating a new IO note, the add-on will now try to keep some fields synchronized with Anki's note editor. This makes it easier to alternate between IO and other note types.
        * The following fields are currently synchronized: *Tags* and *Sources*
        * In practice this means that if your regular note type (e.g. basic) has a *Sources* field, then IO will copy the value of that field over when it's launched and copy it back when new IO notes have been generated
- **Remember last used directory**
    + IO will now try to set the file selection directory based on the last used directory

### Smaller tweaks and bug fixes

- **Packaging**
    + drastically reduced add-on size by trimming down local version of PIL
    + removed SVG-edit 2.7 from the repository
        * in my experience, SVG-Edit 2.7 was too slow and buggy to be used properly with IO. I removed it to reduce development overhead and confusion. I might give more recent versions of SVG-Edit a try in the future, but for now 2.6 remains the most performant release for IO.
- **Bug fixes**
    + fixed a few issues with SVG-edit 2.6
        * fixed mousewheel zoom on the canvas
        * fixed a few confusing warnings and error messages that would appear in Anki's stdout
    + fix a bug that would create the wrong SVG masks when changing the z-index of added layers
        * this means that you can now create as many additional layers as you want and arrange them in whatever way you want
        * you could, for instance, create a new layer and use it to add new labels to an image. In order to occlude them you would then simply have to move the layer below the Shapes layer. The add-on will take care of using the right layer for the SVG masks automatically. See [Making full use of SVG-Edit](#making-full-use-of-svg-edit).
    + fixed a bug that would cause modified colour settings not to be saved
    + partially fixed handling of special characters in file names on Windows
- **Tweaks**
    + use a proper SVG namespace, so that the resulting images can be read by any image viewer
    + assign `question-element` IDs to SVG question shapes
        * at some point in the future this might make it possible to target the question shapes via javascript or CSS
    + added tooltips to most UI elements to make things easier for new users
    + disabled a note type upgrade check that would revert any changes applied via the card template editor
        * any modifications to your IO card templates will now be preserved across upgrades of the add-on
    + changed sort field of IO notes to the header. This makes it easier to identify specific notes in the card browser.
    + changed default shape colour from white to dark-turquoise to make recognition of occlusions on white backgrounds easier
    + remember size and position of Editor window

All future changes and updates will be documented on the [Releases](https://github.com/Glutanimate/image-occlusion-enhanced/releases) page.

## Installation

**Installation from AnkiWeb**

Please follow the installation instructions on [Ankiweb](https://ankiweb.net/shared/info/1111933094).

**Manual installation**

- Grab the latest release of the add-on from [Releases](https://github.com/Glutanimate/image-occlusion-enhanced/releases)
- Extract the zip file
- Launch Anki and open the add-on directory by going to *Tools* → *Add-ons* → *Open add-on directory*
- If an earlier version of Image Occlusion is installed you will have to remove it first by finding and deleting the `image_occlusion_2` folder and `Image Occlusion 2.py` file
- Having done that, proceed to copy `image_occlusion_2` and `Image Occlusion 2.py` from the extracted zip file into your add-on directory
- Restart Anki
- *Image Occlusion Enhanced* should now be installed

**Updates**

New versions and changelogs will be posted on the [GitHub Releases page](https://github.com/Glutanimate/image-occlusion-enhanced/releases) and later uploaded to AnkiWeb.

## Usage

See [here](https://github.com/Glutanimate/image-occlusion-enhanced/wiki/Usage).

## Development status

A lot of the persistent issues with the Image Occlusion series of add-ons are still present in this fork. Please don't be surprised if you run into bugs, weird behaviour, or other issues. This is especially true if you are using the add-on on macOS, as the macOS version of Anki has always suffered from a number of compatibility issues with SVG Edit.

For a list of known issues please check out the [issues page](https://github.com/Glutanimate/image-occlusion-enhanced/issues). Bug reports and suggestions are always welcome, but it might take me a while to get to them. If you know how to code please feel free to improve this project, file pull requests, etc.

## Credits

Most of the credit for this add-on goes to [Tiago Barroso (tmbb)](https://github.com/tmbb) who developed the original Image Occlusion and Image Occlusion 2.0 add-ons. *Image Occlusion Enhanced* would not exist without him.

I would also like to thank the following contributors:

- [Abdolmadi Saravi](https://bitbucket.org/amsaravi/) for patching Image Occlusion to reuse existing images in the media collection and on notes
- [Ank_U](https://bitbucket.org/Ank_U/) for modifying Image Occlusion to support more fields

## License and Warranty

*Copyright © 2012-2015 tmbb*

*Copyright © 2016 Glutanimate*

Third-party open-source software shipped with *Image Occlusion Enhanced*:

- [Python Imaging Library](http://www.pythonware.com/products/pil/) (PIL) 1.1.7. Copyright (c) 1997-2011 by Secret Labs AB, Copyright (c) 1995-2011 by Fredrik Lundh. Licensed under the [PIL license](http://www.pythonware.com/products/pil/license.htm)
 
- [SVG Edit](https://github.com/SVG-Edit/svgedit) 2.6. Copyright (c) 2009-2012 by SVG-edit authors. Licensed under the [MIT license](https://github.com/SVG-Edit/svgedit/blob/master/LICENSE)

- Python [ElementTree toolkit](http://effbot.org/zone/element-index.htm). Copyright (c) 1999-2008 by Fredrik Lundh. See header in `ElementTree.py` for licensing information.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. As usual: Use this add-on at your own risk.