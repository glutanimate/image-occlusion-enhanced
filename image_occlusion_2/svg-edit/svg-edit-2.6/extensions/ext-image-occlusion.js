
svgEditor.addExtension("Image Occlusion (Anki)", function() {
                return {
                        name: "Image Occlusion",
			// For more notes on how to make an icon file, see the source of
			// the hellorworld-icon.xml
			svgicons: "extensions/image-occlusion-icon.xml",
			
			// Multiple buttons can be added in this array
			buttons: [
                                /////////////////////////////////////
                                // Button for non-overlapping notes
                                /////////////////////////////////////
                                {
				id: "add_notes_non_overlapping", 
				
				// This indicates that the button will be added to the "mode"
				// button panel on the left side
				type: "mode", 
				
				// Tooltip text
				title: "Add notes with non overlapping occlusions", 
				
				// Events
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
				
				// This indicates that the button will be added to the "mode"
				// button panel on the left side
				type: "mode", 
				
				// Tooltip text
				title: "Add notes with overlapping occlusions", 
				
				// Events
				events: {
					"click": function() {
						// The action taken when the button is clicked on.
						// For "mode" buttons, any other button will 
						// automatically be de-pressed.
						var svg_contents = svgCanvas.svgCanvasToString();
                                                pyObj.add_notes_overlapping(svg_contents);
					}
				}}
                        ],
		};
});
