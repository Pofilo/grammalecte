// JavaScript

"use strict";

// Chrome don’t follow the W3C specification:
// https://browserext.github.io/browserext/
let bChrome = false;
if (typeof(browser) !== "object") {
    var browser = chrome;
    bChrome = true;
}

function createNode  (sType, oAttr, oDataset=null) {
    try {
        let xNode = document.createElement(sType);
        Object.assign(xNode, oAttr);
        if (oDataset) {
            Object.assign(xNode.dataset, oDataset);
        }
        return xNode;
    }
    catch (e) {
        showError(e);
    }
}

function showError (e) {
    console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
}


document.getElementById("lexicon_button").addEventListener("click", () => { oWidgets.showPage("lexicon"); }, false);
document.getElementById("add_word_button").addEventListener("click", () => { oWidgets.showPage("lemma"); }, false);

document.getElementById("table").addEventListener("click", (xEvent) => { oWidgets.onTableClick(xEvent); }, false);
document.getElementById("save_button").addEventListener("click", () => { oLexicon.save(); }, false);

document.getElementById("editor").addEventListener("click", (xEvent) => { oWidgets.onSelectionClick(xEvent); }, false);
document.getElementById("lemma").addEventListener("keyup", () => { oWidgets.onWrite(); }, false);
document.getElementById("lemma2").addEventListener("keyup", () => { oWidgets.onWrite2(); }, false);
document.getElementById("verb_pattern").addEventListener("keyup", () => { oFlexGen.update(); }, false);
document.getElementById("flexion").addEventListener("keyup", () => { oFlexGen.update(); }, false);
document.getElementById("tags").addEventListener("keyup", () => { oFlexGen.update(); }, false);
document.getElementById("add_to_lexicon").addEventListener("click", () => { oFlexGen.addToLexicon(); }, false);



/*
    ACTIONS
*/

