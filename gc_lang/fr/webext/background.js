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
                storeGCOptions(result);
                if (bChrome) {
                    e.data.result = helpers.mapToObject(e.data.result);
                }
                browser.runtime.sendMessage(e.data);
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

function initUIOptions (dSavedOptions) {
    if (!dSavedOptions.hasOwnProperty("ui_options")) {
        browser.storage.local.set({"ui_options": {
            textarea: true,
            editablenode: true
        }});
    }
}

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
        browser.storage.local.get("ui_options", initUIOptions);
        return;
    }
    browser.storage.local.get("gc_options").then(initGrammarChecker, showError);
    browser.storage.local.get("ui_options").then(initUIOptions, showError);
}

init();


browser.runtime.onInstalled.addListener(function (oDetails) {
    // launched at installation or update
    // https://developer.mozilla.org/fr/Add-ons/WebExtensions/API/runtime/onInstalled
    if (oDetails.reason == "update"  ||  oDetails.reason == "installed") {
        // todo
        //browser.tabs.create({url: "http://grammalecte.net"});
    }
});



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

// Selected text
browser.contextMenus.create({ id: "rightClickLxgSelectedText",  title: "Lexicographe (sélection)",                  contexts: ["selection"] });
browser.contextMenus.create({ id: "rightClickGCSelectedText",   title: "Correction grammaticale (sélection)",       contexts: ["selection"] });
browser.contextMenus.create({ id: "separator_selection",        type: "separator",                                  contexts: ["selection"] });
// Editable content
browser.contextMenus.create({ id: "rightClickTFEditableNode",   title: "Formateur de texte (zone de texte)",        contexts: ["editable"] });
browser.contextMenus.create({ id: "rightClickLxgEditableNode",  title: "Lexicographe (zone de texte)",              contexts: ["editable"] });
browser.contextMenus.create({ id: "rightClickGCEditableNode",   title: "Correction grammaticale (zone de texte)",   contexts: ["editable"] });
browser.contextMenus.create({ id: "separator_editable",         type: "separator",                                  contexts: ["editable"] });
// Page
browser.contextMenus.create({ id: "rightClickLxgPage",          title: "Lexicographe (page)",                       contexts: ["page"] });
browser.contextMenus.create({ id: "rightClickGCPage",           title: "Correction grammaticale (page)",            contexts: ["page"] });
browser.contextMenus.create({ id: "separator_page",             type: "separator",                                  contexts: ["page"] });
// Conjugueur
browser.contextMenus.create({ id: "conjugueur_window",          title: "Conjugueur [fenêtre]",                      contexts: ["all"] });
browser.contextMenus.create({ id: "conjugueur_tab",             title: "Conjugueur [onglet]",                       contexts: ["all"] });
// Rescan page
browser.contextMenus.create({ id: "separator_rescan",           type: "separator",                                  contexts: ["editable"] });
browser.contextMenus.create({ id: "rescanPage",                 title: "Rechercher à nouveau les zones de texte",   contexts: ["editable"] });


browser.contextMenus.onClicked.addListener(function (xInfo, xTab) {
    // xInfo = https://developer.mozilla.org/en-US/Add-ons/WebExtensions/API/contextMenus/OnClickData
    // xTab = https://developer.mozilla.org/en-US/Add-ons/WebExtensions/API/tabs/Tab
    // confusing: no way to get the node where we click?!
    switch (xInfo.menuItemId) {
        // editable node
        // page
        case "rightClickTFEditableNode":
        case "rightClickLxgEditableNode":
        case "rightClickGCEditableNode":
        case "rightClickLxgPage":
        case "rightClickGCPage":
            sendCommandToTab(xInfo.menuItemId, xTab.id);
            break;
        // selected text
        case "rightClickGCSelectedText":
            sendCommandToTab("rightClickGCSelectedText", xTab.id);
            xGCEWorker.postMessage({
                sCommand: "parseAndSpellcheck",
                dParam: {sText: xInfo.selectionText, sCountry: "FR", bDebug: false, bContext: false},
                dInfo: {iReturnPort: xTab.id}
            });
            break;
        case "rightClickLxgSelectedText":
            sendCommandToTab("rightClickLxgSelectedText", xTab.id);
            xGCEWorker.postMessage({
                sCommand: "getListOfTokens",
                dParam: {sText: xInfo.selectionText},
                dInfo: {iReturnPort: xTab.id}
            });
            break;
        // conjugueur
        case "conjugueur_window":
            openConjugueurWindow();
            break;
        case "conjugueur_tab":
            openConjugueurTab();
            break;
        // rescan page
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
        dOptions = helpers.mapToObject(dOptions);
    }
    browser.storage.local.set({"gc_options": dOptions});
}

function sendCommandToTab (sCommand, iTab) {
    let xTabPort = dConnx.get(iTab);
    xTabPort.postMessage({sActionDone: sCommand, result: null, dInfo: null, bEnd: false, bError: false});
}

function openConjugueurTab () {
    if (bChrome) {
        browser.tabs.create({
            url: browser.extension.getURL("panel/conjugueur.html")
        });
        return;
    }
    let xConjTab = browser.tabs.create({
        url: browser.extension.getURL("panel/conjugueur.html")
    });
    xConjTab.then(onCreated, onError);
}

function openConjugueurWindow () {
    if (bChrome) {
        browser.windows.create({
            url: browser.extension.getURL("panel/conjugueur.html"),
            type: "popup",
            width: 710,
            height: 980
        });
        return;
    }
    let xConjWindow = browser.windows.create({
        url: browser.extension.getURL("panel/conjugueur.html"),
        type: "popup",
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
