<p align="center"><img src="screenshots/logo.png" width=381 height=224></p>

<h2 align="center">Image Occlusion Enhanced for Anki</h2>

<p align="center">
<a title="Latest (pre-)release" href="https://github.com/glutanimate/image-occlusion-enhanced/releases"><img src ="https://img.shields.io/github/release-pre/glutanimate/image-occlusion-enhanced.svg?colorB=brightgreen"></a>
<a title="License: GNU AGPLv3" href="https://github.com/glutanimate/image-occlusion-enhanced/blob/master/LICENSE"><img  src="https://img.shields.io/badge/license-GNU AGPLv3-green.svg"></a>
<a title="Rate on AnkiWeb" href="https://ankiweb.net/shared/info/1374772155"><img src="https://glutanimate.com/logos/ankiweb-rate.svg"></a>
<br>
<a title="Buy me a coffee :)" href="https://ko-fi.com/X8X0L4YV"><img src="https://img.shields.io/badge/ko--fi-contribute-%23579ebd.svg"></a>
<a title="Support me on Patreon :D" href="https://www.patreon.com/bePatron?u=7522179"><img src="https://img.shields.io/badge/patreon-support-%23f96854.svg"></a>
<a title="Follow me on Twitter" href="https://twitter.com/intent/user?screen_name=glutanimate"><img src="https://img.shields.io/twitter/follow/glutanimate.svg"></a>
</p>

> Flashcards from images – the easy way

*Image Occlusion Enhanced* is an add-on for the spaced repetition flashcard app [Anki](https://apps.ankiweb.net/) that allows you to create image-based cloze-deletions.

### Table of Contents <!-- omit in toc -->

<!-- MarkdownTOC levels="1,2,3" -->

- [Screenshots](#screenshots)
- [Installation](#installation)
- [Documentation](#documentation)
- [Building](#building)
- [Contributing](#contributing)
- [License and Credits](#license-and-credits)

<!-- /MarkdownTOC -->

### Screenshots

*Creating Cards With the Add-on:*

<img src="screenshots/screenshot-io-editor-1.png">
<img src="screenshots/screenshot-io-editor-2.png">

*Reviewing Generated Cards:*

<img src="screenshots/screenshot-io-reviewer.png">

### Installation

#### AnkiWeb <!-- omit in toc -->

The easiest way to install Image Occlusion Enhanced is through [AnkiWeb](https://ankiweb.net/shared/info/1374772155).

#### Manual installation <!-- omit in toc -->

Please click on the entry corresponding to your Anki version:

<details>

<summary><i>Anki 2.1</i></summary>

1. Make sure you have the [latest version](https://apps.ankiweb.net/#download) of Anki 2.1 installed. Earlier releases (e.g. found in various Linux distros) do not support `.ankiaddon` packages.
2. Download the latest `.ankiaddon` package from the [releases tab](https://github.com/glutanimate/image-occlusion-enhanced/releases) (you might need to click on *Assets* below the description to reveal the download links)
3. From Anki's main window, head to *Tools* → *Add-ons*
4. Drag-and-drop the `.ankiaddon` package onto the add-ons list
5. Restart Anki

</details>

<details>

<summary><i>Anki 2.0</i></summary>

1. Go to *Tools* → *Add-ons* → *Open add-ons folder*
2. Find and delete the `Image Occlusion Enhanced.py` file if it already exists.
3. See if you can find a `image_occlusion_enhanced` folder. If so:
    1. If the folder contains a `meta.json` file, copy the file to a safe location. This will allow you to preserve your current settings.
    2. Proceed to delete the `image_occlusion_enhanced` folder
4. Download and extract the latest Anki 2.0 add-on release from the [releases tab](https://github.com/glutanimate/image-occlusion-enhanced/releases) (you might need to click on *Assets* below the description to reveal the download links)
5. Move the extracted `Image Occlusion Enhanced.py` and `image_occlusion_enhanced` into the add-ons folder
6. Optional: Place the `meta.json` file back into the directory if you created a copy beforehand.
7. Restart Anki

</details>

### Documentation

The installation and use of this add-on is detailed in the [Wiki](https://github.com/Glutanimate/image-occlusion-enhanced/wiki) and a [series of video tutorials on YouTube](https://www.youtube.com/playlist?list=PL3MozITKTz5YFHDGB19ypxcYfJ1ITk_6o). More information may also be found in the [AnkiWeb description](docs/description.md).

### Building

With [Anki add-on builder](https://github.com/glutanimate/anki-addon-builder/) installed:

    git clone https://github.com/glutanimate/image-occlusion-enhanced.git
    cd image-occlusion-enhanced
    aab build

For more information on the build process please refer to [`aab`'s documentation](https://github.com/glutanimate/anki-addon-builder/#usage).

### Contributing

Contributions are welcome! Please review the [contribution guidelines](./CONTRIBUTING.md) on how to:

- Report issues
- File pull requests
- Support the project as a non-developer

### License and Credits

*Image Occlusion Enhanced* is

*Copyright © 2012-2015 [Tiago Barroso](https://github.com/tmbb)*

*Copyright © 2013 [Steve AW](https://github.com/steveaw)*

*Copyright © 2016-2019 [Aristotelis P.](https://glutanimate.com/) (Glutanimate)*

With code contributions from: Damien Elmes, Kyle Mills, James Kraus, Matt Restko

-----

*Image Occlusion Enhanced* is based on [Image Occlusion 2.0](https://github.com/tmbb/image-occlusion-2) by Tiago Barroso and [Simple Picture Occlusion](https://github.com/steveaw/anki_addons) by Steve AW. All credit for the original add-ons goes to their respective authors. *Image Occlusion Enhanced* would not exist without their work.

I would also like to extend my heartfelt thanks to everyone who has helped with testing, provided suggestions, or contributed in any other way.

*Image Occlusion Enhanced* ships with the following third-party open-source software:

- [SVG Edit](https://github.com/SVG-Edit/svgedit) 2.6. Copyright (c) 2009-2012 by SVG-edit authors. Licensed under the MIT license.

- [Python Imaging Library](http://www.pythonware.com/products/pil/) (PIL) 1.1.7. Copyright (c) 1997-2011 by Secret Labs AB, Copyright (c) 1995-2011 by Fredrik Lundh. Licensed under the [PIL license](http://www.pythonware.com/products/pil/license.htm)

- [imagesize.py](https://github.com/shibukawa/imagesize_py) v0.7.1. Copyright (c) 2016 Yoshiki Shibukawa. Licensed under the MIT license.

Image Occlusion Enhanced is free and open-source software. The add-on code that runs within Anki is released under the GNU AGPLv3 license, extended by a number of additional terms. For more information please see the [LICENSE](https://github.com/glutanimate/image-occlusion-enhanced/blob/master/LICENSE) file that accompanied this program.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY.

----
**:heart: My heartfelt thanks goes out to everyone who has supported this add-on through their [tips, contributions, or any other means](https://github.com/glutanimate/docs/blob/master/anki/add-ons/CONTRIBUTING.md#how-to-contribute-to-my-anki-add-ons) (you know who you are!). All of this would not have been possible without you. Thank you for being awesome!**
