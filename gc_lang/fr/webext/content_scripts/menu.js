// JavaScript

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global oGrammalecte, showError, window, document */

"use strict";


class GrammalecteButton {

    constructor (nMenu, xNode) {
        this.xNode = xNode;
        this.xButton = oGrammalecte.createNode("div", {className: "grammalecte_menu_main_button", textContent: " "});
        this.xButton.onclick = () => {
            oGrammalecte.startGCPanel(this.xNode);
        };
        this.xButton.style.zIndex = (xNode.style.zIndex.search(/^[0-9]+$/) !== -1) ? (parseInt(xNode.style.zIndex) + 1).toString() : xNode.style.zIndex;

        this.bShadow = document.body.createShadowRoot || document.body.attachShadow;
        if (this.bShadow) {
            this.xShadowBtn = oGrammalecte.createNode("div", {style: "display:none;position:absolute;width:0;height:0;"});
            this.xShadowBtnNode = this.xShadowBtn.attachShadow({mode: "open"});
            oGrammalecte.createStyle("content_scripts/menu.css", null, this.xShadowBtnNode);
            this.xShadowBtnNode.appendChild(this.xButton);
            this._insert(this.xShadowBtn);
        } else {
            if (!document.getElementById("grammalecte_cssmenu")) {
                oGrammalecte.createStyle("content_scripts/menu.css", "grammalecte_cssmenu", document.head);
            }
            this._insert(this.xButton);
        }
        this._listen();
    }

    _insert (xNewNode) {
        // insertion
        let xReferenceNode = this.xNode;
        if (this.xNode.classList.contains('rich-editor')) {
            xReferenceNode = this.xNode.parentNode;
        }
        xReferenceNode.parentNode.insertBefore(xNewNode, xReferenceNode.nextSibling);
        // offset
        let nNodeMarginBottom = parseInt(window.getComputedStyle(this.xNode).marginBottom.replace('px', ''), 10);
        let nMarginTop = (this.bShadow) ? -1 * nNodeMarginBottom : -1 * (8 + nNodeMarginBottom);
        xNewNode.style.marginTop = nMarginTop + "px";
    }

    _listen () {
        this.xNode.addEventListener('focus', (e) => {
            if (this.bShadow) {
                this.xShadowBtn.style.display = "block";
            }
            this.xButton.style.display = "block";
        });
        /*this.xNode.addEventListener('blur', (e) => {
            window.setTimeout(() => { this.xButton.style.display = "none"; }, 300);
        });*/
    }

    deleteNodes () {
        if (this.bShadow) {
            this.xShadowBtn.parentNode.removeChild(this.xShadowBtn);
        } else {
            this.xButton.parentNode.removeChild(this.xButton);
        }
    }
}
