
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
    } else if (xElem.className === "select") {
      showPage(xElem.dataset.page);
    } else if (xElem.tagName === "A") {
      openURL(xElem.getAttribute("href"));
    }
  },
  false
);

function showPage (sPageName) {
  try {
    // hide them all
    for (let xNodePage of document.getElementsByClassName("page")) {
      xNodePage.style.display = "None";
    }
    // show the one
    document.getElementById(sPageName).style.display = "block";
    sendMessage("Mon message");
    // specific modifications
    if (sPageName === "conj_page") {
      document.body.style.width = "600px";
      document.documentElement.style.width = "600px";
      document.getElementById("movewindow").style.display = "none";
    } else {
      document.body.style.width = "530px";
      document.documentElement.style.width = "530px";
      document.getElementById("movewindow").style.display = "block";
    }
  }
  catch (e) {
    showError(e);
  }
}

function handleResponse(message) {
  console.log(`background script sent a response: ${message.response}`);
}

function handleError(error) {
  console.log(`Error: ${error}`);
}

function sendMessage (sMessage) {
  let sending = browser.runtime.sendMessage({content: sMessage});
  sending.then(handleResponse, handleError);  
}
