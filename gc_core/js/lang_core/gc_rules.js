// Grammar checker rules
/*jslint esversion: 6*/
/*global exports*/

"use strict";

${string}
${regex}

var gc_rules = {
    lParagraphRules: ${paragraph_rules_JS},

    lSentenceRules: ${sentence_rules_JS}
}


if (typeof(exports) !== 'undefined') {
    exports.lParagraphRules = gc_rules.lParagraphRules;
    exports.lSentenceRules = gc_rules.lSentenceRules;
}
