// JavaScript

"use strict";

// Chrome don’t follow the W3C specification:
// https://browserext.github.io/browserext/
let bChrome = false;
if (typeof(browser) !== "object") {
    var browser = chrome;
    bChrome = true;
}


/*
    Common functions
*/

function showError (e) {
    console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
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

function showElement (sElemId) {
    if (document.getElementById(sElemId)) {
        document.getElementById(sElemId).style.display = "block";
    } else {
        console.log("HTML node named <" + sElemId + "> not found.")
    }
}

function hideElement (sElemId) {
    if (document.getElementById(sElemId)) {
        document.getElementById(sElemId).style.display = "none";
    } else {
        console.log("HTML node named <" + sElemId + "> not found.")
    }
}


const oTabulations = {

    lPage: ["lexicon_page", "add_page", "search_page", "info_page"],

    showPage: function (sRequestedPage) {
        for (let sPage of this.lPage) {
            if (sPage !== sRequestedPage) {
                hideElement(sPage);
                this.downlightButton(sPage.slice(0,-5) + "_button");
            }
        }
        showElement(sRequestedPage);
        this.highlightButton(sRequestedPage.slice(0,-5) + "_button");
        if (sRequestedPage == "add_page") {
            document.getElementById("lemma").focus();
        }
    },

    highlightButton: function (sButton) {
        if (document.getElementById(sButton)) {
            let xButton = document.getElementById(sButton);
            xButton.style.backgroundColor = "hsl(210, 80%, 90%)";
            xButton.style.color = "hsl(210, 80%, 30%)";
            xButton.style.fontWeight = "bold";
        }
    },

    downlightButton: function (sButton) {
        if (document.getElementById(sButton)) {
            let xButton = document.getElementById(sButton);
            xButton.style.backgroundColor = "hsl(210, 10%, 95%)";
            xButton.style.color = "hsl(210, 10%, 50%)";
            xButton.style.fontWeight = "normal";
        }
    },

    listen: function () {
        document.getElementById("lexicon_button").addEventListener("click", () => { this.showPage("lexicon_page"); }, false);
        document.getElementById("add_button").addEventListener("click", () => { this.showPage("add_page"); }, false);
        document.getElementById("search_button").addEventListener("click", () => { this.showPage("search_page"); }, false);
        document.getElementById("info_button").addEventListener("click", () => { this.showPage("info_page"); }, false);
    }
}


class Table {

    constructor (sNodeId, lColumn, sProgressBarId, sResultId="", bDeleteButtons=true) {
        this.sNodeId = sNodeId;
        this.xTable = document.getElementById(sNodeId);
        this.nColumn = lColumn.length;
        this.lColumn = lColumn;
        this.xProgressBar = document.getElementById(sProgressBarId);
        this.xNumEntry = document.getElementById(sResultId);
        this.iEntryIndex = 0;
        this.lEntry = [];
        this.nEntry = 0;
        this.bDeleteButtons = bDeleteButtons;
        this._createHeader();
        this.listen();
    }

    _createHeader () {
        let xRowNode = createNode("tr");
        if (this.bDeleteButtons) {
            xRowNode.appendChild(createNode("th", { textContent: "·", width: "12px" }));
        }
        for (let sColumn of this.lColumn) {
            xRowNode.appendChild(createNode("th", { textContent: sColumn }));
        }
        this.xTable.appendChild(xRowNode);
    }

    clear () {
        while (this.xTable.firstChild) {
            this.xTable.removeChild(this.xTable.firstChild);
        }
        this.lEntry = [];
        this.nEntry = 0;
        this.iEntryIndex = 0;
        this._createHeader();
        this.showEntryNumber();
    }

    fill (lFlex) {
        this.clear();
        if (lFlex.length > 0) {
            this.xProgressBar.max = lFlex.length;
            this.xProgressBar.value = 1;
            for (let lData of lFlex) {
                this._addRow(lData);
                this.xProgressBar.value += 1;
            }
            this.xProgressBar.value = this.xProgressBar.max;
        }
        this.lEntry = lFlex;
        this.nEntry = lFlex.length;
        this.showEntryNumber();
    }

    addEntries (lFlex) {
        this.lEntry.push(...lFlex);
        for (let lData of lFlex) {
            this._addRow(lData);
        }
        this.nEntry += lFlex.length;
        this.showEntryNumber();
    }

    showEntryNumber () {
        if (this.xNumEntry) {
            this.xNumEntry.textContent = this.nEntry;
        }
    }

    _addRow (lData) {
        let xRowNode = createNode("tr", { id: this.sNodeId + "_row_" + this.iEntryIndex });
        if (this.bDeleteButtons) {
            xRowNode.appendChild(createNode("td", { textContent: "×", className: "delete_entry", title: "Effacer cette entrée" }, { id_entry: this.iEntryIndex }));
        }
        for (let data of lData) {
            xRowNode.appendChild(createNode("td", { textContent: data }));
        }
        this.xTable.appendChild(xRowNode);
        this.iEntryIndex += 1;
    }

    listen () {
        if (this.bDeleteButtons) {
            this.xTable.addEventListener("click", (xEvent) => { this.onTableClick(xEvent); }, false);
        }
    }

    onTableClick (xEvent) {
        try {
            let xElem = xEvent.target;
            if (xElem.className) {
                if (xElem.className == "delete_entry") {
                    this.deleteRow(xElem.dataset.id_entry);
                }
            }
        }
        catch (e) {
            showError(e);
        }
    }

    deleteRow (iEntry) {
        this.lEntry[parseInt(iEntry)] = null;
        if (document.getElementById(this.sNodeId + "_row_" + iEntry)) {
            document.getElementById(this.sNodeId + "_row_" + iEntry).style.display = "none";
        }
        this.nEntry -= 1;
        this.showEntryNumber();
        if (this.sNodeId == "lexicon_table") {
            showElement("save_button");
        }
    }

    getEntries () {
        return this.lEntry.filter((e) => e !== null);
    }
}


const oGenerator = {

    sLemma: "",

    cMainTag: "",

    lFlexion: [],

    listen: function () {
        document.getElementById("editor").addEventListener("click", (xEvent) => { this.onSelectionClick(xEvent); }, false);
        document.getElementById("lemma").addEventListener("keyup", () => { this.onWrite(); }, false);
        document.getElementById("lemma2").addEventListener("keyup", () => { this.onWrite2(); }, false);
        document.getElementById("verb_pattern").addEventListener("keyup", () => { this.update(); }, false);
        document.getElementById("flexion").addEventListener("keyup", () => { this.update(); }, false);
        document.getElementById("tags").addEventListener("keyup", () => { this.update(); }, false);
        document.getElementById("add_to_lexicon").addEventListener("click", () => { this.addToLexicon(); }, false);
    },

    lSection: ["nom", "verbe", "adverbe", "nom_propre", "autre"],

    hideAllSections: function () {
        for (let sSection of this.lSection) {
            hideElement("section_" + sSection);
            document.getElementById("select_" + sSection).style.backgroundColor = "";
        }
    },

    showSection: function (sName) {
        this.clear();
        this.hideAllSections();
        if (document.getElementById(sName).style.display == "none") {
            showElement(sName);
        } else {
            hideElement(sName);
        }
    },

    clear: function () {
        try {
            document.getElementById("lemma2").value = "";
            hideElement("word_section2");
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
                    xElem.style.backgroundColor = "hsl(210, 50%, 90%)";
                    this.cMainTag = xElem.dataset.tag;
                    this.update();
                } else if (xElem.id.startsWith("up_")) {
                    this.update();
                }
            }
        }
        catch (e) {
            showError(e);
        }
    },

    onWrite: function () {
        if (document.getElementById("lemma").value.trim() !== "") {
            showElement("editor");
            this.update();
        } else {
            hideElement("editor");
        }
    },

    onWrite2: function () {
        if (document.getElementById("lemma2").value.trim() !== "") {
            showElement("word_section2");
            this.update();
        } else {
            hideElement("word_section2");
        }
    },

    update: function () {
        try {
            this.lFlexion = [];
            this.sLemma = document.getElementById("lemma").value.trim();
            if (this.sLemma.length > 0) {
                switch (this.cMainTag) {
                    case "N":
                        if (!this.getRadioValue("POS") || !this.getRadioValue("genre")) {
                            break;
                        }
                        let sTag = this.getRadioValue("POS") + this.getRadioValue("genre");
                        switch (this.getRadioValue("pluriel")) {
                            case "s":
                                this.lFlexion.push([this.sLemma, sTag+":s/*"]);
                                this.lFlexion.push([this.sLemma+"s", sTag+":p/*"]);
                                break;
                            case "x":
                                this.lFlexion.push([this.sLemma, sTag+":s/*"]);
                                this.lFlexion.push([this.sLemma+"x", sTag+":p/*"]);
                                break;
                            case "i":
                                this.lFlexion.push([this.sLemma, sTag+":i/*"]);
                                break;
                        }
                        let sLemma2 = document.getElementById("lemma2").value.trim();
                        if (sLemma2.length > 0  &&  this.getRadioValue("POS2")  &&  this.getRadioValue("genre2")) {
                            let sTag2 = this.getRadioValue("POS2") + this.getRadioValue("genre2");
                            switch (this.getRadioValue("pluriel2")) {
                                case "s":
                                    this.lFlexion.push([sLemma2, sTag2+":s/*"]);
                                    this.lFlexion.push([sLemma2+"s", sTag2+":p/*"]);
                                    break;
                                case "x":
                                    this.lFlexion.push([sLemma2, sTag2+":s/*"]);
                                    this.lFlexion.push([sLemma2+"x", sTag2+":p/*"]);
                                    break;
                                case "i":
                                    this.lFlexion.push([sLemma2, sTag2+":i/*"]);
                                    break;
                            }
                        }
                        break;
                    case "V": {
                        if (!this.sLemma.endsWith("er") && !this.sLemma.endsWith("ir") && !this.sLemma.endsWith("re")) {
                            break;
                        }
                        this.sLemma = this.sLemma.toLowerCase();
                        let cGroup = "";
                        let c_i = (document.getElementById("up_v_i").checked) ? "i" : "_";
                        let c_t = (document.getElementById("up_v_t").checked) ? "t" : "_";
                        let c_n = (document.getElementById("up_v_n").checked) ? "n" : "_";
                        let c_p = (document.getElementById("up_v_p").checked) ? "p" : "_";
                        let c_m = (document.getElementById("up_v_m").checked) ? "m" : "_";
                        let c_ae = (document.getElementById("up_v_ae").checked) ? "e" : "_";
                        let c_aa = (document.getElementById("up_v_aa").checked) ? "a" : "_";
                        let sVerbTag = c_i + c_t + c_n + c_p + c_m + c_ae + c_aa;
                        if (sVerbTag.includes("p") && !sVerbTag.startsWith("___p_")) {
                            sVerbTag = sVerbTag.replace("p", "q");
                        }
                        if (!sVerbTag.endsWith("__") && !sVerbTag.startsWith("____")) {
                            let sVerbPattern = document.getElementById("verb_pattern").value.trim();
                            if (sVerbPattern.length == 0) {
                                // utilisation du générateur de conjugaison
                                let bVarPpas = !document.getElementById("up_v_ppas").checked;
                                for (let [sFlexion, sFlexTags] of conj_generator.conjugate(this.sLemma, sVerbTag, bVarPpas)) {
                                    this.lFlexion.push([sFlexion, sFlexTags]);
                                }
                            } else {
                                // copie du motif d’un autre verbe : utilisation du conjugueur
                                if (conj.isVerb(sVerbPattern)) {
                                    let oVerb = new Verb(this.sLemma, sVerbPattern);
                                    for (let [sTag1, dFlex] of oVerb.dConj.entries()) {
                                        if (sTag1 !== ":Q") {
                                            for (let [sTag2, sConj] of dFlex.entries()) {
                                                if (sTag2.startsWith(":") && sConj !== "") {
                                                    this.lFlexion.push([sConj, ":V" + oVerb.cGroup + "_" + sVerbTag + sTag1 + sTag2]);
                                                }
                                            }
                                        } else {
                                            // participes passés
                                            if (dFlex.get(":Q3") !== "") {
                                                if (dFlex.get(":Q2") !== "") {
                                                    this.lFlexion.push([dFlex.get(":Q1"), ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:m:s/*"]);
                                                    this.lFlexion.push([dFlex.get(":Q2"), ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:m:p/*"]);
                                                } else {
                                                    this.lFlexion.push([dFlex.get(":Q1"), ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:m:i/*"]);
                                                }
                                                this.lFlexion.push([dFlex.get(":Q3"), ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:f:s/*"]);
                                                this.lFlexion.push([dFlex.get(":Q4"), ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:A:f:p/*"]);
                                            } else {
                                                this.lFlexion.push([dFlex.get(":Q1"), ":V" + oVerb.cGroup + "_" + sVerbTag + ":Q:e:i/*"]);
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        break;
                    }
                    case "W":
                        this.sLemma = this.sLemma.toLowerCase();
                        this.lFlexion.push([this.sLemma, ":W/*"]);
                        break;
                    case "M":
                        this.sLemma = this.sLemma.slice(0,1).toUpperCase() + this.sLemma.slice(1);
                        let sPOSTag = this.getRadioValue("pos_nom_propre")
                        let sGenderTag = this.getRadioValue("genre_m");
                        if (sGenderTag) {
                            this.lFlexion.push([this.sLemma, sPOSTag+sGenderTag+":i/*"]);
                        }
                        break;
                    case "X":
                        let sFlexion = document.getElementById("flexion").value.trim();
                        let sTags = document.getElementById("tags").value.trim();
                        if (sFlexion.length > 0 && sTags.startsWith(":")) {
                            this.lFlexion.push([sFlexion, sTags]);
                        }
                        break;
                }
            }
            if (this.lFlexion.length > 0) {
                showElement("add_to_lexicon");
            } else {
                hideElement("add_to_lexicon");
            }
            oGenWordsTable.fill(this.lFlexion);
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

    createFlexLemmaTagArray: function () {
        let lEntry = [];
        for (let [sFlex, sTags] of oGenWordsTable.getEntries()) {
            lEntry.push([sFlex, this.sLemma, sTags]);
        }
        return lEntry;
    },

    addToLexicon: function () {
        try {
            oLexiconTable.addEntries(this.createFlexLemmaTagArray());
            oGenWordsTable.clear();
            document.getElementById("lemma").value = "";
            document.getElementById("lemma").focus();
            this.hideAllSections();
            hideElement("editor");
            showElement("save_button");
            this.clear();
            this.cMainTag = "";
        }
        catch (e) {
            showError(e);
        }
    }
}

const oDictHandler = {
    oDictionaries: null,

    loadDictionaries: function () {
        if (bChrome) {
            browser.storage.local.get("dictionaries", this._loadDictionaries.bind(this));
            return;
        }
        let xPromise = browser.storage.local.get("dictionaries");
        xPromise.then(this._loadDictionaries.bind(this), showError);
    },

    _loadDictionaries: function (oResult) {
        if (!oResult.hasOwnProperty("dictionaries")) {
            return;
        }
        this.oDictionaries = oResult.dictionaries;
        oBinaryDict.load("__personal__");
    },

    getDictionary: function (sName) {
        if (this.oDictionaries  &&  this.oDictionaries.hasOwnProperty(sName)) {
            //console.log(this.oDictionaries[sName]);
            return this.oDictionaries[sName];
        }
        return null;
    },

    saveDictionary: function (sName, oJSON) {
        this.oDictionaries[sName] = oJSON;
        if (sName == "__personal__") {
            browser.runtime.sendMessage({ sCommand: "setDictionary", dParam: {sDictionary: "personal", oDict: oJSON}, dInfo: {} });
        }
        else if (sName == "__community__") {
            browser.runtime.sendMessage({ sCommand: "setDictionary", dParam: {sDictionary: "community", oDict: oJSON}, dInfo: {} });
        }
        else {
            // TODO: merge sub-dictionaries
        }
        this.storeDictionaries();
    },

    storeDictionaries: function () {
        browser.storage.local.set({ "dictionaries": this.oDictionaries });
    }
}

const oBinaryDict = {

    oIBDAWG: null,
    sName: null,

    load: function (sName) {
        console.log("lexicon editor, load: " + sName);
        this.sName = sName;
        let oJSON = oDictHandler.getDictionary(sName);
        if (oJSON) {
            this.parseDict(oJSON);
        } else {
            oLexiconTable.clear();
            this.setDictData(0, "[néant]");
        }
    },

    parseDict: function (oJSON) {
        try {
            this.oIBDAWG = new IBDAWG(oJSON);
        }
        catch (e) {
            console.error(e);
            this.setDictData(0, "#Erreur. Voir la console.");
            return;
        }
        let lEntry = [];
        for (let aRes of this.oIBDAWG.select()) {
            lEntry.push(aRes);
        }
        oLexiconTable.fill(lEntry);
        this.setDictData(this.oIBDAWG.nEntry, this.oIBDAWG.sDate);
    },

    import: function () {
        let xInput = document.getElementById("import_input");
        let xFile = xInput.files[0];
        let xURL = URL.createObjectURL(xFile);
        let sJSON = helpers.loadFile(xURL);
        if (sJSON) {
            try {
                let oJSON = JSON.parse(sJSON);
                this.parseDict(oJSON);
                oDictHandler.saveDictionary(this.sName, oJSON);
            }
            catch (e) {
                console.error(e);
                this.setDictData(0, "#Erreur. Voir la console.");
                return;
            }
        } else {
            this.setDictData(0, "[néant]");
            oDictHandler.saveDictionary(this.sName, null);
        }
    },

    setDictData: function (nEntries, sDate) {
        document.getElementById("dic_num_entries").textContent = nEntries;
        document.getElementById("dic_save_date").textContent = sDate;
        if (nEntries == 0) {
            hideElement("export_button");
        } else {
            showElement("export_button");
        }
    },

    listen: function () {
        document.getElementById("dic_selector").addEventListener("change", () => {this.load(document.getElementById("dic_selector").value)}, false);
        document.getElementById("save_button").addEventListener("click", () => { this.build(); }, false);
        document.getElementById("export_button").addEventListener("click", () => { this.export(); }, false);
        document.getElementById("import_input").addEventListener("change", () => { this.import(); }, false);
    },

    build: function () {
        let xProgressNode = document.getElementById("wait_progress");
        let lEntry = oLexiconTable.getEntries();
        if (lEntry.length > 0) {
            let oDAWG = new DAWG(lEntry, "S", "fr", "Français", this.sName, xProgressNode);
            let oJSON = oDAWG.createBinaryJSON(1);
            oDictHandler.saveDictionary(this.sName, oJSON);
            this.oIBDAWG = new IBDAWG(oJSON);
            this.setDictData(this.oIBDAWG.nEntry, this.oIBDAWG.sDate);
        } else {
            oDictHandler.saveDictionary(this.sName, null);
            this.setDictData(0, "[néant]");
        }
        hideElement("save_button");
    },

    export: function () {
        let xBlob = new Blob([ JSON.stringify(this.oIBDAWG.getJSON()) ], {type: 'application/json'});
        let sURL = URL.createObjectURL(xBlob);
        browser.downloads.download({ filename: "fr."+this.sName+".json", url: sURL, saveAs: true });
    }
}


const oSearch = {

    oSpellChecker: null,

    load: function () {
        this.oSpellChecker = new SpellChecker("fr", browser.extension.getURL("")+"grammalecte/graphspell/_dictionaries", "fr-allvars.json");
    },

    loadOtherDictionaries: function () {
        //TODO
    },

    listen: function () {
        document.getElementById("search_similar_button").addEventListener("click", () => { this.searchSimilar(); }, false);
        document.getElementById("search_regex_button").addEventListener("click", () => { this.searchRegex() }, false);
    },

    searchSimilar: function () {
        oSearchTable.clear();
        let sWord = document.getElementById("search_similar").value;
        if (sWord !== "") {
            let lResult = this.oSpellChecker.getSimilarEntries(sWord, 20);
            oSearchTable.fill(lResult);
        }
    },

    searchRegex: function () {
        let sFlexPattern = document.getElementById("search_flexion_pattern").value.trim();
        let sTagsPattern = document.getElementById("search_tags_pattern").value.trim();
        let lEntry = [];
        let i = 0;
        for (let aRes of this.oSpellChecker.select(sFlexPattern, sTagsPattern)) {
            lEntry.push(aRes);
            i++;
            if (i >= 2000) {
                break;
            }
        }
        oSearchTable.fill(lEntry);
    }
}


const oTagsInfo = {
    load: function () {
        let lEntry = [];
        for (let [sTag, [_, sLabel]] of _dTag) {
            lEntry.push([sTag, sLabel.trim()]);
        }
        oTagsTable.fill(lEntry);
    }
}


const oGenWordsTable = new Table("generated_words_table", ["Flexions", "Étiquettes"], "wait_progress");
const oLexiconTable = new Table("lexicon_table", ["Flexions", "Lemmes", "Étiquettes"], "wait_progress", "num_entries");
const oSearchTable = new Table("search_table", ["Flexions", "Lemmes", "Étiquettes"], "wait_progress", "search_num_entries", false);
const oTagsTable = new Table("tags_table", ["Étiquette", "Signification"], "wait_progress", "", false);


oTagsInfo.load();
oSearch.load();
oDictHandler.loadDictionaries();
oBinaryDict.listen();
oGenerator.listen();
oTabulations.listen();
oSearch.listen();
