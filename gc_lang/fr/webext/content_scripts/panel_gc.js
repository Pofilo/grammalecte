// JavaScript

"use strict";

function onGrammalecteGCPanelClick (xEvent) {
    try {
        let xElem = xEvent.target;
        if (xElem.id) {
            if (xElem.id.startsWith("grammalecte_sugg")) {
                oGrammalecte.oGCPanel.applySuggestion(xElem.id);
            } else if (xElem.id === "grammalecte_tooltip_ignore") {
                oGrammalecte.oGCPanel.ignoreError(xElem.id);
            } else if (xElem.id.startsWith("grammalecte_check")) {
                oGrammalecte.oGCPanel.recheckParagraph(parseInt(xElem.dataset.para_num));
            } else if (xElem.id.startsWith("grammalecte_hide")) {
                xElem.parentNode.parentNode.style.display = "none";
            } else if (xElem.id.startsWith("grammalecte_err")
                       && xElem.className !== "grammalecte_error_corrected"
                       && xElem.className !== "grammalecte_error_ignored") {
                oGrammalecte.oGCPanel.oTooltip.show(xElem.id);
            } else if (xElem.id === "grammalecte_tooltip_url") {
                oGrammalecte.oGCPanel.openURL(xElem.dataset.url);
            } else {
                oGrammalecte.oGCPanel.oTooltip.hide();
            }
        } else {
            oGrammalecte.oGCPanel.oTooltip.hide();
        }
    }
    catch (e) {
        showError(e);
    }
}


class GrammalecteGrammarChecker extends GrammalectePanel {
    /*
        KEYS for identifiers:
            grammalecte_paragraph{Id} : [paragraph number]
            grammalecte_check{Id}     : [paragraph number]
            grammalecte_hide{Id}      : [paragraph number]
            grammalecte_error{Id}     : [paragraph number]-[error_number]
            grammalecte_sugg{Id}      : [paragraph number]-[error_number]--[suggestion_number]
    */

    constructor (...args) {
        super(...args);
        this.aIgnoredErrors = new Set();
        this.xContentNode = oGrammalecte.createNode("div", {id: "grammalecte_gc_panel_content"});
        this.xParagraphList = oGrammalecte.createNode("div", {id: "grammalecte_paragraph_list"});
        this.xContentNode.appendChild(this.xParagraphList);
        this.xPanelContent.addEventListener("click", onGrammalecteGCPanelClick, false);
        this.oTooltip = new GrammalecteTooltip(this.xContentNode);
        this.xPanelContent.appendChild(this.xContentNode);
        this.oNodeControl = new GrammalecteNodeControl();
    }

    start (xNode=null) {
        this.oTooltip.hide();
        this.clear();
        if (xNode) {
            if (xNode.tagName == "TEXTAREA") {
                this.oNodeControl.setNode(xNode);
            } else {
                this.addMessage("Cette zone de texte n’est pas un champ de formulaire “textarea” mais un node HTML éditable. Les modifications ne seront pas répercutées automatiquement. Une fois votre texte corrigé, vous pouvez utiliser le bouton ‹∑› pour copier le texte dans le presse-papiers.");
            }
        }
    }

    clear () {
        while (this.xParagraphList.firstChild) {
            this.xParagraphList.removeChild(this.xParagraphList.firstChild);
        }
        this.aIgnoredErrors.clear();
    }

    hide () {
        this.xPanel.style.display = "none";
        this.oNodeControl.clear();
    }

