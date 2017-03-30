# Image Occlusion Enhanced

## Overview

*Image Occlusion Enhanced* is an add-on for the spaced repetition flashcard program [Anki](http://ankisrs.net/). It allows you to create flashcards that hide parts of an image to test your knowledge of that hidden information.

## Table of Contents

<!-- MarkdownTOC -->

- [Screenshots](#screenshots)
- [Changes Compared to Image Occlusion 2.0](#changes-compared-to-image-occlusion-20)
    - [Overview](#overview)
    - [Updated Information](#updated-information)
- [Documentation](#documentation)
- [Help](#help)
- [Development Status](#development-status)
- [Credits](#credits)
- [License and Warranty](#license-and-warranty)

<!-- /MarkdownTOC -->

## Screenshots

*Creating Cards With the Add-on:*

<img src="/screenshots/screenshot-io-editor-1.png?raw=true">
<img src="/screenshots/screenshot-io-editor-2.png?raw=true">

*Reviewing Generated Cards:*

<img src="/screenshots/screenshot-io-reviewer.png?raw=true">

## Changes Compared to Image Occlusion 2.0

### Overview

- **Modify Existing Notes**
    + Update and modify your IO notes to your heart's content
- **Change Images on the Fly**
    + Switch to a different image right from the Editor
- **Create Custom Labels**
    + Your image is lacking a specific label? Now you can create it yourself!
- **Completely Overhauled User Interface**
    + Tabs, multi-line entry fields, numerous new hotkey assignments
- **New Occlusion Mode**
    + Hides all labels on the question side, and reveals all of them on the back
- **Completely Reworked Note Type**
    + 4 additional fields to give your notes enough space for all the extra information they might need
    + New intuitive field order, with the Header and Image right on top. No more issues identifying your notes in the Browser!
- **Updated Card Template**
    + Includes a button to reveal all masks
    + Should work much better on mobile now
- **Full Customization**
    + You can now add as many fields to the note type as you like
    + New Options entry for renaming default fields
- **Updated Options Interface**
    + More options, fewer bugs
- **Fully Rewritten Note Generator**
    + Faster, more extensible, and less bug-prone
- **Performance Improvements**
    + Smaller memory footprint in general use
- **Stability Improvements**
    + Bug fixes everywhere

### Updated Information

Please make sure to check out the [Releases](https://github.com/Glutanimate/image-occlusion-enhanced/releases) page for more details about all recent changes to the add-on.

## Documentation

The installation and use of the add-on is detailed in the [Wiki section](https://github.com/Glutanimate/image-occlusion-enhanced/wiki).

## Help

Please use the [official forum thread](https://anki.tenderapp.com/discussions/add-ons/8295-image-occlusion-enhanced-official-thread) for all support requests.

## Development Status

*Image Occlusion Enhanced* should now be stable for the most part. However, there still exist a number of longstanding issues that have less to do with the add-on itself and more with Anki and the libraries it's based on. macOS, in particular, has always suffered from compatibility issues with SVG-Edit.

For a list of known issues please check out the [Issues](https://github.com/Glutanimate/image-occlusion-enhanced/issues) page. Bug reports and suggestions are always welcome, but it might take me a while to get to them. If you know how to code please feel free to improve this project, file pull requests, etc.

## Credits

*Image Occlusion Enhanced* is based on [Image Occlusion 2.0](https://github.com/tmbb/image-occlusion-2) by [Tiago Barroso](https://github.com/tmbb) and [Simple Picture Occlusion](https://github.com/steveaw/anki_addons) by [Steve AW](https://github.com/steveaw).

All credit for the original add-ons goes to their respective authors. Without their work, *Image Occlusion Enhanced* would not exist.

*Image Occlusion Enhanced* also ships with the following third-party open-source software:

- [Python Imaging Library](http://www.pythonware.com/products/pil/) (PIL) 1.1.7. Copyright (c) 1997-2011 by Secret Labs AB, Copyright (c) 1995-2011 by Fredrik Lundh. Licensed under the [PIL license](http://www.pythonware.com/products/pil/license.htm)
 
- [SVG Edit](https://github.com/SVG-Edit/svgedit) 2.6. Copyright (c) 2009-2012 by SVG-edit authors. Licensed under the [MIT license](https://github.com/SVG-Edit/svgedit/blob/master/LICENSE)

## License and Warranty

*Copyright © 2012-2015 Tiago Barroso*

*Copyright © 2013 Steve AW*

*Copyright © 2016-2017 Aristotelis P.*

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.