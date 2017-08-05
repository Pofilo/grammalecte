// Background 

"use strict";

let xGCEWorker = new Worker("gce_worker.js");

xGCEWorker.onmessage = function (e) {
    switch (e.data[0]) {
        case "grammar_errors":
            console.log("GRAMMAR ERRORS");
            console.log(e.data[1].aGrammErr);
            break;
        case "spelling_and_grammar_errors":
            console.log("SPELLING AND GRAMMAR ERRORS");
            console.log(e.data[1].aSpellErr);
            console.log(e.data[1].aGrammErr);
            break;
        case "tests_results":
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

xGCEWorker.postMessage(["parse", {sText: "J’en aie mare...", sCountry: "FR", bDebug: false, bContext: false}]);

xGCEWorker.postMessage(["parseAndSpellcheck", {sText: "C’est terribles, ils va tout perdrre.", sCountry: "FR", bDebug: false, bContext: false}]);

xGCEWorker.postMessage(["getListOfTokens", {sText: "J’en ai assez de ces âneries ! Merci bien. Ça suffira."}]);

xGCEWorker.postMessage(["fullTests"]);


/*
    Messages from the extension (not the Worker)
*/
function handleMessage (oRequest, xSender, sendResponse) {
  console.log(`[background] received: ${oRequest.content}`);
  sendResponse({response: "response from background script"});
}

browser.runtime.onMessage.addListener(handleMessage);
