const NoteEditor = require("anki/NoteEditor");

class ImageOcclusion {
  markIdField(index) {
    const idField = NoteEditor.instances[0].fields[index];
    if (!idField) {
      return;
    }
    idField.element.then((element) => {
      {
        element.classList.add("ionote-field-id");
      }
    });
  }
}

globalThis.imageOcclusion = new ImageOcclusion();
