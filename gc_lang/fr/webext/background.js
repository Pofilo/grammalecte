// Background 

"use strict";


/*
    Worker (separate thread to avoid freezing Firefox)
*/
let xGCEWorker = new Worker("gce_worker.js");

xGCEWorker.onmessage = function (e) {
    // https://developer.mozilla.org/en-US/docs/Web/API/MessageEvent
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
            break;
        case "error":
            console.log("ERROR");
            console.log(e.data[1]);
            break;
        default:
            console.log("Unknown command: " + e.data[0]);
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
            break;
    }
});
