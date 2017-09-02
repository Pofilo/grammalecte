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
        let {sActionDone, result, dInfo} = e.data;
        switch (sActionDone) {
            case "init":
                browser.storage.local.set({"gc_options": result});
                break;
            case "parse":
            case "parseAndSpellcheck":
            case "parseAndSpellcheck1":
            case "getListOfTokens":
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
                browser.storage.local.set({"gc_options": result});
                break;
            case "setOptions":
            case "setOption":
                browser.storage.local.set({"gc_options": result});
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


function init () {
    let xPromise = browser.storage.local.get("gc_options");
    xPromise.then(
        function (dSavedOptions) {
            let dOptions = (dSavedOptions.hasOwnProperty("gc_options")) ? dSavedOptions.gc_options : null;
            xGCEWorker.postMessage({
                sCommand: "init",
                dParam: {sExtensionPath: browser.extension.getURL("."), dOptions: dOptions, sContext: "Firefox"},
                dInfo: {}
            });
        },
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
    id: "whatever",
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
