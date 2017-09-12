// JavaScript

"use strict";


class GrammalecteMenu {

    constructor (nMenu, xTextArea) {
        this.sMenuId = "grammalecte_menu" + nMenu;
        let xButton = createNode("div", {className: "grammalecte_menu_main_button", textContent: " "});
        xButton.onclick = () => { this.switchMenu(); };
        let xMenu = this._createMenu(xTextArea);
        this._insertAfter(xButton, xTextArea);
        this._insertAfter(xMenu, xTextArea);
    }

    _insertAfter (xNewNode, xReferenceNode) {
        xReferenceNode.parentNode.insertBefore(xNewNode, xReferenceNode.nextSibling);
    }

    _createMenu (xTextArea) {
        try {
            let xMenu = createNode("div", {id: this.sMenuId, className: "grammalecte_menu"});
            // Text formatter
            let xTFButton = createNode("div", {className: "grammalecte_menu_item", textContent: "Formateur de texte"});
            xTFButton.onclick = () => {
            	this.switchMenu();
                oGrammalecte.createTFPanel();
                oGrammalecte.oTFPanel.start(xTextArea);
                oGrammalecte.oTFPanel.show();
            };
            // lexicographe
            let xLxgButton = createNode("div", {className: "grammalecte_menu_item", textContent: "Lexicographe"});
            xLxgButton.onclick = () => {
            	this.switchMenu();
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
            // Grammar checker
            let xGCButton = createNode("div", {className: "grammalecte_menu_item", textContent: "Correction grammaticale"});
            xGCButton.onclick = () => {
            	this.switchMenu();
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
            // Conjugation tool
            let xConjButton = createNode("div", {className: "grammalecte_menu_item_block", textContent: "Conjugueur"});
            let xConjButtonTab = createNode("div", {className: "grammalecte_menu_button", textContent: "Onglet"});
            xConjButtonTab.onclick = () => {
            	this.switchMenu();
            	xGrammalectePort.postMessage({sCommand: "openConjugueurTab", dParam: null, dInfo: null});
            };
            let xConjButtonWin = createNode("div", {className: "grammalecte_menu_button", textContent: "Fenêtre"});
            xConjButtonWin.onclick = () => {
            	this.switchMenu();
            	xGrammalectePort.postMessage({sCommand: "openConjugueurWindow", dParam: null, dInfo: null});
            };
            xConjButton.appendChild(xConjButtonTab);
            xConjButton.appendChild(xConjButtonWin);
            // Create
            xMenu.appendChild(createNode("div", {className: "grammalecte_menu_header", textContent: "GRAMMALECTE"}));
            xMenu.appendChild(xTFButton);
            xMenu.appendChild(xLxgButton);
            xMenu.appendChild(xGCButton);
            xMenu.appendChild(xConjButton);
            //xMenu.appendChild(createNode("img", {scr: browser.extension.getURL("img/logo-16.png")}));
            // can’t work, due to content-script policy: https://bugzilla.mozilla.org/show_bug.cgi?id=1267027
            xMenu.appendChild(createNode("div", {className: "grammalecte_menu_footer"}));
            return xMenu;
        }
        catch (e) {
            showError(e);
        }
    }

    switchMenu () {
    	let xMenu = document.getElementById(this.sMenuId);
        xMenu.style.display = (xMenu.style.display == "block") ? "none" : "block";
    }
}
