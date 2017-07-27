// JavaScript

"use strict";

const helpers = require("resource://grammalecte/helpers.js");


function* getParagraph (sText) {
    // generator: returns paragraphs of text
    let iStart = 0;
    let iEnd = 0;
    sText = sText.replace("\r", "");
    while ((iEnd = sText.indexOf("\n", iStart)) !== -1) {
        yield sText.slice(iStart, iEnd);
        iStart = iEnd + 1;
    }
    yield sText.slice(iStart);
}

function* wrap (sText, nWidth=80) {
    // generator: returns text line by line
    while (sText) {
        if (sText.length >= nWidth) {
            let nEnd = sText.lastIndexOf(" ", nWidth) + 1;
            if (nEnd > 0) {
                yield sText.slice(0, nEnd);
                sText = sText.slice(nEnd);
            } else {
                yield sText.slice(0, nWidth);
                sText = sText.slice(nWidth);
            }
        } else {
            break;
        }
    }
    yield sText;
}

function getReadableError (oErr) {
    // Returns an error oErr as a readable error
    try {
        let sResult = "\n* " + oErr['nStart'] + ":" + oErr['nEnd'] 
                    + "  # " + oErr['sLineId'] + "  # " + oErr['sRuleId'] + ":\n";
        sResult += "  " + oErr["sMessage"];
        if (oErr["aSuggestions"].length > 0) {
            sResult += "\n  > Suggestions : " + oErr["aSuggestions"].join(" | ");
        }
        if (oErr["URL"] !== "") {
            sResult += "\n  > URL: " + oErr["URL"];
        }
        return sResult;
    }
    catch (e) {
        helpers.logerror(e);
        return "\n# Error. Data: " + oErr.toString();
    }
}

function addHtmlEntities (sParagraph) {
    if (sParagraph.includes("&")) {
        sParagraph = sParagraph.replace(/&/g, "&amp;");
    }
    if (sParagraph.includes("<")) {
        sParagraph = sParagraph.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }
    return sParagraph;
}

function createHTMLBlock (sParagraph, iParagraph) {
    let sClassName = (sParagraph.includes('<u id="err')) ? " softred" : "";
    return '<p id="paragr'+iParagraph.toString()+'" class="paragraph' + sClassName + '" lang="fr" spellcheck="false">' + sParagraph + '</p>\n'
           + '<div class="actions"><div id="end'+iParagraph.toString()+'" class="button red">×</div>'
           + '<div id="edit'+iParagraph.toString()+'" class="button">Éditer</div>'
           + '<div id="check'+iParagraph.toString()+'" class="button green">Réanalyser</div>&nbsp;</div>\n';
}

function tagParagraph (sParagraph, iParagraph, aGrammErr, aSpellErr, bDebug=false) {
    // Returns a text with with underlined errors and messages in tooltip
    try {
        if (aGrammErr.length === 0  &&  aSpellErr.length === 0) {
            return sParagraph;
        }
        aGrammErr.push(...aSpellErr);
        aGrammErr.sort(function (a, b) {
            if (a["nStart"] < b["nStart"])
                return 1;
            if (a["nStart"] > b["nStart"])
                return -1;
            return 0;
        });

        let nErr = aGrammErr.length - 1; // we count errors to give them an identifier
        let nStartLastErr = sParagraph.length;
        for (let oErr of aGrammErr) {
            let sErrId = iParagraph.toString() + "_" + nErr.toString();
            let nStart = oErr["nStart"];
            let nEnd = oErr["nEnd"];
            if (nEnd <= nStartLastErr) {
                oErr["sId"] = sErrId;
                if (oErr['sType'] !== 'WORD') {
                    // Grammar Error
                    sParagraph = sParagraph.slice(0, nStart)
                               + '<u id="err' + sErrId + '" class="error '+oErr['sType']+'" href="#" onclick="return false;">'
                               + sParagraph.slice(nStart, nEnd)
                               + '<span id="tooltip' + sErrId + '" class="tooltip" contenteditable="false">'
                               + getGrammarErrorHTML(oErr, bDebug) + '</span>'
                               + "</u><!-- err_end -->" + sParagraph.slice(nEnd);
                } else {
                    // Spelling error
                    sParagraph = sParagraph.slice(0, nStart)
                               + '<u id="err' + sErrId + '" class="error spell" href="#" onclick="return false;">'
                               + sParagraph.slice(nStart, nEnd)
                               + '<span id="tooltip' + sErrId + '" class="tooltip" contenteditable="false">'
                               + getSpellingErrorHTML(oErr) + '</span>'
                               + "</u><!-- err_end -->" + sParagraph.slice(nEnd);
                }
                nStartLastErr = nStart;
            }
            nErr -= 1;
        }
        return sParagraph;
    }
    catch (e) {
        helpers.logerror(e);
        return "# Error.";
    }
}

function getGrammarErrorHTML (oErr, bDebug=false) {
    // Returns an error oErr as a readable error in HTML
    try {
        let sErr = '';
        if (bDebug) {
            sErr += '<em class="debug">'
              + '<i id="data'+oErr['sId']+'" class="data" hidden>'
              + oErr['nStart'] + ":" + oErr['nEnd'] + ' · #' + oErr['sRuleId'] + " </i>+</em>";
        }
        sErr += oErr["sMessage"];
        sErr += ' <a id="ignore'+oErr['sId']+'" class="ignore" href="#" onclick="return false;">IGNORER</a>';
        if (oErr["URL"] !== "") {
            sErr += ' <a href="' + oErr["URL"] + '" onclick="return false;">Infos…</a>';
        }
        if (oErr["aSuggestions"].length > 0) {
            sErr += '<br/><s>Suggestions :</s><br/>';
            let iSugg = 0;
            for (let sSugg of oErr["aSuggestions"]) {
                sErr += '<a id="sugg' + oErr['sId'] + "-" + iSugg + '" class="sugg" href="#" onclick="return false;">' + sSugg + '</a> ';
                iSugg += 1;
            }
        }
        return sErr;
    }
    catch (e) {
        helpers.logerror(e);
        return '# Error. Data: ' + oErr.toString();
    }
}

function getSpellingErrorHTML (oErr) {
    // Returns an error oErr as a readable error in HTML
    try {
        let sErr = 'Mot inconnu du dictionnaire.';
        sErr += ' <a id="ignore' + oErr['sId'] + '" class="ignore" href="#" onclick="return false;">IGNORER</a>';
        sErr += '<br/><s>Suggestions :</s><br/>';
        return sErr;
    }
    catch (e) {
        helpers.logerror(e);
        return '# Error. Data: ' + oErr.toString();
    }
}


if (typeof(exports) !== 'undefined') {
    exports.getParagraph = getParagraph;
    exports.addHtmlEntities = addHtmlEntities;
    exports.createHTMLBlock = createHTMLBlock;
    exports.tagParagraph = tagParagraph;
    exports.getReadableError = getReadableError;
}
