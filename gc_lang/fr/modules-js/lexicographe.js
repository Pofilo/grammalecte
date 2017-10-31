// Grammalecte - Lexicographe
// License: MPL 2
/*jslint esversion: 6*/
/*global require,exports*/

"use strict";

${string}
${map}


if (typeof (require) !== 'undefined') {
    var helpers = require("resource://grammalecte/helpers.js");
}

const _dTAGS = new Map([
    [':G', "[mot grammatical]"],
    [':N', " nom,"],
    [':A', " adjectif,"],
    [':M1', " prénom,"],
    [':M2', " patronyme,"],
    [':MP', " nom propre,"],
    [':W', " adverbe,"],
    [':X', " adverbe de négation,"],
    [':U', " adverbe interrogatif,"],
    [':J', " interjection,"],
    [':B', " nombre,"],
    [':T', " titre,"],

    [':R', " préposition,"],
    [':Rv', " préposition verbale,"],
    [':D', " déterminant,"],
    [':Dd', " déterminant démonstratif,"],
    [':De', " déterminant exclamatif,"],
    [':Dp', " déterminant possessif,"],
    [':Di', " déterminant indéfini,"],
    [':Dn', " déterminant négatif,"],
    [':Od', " pronom démonstratif,"],
    [':Oi', " pronom indéfini,"],
    [':On', " pronom indéfini négatif,"],
    [':Ot', " pronom interrogatif,"],
    [':Or', " pronom relatif,"],
    [':Ow', " pronom adverbial,"],
    [':Os', " pronom personnel sujet,"],
    [':Oo', " pronom personnel objet,"],
    [':C',  " conjonction,"],
    [':Ĉ',  " conjonction (él.),"],
    [':Cc', " conjonction de coordination,"],
    [':Cs', " conjonction de subordination,"],
    [':Ĉs', " conjonction de subordination (él.),"],

    [':Ŵ', " locution adverbiale (él.),"],
    [':Ñ', " locution nominale (él.),"],
    [':Â', " locution adjectivale (él.),"],
    [':Ṽ', " locution verbale (él.),"],
    [':Ŕ', " locution prépositive (él.),"],
    [':Ĵ', " locution interjective (él.),"],

    [':Zp', " préfixe,"],
    [':Zs', " suffixe,"],

    [':V1', " verbe (1ᵉʳ gr.),"],
    [':V2', " verbe (2ᵉ gr.),"],
    [':V3', " verbe (3ᵉ gr.),"],
    [':V0e', " verbe,"],
    [':V0a', " verbe,"],

    [':O1', " 1ʳᵉ pers.,"],
    [':O2', " 2ᵉ pers.,"],
    [':O3', " 3ᵉ pers.,"],

    [':e', " épicène"],
    [':m', " masculin"],
    [':f', " féminin"],
    [':s', " singulier"],
    [':p', " pluriel"],
    [':i', " invariable"],

    [':Y', " infinitif,"],
    [':P', " participe présent,"],
    [':Q', " participe passé,"],

    [':Ip', " présent,"],
    [':Iq', " imparfait,"],
    [':Is', " passé simple,"],
    [':If', " futur,"],
    [':K', " conditionnel présent,"],
    [':Sp', " subjonctif présent,"],
    [':Sq', " subjonctif imparfait,"],
    [':E', " impératif,"],

    [':1s', " 1ʳᵉ p. sg.,"],
    [':1ŝ', " présent interr. 1ʳᵉ p. sg.,"],
    [':1ś', " présent interr. 1ʳᵉ p. sg.,"],
    [':2s', " 2ᵉ p. sg.,"],
    [':3s', " 3ᵉ p. sg.,"],
    [':1p', " 1ʳᵉ p. pl.,"],
    [':2p', " 2ᵉ p. pl.,"],
    [':3p', " 3ᵉ p. pl.,"],
    [':3p!', " 3ᵉ p. pl.,"],

    [';S', " : symbole (unité de mesure)"],

    ['/*', ""],
    ['/C', " {classique}"],
    ['/M', ""],
    ['/R', " {réforme}"],
    ['/A', ""],
    ['/X', ""]
]);

