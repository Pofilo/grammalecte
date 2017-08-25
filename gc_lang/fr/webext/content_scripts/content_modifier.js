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


const oGrammalecte = {

    nTadId: null,
    nWrapper: 1,

    oConjPanel: null,
    oTFPanel: null,
    oLxgPanel: null,
    oGCPanel: null,

    wrapTextareas: function () {
        let lNode = document.getElementsByTagName("textarea");
        for (let xNode of lNode) {
            this._createWrapper(xNode);
        }
    },

    _createWrapper (xTextArea) {
        try {
            let xParentElement = xTextArea.parentElement;
            let xWrapper = document.createElement("div");
            xWrapper.className = "grammalecte_wrapper";
            xWrapper.id = "grammalecte_wrapper" + this.nWrapper;
            this.nWrapper += 1;
            xParentElement.insertBefore(xWrapper, xTextArea);
            xWrapper.appendChild(xTextArea); // move textarea in wrapper
            xWrapper.appendChild(this._createWrapperToolbar(xTextArea));
        }
        catch (e) {
            showError(e);
        }
    },

    _createWrapperToolbar: function (xTextArea) {
        try {
            let xToolbar = createNode("div", {className: "grammalecte_wrapper_toolbar"});
            let xConjButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Conjuguer"});
            xConjButton.onclick = function () {
                this.createConjPanel();
            }.bind(this);
            let xTFButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Formater"});
            xTFButton.onclick = function () {
                this.createTFPanel(xTextArea);
            }.bind(this);
            let xLxgButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Analyser"});
            xLxgButton.onclick = function () {
                this.createLxgPanel();
                this.oLxgPanel.startWaitIcon();
                xPort.postMessage({
                    sCommand: "getListOfTokens",
                    dParam: {sText: xTextArea.value},
                    dInfo: {sTextAreaId: xTextArea.id}
                });
            }.bind(this);
            let xGCButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Corriger"});
            xGCButton.onclick = function () {
                this.createGCPanel();
                this.oGCPanel.startWaitIcon();
                this.oGCPanel.start(xTextArea);
                xPort.postMessage({
                    sCommand: "parseAndSpellcheck",
                    dParam: {sText: xTextArea.value, sCountry: "FR", bDebug: false, bContext: false},
                    dInfo: {sTextAreaId: xTextArea.id}
                });
            }.bind(this);
            // Create
            //xToolbar.appendChild(createNode("img", {scr: browser.extension.getURL("img/logo-16.png")}));
            // can’t work, due to content-script policy: https://bugzilla.mozilla.org/show_bug.cgi?id=1267027
            //xToolbar.appendChild(createLogo());
            xToolbar.appendChild(document.createTextNode("Grammalecte"));
            xToolbar.appendChild(xConjButton);
            xToolbar.appendChild(xTFButton);
            xToolbar.appendChild(xLxgButton);
            xToolbar.appendChild(xGCButton);
            return xToolbar;
        }
        catch (e) {
            showError(e);
        }
    },

    createConjPanel: function () {
        console.log("Conjugueur");
        if (this.oConjPanel !== null) {
            this.oConjPanel.show();
        } else {
            // create the panel
            this.oConjPanel = new GrammalectePanel("grammalecte_conj_panel", "Conjugueur", 600, 600);
            this.oConjPanel.insertIntoPage();
        }
    },

    createTFPanel: function (xTextArea) {
        console.log("Formateur de texte");
        if (this.oTFPanel !== null) {
            this.oTFPanel.start(xTextArea);
            this.oTFPanel.show();
        } else {
            // create the panel
            this.oTFPanel = new GrammalecteTextFormatter("grammalecte_tf_panel", "Formateur de texte", 800, 620, false);
            this.oTFPanel.logInnerHTML();
            this.oTFPanel.start(xTextArea);
            this.oTFPanel.insertIntoPage();
        }
    },

    createLxgPanel: function () {
        console.log("Lexicographe");
        if (this.oLxgPanel !== null) {
            this.oLxgPanel.clear();
            this.oLxgPanel.show();
        } else {
            // create the panel
            this.oLxgPanel = new GrammalecteLexicographer("grammalecte_lxg_panel", "Lexicographe", 500, 700);
            this.oLxgPanel.insertIntoPage();
        }
    },

    createGCPanel: function () {
        console.log("Correction grammaticale");
        if (this.oGCPanel !== null) {
            this.oGCPanel.clear();
            this.oGCPanel.show();
        } else {
            // create the panel
            this.oGCPanel = new GrammalecteGrammarChecker("grammalecte_gc_panel", "Grammalecte", 500, 700);
            this.oGCPanel.insertIntoPage();
        }
    }
}


/*
    Connexion to the background
*/
let xPort = browser.runtime.connect({name: "content-script port"});

xPort.onMessage.addListener(function (oMessage) {
    console.log("[Content script] received…");
    let {sActionDone, result, dInfo, bEnd, bError} = oMessage;
    switch (sActionDone) {
        case "getCurrentTabId":
            console.log("[Content script] tab id: " + result);
            oGrammalecte.nTadId = result;
            break;
        case "parseAndSpellcheck":
            console.log("[content script] received: parseAndSpellcheck");
            if (!bEnd) {
                oGrammalecte.oGCPanel.addParagraphResult(result);
            } else {
                oGrammalecte.oGCPanel.stopWaitIcon();
            }
            break;
        case "parseAndSpellcheck1":
            console.log("[content script] received: parseAndSpellcheck1");
            oGrammalecte.oGCPanel.refreshParagraph(dInfo.sParagraphId, result);
            break;
        case "getListOfTokens":
            console.log("[content script] received: getListOfTokens");
            if (!bEnd) {
                oGrammalecte.oLxgPanel.addListOfTokens(result);
            } else {
                oGrammalecte.oLxgPanel.stopWaitIcon();
            }
            break;
        default:
            console.log("[Content script] Unknown command: " + sActionDone);
    }
});

xPort.postMessage({
    sCommand: "getCurrentTabId",
    dParam: {},
    dInfo: {}
});


oGrammalecte.wrapTextareas();
