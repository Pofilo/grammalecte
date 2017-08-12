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
        xWrapper.className = "grammalecte_wrapper";
        xWrapper.id = nWrapper + 1;
        nWrapper += 1;
        xParentElement.insertBefore(xWrapper, xTextArea);
        xWrapper.appendChild(xTextArea); // move textarea in wrapper
        let xToolbar = createWrapperToolbar(xTextArea);
        xWrapper.appendChild(xToolbar);
    }
    catch (e) {
        showError(e);
    }
}

function createWrapperToolbar (xTextArea) {
    try {
        let xToolbar = document.createElement("div");
        xToolbar.style = "display: flex; justify-content: flex-end; margin-top: 5px; padding: 5px 10px;";
        /*let xLogo = document.createElement("img");
        xLogo.src = browser.extension.getURL("img/logo-16.png"); // can’t work, due to content-script policy: https://bugzilla.mozilla.org/show_bug.cgi?id=1267027
        xTitle.appendChild(xLogo);*/

        xToolbar.appendChild(document.createTextNode("Grammalecte"));
        let xConjButton = document.createElement("div");
        xConjButton.textContent = "Conjuguer";
        xConjButton.className = "grammalecte_wrapper_button";
        xConjButton.onclick = function() {
            createConjPanel();
        };
        xToolbar.appendChild(xConjButton);
        let xTFButton = document.createElement("div");
        xTFButton.textContent = "Formater";
        xTFButton.className = "grammalecte_wrapper_button";
        xTFButton.onclick = function() {
            createTFPanel(xTextArea);
        };
        xToolbar.appendChild(xTFButton);
        let xLxgButton = document.createElement("div");
        xLxgButton.textContent = "Analyser";
        xLxgButton.className = "grammalecte_wrapper_button";
        xLxgButton.onclick = function() {
            createLxgPanel(xTextArea);
        };
        xToolbar.appendChild(xLxgButton);
        let xGCButton = document.createElement("div");
        xGCButton.textContent = "Corriger";
        xGCButton.className = "grammalecte_wrapper_button";
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
        xConjPanel = createPanelFrame("grammalecte_conj_panel", "Conjugueur");
        document.body.appendChild(xConjPanel);
    }
}

function createTFPanel (xTextArea) {
    console.log("Formateur de texte");
    if (xTFPanel !== null) {
        xTFPanel.style.display = "block";
    } else {
        // create the panel
        xTFPanel = createPanelFrame("grammalecte_tf_panel", "Formateur de texte");
        document.body.appendChild(xTFPanel);
        document.getElementById("grammalecte_tf_panel_content").appendChild(createTextFormatter(xTextArea));
    }
}

function createLxgPanel (xTextArea) {
    console.log("Lexicographe");
    if (xLxgPanel !== null) {
        xLxgPanel.style.display = "block";
    } else {
        // create the panel
        xLxgPanel = createPanelFrame("grammalecte_lxg_panel", "Lexicographe");
        document.body.appendChild(xLxgPanel);
    }
}

function createGCPanel (oErrors) {
    console.log("Correction grammaticale");
    if (xGCPanel !== null) {
        xGCPanel.style.display = "block";
    } else {
        // create the panel
        xGCPanel = createPanelFrame("grammalecte_gc_panel", "Correcteur");
        document.body.appendChild(xGCPanel);
        document.getElementById("grammalecte_gc_panel_content").appendChild(document.createTextNode(JSON.stringify(oErrors)));
    }
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
