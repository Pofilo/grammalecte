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

function showElement (sElemId, sDisplay="block") {
    if (document.getElementById(sElemId)) {
        document.getElementById(sElemId).style.display = sDisplay;
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



class Table {

    constructor (sNodeId, lColumn, sProgressBarId, sResultId="", bDeleteButtons=true, bActionButtons) {
        this.sNodeId = sNodeId;
        this.xTable = document.getElementById(sNodeId);
        this.xApply = document.getElementById("apply");
        this.nColumn = lColumn.length;
        this.lColumn = lColumn;
        this.xProgressBar = document.getElementById(sProgressBarId);
        this.xNumEntry = document.getElementById(sResultId);
        this.lEntry = [];
        this.nEntry = 0;
        this.dSelectedDictionaries = new Map();
        this.lSelectedDictionaries = [];
        this.dDict = new Map();
        this.bDeleteButtons = bDeleteButtons;
        this.bActionButtons = bActionButtons;
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

    init () {
        if (bChrome) {
            browser.storage.local.get("selected_dictionaries_list", this._init.bind(this));
            return;
        }
        let xPromise = browser.storage.local.get("selected_dictionaries_list");
        xPromise.then(this._init.bind(this), showError);
    }

    _init (oResult) {
        if (oResult.hasOwnProperty("selected_dictionaries_list")) {
            this.lSelectedDictionaries = oResult.selected_dictionaries_list;
            console.log(this.lSelectedDictionaries);
        }
        this.getDictionarieslist();
    }

    getDictionarieslist () {
        fetch("http://localhost/dictionaries/")
        .then((response) => {
            if (response.ok) {
                return response.json();
            } else {
                return null;
            }
        })
        .then((response) => {
            if (response) {
                this.fill(response);
                this.showSelectedDictionaries(true);
            } else {
                // todo
            }
        })
        .catch((e) => {
            showError(e);
        });
    }

    getDictionary (sId, sName) {
        console.log("get: "+sName);
        fetch("http://localhost/download/"+sName)
        .then((response) => {
            if (response.ok) {
                return response.json();
            } else {
                console.log("dictionary not loaded: " + sName);
                return null;
            }
        })
        .then((response) => {
            if (response) {
                this.selectEntry(sId, sName);
                this.dDict.set(sName, response);
                browser.storage.local.set({ "stored_dictionaries": this.dDict });
            } else {
                //
            }
        })
        .catch((e) => {
            showError(e);
        });
    }

    showEntryNumber () {
        if (this.xNumEntry) {
            this.xNumEntry.textContent = this.nEntry;
        }
    }

    _addRow (lData) {
        let [nDicId, sName, nEntry, sDescription, sLastUpdate, ...data] = lData;
        let xRowNode = createNode("tr", { id: this.sNodeId + "_row_" + nDicId });
        if (this.bDeleteButtons) {
            xRowNode.appendChild(createNode("td", { textContent: "×", className: "delete_entry", title: "Effacer cette entrée" }, { id_entry: nDicId }));
        }
        xRowNode.appendChild(createNode("td", { textContent: sName }));
        xRowNode.appendChild(createNode("td", { textContent: nEntry }));
        xRowNode.appendChild(createNode("td", { textContent: sDescription }));
        xRowNode.appendChild(createNode("td", { textContent: sLastUpdate }));
        if (this.bActionButtons) {
            xRowNode.appendChild(createNode("td", { textContent: "+", className: "select_entry", title: "Sélectionner/Désélectionner cette entrée" }, { id_entry: nDicId, dict_name: sName }));
        }
        this.xTable.appendChild(xRowNode);
        if (this.lSelectedDictionaries.includes(sName)) {
            this.dSelectedDictionaries.set(sName, nDicId);
        }
    }

    listen () {
        if (this.bDeleteButtons || this.bActionButtons) {
            this.xTable.addEventListener("click", (xEvent) => { this.onTableClick(xEvent); }, false);
        }
        this.xApply.addEventListener("click", (xEvent) => { this.generateCommunityDictionary(xEvent); }, false);
    }

    onTableClick (xEvent) {
        try {
            let xElem = xEvent.target;
            if (xElem.className) {
                switch (xElem.className) {
                    case "delete_entry":
                        this.deleteRow(xElem.dataset.id_entry, xElem.dataset.dict_name);
                        break;
                    case "select_entry":
                        this.getDictionary(xElem.dataset.id_entry, xElem.dataset.dict_name);
                        break;
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
            showElement("save_button", "inline-block");
        }
        showElement("apply");
    }

    selectEntry (nEntryId, sDicName) {
        let sRowId = this.sNodeId + "_row_" + nEntryId;
        if (!this.dSelectedDictionaries.has(sDicName)) {
            this.dSelectedDictionaries.set(sDicName, nEntryId);
            document.getElementById(sRowId).style.backgroundColor = "hsl(210, 50%, 90%)";
        }
        else {
            this.dSelectedDictionaries.delete(sDicName);
            document.getElementById(sRowId).style.backgroundColor = "";
        }
        showElement("apply");
        this.showSelectedDictionaries();
    }

    clearSelectedDict () {
        let xDicList = document.getElementById("dictionaries_list");
        while (xDicList.firstChild) {
            xDicList.removeChild(xDicList.firstChild);
        }
    }

    showSelectedDictionaries (bUpdateTable=false) {
        this.clearSelectedDict();
        let xDicList = document.getElementById("dictionaries_list");
        if (this.dSelectedDictionaries.size === 0) {
            xDicList.textContent = "[Aucun]";
            return;
        }
        for (let [sName, nDicId] of this.dSelectedDictionaries) {
            xDicList.appendChild(this._createDictLabel(nDicId, sName));
            if (bUpdateTable) {
                document.getElementById(this.sNodeId + "_row_" + nDicId).style.backgroundColor = "hsl(210, 50%, 90%)";
            }
        }
    }

    _createDictLabel (nDicId, sLabel) {
        let xLabel = createNode("div", {className: "dic_button"});
        let xCloseButton = createNode("div", {className: "dic_button_close", textContent: "×"}, {id_entry: nDicId});
        xCloseButton.addEventListener("click", () => {
            this.dSelectedDictionaries.delete(sLabel);
            document.getElementById(this.sNodeId+"_row_"+nDicId).style.backgroundColor = "";
            xLabel.style.display = "none";
            showElement("apply");
        });
        xLabel.appendChild(xCloseButton);
        xLabel.appendChild(createNode("div", {className: "dic_button_label", textContent: sLabel}));
        return xLabel;
    }

    generateCommunityDictionary (xEvent) {
        hideElement("apply");
        let lDict = [];
        for (let sName of this.dSelectedDictionaries.keys()) {
            lDict.push(this.dDict.get(sName));
        }
        let oDict = dic_merger.merge(lDict, "S", "fr", "Français", "fr.community", "Dictionnaire communautaire (personnalisé)", this.xProgressBar);
        console.log(oDict);
        browser.storage.local.set({ "community_dictionary": oDict });
        browser.storage.local.set({ "selected_dictionaries_list": Array.from(this.dSelectedDictionaries.keys()) });
    }
}

const oDicTable = new Table("dictionaries_table", ["Nom", "Entrées", "Description", "Date"], "wait_progress", "num_dic", false, true);

oDicTable.init();
