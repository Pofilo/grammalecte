// JavaScript

"use strict";


const Cc = Components.classes;
const Ci = Components.interfaces;
const Cu = Components.utils;
const { require } = Cu.import("resource://gre/modules/commonjs/toolkit/require.js", {});

const { BasePromiseWorker } = Cu.import('resource://gre/modules/PromiseWorker.jsm', {});
const Task = Cu.import("resource://gre/modules/Task.jsm").Task;
const prefs = Cc["@mozilla.org/preferences-service;1"].getService(Ci.nsIPrefService).getBranch("extensions.grammarchecker.");
//Cu.import("resource://gre/modules/Console.jsm"); // doesn’t work
//const xConsole = Cc["@mozilla.org/consoleservice;1"].getService(Ci.nsIConsoleService);
//xConsole.logStringMessage("Grammalecte: " + args.join(" · ")); // useless now. Use: Services.console.logStringMessage("***");

const text = require("resource://grammalecte/text.js");
const tf = require("resource://grammalecte/fr/textformatter.js");


function echo (...args) {
    dump(args.join(" -- ") + "\n");  // obsolete since TB 52?
    Services.console.logStringMessage("Grammalecte: " + args.join(" · "));
}


const oConverterToExponent = {
    dNumbers: new Map ([
        ["1", "¹"], ["2", "²"], ["3", "³"], ["4", "⁴"], ["5", "⁵"],
        ["6", "⁶"], ["7", "⁷"], ["8", "⁸"], ["9", "⁹"], ["0", "⁰"]
    ]),
    convert: function (sText) {
        let sRes = "";
        for (let c of sText) {
            sRes += (this.dNumbers.has(c)) ? this.dNumbers.get(c) : "⁻";
        }
        return sRes;
    }
};


