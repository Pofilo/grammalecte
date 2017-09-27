// Background 

"use strict";


function showError (e) {
    console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
}

// Chrome don’t follow the W3C specification:
// https://browserext.github.io/browserext/
let bChrome = false;
if (typeof(browser) !== "object") {
    var browser = chrome;
    bChrome = true;
}


/*
    Worker (separate thread to avoid freezing Firefox)
*/
let xGCEWorker = new Worker("gce_worker.js");

xGCEWorker.onmessage = function (e) {
    // https://developer.mozilla.org/en-US/docs/Web/API/MessageEvent
    try {
        let {sActionDone, result, dInfo} = e.data;
        switch (sActionDone) {
            case "init":
                storeGCOptions(result);
                break;
            case "parse":
            case "parseAndSpellcheck":
            case "parseAndSpellcheck1":
            case "getListOfTokens":
            case "getSpellSuggestions":
                // send result to content script
                if (typeof(dInfo.iReturnPort) === "number") {
                    let xPort = dConnx.get(dInfo.iReturnPort);
                    xPort.postMessage(e.data);
                } else {
                    console.log("[background] don’t know where to send results");
                    console.log(e.data);
                }
                break;
            case "textToTest":
            case "fullTests":
                // send result to panel
                browser.runtime.sendMessage(e.data);
                break;
            case "getOptions":
            case "getDefaultOptions":
            case "resetOptions":
                // send result to panel
                browser.runtime.sendMessage(e.data);
                storeGCOptions(result);
                break;
            case "setOptions":
            case "setOption":
                storeGCOptions(result);
                break;
            default:
                console.log("[background] Unknown command: " + sActionDone);
                console.log(e.data);
        }
    }
    catch (e) {
        showError(e);
    }
};

function initGrammarChecker (dSavedOptions) {
    let dOptions = (dSavedOptions.hasOwnProperty("gc_options")) ? dSavedOptions.gc_options : null;
    xGCEWorker.postMessage({
        sCommand: "init",
        dParam: {sExtensionPath: browser.extension.getURL(""), dOptions: dOptions, sContext: "Firefox"},
        dInfo: {}
    });
}

function init () {
    if (bChrome) {
        browser.storage.local.get("gc_options", initGrammarChecker);
        return;
    }
    let xPromise = browser.storage.local.get("gc_options");
    xPromise.then(
        initGrammarChecker,
        function (e) {
            showError(e);
            xGCEWorker.postMessage({
                sCommand: "init",
                dParam: {sExtensionPath: browser.extension.getURL("."), dOptions: null, sContext: "Firefox"},
                dInfo: {}
            });
        }
    );
}

init();


/*
    Ports from content-scripts
*/

let dConnx = new Map();


/*
    Messages from the extension (not the Worker)
*/
function handleMessage (oRequest, xSender, sendResponse) {
    //console.log(xSender);
    let {sCommand, dParam, dInfo} = oRequest;
    switch (sCommand) {
        case "getOptions":
        case "getDefaultOptions":
        case "setOptions":
        case "setOption":
        case "resetOptions":
        case "textToTest":
        case "fullTests":
            xGCEWorker.postMessage(oRequest);
            break;
        case "openURL":
            browser.tabs.create({url: dParam.sURL});
            break;
        default:
            console.log("[background] Unknown command: " + sCommand);
            console.log(oRequest);
    }
    //sendResponse({response: "response from background script"});
}

browser.runtime.onMessage.addListener(handleMessage);


function handleConnexion (xPort) {
    let iPortId = xPort.sender.tab.id; // identifier for the port: each port can be found at dConnx[iPortId]
    dConnx.set(iPortId, xPort);
    xPort.onMessage.addListener(function (oRequest) {
        let {sCommand, dParam, dInfo} = oRequest;
        switch (sCommand) {
            case "parse":
            case "parseAndSpellcheck":
            case "parseAndSpellcheck1":
            case "getListOfTokens":
            case "getSpellSuggestions":
                oRequest.dInfo.iReturnPort = iPortId; // we pass the id of the return port to receive answer
                xGCEWorker.postMessage(oRequest);
                break;
            case "openURL":
                browser.tabs.create({url: dParam.sURL});
                break;
            case "openConjugueurTab":
                openConjugueurTab();
                break;
            case "openConjugueurWindow":
                openConjugueurWindow();
                break;
            default:
                console.log("[background] Unknown command: " + sCommand);
                console.log(oRequest);
        }
    });
    //xPort.postMessage({sActionDone: "newId", result: iPortId});
}

