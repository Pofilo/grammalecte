// Modify page

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global GrammalectePanel, GrammalecteMenu, GrammalecteTextFormatter, GrammalecteLexicographer, GrammalecteGrammarChecker, GrammalecteMessageBox, showError, MutationObserver, chrome, document, console */

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

    xObserver: null,

    sExtensionUrl: null,

    oOptions: null,

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
        if (bChrome) {
            browser.storage.local.get("ui_options", this._createMenus.bind(this));
            return;
        }
        browser.storage.local.get("ui_options").then(this._createMenus.bind(this), showError);
    },

    _createMenus: function (oOptions) {
        if (oOptions.hasOwnProperty("ui_options")) {
            this.oOptions = oOptions.ui_options;
            if (this.oOptions.textarea) {
                for (let xNode of document.getElementsByTagName("textarea")) {
                    if (xNode.style.display !== "none" && xNode.style.visibility !== "hidden" && xNode.getAttribute("spellcheck") !== "false") {
                        this.lMenu.push(new GrammalecteMenu(this.nMenu, xNode));
                        this.nMenu += 1;
                    }
                }
            }
            if (this.oOptions.editablenode) {
                for (let xNode of document.querySelectorAll("[contenteditable]")) {
                    this.lMenu.push(new GrammalecteMenu(this.nMenu, xNode));
                    this.nMenu += 1;
                }
            }
        }
    },

    observePage: function () {
        //    When a textarea is added via jascript we add the menu
        let that = this;
        let that = this;
        this.xObserver = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                for (let i = 0;  i < mutation.addedNodes.length;  i++){
                    if (mutation.addedNodes[i].tagName == "TEXTAREA") {
                        if (that.oOptions === null || that.oOptions.textarea) {
                            oGrammalecte.lMenu.push(new GrammalecteMenu(oGrammalecte.nMenu, mutation.addedNodes[i]));
                            oGrammalecte.nMenu += 1;
                        }
                    } else if (mutation.addedNodes[i].getElementsByTagName) {
                        if (that.oOptions === null || that.oOptions.textarea) {
                            for (let xNode of mutation.addedNodes[i].getElementsByTagName("textarea")) {
                                oGrammalecte.lMenu.push(new GrammalecteMenu(oGrammalecte.nMenu, xNode));
                                oGrammalecte.nMenu += 1;
                            }
                        }
                    }
                }
            });
        });
        this.xObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
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
    },

    createTFPanel: function () {
        if (this.oTFPanel === null) {
            this.oTFPanel = new GrammalecteTextFormatter("grammalecte_tf_panel", "Formateur de texte", 760, 615, false);
            //this.oTFPanel.logInnerHTML();
            this.oTFPanel.insertIntoPage();
            window.setTimeout(function(self){
                self.oTFPanel.adjustHeight();
            }, 50, this);
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
            this.oMessageBox = new GrammalecteMessageBox("grammalecte_message_box", "Grammalecte");
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
        this.oMessageBox.setMessage(sMessage);
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
    },

    createStyle: function (sLinkCss, sLinkId=null, xNodeToAppendTo=null) {
        try {
            let xNode = document.createElement("link");
            Object.assign(xNode, {
                rel: "stylesheet",
                type: "text/css",
                media: "all",
                href: this.sExtensionUrl + sLinkCss
            });
            if (sLinkId) {
                Object.assign(xNode, {id: sLinkId});
            }
            if (xNodeToAppendTo) {
                xNodeToAppendTo.appendChild(xNode);
            }
            return xNode;
        }
        catch (e) {
            showError(e);
        }
    }
};


/*
    Connexion to the background
*/
let xGrammalectePort = browser.runtime.connect({name: "content-script port"});

