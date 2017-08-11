// Modify page

/*
    JS sucks (again and again and again and again…)
    Not possible to load content from within the extension:
    https://bugzilla.mozilla.org/show_bug.cgi?id=1267027
    No SharedWorker, no images allowed for now…
*/

"use strict";

console.log("[Content script] Start");


let nTadId = null;
let nWrapper = 0;

let xConjPanel = null;
let xTFPanel = null;
let xLxgPanel = null;
let xGCPanel = null;


function showError (e) {
    console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
}

function wrapTextareas () {
    let lNode = document.getElementsByTagName("textarea");
    for (let xNode of lNode) {
        createWrapper(xNode);
    }
}

function createWrapper (xTextArea) {
    try {
        let xParentElement = xTextArea.parentElement;
        let xWrapper = document.createElement("div");
        xWrapper.style = "padding: 5px; color: hsl(210, 10%, 90%); background-color: hsl(210, 50%, 50%); border-radius: 3px;";
        xWrapper.id = nWrapper + 1;
        nWrapper += 1;
        xParentElement.insertBefore(xWrapper, xTextArea);
        xWrapper.appendChild(xTextArea); // move textarea in wrapper
        let xToolbar = createWrapperToolbar(xTextArea);
        xWrapper.appendChild(xToolbar);
        loadImage("GrammalecteTitle", "img/logo-16.png");
    }
    catch (e) {
        showError(e);
    }
}

let sButtonStyle = "display: inline-block; padding: 0 5px; margin-left: 5px; background-color: hsl(210, 50%, 60%); border-radius: 2px; cursor: pointer;";

function createWrapperToolbar (xTextArea) {
    try {
        let xToolbar = document.createElement("div");
        xToolbar.style = "display: flex; justify-content: flex-end; margin-top: 5px; padding: 5px 10px;";
        /*let xLogo = document.createElement("img");
        xLogo.src = browser.extension.getURL("img/logo-16.png");
        xTitle.appendChild(xLogo);*/

        let xImagePlace = document.createElement("span");
        xImagePlace.className = "GrammalecteTitle";
        xToolbar.appendChild(xImagePlace);

        xToolbar.appendChild(document.createTextNode("Grammalecte"));
        let xConjButton = document.createElement("div");
        xConjButton.textContent = "Conjuguer";
        xConjButton.style = sButtonStyle;
        xConjButton.onclick = function() {
            createConjPanel();
        };
        xToolbar.appendChild(xConjButton);
        let xTFButton = document.createElement("div");
        xTFButton.textContent = "Formater";
        xTFButton.style = sButtonStyle;
        xTFButton.onclick = function() {
            createTFPanel(xTextArea);
        };
        xToolbar.appendChild(xTFButton);
        let xLxgButton = document.createElement("div");
        xLxgButton.textContent = "Analyser";
        xLxgButton.style = sButtonStyle;
        xLxgButton.onclick = function() {
            console.log("Analyser");
        };
        xToolbar.appendChild(xLxgButton);
        let xGCButton = document.createElement("div");
        xGCButton.textContent = "Corriger";
        xGCButton.style = sButtonStyle;
        xGCButton.onclick = function() {
            xPort.postMessage({sCommand: "parseAndSpellcheck", dParam: {sText: xTextArea.value, sCountry: "FR", bDebug: false, bContext: false}, dInfo: {sTextAreaId: xTextArea.id}});
        };
        xToolbar.appendChild(xGCButton);
        return xToolbar;
    }
    catch (e) {
        showError(e);
    }
}

function createConjPanel () {
    console.log("Conjugueur");
    if (xConjPanel !== null) {
        xConjPanel.style.display = "block";
    } else {
        // create the panel
        xConjPanel = document.createElement("div");
        xConjPanel.style = "position: fixed; left: 50%; top: 50%; z-index: 100; height: 400px; margin-top: -200px; width: 600px; margin-left: -300px; border-radius: 10px;"
                         + " color: hsl(210, 10%, 4%); background-color: hsl(210, 20%, 90%); border: 10px solid hsla(210, 20%, 70%, .5);";
        xConjPanel.textContent = "Conjugueur";
        xConjPanel.setAttribute("draggable", true);
        xConjPanel.appendChild(createCloseButton(xConjPanel));
        document.body.appendChild(xConjPanel);
    }
}

function createTFPanel (xTextArea) {
    console.log("Formateur de texte");
}

function createLxgPanel (xTextArea) {
    console.log("Analyse");
}

function createGCPanel (oErrors) {
    console.log("Correction grammaticale");
    if (xGCPanel !== null) {
        xGCPanel.style.display = "block";
    } else {
        // create the panel
        xGCPanel = document.createElement("div");
        xGCPanel.style = "position: fixed; left: 50%; top: 50%; z-index: 100; height: 400px; margin-top: -200px; width: 600px; margin-left: -300px; border-radius: 10px;"
                         + " color: hsl(210, 10%, 4%); background-color: hsl(210, 20%, 90%); border: 10px solid hsla(210, 20%, 70%, .5);";
        xGCPanel.textContent = JSON.stringify(oErrors);
        xGCPanel.setAttribute("draggable", true);
        xGCPanel.appendChild(createCloseButton(xGCPanel));
        document.body.appendChild(xGCPanel);
    }
}

function createCloseButton (xParentNode) {
    let xButton = document.createElement("div");
    xButton.style = "float: right; width: 20px; padding: 5px 10px; color: hsl(210, 0%, 100%); text-align: center;"
                  + "font-size: 20px; font-weight: bold; background-color: hsl(0, 80%, 50%); border-radius: 0 0 0 3px; cursor: pointer;";
    xButton.textContent = "×";
    xButton.onclick = function () {
        xParentNode.style.display = "none";
    }
    return xButton;
}

function loadImage (sContainerClass, sImagePath) {
    let xRequest = new XMLHttpRequest();
    xRequest.open('GET', browser.extension.getURL("")+sImagePath, false);
    xRequest.responseType = "arraybuffer";
    xRequest.send();
    let blobTxt = new Blob([xRequest.response], {type: 'image/png'});
    let img = document.createElement('img');
    img.src = (URL || webkitURL).createObjectURL(blobTxt);
    Array.filter(document.getElementsByClassName(sContainerClass), function (oElem) {
        oElem.appendChild(img);
    });
}


/*
    Simple message
*/
function handleMessage (oMessage, xSender, sendResponse) {
    console.log("[Content script] received:");
    console.log(oMessage);
    //change(request.myparam);
    //browser.runtime.onMessage.removeListener(handleMessage);
    sendResponse({response: "response from content script"});
}

browser.runtime.onMessage.addListener(handleMessage);


/*
    Connexion
*/
let xPort = browser.runtime.connect({name: "content-script port"});
xPort.onMessage.addListener(function (oMessage) {
    console.log("[Content script] received…");
    let {sActionDone, result, dInfo, bError} = oMessage;
    switch (sActionDone) {
        case "getCurrentTabId":
            console.log("[Content script] tab id: " + result);
            nTadId = result;
            break;
        case "parseAndSpellcheck":
            console.log(result);
            createGCPanel(result);
            break;
        case "getListOfTokens":
            console.log(result);
            break;
        default:
            console.log("[Content script] Unknown command: " + sActionDone);
    }
});
xPort.postMessage({sCommand: "getCurrentTabId", dParam: {}, dInfo: {}});

/*document.body.addEventListener("click", function () {
    xPort.postMessage({greeting: "they clicked the page!"});
});*/

wrapTextareas();
