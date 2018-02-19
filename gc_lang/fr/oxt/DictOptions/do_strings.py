def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
        "title": "Grammalecte · Options des dictionnaires",
        
        "spelling_section": "Correcteur orthographique",
        "activate_main": "Activer le correcteur orthographique de Grammalecte",
        "activate_main_descr": "Supplante le correcteur orthographique inclus dans LibreOffice (Hunspell).",

        "personal_section": "Dictionnaire personnel",
        "activate_personal": "Utiliser",
        "activate_personal_descr": "Le dictionnaire personnel est une commodité pour ajouter le vocabulaire qui vous est utile. Il ne supplante pas le dictionnaire commun ; il ne fait qu’ajouter de nouveaux mots.",
        "import_personal": "Importer un dictionnaire personnel",
        "import_button": "Importer",
        "create_dictionary": "Vous pouvez créer un dictionnaire personnel avec l’extension Grammalecte pour Firefox ou Chrome.",

        "suggestion_section": "Moteur de suggestion orthographique",
        "activate_spell_sugg": "Activer le moteur de suggestion de Grammalecte",
        "activate_spell_sugg_descr": "Désactivée, cette option remplace la suggestion orthographique de Grammalecte par celle fournie par LibreOffice (Hunspell). Les mots inclus dans le dictionnaire personnalisé ne seront plus inclus aux suggestions.",

        "apply_button": "Appliquer",
        "cancel_button": "Annuler",
    },
    "en": {
        "title": "Grammalecte · Options for dictionaries",
        
        "spelling_section": "Spell checker",
        "activate_main": "Activate the spell checker from Grammalecte",
        "activate_main_descr": "Overrides the spell checker included in LibreOffice (Hunspell)",

        "personal_section": "Personal dictionary",
        "activate_personal": "Use",
        "activate_personal_descr": "The personal dictionary is a commodity to add the vocabulary you want. It doesn’t override the common dictionary ; it only adds new words.",
        "import_personal": "Import a personal dictionary",
        "import_button": "Import",
        "create_dictionary": "You can create a personal dictionary with the Grammalecte addon for Firefox or Chrome.",

        "suggestion_section": "Spell suggestion engine",
        "activate_spell_sugg": "Activate the suggestion engine of Grammalecte",
        "activate_spell_sugg_descr": "Disactivated, this option replace the spell suggestion engine of Grammalecte by the one of LibreOffice (Hunspell). Words included in the personal dictionary won’t be included among suggestions.",

        "apply_button": "Apply",
        "cancel_button": "Cancel",
    },
}