xGrammalectePort.onMessage.addListener(function (oMessage) {
    let {sActionDone, result, dInfo, bEnd, bError} = oMessage;
    switch (sActionDone) {
        case "init":
            oGrammalecte.sExtensionUrl = oMessage.sUrl;
            // Start
            oGrammalecte.listenRightClick();
            oGrammalecte.createMenus();
            oGrammalecte.observePage();
            break;
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
            oGrammalecte.oGCPanel.oTooltip.setSpellSuggestionsFor(result.sWord, result.aSugg, result.iSuggBlock, dInfo.sErrorId);
            break;
        /*
            Commands received from the context menu
            (Context menu are initialized in background)
        */
        // Grammar checker commands
        case "rightClickGCEditableNode":
            if (oGrammalecte.xRightClickedNode !== null) {
                parseAndSpellcheckEditableNode(oGrammalecte.xRightClickedNode);
            } else {
                oGrammalecte.showMessage("Erreur. Le node sur lequel vous avez cliqué n’a pas pu être identifié. Sélectionnez le texte à corriger et relancez le correcteur via le menu contextuel.");
            }
            break;
        case "rightClickGCPage":
            parseAndSpellcheckPage();
            break;
        case "rightClickGCSelectedText":
            oGrammalecte.startGCPanel();
            // selected text is sent to the GC worker in the background script.
            break;
        // Lexicographer commands
        case "rightClickLxgEditableNode":
            if (oGrammalecte.xRightClickedNode !== null) {
                lexicographerEditableNode(oGrammalecte.xRightClickedNode);
            } else {
                oGrammalecte.showMessage("Erreur. Le node sur lequel vous avez cliqué n’a pas pu être identifié. Sélectionnez le texte à analyser et relancez le lexicographe via le menu contextuel.");
            }
            break;
        case "rightClickLxgPage":
            lexicographerPage();
            break;
        case "rightClickLxgSelectedText":
            oGrammalecte.startLxgPanel();
            // selected text is sent to the GC worker in the background script.
            break;
        // Text formatter command
        case "rightClickTFEditableNode":
            if (oGrammalecte.xRightClickedNode !== null) {
                if (oGrammalecte.xRightClickedNode.tagName == "TEXTAREA" || oGrammalecte.xRightClickedNode.tagName == "INPUT") {
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

    }
});


/*
    Other messages from background
*/
browser.runtime.onMessage.addListener(function (oMessage) {
    let {sActionRequest} = oMessage;
    let xActiveNode = document.activeElement;
    switch (sActionRequest) {
        /*
            Commands received from the keyboard (shortcuts)
        */
        case "shortcutLexicographer":
            if (xActiveNode && (xActiveNode.tagName == "TEXTAREA" || xActiveNode.tagName == "INPUT")) {
                lexicographerEditableNode(xActiveNode);
            } else {
                lexicographerPage();
            }
            break;
        case "shortcutTextFormatter":
            if (xActiveNode && (xActiveNode.tagName == "TEXTAREA" || xActiveNode.tagName == "INPUT")) {
                oGrammalecte.startFTPanel(xActiveNode);
            }
            break;
        case "shortcutGrammarChecker":
            if (xActiveNode && (xActiveNode.tagName == "TEXTAREA" || xActiveNode.tagName == "INPUT")) {
                parseAndSpellcheckEditableNode(xActiveNode);
            } else {
                parseAndSpellcheckPage();
            }
            break;
        default:
            console.log("[Content script] Unknown command: " + sActionDone);
    }
});


/*
    Actions
*/

function parseAndSpellcheckPage () {
    oGrammalecte.startGCPanel();
    xGrammalectePort.postMessage({
        sCommand: "parseAndSpellcheck",
        dParam: {sText: oGrammalecte.getPageText(), sCountry: "FR", bDebug: false, bContext: false},
        dInfo: {}
    });
}

function parseAndSpellcheckEditableNode (xNode) {
    oGrammalecte.startGCPanel(xNode);
    let sText = (xNode.tagName == "TEXTAREA" || xNode.tagName == "INPUT") ? xNode.value : xNode.innerText;
    xGrammalectePort.postMessage({
        sCommand: "parseAndSpellcheck",
        dParam: {sText: sText, sCountry: "FR", bDebug: false, bContext: false},
        dInfo: {sTextAreaId: xNode.id}
    });
}

function lexicographerPage () {
    oGrammalecte.startLxgPanel();
    xGrammalectePort.postMessage({
        sCommand: "getListOfTokens",
        dParam: {sText: oGrammalecte.getPageText()},
        dInfo: {}
    });
}

function lexicographerEditableNode (xNode) {
    oGrammalecte.startLxgPanel();
    let sText = (xNode.tagName == "TEXTAREA" || xNode.tagName == "INPUT") ? xNode.value : xNode.innerText;
    xGrammalectePort.postMessage({
        sCommand: "getListOfTokens",
        dParam: {sText: sText},
        dInfo: {sTextAreaId: xNode.id}
    });
}
