// Grammalecte - Lexicographe
// License: MPL 2
/*jslint esversion: 6*/
/*global require,exports*/

"use strict";

${string}
${map}


if (typeof(require) !== 'undefined') {
    var helpers = require("resource://grammalecte/helpers.js");
}

const _dTAGS = new Map ([
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

const _dPFX = new Map ([
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

const _dAD = new Map ([
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

const _dSeparator = new Map ([
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

    constructor (oDict) {
        this.oDict = oDict;
        this._zElidedPrefix = new RegExp ("^([dljmtsncç]|quoiqu|lorsqu|jusqu|puisqu|qu)['’](.+)", "i");
        this._zCompoundWord = new RegExp ("([a-zA-Zà-ö0-9À-Öø-ÿØ-ßĀ-ʯ]+)-((?:les?|la)-(?:moi|toi|lui|[nv]ous|leur)|t-(?:il|elle|on)|y|en|[mts][’'](?:y|en)|les?|l[aà]|[mt]oi|leur|lui|je|tu|ils?|elles?|on|[nv]ous)$", "i");
        this._zTag = new RegExp ("[:;/][a-zA-Zà-ö0-9À-Öø-ÿØ-ßĀ-ʯ*][^:;/]*", "g");
    }

    getInfoForToken (oToken) {
        // Token: .sType, .sValue, .nStart, .nEnd
        // return a list [type, token_string, values]
        let m = null;
        try {
            switch (oToken.sType) {
                case 'SEPARATOR':
                    return { sType: oToken.sType, sValue: oToken.sValue, aLabel: [_dSeparator.gl_get(oToken.sValue, "caractère indéterminé")] };
                    break;
                case 'NUM':
                    return { sType: oToken.sType, sValue: oToken.sValue, aLabel: ["nombre"] };
                    break;
                case 'LINK':
                    return { sType: oToken.sType, sValue: oToken.sValue.slice(0,40)+"…", aLabel: ["hyperlien"] };
                    break;
                case 'ELPFX':
                    let sTemp = oToken.sValue.replace("’", "").replace("'", "").replace("`", "").toLowerCase();
                    return { sType: oToken.sType, sValue: oToken.sValue, aLabel: [_dPFX.gl_get(sTemp, "préfixe élidé inconnu")] };
                    break;
                case 'WORD': 
                    if (oToken.sValue.gl_count("-") > 4) {
                        return { sType: "COMPLEX", sValue: oToken.sValue, aLabel: ["élément complexe indéterminé"] };
                    }
                    else if (this.oDict.isValidToken(oToken.sValue)) {
                        let lMorph = this.oDict.getMorph(oToken.sValue);
                        let aElem = [];
                        for (let s of lMorph){
                            if (s.includes(":"))  aElem.push( this._formatTags(s) );
                        }
                        return { sType: oToken.sType, sValue: oToken.sValue, aLabel: aElem};
                    }
                    else if (m = this._zCompoundWord.exec(oToken.sValue)) {
                        // mots composés
                        let lMorph = this.oDict.getMorph(m[1]);
                        let aElem = [];
                        for (let s of lMorph){
                            if (s.includes(":"))  aElem.push( this._formatTags(s) );
                        }
                        aElem.push("-" + m[2] + ": " + this._formatSuffix(m[2].toLowerCase()));
                        return { sType: oToken.sType, sValue: oToken.sValue, aLabel: aElem };
                    }
                    else {
                        return { sType: "UNKNOWN", sValue: oToken.sValue, aLabel: ["inconnu du dictionnaire"] };
                    }
                    break;
            }
        }
        catch (e) {
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
        return _dAD.get(s.slice(0, nPos)) + " +" + _dAD.get(s.slice(nPos+1));
    }
}


if (typeof(exports) !== 'undefined') {
    exports.Lexicographe = Lexicographe;
}
