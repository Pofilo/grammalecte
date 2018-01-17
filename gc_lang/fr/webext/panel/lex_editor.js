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
                oPage.showSection("section_" + xElem.id.slice(7));
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

const oPage = {

    hideAllSections: function () {
        for (let xElem of document.getElementById("editor").childNodes) {
            if (xElem.id) {
                xElem.style.display = "none";
            }
        }
    },

    showSection: function (sName) {
        this.clear();
        this.hideAllSections();
        if (document.getElementById(sName)) {
            document.getElementById(sName).style.display = "block";
        }
    },

    clear: function () {
        try {
            // nom, adjectif, noms propres
            for (let xElem of document.getElementsByName("POS")) {
                xElem.checked = false;
            }
            for (let xElem of document.getElementsByName("POS2")) {
                xElem.checked = false;
            }
            for (let xElem of document.getElementsByName("pluriel")) {
                xElem.checked = false;
            }
            for (let xElem of document.getElementsByName("genre")) {
                xElem.checked = false;
            }
            // verbe
            document.getElementById("v_i").checked = false;
            document.getElementById("v_t").checked = false;
            document.getElementById("v_n").checked = false;
            document.getElementById("v_p").checked = false;
            document.getElementById("v_m").checked = false;
            document.getElementById("v_ae").checked = false;
            document.getElementById("v_aa").checked = false;
            // autre
            document.getElementById("lemma").value = "";
            document.getElementById("tags").value = "";
        }
        catch (e) {
            showError(e);
        }
    }
}



const oFlex = {

    sLemma: "",
    lFlexion: [],

    getLemma: function () {
        this.sLemma = document.getElementById("lemma").value;
    },

    create: function () {

    },

    show: function () {

    },

    addToDictionary: function () {

    }
}
