// JavaScript
// Very simple tokenizer
/*jslint esversion: 6*/
/*global require,exports*/

"use strict";


const aTkzPatterns = {
    // All regexps must start with ^.
    "default":
        [
            [/^[   \t]+/, 'SPACE'],
            [/^\/(?:~|bin|boot|dev|etc|home|lib|mnt|opt|root|sbin|tmp|usr|var|Bureau|Documents|Images|Musique|Public|Téléchargements|Vidéos)(?:\/[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ_.()-]+)*/, 'FOLDERUNIX'],
            [/^[a-zA-Z]:\\(?:Program Files(?: \(x86\)|)|[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ.()]+)(?:\\[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ_.()-]+)*/, 'FOLDERWIN'],
            [/^[,.;:!?…«»“”‘’"(){}\[\]·–—]/, 'SEPARATOR'],
            [/^[A-Z][.][A-Z][.](?:[A-Z][.])*/, 'WORD_ACRONYM'],
            [/^(?:https?:\/\/|www[.]|[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ_-]+[@.][a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ_-]{2,}[@.])[a-zA-Z0-9][a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ_.\/?&!%=+*"'@$#-]+/, 'LINK'],
            [/^[#@][a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ_-]+/, 'TAG'],
            [/^<[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ]+.*?>|<\/[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ]+ *>/, 'HTML'],
            [/^\[\/?[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ]+\]/, 'PSEUDOHTML'],
            [/^&\w+;(?:\w+;|)/, 'HTMLENTITY'],
            [/^\d\d?h\d\d\b/, 'HOUR'],
            [/^\d+(?:[.,]\d+|)/, 'NUM'],
            [/^[%‰+=*/<>⩾⩽-]/, 'SIGN'],
            [/^[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ]+(?:[’'`-][a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ]+)*/, 'WORD']
        ],
    "fr":
        [
            [/^[   \t]+/, 'SPACE'],
            [/^\/(?:~|bin|boot|dev|etc|home|lib|mnt|opt|root|sbin|tmp|usr|var|Bureau|Documents|Images|Musique|Public|Téléchargements|Vidéos)(?:\/[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ_.()-]+)*/, 'FOLDERUNIX'],
            [/^[a-zA-Z]:\\(?:Program Files(?: \(x86\)|)|[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ.()]+)(?:\\[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ_.()-]+)*/, 'FOLDERWIN'],
            [/^[,.;:!?…«»“”‘’"(){}\[\]·–—]/, 'SEPARATOR'],
            [/^[A-Z][.][A-Z][.](?:[A-Z][.])*/, 'WORD_ACRONYM'],
            [/^(?:https?:\/\/|www[.]|[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ_-]+[@.][a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ_-]{2,}[@.])[a-zA-Z0-9][a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ_.\/?&!%=+*"'@$#-]+/, 'LINK'],
            [/^[#@][a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ_-]+/, 'TAG'],
            [/^<[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ]+.*?>|<\/[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ]+ *>/, 'HTML'],
            [/^\[\/?[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ]+\]/, 'PSEUDOHTML'],
            [/^&\w+;(?:\w+;|)/, 'HTMLENTITY'],
            [/^(?:l|d|n|m|t|s|j|c|ç|lorsqu|puisqu|jusqu|quoiqu|qu)['’`]/i, 'WORD_ELIDED'],
            [/^\d\d?[hm]\d\d\b/, 'HOUR'],
            [/^\d+(?:ers?|nds?|es?|des?|ièmes?|èmes?|emes?|ᵉʳˢ?|ⁿᵈˢ?|ᵉˢ?|ᵈᵉˢ?)\b/, 'WORD_ORDINAL'],
            [/^\d+(?:[.,]\d+|)/, 'NUM'],
            [/^[%‰+=*/<>⩾⩽-]/, 'SIGN'],
            [/^[a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ]+(?:[’'`-][a-zA-Zà-öÀ-Ö0-9ø-ÿØ-ßĀ-ʯﬁ-ﬆ]+)*/, 'WORD']
        ]
};


class Tokenizer {

    constructor (sLang) {
        this.sLang = sLang;
        if (!aTkzPatterns.hasOwnProperty(sLang)) {
            this.sLang = "default";
        }
        this.aRules = aTkzPatterns[this.sLang];
    }

    * genTokens (sText, bStartEndToken=false, bWithSpaces=false) {
        let m;
        let iToken;
        let iNext = 0;
        let iEnd = sText.length;
        if (bStartEndToken) {
            yield { "i": 0, "sType": "INFO", "sValue": "<start>", "nStart": 0, "nEnd": 0, "lMorph": ["<start>"] };
        }
        while (sText) {
            let iCut = 1;
            let iToken = 0;
            for (let [zRegex, sType] of this.aRules) {
                if (sType !== "SPACE"  ||  bWithSpaces) {
                    try {
                        if ((m = zRegex.exec(sText)) !== null) {
                            iToken += 1;
                            yield { "i": iToken, "sType": sType, "sValue": m[0], "nStart": iNext, "nEnd": iNext + m[0].length }
                            iCut = m[0].length;
                            break;
                        }
                    }
                    catch (e) {
                        console.error(e);
                    }
                }
            }
            iNext += iCut;
            sText = sText.slice(iCut);
        }
        if (bStartEndToken) {
            yield { "i": iToken+1, "sType": "INFO", "sValue": "<end>", "nStart": iEnd, "nEnd": iEnd, "lMorph": ["<end>"] };
        }
    }
}


if (typeof(exports) !== 'undefined') {
    exports.Tokenizer = Tokenizer;
}
