
function showError (e) {
  console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
}

function beastNameToURL(beastName) {
  switch (beastName) {
    case "Frog":
      return browser.extension.getURL("beasts/frog.jpg");
    case "Snake":
      return browser.extension.getURL("beasts/snake.jpg");
    case "Turtle":
      return browser.extension.getURL("beasts/turtle.jpg");
  }
}

window.addEventListener(
  "click",
  function (xEvent) {
    let xElem = xEvent.target;
    if (xElem.id) {
      if (xElem.id) {

      }
    } else if (xElem.tagName === "A") {
      openURL(xElem.getAttribute("href"));
    }
  },
  false
);