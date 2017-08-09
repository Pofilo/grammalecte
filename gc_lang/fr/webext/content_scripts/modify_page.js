// Modify page

"use strict";

console.log("Content script [start]");

function showError (e) {
    console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
}

/*
    Worker (separate thread to avoid freezing Firefox)
*/
let xGCEWorker = new SharedWorker("../gce_sharedworker.js");

xGCEWorker.onerror = function(e) {
    console.log('There is an error with your worker!');
    console.log(typeof(e));
    console.log(e);
    for (let sParam in e) {
        console.log(sParam);
        console.log(e.sParam);
    }
}

xGCEWorker.port.onmessage = function (e) {
    // https://developer.mozilla.org/en-US/docs/Web/API/MessageEvent
    try {
        switch (e.data[0]) {
            case "grammar_errors":
                console.log("GRAMMAR ERRORS");
                console.log(e.data[1].aGrammErr);
                //browser.runtime.sendMessage({sCommand: "grammar_errors", aGrammErr: e.data[1].aGrammErr});
                break;
            case "spelling_and_grammar_errors":
                console.log("SPELLING AND GRAMMAR ERRORS");
                console.log(e.data[1].aSpellErr);
                console.log(e.data[1].aGrammErr);
                break;
            case "text_to_test_result":
                console.log("TESTS RESULTS");
                console.log(e.data[1]);
                break;
            case "fulltests_result":
                console.log("TESTS RESULTS");
                console.log(e.data[1]);
                break;
            case "options":
                console.log("OPTIONS");
                console.log(e.data[1]);
                break;
            case "tokens":
                console.log("TOKENS");
                console.log(e.data[1]);
                let xLxgTab = browser.tabs.create({
                    url: browser.extension.getURL("panel/lexicographer.html"),
                });
                xLxgTab.then(onCreated, onError);
                break;
            case "error":
                console.log("ERROR");
                console.log(e.data[1]);
                break;
            default:
                console.log("Unknown command: " + e.data[0]);
        }
    }
    catch (e) {
        showError(e);
    }
};

console.log("Content script [worker]");
console.log(xGCEWorker);


//xGCEWorker.port.start();
//console.log("Content script [port started]");

//xGCEWorker.port.postMessage(["init", {sExtensionPath: browser.extension.getURL("."), sOptions: "", sContext: "Firefox"}]);

console.log("Content script [worker initialzed]");

xGCEWorker.port.postMessage(["parse", {sText: "Vas... J’en aie mare...", sCountry: "FR", bDebug: false, bContext: false}]);
//xGCEWorker.port.postMessage(["parseAndSpellcheck", {sText: oRequest.sText, sCountry: "FR", bDebug: false, bContext: false}]);
//xGCEWorker.port.postMessage(["getListOfTokens", {sText: oRequest.sText}]);
//xGCEWorker.port.postMessage(["textToTest", {sText: oRequest.sText, sCountry: "FR", bDebug: false, bContext: false}]);
//xGCEWorker.port.postMessage(["fullTests"]);



function wrapTextareas() {;
    let lNode = document.getElementsByTagName("textarea");
    for (let xNode of lNode) {
        createGCButton(xNode);
    }
}

function createGCButton (xActiveTextZone) {
    let xParentElement = xActiveTextZone.parentElement;
    let xGCButton = document.createElement("div");
    xGCButton.textContent = "@";
    xGCButton.title = "Grammalecte"
    xGCButton.style = "padding: 5px; color: #FFF; background-color: hsla(210, 50%, 50%, 80%); border-radius: 3px; cursor: pointer";
    xGCButton.onclick = function() {
        console.log(xActiveTextZone.value);
    };
    xParentElement.insertBefore(xGCButton, xActiveTextZone);
}

function removeEverything () {
    while (document.body.firstChild) {
        document.body.firstChild.remove();
    }
}

function change (param) {
    document.getElementById("title").setAttribute("background-color", "#809060");
    console.log("param: " + param);
    document.getElementById("title").setAttribute("background-color", "#FF0000");
}


/*
    Assign do_something() as a listener for messages from the extension.
*/


function handleMessage2 (oRequest, xSender, sendResponse) {
    console.log(`[Content script] received: ${oRequest.content}`);
    change(request.myparam);
    //browser.runtime.onMessage.removeListener(handleMessage);
    sendResponse({response: "response from content script"});
}

browser.runtime.onMessage.addListener(handleMessage2);


wrapTextareas();
