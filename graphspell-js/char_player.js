// list of similar chars
// useful for suggestion mechanism

${map}


var char_player = {

    _xTransCharsForSpelling: new Map([
        ['ſ', 's'],  ['ﬃ', 'ffi'],  ['ﬄ', 'ffl'],  ['ﬀ', 'ff'],  ['ﬅ', 'ft'],  ['ﬁ', 'fi'],  ['ﬂ', 'fl'],  ['ﬆ', 'st']
    ]),

    spellingNormalization: function (sWord) {
        let sNewWord = "";
        for (let c of sWord) {
            sNewWord += this._xTransCharsForSpelling.gl_get(c, c);
        }
        return sNewWord.normalize("NFC");
    },

    _xTransCharsForSimplification: new Map([
        ['à', 'a'],  ['é', 'e'],  ['î', 'i'],  ['ô', 'o'],  ['û', 'u'],  ['ÿ', 'i'],  ['y', 'i'],
        ['â', 'a'],  ['è', 'e'],  ['ï', 'i'],  ['ö', 'o'],  ['ù', 'u'],  ['ŷ', 'i'],
        ['ä', 'a'],  ['ê', 'e'],  ['í', 'i'],  ['ó', 'o'],  ['ü', 'u'],  ['ý', 'i'],
        ['á', 'a'],  ['ë', 'e'],  ['ì', 'i'],  ['ò', 'o'],  ['ú', 'u'],  ['ỳ', 'i'],
        ['ā', 'a'],  ['ē', 'e'],  ['ī', 'i'],  ['ō', 'o'],  ['ū', 'u'],  ['ȳ', 'i'],
        ['ç', 'c'],  ['ñ', 'n'],  ['k', 'q'],  ['w', 'v'],
        ['œ', 'oe'], ['æ', 'ae'], 
        ['ſ', 's'],  ['ﬃ', 'ffi'],  ['ﬄ', 'ffl'],  ['ﬀ', 'ff'],  ['ﬅ', 'ft'],  ['ﬁ', 'fi'],  ['ﬂ', 'fl'],  ['ﬆ', 'st']
    ]),

    simplifyWord: function (sWord) {
        // word simplication before calculating distance between words
        sWord = sWord.toLowerCase();
        let sNewWord = "";
        let i = 1;
        for (let c of sWord) {
            let cNew = this._xTransCharsForSimplification.gl_get(c, c);
            let cNext = sWord.slice(i, i+1)
            if (cNew != this._xTransCharsForSimplification.gl_get(cNext, cNext)) {
                sNewWord += cNew;
            }
            i++;
        }
        return sNewWord.replace(/eau/g, "o").replace(/au/g, "o").replace(/ai/g, "e").replace(/ei/g, "e").replace(/ph/g, "f");
    },

    aVowel: new Set("aáàâäāeéèêëēiíìîïīoóòôöōuúùûüūyýỳŷÿȳœæAÁÀÂÄĀEÉÈÊËĒIÍÌÎÏĪOÓÒÔÖŌUÚÙÛÜŪYÝỲŶŸȲŒÆ"),
    aConsonant: new Set("bcçdfghjklmnñpqrstvwxzBCÇDFGHJKLMNÑPQRSTVWXZ"),
    aDouble: new Set("bcdfjklmnprstzBCDFJKLMNPRSTZ"),  // letters that may be used twice successively


    // Similar chars

    d1to1: new Map([
        ["1", "liîLIÎ"],
        ["2", "zZ"],
        ["3", "eéèêEÉÈÊ"],
        ["4", "aàâAÀÂ"],
        ["5", "sgSG"],
        ["6", "bdgBDG"],
        ["7", "ltLT"],
        ["8", "bB"],
        ["9", "gbdGBD"],
        ["0", "oôOÔ"],

        ["a", "aàâáäæ"],
        ["A", "AÀÂÁÄÆ"],
        ["à", "aàâáäæ"],
        ["À", "AÀÂÁÄÆ"],
        ["â", "aàâáäæ"],
        ["Â", "AÀÂÁÄÆ"],
        ["á", "aàâáäæ"],
        ["Á", "AÀÂÁÄÆ"],
        ["ä", "aàâáäæ"],
        ["Ä", "AÀÂÁÄÆ"],

        ["æ", "æéa"],
        ["Æ", "ÆÉA"],

        ["c", "cçskqśŝ"],
        ["C", "CÇSKQŚŜ"],
        ["ç", "cçskqśŝ"],
        ["Ç", "CÇSKQŚŜ"],

        ["e", "eéèêëœ"],
        ["E", "EÉÈÊËŒ"],
        ["é", "eéèêëœ"],
        ["É", "EÉÈÊËŒ"],
        ["ê", "eéèêëœ"],
        ["Ê", "EÉÈÊËŒ"],
        ["è", "eéèêëœ"],
        ["È", "EÉÈÊËŒ"],
        ["ë", "eéèêëœ"],
        ["Ë", "EÉÈÊËŒ"],

        ["g", "gj"],
        ["G", "GJ"],
        
        ["i", "iîïyíìÿ"],
        ["I", "IÎÏYÍÌŸ"],
        ["î", "iîïyíìÿ"],
        ["Î", "IÎÏYÍÌŸ"],
        ["ï", "iîïyíìÿ"],
        ["Ï", "IÎÏYÍÌŸ"],
        ["í", "iîïyíìÿ"],
        ["Í", "IÎÏYÍÌŸ"],
        ["ì", "iîïyíìÿ"],
        ["Ì", "IÎÏYÍÌŸ"],

        ["j", "jg"],
        ["J", "JG"],

        ["k", "kcq"],
        ["K", "KCQ"],

        ["n", "nñ"],
        ["N", "NÑ"],

        ["o", "oôóòöœ"],
        ["O", "OÔÓÒÖŒ"],
        ["ô", "oôóòöœ"],
        ["Ô", "OÔÓÒÖŒ"],
        ["ó", "oôóòöœ"],
        ["Ó", "OÔÓÒÖŒ"],
        ["ò", "oôóòöœ"],
        ["Ò", "OÔÓÒÖŒ"],
        ["ö", "oôóòöœ"],
        ["Ö", "OÔÓÒÖŒ"],

        ["œ", "œoôeéèêë"],
        ["Œ", "ŒOÔEÉÈÊË"],

        ["q", "qck"],
        ["Q", "QCK"],

        ["s", "sśŝcç"],
        ["S", "SŚŜCÇ"],
        ["ś", "sśŝcç"],
        ["Ś", "SŚŜCÇ"],
        ["ŝ", "sśŝcç"],
        ["Ŝ", "SŚŜCÇ"],

        ["u", "uûùüú"],
        ["U", "UÛÙÜÚ"],
        ["û", "uûùüú"],
        ["Û", "UÛÙÜÚ"],
        ["ù", "uûùüú"],
        ["Ù", "UÛÙÜÚ"],
        ["ü", "uûùüú"],
        ["Ü", "UÛÙÜÚ"],
        ["ú", "uûùüú"],
        ["Ú", "UÛÙÜÚ"],

        ["v", "vw"],
        ["V", "VW"],

        ["w", "wv"],
        ["W", "WV"],

        ["x", "xck"],
        ["X", "XCK"],

        ["y", "yÿiîŷýỳ"],
        ["Y", "YŸIÎŶÝỲ"],
        ["ÿ", "yÿiîŷýỳ"],
        ["Ÿ", "YŸIÎŶÝỲ"],
        ["ŷ", "yÿiîŷýỳ"],
        ["Ŷ", "YŸIÎŶÝỲ"],
        ["ý", "yÿiîŷýỳ"],
        ["Ý", "YŸIÎŶÝỲ"],
        ["ỳ", "yÿiîŷýỳ"],
        ["Ỳ", "YŸIÎŶÝỲ"],

        ["z", "zs"],
        ["Z", "ZS"],
    ]),

    d1toX: new Map([
        ["æ", ["ae",]],
        ["Æ", ["AE",]],
        ["b", ["bb",]],
        ["B", ["BB",]],
        ["c", ["cc", "ss", "qu", "ch"]],
        ["C", ["CC", "SS", "QU", "CH"]],
        ["d", ["dd",]],
        ["D", ["DD",]],
        ["é", ["ai", "ei"]],
        ["É", ["AI", "EI"]],
        ["f", ["ff", "ph"]],
        ["F", ["FF", "PH"]],
        ["g", ["gu", "ge", "gg", "gh"]],
        ["G", ["GU", "GE", "GG", "GH"]],
        ["j", ["jj", "dj"]],
        ["J", ["JJ", "DJ"]],
        ["k", ["qu", "ck", "ch", "cu", "kk", "kh"]],
        ["K", ["QU", "CK", "CH", "CU", "KK", "KH"]],
        ["l", ["ll",]],
        ["L", ["LL",]],
        ["m", ["mm", "mn"]],
        ["M", ["MM", "MN"]],
        ["n", ["nn", "nm", "mn"]],
        ["N", ["NN", "NM", "MN"]],
        ["o", ["au", "eau"]],
        ["O", ["AU", "EAU"]],
        ["œ", ["oe", "eu"]],
        ["Œ", ["OE", "EU"]],
        ["p", ["pp", "ph"]],
        ["P", ["PP", "PH"]],
        ["q", ["qu", "ch", "cq", "ck", "kk"]],
        ["Q", ["QU", "CH", "CQ", "CK", "KK"]],
        ["r", ["rr",]],
        ["R", ["RR",]],
        ["s", ["ss", "sh"]],
        ["S", ["SS", "SH"]],
        ["t", ["tt", "th"]],
        ["T", ["TT", "TH"]],
        ["x", ["cc", "ct", "xx"]],
        ["X", ["CC", "CT", "XX"]],
        ["z", ["ss", "zh"]],
        ["Z", ["SS", "ZH"]],
    ]),

    get1toXReplacement: function (cPrev, cCur, cNext) {
        if (this.aConsonant.has(cCur)  &&  (this.aConsonant.has(cPrev)  ||  this.aConsonant.has(cNext))) {
            return [];
        }
        return this.d1toX.gl_get(cCur, []);
    },

    d2toX: new Map([
        ["am", ["an", "en", "em"]],
        ["AM", ["AN", "EN", "EM"]],
        ["an", ["am", "en", "em"]],
        ["AN", ["AM", "EN", "EM"]],
        ["au", ["eau", "o", "ô"]],
        ["AU", ["EAU", "O", "Ô"]],
        ["em", ["an", "am", "en"]],
        ["EM", ["AN", "AM", "EN"]],
        ["en", ["an", "am", "em"]],
        ["EN", ["AN", "AM", "EM"]],
        ["ae", ["æ", "é"]],
        ["AE", ["Æ", "É"]],
        ["ai", ["ei", "é", "è", "ê", "ë"]],
        ["AI", ["EI", "É", "È", "Ê", "Ë"]],
        ["ei", ["ai", "é", "è", "ê", "ë"]],
        ["EI", ["AI", "É", "È", "Ê", "Ë"]],
        ["ch", ["sh", "c", "ss"]],
        ["CH", ["SH", "C", "SS"]],
        ["ct", ["x", "cc"]],
        ["CT", ["X", "CC"]],
        ["oa", ["oi",]],
        ["OA", ["OI",]],
        ["oe", ["œ",]],
        ["OE", ["Œ",]],
        ["oi", ["oa", "oie"]],
        ["OI", ["OA", "OIE"]],
        ["gg", ["gu",]],
        ["GG", ["GU",]],
        ["gu", ["gg",]],
        ["GU", ["GG",]],
        ["ph", ["f",]],
        ["PH", ["F",]],
        ["qu", ["q", "cq", "ck", "c", "k"]],
        ["QU", ["Q", "CQ", "CK", "C", "K"]],
        ["ss", ["c", "ç"]],
        ["SS", ["C", "Ç"]],
        ["un", ["ein",]],
        ["UN", ["EIN",]],
    ]),

    // End of word
    dFinal1: new Map([
        ["a", ["as", "at", "ant", "ah"]],
        ["A", ["AS", "AT", "ANT", "AH"]],
        ["c", ["ch",]],
        ["C", ["CH",]],
        ["e", ["et", "er", "ets", "ée", "ez", "ai", "ais", "ait", "ent", "eh"]],
        ["E", ["ET", "ER", "ETS", "ÉE", "EZ", "AI", "AIS", "AIT", "ENT", "EH"]],
        ["é", ["et", "er", "ets", "ée", "ez", "ai", "ais", "ait"]],
        ["É", ["ET", "ER", "ETS", "ÉE", "EZ", "AI", "AIS", "AIT"]],
        ["è", ["et", "er", "ets", "ée", "ez", "ai", "ais", "ait"]],
        ["È", ["ET", "ER", "ETS", "ÉE", "EZ", "AI", "AIS", "AIT"]],
        ["ê", ["et", "er", "ets", "ée", "ez", "ai", "ais", "ait"]],
        ["Ê", ["ET", "ER", "ETS", "ÉE", "EZ", "AI", "AIS", "AIT"]],
        ["ë", ["et", "er", "ets", "ée", "ez", "ai", "ais", "ait"]],
        ["Ë", ["ET", "ER", "ETS", "ÉE", "EZ", "AI", "AIS", "AIT"]],
        ["g", ["gh",]],
        ["G", ["GH",]],
        ["i", ["is", "it", "ie", "in"]],
        ["I", ["IS", "IT", "IE", "IN"]],
        ["n", ["nt", "nd", "ns", "nh"]],
        ["N", ["NT", "ND", "NS", "NH"]],
        ["o", ["aut", "ot", "os"]],
        ["O", ["AUT", "OT", "OS"]],
        ["ô", ["aut", "ot", "os"]],
        ["Ô", ["AUT", "OT", "OS"]],
        ["ö", ["aut", "ot", "os"]],
        ["Ö", ["AUT", "OT", "OS"]],
        ["p", ["ph",]],
        ["P", ["PH",]],
        ["s", ["sh",]],
        ["S", ["SH",]],
        ["t", ["th",]],
        ["T", ["TH",]],
        ["u", ["ut", "us", "uh"]],
        ["U", ["UT", "US", "UH"]],
    ]),

    dFinal2: new Map([
        ["ai", ["aient", "ais", "et"]],
        ["AI", ["AIENT", "AIS", "ET"]],
        ["an", ["ant", "ent"]],
        ["AN", ["ANT", "ENT"]],
        ["en", ["ent", "ant"]],
        ["EN", ["ENT", "ANT"]],
        ["ei", ["ait", "ais"]],
        ["EI", ["AIT", "AIS"]],
        ["on", ["ons", "ont"]],
        ["ON", ["ONS", "ONT"]],
        ["oi", ["ois", "oit", "oix"]],
        ["OI", ["OIS", "OIT", "OIX"]],
    ]),


    // Préfixes et suffixes
    aPfx1: new Set([
        "anti", "archi", "contre", "hyper", "mé", "méta", "im", "in", "ir", "par", "proto",
        "pseudo", "pré", "re", "ré", "sans", "sous", "supra", "sur", "ultra"
    ]),

    aPfx2: new Set([
        "belgo", "franco", "génito", "gynéco", "médico", "russo"
    ]),


    cut: function (sWord) {
        // returns an arry of strings (prefix, trimed_word, suffix)
        let m = /^([a-zA-Zà-öÀ-Ö0-9_ø-ÿØ-ßĀ-ʯﬁ-ﬆ]+)(-(?:t-|)(?:ils?|elles|on|je|tu|nous|vous)$)/.exec(sWord);
        if (m) {
            return ["", m[1], m[2]];
        }
        return ["", sWord, ""];
    },

    // Other functions
    filterSugg: function (aSugg) {
        return aSugg.filter((sSugg) => { return !sSugg.endsWith("è") && !sSugg.endsWith("È"); });
    }

}


if (typeof(exports) !== 'undefined') {
    exports._xTransCharsForSpelling = char_player._xTransCharsForSpelling;
    exports.spellingNormalization = char_player.spellingNormalization;
    exports._xTransCharsForSimplification = char_player._xTransCharsForSimplification;
    exports.simplifyWord = char_player.simplifyWord;
    exports.aVowel = char_player.aVowel;
    exports.aConsonant = char_player.aConsonant;
    exports.aDouble = char_player.aDouble;
    exports.d1to1 = char_player.d1to1;
    exports.d1toX = char_player.d1toX;
    exports.get1toXReplacement = char_player.get1toXReplacement;
    exports.d2toX = char_player.d2toX;
    exports.dFinal1 = char_player.dFinal1;
    exports.dFinal2 = char_player.dFinal2;
    exports.aPfx1 = char_player.aPfx1;
    exports.aPfx2 = char_player.aPfx2;
    exports.cut = char_player.cut;
    exports.filterSugg = char_player.filterSugg;
}
