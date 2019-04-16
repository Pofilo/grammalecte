// JavaScript

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global GrammalectePanel, oGrammalecte, xGrammalectePort, showError, window, document, console */

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
            } else if (xElem.id === "grammalecte_tooltip_url"  || xElem.id === "grammalecte_tooltip_db_search") {
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
        this.oTooltip = new GrammalecteTooltip(this.xParent, this.xContentNode);
        this.xPanelContent.appendChild(this.xContentNode);
        this.oNodeControl = new GrammalecteNodeControl();
    }

    start (xNode=null) {
        this.oTooltip.hide();
        this.clear();
        if (xNode) {
            this.oNodeControl.setNode(xNode);
            if (!(xNode.tagName == "TEXTAREA" || xNode.tagName == "INPUT")) {
                this.addMessage("Note : cette zone de texte n’est pas un champ de formulaire “textarea” mais un node HTML éditable. Une telle zone de texte est susceptible de contenir des éléments non textuels qui seront effacés lors de la correction.");
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
                xActionsBar.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_check" + oResult.iParaNum, className: "grammalecte_paragraph_button grammalecte_green", textContent: "A", title: "Réanalyser…"}, {para_num: oResult.iParaNum}));
                xActionsBar.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_hide" + oResult.iParaNum, className: "grammalecte_paragraph_button grammalecte_red", textContent: "×", title: "Cacher", style: "font-weight: bold;"}));
                // paragraph
                let xParagraph = oGrammalecte.createNode("p", {id: "grammalecte_paragraph"+oResult.iParaNum, className: "grammalecte_paragraph", lang: "fr", contentEditable: "true"}, {para_num: oResult.iParaNum});
                xParagraph.setAttribute("spellcheck", "false"); // doesn’t seem possible to use “spellcheck” as a common attribute.
                xParagraph.dataset.timer_id = "0";
                xParagraph.addEventListener("input", function (xEvent) {
                    window.clearTimeout(parseInt(xParagraph.dataset.timer_id));
                    xParagraph.dataset.timer_id = window.setTimeout(this.recheckParagraph.bind(this), 3000, oResult.iParaNum);
                    let [nStart, nEnd] = oGrammalecte.getCaretPosition(xParagraph);
                    xParagraph.dataset.caret_position_start = nStart;
                    xParagraph.dataset.caret_position_end = nEnd;
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
        let xParagraph = this.xParent.getElementById(sParagraphId);
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
            let xParagraph = this.xParent.getElementById(sParagraphId);
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
        xNodeErr.className = (this.aIgnoredErrors.has(xNodeErr.dataset.ignored_key)) ? "grammalecte_error_ignored" : "grammalecte_error";
        xNodeErr.style.backgroundColor = (oErr['sType'] === "WORD") ? "hsl(0, 50%, 50%)" : oErr["aColor"];
        return xNodeErr;
    }

    blockParagraph (xParagraph) {
        xParagraph.contentEditable = "false";
        this.xParent.getElementById("grammalecte_check"+xParagraph.dataset.para_num).textContent = "!!";
        this.xParent.getElementById("grammalecte_check"+xParagraph.dataset.para_num).style.backgroundColor = "hsl(0, 50%, 50%)";
        this.xParent.getElementById("grammalecte_check"+xParagraph.dataset.para_num).style.boxShadow = "0 0 0 3px hsla(0, 0%, 50%, .2)";
        this.xParent.getElementById("grammalecte_check"+xParagraph.dataset.para_num).style.animation = "grammalecte-pulse 1s linear infinite";

    }

    freeParagraph (xParagraph) {
        xParagraph.contentEditable = "true";
        let nStart = parseInt(xParagraph.dataset.caret_position_start);
        let nEnd = parseInt(xParagraph.dataset.caret_position_end);
        oGrammalecte.setCaretPosition(xParagraph, nStart, nEnd);
        this.xParent.getElementById("grammalecte_check"+xParagraph.dataset.para_num).textContent = "A";
        this.xParent.getElementById("grammalecte_check"+xParagraph.dataset.para_num).style.backgroundColor = "hsl(120, 30%, 50%)";
        this.xParent.getElementById("grammalecte_check"+xParagraph.dataset.para_num).style.animation = "";
        setTimeout(() => { this.xParent.getElementById("grammalecte_check"+xParagraph.dataset.para_num).style.boxShadow = ""; }, 1000);
    }

    applySuggestion (sNodeSuggId) { // sugg
        try {
            let sErrorId = this.xParent.getElementById(sNodeSuggId).dataset.error_id;
            //let sParaNum = sErrorId.slice(0, sErrorId.indexOf("-"));
            let xNodeErr = this.xParent.getElementById("grammalecte_err" + sErrorId);
            xNodeErr.textContent = this.xParent.getElementById(sNodeSuggId).textContent;
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
            let sErrorId = this.xParent.getElementById(sIgnoreButtonId).dataset.error_id;
            let xNodeErr = this.xParent.getElementById("grammalecte_err" + sErrorId);
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
        }
        document.addEventListener("copy", setClipboardData, true);
        document.execCommand("copy");
    }

    copyTextToClipboard () {
        this.startWaitIcon();
        try {
            let xClipboardButton = this.xParent.getElementById("grammalecte_clipboard_button");
            xClipboardButton.textContent = "->>";
            let sText = "";
            // Quand c'est dans un shadow "this.xParent.getElementsByClassName" n'existe pas.
            let xElem = this.xParent.getElementById("grammalecte_gc_panel");
            for (let xNode of xElem.getElementsByClassName("grammalecte_paragraph")) {
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

    constructor (xParent, xContentNode) {
        this.xParent = xParent;
        this.sErrorId = null;
        this.bDebug = false;
        this.xTooltip = oGrammalecte.createNode("div", {id: "grammalecte_tooltip"});
        this.xTooltipArrow = oGrammalecte.createNode("img", {
            id: "grammalecte_tooltip_arrow",
            src: " data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwAAADsABataJCQAAABl0RVh0U29mdHdhcmUAcGFpbnQubmV0IDQuMC4xNzNun2MAAAAnSURBVChTY/j//z8cq/kW/wdhZDEMSXRFWCVhGKwAmwQyHngFxf8B5fOGYfeFpYoAAAAASUVORK5CYII=",
            alt: "^",
        });
        // message
        let xMessageBlock = oGrammalecte.createNode("div", {id: "grammalecte_tooltip_message_block"});
        xMessageBlock.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_tooltip_rule_id"}));
        xMessageBlock.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_tooltip_message", textContent: "Erreur."}));
        this.xTooltip.appendChild(xMessageBlock);
        // suggestions
        this.xTooltip.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_tooltip_sugg_title", textContent: "SUGGESTIONS :"}));
        this.xTooltipSuggBlock = oGrammalecte.createNode("div", {id: "grammalecte_tooltip_sugg_block"});
        this.xTooltip.appendChild(this.xTooltipSuggBlock);
        // actions
        let xActions = oGrammalecte.createNode("div", {id: "grammalecte_tooltip_actions"});
        xActions.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_tooltip_ignore", textContent: "Ignorer"}));
        xActions.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_tooltip_url", textContent: "Voulez-vous en savoir plus ?…"}, {url: ""}));
        xActions.appendChild(oGrammalecte.createNode("div", {id: "grammalecte_tooltip_db_search", textContent: " ››› base de données"}, {url: ""}));
        this.xTooltip.appendChild(xActions);
        // add tooltip to the page
        xContentNode.appendChild(this.xTooltip);
        xContentNode.appendChild(this.xTooltipArrow);
    }

    show (sNodeErrorId) {  // err
        try {
            let xNodeErr = this.xParent.getElementById(sNodeErrorId);
            this.sErrorId = xNodeErr.dataset.error_id; // we store error_id here to know if spell_suggestions are given to the right word.
            let nTooltipLeftLimit = oGrammalecte.oGCPanel.getWidth() - 330; // paragraph width - tooltip width
            let nArrowLimit = oGrammalecte.oGCPanel.getWidth() - 20;
            this.xTooltipArrow.style.top = (xNodeErr.offsetTop + 16) + "px";
            let nUsefulErrorWidth = ((xNodeErr.offsetLeft + xNodeErr.offsetWidth) > nArrowLimit) ? (nArrowLimit - xNodeErr.offsetLeft) : xNodeErr.offsetWidth;
            this.xTooltipArrow.style.left = (xNodeErr.offsetLeft + Math.floor((nUsefulErrorWidth / 2)) - 4) + "px"; // 4 is half the width of the arrow.
            this.xTooltip.style.top = (xNodeErr.offsetTop + 20) + "px";
            this.xTooltip.style.left = (xNodeErr.offsetLeft > nTooltipLeftLimit) ? nTooltipLeftLimit + "px" : xNodeErr.offsetLeft + "px";
            if (xNodeErr.dataset.error_type === "grammar") {
                // grammar error
                this.xParent.getElementById("grammalecte_tooltip_db_search").style.display = "none";
                if (xNodeErr.dataset.gc_message.includes(" ##")) {
                    this.bDebug = true;
                    // display rule id
                    let n = xNodeErr.dataset.gc_message.indexOf(" ##");
                    this.xParent.getElementById("grammalecte_tooltip_message").textContent = xNodeErr.dataset.gc_message.slice(0, n);
                    this.xParent.getElementById("grammalecte_tooltip_rule_id").textContent = "Règle : " + xNodeErr.dataset.gc_message.slice(n+2);
                    this.xParent.getElementById("grammalecte_tooltip_rule_id").style.display = "block";
                } else {
                    this.bDebug = false;
                    this.xParent.getElementById("grammalecte_tooltip_message").textContent = xNodeErr.dataset.gc_message;
                    this.xParent.getElementById("grammalecte_tooltip_rule_id").style.display = "none";
                }
                if (xNodeErr.dataset.gc_url != "") {
                    this.xParent.getElementById("grammalecte_tooltip_url").dataset.url = xNodeErr.dataset.gc_url;
                    this.xParent.getElementById("grammalecte_tooltip_url").style.display = "inline";
                } else {
                    this.xParent.getElementById("grammalecte_tooltip_url").dataset.url = "";
                    this.xParent.getElementById("grammalecte_tooltip_url").style.display = "none";
                }
                this.xParent.getElementById("grammalecte_tooltip_ignore").dataset.error_id = xNodeErr.dataset.error_id;
                let iSugg = 0;
                this.clearSuggestionBlock();
                if (xNodeErr.dataset.suggestions.length > 0) {
                    for (let sSugg of xNodeErr.dataset.suggestions.split("|")) {
                        this.xTooltipSuggBlock.appendChild(this._createSuggestion(xNodeErr.dataset.error_id, 0, iSugg, sSugg));
                        this.xTooltipSuggBlock.appendChild(document.createTextNode(" "));
                        iSugg += 1;
                    }
                } else {
                    this.xTooltipSuggBlock.textContent = "Aucune.";
                }
            }
            if (xNodeErr.dataset.error_type === "spelling") {
                // spelling mistake
                this.xParent.getElementById("grammalecte_tooltip_message").textContent = "Mot inconnu du dictionnaire.";
                this.xParent.getElementById("grammalecte_tooltip_ignore").dataset.error_id = xNodeErr.dataset.error_id;
                this.xParent.getElementById("grammalecte_tooltip_rule_id").style.display = "none";
                this.xParent.getElementById("grammalecte_tooltip_url").dataset.url = "";
                this.xParent.getElementById("grammalecte_tooltip_url").style.display = "none";
                if (this.bDebug) {
                    this.xParent.getElementById("grammalecte_tooltip_db_search").style.display = "inline";
                    this.xParent.getElementById("grammalecte_tooltip_db_search").dataset.url = "https://grammalecte.net/dictionary.php?prj=fr&lemma="+xNodeErr.textContent;
                } else {
                    this.xParent.getElementById("grammalecte_tooltip_db_search").style.display = "none";
                }
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

    _createSuggestion (sErrorId, iSuggBlock, iSugg, sSugg) {
        let xNodeSugg = document.createElement("div");
        xNodeSugg.id = "grammalecte_sugg" + sErrorId + "-" + iSuggBlock.toString() + "-" + iSugg.toString();
        xNodeSugg.className = "grammalecte_tooltip_sugg";
        xNodeSugg.dataset.error_id = sErrorId;
        xNodeSugg.textContent = sSugg;
        return xNodeSugg;
    }

    setSpellSuggestionsFor (sWord, aSugg, iSuggBlock, sErrorId) {
        // spell checking suggestions
        try {
            if (sErrorId === this.sErrorId) {
                let xSuggBlock = this.xParent.getElementById("grammalecte_tooltip_sugg_block");
                if (iSuggBlock == 0) {
                    xSuggBlock.textContent = "";
                }
                if (!aSugg || aSugg.length == 0) {
                    if (iSuggBlock == 0) {
                        xSuggBlock.appendChild(document.createTextNode("Aucune."));
                    }
                } else {
                    if (iSuggBlock > 0) {
                        xSuggBlock.appendChild(oGrammalecte.createNode("div", {className: "grammalecte_tooltip_other_sugg_title", textContent: "AUTRES SUGGESTIONS :"}));
                    }
                    let iSugg = 0;
                    for (let sSugg of aSugg) {
                        xSuggBlock.appendChild(this._createSuggestion(sErrorId, iSuggBlock, iSugg, sSugg));
                        xSuggBlock.appendChild(document.createTextNode(" "));
                        iSugg += 1;
                    }
                }
            }
        }
        catch (e) {
            let xSuggBlock = this.xParent.getElementById("grammalecte_tooltip_sugg_block");
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
    }

    setNode (xNode) {
        this.clear();
        this.xNode = xNode;
        this.bTextArea = (xNode.tagName == "TEXTAREA" || xNode.tagName == "INPUT");
        this.xNode.disabled = true;
        this._loadText();
    }

    clear () {
        if (this.xNode !== null) {
            this.xNode.disabled = false;
            this.bTextArea = false;
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
        sText = sText.replace(/\r\n/g, "\n").replace(/\r/g, "\n").replace(/­/g, "").normalize("NFC");
        while ((iEnd = sText.indexOf("\n", iStart)) !== -1) {
            this.dParagraph.set(i, sText.slice(iStart, iEnd));
            i++;
            iStart = iEnd+1;
        }
        this.dParagraph.set(i, sText.slice(iStart));
        //console.log("Paragraphs number: " + (i+1));
    }

    eraseContent () {
        while (this.xNode.firstChild) {
            this.xNode.removeChild(this.xNode.firstChild);
        }
    }

    write () {
        if (this.xNode !== null) {
            let sText = "";
            if (this.bTextArea) {
                this.dParagraph.forEach(function (val, key) {
                    sText += val + "\n";
                });
                this.xNode.value = sText.slice(0,-1).normalize("NFC");
            } else {
                this.eraseContent();
                this.dParagraph.forEach((val, key) => {
                    this.xNode.appendChild(document.createTextNode(val.normalize("NFC")));
                    this.xNode.appendChild(document.createElement("br"));
                });
                /*
                this.dParagraph.forEach(function (val, key) {
                    sText += val + "<br/>";
                });
                this.xNode.innerHTML = sText.normalize("NFC");
                */
            }
        }
    }
}