const oWidgets = {

    showPage: function (sPage) {
        if (sPage == "lexicon") {
            this.hideElement("add_word_page");
            this.showElement("lexicon_page");
            document.getElementById("lexicon_button").style.backgroundColor = "hsl(210, 80%, 90%)";
            document.getElementById("add_word_button").style.backgroundColor = "hsl(210, 10%, 95%)";
        } else {
            this.hideElement("lexicon_page");
            this.showElement("add_word_page");
            document.getElementById("lexicon_button").style.backgroundColor = "hsl(210, 10%, 95%)";
            document.getElementById("add_word_button").style.backgroundColor = "hsl(210, 80%, 90%)";
        }
    },

    showElement: function (sElemId) {
        if (document.getElementById(sElemId)) {
            document.getElementById(sElemId).style.display = "block";
        } else {
            console.log("HTML node named <" + sElemId + "> not found.")
        }
    },

    hideElement: function (sElemId) {
        if (document.getElementById(sElemId)) {
            document.getElementById(sElemId).style.display = "none";
        } else {
            console.log("HTML node named <" + sElemId + "> not found.")
        }
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
        this.showElement(sName);
    },

    clear: function () {
        try {
            document.getElementById("lemma2").value = "";
            this.hideElement("word_section2");
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
            document.getElementById("verb_pattern").value = "";
            // autre
            document.getElementById("flexion").value = "";
            document.getElementById("tags").value = "";
        }
        catch (e) {
            showError(e);
        }
    },

    onSelectionClick: function (xEvent) {
        try {
            let xElem = xEvent.target;
            if (xElem.id) {
                if (xElem.id.startsWith("select_")) {
                    this.showSection("section_" + xElem.id.slice(7));
                    oFlexGen.setMainTag(xElem.dataset.tag);
                    oFlexGen.update();
                } else if (xElem.id.startsWith("up_")) {
                    oFlexGen.update();
                }
            }
        }
        catch (e) {
            showError(e);
        }
    },

    onWrite: function () {
        if (document.getElementById("lemma").value.trim() !== "") {
            this.showElement("editor");
            oFlexGen.update();
        } else {
            this.showSection("section_vide");
            this.hideElement("editor");
            this.hideElement("actions");
        }
    },

    onWrite2: function () {
        if (document.getElementById("lemma2").value.trim() !== "") {
            this.showElement("word_section2");
            oFlexGen.update();
        } else {
            this.hideElement("word_section2");
        }
    },

    createTableHeader: function () {
        let xRowNode = createNode("tr");
        xRowNode.appendChild(createNode("th", { textContent: "·" }));
        xRowNode.appendChild(createNode("th", { textContent: "#" }));
        xRowNode.appendChild(createNode("th", { textContent: "Forme fléchie" }));
        xRowNode.appendChild(createNode("th", { textContent: "Lemme" }));
        xRowNode.appendChild(createNode("th", { textContent: "Étiquettes" }));
        return xRowNode;
    },

    createRowNode: function (n, sFlexion, sLemma, sTags) {
        let xRowNode = createNode("tr", { id: "row_" + n });
        xRowNode.appendChild(createNode("td", { textContent: "×", className: "delete_entry", title: "Effacer cette entrée" }, { id_entry: n }));
        xRowNode.appendChild(createNode("td", { textContent: n }));
        xRowNode.appendChild(createNode("td", { textContent: sFlexion }));
        xRowNode.appendChild(createNode("td", { textContent: sLemma }));
        xRowNode.appendChild(createNode("td", { textContent: sTags }));
        return xRowNode;
    },

    displayTable: function (lFlex) {
        this.clearTable();
        if (lFlex.length > 0) {
            let xTable = document.getElementById("table");
            let n = 0;
            this.hideElement("no_elem_line");
            xTable.appendChild(this.createTableHeader());
            for (let [sFlexion, sLemma, sTags] of lFlex) {
                xTable.appendChild(this.createRowNode(n, sFlexion, sLemma, sTags));
                n += 1;
            }
        } else {
            this.showElement("no_elem_line");
        }
    },

    addEntriesToTable: function (n, lFlex) {
        let xTable = document.getElementById("table");
        if (lFlex.length > 0) {
            if (document.getElementById("no_elem_line").style.display !== "none") {
                this.hideElement("no_elem_line");
                xTable.appendChild(this.createTableHeader());
            }
            for (let [sFlexion, sLemma, sTags] of lFlex) {
                xTable.appendChild(this.createRowNode(n, sFlexion, sLemma, sTags));
                n += 1;
            }
        }
    },

    clearTable: function () {
        let xTable = document.getElementById("table");
        while (xTable.firstChild) {
            xTable.removeChild(xTable.firstChild);
        }
    },

    onTableClick: function (xEvent) {
        try {
            let xElem = xEvent.target;
            if (xElem.className) {
                if (xElem.className == "delete_entry") {
                    let iEntry = xElem.dataset.id_entry
                    oLexicon.lFlexion[parseInt(iEntry)] = null;
                    this.hideElement("row_"+iEntry);
                    this.showElement("save_button");
                }
            }
        }
        catch (e) {
            showError(e);
        }
    }
}



