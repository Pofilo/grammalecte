// Background 

"use strict";

function showError (e) {
    console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
}

/*
    Worker (separate thread to avoid freezing Firefox)
*/
let xGCEWorker = new Worker("gce_worker.js");

xGCEWorker.onmessage = function (e) {
    // https://developer.mozilla.org/en-US/docs/Web/API/MessageEvent
    try {
        switch (e.data[0]) {
            case "grammar_errors":
                console.log("GRAMMAR ERRORS");
                console.log(e.data[1].aGrammErr);
                browser.runtime.sendMessage({sCommand: "grammar_errors", aGrammErr: e.data[1].aGrammErr});
                break;
            case "spelling_and_grammar_errors":
                console.log("SPELLING AND GRAMMAR ERRORS");
                console.log(e.data[1].aSpellErr);
                console.log(e.data[1].aGrammErr);
                break;
            case "text_to_test_result":
                browser.runtime.sendMessage({sCommand: "text_to_test_result", sResult: e.data[1]});
                break;
            case "fulltests_result":
                console.log("TESTS RESULTS");
                browser.runtime.sendMessage({sCommand: "fulltests_result", sResult: e.data[1]});
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

xGCEWorker.postMessage(["init", {sExtensionPath: browser.extension.getURL("."), sOptions: "", sContext: "Firefox"}]);


/*
    Messages from the extension (not the Worker)
*/
function handleMessage (oRequest, xSender, sendResponse) {
    //console.log(xSender);
    switch(oRequest.sCommand) {
        case "parse":
            xGCEWorker.postMessage(["parse", {sText: oRequest.sText, sCountry: "FR", bDebug: false, bContext: false}]);
            break;
        case "parse_and_spellcheck":
            xGCEWorker.postMessage(["parseAndSpellcheck", {sText: oRequest.sText, sCountry: "FR", bDebug: false, bContext: false}]);
            break;
        case "get_list_of_tokens":
            xGCEWorker.postMessage(["getListOfTokens", {sText: oRequest.sText}]);
            break;
        case "text_to_test":
            xGCEWorker.postMessage(["textToTest", {sText: oRequest.sText, sCountry: "FR", bDebug: false, bContext: false}]);
            break;
        case "fulltests":
            xGCEWorker.postMessage(["fullTests"]);
            break;
    }
    //sendResponse({response: "response from background script"});
}

browser.runtime.onMessage.addListener(handleMessage);


/*
    Context Menu
*/
browser.contextMenus.create({
    id: "grammar_checking",
    title: "Correction grammaticale",
    contexts: ["selection", "editable", "page"]
});

browser.contextMenus.create({
    id: "lexicographer",
    title: "Lexicographe",
    contexts: ["selection", "editable", "page"]
});

browser.contextMenus.create({
    id: "conjugueur_panel",
    title: "Conjugueur [fenêtre]",
    contexts: ["all"]
});
browser.contextMenus.create({
    id: "conjugueur_tab",
    title: "Conjugueur [onglet]",
    contexts: ["all"]
});

function onCreated(windowInfo) {
  console.log(`Created window: ${windowInfo.id}`);
}

function onError(error) {
  console.log(`Error: ${error}`);
}

let xConjWindow = null;
let xConjTab = null;

browser.contextMenus.onClicked.addListener(function (xInfo, xTab) {
    // xInfo = https://developer.mozilla.org/en-US/Add-ons/WebExtensions/API/contextMenus/OnClickData
    // xTab = https://developer.mozilla.org/en-US/Add-ons/WebExtensions/API/tabs/Tab
    console.log(xInfo);
    console.log(xTab);
    console.log("Item " + xInfo.menuItemId + " clicked in tab " + xTab.id);
    console.log("editable: " + xInfo.editable + " · selected: " + xInfo.selectionText);
    // confusing: no way to get the node where we click?!
    switch (xInfo.menuItemId) {
        case "grammar_checking":
            break;
        case "lexicographer":
            if (xInfo.selectionText) {
                xGCEWorker.postMessage(["getListOfTokens", {sText: xInfo.selectionText}]);
            }
            break;
        case "conjugueur_panel":
            xConjWindow = browser.windows.create({
                url: browser.extension.getURL("panel/conjugueur.html"),
                type: "detached_panel",
                width: 710,
                height: 980
            });
            xConjWindow.then(onCreated, onError);
            break;
        case "conjugueur_tab":
            xConjTab = browser.tabs.create({
                url: browser.extension.getURL("panel/conjugueur.html"),
                pinned: true
            });
            xConjTab.then(onCreated, onError);
            break;
    }    
});


async function newwin () {
    console.log("Async on");
    const getActive = browser.tabs.query({ currentWindow: true, active: true, });
    const xWindowInfo = await browser.windows.getLastFocused();
    // the pop-up will not resize itself as the panel would, so the dimensions can be passed as query params 'w' and 'h'
    const width = 710, height = 980; // the maximum size for panels is somewhere around 700x800. Firefox needs some additional pixels: 14x42 for FF54 on Win 10 with dpi 1.25
    const left = Math.round(xWindowInfo.left + xWindowInfo.width - width - 25);
    const top = Math.round(xWindowInfo.top + 74); // the actual frame height of the main window varies, but 74px should place the pop-up at the bottom if the button
    const xWin = await browser.windows.create({
        type: 'panel', url: browser.extension.getURL("panel/conjugueur.html"), top: top, left: left, width: width, height: height,
    });
    browser.windows.update(xWin.id, { top:top, left:left, }); // firefox currently ignores top and left in .create(), so move it here
    console.log("Async done");
}

//newwin();


/*
    Worker (separate thread to avoid freezing Firefox)
*/
/*
let xGCESharedWorker = new SharedWorker("gce_sharedworker.js");

xGCESharedWorker.port.onmessage = function (e) {
    // https://developer.mozilla.org/en-US/docs/Web/API/MessageEvent
    try {
        switch (e.data[0]) {
            case "grammar_errors":
                console.log("GRAMMAR ERRORS (SHARE)");
                console.log(e.data[1].aGrammErr);
                //browser.runtime.sendMessage({sCommand: "grammar_errors", aGrammErr: e.data[1].aGrammErr});
                break;
            case "spelling_and_grammar_errors":
                console.log("SPELLING AND GRAMMAR ERRORS (SHARE)");
                console.log(e.data[1].aSpellErr);
                console.log(e.data[1].aGrammErr);
                break;
            case "text_to_test_result":
                console.log("TESTS RESULTS (SHARE)");
                console.log(e.data[1]);
                break;
            case "fulltests_result":
                console.log("TESTS RESULTS (SHARE)");
                console.log(e.data[1]);
                break;
            case "options":
                console.log("OPTIONS (SHARE)");
                console.log(e.data[1]);
                break;
            case "tokens":
                console.log("TOKENS (SHARE)");
                console.log(e.data[1]);
                let xLxgTab = browser.tabs.create({
                    url: browser.extension.getURL("panel/lexicographer.html"),
                });
                xLxgTab.then(onCreated, onError);
                break;
            case "error":
                console.log("ERROR (SHARE)");
                console.log(e.data[1]);
                break;
            default:
                console.log("Unknown command (SHARE): " + e.data[0]);
        }
    }
    catch (e) {
        showError(e);
    }
};

console.log("Content script [worker]");
console.log(xGCESharedWorker);


//xGCESharedWorker.port.start();
//console.log("Content script [port started]");

xGCESharedWorker.port.postMessage(["init", {sExtensionPath: browser.extension.getURL("."), sOptions: "", sContext: "Firefox"}]);

console.log("Content script [worker initialzed]");

xGCESharedWorker.port.postMessage(["parse", {sText: "Vas... J’en aie mare...", sCountry: "FR", bDebug: false, bContext: false}]);
//xGCESharedWorker.port.postMessage(["parseAndSpellcheck", {sText: oRequest.sText, sCountry: "FR", bDebug: false, bContext: false}]);
//xGCESharedWorker.port.postMessage(["getListOfTokens", {sText: oRequest.sText}]);
//xGCESharedWorker.port.postMessage(["textToTest", {sText: oRequest.sText, sCountry: "FR", bDebug: false, bContext: false}]);
//xGCESharedWorker.port.postMessage(["fullTests"]);


*/