*Image Occlusion 2.0 Enhanced* is an updated version of the [Image Occlusion 2.0](https://github.com/tmbb/image-occlusion-2) add-on for Anki with a large number of new features and improvements.

**Overview of the Changes**

- new tabbed interface
- multi-line entry fields
- new buttons for adding notes
- advanced keyboard controls
- new "labels" layer for occluding custom labels
- new note type with more fields
- ability to customize field names
- ability to reuse existing i/o notes
- synchronization between image occlusion editor window and Anki's editor
- remember last used directory

...and many many other bug fixes and improvements. 

As you can probably tell, there have been some significant changes to how Image Occlusion behaves. With that in mind, I'd advise you give the [README on my GitHub repository](https://github.com/Glutanimate/image-occlusion-2-enhanced) a full read, as it elaborates on each of these changes and how they will affect your workflow.

**Screenshots**

![Screenshot of the Masks Editor](https://github.com/Glutanimate/image-occlusion-2-enhanced/blob/master/screenshots/screenshot-io-editor-1.png?raw=true)

![Screenshot of the field entry tab](https://github.com/Glutanimate/image-occlusion-2-enhanced/blob/master/screenshots/screenshot-io-editor-2.png?raw=true)

![Screenshot of the reviewer](https://github.com/Glutanimate/image-occlusion-2-enhanced/blob/master/screenshots/screenshot-io-reviewer.png?raw=true)

**Development status**

While this add-on has gone through some testing on Linux and Windows by now, it's still in its early stages. If you use this add-on do not be surprised if you run into bugs, weird behaviour or other issues - especially if you're on OS X.

As always: Use this add-on at your own risk.

Bug reports and suggestions are always welcome, but it might take me a while to get to them. Please don't post them here, as I won't be able to help you or reply to them. Instead, either use the [Issues page](https://github.com/Glutanimate/image-occlusion-2-enhanced/issues) on GitHub or [this discussion](https://anki.tenderapp.com/discussions/add-ons/7049-revamped-version-of-image-occlusion-2-for-anki-beta-testers-wanted) on the Anki forums.

If you know how to code please feel free to improve this project, file pull requests, etc. The code could definitely benefit from some refactoring as I am not very adept in Python.

See [here](https://github.com/Glutanimate/image-occlusion-2-enhanced#known-issues-and-limitations) for a list of known issues.

**Installation**

You can install this like you would with any other add-on. It doesn't matter if Image Occlusion 2.0 has been installed previously, as the installation will automatially overwrite any existing files.

**Customization**

*Image Occlusion 2.0 Enhanced* can be customized, but only to a certain degree. Please read [this](https://glutanimate.github.io/image-occlusion-2-enhanced/#customization) to learn which settings you can change and which you should never touch.

**Usage**

The core functionality of Image Occlusion hasn't changed much with this latest iteration of the add-on, so you can still follow [tmbb's comprehensive manual](http://tmbb.bitbucket.org/image-occlusion-2/) for a full introduction into image occlusion.

For a number of pointers specific to *Image Occlusion 2.0 Enhanced* check out the [Usage and Tips section](https://glutanimate.github.io/image-occlusion-2-enhanced/#usage-and-tips) of the README.

You will also find lot of of video tutorials on Image Occlusion 2.0 on [YouTube](https://www.youtube.com/results?search_query=anki+image+occlusion). While *Image Occlusion 2.0 Enhanced* looks and behaves slightly differently from I/O 2.0, these should still be helpful; and who knows, someone might take the time to create a tutorial on this specific version of I/O. If so, please contact me on the forums and i'll link it here.

**Changes**

2016-04-04: v0.2.1 - fixes an encoding error on Windows
2016-04-03: v0.2.0 - Initial release

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

All software in this package is provided  "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. 
