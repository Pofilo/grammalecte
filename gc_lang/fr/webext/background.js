// Background

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global GrammalectePanel, oGrammalecte, helpers, showError, Worker, chrome, console */

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
        let {sActionDone, result, dInfo, bEnd, bError} = e.data;
        if (bError) {
            console.log(result);
            console.log(dInfo);
            return;
        }
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
                browser.runtime.sendMessage(e.data);
                break;
            case "setOptions":
            case "setOption":
                storeGCOptions(result);
                break;
            case "setDictionary":
            case "setDictionaryOnOff":
                //console.log("[background] " + sActionDone + ": " + result);
                break;
            default:
                console.log("[background] Unknown command: " + sActionDone);
                console.log(e.data);
        }
    }
    catch (error) {
        showError(error);
        console.log(e.data);
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
    try {
        let dOptions = (dSavedOptions.hasOwnProperty("gc_options")) ? dSavedOptions.gc_options : null;
        if (dOptions !== null && Object.getOwnPropertyNames(dOptions).length == 0) {
            console.log("# Error: the saved options was an empty object.");
            dOptions = null;
        }
        xGCEWorker.postMessage({
            sCommand: "init",
            dParam: {sExtensionPath: browser.extension.getURL(""), dOptions: dOptions, sContext: "Firefox"},
            dInfo: {}
        });
    }
    catch (e) {
        console.log("initGrammarChecker failed");
        showError(e);
    }
}

function setDictionaryOnOff (sDictionary, bActivate) {
    xGCEWorker.postMessage({
        sCommand: "setDictionaryOnOff",
        dParam: { sDictionary: sDictionary, bActivate: bActivate },
        dInfo: {}
    });
}

function initSCOptions (oData) {
    if (!oData.hasOwnProperty("sc_options")) {
        browser.storage.local.set({"sc_options": {
            extended: true,
            community: true,
            personal: true
        }});
        setDictionaryOnOff("community", true);
        setDictionaryOnOff("personal", true);
    } else {
        setDictionaryOnOff("community", oData.sc_options["community"]);
        setDictionaryOnOff("personal", oData.sc_options["personal"]);
    }
}

function setDictionary (sDictionary, oDictionary) {
    xGCEWorker.postMessage({
        sCommand: "setDictionary",
        dParam: { sDictionary: sDictionary, oDict: oDictionary },
        dInfo: {}
    });
}

function setSpellingDictionaries (oData) {
    if (oData.hasOwnProperty("oPersonalDictionary")) {
        // deprecated
        console.log("personal dictionary migration");
        browser.storage.local.set({ "dictionaries": { "__personal__": oData["oPersonalDictionary"] } });
        setDictionary("personal", oData["oPersonalDictionary"]);
        browser.storage.local.remove("oPersonalDictionary");
    }
    if (oData.hasOwnProperty("dictionaries")) {
        if (oData.dictionaries.hasOwnProperty("__personal__")) {
            setDictionary("personal", oData.dictionaries["__personal__"]);
        }
        if (oData.dictionaries.hasOwnProperty("__community__")) {
            setDictionary("personal", oData.dictionaries["__community__"]);
        }
    }
}

function init () {
    if (bChrome) {
        browser.storage.local.get("gc_options", initGrammarChecker);
        browser.storage.local.get("ui_options", initUIOptions);
        browser.storage.local.get("dictionaries", setSpellingDictionaries);
        browser.storage.local.get("oPersonalDictionary", setSpellingDictionaries); // deprecated
        browser.storage.local.get("sc_options", initSCOptions);
        return;
    }
    browser.storage.local.get("gc_options").then(initGrammarChecker, showError);
    browser.storage.local.get("ui_options").then(initUIOptions, showError);
    browser.storage.local.get("dictionaries").then(setSpellingDictionaries, showError);
    browser.storage.local.get("oPersonalDictionary").then(setSpellingDictionaries, showError); // deprecated
    browser.storage.local.get("sc_options").then(initSCOptions, showError);
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
        case "setDictionary":
        case "setDictionaryOnOff":
            xGCEWorker.postMessage(oRequest);
            break;
        case "openURL":
            browser.tabs.create({url: dParam.sURL});
            break;
        case "openConjugueurTab":
            openConjugueurTab();
            break;
        case "openLexiconEditor":
            openLexiconEditor(dParam["dictionary"]);
            break;
        case "openDictionaries":
            openDictionaries();
            break;
        default:
            console.log("[background] Unknown command: " + sCommand);
            console.log(oRequest);
    }
    //sendResponse({response: "response from background script"});
}

