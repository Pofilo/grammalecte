/*
    ! Grammalecte, grammar checker !
    API pour faciliter l'utilisation de Grammalecte.
*/

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global require, exports, console */

"use strict";

class GrammarChecker {

    constructor(aInit, sPathRoot = "", sLangCode = "fr", sContext = "Javascript") {
        this.sLangCode = sLangCode;
        this.sPathRoot = sPathRoot;
        this.sContext = sContext;

        //Importation des fichiers nécessaire
        this._helpers = require(sPathRoot + "/graphspell/helpers.js");

        this.isInit = {
            Grammalecte: false,
            Graphspell: false,
            Tokenizer: false,
            TextFormatter: false,
            Lexicographer: false
        };

        if (aInit){
            this.load(aInit);
        }
    }

    //Auto-chargement avec dépendence
    load(aInit = ["Grammalecte", "Graphspell", "TextFormatter", "Lexicographer", "Tokenizer"]){
        //aInit permet de charger que certain composant
        // => évite de charger toutes données si par exemple on a besoin que du lexigraphe
        // => sorte de gestionnaire de dépendence (peut être amélioré)
        this.isInit = {};
        if ( aInit.indexOf("Grammalecte") !== false ){
            //console.log('init Grammalecte');
            this._oGce = require(this.sPathRoot + "/fr/gc_engine.js");
            this._oGce.load(this.sContext);
            this.isInit.Grammalecte = true;
            this.oSpellChecker = this._oGce.getSpellChecker();
            this.isInit.Graphspell = true;
            this.oTokenizer = this.oSpellChecker.getTokenizer();
            this.isInit.Tokenizer = true;
        }

        if ( !this.isInit.Graphspell && (aInit.indexOf("Graphspell") !== false || aInit.indexOf("Lexicographer") !== false)){
            //console.log('init Graphspell');
            this._SpellChecker = require(this.sPathRoot + "/graphspell/spellchecker.js");
            this.oSpellChecker = new this._SpellChecker.SpellChecker(this.sLangCode, this.sPathRoot + "/graphspell/_dictionaries");
            this.isInit.Graphspell = true;
            this.oTokenizer = this.oSpellChecker.getTokenizer();
            this.isInit.Tokenizer = true;
        }

        if ( !this.isInit.Tokenizer && aInit.indexOf("Tokenizer") !== false ){
            //console.log('init Tokenizer');
            this._Tokenizer = require(this.sPathRoot + "/graphspell/tokenizer.js");
            this.oTokenizer = new this._Tokenizer.Tokenizer(this.sLangCode);
            this.isInit.Tokenizer = true;
        }

        if ( aInit.indexOf("TextFormatter") !== false ){
            //console.log('init TextFormatter');
            this._oText = require(this.sPathRoot + "/fr/textformatter.js");
            this.oTextFormatter = new this._oText.TextFormatter();
            this.isInit.TextFormatter = true;
        }

        if ( aInit.indexOf("Lexicographer") !== false ){
            //console.log('init Lexicographer');
            this._oLex = require(this.sPathRoot + "/fr/lexicographe.js");
            this.oLexicographer = new this._oLex.Lexicographe(
                this.oSpellChecker,
                this.oTokenizer,
                this._helpers.loadFile(this.sPathRoot + "/fr/locutions_data.json")
            );
            this.isInit.Lexicographer = true;
        }
    }

    //Fonctions concernant: Grammalecte
    getGrammalecte(){
        if (!this.isInit.Grammalecte) {
            this.load(["Grammalecte"]);
        }
        return this._oGce;
    }

    gramma(sText){
        if (!this.isInit.Grammalecte) {
            this.load(["Grammalecte"]);
        }
        return Array.from(this._oGce.parse(sText, this.sLangCode));
    }

    getGceOptions () {
        if (!this.isInit.Grammalecte) {
            this.load(["Grammalecte"]);
        }
        return this._helpers.mapToObject(this._oGce.getOptions());
    }

