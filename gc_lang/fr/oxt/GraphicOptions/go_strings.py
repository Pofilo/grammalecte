def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
        "title": "Grammalecte · Options graphiques",

        "graphic_info": "Apparence du soulignement des erreurs grammaticales et typographiques",
        "spell_info": "L’apparence du soulignement des erreurs orthographiques (trait ondulé rouge) n’est pas modifiable",

        "linetype_section": "Style de ligne (pour LibreOffice 6.3+)",
        "wave_line": "Trait ondulé fin (réglage par défaut de Writer)",
        "boldwave_line": "Trait ondulé épais (réglage par défaut de Grammalecte)",
        "bold_line": "Trait droit épais",

        "color_section": "Couleurs (pour LibreOffice 6.2+)",
        "multicolor_line": "Utiliser plusieurs couleurs",
        "multicolor_descr": "Par défaut, Writer signale les erreurs grammaticales et typographiques avec un trait ondulé de couleur bleue. Si cette option est cochée, Grammalecte attribuera des couleurs différentes aux erreurs selon leur type.",

        "restart": "Le changement ne prendra effet qu’après le redémarrage du logiciel.",

        "apply_button": "Appliquer",
        "cancel_button": "Annuler",
    },
    "en": {
        "title": "Grammalecte · Graphic options",

        "graphic_info": "Appearance of underlines for grammar and typographical mistakes",
        "spell_info": "Appearance of underlines for spelling mistakes (red thin wiggly line) can’t be modified",

        "linetype_section": "Line style (for LibreOffice 6.3+)",
        "wave_line": "Thin wiggly line (default setting of Writer)",
        "boldwave_line": "Thick wiggly line (default setting of Grammalecte)",
        "bold_line": "Thick straight line",

        "color_section": "Colors (for LibreOffice 6.2+)",
        "multicolor_line": "Use several colors",
        "multicolor_descr": "By default, Writer underlines grammar and typographical mistakes with a blue wiggly line. If this option is activated, Grammalecte uses different colors for mistakes according to the type they belong to.",

        "restart": "The modification will be effective only after restarting the software.",

        "apply_button": "Apply",
        "cancel_button": "Cancel",
    },
}