var oGrammarChecker = {
    // you must use var to be able to call this object from elsewhere
    xGCEWorker: null,
    bDictActive: null,
    loadGC: function () {
        if (this.xGCEWorker === null) {
            // Grammar checker
            echo('Loading Grammalecte');
            this.xGCEWorker = new BasePromiseWorker('chrome://promiseworker/content/gce_worker.js');
            let xPromise = this.xGCEWorker.post('loadGrammarChecker', [prefs.getCharPref("sGCOptions")]);
            xPromise.then(
                function (aVal) {
                    echo(aVal);
                    prefs.setCharPref("sGCOptions", aVal);
                },
                function (aReason) { echo('Promise rejected - ', aReason); }
            ).catch(
                function (aCaught) { echo('Promise Error - ', aCaught); }
            );
        }
    },
    fullTests: function () {
        echo('Performing tests... Wait...');
        let xPromise = this.xGCEWorker.post('fullTests', ['{"nbsp":true, "esp":true, "unit":true, "num":true}']);
        xPromise.then(
            function (aVal) {
                echo('Done.');
                echo(aVal);
            },
            function (aReason) { echo('Promise rejected', aReason); }
        ).catch(
            function (aCaught) { echo('Promise Error', aCaught); }
        );
    },
    test: function (sText) {
        echo("Test...");
        let xPromise = this.xGCEWorker.post('parse', [sText, "FR", true]);
        xPromise.then(
            function (aVal) {
                let lErr = JSON.parse(aVal);
                if (lErr.length > 0) {
                    for (let dErr of lErr) {
                        echo(text.getReadableError(dErr));
                    }
                } else {
                    echo("no error found");
                }
            },
            function (aReason) { echo('Promise rejected', aReason); }
        ).catch(
            function (aCaught) { echo('Promise Error', aCaught); }
        );
    },
    setOptions: function () {
        echo('Set options');
        let xPromise = this.xGCEWorker.post('setOptions', [prefs.getCharPref("sGCOptions")]);
        xPromise.then(
            function (aVal) {
                echo(aVal);
                prefs.setCharPref("sGCOptions", aVal);
            },
            function (aReason) { echo('Promise rejected', aReason); }
        ).catch(
            function (aCaught) { echo('Promise Error', aCaught); }
        );
    },
    resetOptions: function () {
        let xPromise = this.xGCEWorker.post('resetOptions');
        xPromise.then(
            function (aVal) {
                echo(aVal);
                prefs.setCharPref("sGCOptions", aVal);
            },
            function (aReason) { echo('Promise rejected', aReason); }
        ).catch(
            function (aCaught) { echo('Promise Error', aCaught); }
        );
    },
    _getGCResultPromise: function (sParagraph, sLang, bDebug, bContext) {
        // For some reason, you can’t use result of PromiseWorker within a Task,
        // you have to wrap it in a common Promise. Task and yield can be replaced with async / await when it is available.
        let that = this;
        return new Promise(function (resolve, reject) {
            let xPromise = that.xGCEWorker.post('parseAndSpellcheck', [sParagraph, sLang, bDebug, bContext]);
            xPromise.then(
                function (aVal) {
                    resolve(aVal);
                },
                function (aReason) {
                    // rejected
                    resolve(aReason);
                }
            ).catch(
                function (aCaught) {
                    // error
                    reject(aCaught);
                }
            );
        });
    },
    parse: function () {
        this.clearPreview();
        this.openPanel();
        this.setInfo("Analyse en cours…");
        let that = this;
        Task.spawn(function* () {
            let xEditor = new Editor();
            let nParagraph = 0;
            let bIsError = false;
            for (let [iParagraph, sParagraph] of xEditor.getParagraphs()) {
                if (sParagraph.trim() !== "") {
                    let sRes = yield that._getGCResultPromise(sParagraph, "FR", false, false);
                    let oRes = JSON.parse(sRes);
                    if (oRes.aGrammErr.length > 0 || oRes.aSpellErr.length > 0) {
                        document.getElementById("grammalecte-errors").appendChild(that.createResultNode(xEditor, sParagraph, iParagraph, oRes.aGrammErr, oRes.aSpellErr));
                        bIsError = true;
                    }
                    nParagraph += 1;
                }
            }
            if (bIsError === false) {
                let xNodeP = document.createElement("p");
                xNodeP.setAttribute("class", "message");
                xNodeP.textContent = "Aucune erreur détectée…";
                document.getElementById("grammalecte-errors").appendChild(xNodeP);
            }
            return nParagraph;
        }).then(function (res) {
            that.setInfo("Nombre de paragraphes analysés : " + res);
        }, function (e) {
            that.setInfo("Erreur : " + e.message);
            Cu.reportError(e);
        });
    },
    createResultNode: function (xEditor, sParagraph, iParagraph, aGrammErr, aSpellErr) {
        let xResultNode = document.createElement("div");
        xResultNode.setAttribute("id", "resnode" + iParagraph);
        this.fillResultNode(xResultNode, xEditor, sParagraph, iParagraph, aGrammErr, aSpellErr);
        return xResultNode;
    },
    reparseParagraph: function (xEditor, iParagraph) {
        try {
            let that = this;
            let xResultNode = document.getElementById("resnode"+iParagraph);
            xResultNode.textContent = "…………… réanalyse en cours ……………";
            let sParagraph = xEditor.getParagraph(iParagraph);
            let xPromise = this._getGCResultPromise(sParagraph, "FR", false, false);
            xPromise.then(function (res) {
                //echo("res: " + res);
                xResultNode.textContent = "";
                let oRes = JSON.parse(res);
                if (oRes.aGrammErr.length > 0 || oRes.aSpellErr.length > 0) {
                    that.fillResultNode(xResultNode, xEditor, sParagraph, iParagraph, oRes.aGrammErr, oRes.aSpellErr);
                }
            }, function (res) {
                xResultNode.textContent = "Erreur: " + res;
            });
        }
        catch (e) {
            Cu.reportError(e);
        }
    },
    fillResultNode: function (xResultNode, xEditor, sParagraph, iParagraph, aGrammErr, aSpellErr) {
        try {
            if (aGrammErr.length === 0  &&  aSpellErr.length === 0) {
                return null;
            }
            aGrammErr.push(...aSpellErr);
            aGrammErr.sort(function (a, b) {
                if (a["nStart"] < b["nStart"])
                    return -1;
                if (a["nStart"] > b["nStart"])
                    return 1;
                return 0;
            });
            let xParagraphNode = document.createElement("p");
            let lNodeError = [];
            let nEndLastErr = 0;
            let nError = 1;
            xParagraphNode.setAttribute("class", "paragraph");
            for (let dErr of aGrammErr) {
                let nStart = dErr["nStart"];
                let nEnd = dErr["nEnd"];
                if (nStart >= nEndLastErr) {
                    xParagraphNode.appendChild(document.createTextNode(this._purgeTags(sParagraph.slice(nEndLastErr, nStart))));
                    let xNodeError = document.createElement("b");
                    if (dErr['sType'] !== 'WORD') {
                        xNodeError.setAttribute("class", "error " + dErr["sType"]);
                        xNodeError.textContent = oConverterToExponent.convert(nError.toString()) + sParagraph.slice(nStart, nEnd);
                        xParagraphNode.appendChild(xNodeError);
                        lNodeError.push(this._createNodeGCErrorDescription(xEditor, nError, dErr, iParagraph));
                    }
                    else {
                        xNodeError.setAttribute("class", "error spell");
                        xNodeError.textContent = oConverterToExponent.convert(nError.toString()) + sParagraph.slice(nStart, nEnd);
                        xParagraphNode.appendChild(xNodeError);
                        lNodeError.push(this._createNodeSpellErrorDescription(xEditor, nError, dErr, iParagraph));
                    }
                    nEndLastErr = nEnd;
                    nError += 1;
                }
            }
            xParagraphNode.appendChild(document.createTextNode(this._purgeTags(sParagraph.slice(nEndLastErr))));
            xResultNode.appendChild(xParagraphNode);
            for (let xNode of lNodeError) {
                xResultNode.appendChild(xNode);
            }
        }
        catch (e) {
            Cu.reportError(e);
            xResultNode.textContent = "# Error: " + e.message;
        }
    },
    _createNodeGCErrorDescription: function (xEditor, nError, dErr, iParagraph) {
        let xNodeDiv = document.createElement("div");
        let that = this;
        // message
        let xNodeMessage = document.createElement("p");
        xNodeMessage.setAttribute("class", "message");
        let xNodeErrorNumber = document.createElement("b");
        xNodeErrorNumber.setAttribute("class", "errornum");
        xNodeErrorNumber.textContent = "[" + nError + "] ";
        xNodeMessage.appendChild(xNodeErrorNumber);
        xNodeMessage.appendChild(document.createTextNode(" " + dErr["sMessage"].replace(/&nbsp;/g, " ") + " "));
        if (false) {
            // debug info
            let xNodeDebug = document.createElement("span");
            xNodeDebug.setAttribute("class", "debug_info");
            xNodeDebug.textContent = " #" + dErr["sRuleId"] + " #" + dErr["sLineId"];
            xNodeMessage.appendChild(xNodeDebug);
        }
        xNodeDiv.appendChild(xNodeMessage);
        // URL
        if (dErr["URL"]) {
            let xNodeP = document.createElement("p");
            xNodeP.setAttribute("class", "moreinfo");
            xNodeP.appendChild(document.createTextNode("→ "));
            let xNodeURL = document.createElement("a");
            xNodeURL.setAttribute("href", dErr["URL"]);
            xNodeURL.textContent = "Plus d’informations…";
            xNodeURL.addEventListener("click", function (e) {
                that.openInTabURL(dErr["URL"]);
            });
            xNodeP.appendChild(xNodeURL);
            xNodeDiv.appendChild(xNodeP);
        }
        // suggestions
        if (dErr["aSuggestions"].length > 0) {
            let xNodeSuggLine = document.createElement("p");
            xNodeSuggLine.setAttribute("class", "suggestions");
            xNodeSuggLine.textContent = "Suggestions : ";
            let n = 0;
            for (let sSugg of dErr["aSuggestions"]) {
                if (n > 0) {
                    xNodeSuggLine.appendChild(document.createTextNode(" "));
                }
                let xNodeSugg = document.createElement("span");
                xNodeSugg.setAttribute("class", "sugg");
                xNodeSugg.textContent = sSugg;
                xNodeSugg.addEventListener("click", function (e) {
                    xEditor.changeParagraph(iParagraph, xNodeSugg.textContent, dErr["nStart"], dErr["nEnd"]);
                    xNodeDiv.textContent = "";
                    that.reparseParagraph(xEditor, iParagraph);
                });
                xNodeSuggLine.appendChild(xNodeSugg);
                n += 1;
            }
            xNodeDiv.appendChild(xNodeSuggLine);
        }
        return xNodeDiv;
    },
    _purgeTags: function (sText) {
        sText = sText.replace(/<br ?\/?>/ig, " ");
        return sText.replace(/<\/? ?[a-zA-Z]+ ?>/g, "");
    },
    _createNodeSpellErrorDescription: function (xEditor, nError, dErr, iParagraph) {
        let xNodeDiv = document.createElement("div");
        let that = this;
        // message
        let xNodeMessage = document.createElement("p");
        xNodeMessage.setAttribute("class", "message");
        let xNodeErrorNumber = document.createElement("b");
        xNodeErrorNumber.setAttribute("class", "errornum");
        xNodeErrorNumber.textContent = "[" + nError + "] ";
        xNodeMessage.appendChild(xNodeErrorNumber);
        xNodeMessage.appendChild(document.createTextNode(" Mot inconnu du dictionnaire. "));
        xNodeDiv.appendChild(xNodeMessage);
        // suggestions
        let xNodeSuggLine = document.createElement("p");
        xNodeSuggLine.setAttribute("class", "suggestions");
        let xNodeSuggButton = document.createElement("span");
        xNodeSuggButton.setAttribute("class", "suggestions_button");
        xNodeSuggButton.textContent = "Suggestions : ";
        xNodeSuggButton.addEventListener("click", function (e) {
            if (this.bDictActive === null) {
                this.bDictActive = oSpellControl.setDictionary("fr");
            }
            try {
                let aSugg = oSpellControl.suggest(dErr['sValue']);
                if (aSugg) {
                    let n = 0;
                    for (let sSugg of aSugg) {
                        if (true || n > 0) {
                            xNodeSuggLine.appendChild(document.createTextNode(" "));
                        }
                        let xNodeSugg = document.createElement("span");
                        xNodeSugg.setAttribute("class", "sugg");
                        xNodeSugg.textContent = sSugg;
                        xNodeSugg.addEventListener("click", function (e) {
                            xEditor.changeParagraph(iParagraph, xNodeSugg.textContent, dErr["nStart"], dErr["nEnd"]);
                            xNodeDiv.textContent = "";
                            that.reparseParagraph(xEditor, iParagraph);
                        });
                        xNodeSuggLine.appendChild(xNodeSugg);
                        n += 1;
                    }
                } else {
                    xNodeSuggLine.appendChild(document.createTextNode("Aucune suggestion."));
                }
            }
            catch (e) {
                xNodeSuggLine.appendChild(document.createTextNode("# Erreur : dictionnaire orthographique introuvable."));
                Cu.reportError(e);
            }
        });
        xNodeSuggLine.appendChild(xNodeSuggButton);
        xNodeDiv.appendChild(xNodeSuggLine);
        return xNodeDiv;
    },
    loadUI: function() {
        echo("loadUI");
        this._strings = document.getElementById("grammarchecker-strings");
        let that = this;
        let nsGrammarCommand = {
            isCommandEnabled: function (aCommand, dummy) {
                return (IsDocumentEditable() && !IsInHTMLSourceMode());
            },
            getCommandStateParams: function (aCommand, aParams, aRefCon) {},
            doCommandParams: function (aCommand, aParams, aRefCon) {},
            doCommand: function (aCommand) {
                that.onParseText(aCommand);
            }
        };
        let xCommandTable = GetComposerCommandTable();
        xCommandTable.registerCommand("cmd_grammar", nsGrammarCommand);
        let sButtonId = "grammarchecker-toolbar-button";
        let sButtonId2 = "grammalecte-menu";
        let xNavBar  = document.getElementById("composeToolbar2");
        let lCurSet  = xNavBar.currentSet.split(",");
        if (lCurSet.indexOf(sButtonId) == -1) {
            let iPos = lCurSet.indexOf("spellingButton") + 1 || lCurSet.length;
            let aSet = lCurSet.slice(0, iPos).concat(sButtonId).concat(sButtonId2).concat(lCurSet.slice(iPos));
            xNavBar.setAttribute("currentset", aSet.join(","));
            xNavBar.currentSet = aSet.join(",");
            document.persist(xNavBar.id, "currentset");
            try {
                BrowserToolboxCustomizeDone(true);
            }
            catch (e) {
                Cu.reportError(e);
            }
        }
    },
    clearPreview: function() {
        let xPreview = document.getElementById("grammalecte-errors");
        while (xPreview.firstChild) {
            xPreview.removeChild(xPreview.firstChild);
        };
        let xEditor = GetCurrentEditor();
        if (xEditor != null) {
            try {
                xEditor.QueryInterface(Ci.nsIEditorStyleSheets);
                xEditor.addOverrideStyleSheet("chrome://grammarchecker/content/overlay.css");
            }
            catch (e) {
                Cu.reportError(e);
            }
        }
        this.setInfo("[vide]");
    },
    setInfo: function (sText) {
        document.getElementById("grammalecte-info").textContent = sText;
    },
    openPanel: function () {
        document.getElementById("textformatter-splitter").setAttribute("state", "collapsed");
        document.getElementById("grammarchecker-splitter").setAttribute("state", "open");
    },
    closePanel: function () {
        document.getElementById("grammarchecker-splitter").setAttribute("state", "collapsed");
    },
    openDialog: function (sWhat, sName="", sOptions="") {
        try {
            window.openDialog(sWhat, sName, sOptions);
        }
        catch (e) {
            Cu.reportError(e);
        }
    },
    openInTabURL: function (sURL) {
        // method found in S3.Google.Translator
        try {
            let xWM = Cc["@mozilla.org/appshell/window-mediator;1"].getService(Ci.nsIWindowMediator);
            let xWin = xWM.getMostRecentWindow("mail:3pane");
            let xTabmail = xWin.document.getElementById('tabmail');
            xWin.focus();
            if (xTabmail) {
                xTabmail.openTab('contentTab', { contentPage: sURL });
            }
        }
        catch (e) {
            Cu.reportError(e);
        }
    },
    openInBrowserURL: function (sURL) {
        // method found in S3.Google.Translator
        try {
            openURL(sURL);
        }
        catch (e) {
            Cu.reportError(e);
        }
    },
    onParseText: function (e) {
        this.parse();
    },
    onClosePanel: function (e) {
        this.closePanel();
    },
    onOpenGCOptions: function (e) {
        let that = this;
        let xPromise = this.xGCEWorker.post('getDefaultOptions');
        xPromise.then(
            function (aVal) {
                echo(aVal);
                prefs.setCharPref("sGCDefaultOptions", aVal);
            },
            function (aReason) { echo('Promise rejected', aReason); }
        ).catch(
            function (aCaught) { echo('Promise Error', aCaught); }
        ).then(
            function () {
                that.openDialog("chrome://grammarchecker/content/gc_options.xul", "", "chrome, dialog, modal, resizable=no");
                that.setOptions();
            },
            function (aReason) { echo('Error options dialog', aReason); }
        ).catch(
            function (aCaught) { echo('Error', aCaught); }
        );
    },
    onOpenSpellOptions: function (e) {
        this.openDialog("chrome://grammarchecker/content/spell_options.xul", "", "chrome, dialog, modal, resizable=no");
    },
    onOpenOptions: function (e) {
        this.openDialog("chrome://grammarchecker/content/options.xul", "", "chrome, dialog, modal, resizable=no");
    },
    onOpenTextFormatter: function (e) {
        oTextFormatter.openPanel();
    },
    onOpenConjugueur: function (e) {
        this.openDialog("chrome://grammarchecker/content/conjugueur.xul", "", "chrome, resizable=no");
    },
    onAbout: function (e) {
        this.openDialog("chrome://grammarchecker/content/about.xul", "", "chrome, dialog, modal, resizable=no");
    }
};


