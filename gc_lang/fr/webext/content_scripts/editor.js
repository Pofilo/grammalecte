// JavaScript

// Editor for HTML page


"use strict";


class HTMLPageEditor {

	constructor (xRootNode=document.rootElement, bCheckSignature=false) {
        this.xRootNode = xRootNode;
        this.lNode = [];
        this.bCheckSignature = bCheckSignature;
        this._lParsableNodes = ["P", "LI"];
        this._lRootNodes = ["DIV", "UL", "OL"];

    }

    * _getParsableNodes (xRootNode) {
        // recursive function
        try {
            for (let xNode of this.xRootNode.childNodes) {
                if (xNode.className !== "moz-cite-prefix" && xNode.tagName !== "BLOCKQUOTE"
                    && (xNode.nodeType == Node.TEXT_NODE || (xNode.nodeType == Node.ELEMENT_NODE && !xNode.textContent.startsWith(">")))
                    && xNode.textContent !== "") {
                    if (xNode.tagName === undefined) {
                        if (!this.bCheckSignature && xNode.textContent.startsWith("-- ")) {
                            break;
                        }
                        yield xNode;
                    }
                    else if (this._lParsableNodes.includes(xNode.tagName)) {
                        yield xNode;
                    }
                    else if (this._lRootNodes.includes(xNode.tagName)) {
                        yield* this._getParsableNodes(xNode);
                    }
                }
            }
        }
        catch (e) {
            showError(e);
        }
    }

    * getParagraphs () {
        try {
            let i = 0;
            for (let xNode of this._getParsableNodes()) {
                this.lNode.push(xNode);
                yield [i, xNode.textContent];
                i += 1;
            }
        }
        catch (e) {
            showError(e);
        }
    }

    getPageText () {
        try {
            let sPageText = "";
            for (let [i, sLine] of this.getParagraphs()) {
                sPageText += sLine + "\n";
            }
            return sPageText;
        }
        catch (e) {
            showError(e);
        }
    }

    getParagraph (iPara) {
        try {
            return this.lNode[iPara].textContent;
        }
        catch (e) {
            showError(e);
        }
    }

    writeParagraph (iPara, sText) {
        try {
            return this.lNode[iPara].textContent = sText;
        }
        catch (e) {
            showError(e);
        }
    }

    changeParagraph (iPara, sModif, iStart, iEnd) {
        let sText = this.getParagraph(iPara);
        this.writeParagraph(iPara, sText.slice(0, iStart) + sModif + sText.slice(iEnd));
    }
}