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


class GrammalecteWrapper {

    constructor (nWrapper, xTextArea) {
        this.nWrapper = nWrapper;
        let xParentElement = xTextArea.parentElement;
        let xWrapper = createNode("div", {id: "grammalecte_wrapper" + nWrapper, className: "grammalecte_wrapper"});
        xParentElement.insertBefore(xWrapper, xTextArea);
        xWrapper.appendChild(this._createTitle());
        xWrapper.appendChild(xTextArea); // move textarea in wrapper
        xWrapper.appendChild(this._createWrapperToolbar(xTextArea));
    }

    _createTitle () {
        return createNode("div", {className: "grammalecte_wrapper_title", textContent: "Grammalecte"});
    }

    _createWrapperToolbar (xTextArea) {
        try {
            let xToolbar = createNode("div", {className: "grammalecte_wrapper_toolbar"});
            let xConjButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Conjuguer"});
            xConjButton.onclick = () => { this.showConjButtons(); };
            let xConjSection = createNode("div", {id: "grammalecte_wrapper_conj_section"+this.nWrapper, className: "grammalecte_wrapper_conj_section"});
            let xConjButtonTab = createNode("div", {className: "grammalecte_wrapper_button2", textContent: ">Onglet"});
            xConjButtonTab.onclick = function () {
                xPort.postMessage({sCommand: "openConjugueurTab", dParam: null, dInfo: null});
                this.hideConjButtons();
            }.bind(this);
            let xConjButtonWin = createNode("div", {className: "grammalecte_wrapper_button2", textContent: ">Fenêtre"});
            xConjButtonWin.onclick = function () {
                xPort.postMessage({sCommand: "openConjugueurWindow", dParam: null, dInfo: null});
                this.hideConjButtons();
            }.bind(this);
            let xTFButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Formater"});
            xTFButton.onclick = function () {
                oGrammalecte.createTFPanel();
                oGrammalecte.oTFPanel.start(xTextArea);
                oGrammalecte.oTFPanel.show();
            };
            let xLxgButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Analyser"});
            xLxgButton.onclick = function () {
                oGrammalecte.createLxgPanel();
                oGrammalecte.oLxgPanel.clear();
                oGrammalecte.oLxgPanel.show();
                oGrammalecte.oLxgPanel.startWaitIcon();
                xPort.postMessage({
                    sCommand: "getListOfTokens",
                    dParam: {sText: xTextArea.value},
                    dInfo: {sTextAreaId: xTextArea.id}
                });
            };
            let xGCButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Corriger"});
            xGCButton.onclick = function () {
                oGrammalecte.createGCPanel();
                oGrammalecte.oGCPanel.clear();
                oGrammalecte.oGCPanel.show();
                oGrammalecte.oGCPanel.start(xTextArea);
                oGrammalecte.oGCPanel.startWaitIcon();
                xPort.postMessage({
                    sCommand: "parseAndSpellcheck",
                    dParam: {sText: xTextArea.value, sCountry: "FR", bDebug: false, bContext: false},
                    dInfo: {sTextAreaId: xTextArea.id}
                });
            };
            // Create
            //xToolbar.appendChild(createNode("img", {scr: browser.extension.getURL("img/logo-16.png")}));
            // can’t work, due to content-script policy: https://bugzilla.mozilla.org/show_bug.cgi?id=1267027
            //xToolbar.appendChild(createLogo());
            xToolbar.appendChild(xConjButton);
            xConjSection.appendChild(xConjButtonTab);
            xConjSection.appendChild(xConjButtonWin);
            xToolbar.appendChild(xConjSection);
            xToolbar.appendChild(xTFButton);
            xToolbar.appendChild(xLxgButton);
            xToolbar.appendChild(xGCButton);
            return xToolbar;
        }
        catch (e) {
            showError(e);
        }
    }

    showConjButtons () {
        document.getElementById("grammalecte_wrapper_conj_section"+this.nWrapper).style.display = "block";
    }

    hideConjButtons () {
        document.getElementById("grammalecte_wrapper_conj_section"+this.nWrapper).style.display = "none";
    }
}


const oGrammalecte = {

    nWrapper: 0,
    lWrapper: [],

    oTFPanel: null,
    oLxgPanel: null,
    oGCPanel: null,

    wrapTextareas: function () {
        let lNode = document.getElementsByTagName("textarea");
        for (let xNode of lNode) {
            this.lWrapper.push(new GrammalecteWrapper(this.nWrapper, xNode));
            this.nWrapper += 1;
        }
    },

    createTFPanel: function () {
        if (this.oTFPanel === null) {
            this.oTFPanel = new GrammalecteTextFormatter("grammalecte_tf_panel", "Formateur de texte", 800, 620, false);
            //this.oTFPanel.logInnerHTML();
            this.oTFPanel.insertIntoPage();
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
            //this.oGCPanel.logInnerHTML();
            this.oGCPanel.insertIntoPage();
        }
    }
}


/*
    Connexion to the background
*/
let xPort = browser.runtime.connect({name: "content-script port"});

xPort.onMessage.addListener(function (oMessage) {
    let {sActionDone, result, dInfo, bEnd, bError} = oMessage;
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
        // Design WTF: context menus are made in background, not in content-script.
        // Commands from context menu received here to initialize panels
        case "openGCPanel":
            oGrammalecte.createGCPanel();
            oGrammalecte.oGCPanel.clear();
            oGrammalecte.oGCPanel.show();
            oGrammalecte.oGCPanel.start();
            oGrammalecte.oGCPanel.startWaitIcon();
            break;
        case "openLxgPanel":
            oGrammalecte.createLxgPanel();
            oGrammalecte.oLxgPanel.clear();
            oGrammalecte.oLxgPanel.show();
            oGrammalecte.oLxgPanel.startWaitIcon();
            break;
        default:
            console.log("[Content script] Unknown command: " + sActionDone);
    }
});


/*
    Start
*/
oGrammalecte.wrapTextareas();
