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
        "num_of_entries": "Nombre d’entrées :",
        "tot_of_entries": "Total des entrées :",

        "words": "Mots",
        "lemmas": "Lemmes",
        "unknown_words": "Mots inconnus",

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
        "num_of_entries": "Number of entries:",
        "tot_of_entries": "Total of words:",

        "words": "Words",
        "lemmas": "Lemmas",
        "unknown_words": "Unknown words",

        "tag_section": "Format",
        "tag": "Tag",

        "close_button": "Close",
    },
}
