def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
        "title": "Grammalecte · Recherche et informations",

        "search_section": "Recherche",

        "similar_search_section": "Graphies similaires",
        "similar_search_button": "Chercher",

        "regex_search_section": "Expression régulières",
        "flexion": "Flexion",
        "tags": "Étiquettes",
        "regex_search_button": "Chercher",

        "result_section": "Résultats",
        "res_flexion": "Flexions",
        "res_lemma": "Lemmes",
        "res_tags": "Étiquettes",
        
        "close_button": "Fermer",
    },

    "en": {
        "title": "Grammalecte · Search and informations",
        
        "close_button": "Close",
    },
}
