
svgEditor.addExtension("Image Occlusion (Anki)", function() {
      return {
        name: "Image Occlusion",
        svgicons: "extensions/image-occlusion-icon.xml",
        buttons: [
        /////////////////////////////////////
        // Button for non-overlapping notes
        /////////////////////////////////////
        {
          id: "add_notes_non_overlapping",
          type: "mode",
          title: "Add notes with non overlapping occlusions",
          key: "1",
          events: {
            "click": function() {
              // The action taken when the button is clicked on.
              // For "mode" buttons, any other button will
              // automatically be de-pressed.
              var svg_contents = svgCanvas.svgCanvasToString();
              pyObj.add_notes_non_overlapping(svg_contents);
            }
          }
        },
        /////////////////////////////////////
        // Button for overlapping notes
        /////////////////////////////////////
        {
          id: "add_notes_overlapping",
          type: "mode",
          title: "Add notes with overlapping occlusions",
          key: "2",
          events: {
            "click": function() {
              // The action taken when the button is clicked on.
              // For "mode" buttons, any other button will
              // automatically be de-pressed.
              var svg_contents = svgCanvas.svgCanvasToString();
              pyObj.add_notes_overlapping(svg_contents);
            }
          }
        },
        /////////////////////////////////////
        // Button for zoom to canvas
        /////////////////////////////////////
        {
          id: "set_zoom_canvas",
          type: "mode",
          title: "Fit image to canvas",
          key: "C",
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
