// JavaScript

let nPanelWidth = 0;  // must be set at launch
let bExpanded = true;

/*
    Ignored errors
    idendified by <sIgnoredKey>
    sIgnoredKey: <iParagraph:nStart:nEnd:sUnderlined> 
*/
let aIgnoredErrors = new Set();


/*
    Events
*/

showSpecialMessage();


document.getElementById('close').addEventListener("click", function (event) {
    bExpanded = true; // size is reset in ui.js
    self.port.emit('closePanel');
});

document.getElementById('expand_reduce').addEventListener("click", function (event) {
    if (bExpanded) {
        self.port.emit("resize", "reduce", 10); // the number has no meaning here
        bExpanded = false;
    } else {
        self.port.emit("resize", "expand", 10); // the number has no meaning here
        bExpanded = true;
    }
});

document.getElementById('copy_to_clipboard').addEventListener("click", function (event) {
    copyToClipboard();
});

document.getElementById('closemsg').addEventListener("click", function (event) {
    closeMessageBox();
});

self.port.on("setPanelWidth", function (n) {
    nPanelWidth = n;
});

self.port.on("addMessage", function (sClass, sText) {
    addMessage(sClass, sText);
});

self.port.on("addParagraph", function (sText, iParagraph, sJSON) {
    addParagraph(sText, iParagraph, sJSON);
});

self.port.on("refreshParagraph", function (sText, sIdParagr, sJSON) {
    refreshParagraph(sText, sIdParagr, sJSON);
});

self.port.on("showMessage", function (sText) {
    document.getElementById("message").textContent = sText;
    document.getElementById("messagebox").style.display = "block";
    window.setTimeout(closeMessageBox, 20000);
});

self.port.on("clearErrors", function (sHtml) {
    document.getElementById("errorlist").textContent = "";
    aIgnoredErrors.clear();
    hideAllTooltips();
});

self.port.on("start", function() {
    startWaitIcon();
});

self.port.on("end", function() {
    stopWaitIcon();
    document.getElementById("copy_to_clipboard").style.display = "block";
});

self.port.on("suggestionsFor", function (sWord, sSuggestions, sErrId) {
    setSpellSuggestionsFor(sWord, sSuggestions, sErrId);
});


window.addEventListener(
    "click",
    function (xEvent) {
        try {
            let xElem = xEvent.target;
            if (xElem.id) {
                if (xElem.id.startsWith("sugg")) {
                    applySuggestion(xElem.id);
                } else if (xElem.id.endsWith("_ignore")) {
                    ignoreError(xElem.id);
                } else if (xElem.id.startsWith("check")) {
                    sendBackAndCheck(xElem.id);
                /*} else if (xElem.id.startsWith("edit")) {
                    switchEdition(xElem.id);*/
                } else if (xElem.id.startsWith("end")) {
                    document.getElementById(xElem.id).parentNode.parentNode.style.display = "none";
                } else if (xElem.tagName === "U" && xElem.id.startsWith("err")
                           && xElem.className !== "corrected" && xElem.className !== "ignored") {
                    showTooltip(xElem.id);
                } else if (xElem.id.startsWith("resize")) {
                    self.port.emit("resize", xElem.id, 10);
                } else if (xElem.id === "gc_url") {
                    self.port.emit("openURL", xElem.getAttribute("href"));
                } else {
                    hideAllTooltips();
                }
            } else if (xElem.tagName === "A") {
                self.port.emit("openURL", xElem.getAttribute("href"));
            } else {
                hideAllTooltips();
            }
        }
        catch (e) {
            showError(e);
        }
    },
    false
);


/*
    Actions
*/