    addParagraphResult (oResult) {
        try {
            if (oResult && (oResult.sParagraph.trim() !== "" || oResult.aGrammErr.length > 0 || oResult.aSpellErr.length > 0)) {
                let xNodeDiv = oGrammalecte.createNode("div", {className: "grammalecte_paragraph_block"});
                // actions
                let xActionsBar = oGrammalecte.createNode("div", {className: "grammalecte_paragraph_actions"});
                xActionsBar.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_check" + oResult.iParaNum, className: "grammalecte_paragraph_button grammalecte_green", textContent: "Réanalyser"}, {para_num: oResult.iParaNum}));
                xActionsBar.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_hide" + oResult.iParaNum, className: "grammalecte_paragraph_button grammalecte_red", textContent: "×", style: "font-weight: bold;"}));
                // paragraph
                let xParagraph = oGrammalecte.createNode("p", {id: "grammalecte_paragraph"+oResult.iParaNum, className: "grammalecte_paragraph", lang: "fr", contentEditable: "true"}, {para_num: oResult.iParaNum});
                xParagraph.setAttribute("spellcheck", "false"); // doesn’t seem possible to use “spellcheck” as a common attribute.
                xParagraph.addEventListener("keyup", function (xEvent) {
                    this.oNodeControl.setParagraph(parseInt(xEvent.target.dataset.para_num), this.purgeText(xEvent.target.textContent));
                    this.oNodeControl.write();
                }.bind(this)
                , true);
                this._tagParagraph(xParagraph, oResult.sParagraph, oResult.iParaNum, oResult.aGrammErr, oResult.aSpellErr);
                // creation
                xNodeDiv.appendChild(xActionsBar);
                xNodeDiv.appendChild(xParagraph);
                this.xParagraphList.appendChild(xNodeDiv);
            }
        }
        catch (e) {
            showError(e);
        }
    }

    recheckParagraph (iParaNum) {
        let sParagraphId = "grammalecte_paragraph" + iParaNum;
        let xParagraph = document.getElementById(sParagraphId);
        this.blockParagraph(xParagraph);
        let sText = this.purgeText(xParagraph.textContent);
        xGrammalectePort.postMessage({
            sCommand: "parseAndSpellcheck1",
            dParam: {sText: sText, sCountry: "FR", bDebug: false, bContext: false},
            dInfo: {sParagraphId: sParagraphId}
        });
        this.oNodeControl.setParagraph(iParaNum, sText);
        this.oNodeControl.write();
    }

    refreshParagraph (sParagraphId, oResult) {
        try {
            let xParagraph = document.getElementById(sParagraphId);
            xParagraph.className = (oResult.aGrammErr.length || oResult.aSpellErr.length) ? "grammalecte_paragraph softred" : "grammalecte_paragraph";
            xParagraph.textContent = "";
            this._tagParagraph(xParagraph, oResult.sParagraph, sParagraphId.slice(21), oResult.aGrammErr, oResult.aSpellErr);
            this.freeParagraph(xParagraph);
        }
        catch (e) {
            showError(e);
        }
    }

    _tagParagraph (xParagraph, sParagraph, iParaNum, aSpellErr, aGrammErr) {
        try {
            if (aGrammErr.length === 0  &&  aSpellErr.length === 0) {
                xParagraph.textContent = sParagraph;
                return;
            }
            aGrammErr.push(...aSpellErr);
            aGrammErr.sort(function (a, b) {
                if (a["nStart"] < b["nStart"])
                    return -1;
                if (a["nStart"] > b["nStart"])
                    return 1;
                return 0;
            });
            let nErr = 0; // we count errors to give them an identifier
            let nEndLastErr = 0;
            for (let oErr of aGrammErr) {
                let nStart = oErr["nStart"];
                let nEnd = oErr["nEnd"];
                if (nStart >= nEndLastErr) {
                    oErr['sErrorId'] = iParaNum + "-" + nErr.toString(); // error identifier
                    oErr['sIgnoredKey'] = iParaNum + ":" + nStart.toString() + ":" + sParagraph.slice(nStart, nEnd);
                    if (nEndLastErr < nStart) {
                        xParagraph.appendChild(document.createTextNode(sParagraph.slice(nEndLastErr, nStart)));
                    }
                    xParagraph.appendChild(this._createError(sParagraph.slice(nStart, nEnd), oErr));
                    nEndLastErr = nEnd;
                }
                nErr += 1;
            }
            if (nEndLastErr <= sParagraph.length) {
                xParagraph.appendChild(document.createTextNode(sParagraph.slice(nEndLastErr)));
            }
        }
        catch (e) {
            showError(e);
        }
    }

