// Main panel

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
    Events
*/
window.addEventListener(
    "click",
    function (xEvent) {
        let xElem = xEvent.target;
        if (xElem.id) {
            if (xElem.id === "text_to_test_button") {
                browser.runtime.sendMessage({
                    sCommand: "textToTest",
                    dParam: {sText: document.getElementById("text_to_test").value, sCountry: "FR", bDebug: true, bContext: false},
                    dInfo: {}
                });
            }
            else if (xElem.id === "fulltests_button") {
                document.getElementById("tests_result").textContent = "Veuillez patienter…";
                browser.runtime.sendMessage({
                    sCommand: "fullTests",
                    dParam: {},
                    dInfo: {}
                });
            }
            else if (xElem.id === "default_options_button") {
                browser.runtime.sendMessage({
                   sCommand: "resetOptions",
                   dParam: {},
                   dInfo: {}
                });
            }
            else if (xElem.id.startsWith("option_")) {
                browser.runtime.sendMessage({
                    sCommand: "setOption",
                    dParam: {sOptName: xElem.dataset.option, bValue: xElem.checked},
                    dInfo: {}
                });
            }
            else if (xElem.id.startsWith("link_")) {
                browser.tabs.create({url: xElem.dataset.url});
            }
        } else if (xElem.className.startsWith("select")) {
            showPage(xElem.dataset.page);
        }/* else if (xElem.tagName === "A") {
            openURL(xElem.getAttribute("href"));
        }*/
    },
    false
);


/* 
    Message sender
    and response handling
*/
function handleResponse (oResponse) {
    console.log(`[Panel] received:`);
    console.log(oResponse);
}

function handleError (error) {
    console.log(`[Panel] Error:`);
    console.log(error);
}

function sendMessageAndWaitResponse (oData) {
    let xPromise = browser.runtime.sendMessage(oData);
    xPromise.then(handleResponse, handleError);  
}


/*
    Messages received
*/
function handleMessage (oMessage, xSender, sendResponse) {
    let {sActionDone, result, dInfo, bEnd, bError} = oMessage;
    switch(sActionDone) {
        case "textToTest":
        case "fullTests":
            showTestResult(result);
            break;
        case "resetOptions":
            setGCOptions(result);
            break;
        default:
            console.log("GRAMMALECTE. Unknown command: " + sActionDone);
    }
    //sendResponse({sCommand: "none", result: "done"});
}

browser.runtime.onMessage.addListener(handleMessage);


/*
    Actions
*/

function showPage (sPageName) {
    try {
        // hide them all
        for (let xNodePage of document.getElementsByClassName("page")) {
            xNodePage.style.display = "none";
        }
        // show the selected one
        document.getElementById(sPageName).style.display = "block";
        if (sPageName == "gc_options_page") {
            setGCOptionsFromStorage();
        }
    }
    catch (e) {
        showError(e);
    }
}


function showTestResult (sText) {
    document.getElementById("tests_result").textContent = sText;
}


function setGCOptionsFromStorage () {
    if (bChrome) {
        browser.storage.local.get("gc_options", _setGCOptions);
        return;
    }
    let xPromise = browser.storage.local.get("gc_options");
    xPromise.then(_setGCOptions, showError);
}

function _setGCOptions (dSavedOptions) {
    if (dSavedOptions.hasOwnProperty("gc_options")) {
        setGCOptions(dSavedOptions.gc_options);
    }
}

function setGCOptions (dOptions) {
    console.log(typeof(dOptions));
    console.log(dOptions);
    /*for (let [sOpt, bVal] of dOptions) {
        if (document.getElementById("option_"+sOpt)) {
            document.getElementById("option_"+sOpt).checked = bVal;
        }
    }*/
    // JS bullshit never ends. For some reason, it’s not a Map anymore on Chrome! 
    for (let xOption of document.getElementsByClassName("gc_option")) {
        console.log(xOption.id);
        let sOpt = xOption.id.slice(7);
        if (dOptions.has(sOpt)) {
            xOption.checked = dOptions.get(sOpt);
        }
    }
}
