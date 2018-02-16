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
document.getElementById("export_button").addEventListener("click", () => { oBinaryDict.export(); }, false);

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
            document.getElementById("lemma").focus();
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
            this.showElement("display_progress");
            let xDisplayProgress = document.getElementById("display_progress");
            let xTable = document.getElementById("table");
            let n = 0;
            xDisplayProgress.max = lFlex.length;
            xDisplayProgress.value = 1;
            this.hideElement("no_elem_line");
            xTable.appendChild(this.createTableHeader());
            for (let [sFlexion, sLemma, sTags] of lFlex) {
                xTable.appendChild(this.createRowNode(n, sFlexion, sLemma, sTags));
                n += 1;
                xDisplayProgress.value += 1;
            }
            xDisplayProgress.value = xDisplayProgress.max;
            this.hideElement("display_progress");
        } else {
            this.showElement("no_elem_line");
        }
        this.updateData();
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
                    this.deleteEntry(xElem.dataset.id_entry);
                }
            }
        }
        catch (e) {
            showError(e);
        }
    },

    addEntriesToTable: function (iStart, lFlex) {
        let xTable = document.getElementById("table");
        if (lFlex.length > 0) {
            if (document.getElementById("no_elem_line").style.display !== "none") {
                this.hideElement("no_elem_line");
                xTable.appendChild(this.createTableHeader());
            }
            for (let [sFlexion, sLemma, sTags] of lFlex) {
                xTable.appendChild(this.createRowNode(iStart, sFlexion, sLemma, sTags));
                iStart += 1;
            }
        }
        this.updateData();
    },

    deleteEntry: function (iEntry) {
        oLexicon.deleteEntry(iEntry);
        this.hideElement("row_"+iEntry);
        this.showElement("save_button");
        this.updateData();
    },

    updateData: function () {
        document.getElementById("num_added_entries").textContent = oLexicon.nAddedEntries;
        document.getElementById("num_deleted_entries").textContent = oLexicon.nDeletedEntries;
        document.getElementById("num_entries").textContent = oLexicon.nEntries;
    },

    setDictData: function (nEntries, sDate) {
        document.getElementById("num_entries_saved").textContent = nEntries;
        document.getElementById("save_date").textContent = sDate;
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
            // premier groupe, conjugaison en fonction de la terminaison du lemme
            // 5 lettres
            if (sVerb.slice(-5) in oConj["V1"]) {
                return oConj["V1"][sVerb.slice(-5)];
            }
            // 4 lettres
            if (sVerb.slice(-4) in oConj["V1"]) {
                if (sVerb.endsWith("eler") || sVerb.endsWith("eter")) {
                    return oConj["V1"][sVerb.slice(-4)]["1"];
                }
                return oConj["V1"][sVerb.slice(-4)];
            }
            // 3 lettres
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
            document.getElementById("lemma").focus();
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
    nEntries: 0,
    nDeletedEntries: 0,
    nAddedEntries: 0,

    set: function (lFlexion) {
        this.lFlexion = lFlexion;
        this.resetModif();
        oWidgets.displayTable(this.lFlexion);
        if (this.lFlexion.length > 0) {
            oWidgets.showElement("export_button");
        } else {
            oWidgets.hideElement("export_button");
        }
    },

    addFlexions: function (lNewFlex) {
        let iStart = this.lFlexion.length;
        for (let aFlex of lNewFlex) {
            this.lFlexion.push(aFlex);
        }
        this.nAddedEntries += lNewFlex.length;
        this.nEntries += lNewFlex.length;
        oWidgets.addEntriesToTable(iStart, lNewFlex);
    },

    deleteEntry: function (iEntry) {
        this.lFlexion[parseInt(iEntry)] = null;
        this.nDeletedEntries++;
        this.nEntries--;
    },

    resetModif: function () {
        this.nEntries = this.lFlexion.length;
        this.nAddedEntries = 0;
        this.nDeletedEntries = 0;
    },

    save: function () {
        oWidgets.hideElement("save_button");
        this.lFlexion = this.lFlexion.filter((e) => e !== null);
        oBinaryDict.build(this.lFlexion);
        this.resetModif();
        oWidgets.displayTable(this.lFlexion);
        oWidgets.updateData();
    }
}


const oBinaryDict = {
    
    oIBDAWG: null,

    load: function () {
        if (bChrome) {
            browser.storage.local.get("oPersonalDictionary", this._load);
            return;
        }
        let xPromise = browser.storage.local.get("oPersonalDictionary");
        xPromise.then(this._load.bind(this), showError);
    },

    _load: function (oResult) {
        if (!oResult.hasOwnProperty("oPersonalDictionary")) {
            oWidgets.hideElement("export_button");
            return;
        }
        let oJSON = oResult.oPersonalDictionary;
        this.oIBDAWG = new IBDAWG(oJSON);
        let lEntry = [];
        for (let s of this.oIBDAWG.select()) {
            lEntry.push(s.split("\t"));
        }        
        oLexicon.set(lEntry);
        oWidgets.setDictData(this.oIBDAWG.nEntry, this.oIBDAWG.sDate);
        oWidgets.showElement("export_button");
    },

    build: function (lEntry) {
        oWidgets.showElement("build_progress");
        let xProgressNode = document.getElementById("build_progress");
        let oDAWG = new DAWG(lEntry, "S", "fr", "Français", "Dictionnaire personnel", xProgressNode);
        let oJSON = oDAWG.createBinaryJSON(1);
        this.save(oJSON);
        this.oIBDAWG = new IBDAWG(oJSON);
        oWidgets.setDictData(this.oIBDAWG.nEntry, this.oIBDAWG.sDate);
        oWidgets.hideElement("build_progress");
        oWidgets.showElement("export_button");
        browser.runtime.sendMessage({ sCommand: "setDictionary", dParam: {sType: "personal", oDict: oJSON}, dInfo: {} });
    },

    save: function (oJSON) {
        browser.storage.local.set({ "oPersonalDictionary": oJSON });
    },

    import: function () {
        // TO DO
    },

    export: function () {
        let xBlob = new Blob([ JSON.stringify(this.oIBDAWG.getJSON()) ], {type: 'application/json'}); 
        let sURL = URL.createObjectURL(xBlob);
        browser.downloads.download({ filename: "grammalecte_dictionnaire_personnel.json", url: sURL, saveAs: true });
    }
}

oBinaryDict.load();