    _createError (sUnderlined, oErr) {
        let xNodeErr = document.createElement("mark");
        xNodeErr.id = "grammalecte_err" + oErr['sErrorId'];
        xNodeErr.textContent = sUnderlined;
        xNodeErr.dataset.error_id = oErr['sErrorId'];
        xNodeErr.dataset.ignored_key = oErr['sIgnoredKey'];
        xNodeErr.dataset.error_type = (oErr['sType'] === "WORD") ? "spelling" : "grammar";
        if (xNodeErr.dataset.error_type === "grammar") {
            xNodeErr.dataset.gc_message = oErr['sMessage'];
            xNodeErr.dataset.gc_url = oErr['URL'];
            if (xNodeErr.dataset.gc_message.includes(" #")) {
                xNodeErr.dataset.line_id = oErr['sLineId'];
                xNodeErr.dataset.rule_id = oErr['sRuleId'];
            }
            xNodeErr.dataset.suggestions = oErr["aSuggestions"].join("|");
        }
        xNodeErr.className = (this.aIgnoredErrors.has(xNodeErr.dataset.ignored_key)) ? "grammalecte_error_ignored" : "grammalecte_error grammalecte_error_" + oErr['sType'];
        return xNodeErr;
    }

    blockParagraph (xParagraph) {
        xParagraph.contentEditable = "false";
        document.getElementById("grammalecte_check"+xParagraph.dataset.para_num).textContent = "Analyse…";
    }

    freeParagraph (xParagraph) {
        xParagraph.contentEditable = "true";
        document.getElementById("grammalecte_check"+xParagraph.dataset.para_num).textContent = "Réanalyser";
    }

    applySuggestion (sNodeSuggId) { // sugg
        try {
            let sErrorId = document.getElementById(sNodeSuggId).dataset.error_id;
            //let sParaNum = sErrorId.slice(0, sErrorId.indexOf("-"));
            let xNodeErr = document.getElementById("grammalecte_err" + sErrorId);
            xNodeErr.textContent = document.getElementById(sNodeSuggId).textContent;
            xNodeErr.className = "grammalecte_error_corrected";
            xNodeErr.removeAttribute("style");
            this.oTooltip.hide();
            this.recheckParagraph(parseInt(sErrorId.slice(0, sErrorId.indexOf("-"))));
        }
        catch (e) {
            showError(e);
        }
    }

    ignoreError (sIgnoreButtonId) {  // ignore
        try {
            let sErrorId = document.getElementById(sIgnoreButtonId).dataset.error_id;
            let xNodeErr = document.getElementById("grammalecte_err" + sErrorId);
            this.aIgnoredErrors.add(xNodeErr.dataset.ignored_key);
            xNodeErr.className = "grammalecte_error_ignored";
            this.oTooltip.hide();
        }
        catch (e) {
            showError(e);
        }
    }

    purgeText (sText) {
        return sText.replace(/&nbsp;/g, " ").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
    }

    addSummary () {
        // todo
    }

    addMessage (sMessage) {
        let xNode = oGrammalecte.createNode("div", {className: "grammalecte_panel_message", textContent: sMessage});
        this.xParagraphList.appendChild(xNode);
    }

    _copyToClipboard (sText)  {
        // recipe from https://github.com/mdn/webextensions-examples/blob/master/context-menu-copy-link-with-types/clipboard-helper.js
        function setClipboardData (xEvent) {
            document.removeEventListener("copy", setClipboardData, true);
            xEvent.stopImmediatePropagation();
            xEvent.preventDefault();
            xEvent.clipboardData.setData("text/plain", sText);
        };

        document.addEventListener("copy", setClipboardData, true);
        document.execCommand("copy");
    }

    copyTextToClipboard () {
        this.startWaitIcon();
        try {
            let xClipboardButton = document.getElementById("grammalecte_clipboard_button");
            xClipboardButton.textContent = "->>";
            let sText = "";
            for (let xNode of document.getElementsByClassName("grammalecte_paragraph")) {
                sText += xNode.textContent + "\n";
            }
            this._copyToClipboard(sText);
            xClipboardButton.textContent = "OK";
            window.setTimeout(function() { xClipboardButton.textContent = "∑"; } , 2000);
        }
        catch (e) {
            showError(e);
        }
        this.stopWaitIcon();
    }
}


class GrammalecteTooltip {

