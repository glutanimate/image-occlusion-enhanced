
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
              svgCanvas.setConfig(svgEditor.curConfig);
              $('#toggle_snap').toggleClass('push_button_pressed tool_button');
              svgEditor.updateCanvas();
          }
        }
      }
    ]};
});