const _dLocTAGS = new Map([
    [':LN', "locution nominale"],
    [':LA', "locution adjectivale"],
    [':LV', "locution verbale"],
    [':LW', "locution adverbiale"],
    [':LR', "locution prépositive"],
    [':LO', "locution pronominale"],
    [':LC', "locution conjonctive"],
    [':LJ', "locution interjective"],

    [':B', " cardinal"],
    [':e', " épicène"],
    [':m', " masculin"],
    [':f', " féminin"],
    [':s', " singulier"],
    [':p', " pluriel"],
    [':i', " invariable"],
    ['/L', " {latin}"]
]);
const _dLocVERB = new Map([
    ['i', " intransitif"],
    ['n', " transitif indirect"],
    ['t', " transitif direct"],
    ['p', " pronominal"],
    ['m', " impersonnel"],
]);

const _dPFX = new Map([
    ['d', "(de), déterminant épicène invariable"],
    ['l', "(le/la), déterminant masculin/féminin singulier"],
    ['j', "(je), pronom personnel sujet, 1ʳᵉ pers., épicène singulier"],
    ['m', "(me), pronom personnel objet, 1ʳᵉ pers., épicène singulier"],
    ['t', "(te), pronom personnel objet, 2ᵉ pers., épicène singulier"],
    ['s', "(se), pronom personnel objet, 3ᵉ pers., épicène singulier/pluriel"],
    ['n', "(ne), adverbe de négation"],
    ['c', "(ce), pronom démonstratif, masculin singulier/pluriel"],
    ['ç', "(ça), pronom démonstratif, masculin singulier"],
    ['qu', "(que), conjonction de subordination"],
    ['lorsqu', "(lorsque), conjonction de subordination"],
    ['quoiqu', "(quoique), conjonction de subordination"],
    ['jusqu', "(jusque), préposition"]
]);

const _dAD = new Map([
    ['je', " pronom personnel sujet, 1ʳᵉ pers. sing."],
    ['tu', " pronom personnel sujet, 2ᵉ pers. sing."],
    ['il', " pronom personnel sujet, 3ᵉ pers. masc. sing."],
    ['on', " pronom personnel sujet, 3ᵉ pers. sing. ou plur."],
    ['elle', " pronom personnel sujet, 3ᵉ pers. fém. sing."],
    ['nous', " pronom personnel sujet/objet, 1ʳᵉ pers. plur."],
    ['vous', " pronom personnel sujet/objet, 2ᵉ pers. plur."],
    ['ils', " pronom personnel sujet, 3ᵉ pers. masc. plur."],
    ['elles', " pronom personnel sujet, 3ᵉ pers. masc. plur."],

    ["là", " particule démonstrative"],
    ["ci", " particule démonstrative"],

    ['le', " COD, masc. sing."],
    ['la', " COD, fém. sing."],
    ['les', " COD, plur."],

    ['moi', " COI (à moi), sing."],
    ['toi', " COI (à toi), sing."],
    ['lui', " COI (à lui ou à elle), sing."],
    ['nous2', " COI (à nous), plur."],
    ['vous2', " COI (à vous), plur."],
    ['leur', " COI (à eux ou à elles), plur."],

    ['y', " pronom adverbial"],
    ["m'y", " (me) pronom personnel objet + (y) pronom adverbial"],
    ["t'y", " (te) pronom personnel objet + (y) pronom adverbial"],
    ["s'y", " (se) pronom personnel objet + (y) pronom adverbial"],

    ['en', " pronom adverbial"],
    ["m'en", " (me) pronom personnel objet + (en) pronom adverbial"],
    ["t'en", " (te) pronom personnel objet + (en) pronom adverbial"],
    ["s'en", " (se) pronom personnel objet + (en) pronom adverbial"]
]);

const _dSeparator = new Map([
    ['.', "point"],
    ['·', "point médian"],
    ['…', "points de suspension"],
    [':', "deux-points"],
    [';', "point-virgule"],
    [',', "virgule"],
    ['?', "point d’interrogation"],
    ['!', "point d’exclamation"],
    ['(', "parenthèse ouvrante"],
    [')', "parenthèse fermante"],
    ['[', "crochet ouvrante"],
    [']', "crochet fermante"],
    ['{', "accolade ouvrante"],
    ['}', "accolade fermante"],
    ['-', "tiret"],
    ['—', "tiret cadratin"],
    ['–', "tiret demi-cadratin"],
    ['«', "guillemet ouvrant (chevrons)"],
    ['»', "guillemet fermant (chevrons)"],
    ['“', "guillemet ouvrant double"],
    ['”', "guillemet fermant double"],
    ['‘', "guillemet ouvrant"],
    ['’', "guillemet fermant"],
    ['/', "signe de la division"],
    ['+', "signe de l’addition"],
    ['*', "signe de la multiplication"],
    ['=', "signe de l’égalité"],
    ['<', "inférieur à"],
    ['>', "supérieur à"],
]);


