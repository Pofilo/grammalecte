// JavaScript

let nPanelWidth = 0;  // must be set at launch
let bExpanded = true;

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
});

self.port.on("start", function() {
	startWaitIcon();
});

self.port.on("end", function() {
	stopWaitIcon();
	document.getElementById("copy_to_clipboard").style.display = "block";
});

self.port.on("suggestionsFor", function (sWord, sSuggestions, sTooltipId) {
	setSpellSuggestionsFor(sWord, sSuggestions, sTooltipId);
});


window.addEventListener(
	"click",
	function (xEvent) {
		let xElem = xEvent.target;
		if (xElem.id) {
			if (xElem.id.startsWith("sugg")) {
				applySuggestion(xElem.id);
			} else if (xElem.id.startsWith("ignore")) {
				ignoreError(xElem.id);
			} else if (xElem.id.startsWith("check")) {
				sendBackAndCheck(xElem.id);
			} else if (xElem.id.startsWith("edit")) {
				switchEdition(xElem.id);
			} else if (xElem.id.startsWith("end")) {
				document.getElementById(xElem.id).parentNode.parentNode.style.display = "none";
			} else if (xElem.tagName === "U" && xElem.id.startsWith("err")) {
				showTooltip(xElem.id);
			} else if (xElem.id.startsWith("resize")) {
				self.port.emit("resize", xElem.id, 10);
			} else {
				hideAllTooltips();
			}
		} else if (xElem.tagName === "A") {
			self.port.emit("openURL", xElem.getAttribute("href"));
		} else {
			hideAllTooltips();
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
		// paragraph
		let xParagraph = document.createElement("p");
		xParagraph.id = "paragr" + iParagraph.toString();
		xParagraph.lang = "fr";
		xParagraph.setAttribute("spellcheck", false);
		let oErrors = JSON.parse(sJSON);
		xParagraph.className = (oErrors.aGrammErr.length || oErrors.aSpellErr.length) ? "paragraph softred" : "paragraph";
		_tagParagraph(sText, xParagraph, iParagraph, oErrors.aGrammErr, oErrors.aSpellErr);
		xNodeDiv.appendChild(xParagraph);
		// actions
		let xDivActions = document.createElement("div");
		xDivActions.className = "actions";
		let xDivClose = document.createElement("div");
		xDivClose.id = "end" + iParagraph.toString();
		xDivClose.className = "button red";
		xDivClose.textContent = "×";
		let xDivEdit = document.createElement("div");
		xDivEdit.id = "edit" + iParagraph.toString();
		xDivEdit.className = "button";
		xDivEdit.textContent = "Éditer";
		let xDivCheck = document.createElement("div");
		xDivCheck.id = "check" + iParagraph.toString();
		xDivCheck.className = "button green";
		xDivCheck.textContent = "Réanalyser";
		xDivActions.appendChild(xDivClose);
		xDivActions.appendChild(xDivEdit);
		xDivActions.appendChild(xDivCheck);
		xNodeDiv.appendChild(xDivActions);
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
                oErr["sId"] = iParagraph.toString() + "_" + nErr.toString(); // error identifier
                if (nEndLastErr < nStart) {
                	xParagraph.appendChild(document.createTextNode(sParagraph.slice(nEndLastErr, nStart)));
                }
                xParagraph.appendChild(_createError(sParagraph.slice(nStart, nEnd), oErr));
                xParagraph.insertAdjacentHTML("beforeend", "<!-- err_end -->");
                nEndLastErr = nEnd;
            }
            nErr += 1;
        }
        if (nEndLastErr < sParagraph.length) {
        	xParagraph.appendChild(document.createTextNode(sParagraph.slice(nEndLastErr)));
        }
	}
	catch (e) {
		showError(e);
	}
}

function _createError (sUnderlined, oErr) {
	let xNodeErr = document.createElement("u");
	xNodeErr.id = "err" + oErr['sId'];
	xNodeErr.className = "error " + oErr['sType'];
	xNodeErr.textContent = sUnderlined;
	xNodeErr.setAttribute("href", "#");
	xNodeErr.setAttribute("onclick", "return false;");
	let xTooltip = (oErr['sType'] !== "WORD") ? _getGrammarTooltip(oErr) : _getSpellingTooltip(oErr);
	xNodeErr.appendChild(xTooltip);
	return xNodeErr;
}

