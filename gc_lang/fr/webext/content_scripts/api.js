// JavaScript

"use strict";


const oGrammalecteAPI = {
    // functions callable from within pages

    sVersion: "1.0",

    parse: function (arg1) {
        let xNode = null;
        if (typeof(arg1) === 'string') {
            if (document.getElementById(arg1)) {
                xNode = document.getElementById(arg1);
            } else {
                this.parseText(arg1);
            }
        }
        else if (arg1 instanceof HTMLElement) {
            xNode = arg1;
        }
        if (xNode) {
            console.log("xnode");
            if (xNode.tagName == "INPUT"  ||  xNode.tagName == "TEXTAREA"  ||  xNode.isContentEditable) {
                this.parseNode(xNode);
            }
            else if (xNode.tagName == "IFRAME") {
                this.parseText(xNode.contentWindow.document.body.innerText);
            }
            else {
                this.parseText(xNode.innerText);
            }
        }
    },

    parseNode: function (xNode) {
        console.log("parseNode");
        if (xNode instanceof HTMLElement) {
            let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "parseNode", xNode: xNode} });
            document.dispatchEvent(xEvent);
        } else {
            console.log("[Grammalecte API] Error: parameter is not a HTML node.");
        }
    },

    parseText: function (sText) {
        console.log("parseText");
        if (typeof(sText) === "string") {
            let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "parseText", sText: sText} });
            document.dispatchEvent(xEvent);
        } else {
            console.log("[Grammalecte API] Error: parameter is not a text.");
        }
    }
}
