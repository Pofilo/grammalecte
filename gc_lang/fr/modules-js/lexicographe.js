// Grammalecte - Lexicographe
// License: MPL 2

"use strict";

${string}
${map}


const helpers = require("resource://grammalecte/helpers.js");
const tkz = require("resource://grammalecte/tokenizer.js");


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
    ['—', "tiret cadratin"],
    ['–', "tiret demi-cadratin"],
    ['«', "guillemet ouvrant (chevrons)"],
    ['»', "guillemet fermant (chevrons)"],
    ['“', "guillemet ouvrant double"],
    ['”', "guillemet fermant double"],
    ['‘', "guillemet ouvrant"],
    ['’', "guillemet fermant"],
]);


class Lexicographe {

    constructor (oDict) {
        this.oDict = oDict;
        this._zElidedPrefix = new RegExp ("^([dljmtsncç]|quoiqu|lorsqu|jusqu|puisqu|qu)['’](.+)", "i");
        this._zCompoundWord = new RegExp ("([a-zA-Zà-ö0-9À-Öø-ÿØ-ßĀ-ʯ]+)-((?:les?|la)-(?:moi|toi|lui|[nv]ous|leur)|t-(?:il|elle|on)|y|en|[mts][’'](?:y|en)|les?|l[aà]|[mt]oi|leur|lui|je|tu|ils?|elles?|on|[nv]ous)$", "i");
        this._zTag = new RegExp ("[:;/][a-zA-Zà-ö0-9À-Öø-ÿØ-ßĀ-ʯ*][^:;/]*", "g");
    };

    getInfoForToken (oToken) {
        // Token: .sType, .sValue, .nStart, .nEnd
        let m = null;
        try {
            helpers.echo(oToken);
            switch (oToken.sType) {
                case 'SEPARATOR':
                    return [oToken.sType, oToken.sValue, _dSeparator._get(oToken.sValue, "caractère indéterminé")];
                    break;
                case 'NUM':
                    return [oToken.sType, oToken.sValue, "nombre"];
                    break;
                case 'LINK':
                    return [oToken.sType, oToken.sValue.slice(0,40)+"…", "hyperlien"];
                    break;
                case 'ELPFX':
                    sTemp = oToken.sValue.replace("’", "'").replace("`", "'").toLowerCase();
                    return [oToken.sType, oToken.sValue, _dPFX._get(sTemp, "préfixe élidé inconnu")];
                    break;
                case 'WORD': 
                    if (oToken.sValue._count("-") > 4) {
                        return ["COMPLEX", oToken.sValue, "élément complexe indéterminé"];
                    }
                    else if (this.oDict.isValidToken(oToken.sValue)) {
                        let lMorph = this.oDict.getMorph(oToken.sValue);
                        let aElem = [ for (s of lMorph) if (s.includes(":")) this._formatTags(s) ];
                        return [ oToken.sType, oToken.sValue, [aElem] ];
                    }
                    else if (m = this._zCompoundWord.exec(oToken.sValue)) {
                        // mots composés
                        let lMorph = this.oDict.getMorph(m[1]);
                        let aElem = [ for (s of lMorph) if (s.includes(":")) this._formatTags(s) ];
                        aElem.push("-" + m[2] + ": " + this._formatSuffix(m[2].toLowerCase()));
                        return [ oToken.sType, oToken.sValue, [aElem] ];
                    }
                    else {
                        return ["INCONNU", oToken.sValue, "inconnu du dictionnaire"];
                    }
                    break;
            }
        }
        catch (e) {
            helpers.logerror(e);
        }
        return null
    };

    getHTMLForText (sText) {
        sText = sText.replace(/[.,.?!:;…\/()\[\]“”«»"„{}–—#+*<>%=\n]/g, " ").replace(/\s+/g, " ");
        let iStart = 0;
        let iEnd = 0;
        let sHtml = '<div class="paragraph">\n';
        while ((iEnd = sText.indexOf(" ", iStart)) !== -1) {
            sHtml += this.getHTMLForToken(sText.slice(iStart, iEnd));
            iStart = iEnd + 1;
        }
        sHtml += this.getHTMLForToken(sText.slice(iStart));
        return sHtml + '</div>\n';
    };

    getHTMLForToken (sWord) {
        try {
            if (!sWord) {
                return "";
            }
            if (sWord._count("-") > 4) {
                return '<p><b class="mbok">' + sWord + "</b> <s>:</s> élément complexe indéterminé</p>\n";
            }
            if (sWord._isDigit()) {
                return '<p><b class="nb">' + sWord + "</b> <s>:</s> nombre</p>\n";
            }

            let sHtml = "";
            // préfixes élidés
            let m = this._zElidedPrefix.exec(sWord);
            if (m !== null) {
                sWord = m[2];
                sHtml += "<p><b>" + m[1] + "’</b> <s>:</s> " + _dPFX.get(m[1].toLowerCase()) + " </p>\n";
            }
            // mots composés
            let m2 = this._zCompoundWord.exec(sWord);
            if (m2 !== null) {
                sWord = m2[1];
            }
            // Morphologies
            let lMorph = this.oDict.getMorph(sWord);
            if (lMorph.length === 1) {
                sHtml += "<p><b>" + sWord + "</b> <s>:</s> " + this._formatTags(lMorph[0]) + "</p>\n";
            } else if (lMorph.length > 1) {
                sHtml += "<p><b>" + sWord + "</b><ul><li>" + [for (s of lMorph) if (s.includes(":")) this._formatTags(s)].join(" </li><li> ") + "</li></ul></p>\n";
            } else {
                sHtml += '<p><b class="unknown">' + sWord + "</b> <s>:</s>  absent du dictionnaire<p>\n";
            }
            // suffixe d’un mot composé
            if (m2) {
                sHtml += "<p>-<b>" + m2[2] + "</b> <s>:</s> " + this._formatSuffix(m2[2].toLowerCase()) + "</p>\n";
            }
            // Verbes
            //let aVerb = new Set([ for (s of lMorph) if (s.includes(":V")) s.slice(1, s.indexOf(" ")) ]);
            return sHtml;
        }
        catch (e) {
            helpers.logerror(e);
            return "#erreur";
        }
    };

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
        return sRes._trimRight(",");
    };

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
    };
}


exports.Lexicographe = Lexicographe;
