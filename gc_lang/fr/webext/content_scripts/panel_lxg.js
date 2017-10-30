// JavaScript

"use strict";

class GrammalecteLexicographer extends GrammalectePanel {

    constructor (...args) {
        super(...args);
        this._nCount = 0;
        this._xContentNode = oGrammalecte.createNode("div", {id: "grammalecte_lxg_panel_content"});
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
            this._xContentNode.appendChild(oGrammalecte.createNode("div", {className: "grammalecte_lxg_separator", textContent: sText}));
        }
    }

    addMessage (sMessage) {
        let xNode = oGrammalecte.createNode("div", {className: "grammalecte_panel_message", textContent: sMessage});
        this._xContentNode.appendChild(xNode);
    }

    addListOfTokens (lToken) {
        try {
            if (lToken) {
                this._nCount += 1;
                let xTokenList = oGrammalecte.createNode("div", {className: "grammalecte_lxg_list_of_tokens"});
                xTokenList.appendChild(oGrammalecte.createNode("div", {className: "grammalecte_lxg_list_num", textContent: this._nCount}));
                for (let oToken of lToken) {
                    xTokenList.appendChild(this._createTokenBlock(oToken));
                }
                this._xContentNode.appendChild(xTokenList);
            }
        }
        catch (e) {
            showError(e);
        }
    }

    _createTokenBlock (oToken) {
        let xTokenBlock = oGrammalecte.createNode("div", {className: "grammalecte_lxg_token_block"});
        xTokenBlock.appendChild(this._createTokenDescr(oToken));
        if (oToken.aSubElem) {
            let xSubBlock = oGrammalecte.createNode("div", {className: "grammalecte_lxg_token_subblock"});
            for (let oSubElem of oToken.aSubElem) {
                xSubBlock.appendChild(this._createTokenDescr(oSubElem));
            }
            xTokenBlock.appendChild(xSubBlock);
        }
        return xTokenBlock;
    }

    _createTokenDescr (oToken) {
        try {
            let xTokenDescr = oGrammalecte.createNode("div", {className: "grammalecte_lxg_token_descr"});
            xTokenDescr.appendChild(oGrammalecte.createNode("div", {className: "grammalecte_lxg_token grammalecte_lxg_token_" + oToken.sType, textContent: oToken.sValue}));
            xTokenDescr.appendChild(oGrammalecte.createNode("div", {className: "grammalecte_lxg_token_colon", textContent: ":"}));
            if (oToken.aLabel.length === 1) {
                xTokenDescr.appendChild(document.createTextNode(oToken.aLabel[0]));
            } else {
                let xMorphList = oGrammalecte.createNode("div", {className: "grammalecte_lxg_morph_list"});
                for (let sLabel of oToken.aLabel) {
                    xMorphList.appendChild(oGrammalecte.createNode("div", {className: "grammalecte_lxg_morph_elem", textContent: "• " + sLabel}));
                }
                xTokenDescr.appendChild(xMorphList);
            }
            return xTokenDescr;
        }
        catch (e) {
            showError(e);
        }
    }

    setHidden (sClass, bHidden) {
        for (let xNode of document.getElementsByClassName(sClass)) {
            xNode.hidden = bHidden;
        }
    }
}
