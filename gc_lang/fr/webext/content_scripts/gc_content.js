// JavaScript

"use strict";

const oGCPanelContent = {

    _xContentNode: createNode("div", {id: "grammalecte_gc_panel_content"}),

    aIgnoredErrors: new Map(),

    getNode: function () {
        return this._xContentNode;
    },

    clear: function () {
        while (this._xContentNode.firstChild) {
            this._xContentNode.removeChild(this._xContentNode.firstChild);
        }
    },

    addParagraphResult: function (oResult) {
        try {
            if (oResult) {
                let xNodeDiv = createNode("div", {className: "grammalecte_paragraph_block"});
                // actions
                let xActionsBar = createNode("div", {className: "grammalecte_paragraph_actions"});
                let xCloseButton = createNode("div", {id: "end" + oResult.sParaNum, className: "grammalecte_paragraph_close_button", textContent: "×"});
                let xAnalyseButton = createNode("div", {id: "check" + oResult.sParaNum, className: "grammalecte_paragraph_analyse_button", textContent: "Réanalyser"});
                xActionsBar.appendChild(xAnalyseButton);
                xActionsBar.appendChild(xCloseButton);
                // paragraph
                let xParagraph = createNode("p", {id: "paragr"+oResult.sParaNum, lang: "fr", spellcheck: "false", contenteditable: "true"});
                xParagraph.className = (oResult.aGrammErr.length || oResult.aSpellErr.length) ? "grammalecte_paragraph softred" : "grammalecte_paragraph";
                this._tagParagraph(xParagraph, oResult.sParagraph, oResult.sParaNum, oResult.aGrammErr, oResult.aSpellErr);
                // creation
                xNodeDiv.appendChild(xActionsBar);
                xNodeDiv.appendChild(xParagraph);
                this._xContentNode.appendChild(xNodeDiv);
            }
        }
        catch (e) {
            showError(e);
        }
    },

    refreshParagraph: function (oResult) {
        try {
            let xParagraph = document.getElementById("paragr"+sIdParagr);
            xParagraph.className = (oResult.aGrammErr.length || oResult.aSpellErr.length) ? "grammalecte_paragraph softred" : "grammalecte_paragraph";
            xParagraph.textContent = "";
            this._tagParagraph(xParagraph, oResult.sParagraph, oResult.sParaNum, oResult.aGrammErr, oResult.aSpellErr);
        }
        catch (e) {
            showError(e);
        }
    },

    _tagParagraph: function (xParagraph, sParagraph, sParaNum, aSpellErr, aGrammErr) {
        try {
            if (aGrammErr.length === 0  &&  aSpellErr.length === 0) {
                xParagraph.textContent = sParagraph;
                return
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
                    oErr['sErrorId'] = sParaNum + "_" + nErr.toString(); // error identifier
                    oErr['sIgnoredKey'] = sParaNum + ":" + nStart.toString() + ":" + nEnd.toString() + ":" + sParagraph.slice(nStart, nEnd);
                    if (nEndLastErr < nStart) {
                        xParagraph.appendChild(document.createTextNode(sParagraph.slice(nEndLastErr, nStart)));
                    }
                    xParagraph.appendChild(this._createError(sParagraph.slice(nStart, nEnd), oErr));
                    xParagraph.insertAdjacentHTML("beforeend", "<!-- err_end -->");
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
    },

    _createError: function (sUnderlined, oErr) {
        let xNodeErr = document.createElement("u");
        xNodeErr.id = "err" + oErr['sErrorId'];
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
        xNodeErr.className = (this.aIgnoredErrors.has(xNodeErr.dataset.ignored_key)) ? "ignored" : "error " + oErr['sType'];
        return xNodeErr;
    },

    applySuggestion: function (sSuggId) { // sugg
        try {
            let sErrorId = document.getElementById(sSuggId).dataset.error_id;
            let sIdParagr = sErrorId.slice(0, sErrorId.indexOf("_"));
            startWaitIcon("paragr"+sIdParagr);
            let xNodeErr = document.getElementById("err" + sErrorId);
            xNodeErr.textContent = document.getElementById(sSuggId).textContent;
            xNodeErr.className = "corrected";
            xNodeErr.removeAttribute("style");
            self.port.emit("correction", sIdParagr, getPurgedTextOfParagraph("paragr"+sIdParagr));
            this.hideAllTooltips();
            stopWaitIcon("paragr"+sIdParagr);
        }
        catch (e) {
            showError(e);
        }
    },

    ignoreError: function (sIgnoreButtonId) {  // ignore
        try {
            //console.log("ignore button: " + sIgnoreButtonId + " // error id: " + document.getElementById(sIgnoreButtonId).dataset.error_id);
            let xNodeErr = document.getElementById("err"+document.getElementById(sIgnoreButtonId).dataset.error_id);
            this.aIgnoredErrors.add(xNodeErr.dataset.ignored_key);
            xNodeErr.className = "ignored";
            xNodeErr.removeAttribute("style");
            this.hideAllTooltips();
        }
        catch (e) {
            showError(e);
        }
    },

    showTooltip: function (sNodeErrorId) {  // err
        try {
            this.hideAllTooltips();
            let xNodeErr = document.getElementById(sNodeErrorId);
            let sTooltipId = (xNodeErr.dataset.error_type === "grammar") ? "gc_tooltip" : "sc_tooltip";
            let xNodeTooltip = document.getElementById(sTooltipId);
            let xNodeTooltipArrow = document.getElementById(sTooltipId+"_arrow"); 
            let nLimit = nPanelWidth - 330; // paragraph width - tooltip width
            xNodeTooltipArrow.style.top = (xNodeErr.offsetTop + 16) + "px"
            xNodeTooltipArrow.style.left = (xNodeErr.offsetLeft + Math.floor((xNodeErr.offsetWidth / 2))-4) + "px" // 4 is half the width of the arrow.
            xNodeTooltip.style.top = (xNodeErr.offsetTop + 20) + "px";
            xNodeTooltip.style.left = (xNodeErr.offsetLeft > nLimit) ? nLimit + "px" : xNodeErr.offsetLeft + "px";
            if (xNodeErr.dataset.error_type === "grammar") {
                // grammar error
                if (xNodeErr.dataset.gc_message.includes(" ##")) {
                    let n = xNodeErr.dataset.gc_message.indexOf(" ##");
                    document.getElementById("gc_message").textContent = xNodeErr.dataset.gc_message.slice(0, n);
                    document.getElementById("gc_rule_id").textContent = "Règle : " + xNodeErr.dataset.gc_message.slice(n+2);
                    document.getElementById("gc_rule_id").style.display = "block";
                } else {
                    document.getElementById("gc_message").textContent = xNodeErr.dataset.gc_message;
                }
                if (xNodeErr.dataset.gc_url != "") {
                    document.getElementById("gc_url").style.display = "inline";
                    document.getElementById("gc_url").setAttribute("href", xNodeErr.dataset.gc_url);
                } else {
                    document.getElementById("gc_url").style.display = "none";
                }
                document.getElementById("gc_ignore").dataset.error_id = xNodeErr.dataset.error_id;
                let iSugg = 0;
                let xGCSugg = document.getElementById("gc_sugg_block");
                xGCSugg.textContent = "";
                for (let sSugg of xNodeErr.dataset.suggestions.split("|")) {
                    xGCSugg.appendChild(this._createSuggestion(xNodeErr.dataset.error_id, iSugg, sSugg));
                    xGCSugg.appendChild(document.createTextNode(" "));
                    iSugg += 1;
                }
            }
            xNodeTooltipArrow.style.display = "block";
            xNodeTooltip.style.display = "block";
            if (xNodeErr.dataset.error_type === "spelling") {
                // spelling mistake
                document.getElementById("sc_ignore").dataset.error_id = xNodeErr.dataset.error_id;
                //console.log("getSuggFor: " + xNodeErr.textContent.trim() + " // error_id: " + xNodeErr.dataset.error_id);
                self.port.emit("getSuggestionsForTo", xNodeErr.textContent.trim(), xNodeErr.dataset.error_id);
            }
        }
        catch (e) {
            showError(e);
        }
    },

    _createSuggestion: function (sErrId, iSugg, sSugg) {
        let xNodeSugg = document.createElement("a");
        xNodeSugg.id = "sugg" + sErrId + "-" + iSugg.toString();
        xNodeSugg.className = "sugg";
        xNodeSugg.dataset.error_id = sErrId;
        xNodeSugg.textContent = sSugg;
        return xNodeSugg;
    },

    setSpellSuggestionsFor: function (sWord, sSuggestions, sErrId) {
        // spell checking suggestions
        try {
            // console.log("setSuggestionsFor: " + sWord + " > " + sSuggestions + " // " + sErrId);
            let xSuggBlock = document.getElementById("sc_sugg_block");
            xSuggBlock.textContent = "";
            if (sSuggestions === "") {
                xSuggBlock.appendChild(document.createTextNode("Aucune."));
            } else if (sSuggestions.startsWith("#")) {
                xSuggBlock.appendChild(document.createTextNode(sSuggestions));
            } else {
                let lSugg = sSuggestions.split("|");
                let iSugg = 0;
                for (let sSugg of lSugg) {
                    xSuggBlock.appendChild(this._createSuggestion(sErrId, iSugg, sSugg));
                    xSuggBlock.appendChild(document.createTextNode(" "));
                    iSugg += 1;
                }
            }
        }
        catch (e) {
            showError(e);
        }
    },

    hideAllTooltips: function () {
        document.getElementById("gc_tooltip").style.display = "none";
        document.getElementById("gc_rule_id").style.display = "none";
        document.getElementById("sc_tooltip").style.display = "none";
        document.getElementById("gc_tooltip_arrow").style.display = "none";
        document.getElementById("sc_tooltip_arrow").style.display = "none";
    },

    addSummary: function () {
        // todo
    },

    addMessage: function (sMessage) {
        let xNode = createNode("div", {className: "grammalecte_gc_panel_message", textContent: sMessage});
        this._xContentNode.appendChild(xNode);
    }
}

    

    

    





function sendBackAndCheck (sCheckButtonId) {  // check
    startWaitIcon();
    let sIdParagr = sCheckButtonId.slice(5);
    self.port.emit("modifyAndCheck", sIdParagr, getPurgedTextOfParagraph("paragr"+sIdParagr));
    stopWaitIcon();
}





function getPurgedTextOfParagraph (sNodeParagrId) {
    let sText = document.getElementById(sNodeParagrId).textContent;
    sText = sText.replace(/&nbsp;/g, " ").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
    return sText;
}

function copyToClipboard () {
    startWaitIcon();
    try {
        let xClipboardButton = document.getElementById("clipboard_msg");
        xClipboardButton.textContent = "copie en cours…";
        let sText = "";
        for (let xNode of document.getElementById("errorlist").getElementsByClassName("paragraph")) {
            sText += xNode.textContent + "\n";
        }
        self.port.emit('copyToClipboard', sText);
        xClipboardButton.textContent = "-> presse-papiers";
        window.setTimeout(function() { xClipboardButton.textContent = "∑"; } , 3000);
    }
    catch (e) {
        console.log(e.lineNumber + ": " +e.message);
    }
    stopWaitIcon();
}

function startWaitIcon (sIdParagr=null) {
    if (sIdParagr) {
        document.getElementById(sIdParagr).disabled = true;
        document.getElementById(sIdParagr).style.opacity = .3;
    }
    document.getElementById("waiticon").hidden = false;
}

function stopWaitIcon (sIdParagr=null) {
    if (sIdParagr) {
        document.getElementById(sIdParagr).disabled = false;
        document.getElementById(sIdParagr).style.opacity = 1;
    }
    document.getElementById("waiticon").hidden = true;
}