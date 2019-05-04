// JavaScript

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global oGrammalecte, xGrammalectePort, showError, window, document */

"use strict";


class GrammalecteButton {

    constructor (nMenu, xNode) {
        this.xNode = xNode;
        this.xButton = oGrammalecte.createNode("div", {className: "grammalecte_menu_main_button", textContent: " "});
        this.xButton.onclick = () => {
            oGrammalecte.startGCPanel(this.xNode);
            xGrammalectePort.postMessage({
                sCommand: "parseAndSpellcheck",
                dParam: {sText: this._getText(), sCountry: "FR", bDebug: false, bContext: false},
                dInfo: {sTextAreaId: this.xNode.id}
            });
        };
        this.xButton.style.zIndex = (xNode.style.zIndex.search(/^[0-9]+$/) !== -1) ? (parseInt(xNode.style.zIndex) + 1).toString() : xNode.style.zIndex;

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
        } else {
            let nMarginTop = -1 * (8 + parseInt(xStyle.marginBottom.replace('px', ''), 10));
            if (!document.getElementById("grammalecte_cssmenu")) {
                oGrammalecte.createStyle("content_scripts/menu.css", "grammalecte_cssmenu", document.head);
            }
            this._insertAfter(this.xButton, xNodeInsertAfter, nMarginTop);
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
        return (this.xNode.tagName == "TEXTAREA" || this.xNode.tagName == "INPUT") ? this.xNode.value.normalize("NFC") : this.xNode.innerText.normalize("NFC")
    }

    deleteNodes () {
        if (this.bShadow) {
            this.xShadowBtn.parentNode.removeChild(this.xShadowBtn);
        } else {
            this.xButton.parentNode.removeChild(this.xButton);
        }
    }
}
