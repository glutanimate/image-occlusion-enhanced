/*
 * ext-image-occlusion.js
 *
 * Licensed under the GNU AGPLv3
 *
 * Copyright(c) 2012-2015 tmbb
 * Copyright(c) 2016-2017 Glutanimate
 *
 * This file is part of Image Occlusion Enhanced for Anki
 *
 */

svgEditor.addExtension("Image Occlusion (Anki)", function() {
      return {
        name: "Image Occlusion",
  			svgicons: "extensions/image-occlusion-icon.xml",
  			buttons: [{
          id: "set_zoom_canvas",
          type: "mode",
          title: "Fit image to canvas",
          key: "F",
          events: {
            "click": function() {
              svgCanvas.zoomChanged('', 'canvas');
            }
          }
        }],
      // set zoom to "fit to canvas" after loading extension
		};
});
svgEditor.ready(function () {
  pycmd("svgEditDone");
})