function _getGrammarTooltip (oErr) {
	let xSpan = document.createElement("span");
	xSpan.id = "tooltip" + oErr['sId'];
	xSpan.className = "tooltip";
	xSpan.setAttribute("contenteditable", false);
	xSpan.appendChild(document.createTextNode(oErr["sMessage"]+" "));
	xSpan.appendChild(_createIgnoreButton(oErr["sId"]));
	if (oErr["URL"] !== "") {
		xSpan.appendChild(_createInfoLink(oErr["URL"]));
	}
	if (oErr["aSuggestions"].length > 0) {
		xSpan.appendChild(document.createElement("br"));
		xSpan.appendChild(_createSuggestionLabel());
		xSpan.appendChild(document.createElement("br"));
		let iSugg = 0;
        for (let sSugg of oErr["aSuggestions"]) {
        	xSpan.appendChild(_createSuggestion(oErr["sId"], iSugg, sSugg));
            xSpan.appendChild(document.createTextNode(" "));
            iSugg += 1;
        }
	}
	return xSpan;
}

function _getSpellingTooltip (oErr) {
	let xSpan = document.createElement("span");
	xSpan.id = "tooltip" + oErr['sId'];
	xSpan.className = "tooltip";
	xSpan.setAttribute("contenteditable", "false");
	xSpan.appendChild(document.createTextNode("Mot inconnu du dictionnaire. "));
	xSpan.appendChild(_createIgnoreButton(oErr["sId"]));
	xSpan.appendChild(document.createElement("br"));
	xSpan.appendChild(_createSuggestionLabel());
	xSpan.appendChild(document.createElement("br"));
	return xSpan;
}

function _createIgnoreButton (sErrorId) {
	let xIgnore = document.createElement("a");
	xIgnore.id = "ignore" + sErrorId;
	xIgnore.className = "ignore";
	xIgnore.setAttribute("href", "#");
	xIgnore.setAttribute("onclick", "return false;");
	xIgnore.textContent = "IGNORER";
	return xIgnore;
}

function _createInfoLink (sURL) {
	let xInfo = document.createElement("a");
	xInfo.setAttribute("href", sURL);
	xInfo.setAttribute("onclick", "return false;");
	xInfo.textContent = "Infos…";
	return xInfo;
}

function _createSuggestionLabel () {
	let xNode = document.createElement("s");
	xNode.textContent = "Suggestions :";
	return xNode;
}

function _createSuggestion (sErrId, iSugg, sSugg) {
	let xNodeSugg = document.createElement("a");
	xNodeSugg.id = "sugg" + sErrId + "-" + iSugg.toString();
	xNodeSugg.className = "sugg";
	xNodeSugg.setAttribute("href", "#");
	xNodeSugg.setAttribute("onclick", "return false;");
	xNodeSugg.textContent = sSugg;
	return xNodeSugg;
}

function closeMessageBox () {
	document.getElementById("messagebox").style.display = "none";
	document.getElementById("message").textContent = "";
}

function applySuggestion (sElemId) { // sugg
	try {
		let sIdParagr = sElemId.slice(4, sElemId.indexOf("_"));
		startWaitIcon("paragr"+sIdParagr);
		let sIdErr = "err" + sElemId.slice(4, sElemId.indexOf("-"));
		document.getElementById(sIdErr).textContent = document.getElementById(sElemId).textContent;
		document.getElementById(sIdErr).className = "corrected";
		document.getElementById(sIdErr).removeAttribute("style");
		self.port.emit("correction", sIdParagr, getPurgedTextOfElem("paragr"+sIdParagr));
		stopWaitIcon("paragr"+sIdParagr);
	}
	catch (e) {
		showError(e);
	}
}

function ignoreError (sElemId) {  // ignore
	let sIdErr = "err" + sElemId.slice(6);
	let xTooltipElem = document.getElementById("tooltip"+sElemId.slice(6));
	document.getElementById(sIdErr).removeChild(xTooltipElem);
	document.getElementById(sIdErr).className = "ignored";
	document.getElementById(sIdErr).removeAttribute("style");
}

function showTooltip (sElemId) {  // err
	hideAllTooltips();
	let sTooltipId = "tooltip" + sElemId.slice(3);
	let xTooltipElem = document.getElementById(sTooltipId);
	let nLimit = nPanelWidth - 300; // paragraph width - tooltip width
	if (document.getElementById(sElemId).offsetLeft > nLimit) {
		xTooltipElem.style.left = "-" + (document.getElementById(sElemId).offsetLeft - nLimit) + "px";
	}
	xTooltipElem.setAttribute("contenteditable", false);
	xTooltipElem.className = 'tooltip_on';
	if (document.getElementById(sElemId).className === "error WORD"  &&  xTooltipElem.textContent.endsWith(":")) {
		// spelling mistake
		self.port.emit("getSuggestionsForTo", document.getElementById(sElemId).innerHTML.replace(/<span .*$/, "").trim(), sTooltipId);
	}
}

