// Modify page

/*
    JS sucks (again, and again, and again, and again…)
    Not possible to load content from within the extension:
    https://bugzilla.mozilla.org/show_bug.cgi?id=1267027
    No SharedWorker, no images allowed for now…
*/

"use strict";


function showError (e) {
    console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
}

// Chrome don’t follow the W3C specification:
// https://browserext.github.io/browserext/
let bChrome = false;
if (typeof(browser) !== "object") {
    var browser = chrome;
    bChrome = true;
}


/*
function loadImage (sContainerClass, sImagePath) {
    let xRequest = new XMLHttpRequest();
    xRequest.open('GET', browser.extension.getURL("")+sImagePath, false);
    xRequest.responseType = "arraybuffer";
    xRequest.send();
    let blobTxt = new Blob([xRequest.response], {type: 'image/png'});
    let img = document.createElement('img');
    img.src = (URL || webkitURL).createObjectURL(blobTxt); // webkitURL is obsolete: https://bugs.webkit.org/show_bug.cgi?id=167518
    Array.filter(document.getElementsByClassName(sContainerClass), function (oElem) {
        oElem.appendChild(img);
    });
}
*/


const oGrammalecte = {

    nMenu: 0,
    lMenu: [],

    oTFPanel: null,
    oLxgPanel: null,
    oGCPanel: null,

    oMessageBox: null,

    xRightClickedNode: null,

    listenRightClick: function () {
        // Node where a right click is done
        // Bug report: https://bugzilla.mozilla.org/show_bug.cgi?id=1325814
        document.addEventListener('contextmenu', function (xEvent) {
            this.xRightClickedNode = xEvent.target;
        }.bind(this), true);
    },

    clearRightClickedNode: function () {
        this.xRightClickedNode = null;
    },

    createMenus: function () {
        let lNode = document.getElementsByTagName("textarea");
        for (let xNode of lNode) {
            if (xNode.style.display !== "none" && xNode.style.visibility !== "hidden") {
                this.lMenu.push(new GrammalecteMenu(this.nMenu, xNode));
                this.nMenu += 1;
            }
        }
    },

    createMenus2 () {
        let lNode = document.querySelectorAll("[contenteditable]");
        for (let xNode of lNode) {
            this.lMenu.push(new GrammalecteMenu(this.nMenu, xNode));
            this.nMenu += 1;
        }
    },

    rescanPage: function () {
        if (this.oTFPanel !== null) { this.oTFPanel.hide(); }
        if (this.oLxgPanel !== null) { this.oLxgPanel.hide(); }
        if (this.oGCPanel !== null) { this.oGCPanel.hide(); }
        for (let oMenu of this.lMenu) {
            oMenu.deleteNodes();
        }
        this.lMenu.length = 0; // to clear an array
        this.listenRightClick();
        this.createMenus();
        this.createMenus2();
    },

    createTFPanel: function () {
        if (this.oTFPanel === null) {
            this.oTFPanel = new GrammalecteTextFormatter("grammalecte_tf_panel", "Formateur de texte", 760, 600, false);
            //this.oTFPanel.logInnerHTML();
            this.oTFPanel.insertIntoPage();
            this.oTFPanel.adjustHeight();
        }
    },

    createLxgPanel: function () {
        if (this.oLxgPanel === null) {
            this.oLxgPanel = new GrammalecteLexicographer("grammalecte_lxg_panel", "Lexicographe", 500, 700);
            this.oLxgPanel.insertIntoPage();
        }
    },

    createGCPanel: function () {
        if (this.oGCPanel === null) {
            this.oGCPanel = new GrammalecteGrammarChecker("grammalecte_gc_panel", "Grammalecte", 500, 700);
            this.oGCPanel.insertIntoPage();
        }
    },

    createMessageBox: function () {
        if (this.oMessageBox === null) {
            this.oMessageBox = new GrammalecteMessageBox("grammalecte_message_box", "Grammalecte", 400, 250);
            this.oMessageBox.insertIntoPage();
        }
    },

    startGCPanel: function (xNode=null) {
        this.createGCPanel();
        this.oGCPanel.clear();
        this.oGCPanel.show();
        this.oGCPanel.start(xNode);
        this.oGCPanel.startWaitIcon();
    },

    startLxgPanel: function () {
        this.createLxgPanel();
        this.oLxgPanel.clear();
        this.oLxgPanel.show();
        this.oLxgPanel.startWaitIcon();
    },

    startFTPanel: function (xNode=null) {
        this.createTFPanel();
        this.oTFPanel.start(xNode);
        this.oTFPanel.show();
    },

    showMessage: function (sMessage) {
        this.createMessageBox();
        this.oMessageBox.show();
        this.oMessageBox.addMessage(sMessage);
    },

    getPageText: function () {
        let sPageText = document.body.innerText;
        let nPos = sPageText.indexOf("__grammalecte_panel__");
        if (nPos >= 0) {
            sPageText = sPageText.slice(0, nPos);
        }
        return sPageText;
    },

    createNode: function (sType, oAttr, oDataset=null) {
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
}


/*
    Connexion to the background
*/
let xGrammalectePort = browser.runtime.connect({name: "content-script port"});

xGrammalectePort.onMessage.addListener(function (oMessage) {
    let {sActionDone, result, dInfo, bEnd, bError} = oMessage;
    let sText = "";
    switch (sActionDone) {
        case "parseAndSpellcheck":
            if (!bEnd) {
                oGrammalecte.oGCPanel.addParagraphResult(result);
            } else {
                oGrammalecte.oGCPanel.stopWaitIcon();
            }
            break;
        case "parseAndSpellcheck1":
            oGrammalecte.oGCPanel.refreshParagraph(dInfo.sParagraphId, result);
            break;
        case "getListOfTokens":
            if (!bEnd) {
                oGrammalecte.oLxgPanel.addListOfTokens(result);
            } else {
                oGrammalecte.oLxgPanel.stopWaitIcon();
            }
            break;
        case "getSpellSuggestions":
            oGrammalecte.oGCPanel.oTooltip.setSpellSuggestionsFor(result.sWord, result.aSugg, dInfo.sErrorId);
            break;
        /*
            Commands received from the context menu
            (Context menu are initialized in background)
        */
        // Grammar checker commands
        case "rightClickGCEditableNode":
            if (oGrammalecte.xRightClickedNode !== null) {
                oGrammalecte.startGCPanel(oGrammalecte.xRightClickedNode);
                sText = (oGrammalecte.xRightClickedNode.tagName == "TEXTAREA") ? oGrammalecte.xRightClickedNode.value : oGrammalecte.xRightClickedNode.innerText;
                xGrammalectePort.postMessage({
                    sCommand: "parseAndSpellcheck",
                    dParam: {sText: sText, sCountry: "FR", bDebug: false, bContext: false},
                    dInfo: {sTextAreaId: oGrammalecte.xRightClickedNode.id}
                });
            } else {
                oGrammalecte.showMessage("Erreur. Le node sur lequel vous avez cliqué n’a pas pu être identifié. Sélectionnez le texte à corriger et relancez le correcteur via le menu contextuel.");
            }
            break;
        case "rightClickGCPage":
            oGrammalecte.startGCPanel();
            xGrammalectePort.postMessage({
                sCommand: "parseAndSpellcheck",
                dParam: {sText: oGrammalecte.getPageText(), sCountry: "FR", bDebug: false, bContext: false},
                dInfo: {}
            });
            break;
        case "rightClickGCSelectedText":
            oGrammalecte.startGCPanel();
            // selected text is sent to the GC worker in the background script.
            break;
        // Lexicographer commands
        case "rightClickLxgEditableNode":
            if (oGrammalecte.xRightClickedNode !== null) {
                oGrammalecte.startLxgPanel();
                sText = (oGrammalecte.xRightClickedNode.tagName == "TEXTAREA") ? oGrammalecte.xRightClickedNode.value : oGrammalecte.xRightClickedNode.textContent;
                xGrammalectePort.postMessage({
                    sCommand: "getListOfTokens",
                    dParam: {sText: sText},
                    dInfo: {sTextAreaId: oGrammalecte.xRightClickedNode.id}
                });
            } else {
                oGrammalecte.showMessage("Erreur. Le node sur lequel vous avez cliqué n’a pas pu être identifié. Sélectionnez le texte à analyser et relancez le lexicographe via le menu contextuel.");
            }
            break;
        case "rightClickLxgPage":
            oGrammalecte.startLxgPanel();
            xGrammalectePort.postMessage({
                sCommand: "getListOfTokens",
                dParam: {sText: oGrammalecte.getPageText()},
                dInfo: {}
            });
            break;
        case "rightClickLxgSelectedText":
            oGrammalecte.startLxgPanel();
            // selected text is sent to the GC worker in the background script.
            break;
        // Text formatter command
        case "rightClickTFEditableNode":
            if (oGrammalecte.xRightClickedNode !== null) {
                if (oGrammalecte.xRightClickedNode.tagName == "TEXTAREA") {
                    oGrammalecte.startFTPanel(oGrammalecte.xRightClickedNode);
                } else {
                    oGrammalecte.showMessage("Cette zone de texte n’est pas réellement un champ de formulaire, mais un node HTML éditable. Le formateur de texte n’est pas disponible pour ce type de champ de saisie.");
                }
            } else {
                oGrammalecte.showMessage("Erreur. Le node sur lequel vous avez cliqué n’a pas pu être identifié.");
            }
            break;
        // rescan page command
        case "rescanPage":
            oGrammalecte.rescanPage();
            break;
        default:
            console.log("[Content script] Unknown command: " + sActionDone);
    }
});


/*
    Start
*/
oGrammalecte.listenRightClick();
oGrammalecte.createMenus();
oGrammalecte.createMenus2();
