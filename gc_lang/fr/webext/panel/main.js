// Main panel

"use strict";


function showError (e) {
    console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
}


/*
    Events
*/
window.addEventListener(
    "click",
    function (xEvent) {
        let xElem = xEvent.target;
        if (xElem.id) {
            if (xElem.id === "text_to_test") {
                browser.runtime.sendMessage({
                    sCommand: "textToTest",
                    dParam: {sText: document.getElementById("text_to_test").value, sCountry: "FR", bDebug: false, bContext: false},
                    dInfo: {}
                });
            }
            else if (xElem.id === "fulltests") {
                document.getElementById("tests_result").textContent = "Veuillez patienter…";
                browser.runtime.sendMessage({
                    sCommand: "fullTests",
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
        case "getOptions":
        case "getDefaultOptions":
            break;
        default:
            console.log("GRAMMALECTE. Unknown command: " + oMessage.sCommand);
    }
    sendResponse({sCommand: "none", result: "done"});
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
            setGCOptions();
        }
    }
    catch (e) {
        showError(e);
    }
}


function showTestResult (sText) {
    document.getElementById("tests_result").textContent = sText;
}

function setGCOptions () {
    let xPromise = browser.storage.local.get("gc_options");
    xPromise.then(
        function (dSavedOptions) {
            //console.log(dSavedOptions);
            if (dSavedOptions.hasOwnProperty("gc_options")) {
                for (let [sOpt, bVal] of dSavedOptions.gc_options) {
                    if (document.getElementById("option_"+sOpt)) {
                        document.getElementById("option_"+sOpt).checked = bVal;
                    }
                }
            }
        },
        function (e) {
            showError(e);
        }
    );
}
