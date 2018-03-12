/*
 * ext-snapping.js
 *
 * Licensed under the GNU AGPLv3
 *
 * Copyright(c) 2017 Glutanimate
 *
 * This file is part of Image Occlusion Enhanced for Anki
 *
 */

svgEditor.addExtension("toggle_snap", function() {
    snapOn = svgEditor.curConfig.gridSnapping || false
    $(document).bind('keydown', "shift+s", function(e) {
        $('#toggle_snap').click();
    });
    return {
      name: "toggle_snap",
      svgicons: svgEditor.curConfig.extPath + 'snap-icon.xml',
      buttons: [{
        id: 'toggle_snap',
        type: 'context',
        panel: 'editor_panel',
        title: 'Toggle Grid Snapping',
        key: 'F',
        events: {
          "click": function() {
              svgEditor.curConfig.gridSnapping = snapOn = !snapOn;
              if (snapOn){
                var res = svgCanvas.getResolution()
                gridStep = Math.max(5, Math.round(res.w / 100))
                svgEditor.curConfig.snappingStep = gridStep
              };
              svgCanvas.setConfig(svgEditor.curConfig);
              $('#toggle_snap').toggleClass('push_button_pressed tool_button');
              svgEditor.updateCanvas();
          }
        }
      }
    ]};
});
