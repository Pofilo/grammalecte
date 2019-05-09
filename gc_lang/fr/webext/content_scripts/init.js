// Modify page

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global GrammalectePanel, GrammalecteButton, GrammalecteTextFormatter, GrammalecteLexicographer, GrammalecteGrammarChecker, GrammalecteMessageBox, showError, MutationObserver, chrome, document, console */

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

    nButton: 0,
    lButton: [],

    oTFPanel: null,
    oGCPanel: null,

    oMessageBox: null,

    xRightClickedNode: null,

    xObserver: null,

    sExtensionUrl: null,

    oOptions: null,

    listenRightClick: function () {
        // Node where a right click is done
        // Bug report: https://bugzilla.mozilla.org/show_bug.cgi?id=1325814
        document.addEventListener('contextmenu', (xEvent) => {
            this.xRightClickedNode = xEvent.target;
        }, true);
    },

    clearRightClickedNode: function () {
        this.xRightClickedNode = null;
    },

    createButtons: function () {
        if (bChrome) {
            browser.storage.local.get("ui_options", this._createButtons.bind(this));
            return;
        }
        browser.storage.local.get("ui_options").then(this._createButtons.bind(this), showError);
    },

    _createButtons: function (oOptions) {
        if (oOptions.hasOwnProperty("ui_options")) {
            this.oOptions = oOptions.ui_options;
            if (this.oOptions.textarea) {
                for (let xNode of document.getElementsByTagName("textarea")) {
                    if (xNode.style.display !== "none" && xNode.style.visibility !== "hidden" && xNode.getAttribute("spellcheck") !== "false") {
                        this.lButton.push(new GrammalecteButton(this.nButton, xNode));
                        this.nButton += 1;
                    }
                }
            }
            if (this.oOptions.editablenode) {
                for (let xNode of document.querySelectorAll("[contenteditable]")) {
                    this.lButton.push(new GrammalecteButton(this.nButton, xNode));
                    this.nButton += 1;
                }
            }
        }
    },

    observePage: function () {
        // When a textarea is added via jascript we add the menu
        let that = this;
        this.xObserver = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                for (let i = 0;  i < mutation.addedNodes.length;  i++){
                    if (mutation.addedNodes[i].tagName == "TEXTAREA") {
                        if (that.oOptions === null || that.oOptions.textarea) {
                            oGrammalecte.lButton.push(new GrammalecteButton(oGrammalecte.nButton, mutation.addedNodes[i]));
                            oGrammalecte.nButton += 1;
                        }
                    } else if (mutation.addedNodes[i].getElementsByTagName) {
                        if (that.oOptions === null || that.oOptions.textarea) {
                            for (let xNode of mutation.addedNodes[i].getElementsByTagName("textarea")) {
                                oGrammalecte.lButton.push(new GrammalecteButton(oGrammalecte.nButton, xNode));
                                oGrammalecte.nButton += 1;
                            }
                        }
                    }
                }
            });
        });
        this.xObserver.observe(document.body, { childList: true, subtree: true });
    },

    rescanPage: function () {
        if (this.oTFPanel !== null) { this.oTFPanel.hide(); }
        if (this.oGCPanel !== null) { this.oGCPanel.hide(); }
        for (let oMenu of this.lButton) {
            oMenu.deleteNodes();
        }
        this.lButton.length = 0; // to clear an array
        this.listenRightClick();
        this.createButtons();
    },

    createTFPanel: function () {
        if (this.oTFPanel === null) {
            this.oTFPanel = new GrammalecteTextFormatter("grammalecte_tf_panel", "Formateur de texte", 760, 595, false);
            this.oTFPanel.insertIntoPage();
            window.setTimeout( () => { this.oTFPanel.adjustHeight(); }, 50);
        }
    },

    createGCPanel: function () {
        if (this.oGCPanel === null) {
            this.oGCPanel = new GrammalecteGrammarChecker("grammalecte_gc_panel", "Grammalecte", 540, 700);
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
        this.oGCPanel.showEditor();
        this.oGCPanel.start(xNode);
        this.oGCPanel.startWaitIcon();
    },

    showMessage: function (sMessage) {
        this.createMessageBox();
        this.oMessageBox.show();
        this.oMessageBox.setMessage(sMessage);
    },

    parseAndSpellcheck (xNode=null) {
        this.startGCPanel(xNode);
        let sText = "";
        if (xNode) {
            sText = (xNode.tagName == "TEXTAREA" || xNode.tagName == "INPUT") ? xNode.value.normalize("NFC") : xNode.innerText.normalize("NFC");
        } else {
            sText = this.getPageText();
        }
        xGrammalectePort.postMessage({
            sCommand: "parseAndSpellcheck",
            dParam: {sText: sText, sCountry: "FR", bDebug: false, bContext: false},
            dInfo: (xNode) ? {sTextAreaId: xNode.id} : {}
        });
    },

    getPageText: function () {
        let sPageText = document.body.innerText;
        let nPos = sPageText.indexOf("__grammalecte_panel__");
        if (nPos >= 0) {
            sPageText = sPageText.slice(0, nPos).normalize("NFC");
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
    },

    getCaretPosition (xElement) {
        // JS awfulness again.
        // recepie from https://stackoverflow.com/questions/4811822/get-a-ranges-start-and-end-offsets-relative-to-its-parent-container
        let nCaretOffsetStart = 0;
        let nCaretOffsetEnd = 0;
        let xSelection = window.getSelection();
        if (xSelection.rangeCount > 0) {
            let xRange = xSelection.getRangeAt(0);
            let xPreCaretRange = xRange.cloneRange();
            xPreCaretRange.selectNodeContents(xElement);
            xPreCaretRange.setEnd(xRange.endContainer, xRange.endOffset);
            nCaretOffsetStart = xPreCaretRange.toString().length;
            nCaretOffsetEnd = nCaretOffsetStart + xRange.toString().length;
        }
        return [nCaretOffsetStart, nCaretOffsetEnd];
        // for later: solution with multilines text
        // https://stackoverflow.com/questions/4811822/get-a-ranges-start-and-end-offsets-relative-to-its-parent-container/4812022
    },

    setCaretPosition (xElement, nCaretOffsetStart, nCaretOffsetEnd) {
        // JS awfulness again.
        // recipie from https://stackoverflow.com/questions/6249095/how-to-set-caretcursor-position-in-contenteditable-element-div
        let iChar = 0;
        let xRange = document.createRange();
        xRange.setStart(xElement, 0);
        xRange.collapse(true);

        let lNode = [xElement];
        let xNode;
        let bFoundStart = false;
        let bStop = false;
        while (!bStop && (xNode = lNode.pop())) {
            if (xNode.nodeType == 3) { // Node.TEXT_NODE
                let iNextChar = iChar + xNode.length;
                if (!bFoundStart && nCaretOffsetStart >= iChar && nCaretOffsetStart <= iNextChar) {
                    xRange.setStart(xNode, nCaretOffsetStart - iChar);
                    bFoundStart = true;
                }
                if (bFoundStart && nCaretOffsetEnd >= iChar && nCaretOffsetEnd <= iNextChar) {
                    xRange.setEnd(xNode, nCaretOffsetEnd - iChar);
                    bStop = true;
                }
                iChar = iNextChar;
            } else {
                let i = xNode.childNodes.length;
                while (i--) {
                    lNode.push(xNode.childNodes[i]);
                }
            }
        }
        let xSelection = window.getSelection();
        xSelection.removeAllRanges();
        xSelection.addRange(xRange);
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
            oGrammalecte.createButtons();
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
                oGrammalecte.oGCPanel.addListOfTokens(result);
            } else {
                oGrammalecte.oGCPanel.stopWaitIcon();
            }
            break;
        case "getSpellSuggestions":
            oGrammalecte.oGCPanel.oTooltip.setSpellSuggestionsFor(result.sWord, result.aSugg, result.iSuggBlock, dInfo.sErrorId);
            break;
        case "getVerb":
            if (dInfo.bStart) {
                oGrammalecte.oGCPanel.conjugateWith(result.oVerb, result.oConjTable);
            } else {
                oGrammalecte.oGCPanel.displayConj(result.oConjTable);
            }
            break;
        /*
            Commands received from the context menu
            (Context menu are initialized in background)
        */
        // Grammar checker commands
        case "grammar_checker_editable":
            if (oGrammalecte.xRightClickedNode !== null) {
                oGrammalecte.parseAndSpellcheck(oGrammalecte.xRightClickedNode);
            } else {
                oGrammalecte.showMessage("Erreur. Le node sur lequel vous avez cliqué n’a pas pu être identifié. Sélectionnez le texte à corriger et relancez le correcteur via le menu contextuel.");
            }
            break;
        case "grammar_checker_page":
            oGrammalecte.parseAndSpellcheck();
            break;
        case "grammar_checker_selection":
            oGrammalecte.startGCPanel();
            // selected text is sent to the GC worker in the background script.
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
        case "shortcutGrammarChecker":
            if (xActiveNode && (xActiveNode.tagName == "TEXTAREA" || xActiveNode.tagName == "INPUT" || xActiveNode.isContentEditable)) {
                oGrammalecte.parseAndSpellcheck(xActiveNode);
            } else {
                oGrammalecte.parseAndSpellcheck();
            }
            break;
        default:
            console.log("[Content script] Unknown command: " + sActionDone);
    }
});