function showError (e) {
    console.error("\n" + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
}

function closeMessageBox () {
    document.getElementById("messagebox").style.display = "none";
    document.getElementById("message").textContent = "";
}

function addMessage (sClass, sText) {
    let xNode = document.createElement("p");
    xNode.className = sClass;
    xNode.textContent = sText;
    document.getElementById("errorlist").appendChild(xNode);
}

function addParagraph (sText, iParagraph, sJSON) {
    try {
        let xNodeDiv = document.createElement("div");
        xNodeDiv.className = "paragraph_block";
        // actions
        let xDivActions = document.createElement("div");
        xDivActions.className = "actions";
        let xDivClose = document.createElement("div");
        xDivClose.id = "end" + iParagraph.toString();
        xDivClose.className = "button red bold";
        xDivClose.textContent = "×";
        xDivActions.appendChild(xDivClose);
        /*let xDivEdit = document.createElement("div");
        xDivEdit.id = "edit" + iParagraph.toString();
        xDivEdit.className = "button";
        xDivEdit.textContent = "Éditer";
        xDivActions.appendChild(xDivEdit);*/
        let xDivCheck = document.createElement("div");
        xDivCheck.id = "check" + iParagraph.toString();
        xDivCheck.className = "button green";
        xDivCheck.textContent = "Réanalyser";
        xDivCheck.setAttribute("title", "Réanalyser le texte");
        xDivActions.appendChild(xDivCheck);
        xNodeDiv.appendChild(xDivActions);
        // paragraph
        let xParagraph = document.createElement("p");
        xParagraph.id = "paragr" + iParagraph.toString();
        xParagraph.lang = "fr";
        xParagraph.setAttribute("spellcheck", false);
        xParagraph.setAttribute("contenteditable", true);
        let oErrors = JSON.parse(sJSON);
        xParagraph.className = (oErrors.aGrammErr.length || oErrors.aSpellErr.length) ? "paragraph softred" : "paragraph";
        _tagParagraph(sText, xParagraph, iParagraph, oErrors.aGrammErr, oErrors.aSpellErr);
        xNodeDiv.appendChild(xParagraph);
        document.getElementById("errorlist").appendChild(xNodeDiv);
    }
    catch (e) {
        showError(e);
    }
}

function refreshParagraph (sText, sIdParagr, sJSON) {
    try {
        let xParagraph = document.getElementById("paragr"+sIdParagr);
        let oErrors = JSON.parse(sJSON);
        xParagraph.className = (oErrors.aGrammErr.length || oErrors.aSpellErr.length) ? "paragraph softred" : "paragraph softgreen";
        xParagraph.textContent = "";
        _tagParagraph(sText, xParagraph, sIdParagr, oErrors.aGrammErr, oErrors.aSpellErr);
    }
    catch (e) {
        showError(e);
    }
}

function _tagParagraph (sParagraph, xParagraph, iParagraph, aSpellErr, aGrammErr) {
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
                oErr['sErrorId'] = iParagraph.toString() + "_" + nErr.toString(); // error identifier
                oErr['sIgnoredKey'] = iParagraph.toString() + ":" + nStart.toString() + ":" + nEnd.toString() + ":" + sParagraph.slice(nStart, nEnd);
                if (nEndLastErr < nStart) {
                    xParagraph.appendChild(document.createTextNode(sParagraph.slice(nEndLastErr, nStart)));
                }
                xParagraph.appendChild(_createError(sParagraph.slice(nStart, nEnd), oErr));
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
}

function _createError (sUnderlined, oErr) {
    let xNodeErr = document.createElement("u");
    xNodeErr.id = "err" + oErr['sErrorId'];
    xNodeErr.textContent = sUnderlined;
    xNodeErr.dataset.error_id = oErr['sErrorId'];
    xNodeErr.dataset.ignored_key = oErr['sIgnoredKey'];
    xNodeErr.dataset.error_type = (oErr['sType'] === "WORD") ? "spelling" : "grammar";
    /*xNodeErr.setAttribute("href", "#");
    xNodeErr.setAttribute("onclick", "return false;");*/
    if (xNodeErr.dataset.error_type === "grammar") {
        xNodeErr.dataset.gc_message = oErr['sMessage'];
        xNodeErr.dataset.gc_url = oErr['URL'];
        if (xNodeErr.dataset.gc_message.includes(" #")) {
            xNodeErr.dataset.line_id = oErr['sLineId'];
            xNodeErr.dataset.rule_id = oErr['sRuleId'];
        }
        xNodeErr.dataset.suggestions = oErr["aSuggestions"].join("|");
    }
    xNodeErr.className = (aIgnoredErrors.has(xNodeErr.dataset.ignored_key)) ? "ignored" : "error " + oErr['sType'];
    return xNodeErr;
}

function applySuggestion (sSuggId) { // sugg
    try {
        let sErrorId = document.getElementById(sSuggId).dataset.error_id;
        let sIdParagr = sErrorId.slice(0, sErrorId.indexOf("_"));
        startWaitIcon("paragr"+sIdParagr);
        let xNodeErr = document.getElementById("err" + sErrorId);
        xNodeErr.textContent = document.getElementById(sSuggId).textContent;
        xNodeErr.className = "corrected";
        xNodeErr.removeAttribute("style");
        self.port.emit("correction", sIdParagr, getPurgedTextOfParagraph("paragr"+sIdParagr));
        hideAllTooltips();
        stopWaitIcon("paragr"+sIdParagr);
    }
    catch (e) {
        showError(e);
    }
}

function ignoreError (sIgnoreButtonId) {  // ignore
    try {
        //console.log("ignore button: " + sIgnoreButtonId + " // error id: " + document.getElementById(sIgnoreButtonId).dataset.error_id);
        let xNodeErr = document.getElementById("err"+document.getElementById(sIgnoreButtonId).dataset.error_id);
        aIgnoredErrors.add(xNodeErr.dataset.ignored_key);
        xNodeErr.className = "ignored";
        xNodeErr.removeAttribute("style");
        hideAllTooltips();
    }
    catch (e) {
        showError(e);
    }
}

function showTooltip (sNodeErrorId) {  // err
    try {
        hideAllTooltips();
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
                xGCSugg.appendChild(_createSuggestion(xNodeErr.dataset.error_id, iSugg, sSugg));
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
}

function _createSuggestion (sErrId, iSugg, sSugg) {
    let xNodeSugg = document.createElement("a");
    xNodeSugg.id = "sugg" + sErrId + "-" + iSugg.toString();
    xNodeSugg.className = "sugg";
    /*xNodeSugg.setAttribute("href", "#");
    xNodeSugg.setAttribute("onclick", "return false;");*/
    xNodeSugg.dataset.error_id = sErrId;
    xNodeSugg.textContent = sSugg;
    return xNodeSugg;
}

/*function switchEdition (sEditButtonId) {  // edit
    let xParagraph = document.getElementById("paragr" + sEditButtonId.slice(4));
    if (xParagraph.hasAttribute("contenteditable") === false
        || xParagraph.getAttribute("contenteditable") === "false") {
        xParagraph.setAttribute("contenteditable", true);
        document.getElementById(sEditButtonId).className = "button orange";
        xParagraph.focus();
    } else {
        xParagraph.setAttribute("contenteditable", false);
        document.getElementById(sEditButtonId).className = "button";
    }
}*/

function sendBackAndCheck (sCheckButtonId) {  // check
    startWaitIcon();
    let sIdParagr = sCheckButtonId.slice(5);
    self.port.emit("modifyAndCheck", sIdParagr, getPurgedTextOfParagraph("paragr"+sIdParagr));
    stopWaitIcon();
}

function hideAllTooltips () {
    document.getElementById("gc_tooltip").style.display = "none";
    document.getElementById("gc_rule_id").style.display = "none";
    document.getElementById("sc_tooltip").style.display = "none";
    document.getElementById("gc_tooltip_arrow").style.display = "none";
    document.getElementById("sc_tooltip_arrow").style.display = "none";
}

function setSpellSuggestionsFor (sWord, sSuggestions, sErrId) {
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
                xSuggBlock.appendChild(_createSuggestion(sErrId, iSugg, sSugg));
                xSuggBlock.appendChild(document.createTextNode(" "));
                iSugg += 1;
            }
        }
    }
    catch (e) {
        showError(e);
    }
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

function showSpecialMessage () {
    if (Date.now() < Date.UTC(2017, 6, 12)) {
        try {
            document.getElementById('special_message').style.display = "block";
            document.getElementById('errorlist').style.padding = "20px 20px 30px 20px";
        } catch (e) {
            showError(e);
        }
    }
}
