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
        "result_warning": "La recherche par expressions régulières peut générer un nombre gigantesque de résultats. Seules les 2000 premières occurrences trouvées seront affichées. La recherche peut être longue, parce tout le graphe de mots, qui contient 500 000 flexions, sera parcouru si besoin.",

        "result_section": "Résultats",
        "res_flexion": "Flexions",
        "res_lemma": "Lemmes",
        "res_tags": "Étiquettes",
        
        "close_button": "Fermer",

        "error": "Erreur",
        "regex_error_flexion": "L’expression régulière du champ ‹Flexion› est erronée.",
        "regex_error_tags": "L’expression régulière du champ ‹Étiquettes› est erronée."
    },

    "en": {
        "title": "Grammalecte · Search and informations",
        
        "close_button": "Close",
    },
}