browser.runtime.onMessage.addListener(handleMessage);


function handleConnexion (xPort) {
    // Messages from tabs
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
    xPort.postMessage({sActionDone: "init", sUrl: browser.extension.getURL("")});
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
browser.contextMenus.create({ id: "rightClickLxgPage",          title: "Lexicographe (page)",                       contexts: ["all"] }); // on all parts, due to unwanted selection
browser.contextMenus.create({ id: "rightClickGCPage",           title: "Correction grammaticale (page)",            contexts: ["all"] });
browser.contextMenus.create({ id: "separator_page",             type: "separator",                                  contexts: ["all"] });
// Tools
browser.contextMenus.create({ id: "conjugueur_window",          title: "Conjugueur [fenêtre]",                      contexts: ["all"] });
browser.contextMenus.create({ id: "conjugueur_tab",             title: "Conjugueur [onglet]",                       contexts: ["all"] });
browser.contextMenus.create({ id: "dictionaries",               title: "Dictionnaires",                             contexts: ["all"] });
browser.contextMenus.create({ id: "lexicon_editor",             title: "Éditeur lexical",                           contexts: ["all"] });
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
        case "lexicon_editor":
            openLexiconEditor();
            break;
        case "dictionaries":
            openDictionaries();
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
        case "lexicon_editor":
            openLexiconEditor();
            break;
        case "dictionaries":
            openDictionaries();
            break;
    }
});


/*
    Tabs
*/
let nTabLexiconEditor = null;
let nTabDictionaries = null;

browser.tabs.onRemoved.addListener(function (nTabId, xRemoveInfo) {
    if (nTabId === nTabLexiconEditor) {
        nTabLexiconEditor = null;
    }
    else if (nTabId === nTabDictionaries) {
        nTabDictionaries = null;
    }
});


/*
    Actions
*/

function storeGCOptions (dOptions) {
    if (dOptions instanceof Map) {
        dOptions = helpers.mapToObject(dOptions);
    }
    browser.storage.local.set({"gc_options": dOptions});
}

function sendCommandToTab (sCommand, iTab) {
    let xTabPort = dConnx.get(iTab);
    xTabPort.postMessage({sActionDone: sCommand, result: null, dInfo: null, bEnd: false, bError: false});
}

function openLexiconEditor (sName="__personal__") {
    if (nTabLexiconEditor === null) {
        if (bChrome) {
            browser.tabs.create({
                url: browser.extension.getURL("panel/lex_editor.html")
            }, onLexiconEditorOpened);
            return;
        }
        let xLexEditor = browser.tabs.create({
            url: browser.extension.getURL("panel/lex_editor.html")
        });
        xLexEditor.then(onLexiconEditorOpened, onError);
    }
}

function onLexiconEditorOpened (xTab) {
    //console.log(xTab);
    nTabLexiconEditor = xTab.id;
}

function openDictionaries () {
    if (nTabDictionaries === null) {
        if (bChrome) {
            browser.tabs.create({
                url: browser.extension.getURL("panel/dictionaries.html")
            }, onDictionariesOpened);
            return;
        }
        let xLexEditor = browser.tabs.create({
            url: browser.extension.getURL("panel/dictionaries.html")
        });
        xLexEditor.then(onDictionariesOpened, onError);
    }
}

function onDictionariesOpened (xTab) {
    //console.log(xTab);
    nTabDictionaries = xTab.id;
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
    console.log(error);
}
