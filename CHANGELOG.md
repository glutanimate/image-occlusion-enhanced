# Changelog

All notable changes to Image Occlusion Enhanced will be documented here. You can click on each release number to be directed to a detailed log of all code commits for that particular release. The download links will direct you to the GitHub release page, allowing you to manually install a release if you want.

If you enjoy Image Occlusion Enhanced, please consider supporting my work on Patreon, or by buying me a cup of coffee :coffee::

<p align="center">
<a href="https://www.patreon.com/glutanimate" rel="nofollow" title="Support me on Patreon 😄"><img src="https://glutanimate.com/logos/patreon_button.svg"></a>      <a href="https://ko-fi.com/X8X0L4YV" rel="nofollow" title="Buy me a coffee 😊"><img src="https://glutanimate.com/logos/kofi_button.svg"></a>
</p>

:heart: My heartfelt thanks goes out to everyone who has supported this add-on through their tips, contributions, or any other means (you know who you are!). All of this would not have been possible without you. Thank you for being awesome!

## [Unreleased]

## [1.3.0-alpha6] - 2020-04-28

### [Download](https://github.com/glutanimate/image-occlusion-enhanced/releases/tag/v1.3.0-alpha6)

### Fixed

- Fixed note editing support on Anki 2.1.24+ (thanks to @zjosua for the fix!)
- Fixed a rare error that would occur when the add-on would update its template (thanks to Emma for the report!)

## [1.3.0-alpha5] - 2019-09-11

### [Download](https://github.com/glutanimate/image-occlusion-enhanced/releases/tag/v1.3.0-alpha5)

### Fixed

- Handle malformatted and unrecognized image formats more graciously (thanks to Audrey for the report)

## [1.3.0-alpha4] - 2019-04-14

### Added

- Introduces .ankiaddon packaging format for GitHub builds

### Fixed

