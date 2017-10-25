// list of similar chars
// useful for suggestion mechanism

${map}


var char_player = {

    _dTransChars: new Map([
        ['à', 'a'],  ['é', 'e'],  ['î', 'i'],  ['ô', 'o'],  ['û', 'u'],  ['ÿ', 'y'],
        ['â', 'a'],  ['è', 'e'],  ['ï', 'i'],  ['ö', 'o'],  ['ù', 'u'],  ['ŷ', 'y'],
        ['ä', 'a'],  ['ê', 'e'],  ['í', 'i'],  ['ó', 'o'],  ['ü', 'u'],  ['ý', 'y'],
        ['á', 'a'],  ['ë', 'e'],  ['ì', 'i'],  ['ò', 'o'],  ['ú', 'u'],  ['ỳ', 'y'],
        ['ā', 'a'],  ['ē', 'e'],  ['ī', 'i'],  ['ō', 'o'],  ['ū', 'u'],  ['ȳ', 'y'],
        ['ñ', 'n'],
        ['œ', 'oe'], ['æ', 'ae'], 
    ]),

    cleanWord: function (sWord) {
        // word simplication before calculating distance between words
        sWord = sWord.toLowerCase();
        let sRes = "";
        for (let c of sWord) {
            sRes += this._dTransChars.gl_get(c, c);
        }
        return sWord.replace("eau", "o").replace("au", "o");
    },

    distanceDamerauLevenshtein: function (s1, s2) {
        // distance of Damerau-Levenshtein between <s1> and <s2>
        // https://fr.wikipedia.org/wiki/Distance_de_Damerau-Levenshtein
        try {
            let nLen1 = s1.length;
            let nLen2 = s2.length;
            let matrix = [];
            for (let i = 0;  i <= nLen1;  i++) {
                matrix[i] = new Array(nLen2 + 1);
            }
            for (let i = 0;  i <= nLen1;  i++) {
                matrix[i][0] = i;
            }
            for (let j = 0;  j <= nLen2;  j++) {
                matrix[0][j] = j;
            }
            for (let i = 1;  i <= nLen1;  i++) {
                for (let j = 1;  j <= nLen2;  j++) {
                    let nCost = (s1[i] === s2[j]) ? 0 : 1;
                    matrix[i][j] = Math.min(
                        matrix[i-1][j] + 1,         // Deletion
                        matrix[i][j-1] + 1,         // Insertion
                        matrix[i-1][j-1] + nCost    // Substitution
                    );
                    if (i > 1 && j > 1 && s1[i] == s2[j-1] && s1[i-1] == s2[j]) {
                        matrix[i][j] = Math.min(matrix[i][j], matrix[i-2][j-2] + nCost);  // Transposition
                    }
                }
            }
            //console.log(s2 + ": " + matrix[nLen1][nLen2]);
            return matrix[nLen1][nLen2];
        }
        catch (e) {
            helpers.logerror(e);
        }
    },


    // Method: Remove Useless Chars

    aVovels: new Set([
        'a', 'e', 'i', 'o', 'u', 'y',
        'à', 'é', 'î', 'ô', 'û', 'ÿ',
        'â', 'è', 'ï', 'ö', 'ù', 'ŷ',
        'ä', 'ê', 'í', 'ó', 'ü', 'ý',
        'á', 'ë', 'ì', 'ò', 'ú', 'ỳ',
        'ā', 'ē', 'ī', 'ō', 'ū', 'ȳ',
        'h', 'œ', 'æ'
    ]),

    shrinkWord: function (sWord) {
        // remove vovels and h
        let sRes = "";
        for (let cChar of sWord.slice(1)) {
            if (!this.aVovels.has(cChar)) {
                sRes += cChar;
            }
        }
        return sWord.slice(0, 1).replace("h", "") + sRes;
    },


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
        ["ç", ["ss", "cc", "qh", "ch"]],
        ["Ç", ["SS", "CC", "QH", "CH"]],
        ["d", ["dd",]],
        ["D", ["DD",]],
        ["f", ["ff", "ph"]],
        ["F", ["FF", "PH"]],
        ["g", ["gu", "ge", "gg", "gh"]],
        ["G", ["GU", "GE", "GG", "GH"]],
        ["i", ["ii",]],
        ["I", ["II",]],
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

    d2toX: new Map([
        ["an", ["en",]],
        ["AN", ["EN",]],
        ["au", ["eau", "o", "ô"]],
        ["AU", ["EAU", "O", "Ô"]],
        ["en", ["an",]],
        ["EN", ["AN",]],
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
        ["oi", ["oa", "oie"]],
        ["OI", ["OA", "OIE"]],
        ["qu", ["q", "cq", "ck", "c", "k"]],
        ["QU", ["Q", "CQ", "CK", "C", "K"]],
        ["ss", ["c", "ç"]],
        ["SS", ["C", "Ç"]],
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
