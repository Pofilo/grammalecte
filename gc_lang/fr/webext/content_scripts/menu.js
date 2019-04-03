// JavaScript

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global oGrammalecte, xGrammalectePort, showError, window, document */

"use strict";


class GrammalecteMenu {

    constructor (nMenu, xNode) {
        this.xNode = xNode;
        this.sMenuId = "grammalecte_menu" + nMenu;
        this.xButton = oGrammalecte.createNode("div", {className: "grammalecte_menu_main_button", textContent: " "});
        this.xButton.onclick = () => { this.switchMenu(); };
        this.xButton.style.zIndex = (xNode.style.zIndex.search(/^[0-9]+$/) !== -1) ? (parseInt(xNode.style.zIndex) + 1).toString() : xNode.style.zIndex;
        this.xMenu = this._createMenu();

        let xStyle = window.getComputedStyle(this.xNode);

        let xNodeInsertAfter = this.xNode;
        if (document.location.host == "twitter.com" && this.xNode.classList.contains('rich-editor')) {
            xNodeInsertAfter = this.xNode.parentNode;
        }

        this.bShadow = document.body.createShadowRoot || document.body.attachShadow;
        if (this.bShadow) {
            let nMarginTop = -1 * (parseInt(xStyle.marginBottom.replace('px', ''), 10));
            this.xShadowBtn = oGrammalecte.createNode("div", {style: "display:none;position:absolute;width:0;height:0;"});
            this.xShadowBtnNode = this.xShadowBtn.attachShadow({mode: "open"});
            oGrammalecte.createStyle("content_scripts/menu.css", null, this.xShadowBtnNode);
            this.xShadowBtnNode.appendChild(this.xButton);
            this._insertAfter(this.xShadowBtn, xNodeInsertAfter, nMarginTop);

            this.xShadowMenu = oGrammalecte.createNode("div", {id: this.sMenuId+"_shadow", style: "display:none;position:absolute;width:0;height:0;"});
            this.xShadowMenuNode = this.xShadowMenu.attachShadow({mode: "open"});
            oGrammalecte.createStyle("content_scripts/menu.css", null, this.xShadowMenuNode);
            this.xShadowMenuNode.appendChild(this.xMenu);
            this._insertAfter(this.xShadowMenu, xNodeInsertAfter, nMarginTop + 8);
        } else {
            let nMarginTop = -1 * (8 + parseInt(xStyle.marginBottom.replace('px', ''), 10));
            if (!document.getElementById("grammalecte_cssmenu")) {
                oGrammalecte.createStyle("content_scripts/menu.css", "grammalecte_cssmenu", document.head);
            }
            this._insertAfter(this.xButton, xNodeInsertAfter, nMarginTop);
            this._insertAfter(this.xMenu, xNodeInsertAfter, nMarginTop + 8);
        }
        this._createListeners();
    }

    _insertAfter (xNewNode, xReferenceNode, nMarginTop) {
        xReferenceNode.parentNode.insertBefore(xNewNode, xReferenceNode.nextSibling);
        xNewNode.style.marginTop = nMarginTop + "px";
    }

    _createListeners () {
        this.xNode.addEventListener('focus', (e) => {
            if (this.bShadow) {
                this.xShadowBtn.style.display = "block";
            }
            this.xButton.style.display = "block";
        });
        /*this.xNode.addEventListener('blur', (e) => {
            window.setTimeout(() => {this.xButton.style.display = "none";}, 300);
        });*/
    }

    _getText () {
        return (this.xNode.tagName == "TEXTAREA") ? this.xNode.value.normalize("NFC") : this.xNode.innerText.normalize("NFC");
    }

