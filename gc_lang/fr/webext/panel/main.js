// Main panel

"use strict";

/*
    Common functions
*/
function showError (e) {
    console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
}

function showPage (sPageName) {
    try {
        // hide them all
        for (let xNodePage of document.getElementsByClassName("page")) {
            xNodePage.style.display = "none";
        }
        // show the selected one
        document.getElementById(sPageName).style.display = "block";
    }
    catch (e) {
        showError(e);
    }
}

function startWaitIcon () {
    document.getElementById("waiticon").hidden = false;
}

function stopWaitIcon () {
    document.getElementById("waiticon").hidden = true;
}


/*
    Events
*/
window.addEventListener(
    "click",
    function (xEvent) {
        let xElem = xEvent.target;
        if (xElem.id) {
            switch (xElem.id) {
                case "text_to_test":
                    browser.runtime.sendMessage({sCommand: "textToTest", dParam: {sText: document.getElementById("text_to_test").value, sCountry: "FR", bDebug: false, bContext: false}, dInfo: {}});
                    break;
                case "fulltests":
                    document.getElementById("tests_result").textContent = "Veuillez patienter…";
                    browser.runtime.sendMessage({sCommand: "fullTests", dParam: {}, dInfo: {}});
                    break;
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
    switch(oMessage.sCommand) {
        case "text_to_test_result":
            showTestResult(oMessage.sResult);
            break;
        case "fulltests_result":
            showTestResult(oMessage.sResult);
            break;
    }
    sendResponse({sCommand: "none", sResult: "done"});
}

browser.runtime.onMessage.addListener(handleMessage);


/*

    DEDICATED FUNCTIONS 

*/


/*
    Test page
*/
function showTestResult (sText) {
    document.getElementById("tests_result").textContent = sText;
}
