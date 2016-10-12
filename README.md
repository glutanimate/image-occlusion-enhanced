# Image Occlusion Enhanced

## Overview

*Image Occlusion Enhanced* is an add-on for the spaced repetition flashcard program [Anki](http://ankisrs.net/) that allows you to create flashcards which hide parts of an image and test your knowledge on the occluded information.

## Table of Contents

<!-- MarkdownTOC -->

- [Screenshots](#screenshots)
- [Changes compared to Image Occlusion 2.0](#changes-compared-to-image-occlusion-20)
    - [Overview](#overview)
    - [Detailed information](#detailed-information)
- [Installation](#installation)
- [Usage](#usage)
- [Development status](#development-status)
- [Supporting the development of this add-on](#supporting-the-development-of-this-add-on)
- [Credits](#credits)
- [License and Warranty](#license-and-warranty)

<!-- /MarkdownTOC -->

## Screenshots

<p align="center">
    <img src="/screenshots/screenshot-io-editor-1.png?raw=true">
    <img src="/screenshots/screenshot-io-editor-2.png?raw=true">
    <img src="/screenshots/screenshot-io-reviewer.png?raw=true">
</p>

## Changes compared to Image Occlusion 2.0

### Overview

- **Modify Existing Notes**
    + Need to remove or add a shape, update a field, or resize all masks? Now you can!
- **Change Images on the Fly**
    + Simply switch to a different image to occlude right from the IO Editor
- **Completely Overhauled User Interface**
    + Tabs, multi-line entry fields, numerous new hotkey assignments
- **New Occlusion Mode**
    + Hides all labels on the question side, and reveals all of them on the back
- **Completely Reworked Note Type**
    + 4 additional fields to give your notes enough space for all the extra information they might need
    + New intuitive field order, with the Header and Image right on top. No more issues identifying your notes in the Browser!
    + New card template which should be much easier to customize
- **Full Customization**
    + You can now add as many fields to the note type as you like
    + New Options entry for renaming default fields
- **Updated Options Interface**
    + More options, fewer bugs
- **Fully Rewritten Note Generator**
    + Faster, more extendible, and less bug-prone
- **Performance Improvements**
    + Smaller memory footprint in general use (by about 30MB)
- **Stability Improvements**
    + Bug fixes everywhere

### Detailed information

Please make sure to check out the [Releases](https://github.com/Glutanimate/image-occlusion-enhanced/releases) tab or commit log for a more detailed listing of all current and future changes to the add-on.

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

The documentation and tutorial videos have yet to be updated to reflect the large array of new features present in the 1.0 release. I hope I'll be able to change this soon.

## Development status

With the 1.0 release, *Image Occlusion Enhanced* should now be stable for the most part. However, it is still plagued by a number of longstanding issues that have less to do with the add-on itself and more with the libraries it is based on and runs in. This is particularly true for Anki/Qt on macOS, which has always suffered from compatibility issues with SVG-Edit.

For a list of known issues please check out the [issues page](https://github.com/Glutanimate/image-occlusion-enhanced/issues). Bug reports and suggestions are always welcome, but it might take me a while to get to them. If you know how to code please feel free to improve this project, file pull requests, etc.

## Supporting the development of this add-on

Quite a few people have offered to donate to this project over the last few months. I've always been very hesitant about accepting these donations. Both because of the operational overhead and because at that point I just felt like I hadn't contributed enough in terms of code to warrant these donations.

Now that 1.0 is out, with large parts of the add-on rewritten, I feel like this has become less of a concern. For that reason and because I keep receiving these donation requests, I have now added a few PayPal links at the bottom of the [AnkiWeb add-on description](https://ankiweb.net/shared/info/1111933094); not a donation link (because this is not a registered non-profit), but a couple of links you can use if you want to buy me a coffee or a sandwich to say thanks. All funds collected through this will go into fueling my late-night coding and studying sessions :).

## Credits

*Image Occlusion Enhanced* is based on [Image Occlusion 2.0](https://github.com/tmbb/image-occlusion-2) by [Tiago Barroso](https://github.com/tmbb) and [Simple Picture Occlusion](https://github.com/steveaw/anki_addons) by [Steve AW](https://github.com/steveaw).

All credit for the original add-ons goes to their respective authors. Without their work, *Image Occlusion Enhanced* would not exist.

*Image Occlusion Enhanced* also ships with the following third-party open-source software:

- [Python Imaging Library](http://www.pythonware.com/products/pil/) (PIL) 1.1.7. Copyright (c) 1997-2011 by Secret Labs AB, Copyright (c) 1995-2011 by Fredrik Lundh. Licensed under the [PIL license](http://www.pythonware.com/products/pil/license.htm)
 
- [SVG Edit](https://github.com/SVG-Edit/svgedit) 2.6. Copyright (c) 2009-2012 by SVG-edit authors. Licensed under the [MIT license](https://github.com/SVG-Edit/svgedit/blob/master/LICENSE)

## License and Warranty

*Copyright © 2012-2015 Tiago Barroso*

*Copyright © 2013 Steve AW*

*Copyright © 2016 Glutanimate*

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.