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
        "activate_spell_sugg": "Activer le moteur de suggestion de Grammalecte",
        "activate_spell_sugg_descr": "Désactivée, cette option remplace la suggestion orthographique de Grammalecte par celle fournie par LibreOffice (Hunspell). Les mots inclus dans le dictionnaire personnalisé ne seront plus inclus aux suggestions.",

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
        "activate_spell_sugg": "Activate the suggestion engine of Grammalecte",
        "activate_spell_sugg_descr": "Disactivated, this option replace the spell suggestion engine of Grammalecte by the one of LibreOffice (Hunspell). Words included in the personal dictionary won’t be included among suggestions.",

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
