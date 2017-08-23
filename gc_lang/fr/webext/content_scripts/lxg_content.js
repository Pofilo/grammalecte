// JavaScript

"use strict";

class GrammalecteLexicographer extends GrammalectePanel {

    constructor (...args) {
        super(...args);
        this._nCount = 0;
        this._xContentNode = createNode("div", {id: "grammalecte_lxg_panel_content"});
        this.xPanelContent.appendChild(this._xContentNode);
    }

    clear () {
        this._nCount = 0;
        while (this._xContentNode.firstChild) {
            this._xContentNode.removeChild(this._xContentNode.firstChild);
        }
    }

    addSeparator (sText) {
        if (this._xContentNode.textContent !== "") {
            this._xContentNode.appendChild(createNode("div", {className: "grammalecte_lxg_separator", textContent: sText}));
        }
    }

    addMessage (sClass, sText) {
        this._xContentNode.appendChild(createNode("div", {className: sClass, textContent: sText}));
    }

    addListOfTokens (lTokens) {
        try {
            if (lTokens) {
                this._nCount += 1;
                let xNodeDiv = createNode("div", {className: "grammalecte_lxg_list_of_tokens"});
                xNodeDiv.appendChild(createNode("div", {className: "num", textContent: this._nCount}));
                for (let oToken of lTokens) {
                    xNodeDiv.appendChild(this._createTokenNode(oToken));
                }
                this._xContentNode.appendChild(xNodeDiv);
            }
        }
        catch (e) {
            showError(e);
        }
    }

    _createTokenNode (oToken) {
        let xTokenNode = createNode("div", {className: "grammalecte_token"});
        xTokenNode.appendChild(createNode("b", {className: oToken.sType, textContent: oToken.sValue}));
        xTokenNode.appendChild(createNode("s", {textContent: " : "}));
        if (oToken.aLabel.length === 1) {
            xTokenNode.appendChild(document.createTextNode(oToken.aLabel[0]));
        } else {
            let xTokenList = document.createElement("ul");
            for (let sLabel of oToken.aLabel) {
                xTokenList.appendChild(createNode("li", {textContent: sLabel}));
            }
            xTokenNode.appendChild(xTokenList);
        }
        return xTokenNode;
    }

    setHidden (sClass, bHidden) {
        for (let xNode of document.getElementsByClassName(sClass)) {
            xNode.hidden = bHidden;
        }
    }
}
