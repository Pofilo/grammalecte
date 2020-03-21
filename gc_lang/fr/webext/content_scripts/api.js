// JavaScript

"use strict";


const oGrammalecteAPI = {
    // functions callable from within pages
    // to be sent to the content-cript via an event “GrammalecteCall”

    sVersion: "1.0",

    openPanelForNode: function (vNode) {
        //  Parameter: a HTML node or the identifier of a HTML node
        if (vNode instanceof HTMLElement) {
            let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "openPanelForNode", xNode: vNode} });
            document.dispatchEvent(xEvent);
        }
        else if (typeof(vNode) === "string" && document.getElementById(vNode)) {
            let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "openPanelForNode", xNode: document.getElementById(vNode)} });
            document.dispatchEvent(xEvent);
        }
        else {
            console.log("[Grammalecte API] Error: parameter is not a HTML node.");
        }
    },

    openPanelForText: function (sText, vNode=null) {
        //  Parameter: text to analyze, and optionaly a node to send results to.
        if (typeof(sText) === "string") {
            let xNode = null;
            if (vNode instanceof HTMLElement) {
                xNode = vNode;
            }
            else if (typeof(vNode) === "string" && document.getElementById(vNode)) {
                xNode = document.getElementById(vNode);
            }
            let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "openPanelForText", sText: sText, xNode: xNode} });
            document.dispatchEvent(xEvent);
        } else {
            console.log("[Grammalecte API] Error: parameter is not a text.");
        }
    },

    parseNode: function (vNode) {
        /*  Parameter: a HTML node (with a identifier) or the identifier of a HTML node.
            The result will be sent as an event “GrammalecteResult” to the node.
        */
        if (vNode instanceof HTMLElement  &&  vNode.id) {
            let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "parseNode", xNode: vNode} });
            document.dispatchEvent(xEvent);
        }
        else if (typeof(vNode) === "string" && document.getElementById(vNode)) {
            let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "parseNode", xNode: document.getElementById(vNode)} });
            document.dispatchEvent(xEvent);
        }
        else {
            console.log("[Grammalecte API] Error: parameter is not a HTML node or doesn’t have an identifier.");
        }
    },

    parseText: function (sText, vNode) {
        //  Parameter: text to analyze, and a node to send results to.
        if (typeof(sText) === "string") {
            if (vNode instanceof HTMLElement  &&  vNode.id) {
                let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "parseText", sText: sText, xNode: vNode} });
                document.dispatchEvent(xEvent);
            }
            else if (typeof(vNode) === "string" && document.getElementById(vNode)) {
                let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "parseText", sText: sText, xNode: document.getElementById(vNode)} });
                document.dispatchEvent(xEvent);
            }
            else {
                console.log("[Grammalecte API] Error: parameter is not a HTML node or doesn’t have an identifier.");
            }
        } else {
            console.log("[Grammalecte API] Error: parameter is not a text.");
        }
    },

    getSpellSuggestions: function (sWord, sDestination, sRequestId="") {
        /* parameters:
            - sWord (string)
            - sDestination: HTML identifier (string) -> the result will be sent as an event “GrammalecteResult” to destination node
            - sRequestId: custom identifier for the request (string) [default = ""]
        */
        if (typeof(sWord) === "string"  &&  typeof(sDestination) === "string"  &&  typeof(sRequestId) === "string") {
            let xEvent = new CustomEvent("GrammalecteCall", { detail: {sCommand: "getSpellSuggestions", sWord: sWord, sDestination: sDestination, sRequestId: sRequestId} });
            document.dispatchEvent(xEvent);
        } else {
            console.log("[Grammalecte API] Error: one or several parameters aren’t string.");
        }
    }
}

/*
    Tell to the webpage that the Grammalecte API is ready.
*/
document.dispatchEvent(new Event('GrammalecteLoaded'));

