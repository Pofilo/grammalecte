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

let oConjPanel = null;
let oTFPanel = null;
let oLxgPanel = null;
let oGCPanel = null;


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
        let xToolbar = createNode("div", {className: "grammalecte_wrapper_toolbar"});
        let xConjButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Conjuguer"});
        xConjButton.onclick = function() { createConjPanel(); };
        let xTFButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Formater"});
        xTFButton.onclick = function() { createTFPanel(xTextArea); };
        let xLxgButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Analyser"});
        xLxgButton.onclick = function() {
            createLxgPanel();
            xPort.postMessage({sCommand: "getListOfTokens", dParam: {sText: xTextArea.value}, dInfo: {sTextAreaId: xTextArea.id}});
        };
        let xGCButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Corriger"});
        xGCButton.onclick = function() {
            createGCPanel();
            xPort.postMessage({sCommand: "parseAndSpellcheck", dParam: {sText: xTextArea.value, sCountry: "FR", bDebug: false, bContext: false}, dInfo: {sTextAreaId: xTextArea.id}});
        };
        // Create
        //xToolbar.appendChild(createNode("img", {scr: browser.extension.getURL("img/logo-16.png")}));
        // can’t work, due to content-script policy: https://bugzilla.mozilla.org/show_bug.cgi?id=1267027
        xToolbar.appendChild(createLogo());
        xToolbar.appendChild(document.createTextNode("Grammalecte"));
        xToolbar.appendChild(xConjButton);
        xToolbar.appendChild(xTFButton);
        xToolbar.appendChild(xLxgButton);
        xToolbar.appendChild(xGCButton);
        return xToolbar;
    }
    catch (e) {
        showError(e);
    }
}

function createConjPanel () {
    console.log("Conjugueur");
    if (oConjPanel !== null) {
        oConjPanel.show();
    } else {
        // create the panel
        oConjPanel = new GrammalectePanel("grammalecte_conj_panel", "Conjugueur", 600, 600);
        oConjPanel.insertIntoPage();
    }
}

function createTFPanel (xTextArea) {
    console.log("Formateur de texte");
    if (oTFPanel !== null) {
        oTFPanel.show();
    } else {
        // create the panel
        oTFPanel = new GrammalectePanel("grammalecte_tf_panel", "Formateur de texte", 800, 600, false);
        oTFPanel.logInnerHTML();
        oTFPanel.setContentNode(createTextFormatter(xTextArea));
        oTFPanel.insertIntoPage();
    }
}

function createLxgPanel () {
    console.log("Lexicographe");
    if (oLxgPanel !== null) {
        oLxgPanelContent.clear();
        oLxgPanel.show();
    } else {
        // create the panel
        oLxgPanel = new GrammalectePanel("grammalecte_lxg_panel", "Lexicographe", 500, 700);
        oLxgPanel.setContentNode(oLxgPanelContent.getNode());
        oLxgPanel.insertIntoPage();
    }
}

function createGCPanel () {
    console.log("Correction grammaticale");
    if (oGCPanel !== null) {
        oGCPanelContent.clear();
        oGCPanel.show();
    } else {
        // create the panel
        oGCPanel = new GrammalectePanel("grammalecte_gc_panel", "Correcteur", 500, 700);
        oGCPanel.setContentNode(oGCPanelContent.getNode());
        oGCPanel.insertIntoPage();
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
            oGCPanelContent.addParagraphResult(result);
            break;
        case "getListOfTokens":
            console.log(result);
            oLxgPanelContent.addListOfTokens(result);
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