    _createMenu () {
        try {
            let xMenu = oGrammalecte.createNode("div", {id: this.sMenuId, className: "grammalecte_menu"});
            let xCloseButton = oGrammalecte.createNode("div", {className: "grammalecte_menu_close_button", textContent: "×"} );
            xCloseButton.onclick = () => {
                if (this.bShadow){
                    this.xShadowBtn.style.display = "none";
                }
                this.xButton.style.display = "none";
                this.switchMenu();
            }
            xMenu.appendChild(xCloseButton);
            xMenu.appendChild(oGrammalecte.createNode("div", {className: "grammalecte_menu_header", textContent: "GRAMMALECTE"}));
            // Text formatter
            if (this.xNode.tagName == "TEXTAREA") {
                let xTFButton = oGrammalecte.createNode("div", {className: "grammalecte_menu_item", textContent: "Formateur de texte"});
                xTFButton.onclick = () => {
                    this.switchMenu();
                    oGrammalecte.createTFPanel();
                    oGrammalecte.oTFPanel.start(this.xNode);
                    oGrammalecte.oTFPanel.show();
                };
                xMenu.appendChild(xTFButton);
            }
            // lexicographe
            let xLxgButton = oGrammalecte.createNode("div", {className: "grammalecte_menu_item", textContent: "Lexicographe"});
            xLxgButton.onclick = () => {
                this.switchMenu();
                oGrammalecte.startLxgPanel();
                xGrammalectePort.postMessage({
                    sCommand: "getListOfTokens",
                    dParam: {sText: this._getText()},
                    dInfo: {sTextAreaId: this.xNode.id}
                });
            };
            xMenu.appendChild(xLxgButton);
            // Grammar checker
            let xGCButton = oGrammalecte.createNode("div", {className: "grammalecte_menu_item", textContent: "Correction grammaticale"});
            xGCButton.onclick = () => {
                this.switchMenu();
                oGrammalecte.startGCPanel(this.xNode);
                xGrammalectePort.postMessage({
                    sCommand: "parseAndSpellcheck",
                    dParam: {sText: this._getText(), sCountry: "FR", bDebug: false, bContext: false},
                    dInfo: {sTextAreaId: this.xNode.id}
                });
            };
            xMenu.appendChild(xGCButton);
            // Lexicon editor
            let xLEButton = oGrammalecte.createNode("div", {className: "grammalecte_menu_item", textContent: "Éditeur lexical"});
            xLEButton.onclick = () => {
                this.switchMenu();
                xGrammalectePort.postMessage({sCommand: "openLexiconEditor", dParam: null, dInfo: null});
            };
            xMenu.appendChild(xLEButton);
            // Conjugation tool
            let xConjButton = oGrammalecte.createNode("div", {className: "grammalecte_menu_item_block", textContent: "Conjugueur"});
            let xConjButtonTab = oGrammalecte.createNode("div", {className: "grammalecte_menu_button", textContent: "Onglet"});
            xConjButtonTab.onclick = () => {
                this.switchMenu();
                xGrammalectePort.postMessage({sCommand: "openConjugueurTab", dParam: null, dInfo: null});
            };
            let xConjButtonWin = oGrammalecte.createNode("div", {className: "grammalecte_menu_button", textContent: "Fenêtre"});
            xConjButtonWin.onclick = () => {
                this.switchMenu();
                xGrammalectePort.postMessage({sCommand: "openConjugueurWindow", dParam: null, dInfo: null});
            };
            xConjButton.appendChild(xConjButtonTab);
            xConjButton.appendChild(xConjButtonWin);
            xMenu.appendChild(xConjButton);
            //xMenu.appendChild(oGrammalecte.createNode("img", {scr: browser.extension.getURL("img/logo-16.png")}));
            // can’t work, due to content-script policy: https://bugzilla.mozilla.org/show_bug.cgi?id=1267027
            xMenu.appendChild(oGrammalecte.createNode("div", {className: "grammalecte_menu_footer"}));
            return xMenu;
        }
        catch (e) {
            showError(e);
        }
    }

    deleteNodes () {
        if (this.bShadow) {
            this.xShadowMenu.parentNode.removeChild(this.xShadowMenu);
            this.xShadowBtn.parentNode.removeChild(this.xShadowBtn);
        } else {
            this.xMenu.parentNode.removeChild(this.xMenu);
            this.xButton.parentNode.removeChild(this.xButton);
        }
    }

    switchMenu () {
        if (this.bShadow) {
            this.xShadowMenu.style.display = (this.xShadowMenu.style.display == "block") ? "none" : "block";
        }
        this.xMenu.style.display = (this.xMenu.style.display == "block") ? "none" : "block";
    }
}