- Fixes error message when deleting current note in editing session (#87, thanks to @zjosua)
- Fixes rare error message when closing card browser

## [1.3.0-alpha3] - 2018-12-24

### Fixed

- Another uuid-related fix

## [1.3.0-alpha2] - 2018-12-11

### Fixed

- Quick hotfix for Anki 2.1.6 compatibility (now packages the UUID module which no longer seems to ship with Anki 2.1.6's Python distribution)

## [1.3.0-alpha2] - 2018-12-11

### Fixed

- Quick hotfix for Anki 2.1.6 compatibility (now packages the UUID module which no longer seems to ship with Anki 2.1.6's Python distribution)
    
## [1.3.0-alpha1] - 2018-06-29

### Notes

This marks the first official release of Image Occlusion Enhanced for Anki 2.1! Porting the add-on to Anki 2.1 has been [an arduous journey](https://github.com/glutanimate/image-occlusion-enhanced/projects/1), but I'm happy we're finally here. 

Before we dive into the actual changelog I would just like to thank each and everyone of you who has helped in this effort, either by [contributing to the codebase](https://github.com/glutanimate/image-occlusion-enhanced/graphs/contributors), filing [bug reports](https://github.com/glutanimate/image-occlusion-enhanced/issues), or by supporting my work directly through [tips](https://glutanimate.com/tip-jar/), [Patreon](https://www.patreon.com/glutanimate), or add-on commissions!

In particular I would like to thank the following awesome people who support me on Patreon / have supported me at some point during the development of Image Occlusion Enhanced for Anki 2.1:

- Blacky 372
- Sebastián Ortega
- Edan Maor
- Peter Benisch

**Important**: This is an Anki 2.1-only release (for now)

### Added

The primary focus in this release was Anki 2.1 compatibility, but v1.3.0 also comes with a number of nifty **new features** which I would like to highlight first:

- You can now **occlude images in any note type you want**, either by **right clicking** on them and selecting the respective option, or by using the Image Occlusion button!
- As an added bonus: The new context menu introduced by the add-on will also allow you to **open any image with your default system viewer** – a great way to perform quick image editing tasks when needed.
- The masks editor now allows you to **add hints to your occlusion shapes**. In order to do so, simply create a text element on top of a shape and group it with the shape.
- You can now set a **custom hotkey** for invoking I/O. Gone are the days of conflicts with different keyboard locales!
- In-app **help screens** now guide users through the basic use of the add-on (including how to add cards, edit them, group masks, label items, etc.)

(Some of the changes above will likely also be part of a future release of v1.3.0 for Anki 2.0.)

### Fixed

v1.3.0 for Anki 2.1 also comes with a plethora of **bug fixes** (some of the bugs fixed in this update have plagued I/O ever since its original release!):

- Fix: Automatically remove accidentally drawn shapes. This addresses instances where users would end up with more cards than they should have because of invisible shapes drawn by the oversensitive editor component (especially with touch interfaces)
- Fix: Resolve issues with unicode characters in Anki path and/or image path. This should fix most of the problems users were experiencing with non-latin locales (e.g. the I/O editor screen remaining blank because SVG-Edit did not load, or various UnicodeError messages)
- Fix: More robust I/O editor instantiation. Should help address some of the stability issues users experienced over longer card creation sessions (e.g. needing to restart Anki to get I/O working again).
- and a large number of other smaller bug fixes and improvements

### Changes

There also some **changes to the workflow** in I/O v1.3.0 that you need to be aware of:

- The default hotkey for invoking I/O is now Ctrl+Shift+O (customizable through the new settings entry)
- The card generation options have been renamed and simplified: You can now choose between "Hide All, Guess One" (used to be "Hide All, Reveal One") and "Hide One, Guess One" (used to be "Hide All, Reveal All"). My hope with these new names is that they will be more intuitive for new users. (thanks a lot to Tiago Barroso for the suggestion!)
- "Hide All, Reveal All" is no longer available as a mask generation option. With the mask reveal button introduced in recent I/O releases it no longer served much of a purpose and was mostly confusing new users as they expected it to work like a grouped occlusion of all shapes.

    Just in case you were using this option and are now wondering how to cover the same use cases:
        
    + In case you were using "Hide All, Reveal All" to uncover all labels on the back: Try to switch to using "Hide One, Guess One" coupled with the mask reveal button on the backside (hotkey: `G`)
    + In case you were using "Hide All, Reveal All" to 'group' your shapes: Use the [actual grouping feature](https://github.com/glutanimate/image-occlusion-enhanced/wiki/Advanced-Use#grouping-items) instead

### Limitations

There are a number of known limitations to this alpha release that you need to be aware of:

- Due to compatibility issues between SVG-Edit and the new Chromium renderer in Anki 2.1 some of the features in the masks editor no longer work correctly. My hope is to address these in the following beta release:
    + [Pointer not changing to selection mode when clicking on shape](https://github.com/glutanimate/image-occlusion-enhanced/issues/54)
    + [Path tool no longer working](https://github.com/glutanimate/image-occlusion-enhanced/issues/56)
    + [https://github.com/glutanimate/image-occlusion-enhanced/issues/57](https://github.com/glutanimate/image-occlusion-enhanced/issues/57)
- Please do not invoke the add-on's settings menu while the I/O Editor is running. There is currently no support for updating I/O editing sessions at runtime, and while most settings will simply only not be applied, others might cause the add-on to stop working correctly until the editor session is restarted. The same applies to modifications to the add-on's note type via Anki's built-in note type manager.

Of course there also bound to be some unforeseen bugs and regressions in the alpha. If you experience any of these please make sure to either report them on the add-on's [bug tracker](https://github.com/glutanimate/image-occlusion-enhanced/issues) or in the [official support thread](https://anki.tenderapp.com/discussions/add-ons/8295-image-occlusion-enhanced-official-thread). 
    
## [1.2.2] - 2017-04-04

### Fixed

- Fixed: rare AttributeError when changing the image
- Fixed: GIFs should be supported on Windows and macOS now
- Fixed: incompatibility with upcoming release of "Quick not and deck buttons" add-on
    
## [1.2.1] - 2017-02-14

### Fixed

- Fixed: Unicode TypeError on Windows

    
## [1.2.0] - 2017-02-14

### Added

- **New**: Hotkey for toggling masks on the answer side (`G`)
- **New**: Preserve scrollbar position when revealing the answer
- **New**: Reuse existing images when creating multiple occlusion sets from the same base image
- **New**: Limit image display height in editor fields in order to improve navigating notes in the card browser

### Changed

- Changed: Updated default field order to move the question mask below the original image. Should make it easier to identify each respective card in the browser.

### Fixed

- Fixed: Remove card margins on mobile devices
- Fixed: Increased size of mask toggle button on mobile devices

### Notes

Please note that the changes to the field order and card templates only apply to new installations of the add-on. I've decided against enforcing these changes on existing installations as that would undo any customizations you might have applied to the note type. If you'd like to update your cards with these changes, please follow [the instructions in the Wiki](https://github.com/Glutanimate/image-occlusion-enhanced/wiki/Troubleshooting#resetting-note-type-and-template-to-the-defaults) to reset your field order and card template to the (new) defaults.

    
## [1.1.1] - 2017-01-20

### Fixed

- Clicking on a context menu entry would launch the web browser under some circumstances (thanks to PolymorphicVTach for the report)

    
## [1.1.0] - 2017-01-14

### Added

- **New**: Grid-snapping for shapes can now be toggled via a button in the upper panel (hotkey: _Shift+S_)
- **New**: Panning tool (hotkey: _Q_)
- **New**: Control zoom levels with _+/-_
- **New**: Reset zoom with _0_

### Fixed

- Fixed: Error when marking the Image field as sticky (thanks to vidale3 for the report)
- Fixed: _Ctrl+Shift+T_ now focuses the tag field again

### Changed

- Improved: Images now use the available canvas space slightly more efficiently
- plus a number of smaller improvements and bug fixes

    
## [1.0.4] - 2016-12-14

### Added

- add hotkeys for switching between layers (Ctrl+Shift+L and Ctrl+Shift+M)

### Fixed

- fix an encoding issue when editing labels

## [1.0.3] - 2016-12-01

### Fixed

- fix a runtime error that was occuring for some Windows users

    
## [1.0.2] - 2016-11-24

### Fixed

- Fix unicode support in labels

    
## [1.0.1] - 2016-11-16

### Fixed

- Restore proper window controls on Windows

    
## [1.0.0] - 2016-11-09

The most comprehensive update to _Image Occlusion Enhanced_ since its inception:

### Added

- **Modify Existing Notes**
  - Need to remove or add a shape, update a field, or resize all masks? Now you can!
- **Change Images on the Fly**
  - Simply switch to a different image to occlude right from the IO Editor
- **New Occlusion Mode**
  - Hides all labels on the question side, and reveals all of them on the back
  - The different occlusion modes now also follow a new naming scheme. It should be self-explanatory what each of them does, but you can hover over the respective button to get a more detailed description
- **Completely Reworked Note Type**
  - 4 additional fields to give your notes enough space for all the extra information they might need
  - New intuitive field order, with the Header and Image right on top. No more issues identifying your notes in the Browser!
- **Full Customization**
  - You can now add as many fields to the note type as you like
  - New Options entry for renaming default fields

### Changed

- **Updated Options Interface**
  - More options, fewer bugs
- **Fully Rewritten Note Generator**
  - Faster, more extensible, and less bug-prone
- **Performance Improvements**
  - Smaller memory footprint in general use (by about 30MB)

### Fixed

- **Stability Improvements**
  - Bug fixes everywhere

    
## [1.0.0-beta6] - 2016-11-07

### Added

- **New**: Use a button instead of clicking the image to reveal all masks. The old method interfered with gesture support on mobile clients.
- **New**: Default action hotkey (Ctrl+Return)

### Changed

- **Other**: Set Extra fields to be note-specific by default

## [1.0.0-beta5] - 2016-11-05

### Added

- **New**: Reveal all occluded areas when clicking image on answer side – This is a somewhat of an experimental change as there's no official support for JavaScript in Anki. Note: Normally this would require an update to the IO note type, but given that this is an experimental change I decided not to force the update. Instead, feel free to test this new feature on an empty Anki profile.

### Fixed

- **Fix**: Force media sync when updating mask files
- **Fix**: Handle deleted IO note type more graciously

### Changed

- **Other**: Updated tooltips for occlusion types (@dgbeecher)

    
## [1.0.0-beta4] - 2016-10-18

### Changed

- Updated the default card template
  - The new template includes the two new extra fields and uses a more elaborate layout for all sections below the image. It also provides much needed adjustments of the styling for AnkiMobile and AnkiDroid
  - **Important**: This will overwrite any previous changes to the card templates you might have performed. If you've used a previous Beta and customized your template or styles please make sure to back them up before installing this version.
  - FWIW, drastic changes like this will only happen with Beta releases. If I ever see the need to change the template for a stable update I will implement it in a way that asks you for confirmation first.

### Fixed

- Fixed a number of smaller issues (thanks to @dgbeecher for reporting these!)

    
## [1.0.0-beta3] - 2016-10-15

### Added

- New options for labels and lines
- New option for ignoring fields when editing
- New error dialog that provides a help button

### Changed

- More verbose tooltips when generating notes

### Fixed

- Line color and width should now be preserved when switching to a different tool
- Lots of smaller bug fixes


## [1.0.0-beta2] - 2016-10-13

### Fixed

- Possible fix for a module import error on macOS

## [1.0.0-beta1] - 2016-10-12

A tremendous version jump, I know, but this is the most comprehensive update to Image Occlusion since the release of _Image Occlusion Enhanced_

### Added

- **Modify Existing Notes**
  - Need to remove or add a shape, update a field, or resize all masks? Now you can!
- **Change Images on the Fly**
  - Simply switch to a different image to occlude right from the IO Editor
- **New Occlusion Mode**
  - Hides all labels on the question side, and reveals all of them on the back
  - The different occlusion modes now also follow a new naming scheme. It should be self-explanatory what each of them does, but you can hover over the respective button to get a more detailed description
- **Completely Reworked Note Type**
  - 4 additional fields to give your notes enough space for all the extra information they might need
  - New intuitive field order, with the Header and Image right on top. No more issues identifying your notes in the Browser!
- **Full Customization**
  - You can now add as many fields to the note type as you like
  - New Options entry for renaming default fields

### Changed

- **Updated Options Interface**
  - More options, fewer bugs
- **Fully Rewritten Note Generator**
  - Faster, more extensible, and less bug-prone
- **Performance Improvements**
  - Smaller memory footprint in general use (by about 30MB)

### Fixed

- **Stability Improvements**
  - Bug fixes everywhere
    
## [0.3.0] - 2016-09-28

### Changed

- SVGEdit: fixed most of the random opacity changes
- SVGEdit: fixed some issues with the stroke and fill attributes
- SVGEdit: changed default text font
- SVGEdit: added initial fill color to the color palette
- SVGEdit: updated hotkey assignments to improve usability
- SVGEdit: added "Esc" hotkey to deselect current selection

    
## [0.2.6] - 2016-09-22

### Changed

- improved IO note type sanity checks

## [0.2.5] - 2016-09-12

### Changed

- New add-on name
- Added link to new Wiki
 
## [0.2.4] - 2016-08-25

### Fixed

- Several bug fixes and improvements

## [0.2.3] - 2016-05-19

### Changed

- Update mask fill colour when upgrading from Image Occlusion 2.0

    
## [0.2.2] - 2016-04-16

### Added

- added support for preserving occlusions and labels when creating new notes based on old one

    
## [0.2.1] - 2016-04-04

### Fixed

- fixed an encoding error on Windows

    
## [0.2.0] - 2016-04-03

### Changed

- first release on AnkiWeb
- fixes a number of issues with SVG-Edit

    
## [0.1.4] - 2016-04-01

### Changed

- improvements to the Masks editor
- bug fix: support for special characters in file names on Windows

    
## [0.1.3] - 2016-04-01

### Changed

- update the Options window and Help link
- remember window geometry across sessions
- allow upgrading directly from I/O 2.0
- a few miscellaneous fixes

    
## [0.1.2] - 2016-03-29

### Fixed

- More fixes.

    
## [0.1.1] - 2016-03-28

### Fixed

- A few smaller fixes.


## v0.1.0 - 2016-03-28

### Added

- First release of Image Occlusion 2.0 Enhanced.
- Still needs a lot of testing!


[Unreleased]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.3.0-alpha5...HEAD
[1.3.0-alpha5]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.3.0-alpha4...v1.3.0-alpha5
[1.3.0-alpha4]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.3.0-alpha3...v1.3.0-alpha4
[1.3.0-alpha3]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.3.0-alpha2...v1.3.0-alpha3
[1.3.0-alpha2]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.3.0-alpha1...v1.3.0-alpha2
[1.3.0-alpha1]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.2.2...v1.3.0-alpha1
[1.2.2]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.0.4...v1.1.0
[1.0.4]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.0.0-beta6...v1.0.0
[1.0.0-beta6]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.0.0-beta5...v1.0.0-beta6
[1.0.0-beta5]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.0.0-beta4...v1.0.0-beta5
[1.0.0-beta4]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.0.0-beta3...v1.0.0-beta4
[1.0.0-beta3]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.0.0-beta2...v1.0.0-beta3
[1.0.0-beta2]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v1.0.0-beta1...v1.0.0-beta2
[1.0.0-beta1]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.3.0...v1.0.0-beta1
[0.3.0]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.2.6...v0.3.0
[0.2.6]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.2.5...v0.2.6
[0.2.5]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.1.4...v0.2.0
[0.1.4]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/Glutanimate/image-occlusion-enhanced/compare/v0.1.0...v0.1.1

-----

The format of this file is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).