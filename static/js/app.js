// used in new-event to refocus a form field after clicking alan button
let activeField = null;
function getActiveField() {
  return activeField;
}
function setActiveField(field) {
  activeField = field;
  if (activeField) {
    elem = document.getElementsByName(activeField)[0];
    elem.focus();
  }
}

var alanBtnInstance = alanBtn({
  key: "419c3a607f35190e01b014eb6f9a7ca22e956eca572e1d8b807a3e2338fdd0dc/stage",
onCommand: function (commandData) {
  if (commandData.command === "fillFormField") {
    document.getElementById(`id_${commandData.field}`).value = commandData.value;
  }
  if (commandData.command === "onButtonClick") {
    setActiveField(commandData.activeField);
  }
  if (commandData.command === "nextField") {
    setActiveField(commandData.next);
  }
},
rootEl: document.getElementById("alan-btn"),
});
