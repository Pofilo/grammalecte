def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
        "title": "Grammalecte · Recenseur",
        
        "list_section": "Calcul des occurrences des mots",
        "count_button": "Compter tout",
        "count2_button": "Compter par lemme",
        "unknown_button": "Mots inconnus",
        "num_of_words": "Nombre de mots :",
        "tot_of_words": "Total des mots :",

        "tag_section": "Formatage",
        "tag": "Taguer",

        "close_button": "Fermer",
    },
    "en": {
        "title": "Grammalecte · Enumerator",

        "list_section": "Words",
        "count_button": "Count all",
        "count2_button": "Count by lemma",
        "unknown_button": "Unknown words",
        "num_of_words": "Number of words:",
        "tot_of_words": "Total of words:",

        "tag_section": "Format",
        "tag": "Tag",

        "close_button": "Close",
    },
}
