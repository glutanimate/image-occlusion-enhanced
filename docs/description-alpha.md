*Image Occlusion Enhanced* Alpha Release for Anki 2.1

This is an alpha release of Image Occlusion Enhanced for the [Anki 2.1 Beta](https://apps.ankiweb.net/docs/beta.html). Please make sure to carefully read through this description and familiarize yourself with the official Anki 2.1 beta release notes before giving the add-on a try.

The present AnkiWeb upload is temporary and will be removed in favor of the [regular add-on listing](https://ankiweb.net/shared/info/1111933094) once testing is complete.

**RELEASE LOG**

2018-06-30: **v1.3.0-alpha1** - First public release of Image Occlusion Enhanced for Anki 2.1
2017-04-17: **v1.2.2** - Last Image Occlusion Enhanced release for Anki 2.0 as of 2018-06-29.

**LATEST CHANGES AND NEWS**

*2018-06-30*

Today marks the first official release of Image Occlusion Enhanced for Anki 2.1! Porting the add-on to Anki 2.1 has been [an arduous journey](https://github.com/glutanimate/image-occlusion-enhanced/projects/1), but I'm happy we're finally here. 

Before we dive into the actual changelog I would just like to thank each and everyone of you who has helped in this effort, either by [contributing to the codebase](https://github.com/glutanimate/image-occlusion-enhanced/graphs/contributors), filing [bug reports](https://github.com/glutanimate/image-occlusion-enhanced/issues), or by supporting my work directly through [tips](https://glutanimate.com/tip-jar/), [Patreon](https://www.patreon.com/glutanimate), or add-on commissions!

In particular I would like to thank the following awesome people who support me on Patreon / have supported me at some point during the development of Image Occlusion Enhanced for Anki 2.1:

- Blacky 372
- Edan Maor
- Peter Benisch

**v1.3.0-alpha1**

The primary focus in this release was Anki 2.1 compatibility, but v1.3.0 also comes with a number of nifty **new features** which I would like to highlight first:

- You can now **occlude images in any note type you want**, either by **right clicking** on them and selecting the respective option, or by using the Image Occlusion button!
- As an added bonus: The new context menu introduced by the add-on will also allow you to **open any image with your default system viewer** – a great way to perform quick image editing tasks when needed.
- The masks editor now allows you to **add hints to your occlusion shapes**. In order to do so, simply create a text element on top of a shape and group it with the shape.
- You can now set a **custom hotkey** for invoking I/O. Gone are the days of conflicts with different keyboard locales!
- In-app **help screens** now guide users through the basic use of the add-on (including how to add cards, edit them, group masks, label items, etc.)

(Some of the changes above will likely also be part of a future release of v1.3.0 for Anki 2.0.)

v1.3.0 for Anki 2.1 also comes with a plethora of **bug fixes** (some of the bugs fixed in this update have plagued I/O ever since its original release!):

- Fix: Automatically remove accidentally drawn shapes. This addresses instances where users would end up with more cards than they should have because of invisible shapes drawn by the oversensitive editor component (especially with touch interfaces)
- Fix: Resolve issues with unicode characters in Anki path and/or image path. This should fix most of the problems users were experiencing with non-latin locales (e.g. the I/O editor screen remaining blank because SVG-Edit did not load, or various UnicodeError messages)
- Fix: More robust I/O editor instantiation. Should help address some of the stability issues users experienced over longer card creation sessions (e.g. needing to restart Anki to get I/O working again).
- and a large number of other smaller bug fixes and improvements

There also some **changes to the workflow** in I/O v1.3.0 that you need to be aware of:

- The default hotkey for invoking I/O is now Ctrl+Shift+O (customizable through the new settings entry)
- The card generation options have been renamed and simplified: You can now choose between "Hide All, Guess One" (used to be "Hide All, Reveal One") and "Hide One, Guess One" (used to be "Hide All, Reveal All"). My hope with these new names is that they will be more intuitive for new users. (thanks a lot to Tiago Barroso for the suggestion!)
- "Hide All, Reveal All" is no longer available as a mask generation option. With the mask reveal button introduced in recent I/O releases it no longer served much of a purpose and was mostly confusing new users as they expected it to work like a grouped occlusion of all shapes.

    Just in case you were using this option and are now wondering how to cover the same use cases:
        
    + In case you were using "Hide All, Reveal All" to uncover all labels on the back: Try to switch to using "Hide One, Guess One" coupled with the mask reveal button on the backside (hotkey: `G`)
    + In case you were using "Hide All, Reveal All" to 'group' your shapes: Use the [actual grouping feature](https://github.com/glutanimate/image-occlusion-enhanced/wiki/Advanced-Use#grouping-items) instead


**LIMITATIONS OF THIS ALPHA RELEASE**

There are a number of known limitations to this alpha release that you need to aware of:

- Due to compatibility issues between SVG-Edit and the new Chromium renderer in Anki 2.1 some of the features in the masks editor no longer work correctly. My hope is to address these in the following beta release:
    + [Pointer not changing to selection mode when clicking on shape](https://github.com/glutanimate/image-occlusion-enhanced/issues/54)
    + [Path tool no longer working](https://github.com/glutanimate/image-occlusion-enhanced/issues/56)
    + [https://github.com/glutanimate/image-occlusion-enhanced/issues/57](https://github.com/glutanimate/image-occlusion-enhanced/issues/57)
- Please do not invoke the add-on's settings menu while the I/O Editor is running. There is currently no support for updating I/O editing sessions at runtime, and while most settings will simply only not be applied, others might cause the add-on to stop working correctly until the editor session is restarted. The same applies to modifications to the add-on's note type via Anki's built-in note type manager.

Of course there also bound to be some unforeseen bugs and regressions in the alpha. If you experience any of these please make sure to either report them on the add-on's [bug tracker](https://github.com/glutanimate/image-occlusion-enhanced/issues) or in the [official support thread](https://anki.tenderapp.com/discussions/add-ons/8295-image-occlusion-enhanced-official-thread). Any and all feedback is appreciated!

**CREDITS AND LICENSE**

*Copyright © 2012-2015 [Tiago Barroso](https://github.com/tmbb)*
*Copyright © 2013 [Steve AW](https://github.com/steveaw)*
*Copyright © 2016-2018 [Aristotelis P.](https://glutanimate.com/)*

With code contributions from: Damien Elmes, Kyle Mills, James Kraus, Matt Restko

*Image Occlusion Enhanced* is based on [Image Occlusion 2.0](https://github.com/tmbb/image-occlusion-2) by Tiago Barroso and [Simple Picture Occlusion](https://github.com/steveaw/anki_addons) by Steve AW. All credit for the original add-ons goes to their respective authors. *Image Occlusion Enhanced* would not exist without their work.

I would also like to extend my heartfelt thanks to everyone who has helped with testing, provided suggestions, or contributed in any other way.

Licensed under the [GNU AGPL v3](https://www.gnu.org/licenses/agpl.html). The code for this add-on is available on [![GitHub icon](https://glutanimate.com/logos/github.svg) GitHub](https://github.com/glutanimate/image-occlusion-enhanced). For more information on the licensing terms and other software shipped with this package please check out the [README](https://github.com/Glutanimate/image-occlusion-enhanced#credits).

**ADD-ON COMMISSIONS**

A lot of my add-ons were commissioned by fellow Anki users. If you enjoy my work and would like to hire my services to work on an add-on or new feature, please feel free to reach out to me at:  ![Email icon](https://glutanimate.com/logos/email.svg) <em>ankiglutanimate [αt] gmail . com</em>

**MORE RESOURCES**

Want to stay up-to-date with my latest add-on releases and updates? Feel free to follow me on Twitter: [![Twitter bird](https://glutanimate.com/logos/twitter.svg)@Glutanimate](https://twitter.com/glutanimate)

New to Anki? Make sure to check out my YouTube channel where I post weekly tutorials on Anki add-ons and related topics: [![YouTube playbutton](https://glutanimate.com/logos/youtube.svg) / Glutanimate](https://www.youtube.com/c/glutanimate)

============================================

**SUPPORT THIS ADD-ON**

Writing, supporting, and maintaining Anki add-ons like these takes a lot of time and effort. If *Image Occlusion Enhanced* has been a valuable asset in your studies, please consider using one of the buttons below to support my efforts by buying me a **coffee**, **sandwich**, **meal**, or anything else you'd like:

![](https://glutanimate.com/logos/paypal.svg)        [![](https://glutanimate.com/logos/contrib_btnsw_coffee.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=4FT9NG3NJMY4U&on0=Project&os0=image-occlusion "Buy me a coffee ☺")    [![](https://glutanimate.com/logos/contrib_btnsw_sandwich.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=YKSP7QF45Y7SJ&on0=Project&os0=image-occlusion "Buy me a burger 😊")    [![](https://glutanimate.com/logos/contrib_btnsw_meal.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=MVDM6JAL2R5JA&on0=Project&os0=image-occlusion "Buy me a meal 😄")    [![](https://glutanimate.com/logos/contrib_btnsw_custom.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=EYNV4ECSKBGE4&on0=Project&os0=image-occlusion "Contribute a custom amount ☺")

Each and every contribution is greatly appreciated and will help me maintain and improve *Image Occlusion Enhanced* as time goes by!
