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



class Table {

    constructor (sNodeId, lColumn, sProgressBarId, sResultId="", bDeleteButtons=true, bActionButtons) {
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
        if (this.bActionButtons) {
            xRowNode.appendChild(createNode("td", { textContent: "+", className: "select_entry", title: "Sélectionner/Désélectionner cette entrée" }, { id_entry: this.iEntryIndex }));
        }
        this.xTable.appendChild(xRowNode);
        this.iEntryIndex += 1;
    }

    listen () {
        if (this.bDeleteButtons || this.bActionButtons) {
            this.xTable.addEventListener("click", (xEvent) => { this.onTableClick(xEvent); }, false);
        }
    }

    onTableClick (xEvent) {
        try {
            let xElem = xEvent.target;
            if (xElem.className) {
                switch (xElem.className) {
                    case "delete_entry": this.deleteRow(xElem.dataset.id_entry); break;
                    case "select_entry": this.selectEntry(xElem.dataset.id_entry); break;
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
    }

    selectEntry (iEntry) {
        let sRowId = this.sNodeId + "_row_" + iEntry;
        document.getElementById(sRowId).style.backgroundColor = "hsl(120, 50%, 90%)";
    }

    getEntries () {
        return this.lEntry.filter((e) => e !== null);
    }
}


const oDicTable = new Table("dictionaries_table", ["Nom", "Créé par", "Entrées", "Description"], "wait_progress", "", false, true);

oDicTable.fill([
    ["Ambre", "Inconnu", "240", "Univers des Princes d’Ambre (de Roger Zelazny)"],
    ["Malaz", "Inconnu", "2340", "Univers du Livre des Martyrs (de Steven Erikson)"],
    ["Pudlard", "Inconnu", "1440", "Univers d’Harry Potter de XXXX"],
    ["Dune", "Inconnu", "2359", "Univers de Dune (de Frank Herbert)"],
    ["StarWars", "Inconnu", "4359", "Univers de Star Wars (de George Lucas)"]
]);
