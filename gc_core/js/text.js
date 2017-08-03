// JavaScript

"use strict";


if (typeof(exports) !== 'undefined') {
    var helpers = require("resource://grammalecte/helpers.js");
}


var text = {
    getParagraph: function* (sText) {
        // generator: returns paragraphs of text
        let iStart = 0;
        let iEnd = 0;
        sText = sText.replace("\r", "");
        while ((iEnd = sText.indexOf("\n", iStart)) !== -1) {
            yield sText.slice(iStart, iEnd);
            iStart = iEnd + 1;
        }
        yield sText.slice(iStart);
    },

    wrap: function* (sText, nWidth=80) {
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
    },

    getReadableError: function (oErr) {
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
}


if (typeof(exports) !== 'undefined') {
    exports.getParagraph = text.getParagraph;
    exports.wrap = text.wrap;
    exports.getReadableError = text.getReadableError;
}