    constructor (xContentNode) {
        this.sErrorId = null;
        this.xTooltip = oGrammalecte.createNode("div", {id: "grammalecte_tooltip"});
        this.xTooltipArrow = oGrammalecte.createNode("img", {
            id: "grammalecte_tooltip_arrow",
            src: " data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwAAADsABataJCQAAABl0RVh0U29mdHdhcmUAcGFpbnQubmV0IDQuMC4xNzNun2MAAAAnSURBVChTY/j//z8cq/kW/wdhZDEMSXRFWCVhGKwAmwQyHngFxf8B5fOGYfeFpYoAAAAASUVORK5CYII=",
            alt: "^",
        });
        this.xTooltipSuggBlock = oGrammalecte.createNode("div", {id: "grammalecte_tooltip_sugg_block"});
        let xMessageBlock = oGrammalecte.createNode("div", {id: "grammalecte_tooltip_message_block"});
        xMessageBlock.appendChild(oGrammalecte.createNode("p", {id: "grammalecte_tooltip_rule_id"}));
        xMessageBlock.appendChild(oGrammalecte.createNode("p", {id: "grammalecte_tooltip_message", textContent: "Erreur."}));
        let xActions = xMessageBlock.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_tooltip_actions"}));
        xActions.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_tooltip_ignore", textContent: "Ignorer"}));
        xActions.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_tooltip_url", textContent: "Voulez-vous en savoir plus ?…"}, {url: ""}));
        xMessageBlock.appendChild(xActions);
        this.xTooltip.appendChild(xMessageBlock);
        this.xTooltip.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_tooltip_sugg_title", textContent: "SUGGESTIONS :"}));
        this.xTooltip.appendChild(this.xTooltipSuggBlock);
        xContentNode.appendChild(this.xTooltip);
        xContentNode.appendChild(this.xTooltipArrow);
    }

    show (sNodeErrorId) {  // err
        try {
            let xNodeErr = document.getElementById(sNodeErrorId);
            this.sErrorId = xNodeErr.dataset.error_id; // we store error_id here to know if spell_suggestions are given to the right word.
            let nLimit = 500 - 330; // paragraph width - tooltip width
            this.xTooltipArrow.style.top = (xNodeErr.offsetTop + 16) + "px";
            this.xTooltipArrow.style.left = (xNodeErr.offsetLeft + Math.floor((xNodeErr.offsetWidth / 2))-4) + "px"; // 4 is half the width of the arrow.
            this.xTooltip.style.top = (xNodeErr.offsetTop + 20) + "px";
            this.xTooltip.style.left = (xNodeErr.offsetLeft > nLimit) ? nLimit + "px" : xNodeErr.offsetLeft + "px";
            if (xNodeErr.dataset.error_type === "grammar") {
                // grammar error
                if (xNodeErr.dataset.gc_message.includes(" ##")) {
                    let n = xNodeErr.dataset.gc_message.indexOf(" ##");
                    document.getElementById("grammalecte_tooltip_message").textContent = xNodeErr.dataset.gc_message.slice(0, n);
                    document.getElementById("grammalecte_tooltip_rule_id").textContent = "Règle : " + xNodeErr.dataset.gc_message.slice(n+2);
                    document.getElementById("grammalecte_tooltip_rule_id").style.display = "block";
                } else {
                    document.getElementById("grammalecte_tooltip_message").textContent = xNodeErr.dataset.gc_message;
                    document.getElementById("grammalecte_tooltip_rule_id").style.display = "none";
                }
                if (xNodeErr.dataset.gc_url != "") {
                    document.getElementById("grammalecte_tooltip_url").dataset.url = xNodeErr.dataset.gc_url;
                    document.getElementById("grammalecte_tooltip_url").style.display = "inline";
                } else {
                    document.getElementById("grammalecte_tooltip_url").dataset.url = "";
                    document.getElementById("grammalecte_tooltip_url").style.display = "none";
                }
                document.getElementById("grammalecte_tooltip_ignore").dataset.error_id = xNodeErr.dataset.error_id;
                let iSugg = 0;
                this.clearSuggestionBlock();
                if (xNodeErr.dataset.suggestions.length > 0) {
                    for (let sSugg of xNodeErr.dataset.suggestions.split("|")) {
                        this.xTooltipSuggBlock.appendChild(this._createSuggestion(xNodeErr.dataset.error_id, iSugg, sSugg));
                        this.xTooltipSuggBlock.appendChild(document.createTextNode(" "));
                        iSugg += 1;
                    }
                } else {
                    this.xTooltipSuggBlock.textContent = "Aucune.";
                }
            }
            if (xNodeErr.dataset.error_type === "spelling") {
                // spelling mistake
                document.getElementById("grammalecte_tooltip_message").textContent = "Mot inconnu du dictionnaire.";
                document.getElementById("grammalecte_tooltip_ignore").dataset.error_id = xNodeErr.dataset.error_id;
                this.clearSuggestionBlock();
                this.xTooltipSuggBlock.textContent = "Recherche de graphies possibles…";
                xGrammalectePort.postMessage({
                    sCommand: "getSpellSuggestions",
                    dParam: {sWord: xNodeErr.textContent},
                    dInfo: {sErrorId: xNodeErr.dataset.error_id}
                });
            }
            this.xTooltipArrow.style.display = "block";
            this.xTooltip.style.display = "block";
        }
        catch (e) {
            showError(e);
        }
    }