class Lexicographe {

    constructor (oDict, oTokenizer, oLocGraph) {
        this.oDict = oDict;
        this.oTokenizer = oTokenizer;
        this.oLocGraph = JSON.parse(oLocGraph);

        this._zElidedPrefix = new RegExp("^([dljmtsncç]|quoiqu|lorsqu|jusqu|puisqu|qu)['’](.+)", "i");
        this._zCompoundWord = new RegExp("([a-zA-Zà-ö0-9À-Öø-ÿØ-ßĀ-ʯ]+)-((?:les?|la)-(?:moi|toi|lui|[nv]ous|leur)|t-(?:il|elle|on)|y|en|[mts][’'](?:y|en)|les?|l[aà]|[mt]oi|leur|lui|je|tu|ils?|elles?|on|[nv]ous)$", "i");
        this._zTag = new RegExp("[:;/][a-zA-Zà-ö0-9À-Öø-ÿØ-ßĀ-ʯ*Ṽ][^:;/]*", "g");

    }

    getInfoForToken (oToken) {
        // Token: .sType, .sValue, .nStart, .nEnd
        // return a object {sType, sValue, aLabel}
        let m = null;
        try {
            switch (oToken.sType) {
                case 'SEPARATOR':
                    return {
                        sType: oToken.sType,
                        sValue: oToken.sValue,
                        aLabel: [_dSeparator.gl_get(oToken.sValue, "caractère indéterminé")]
                    };
                    break;
                case 'NUM':
                    return {
                        sType: oToken.sType,
                        sValue: oToken.sValue,
                        aLabel: ["nombre"]
                    };
                    break;
                case 'LINK':
                    return {
                        sType: oToken.sType,
                        sValue: oToken.sValue.slice(0, 40) + "…",
                        aLabel: ["hyperlien"]
                    };
                    break;
                case 'ELPFX':
                    let sTemp = oToken.sValue.replace("’", "").replace("'", "").replace("`", "").toLowerCase();
                    return {
                        sType: oToken.sType,
                        sValue: oToken.sValue,
                        aLabel: [_dPFX.gl_get(sTemp, "préfixe élidé inconnu")]
                    };
                    break;
                case 'FOLDER':
                    return {
                        sType: oToken.sType,
                        sValue: oToken.sValue.slice(0, 40) + "…",
                        aLabel: ["dossier"]
                    };
                    break;
                case 'WORD':
                    if (oToken.sValue.gl_count("-") > 4) {
                        return {
                            sType: "COMPLEX",
                            sValue: oToken.sValue,
                            aLabel: ["élément complexe indéterminé"]
                        };
                    } else if (this.oDict.isValidToken(oToken.sValue)) {
                        let lMorph = this.oDict.getMorph(oToken.sValue);
                        let aElem = [];
                        for (let s of lMorph) {
                            if (s.includes(":")) aElem.push(this._formatTags(s));
                        }
                        return {
                            sType: oToken.sType,
                            sValue: oToken.sValue,
                            aLabel: aElem
                        };
                    } else if (m = this._zCompoundWord.exec(oToken.sValue)) {
                        // mots composés
                        let lMorph = this.oDict.getMorph(m[1]);
                        let aElem = [];
                        for (let s of lMorph) {
                            if (s.includes(":")) aElem.push(this._formatTags(s));
                        }
                        aElem.push("-" + m[2] + ": " + this._formatSuffix(m[2].toLowerCase()));
                        return {
                            sType: oToken.sType,
                            sValue: oToken.sValue,
                            aLabel: aElem
                        };
                    } else {
                        return {
                            sType: "UNKNOWN",
                            sValue: oToken.sValue,
                            aLabel: ["inconnu du dictionnaire"]
                        };
                    }
                    break;
            }
        } catch (e) {
            helpers.logerror(e);
        }
        return null;
    }

    _formatTags (sTags) {
        let sRes = "";
        sTags = sTags.replace(/V([0-3][ea]?)[itpqnmr_eaxz]+/, "V$1");
        let m;
        while ((m = this._zTag.exec(sTags)) !== null) {
            sRes += _dTAGS.get(m[0]);
            if (sRes.length > 100) {
                break;
            }
        }
        if (sRes.startsWith(" verbe") && !sRes.endsWith("infinitif")) {
            sRes += " [" + sTags.slice(1, sTags.indexOf(" ")) + "]";
        }
        if (!sRes) {
            sRes = "#Erreur. Étiquette inconnue : [" + sTags + "]";
            helpers.echo(sRes);
            return sRes;
        }
        return sRes.gl_trimRight(",");
    }

