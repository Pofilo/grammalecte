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
    console.log(xSender);
    switch(oMessage.sCommand) {
        case "show_tokens":
            console.log("show tokens");
            addParagraphOfTokens(oMessage.oResult);
            break;
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


/*
    Lexicographer page
*/

function addSeparator (sText) {
    if (document.getElementById("tokens_list").textContent !== "") {
        let xElem = document.createElement("p");
        xElem.className = "separator";
        xElem.textContent = sText;
        document.getElementById("tokens_list").appendChild(xElem);
    }
}

function addMessage (sClass, sText) {
    let xNode = document.createElement("p");
    xNode.className = sClass;
    xNode.textContent = sText;
    document.getElementById("tokens_list").appendChild(xNode);
}

function addParagraphOfTokens (lElem) {
    try {
        let xNodeDiv = document.createElement("div");
        xNodeDiv.className = "paragraph";
        for (let oToken of lElem) {
            xNodeDiv.appendChild(createTokenNode(oToken));
        }
        document.getElementById("tokens_list").appendChild(xNodeDiv);
    }
    catch (e) {
        showError(e);
    }
}

function createTokenNode (oToken) {
    let xTokenNode = document.createElement("div");
    xTokenNode.className = "token " + oToken.sType;
    let xTokenValue = document.createElement("b");
    xTokenValue.className = oToken.sType;
    xTokenValue.textContent = oToken.sValue;
    xTokenNode.appendChild(xTokenValue);
    let xSep = document.createElement("s");
    xSep.textContent = " : ";
    xTokenNode.appendChild(xSep);
    if (oToken.aLabel.length === 1) {
        xTokenNode.appendChild(document.createTextNode(oToken.aLabel[0]));
    } else {
        let xTokenList = document.createElement("ul");
        for (let sLabel of oToken.aLabel) {
            let xTokenLine = document.createElement("li");
            xTokenLine.textContent = sLabel;
            xTokenList.appendChild(xTokenLine);
        }
        xTokenNode.appendChild(xTokenList);
    }
    return xTokenNode;
}
