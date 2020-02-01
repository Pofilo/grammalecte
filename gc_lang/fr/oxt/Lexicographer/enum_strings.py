def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
        "title": "Grammalecte · Recenseur de mots",

        "list_section": "Énumération des occurrences",
        "count_button": "Compter tout",
        "count2_button": "Compter par lemme",
        "unknown_button": "Mots inconnus",
        "num_of_entries": "Entrées :",
        "tot_of_entries": "Total :",
        "export": "Exporter",

        "words": "Mots",
        "lemmas": "Lemmes",
        "unknown_words": "Mots inconnus",

        "dformat_section": "Formatage direct",
        "charstyle_section": "Style de caractères",
        "underline": "Surligner",
        "nounderline": "Effacer",
        "emphasis": "Accentuation",
        "strong_emphasis": "Accentuation forte",
        "nostyle": "Aucun",
        "tag_button": "Taguer",

        "export_title": "Exportation des données",

        "close_button": "Fermer",
    },
    "en": {
        "title": "Grammalecte · Enumerator of words",

        "list_section": "Occurrences enumeration",
        "count_button": "Count all",
        "count2_button": "Count by lemma",
        "unknown_button": "Unknown words",
        "num_of_entries": "Entries:",
        "tot_of_entries": "Total:",
        "export": "Export",

        "words": "Words",
        "lemmas": "Lemmas",
        "unknown_words": "Unknown words",

        "dformat_section": "Direct format",
        "charstyle_section": "Character style",
        "underline": "Underline",
        "nounderline": "Erase",
        "emphasis": "Emphasis",
        "strong_emphasis": "Strong emphasis",
        "nostyle": "None",
        "tag_button": "Tag",

        "export_title": "Data export",

        "close_button": "Close",
    },
}
