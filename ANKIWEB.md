*Image Occlusion 2.0 Enhanced* is an updated version of the [Image Occlusion 2.0](https://github.com/tmbb/image-occlusion-2) add-on for Anki.

**Changes compared to Image Occlusion 2.0**

- new tabbed interface
- ability to create new image occlusion notes based on old ones
- new "labels" layer for occluding your own labels
- advanced keyboard controls
- multi-line entry fields
- new buttons for adding notes
- new note type with more fields
- ability to customize field names
- synchronization between image occlusion editor window and Anki's editor
- remember last used directory

...and many many other bug fixes and improvements. 

To get a full grasp of how these changes might affect your workflow I'd advise you to give the [official README](https://github.com/Glutanimate/image-occlusion-2-enhanced) a careful read-through.

**Changelog**

This section will always be updated with the latest changes to *Image Occlusion 2.0 Enhanced*:

2016-05-19: **v0.2.3** - Update mask fill colour when upgrading from Image Occlusion 2.0
2016-04-16: **v0.2.2** - Occlusions and labels are now preserved when creating new notes based on old ones
2016-04-04: **v0.2.1** - Fixes an encoding error on Windows
2016-04-03: **v0.2.0** - Initial release

**Screenshots**

![Screenshot of the masks editor](https://github.com/Glutanimate/image-occlusion-2-enhanced/blob/master/screenshots/screenshot-io-editor-1.png?raw=true)

![Screenshot of the field entry tab](https://github.com/Glutanimate/image-occlusion-2-enhanced/blob/master/screenshots/screenshot-io-editor-2.png?raw=true)

![Screenshot of the reviewer](https://github.com/Glutanimate/image-occlusion-2-enhanced/blob/master/screenshots/screenshot-io-reviewer.png?raw=true)

**Installation**

Whether you're upgrading from Image Occlusion 2.0 or starting from a fresh Anki installation, simply follow the generic download instructions listed below to download and install *Image Occlusion 2.0 Enhanced*.

**Updating**

Repeat the installation to update to the latest release of the add-on.

**Customization**

This add-on can be customized, but only to a certain degree. Please read [the corresponding section](https://glutanimate.github.io/image-occlusion-2-enhanced/#customization) of the documentation to learn which settings you can change and which you should stay away from.

**Usage**

The core functionality of Image Occlusion hasn't changed too much with this latest iteration of the add-on. You can still follow [tmbb's comprehensive manual](http://tmbb.bitbucket.org/image-occlusion-2/) for a general introduction into image occlusion.

For a number of pointers specific to *Image Occlusion 2.0 Enhanced* check out the [Usage and Tips section](https://glutanimate.github.io/image-occlusion-2-enhanced/#usage-and-tips) of the documentation.

You will also find lot of of video tutorials on Image Occlusion 2.0 on [YouTube](https://www.youtube.com/results?search_query=anki+image+occlusion). While *Image Occlusion 2.0 Enhanced* looks and behaves slightly differently from I/O 2.0, these should still be helpful.

**Development status**

The add-on has gone through some testing by now, but it's still in its early stages. Don't be surprised if you run into bugs, weird behaviour, or other issues - especially if you're on OS X.

As always: Use the add-on at your own risk.

Bug reports and suggestions are always welcome, but it might take me a while to get to them. Please don't post them here, as I won't be able to help you or reply. Instead, either use the [Issues page](https://github.com/Glutanimate/image-occlusion-2-enhanced/issues) on GitHub or [this discussion](https://anki.tenderapp.com/discussions/add-ons/7049-revamped-version-of-image-occlusion-2-for-anki-beta-testers-wanted) on the Anki forums.

If you know how to code please feel free to improve this project, file pull requests, etc. The code could definitely benefit from some refactoring as I am not very adept in Python.

See [here](https://github.com/Glutanimate/image-occlusion-2-enhanced#known-issues-and-limitations) for a list of known issues.

**Credits**

- [tmbb](https://github.com/tmbb) for creating Image Occlusion
- [Abdolmadi Saravi, MD](https://bitbucket.org/amsaravi/) for patching Image Occlusion to reuse existing images in the media collection and on notes
- [Ank_U](https://bitbucket.org/Ank_U/) for patching Image Occlusion to support more fields

**License and Warranty**

*Copyright © 2012-2015 tmbb*

*Copyright © 2016 Glutanimate*

*Image Occlusion 2.0 Enhanced* is licensed under the simplified BSD license.

Third-party open-source software shipped with *Image Occlusion 2.0 Enhanced*:

- [Python Imaging Library](http://www.pythonware.com/products/pil/) (PIL) 1.1.7. Copyright (c) 1997-2011 by Secret Labs AB, Copyright (c) 1995-2011 by Fredrik Lundh. Licensed under the [PIL license](http://www.pythonware.com/products/pil/license.htm)
 
- [SVG Edit](https://github.com/SVG-Edit/svgedit) 2.6. Copyright (c) 2009-2012 by SVG-edit authors. Licensed under the [MIT license](https://github.com/SVG-Edit/svgedit/blob/master/LICENSE)

- Python [ElementTree toolkit](http://effbot.org/zone/element-index.htm). Copyright (c) 1999-2008 by Fredrik Lundh. See header in `ElementTree.py` for licensing information.

All software in this package is provided  "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and non-infringement. 
