// Main panel

"use strict";


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
        // specific modifications
        if (sPageName === "conj_page") {
            document.body.style.width = "600px";
            document.documentElement.style.width = "600px";
            //document.getElementById("movewindow").style.display = "none";
        } else {
            document.body.style.width = "530px";
            document.documentElement.style.width = "530px";
            //document.getElementById("movewindow").style.display = "block";
        }
    }
    catch (e) {
        showError(e);
    }
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
                    browser.runtime.sendMessage({sCommand: "text_to_test", sText: document.getElementById("text_to_test").value});
                    break;
                case "fulltests":
                    document.getElementById("tests_result").textContent = "Veuillez patienter…";
                    browser.runtime.sendMessage({sCommand: "fulltests"});
                    break;
            }
        } else if (xElem.className === "select") {
            showPage(xElem.dataset.page);
        } else if (xElem.tagName === "A") {
            openURL(xElem.getAttribute("href"));
        }
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
    //console.log(xSender);
    switch(oMessage.sCommand) {
        case "text_to_test_result":
            document.getElementById("tests_result").textContent = oMessage.sResult;
            break;
        case "fulltests_result":
            document.getElementById("tests_result").textContent = oMessage.sResult;
            break;
    }
    sendResponse({sCommand: "none", sResult: "done"});
}

browser.runtime.onMessage.addListener(handleMessage);
