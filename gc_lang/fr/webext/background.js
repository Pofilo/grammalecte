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
        let {sActionDone, result, dInfo, bError} = e.data;
        switch (sActionDone) {
            case "init":
                console.log("INIT DONE");
                break;
            case "parse":
                console.log("GRAMMAR ERRORS");
                console.log(result);
                break;
            case "parseAndSpellcheck":
                console.log("SPELLING AND GRAMMAR ERRORS");
                console.log(result.aSpellErr);
                console.log(result.aGrammErr);
                break;
            case "textToTest":
                console.log("TEXT TO TEXT RESULTS");
                browser.runtime.sendMessage({sCommand: "text_to_test_result", sResult: result});
                break;
            case "fullTests":
                console.log("FULL TESTS RESULTS");
                browser.runtime.sendMessage({sCommand: "fulltests_result", sResult: result});
                break;
            case "getOptions":
            case "getDefaultOptions":
            case "setOptions":
            case "setOption":
                console.log("OPTIONS");
                console.log(e.data[1]);
                break;
            case "getListOfTokens":
                console.log("TOKENS");
                console.log(e.data[1]);
                let xLxgTab = browser.tabs.create({
                    url: browser.extension.getURL("panel/lexicographer.html"),
                });
                xLxgTab.then(onCreated, onError);
                break;
                break;
            default:
                console.log("Unknown command: " + sActionDone);
                console.log(result);
        }
    }
    catch (e) {
        showError(e);
    }
};


xGCEWorker.postMessage({sCommand: "init", dParam: {sExtensionPath: browser.extension.getURL("."), sOptions: "", sContext: "Firefox"}, dInfo: {}});


/*
    Messages from the extension (not the Worker)
*/
function handleMessage (oRequest, xSender, sendResponse) {
    //console.log(xSender);
    switch(oRequest.sCommand) {
        case "parse":
            xGCEWorker.postMessage({sCommand: "parse", dParam: {sText: oRequest.sText, sCountry: "FR", bDebug: false, bContext: false}, dInfo: {}});
            break;
        case "parse_and_spellcheck":
            xGCEWorker.postMessage({sCommand: "parseAndSpellcheck", dParam: {sText: oRequest.sText, sCountry: "FR", bDebug: false, bContext: false}, dInfo: {}});
            break;
        case "get_list_of_tokens":
            xGCEWorker.postMessage({sCommand: "getListOfTokens", dParam: {sText: oRequest.sText}, dInfo: {}});
            break;
        case "text_to_test":
            xGCEWorker.postMessage({sCommand: "textToTest", dParam: {sText: oRequest.sText, sCountry: "FR", bDebug: false, bContext: false}, dInfo: {}});
            break;
        case "fulltests":
            xGCEWorker.postMessage({sCommand: "fullTests", dParam: {}, dInfo: {}});
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
    // test for popup window-like, which doesn’t close when losing the focus
    console.log("Async on");
    const getActive = browser.tabs.query({ currentWindow: true, active: true, });
    const xWindowInfo = await browser.windows.getLastFocused();
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