    _formatTagsLoc (sTags) {
        let sRes = "";
        let sTagsVerb = sTags.replace(/(:LV)([a-z].?)(.*)/, '$2');
        sTags = sTags.replace(/(:LV)([a-z].?)(.*)/, "V$1");
        let m;
        while ((m = this._zTag.exec(sTags)) !== null) {
            sRes += _dLocTAGS.get(m[0]);
            if (m[0] == ':LV'){
                sTagsVerb.split(/(?!$)/u).forEach(function(sKey) {
                    sRes += _dLocVERB.get(sKey);
                });
            }
            if (sRes.length > 100) {
                break;
            }
        }
        if (!sRes) {
            sRes = "#Erreur. Étiquette inconnue : [" + sTags + "]";
            helpers.echo(sRes);
            return sRes;
        }
        return sRes.gl_trimRight(",");
    }

    _formatSuffix (s) {
        if (s.startsWith("t-")) {
            return "“t” euphonique +" + _dAD.get(s.slice(2));
        }
        if (!s.includes("-")) {
            return _dAD.get(s.replace("’", "'"));
        }
        if (s.endsWith("ous")) {
            s += '2';
        }
        let nPos = s.indexOf("-");
        return _dAD.get(s.slice(0, nPos)) + " +" + _dAD.get(s.slice(nPos + 1));
    }

    getListOfTokens (sText, bInfo=true) {
        let aElem = [];
        if (sText !== "") {
            for (let oToken of this.oTokenizer.genTokens(sText)) {
                if (bInfo) {
                    let aRes = this.getInfoForToken(oToken);
                    if (aRes) {
                        aElem.push(aRes);
                    }
                } else if (oToken.sType !== "SPACE") {
                    aElem.push(oToken);
                }
            }
        }
        return aElem;
    }

    generateInfoForTokenList (lToken) {
        let aElem = [];
        for (let oToken of lToken) {
            let aRes = this.getInfoForToken(oToken);
            if (aRes) {
                aElem.push(aRes);
            }
        }
        return aElem;
    }

    getListOfTokensReduc (sText, bInfo=true) {
        let aTokenList = this.getListOfTokens(sText.replace("'", "’").trim(), false);
        let iKey = 0;
        let aElem = [];
        do {
            let oToken = aTokenList[iKey];
            let sMorphLoc = '';
            let aTokenTempList = [oToken];
            if (oToken.sType == "WORD" || oToken.sType == "ELPFX"){
                let iKeyTree = iKey + 1;
                let oLocNode = this.oLocGraph[oToken.sValue.toLowerCase()];
                while (oLocNode) {
                    let oTokenNext = aTokenList[iKeyTree];
                    iKeyTree++;
                    if (oTokenNext) {
                        oLocNode = oLocNode[oTokenNext.sValue.toLowerCase()];
                    }
                    if (oLocNode && iKeyTree <= aTokenList.length) {
                        sMorphLoc = oLocNode[":"];
                        aTokenTempList.push(oTokenNext);
                    } else {
                        break;
                    }
                }
            }

            if (sMorphLoc) {
                let sValue = '';
                for (let oTokenWord of aTokenTempList) {
                    sValue += oTokenWord.sValue+' ';
                }
                let oTokenLocution = {
                    'nStart': aTokenTempList[0].nStart,
                    'nEnd': aTokenTempList[aTokenTempList.length-1].nEnd,
                    'sType': "LOC",
                    'sValue': sValue.replace('’ ','’').trim(),
                    'aSubToken': aTokenTempList
                };
                if (bInfo) {
                    let aFormatedTag = [];
                    for (let sTagLoc of sMorphLoc.split('|') ){
                        aFormatedTag.push( this._formatTagsLoc(sTagLoc) );
                    }
                    aElem.push({
                        sType: oTokenLocution.sType,
                        sValue: oTokenLocution.sValue,
                        aLabel: aFormatedTag,
                        aSubElem: this.generateInfoForTokenList(aTokenTempList)
                    });
                } else {
                    aElem.push(oTokenLocution);
                }
                iKey = iKey + aTokenTempList.length;
            } else {
                if (bInfo) {
                    let aRes = this.getInfoForToken(oToken);
                    if (aRes) {
                        aElem.push(aRes);
                    }
                } else {
                    aElem.push(oToken);
                }
                iKey++;
            }
        } while (iKey < aTokenList.length);
        return aElem;
    }
}


if (typeof(exports) !== 'undefined') {
    exports.Lexicographe = Lexicographe;
}