function switchEdition (sElemId) {  // edit
	let sId = "paragr" + sElemId.slice(4);
	if (document.getElementById(sId).hasAttribute("contenteditable") === false
		|| document.getElementById(sId).getAttribute("contenteditable") === "false") {
		document.getElementById(sId).setAttribute("contenteditable", true);
		document.getElementById(sElemId).className = "button orange";
		document.getElementById(sId).focus();
	} else {
		document.getElementById(sId).setAttribute("contenteditable", false);
		document.getElementById(sElemId).className = "button";
	}
}

function sendBackAndCheck (sElemId) {  // check
	startWaitIcon();
	let sIdParagr = sElemId.slice(5);
	self.port.emit("modifyAndCheck", sIdParagr, getPurgedTextOfElem("paragr"+sIdParagr));
	stopWaitIcon();
}

function getPurgedTextOfElem (sId) {
	// Note : getPurgedTextOfElem2 should work better if not buggy.
	// if user writes in error, Fx adds tags <u></u>, we also remove style attribute
	let xParagraphElem = document.getElementById(sId);
	for (xNode of xParagraphElem.getElementsByTagName("u")) {
		if (xNode.id.startsWith('err')) {
			xNode.innerHTML = xNode.innerHTML.replace(/<\/?u>/g, "");
			xNode.removeAttribute("style");
		}
	}
	// we remove style attribute on tooltip
	for (xNode of xParagraphElem.getElementsByTagName("span")) {
		if (xNode.id.startsWith('tooltip')) {
			xNode.removeAttribute("style");
		}
	}
	// now, we remove tooltips, then errors, and we change some html entities
	let sText = xParagraphElem.innerHTML;
	sText = sText.replace(/<br\/? *> *$/ig, "");
	sText = sText.replace(/<span id="tooltip.+?<\/span>/g, "");
	sText = sText.replace(/<u id="err\w+" class="[\w ]+" href="#" onclick="return false;">(.+?)<\/u><!-- err_end -->/g, "$1");
	sText = sText.replace(/&nbsp;/g, " ").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
	return sText;
}

function getPurgedTextOfElem2 (sId) {
	// It is better to remove tooltips via DOM and retrieve textContent,
	// but for some reason getElementsByClassName “hazardously” forgets elements.
	// Unused. Needs investigation.
	let xParagraphElem = document.getElementById(sId).cloneNode(true);
	for (let xNode of xParagraphElem.getElementsByClassName("tooltip")) {
		xNode.parentNode.removeChild(xNode);
	}
	return xParagraphElem.textContent;
}

function hideAllTooltips () {
	for (let xElem of document.getElementsByClassName("tooltip_on")) {
		xElem.className = "tooltip";
		xElem.removeAttribute("style");
	}
}

function setSpellSuggestionsFor (sWord, sSuggestions, sTooltipId) {
	// spell checking suggestions
	//console.log(sWord + ": " + sSuggestions);
	let xTooltip = document.getElementById(sTooltipId);
	if (sSuggestions === "") {
		xTooltip.appendChild(document.createTextNode("Aucune."));
	} else if (sSuggestions.startsWith("#")) {
		xTooltip.appendChild(document.createTextNode(sSuggestions));
	} else {
		let lSugg = sSuggestions.split("|");
		let iSugg = 0;
		let sElemId = sTooltipId.slice(7);
		for (let sSugg of lSugg) {
			xTooltip.appendChild(_createSuggestion(sElemId, iSugg, sSugg));
			xTooltip.appendChild(document.createTextNode(" "));
			iSugg += 1;
		}
	}
}

function copyToClipboard () {
	startWaitIcon();
	try {
		document.getElementById("clipboard_msg").textContent = "copie en cours…";
		let sText = "";
		for (let xNode of document.getElementById("errorlist").getElementsByClassName("paragraph")) {
			sText += getPurgedTextOfElem(xNode.id);
			sText += "\n";
		}
		self.port.emit('copyToClipboard', sText);
		document.getElementById("clipboard_msg").textContent = "-> presse-papiers";
		window.setTimeout(function() { document.getElementById("clipboard_msg").textContent = "∑"; } , 3000);
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
