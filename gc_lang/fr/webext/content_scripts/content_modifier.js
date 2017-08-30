// Modify page

/*
    JS sucks (again, and again, and again, and again…)
    Not possible to load content from within the extension:
    https://bugzilla.mozilla.org/show_bug.cgi?id=1267027
    No SharedWorker, no images allowed for now…
*/

"use strict";


function showError (e) {
    console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
}

function createNode (sType, oAttr, oDataset=null) {
    try {
        let xNode = document.createElement(sType);
        Object.assign(xNode, oAttr);
        if (oDataset) {
            Object.assign(xNode.dataset, oDataset);
        }
        return xNode;
    }
    catch (e) {
        showError(e);
    }
}

/*
function loadImage (sContainerClass, sImagePath) {
    let xRequest = new XMLHttpRequest();
    xRequest.open('GET', browser.extension.getURL("")+sImagePath, false);
    xRequest.responseType = "arraybuffer";
    xRequest.send();
    let blobTxt = new Blob([xRequest.response], {type: 'image/png'});
    let img = document.createElement('img');
    img.src = (URL || webkitURL).createObjectURL(blobTxt); // webkitURL is obsolete: https://bugs.webkit.org/show_bug.cgi?id=167518
    Array.filter(document.getElementsByClassName(sContainerClass), function (oElem) {
        oElem.appendChild(img);
    });
}
*/

const oGrammalecte = {

    nWrapper: 0,
    lWrapper: [],

    oTFPanel: null,
    oLxgPanel: null,
    oGCPanel: null,

    wrapTextareas: function () {
        let lNode = document.getElementsByTagName("textarea");
        for (let xNode of lNode) {
            this.lWrapper.push(new GrammalecteWrapper(this.nWrapper, xNode));
            this.nWrapper += 1;
        }
    },

    createTFPanel: function () {
        if (this.oTFPanel === null) {
            this.oTFPanel = new GrammalecteTextFormatter("grammalecte_tf_panel", "Formateur de texte", 800, 620, false);
            //this.oTFPanel.logInnerHTML();
            this.oTFPanel.insertIntoPage();
        }
    },

    createLxgPanel: function () {
        if (this.oLxgPanel === null) {
            this.oLxgPanel = new GrammalecteLexicographer("grammalecte_lxg_panel", "Lexicographe", 500, 700);
            this.oLxgPanel.insertIntoPage();
        }
    },

    createGCPanel: function () {
        if (this.oGCPanel === null) {
            this.oGCPanel = new GrammalecteGrammarChecker("grammalecte_gc_panel", "Grammalecte", 500, 700);
            //this.oGCPanel.logInnerHTML();
            this.oGCPanel.insertIntoPage();
        }
    }
}


/*
    Connexion to the background
*/
let xPort = browser.runtime.connect({name: "content-script port"});

xPort.onMessage.addListener(function (oMessage) {
    let {sActionDone, result, dInfo, bEnd, bError} = oMessage;
    switch (sActionDone) {
        case "parseAndSpellcheck":
            if (!bEnd) {
                oGrammalecte.oGCPanel.addParagraphResult(result);
            } else {
                oGrammalecte.oGCPanel.stopWaitIcon();
            }
            break;
        case "parseAndSpellcheck1":
            oGrammalecte.oGCPanel.refreshParagraph(dInfo.sParagraphId, result);
            break;
        case "getListOfTokens":
            if (!bEnd) {
                oGrammalecte.oLxgPanel.addListOfTokens(result);
            } else {
                oGrammalecte.oLxgPanel.stopWaitIcon();
            }
            break;
        // Design WTF: context menus are made in background, not in content-script.
        // Commands from context menu received here to initialize panels
        case "openGCPanel":
            oGrammalecte.createGCPanel();
            oGrammalecte.oGCPanel.clear();
            oGrammalecte.oGCPanel.show();
            oGrammalecte.oGCPanel.start();
            oGrammalecte.oGCPanel.startWaitIcon();
            break;
        case "openLxgPanel":
            oGrammalecte.createLxgPanel();
            oGrammalecte.oLxgPanel.clear();
            oGrammalecte.oLxgPanel.show();
            oGrammalecte.oLxgPanel.startWaitIcon();
            break;
        default:
            console.log("[Content script] Unknown command: " + sActionDone);
    }
});


/*
    Start
*/
oGrammalecte.wrapTextareas();
