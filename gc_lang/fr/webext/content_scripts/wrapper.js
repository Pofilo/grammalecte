// JavaScript

"use strict";


class GrammalecteWrapper {

    constructor (nWrapper, xTextArea) {
        this.nWrapper = nWrapper;
        let xWrapper = createNode("div", {id: "grammalecte_wrapper" + nWrapper, className: "grammalecte_wrapper"});
        xWrapper.appendChild(this._createWrapperToolbar(xTextArea));
        this._insertAfter(xWrapper, xTextArea);
        xWrapper.style.marginBottom = xTextArea.style.marginBottom;
        xTextArea.style.marginBottom = "0px";
        xWrapper.style.width = xTextArea.style.width;
    }

    _insertAfter (xNewNode, xReferenceNode) {
        xReferenceNode.parentNode.insertBefore(xNewNode, xReferenceNode.nextSibling);
    }

    _createWrapperToolbar (xTextArea) {
        try {
            let xToolbar = createNode("div", {className: "grammalecte_wrapper_toolbar"});
            let xConjButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Conjuguer"});
            xConjButton.onclick = () => { this.showConjButtons(); };
            let xConjSection = createNode("div", {id: "grammalecte_wrapper_conj_section"+this.nWrapper, className: "grammalecte_wrapper_conj_section"});
            let xConjButtonTab = createNode("div", {className: "grammalecte_wrapper_button2", textContent: ">Onglet"});
            xConjButtonTab.onclick = function () {
                xGrammalectePort.postMessage({sCommand: "openConjugueurTab", dParam: null, dInfo: null});
                this.hideConjButtons();
            }.bind(this);
            let xConjButtonWin = createNode("div", {className: "grammalecte_wrapper_button2", textContent: ">Fenêtre"});
            xConjButtonWin.onclick = function () {
                xGrammalectePort.postMessage({sCommand: "openConjugueurWindow", dParam: null, dInfo: null});
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
                xGrammalectePort.postMessage({
                    sCommand: "getListOfTokens",
                    dParam: {sText: xTextArea.value},
                    dInfo: {sTextAreaId: xTextArea.id}
                });
            };
            let xGCButton = createNode("div", {className: "grammalecte_wrapper_button", textContent: "Corriger"});
            xGCButton.onclick = function () {
                oGrammalecte.createGCPanel();
                oGrammalecte.oGCPanel.start(xTextArea);
                oGrammalecte.oGCPanel.show();
                oGrammalecte.oGCPanel.startWaitIcon();
                xGrammalectePort.postMessage({
                    sCommand: "parseAndSpellcheck",
                    dParam: {sText: xTextArea.value, sCountry: "FR", bDebug: false, bContext: false},
                    dInfo: {sTextAreaId: xTextArea.id}
                });
            };
            // Create
            //xToolbar.appendChild(createNode("img", {scr: browser.extension.getURL("img/logo-16.png")}));
            // can’t work, due to content-script policy: https://bugzilla.mozilla.org/show_bug.cgi?id=1267027
            xToolbar.appendChild(createNode("div", {className: "grammalecte_wrapper_title", textContent: "Grammalecte"}))
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
