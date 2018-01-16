// JavaScript

"use strict";


function showError (e) {
    console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
}


function onSelectionClick (xEvent) {
    try {
        let xElem = xEvent.target;
        if (xElem.id) {
            if (xElem.id.startsWith("select_")) {
                showSection("section_" + xElem.id.slice(7));
            } else {
                
            }
        } else {
            
        }
    }
    catch (e) {
        showError(e);
    }
}


document.getElementById("categories").addEventListener("click", onSelectionClick, false);




/*
    ACTIONS
*/

function hideAllSections () {
    for (let xElem of document.getElementById("editor").childNodes) {
        if (xElem.id) {
            xElem.style.display = "none";
        }
    }
}

function showSection (sName) {
    hideAllSections();
    if (document.getElementById(sName)) {
        document.getElementById(sName).style.display = "block";
    }
}
