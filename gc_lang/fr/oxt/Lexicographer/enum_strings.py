# strings for Enumerator

sUI = "fr"


def selectLang (sLang):
    global sUI
    if sLang in dStrings:
        sUI = sLang


def get (sMsgCode):
    try:
        return dStrings[sUI].get(sMsgCode, sMsgCode)
    except:
        return "#error"


dStrings = {
    "fr": {
        "title": "Grammalecte · Recenseur de mots",

        "list_section": "Énumération des occurrences",
        "count_button": "Compter tout",
        "count2_button": "Compter par lemme",
        "unknown_button": "Mots inconnus",
        "num_of_entries": "Entrées :",
        "tot_of_entries": "Total :",
        "goto": "Sélectionnez une ou plusieurs entrées, puis cliquez sur ce bouton pour trouver la prochaine occurrence",
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
        "goto": "select one or several entries, then click on this button to find the next occurrence",
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