const oFlexGen = {

    cMainTag: "",

    lFlexion: [],

    clear: function () {
        this.lFlexion = [];
        oWidgets.hideElement("actions");
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
            let sLemma = document.getElementById("lemma").value.trim();
            if (sLemma.length > 0) {
                switch (this.cMainTag) {
                    case "N":
                        if (!this.getRadioValue("POS") || !this.getRadioValue("genre")) {
                            break;
                        }
                        let sTag = this.getRadioValue("POS") + this.getRadioValue("genre");
                        switch (this.getRadioValue("pluriel")) {
                            case "s":
                                this.addFlexion(sLemma, sLemma, sTag+":s/*");
                                this.addFlexion(sLemma+"s", sLemma, sTag+":p/*");
                                break;
                            case "x":
                                this.addFlexion(sLemma, sLemma, sTag+":s/*");
                                this.addFlexion(sLemma+"x", sLemma, sTag+":p/*");
                                break;
                            case "i":
                                this.addFlexion(sLemma, sLemma, sTag+":i/*");
                                break;
                        }
                        let sLemma2 = document.getElementById("lemma2").value.trim();
                        if (sLemma2.length > 0  &&  this.getRadioValue("POS2")  &&  this.getRadioValue("genre2")) {
                            let sTag2 = this.getRadioValue("POS2") + this.getRadioValue("genre2");
                            switch (this.getRadioValue("pluriel2")) {
                                case "s":
                                    this.addFlexion(sLemma2, sLemma, sTag2+":s/*");
                                    this.addFlexion(sLemma2+"s", sLemma, sTag2+":p/*");
                                    break;
                                case "x":
                                    this.addFlexion(sLemma2, sLemma, sTag2+":s/*");
                                    this.addFlexion(sLemma2+"x", sLemma, sTag2+":p/*");
                                    break;
                                case "i":
                                    this.addFlexion(sLemma2, sLemma, sTag2+":i/*");
                                    break;
                            }
                        }
                        break;
                    case "V": {
                        if (!sLemma.endsWith("er") && !sLemma.endsWith("ir") && !sLemma.endsWith("re")) {
                            break;
                        }
                        sLemma = sLemma.toLowerCase();
                        let cGroup = "";
                        let c_i = (document.getElementById("up_v_i").checked) ? "i" : "_";
                        let c_t = (document.getElementById("up_v_t").checked) ? "t" : "_";
                        let c_n = (document.getElementById("up_v_n").checked) ? "n" : "_";
                        let c_p = (document.getElementById("up_v_p").checked) ? "p" : "_";
                        let c_m = (document.getElementById("up_v_m").checked) ? "m" : "_";
                        let c_ae = (document.getElementById("up_v_ae").checked) ? "e" : "_";
                        let c_aa = (document.getElementById("up_v_aa").checked) ? "a" : "_";
                        let sVerbTag = c_i + c_t + c_n + c_p + c_m + c_ae + c_aa;
                        if (!sVerbTag.endsWith("__") && !sVerbTag.startsWith("____")) {
                            let sVerbPattern = document.getElementById("verb_pattern").value.trim();
                            if (sVerbPattern.length == 0) {
                                if (!sLemma.endsWith("er") && !sLemma.endsWith("ir")) {
                                    break;
                                }
                                // tables de conjugaison du 1er et du 2e groupe
                                let cGroup = (sLemma.endsWith("er")) ? "1" : "2";
                                for (let [nCut, sAdd, sFlexTags, sPattern] of this._getConjRules(sLemma)) {
                                    if (!sPattern || RegExp(sPattern).test(sLemma)) {
                                        this.addFlexion(sLemma.slice(0,-nCut)+sAdd, sLemma, ":V" + cGroup + "_" + sVerbTag + sFlexTags);
                                    }
                                }
                                // participes passés
                                let bPpasVar = (document.getElementById("up_partpas").checked) ? "var" : "invar";
                                let lPpasRules = (sLemma.endsWith("er")) ? oConj["V1_ppas"][bPpasVar] : oConj["V2_ppas"][bPpasVar];
                                for (let [nCut, sAdd, sFlexTags, sPattern] of lPpasRules) {
                                    if (!sPattern || RegExp(sPattern).test(sLemma)) {
                                        this.addFlexion(sLemma.slice(0,-nCut)+sAdd, sLemma, ":V" + cGroup + "_" + sVerbTag + sFlexTags);
                                    }
                                }
                            } else {
                                // copie du motif d’un autre verbe : utilisation du conjugueur
                                if (conj.isVerb(sVerbPattern)) {
                                    let oVerb = new Verb(sLemma, sVerbPattern);
                                    for (let [sTag1, dFlex] of oVerb.dConj.entries()) {
                                        if (sTag1 !== ":Q") {
                                            for (let [sTag2, sConj] of dFlex.entries()) {
                                                if (sTag2.startsWith(":") && sConj !== "") {
                                                    this.addFlexion(sConj, sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + sTag1 + sTag2);
                                                }
                                            }
                                        } else {
                                            // participes passés
                                            if (dFlex.get(":Q3") !== "") {
                                                if (dFlex.get(":Q2") !== "") {
                                                    this.addFlexion(dFlex.get(":Q1"), sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:m:s/*");
                                                    this.addFlexion(dFlex.get(":Q2"), sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:m:p/*");
                                                } else {
                                                    this.addFlexion(dFlex.get(":Q1"), sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:m:i/*");
                                                }
                                                this.addFlexion(dFlex.get(":Q3"), sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:f:s/*");
                                                this.addFlexion(dFlex.get(":Q4"), sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:f:p/*");
                                            } else {
                                                this.addFlexion(dFlex.get(":Q1"), sLemma, ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:e:i/*");
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        break;
                    }
                    case "W":
                        sLemma = sLemma.toLowerCase();
                        this.addFlexion(sLemma, sLemma, ":W/*");
                        break;
                    case "M1":
                        sLemma = sLemma.slice(0,1).toUpperCase() + sLemma.slice(1);
                        sGenderTag = this.getRadioValue("genre_m1");
                        if (sGenderTag) {
                            this.addFlexion(sLemma, sLemma, ":M1"+sGenderTag+":i/*");
                        }
                        break;
                    case "M2":
                        sLemma = sLemma.slice(0,1).toUpperCase() + sLemma.slice(1);
                        sGenderTag = this.getRadioValue("genre_m2");
                        if (sGenderTag) {
                            this.addFlexion(sLemma, sLemma, ":M2"+sGenderTag+":i/*");
                        }
                        break;
                    case "MP":
                        sGenderTag = this.getRadioValue("genre_mp");
                        if (sGenderTag) {
                            this.addFlexion(sLemma, sLemma, ":MP"+sGenderTag+":i/*");
                        }
                        break;
                    case "X":
                        let sFlexion = document.getElementById("flexion").value.trim();
                        let sTags = document.getElementById("tags").value.trim();
                        if (sFlexion.length > 0 && sTags.startsWith(":")) {
                            this.addFlexion(sFlexion, sLemma, sTags);
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

    _getConjRules: function (sVerb) {
        if (sVerb.endsWith("ir")) {
            // deuxième groupe
            return oConj["V2"];
        } else if (sVerb.endsWith("er")) {
            // premier groupe
            if (sVerb.slice(-5) in oConj["V1"]) {
                return oConj["V1"][sVerb.slice(-5)];
            }
            if (sVerb.slice(-4) in oConj["V1"]) {
                if (sVerb.endsWith("eler") || sVerb.endsWith("eter")) {
                    return oConj["V1"][sVerb.slice(-4)]["1"];
                }
                return oConj["V1"][sVerb.slice(-4)];
            }
            if (sVerb.slice(-3) in oConj["V1"]) {
                return oConj["V1"][sVerb.slice(-3)];
            }
            return oConj["V1"]["er"];
        } else {
            // troisième groupe
            return [ [0, "", ":Y/*", false] ];
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
            sText += sFlexion + " (" + sLemma + ") " + sTag + "\n";
        }
        if (sText) {
            document.getElementById("results").textContent = sText;
            oWidgets.showElement("actions");
        } else {
            oWidgets.hideElement("actions");
        }
    },

    addToLexicon: function () {
        try {
            oLexicon.addFlexions(this.lFlexion);
            document.getElementById("lemma").value = "";
            oWidgets.showSection("section_vide");
            oWidgets.hideElement("editor");
            oWidgets.hideElement("actions");
            oWidgets.clear();
            oWidgets.showElement("save_button");
            this.clear();
            this.cMainTag = "";
        }
        catch (e) {
            showError(e);
        }
    }
}



const oLexicon = {

    lFlexion: [],

    addFlexions: function (lFlex) {
        let n = this.lFlexion.length;
        for (let aFlex of lFlex) {
            this.lFlexion.push(aFlex);
        }
        oWidgets.addEntriesToTable(n, lFlex);
    },

    load: function () {
        if (bChrome) {
            browser.storage.local.get("lexicon_list", this._setList);
            return;
        }
        let xPromise = browser.storage.local.get("lexicon_list");
        xPromise.then(this._setList.bind(this), showError);
    },

    _setList: function (dResult) {
        if (dResult.hasOwnProperty("lexicon_list")) {
            this.lFlexion = dResult.lexicon_list;
        }
        oWidgets.displayTable(this.lFlexion);
    },

    save: function () {
        oWidgets.hideElement("save_button");
        let lResult = [];
        for (let e of this.lFlexion) {
            if (e !== null) {
                lResult.push(e);
            }
        }
        browser.storage.local.set({ "lexicon_list": lResult });
        this.lFlexion = lResult;
        oWidgets.displayTable(this.lFlexion);
    },

    build: function () {
        return null;
    },

    export: function () {
        let xBlob = new Blob(['{ "app": "grammalecte", "data": ' + JSON.stringify(this.lFlexion) + ' }'], {type: 'application/json'}); 
        let sURL = URL.createObjectURL(xBlob);
        browser.downloads.download({ filename: "grammalecte_dictionnaire_personnel.json", url: sURL, saveAs: true });
    }
}


oLexicon.load();
