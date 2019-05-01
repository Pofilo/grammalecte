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

        "graphspell_section": "Dictionnaires actifs",
        "activate_main": "Dictionnaire principal",
        "activate_main_descr": "Environ 83 000 entrées, 500 000 flexions.\nNi éditable, ni désactivable.",
        "spelling": "Orthographe",
        "spelling_descr": "Le dictionnaire “Classique” propose l’orthographe telle qu’elle est écrite aujourd’hui le plus couramment. C’est le dictionnaire recommandé. Il contient les graphies usuelles et classiques, certaines encore communément utilisées, d’autres désuètes.\n\nAvec le dictionnaire “Réforme 1990”, seule l’orthographe réformée est reconnue. Attendu que bon nombre de graphies réformées sont considérées comme erronées par beaucoup, ce dictionnaire est déconseillé. Les graphies passées dans l’usage sont déjà incluses dans le dictionnaire “Classique”.\n\nLe dictionnaire “Toutes variantes” contient toutes les graphies, classiques ou réformées, ainsi que d’autres plus rares encore. Ce dictionnaire est déconseillé à ceux qui ne connaissent pas très bien la langue française.\n\n[Linux] Si vous utilisez Linux, il est possible que votre système impose, en plus du correcteur orthographique de Grammalecte (appelé Graphspell), un autre correcteur orthographique (nommé Hunspell) qui utilise un dictionnaire différent. Dans ce cas, vous devez aller dans les options linguistiques de LibreOffice pour désactiver le correcteur Hunspell pour la langue concernée (fr_…), afin que votre réglage soit respecté.",
        "allvars": "Toutes variantes",
        "classic": "Classique",
        "reform": "Réforme 1990",
        "activate_community": "Dictionnaire communautaire",
        "activate_community_descr": "Fonctionnalité à venir",
        "activate_personal": "Dictionnaire personnel",
        "activate_personal_descr": "Créable et éditable via l’éditeur lexical.",

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

        "graphspell_section": "Active dictionaries",
        "activate_main": "Main dictionary",
        "activate_main_descr": "About 83 000 entries, 500 000 flexions.\nNot editable, not deactivable.",
        "spelling": "Spelling",
        "spelling_descr": "The dictionary “Classic” offers the French spelling as it is written nowadays most often. This is the recommended dictionary. It contains usual and classical spellings, some of them still widely used, others obsolete.\n\nWith the dictionary “Reform 1990”, only the reformed spelling is recognized. As many of reformed spellings are considered erroneous by many people, this dictionary is unadvised. Reformed spellings commonly used are already included in the “Classic” dictionary.\n\nThe dictionary “All variants” contains all spelling variants, classical and reformed, and some others even rarer. This dictionary is unadvised for those who don’t know very well the French language.\n\n[Linux] If you use Linux, your system may force LibreOffice to use another spellchecker service (called Hunspell), which uses another dictionary, on top of the Grammalecte’s spellchecker (called Graphspell). In this case, if you want to ensure your settings are respected, you may deactivate the spellchecker Hunspell for the concerned language (fr_…) in the linguistics options of LibreOffice.",
        "allvars": "All variants",
        "classic": "Classic",
        "reform": "Reform 1990",
        "activate_community": "Community dictionary",
        "activate_community_descr": "Feature to come.",
        "activate_personal": "Personal dictionary",
        "activate_personal_descr": "Creatible and editable via the lexicon editor.",

        "restart": "The modification will be effective only after restarting the software.",

        "apply_button": "Apply",
        "cancel_button": "Cancel",
    },
}
