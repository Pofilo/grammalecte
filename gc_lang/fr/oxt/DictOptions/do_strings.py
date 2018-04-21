def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
        "title": "Grammalecte · Options orthographiques",
        
        "spelling_section": "Correcteur orthographique",
        "activate_main": "Activer le correcteur orthographique de Grammalecte",
        "activate_main_descr": "Supplante le correcteur orthographique inclus dans LibreOffice (Hunspell).",

        "suggestion_section": "Moteur de suggestion orthographique",
        "activate_spell_sugg": "Moteur de suggestion de Grammalecte",
        "activate_spell_sugg_descr": "Les suggestions orthographiques des mots non reconnus par le correcteur sont fournies par Grammalecte. Si ces suggestions ne vous satisfont pas (ou si c’est trop lent), vous pouvez désactiver cette option : les suggestions orthographiques seront alors fournies par le correcteur de LibreOffice. Mais, dans ce cas, les mots que vous avez ajoutés au dictionnaire personnel de Grammalecte ne pourront pas être inclus aux suggestions.",

        "graphspell_section": "Dictionnaires de Grammalecte (Graphspell)",
        "activate_main": "Dictionnaire principal",
        "activate_main_descr": "Environ 83 000 entrées, 500 000 flexions.\nNi éditable, ni désactivable.",
        "activate_extended": "Dictionnaire étendu",
        "activate_extended_descr": "Fonctionnalité à venir",
        "activate_community": "Dictionnaire communautaire",
        "activate_community_descr": "Fonctionnalité à venir",
        "activate_personal": "Dictionnaire personnel",
        "activate_personal_descr": "Le dictionnaire personnel est créé et édité via l’éditeur lexical.",

        "restart": "Le changement ne prendra effet qu’après le redémarrage du logiciel.",

        "apply_button": "Appliquer",
        "cancel_button": "Annuler",
    },
    "en": {
        "title": "Grammalecte · Spelling options",
        
        "spelling_section": "Spell checker",
        "activate_main": "Activate the spell checker from Grammalecte",
        "activate_main_descr": "Overrides the spell checker included in LibreOffice (Hunspell)",

        "suggestion_section": "Spell suggestion engine",
        "activate_spell_sugg": "Suggestion engine of Grammalecte",
        "activate_spell_sugg_descr": "Spelling suggestions for words unrecognized by the spellchecker are provided by Grammalecte. If you aren’t satisfied by these suggestions (or if it’s too slow), you can disable this option: spelling suggestions will then be provided by the LibreOffice proofreader. In this case, words you have added in your Grammalecte’s custom dictionary won’t be included in suggestions.",

        "graphspell_section": "Grammalecte Dictionaries (Graphspell)",
        "activate_main": "Main dictionary",
        "activate_main_descr": "About 83 000 entries, 500 000 flexions.\nNot editable, not deactivable.",
        "activate_extended": "Extended dictionary",
        "activate_extended_descr": "Feature to come.",
        "activate_community": "Community dictionary",
        "activate_community_descr": "Feature to come.",
        "activate_personal": "Personal dictionary",
        "activate_personal_descr": "The personal dictionary is created and edited via the lexicon editor.",

        "restart": "The modification will be effective only after restarting the software.",

        "apply_button": "Apply",
        "cancel_button": "Cancel",
    },
}
