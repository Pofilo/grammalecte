// JavaScript

"use strict";


const oGrammalecteAPI = {
    // functions callable from within pages

    sVersion: "1.0",

    openPanel: function (arg1) {
        let xNode = null;
        if (typeof(arg1) === 'string') {
            if (document.getElementById(arg1)) {
                xNode = document.getElementById(arg1);
            } else {
                this.openPanelForText(arg1);
            }
        }
        else if (arg1 instanceof HTMLElement) {
            xNode = arg1;
        }
        if (xNode) {
            if (xNode.tagName == "INPUT"  ||  xNode.tagName == "TEXTAREA"  ||  xNode.tagName == "IFRAME"  ||  xNode.isContentEditable) {
                this.openPanelForNode(xNode);
            } else {
                this.openPanelForText(xNode.innerText);
            }
        }
    },

    openPanelForNode: function (xNode) {
        if (xNode instanceof HTMLElement) {
            let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "openPanelForNode", xNode: xNode} });
            document.dispatchEvent(xEvent);
        } else {
            console.log("[Grammalecte API] Error: parameter is not a HTML node.");
        }
    },

    openPanelForText: function (sText) {
        if (typeof(sText) === "string") {
            let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "openPanelForText", sText: sText} });
            document.dispatchEvent(xEvent);
        } else {
            console.log("[Grammalecte API] Error: parameter is not a text.");
        }
    },

    parseNode: function (xNode) {
        if (xNode instanceof HTMLElement) {
            let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "parseNode", xNode: xNode} });
            document.dispatchEvent(xEvent);
        } else {
            console.log("[Grammalecte API] Error: parameter is not a HTML node.");
        }
    },

    parseText: function (sText) {
        if (typeof(sText) === "string") {
            let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "parseText", sText: sText} });
            document.dispatchEvent(xEvent);
        } else {
            console.log("[Grammalecte API] Error: parameter is not a text.");
        }
    }
}
