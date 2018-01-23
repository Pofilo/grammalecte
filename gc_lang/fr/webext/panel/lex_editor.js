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
                oFlex.setMainTag(xElem.dataset.tag);
                oFlex.update();
            } else if (xElem.id.startsWith("up_")) {
                oFlex.update();
            }
        }
    }
    catch (e) {
        showError(e);
    }
}

function onWrite (xEvent) {
    if (document.getElementById("word").value.trim() !== "") {
        oPage.showEditor();
    } else {
        oPage.hideEditor();
        oPage.hideActions();
    }
}

function onWrite2 (xEvent) {
    if (document.getElementById("word2").value.trim() !== "") {
        oPage.showWord2();
    } else {
        oPage.hideWord2();
    }
}


document.getElementById("editor").addEventListener("click", onSelectionClick, false);
document.getElementById("word").addEventListener("keyup", onWrite, false);
document.getElementById("word2").addEventListener("keyup", onWrite2, false);
document.getElementById("lemma").addEventListener("keyup", () => { oFlex.update(); }, false);
document.getElementById("tags").addEventListener("keyup", () => { oFlex.update(); } , false);


/*
    ACTIONS
*/

const oPage = {

    showEditor: function () {
        document.getElementById("editor").style.display = "block";
    },

    hideEditor: function () {
        document.getElementById("editor").style.display = "none";
    },

    hideAllSections: function () {
        for (let xElem of document.getElementById("sections").childNodes) {
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
            for (let xElem of document.getElementsByName("pluriel2")) {
                xElem.checked = false;
            }
            for (let xElem of document.getElementsByName("genre2")) {
                xElem.checked = false;
            }
            // verbe
            document.getElementById("up_v_i").checked = false;
            document.getElementById("up_v_t").checked = false;
            document.getElementById("up_v_n").checked = false;
            document.getElementById("up_v_p").checked = false;
            document.getElementById("up_v_m").checked = false;
            document.getElementById("up_v_ae").checked = false;
            document.getElementById("up_v_aa").checked = false;
            // autre
            document.getElementById("lemma").value = "";
            document.getElementById("tags").value = "";
        }
        catch (e) {
            showError(e);
        }
    },

    showWord2: function () {
        document.getElementById("word_section2").style.display = "block";
    },

    hideWord2: function () {
        document.getElementById("word_section2").style.display = "none";
    },

    showActions: function () {
        document.getElementById("actions").style.display = "block";
    },

    hideActions: function () {
        document.getElementById("actions").style.display = "none";
    }
}



const oFlex = {

    cMainTag: "",

    lFlexion: [],

    clear: function () {
        this.lFlexion = [];
        document.getElementById("actions").style.display = "none";
    },

    setMainTag: function (sValue) {
        this.cMainTag = sValue;
    },

    addFlexion: function (sFlexion, sLemma, sTag) {
        this.lFlexion.push( [sFlexion, sLemma, sTag] );
    },

    update: function () {
        try {
            this.clear();
            let sGenderTag = "";
            let sWord = document.getElementById("word").value.trim();
            if (sWord.length > 0) {
                switch (this.cMainTag) {
                    case "N":
                        let sTag = this.getRadioValue("POS") + this.getRadioValue("genre");
                        switch (this.getRadioValue("pluriel")) {
                            case "s":
                                this.addFlexion(sWord, sWord, sTag+":s");
                                this.addFlexion(sWord+"s", sWord, sTag+":p");
                                break;
                            case "x":
                                this.addFlexion(sWord, sWord, sTag+":s");
                                this.addFlexion(sWord+"x", sWord, sTag+":p");
                                break;
                            case "i":
                                this.addFlexion(sWord, sWord, sTag+":i");
                                break;
                        }
                        let sWord2 = document.getElementById("word2").value.trim();
                        if (sWord2.length > 0) {
                            let sTag2 = this.getRadioValue("POS2") + this.getRadioValue("genre2");
                            switch (this.getRadioValue("pluriel2")) {
                                case "s":
                                    this.addFlexion(sWord2, sWord, sTag2+":s");
                                    this.addFlexion(sWord2+"s", sWord, sTag2+":p");
                                    break;
                                case "x":
                                    this.addFlexion(sWord2, sWord, sTag2+":s");
                                    this.addFlexion(sWord2+"x", sWord, sTag2+":p");
                                    break;
                                case "i":
                                    this.addFlexion(sWord2, sWord, sTag2+":i");
                                    break;
                            }
                        }
                        break;
                    case "V":
                        if (!sWord.endsWith("er") && !sWord.endsWith("ir")) {
                            break;
                        }
                        let c_g = (sWord.endsWith("er")) ? "1" : "2";
                        let c_i = (document.getElementById("up_v_i").checked) ? "i" : "_";
                        let c_t = (document.getElementById("up_v_t").checked) ? "t" : "_";
                        let c_n = (document.getElementById("up_v_n").checked) ? "n" : "_";
                        let c_p = (document.getElementById("up_v_p").checked) ? "p" : "_";
                        let c_m = (document.getElementById("up_v_m").checked) ? "m" : "_";
                        let c_ae = (document.getElementById("up_v_ae").checked) ? "e" : "_";
                        let c_aa = (document.getElementById("up_v_aa").checked) ? "a" : "_";
                        let sVerbTag = c_i + c_t + c_n + c_p + c_m + c_ae + c_aa;
                        if (!sVerbTag.endsWith("__") && !sVerbTag.startsWith("____")) {
                            this.addFlexion(sWord, sWord, ":V" + c_g + "_" + sVerbTag);
                        }
                        break;
                    case "W":
                        this.addFlexion(sWord, sWord, ":W");
                        break;
                    case "M1":
                        sGenderTag = this.getRadioValue("genre_m1");
                        if (sGenderTag) {
                            this.addFlexion(sWord, sWord, ":M1"+sGenderTag+":i");
                        }
                        break;
                    case "M2":
                        sGenderTag = this.getRadioValue("genre_m2");
                        if (sGenderTag) {
                            this.addFlexion(sWord, sWord, ":M2"+sGenderTag+":i");
                        }
                        break;
                    case "MP":
                        sGenderTag = this.getRadioValue("genre_mp");
                        if (sGenderTag) {
                            this.addFlexion(sWord, sWord, ":MP"+sGenderTag+":i");
                        }
                        break;
                    case "X":
                        let sLemma = document.getElementById("lemma").value.trim();
                        let sTags = document.getElementById("tags").value.trim();
                        if (sLemma.length > 0 && sTags.startsWith(":")) {
                            this.addFlexion(sWord, sLemma, sTags);
                        }
                        break;
                }
            }
            this.show();
        }
        catch (e) {
            showError(e);
        }
    },

    getRadioValue: function (sName) {
        if (document.querySelector('input[name="' + sName + '"]:checked')) {
            return document.querySelector('input[name="' + sName + '"]:checked').value;
        }
        return null;
    },

    show: function () {
        let sText = "";
        for (let [sFlexion, sLemma, sTag] of this.lFlexion) {
            sText += sFlexion + " (" + sLemma + ") " + sTag + "<br/>\n";
        }
        if (sText) {
            document.getElementById("results").innerHTML = sText;
            oPage.showActions();
        } else {
            oPage.hideActions();
        }
    },

    addToDictionary: function () {

    }
}