    clearSuggestionBlock () {
        while (this.xTooltipSuggBlock.firstChild) {
            this.xTooltipSuggBlock.removeChild(this.xTooltipSuggBlock.firstChild);
        }
    }

    setTooltipColor () {
        // todo
    }

    hide () {
        this.xTooltipArrow.style.display = "none";
        this.xTooltip.style.display = "none";
    }

    _createSuggestion (sErrorId, iSugg, sSugg) {
        let xNodeSugg = document.createElement("div");
        xNodeSugg.id = "grammalecte_sugg" + sErrorId + "--" + iSugg.toString();
        xNodeSugg.className = "grammalecte_tooltip_sugg";
        xNodeSugg.dataset.error_id = sErrorId;
        xNodeSugg.textContent = sSugg;
        return xNodeSugg;
    }

    setSpellSuggestionsFor (sWord, aSugg, sErrorId) {
        // spell checking suggestions
        try {
            if (sErrorId === this.sErrorId) {
                let xSuggBlock = document.getElementById("grammalecte_tooltip_sugg_block");
                xSuggBlock.textContent = "";
                if (!aSugg || aSugg.length == 0) {
                    xSuggBlock.appendChild(document.createTextNode("Aucune."));
                } else {
                    let iSugg = 0;
                    for (let sSugg of aSugg) {
                        xSuggBlock.appendChild(this._createSuggestion(sErrorId, iSugg, sSugg));
                        xSuggBlock.appendChild(document.createTextNode(" "));
                        iSugg += 1;
                    }
                }
            }
        }
        catch (e) {
            xSuggBlock.appendChild(document.createTextNode("# Oups. Le mécanisme de suggestion orthographique a rencontré un bug… (Ce module est encore en phase β.)"));
            showError(e);
        }
    }
}


class GrammalecteNodeControl {

    constructor () {
        this.xNode = null;
        this.dParagraph = new Map();
        this.bTextArea = null;
        this.bWriteEN = false;  // write editable node
    }

    setNode (xNode) {
        this.clear();
        this.xNode = xNode;
        this.bTextArea = (xNode.tagName == "TEXTAREA");
        this.xNode.disabled = true;
        this._loadText();
    }

    clear () {
        if (this.xNode !== null) {
            this.xNode.disabled = false;
            this.xNode = null;
        }
        this.dParagraph.clear();
    }

    setParagraph (iParagraph, sText) {
        if (this.xNode !== null) {
            this.dParagraph.set(iParagraph, sText);
        }
    }

    _loadText () {
        let sText = (this.bTextArea) ? this.xNode.value : this.xNode.innerText;
        let i = 0;
        let iStart = 0;
        let iEnd = 0;
        sText = sText.replace("\r\n", "\n").replace("\r", "\n").normalize("NFC");
        while ((iEnd = sText.indexOf("\n", iStart)) !== -1) {
            this.dParagraph.set(i, sText.slice(iStart, iEnd));
            i++;
            iStart = iEnd+1;
        }
        this.dParagraph.set(i, sText.slice(iStart));
        //console.log("Paragraphs number: " + (i+1));
    }

    write () {
        if (this.xNode !== null && (this.bTextArea || this.bWriteEN)) {
            let sText = "";
            this.dParagraph.forEach(function (val, key) {
                sText += val + "\n";
            });
            sText = sText.slice(0,-1).normalize("NFC");
            if (this.bTextArea) {
                this.xNode.value = sText;
            } else {
                this.xNode.textContent = sText;
            }
        }
    }
}