browser.runtime.onConnect.addListener(handleConnexion);


/*
    Context Menu
*/
browser.contextMenus.create({
    id: "getListOfTokens",
    title: "Analyser",
    contexts: ["selection"]
});

browser.contextMenus.create({
    id: "parseAndSpellcheck",
    title: "Corriger",
    contexts: ["selection"]
});

browser.contextMenus.create({
    id: "separator1",
    type: "separator",
    contexts: ["selection"]
});

browser.contextMenus.create({
    id: "conjugueur_window",
    title: "Conjugueur [fenêtre]",
    contexts: ["all"]
});

browser.contextMenus.create({
    id: "conjugueur_tab",
    title: "Conjugueur [onglet]",
    contexts: ["all"]
});

browser.contextMenus.create({
    id: "separator2",
    type: "separator",
    contexts: ["editable"]
});

browser.contextMenus.create({
    id: "rescanPage",
    title: "Rechercher à nouveau les zones de texte",
    contexts: ["editable"]
});

browser.contextMenus.onClicked.addListener(function (xInfo, xTab) {
    // xInfo = https://developer.mozilla.org/en-US/Add-ons/WebExtensions/API/contextMenus/OnClickData
    // xTab = https://developer.mozilla.org/en-US/Add-ons/WebExtensions/API/tabs/Tab
    // confusing: no way to get the node where we click?!
    switch (xInfo.menuItemId) {
        case "parseAndSpellcheck":
            parseAndSpellcheckSelectedText(xTab.id, xInfo.selectionText);
            break;
        case "getListOfTokens": 
            getListOfTokensFromSelectedText(xTab.id, xInfo.selectionText);
            break;
        case "conjugueur_window":
            openConjugueurWindow();
            break;
        case "conjugueur_tab":
            openConjugueurTab();
            break;
        case "rescanPage":
            let xPort = dConnx.get(xTab.id);
            xPort.postMessage({sActionDone: "rescanPage"});
            break;
        default:
            console.log("[Background] Unknown menu id: " + xInfo.menuItemId);
            console.log(xInfo);
            console.log(xTab);
    }    
});


/*
    Keyboard shortcuts
*/
browser.commands.onCommand.addListener(function (sCommand) {
    switch (sCommand) {
        case "conjugueur_tab":
            openConjugueurTab();
            break;
        case "conjugueur_window":
            openConjugueurWindow();
            break;
    }
});


/*
    Actions
*/

function storeGCOptions (dOptions) {
    if (bChrome) {
        // JS crap again. Chrome can’t store Map object.
        let obj = {};
        for (let [k, v] of dOptions) {
            obj[k] = v;
        }
        dOptions = obj;
    }
    browser.storage.local.set({"gc_options": dOptions});
}

function parseAndSpellcheckSelectedText (iTab, sText) {
    // send message to the tab
    let xTabPort = dConnx.get(iTab);
    xTabPort.postMessage({sActionDone: "openGCPanel", result: null, dInfo: null, bEnd: false, bError: false});
    // send command to the worker
    xGCEWorker.postMessage({
        sCommand: "parseAndSpellcheck",
        dParam: {sText: sText, sCountry: "FR", bDebug: false, bContext: false},
        dInfo: {iReturnPort: iTab}
    });
}

function getListOfTokensFromSelectedText (iTab, sText) {
    // send message to the tab
    let xTabPort = dConnx.get(iTab);
    xTabPort.postMessage({sActionDone: "openLxgPanel", result: null, dInfo: null, bEnd: false, bError: false});
    // send command to the worker
    xGCEWorker.postMessage({
        sCommand: "getListOfTokens",
        dParam: {sText: sText},
        dInfo: {iReturnPort: iTab}
    });
}

function openConjugueurTab () {
    let xConjTab = browser.tabs.create({
        url: browser.extension.getURL("panel/conjugueur.html")
    });
    xConjTab.then(onCreated, onError);
}

function openConjugueurWindow () {
    let xConjWindow = browser.windows.create({
        url: browser.extension.getURL("panel/conjugueur.html"),
        type: "detached_panel",
        width: 710,
        height: 980
    });
    xConjWindow.then(onCreated, onError);
}


function onCreated (xWindowInfo) {
    //console.log(`Created window: ${xWindowInfo.id}`);
}

function onError (error) {
    console.log(`Error: ${error}`);
}