var oDictIgniter = {
    bDone: false,
    init: function () {
        if (!this.bDone) {
            oSpellControl.init();
            this._setDictionary('fr-FR-modern', 'bDictModern');
            this._setDictionary('fr-FR-classic', 'bDictClassic');
            this._setDictionary('fr-FR-reform', 'bDictReform');
            this._setDictionary('fr-FR-classic-reform', 'bDictClassicReform');
        }
    },
    _setDictionary: function (sDicName, sOptName) {
        try {
            oSpellControl.setExtensionDictFolder(sDicName, prefs.getBoolPref(sOptName));
        }
        catch (e) {
            Cu.reportError(e);
        }
    }
}


var oTextFormatter = {
    init: function () {
        try {
            this.closePanel();
            let sTFOptions = prefs.getCharPref("sTFOptions");
            if (sTFOptions !== "") {
                this.setOptionsInPanel(JSON.parse(sTFOptions));
                this.resetProgressBar();
            } else {
                this.reset();
            }
        }
        catch (e) {
            Cu.reportError(e);
        }
    },
    apply: function () {
        try {
            this.saveOptions();
            this.resetProgressBar();
            let xEditor = new Editor();
            let sText = xEditor.getContent();
            let iParagraph = 0;
            sText = this.applyOptions(sText);
            for (let sParagraph of text.getParagraph(sText)) {
                xEditor.writeParagraph(iParagraph, sParagraph);
                iParagraph += 1;
            }
        }
        catch (e) {
            Cu.reportError(e);
        }
    },
    saveOptions: function () {
        let oOptions = {};
        for (let xNode of document.getElementsByClassName("option")) {
            oOptions[xNode.id] = xNode.checked;
        }
        //echo("save options: " + JSON.stringify(oOptions));
        prefs.setCharPref("sTFOptions", JSON.stringify(oOptions));
    },
    setOptionsInPanel: function (oOptions) {
        for (let sOptName in oOptions) {
            //console.log(sOptName + ":" + oOptions[sOptName]);
            if (document.getElementById(sOptName) !== null) {
                document.getElementById(sOptName).checked = oOptions[sOptName];
                if (sOptName.startsWith("o_group_")) {
                    this.switchGroup(sOptName);
                } 
                if (document.getElementById("res_"+sOptName) !== null) {
                    document.getElementById("res_"+sOptName).textContent = "";
                }
            }
        }
    },
    switchGroup: function (sOptName) {
        if (document.getElementById(sOptName).checked) {
            document.getElementById(sOptName.slice(2)).style.opacity = 1;
        } else {
            document.getElementById(sOptName.slice(2)).style.opacity = 0.3;
        }
    },
    reset: function () {
        try {
            this.resetProgressBar();
            for (let xNode of document.getElementsByClassName('option')) {
                xNode.checked = (xNode.getAttribute('data-default') === "true");
                if (xNode.id.startsWith("o_group_")) {
                    this.switchGroup(xNode.id);
                }
            }
        }
        catch (e) {
            Cu.reportError(e);
        }
    },
    resetProgressBar: function () {
        document.getElementById('progressbar').value = 0;
        document.getElementById('time_res').textContent = "";
    },
    getTimeRes: function (n) {
        // returns duration in seconds as string
        if (n < 10) {
            return n.toFixed(3).toString() + " s";
        }
        if (n < 100) {
            return n.toFixed(2).toString() + " s";
        }
        if (n < 1000) {
            return n.toFixed(1).toString() + " s";
        }
        return n.toFixed().toString() + " s";
    },
    openPanel: function () {
        document.getElementById("grammarchecker-splitter").setAttribute("state", "collapsed");
        document.getElementById("textformatter-splitter").setAttribute("state", "open");
    },
    closePanel: function () {
        document.getElementById("textformatter-splitter").setAttribute("state", "collapsed");
    },
    onOpenPanel: function (e) {
        this.openPanel();
    },
    onClosePanel: function (e) {
        this.closePanel();
    },
    onApply: function (e) {
        this.apply();
    },
    onReset: function (e) {
        this.reset();
    },
    //
    applyOptions: function (sText) {
        try {
            const t0 = Date.now();
            //window.setCursor("wait"); // change pointer
            document.getElementById('progressbar').value = 0;
            document.getElementById('progressbar').max = 6;
            let n1 = 0, n2 = 0, n3 = 0, n4 = 0, n5 = 0, n6 = 0, n7 = 0;
            
            // espaces surnuméraires
            if (document.getElementById("o_group_ssp").checked) {
                if (document.getElementById("o_end_of_paragraph").checked) {
                    [sText, n1] = this.formatText(sText, "end_of_paragraph");
                    document.getElementById('res_o_end_of_paragraph').textContent = n1;
                }
                if (document.getElementById("o_between_words").checked) {
                    [sText, n1] = this.formatText(sText, "between_words");
                    document.getElementById('res_o_between_words').textContent = n1;
                }
                if (document.getElementById("o_start_of_paragraph").checked) {
                    [sText, n1] = this.formatText(sText, "start_of_paragraph");
                    document.getElementById('res_o_start_of_paragraph').textContent = n1;
                }
                if (document.getElementById("o_before_punctuation").checked) {
                    [sText, n1] = this.formatText(sText, "before_punctuation");
                    document.getElementById('res_o_before_punctuation').textContent = n1;
                }
                if (document.getElementById("o_within_parenthesis").checked) {
                    [sText, n1] = this.formatText(sText, "within_parenthesis");
                    document.getElementById('res_o_within_parenthesis').textContent = n1;
                }
                if (document.getElementById("o_within_square_brackets").checked) {
                    [sText, n1] = this.formatText(sText, "within_square_brackets");
                    document.getElementById('res_o_within_square_brackets').textContent = n1;
                }
                if (document.getElementById("o_within_quotation_marks").checked) {
                    [sText, n1] = this.formatText(sText, "within_quotation_marks");
                    document.getElementById('res_o_within_quotation_marks').textContent = n1;
                }
                document.getElementById("o_group_ssp").checked = false;
                this.switchGroup("o_group_ssp");
            }
            document.getElementById('progressbar').value = 1;

            // espaces typographiques
            if (document.getElementById("o_group_nbsp").checked) {
                if (document.getElementById("o_nbsp_before_punctuation").checked) {
                    [sText, n1] = this.formatText(sText, "nbsp_before_punctuation");
                    [sText, n2] = this.formatText(sText, "nbsp_repair");
                    document.getElementById('res_o_nbsp_before_punctuation').textContent = n1 - n2;
                }
                if (document.getElementById("o_nbsp_within_quotation_marks").checked) {
                    [sText, n1] = this.formatText(sText, "nbsp_within_quotation_marks");
                    document.getElementById('res_o_nbsp_within_quotation_marks').textContent = n1;
                }
                if (document.getElementById("o_nbsp_before_symbol").checked) {
                    [sText, n1] = this.formatText(sText, "nbsp_before_symbol");
                    document.getElementById('res_o_nbsp_before_symbol').textContent = n1;
                }
                if (document.getElementById("o_nbsp_within_numbers").checked) {
                    [sText, n1] = this.formatText(sText, "nbsp_within_numbers");
                    document.getElementById('res_o_nbsp_within_numbers').textContent = n1;
                }
                if (document.getElementById("o_nbsp_before_units").checked) {
                    [sText, n1] = this.formatText(sText, "nbsp_before_units");
                    document.getElementById('res_o_nbsp_before_units').textContent = n1;
                }
                document.getElementById("o_group_nbsp").checked = false;
                this.switchGroup("o_group_nbsp");
            }
            document.getElementById('progressbar').value = 2;

            // espaces manquants
            if (document.getElementById("o_group_typo").checked) {
                if (document.getElementById("o_ts_units").checked) {
                    [sText, n1] = this.formatText(sText, "ts_units");
                    document.getElementById('res_o_ts_units').textContent = n1;
                }
            }
            if (document.getElementById("o_group_space").checked) {
                if (document.getElementById("o_add_space_after_punctuation").checked) {
                    [sText, n1] = this.formatText(sText, "add_space_after_punctuation");
                    [sText, n2] = this.formatText(sText, "add_space_repair");
                    document.getElementById('res_o_add_space_after_punctuation').textContent = n1 - n2;
                }
                if (document.getElementById("o_add_space_around_hyphens").checked) {
                    [sText, n1] = this.formatText(sText, "add_space_around_hyphens");
                    document.getElementById('res_o_add_space_around_hyphens').textContent = n1;
                }
                document.getElementById("o_group_space").checked = false;
                this.switchGroup("o_group_space");
            }
            document.getElementById('progressbar').value = 3;

            // suppression
            if (document.getElementById("o_group_delete").checked) {
                if (document.getElementById("o_erase_non_breaking_hyphens").checked) {
                    [sText, n1] = this.formatText(sText, "erase_non_breaking_hyphens");
                    document.getElementById('res_o_erase_non_breaking_hyphens').textContent = n1;
                }
                document.getElementById("o_group_delete").checked = false;
                this.switchGroup("o_group_delete");
            }
            document.getElementById('progressbar').value = 4;

            // signes typographiques
            if (document.getElementById("o_group_typo").checked) {
                if (document.getElementById("o_ts_apostrophe").checked) {
                    [sText, n1] = this.formatText(sText, "ts_apostrophe");
                    document.getElementById('res_o_ts_apostrophe').textContent = n1;
                }
                if (document.getElementById("o_ts_ellipsis").checked) {
                    [sText, n1] = this.formatText(sText, "ts_ellipsis");
                    document.getElementById('res_o_ts_ellipsis').textContent = n1;
                }
                if (document.getElementById("o_ts_dash_start").checked) {
                    if (document.getElementById("o_ts_m_dash_start").checked) {
                        [sText, n1] = this.formatText(sText, "ts_m_dash_start");
                    } else {
                        [sText, n1] = this.formatText(sText, "ts_n_dash_start");
                    }
                    document.getElementById('res_o_ts_dash_start').textContent = n1;
                }
                if (document.getElementById("o_ts_dash_middle").checked) {
                    if (document.getElementById("o_ts_m_dash_middle").checked) {
                        [sText, n1] = this.formatText(sText, "ts_m_dash_middle");
                    } else {
                        [sText, n1] = this.formatText(sText, "ts_n_dash_middle");
                    }
                    document.getElementById('res_o_ts_dash_middle').textContent = n1;
                }
                if (document.getElementById("o_ts_quotation_marks").checked) {
                    [sText, n1] = this.formatText(sText, "ts_quotation_marks");
                    document.getElementById('res_o_ts_quotation_marks').textContent = n1;
                }
                if (document.getElementById("o_ts_spell").checked) {
                    [sText, n1] = this.formatText(sText, "ts_spell");
                    document.getElementById('res_o_ts_spell').textContent = n1;
                }
                if (document.getElementById("o_ts_ligature").checked) {
                    // ligatures typographiques : fi, fl, ff, ffi, ffl, ft, st
                    if (document.getElementById("o_ts_ligature_do").checked) {
                        if (document.getElementById("o_ts_ligature_ffi").checked) {
                            [sText, n1] = this.formatText(sText, "ts_ligature_ffi_do");
                        }
                        if (document.getElementById("o_ts_ligature_ffl").checked) {
                            [sText, n2] = this.formatText(sText, "ts_ligature_ffl_do");
                        }
                        if (document.getElementById("o_ts_ligature_fi").checked) {
                            [sText, n3] = this.formatText(sText, "ts_ligature_fi_do");
                        }
                        if (document.getElementById("o_ts_ligature_fl").checked) {
                            [sText, n4] = this.formatText(sText, "ts_ligature_fl_do");
                        }
                        if (document.getElementById("o_ts_ligature_ff").checked) {
                            [sText, n5] = this.formatText(sText, "ts_ligature_ff_do");
                        }
                        if (document.getElementById("o_ts_ligature_ft").checked) {
                            [sText, n6] = this.formatText(sText, "ts_ligature_ft_do");
                        }
                        if (document.getElementById("o_ts_ligature_st").checked) {
                            [sText, n7] = this.formatText(sText, "ts_ligature_st_do");
                        }
                    }
                    if (document.getElementById("o_ts_ligature_undo").checked) {
                        if (document.getElementById("o_ts_ligature_ffi").checked) {
                            [sText, n1] = this.formatText(sText, "ts_ligature_ffi_undo");
                        }
                        if (document.getElementById("o_ts_ligature_ffl").checked) {
                            [sText, n2] = this.formatText(sText, "ts_ligature_ffl_undo");
                        }
                        if (document.getElementById("o_ts_ligature_fi").checked) {
                            [sText, n3] = this.formatText(sText, "ts_ligature_fi_undo");
                        }
                        if (document.getElementById("o_ts_ligature_fl").checked) {
                            [sText, n4] = this.formatText(sText, "ts_ligature_fl_undo");
                        }
                        if (document.getElementById("o_ts_ligature_ff").checked) {
                            [sText, n5] = this.formatText(sText, "ts_ligature_ff_undo");
                        }
                        if (document.getElementById("o_ts_ligature_ft").checked) {
                            [sText, n6] = this.formatText(sText, "ts_ligature_ft_undo");
                        }
                        if (document.getElementById("o_ts_ligature_st").checked) {
                            [sText, n7] = this.formatText(sText, "ts_ligature_st_undo");
                        }
                    }
                    document.getElementById('res_o_ts_ligature').textContent = n1 + n2 + n3 + n4 + n5 + n6 + n7;
                }
                document.getElementById("o_group_typo").checked = false;
                this.switchGroup("o_group_typo");
            }
            document.getElementById('progressbar').value = 5;

            // divers
            if (document.getElementById("o_group_misc").checked) {
                if (document.getElementById("o_ordinals_no_exponant").checked) {
                    if (document.getElementById("o_ordinals_exponant").checked) {
                        [sText, n1] = this.formatText(sText, "ordinals_exponant");
                    } else {
                        [sText, n1] = this.formatText(sText, "ordinals_no_exponant");
                    }
                    document.getElementById('res_o_ordinals_no_exponant').textContent = n1;
                }
                if (document.getElementById("o_etc").checked) {
                    [sText, n1] = this.formatText(sText, "etc");
                    document.getElementById('res_o_etc').textContent = n1;
                }
                if (document.getElementById("o_missing_hyphens").checked) {
                    [sText, n1] = this.formatText(sText, "missing_hyphens");
                    document.getElementById('res_o_missing_hyphens').textContent = n1;
                }
                if (document.getElementById("o_ma_word").checked) {
                    [sText, n1] = this.formatText(sText, "ma_word");
                    if (document.getElementById("o_ma_1letter_lowercase").checked) {
                        [sText, n1] = this.formatText(sText, "ma_1letter_lowercase");
                        if (document.getElementById("o_ma_1letter_uppercase").checked) {
                            [sText, n1] = this.formatText(sText, "ma_1letter_uppercase");
                        }
                    }
                    document.getElementById('res_o_ma_word').textContent = n1;
                }
                document.getElementById("o_group_misc").checked = false;
                this.switchGroup("o_group_misc");
            }
            document.getElementById('progressbar').value = document.getElementById('progressbar').max;
            // end of processing

            //window.setCursor("auto"); // restore pointer
            const t1 = Date.now();
            document.getElementById('time_res').textContent = this.getTimeRes((t1-t0)/1000);
        }
        catch (e) {
            Cu.reportError(e);
        }
        return sText;
    },
    formatText: function (sText, sOptName) {
        let nCount = 0;
        try {
            if (!tf.oReplTable.hasOwnProperty(sOptName)) {
                echo("# Error. TF: there is no option “" + sOptName+ "”.");
                return [sText, nCount];
            }
            for (let [zRgx, sRep] of tf.oReplTable[sOptName]) {
                nCount += (sText.match(zRgx) || []).length;
                sText = sText.replace(zRgx, sRep);
            }
        }
        catch (e) {
            Cu.reportError(e);
        }
        return [sText, nCount];
    }
}


/* EVENTS */

window.addEventListener("click", function (xEvent) {
    let xElem = xEvent.target;
    if (xElem.id && xElem.id.startsWith("o_group_")) {
        oTextFormatter.switchGroup(xElem.id);
        oTextFormatter.resetProgressBar();
    }
}, false);

window.addEventListener("load", function (xEvent) {
    oDictIgniter.init();
    oGrammarChecker.loadGC();
}, false);

window.addEventListener("compose-window-init", function (xEvent) {
    oGrammarChecker.loadUI();
    oGrammarChecker.closePanel();
    oGrammarChecker.clearPreview();
    oTextFormatter.init();
}, true);
