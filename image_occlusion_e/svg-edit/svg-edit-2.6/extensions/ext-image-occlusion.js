
svgEditor.addExtension("Image Occlusion (Anki)", function() {
      return {
        name: "Image Occlusion",
  			svgicons: "extensions/image-occlusion-icon.xml",
  			buttons: [
        /////////////////////////////////////
        // Button for zoom to canvas
        /////////////////////////////////////
        {
          id: "set_zoom_canvas",
          type: "mode",
          title: "Fit image to canvas",
          key: "F",
          events: {
            "click": function() {
              svgCanvas.zoomChanged('', 'canvas');
            }
          }
        }
      ],
      // set zoom to "fit to canvas" after loading extension
      callback: function() {
        svgCanvas.zoomChanged('', 'canvas');
      }
		};
});
