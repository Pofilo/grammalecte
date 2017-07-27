// Grammar checker rules
"use strict";

${string}
${regex}

const lParagraphRules = ${paragraph_rules_JS};

const lSentenceRules = ${sentence_rules_JS};


if (typeof(exports) !== 'undefined') {
	exports.lParagraphRules = lParagraphRules;
	exports.lSentenceRules = lSentenceRules;
}
