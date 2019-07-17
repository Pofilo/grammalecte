// JavaScript

"use strict";

var suggest = {
    fr: new Map ([
        ["bcp", "beaucoup"],
        ["ca", "ça"],
        ["cad", "c’est-à-dire"],
        ["cb", "combien|CB"],
        ["cdlt", "cordialement"],
        ["construirent", "construire|construisirent|construisent|construiront"],
        ["càd", "c’est-à-dire"],
        ["dc", "de|donc"],
        ["done", "donc|donne"],
        ["email", "courriel|e-mail|émail"],
        ["emails", "courriels|e-mails"],
        ["ete", "êtes|été"],
        ["Etes-vous", "Êtes-vous"],
        ["Etiez-vous", "Étiez-vous"],
        ["Etions-vous", "Étions-nous"],
        ["loins", "loin"],
        ["parce-que", "parce que"],
        ["pcq", "parce que"],
        ["pd", "pendant|pédé"],
        ["pdq", "pendant que"],
        ["pdt", "pendant"],
        ["pdtq", "pendant que"],
        ["pk", "pourquoi"],
        ["pq", "pourquoi|PQ"],
        ["prq", "presque"],
        ["prsq", "presque"],
        ["qcq", "quiconque"],
        ["qq", "quelque"],
        ["qqch", "quelque chose"],
        ["qqn", "quelqu’un"],
        ["qqne", "quelqu’une"],
        ["qqs", "quelques"],
        ["qqunes", "quelques-unes"],
        ["qquns", "quelques-uns"],
        ["tdq", "tandis que"],
        ["tj", "toujours"],
        ["tjs", "toujours"],
        ["tq", "tant que|tandis que"],
        ["ts", "tous"],
        ["tt", "tant|tout"],
        ["tte", "toute"],
        ["ttes", "toutes"]
    ])
};


if (typeof(exports) !== 'undefined') {
    exports.fr = suggest.fr;
}
