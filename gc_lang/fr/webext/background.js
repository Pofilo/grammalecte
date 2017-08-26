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
                console.log("INIT DONE");
                break;
            case "parse":
            case "parseAndSpellcheck":
            case "parseAndSpellcheck1":
            case "getListOfTokens":
                console.log("Action done: " + sActionDone);
                if (typeof(dInfo.iReturnPort) === "number") {
                    let xPort = dConnx.get(dInfo.iReturnPort);
                    xPort.postMessage(e.data);
                } else {
                    console.log("[background] don’t know where to send results");
                    console.log(e.data);
                }
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
    Ports from content-scripts
*/

let dConnx = new Map();


/*
    Messages from the extension (not the Worker)
*/
function handleMessage (oRequest, xSender, sendResponse) {
    //console.log(xSender);
    console.log("[background] received:");
    console.log(oRequest);
    switch (oRequest.sCommand) {
        case "parse":
        case "parseAndSpellcheck":
        case "parseAndSpellcheck1":
        case "getListOfTokens":
        case "textToTest":
        case "getOptions":
        case "getDefaultOptions":
        case "setOptions":
        case "setOption":
        case "fullTests":
            xGCEWorker.postMessage(oRequest);
            break;
        default:
            console.log("[background] Unknown command: " + oRequest.sCommand);
    }
    //sendResponse({response: "response from background script"});
}

browser.runtime.onMessage.addListener(handleMessage);


function handleConnexion (p) {
    var xPort = p;
    let iPortId = xPort.sender.tab.id; // identifier for the port: each port can be found at dConnx[iPortId]
    console.log("tab_id: " + iPortId);
    dConnx.set(iPortId, xPort);
    xPort.onMessage.addListener(function (oRequest) {
        console.log("[background] message via connexion:");
        console.log(oRequest);
        switch (oRequest.sCommand) {
            case "parse":
            case "parseAndSpellcheck":
            case "parseAndSpellcheck1":
            case "getListOfTokens":
                oRequest.dInfo.iReturnPort = iPortId; // we pass the id of the return port to receive answer
                console.log(oRequest);
                xGCEWorker.postMessage(oRequest);
                break;
            default:
                console.log("[background] Unknown command: " + oRequest.sCommand);
                console.log(oRequest);
        }
    });
    xPort.postMessage({sActionDone: "newId", result: iPortId});
}

browser.runtime.onConnect.addListener(handleConnexion);


/*
    Context Menu
*/
browser.contextMenus.create({
    id: "parseAndSpellcheck",
    title: "Correction grammaticale",
    contexts: ["selection"]
});

browser.contextMenus.create({
    id: "getListOfTokens",
    title: "Lexicographe",
    contexts: ["selection"]
});

browser.contextMenus.create({
    id: "whatever",
    type: "separator",
    contexts: ["selection"]
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


browser.contextMenus.onClicked.addListener(function (xInfo, xTab) {
    // xInfo = https://developer.mozilla.org/en-US/Add-ons/WebExtensions/API/contextMenus/OnClickData
    // xTab = https://developer.mozilla.org/en-US/Add-ons/WebExtensions/API/tabs/Tab
    console.log(xInfo);
    console.log(xTab);
    console.log("Item " + xInfo.menuItemId + " clicked in tab " + xTab.id);
    console.log("editable: " + xInfo.editable + " · selected: " + xInfo.selectionText);
    // confusing: no way to get the node where we click?!
    switch (xInfo.menuItemId) {
        case "parseAndSpellcheck": {
            let xPort = dConnx.get(xTab.id);
            xPort.postMessage({sActionDone: "openGCPanel", result: null, dInfo: null, bEnd: false, bError: false});
            xGCEWorker.postMessage({
                sCommand: "parseAndSpellcheck",
                dParam: {sText: xInfo.selectionText, sCountry: "FR", bDebug: false, bContext: false},
                dInfo: {iReturnPort: xTab.id}
            });
            break;
        }
        case "getListOfTokens": {
            let xPort = dConnx.get(xTab.id);
            xPort.postMessage({sActionDone: "openLxgPanel", result: null, dInfo: null, bEnd: false, bError: false});
            xGCEWorker.postMessage({
                sCommand: "getListOfTokens",
                dParam: {sText: xInfo.selectionText},
                dInfo: {iReturnPort: xTab.id}
            });
            break;
        }
        case "conjugueur_panel":
            let xConjWindow = browser.windows.create({
                url: browser.extension.getURL("panel/conjugueur.html"),
                type: "detached_panel",
                width: 710,
                height: 980
            });
            xConjWindow.then(onCreated, onError);
            break;
        case "conjugueur_tab":
            let xConjTab = browser.tabs.create({
                url: browser.extension.getURL("panel/conjugueur.html")
            });
            xConjTab.then(onCreated, onError);
            break;
    }    
});



/*
    TESTS ONLY
*/
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