    getGceDefaultOptions () {
        if (!this.isInit.Grammalecte) {
            this.load(["Grammalecte"]);
        }
        return this._helpers.mapToObject(this._oGce.getDefaultOptions());
    }

    setGceOptions (dOptions) {
        if (!this.isInit.Grammalecte) {
            this.load(["Grammalecte"]);
        }
        if (!(dOptions instanceof Map)) {
            dOptions = this._helpers.objectToMap(dOptions);
        }
        this._oGce.setOptions(dOptions);
        return this._helpers.mapToObject(this._oGce.getOptions());
    }

    setGceOption (sOptName, bValue) {
        if (!this.isInit.Grammalecte) {
            this.load(["Grammalecte"]);
        }
        if (sOptName) {
            this._oGce.setOption(sOptName, bValue);
            return this._helpers.mapToObject(this._oGce.getOptions());
        }
    }

    resetOptions () {
        if (!this.isInit.Grammalecte) {
            this.load(["Grammalecte"]);
        }
        this._oGce.resetOptions();
        return this._helpers.mapToObject(this._oGce.getOptions());
    }

    //Fonctions concernant: Graphspell
    getGraphspell(){
        if (!this.isInit.Graphspell) {
            this.load(["Graphspell"]);
        }
        return this.oSpellChecker;
    }

    spellParagraph(sText, bSuggest = true){
        if (!this.isInit.Graphspell) {
            this.load(["Graphspell"]);
        }
        if (bSuggest){
            let lError = this.oSpellChecker.parseParagraph(sText);
            for (let token of lError) {
                token.aSuggestions = this.suggest(token.sValue);
            }
            return lError;
        } else {
            return this.oSpellChecker.parseParagraph(sText);
        }
    }

    spell(sWord){
        if (!this.isInit.Graphspell) {
            this.load(["Graphspell"]);
        }
        return this.oSpellChecker.isValid(sWord);
    }

    suggest(sWord, nbLimit = 10, bMerge = true){
        if (!this.isInit.Graphspell) {
            this.load(["Graphspell"]);
        }
        let lSuggest = this.oSpellChecker.suggest(sWord, nbLimit);
        if (bMerge){
            let lSuggestRep = [];
            for (let lSuggestTmp of lSuggest) {
                for (let word of lSuggestTmp) {
                    lSuggestRep.push(word);
                }
            }
            return lSuggestRep;
        } else {
            return Array.from(lSuggest);
        }

    }

    lemma(sWord){
        if (!this.isInit.Graphspell) {
            this.load(["Graphspell"]);
        }
        return this.oSpellChecker.getLemma(sWord);
    }

    morph(sWord){
        if (!this.isInit.Graphspell) {
            this.load(["Graphspell"]);
        }
        return this.oSpellChecker.getMorph(sWord);
    }

    //Fonctions concernant: Lexicographer
    getLexicographer(){
        if (!this.isInit.Lexicographer) {
            this.load(["Lexicographer"]);
        }
        return this.oLexicographer;
    }

    lexique(sText){
        if (!this.isInit.Lexicographer) {
            this.load(["Lexicographer"]);
        }
        return this.oLexicographer.getListOfTokensReduc(sText);
    }

    //Fonctions concernant: TextFormatter
    getTextFormatter(){
        if (!this.isInit.TextFormatter) {
            this.load(["TextFormatter"]);
        }
        return this.oTextFormatter;
    }

    formatText(sText){
        if (!this.isInit.TextFormatter) {
            this.load(["TextFormatter"]);
        }
        return this.oTextFormatter.formatText(sText);
    }

    //fonctions concernant plussieurs parties
    verifParagraph(sText, bSuggest = true){
        if (!this.isInit.Grammalecte || !this.isInit.Graphspell) {
            this.load(["Grammalecte"]);
        }
        return {
            lGrammarErrors: Array.from(this._oGce.parse(sText, this.sLangCode)),
            lSpellingErrors: this.spellParagraph(sText, bSuggest)
        };
    }

}

if (typeof exports !== "undefined") {
    exports.GrammarChecker = GrammarChecker;
}
