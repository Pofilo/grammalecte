// JavaScript

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global oGrammalecte, showError, window, document */

"use strict";

class GrammalecteButton {

    constructor () {
        // the pearl button
        this.xButton = oGrammalecte.createNode("div", { className: "grammalecte_menu_main_button", textContent: " " });
        this.xButton.onclick = () => {
            if (this.xTextNode) {
                oGrammalecte.startGCPanel(this.xTextNode);
            }
        };
        // about the text node
        this.xTextNode = null;
        // read user config
        this._bTextArea = true;
        this._bEditableNode = true;
        this._bIframe = false;
        if (bChrome) {
            browser.storage.local.get("ui_options", this.setOptions.bind(this));
        } else {
            browser.storage.local.get("ui_options").then(this.setOptions.bind(this), showError);
        }
    }

    setOptions (oOptions) {
        if (oOptions.hasOwnProperty("ui_options")) {
            this._bTextArea = oOptions.ui_options.textarea;
            this._bEditableNode = oOptions.ui_options.editablenode;
        }
    }

    examineNode (xNode) {
        if (xNode && xNode instanceof HTMLElement
                && ( (xNode.tagName == "TEXTAREA" && this._bTextArea && xNode.getAttribute("spellcheck") !== "false")
                    || (xNode.isContentEditable && this._bEditableNode)
                    || (xNode.tagName == "IFRAME" && this._bIframe) )
                && xNode.style.display !== "none" && xNode.style.visibility !== "hidden"
                && !(xNode.dataset.grammalecte_button  &&  xNode.dataset.grammalecte_button == "false")) {
            this.xTextNode = xNode;
            this.show()
        }
        else {
            this.xTextNode = null;
            this.hide();
        }
    }

    show () {
        if (this.xTextNode) {
            this.xButton.style.display = "none"; // we hide it before showing it again to relaunch the animation
            let oCoord = oGrammalecte.getElementCoord(this.xTextNode);
            //console.log("top:", oCoord.left, "bottom:", oCoord.top, "left:", oCoord.bottom, "right:", oCoord.right);
            this.xButton.style.top = `${oCoord.bottom}px`;
            this.xButton.style.left = `${oCoord.left}px`;
            this.xButton.style.display = "block";
        }
    }

    hide () {
        this.xButton.style.display = "none";
    }

    insertIntoPage () {
        this.bShadow = document.body.createShadowRoot || document.body.attachShadow;
        if (this.bShadow) {
            this.xShadowBtn = oGrammalecte.createNode("div", { style: "display:none; position:absolute; width:0; height:0;" });
            this.xShadowBtnNode = this.xShadowBtn.attachShadow({ mode: "open" });
            oGrammalecte.createStyle("content_scripts/menu.css", null, this.xShadowBtnNode);
            this.xShadowBtnNode.appendChild(this.xButton);
            document.body.appendChild(this.xShadowBtnNode);
        }
        else {
            if (!document.getElementById("grammalecte_cssmenu")) {
                oGrammalecte.createStyle("content_scripts/menu.css", "grammalecte_cssmenu", document.head);
            }
            document.body.appendChild(this.xButton);
        }
    }
}
