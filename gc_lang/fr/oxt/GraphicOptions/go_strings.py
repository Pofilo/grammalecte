def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
        "title": "Grammalecte · Options graphiques",

        "graphic_info": "Apparence du soulignement des erreurs grammaticales et typographiques",

        "linetype_section": "Type de ligne (pour LibreOffice 6.3+)",
        "wave_line": "Vaguelette fine (réglage par défaut de Writer)",
        "boldwave_line": "Vaguelette épaisse (réglage par défaut de Grammalecte)",
        "bold_line": "Trait droit et épais",

        "color_section": "Couleurs",
        "multicolor_line": "Utiliser plusieurs couleurs",
        "multicolor_descr": "Par défaut, Writer signale les erreurs grammaticales et typographiques avec une vaguelette de couleur bleue. Si cette option est cochée, Grammalecte attribuera des couleurs différentes aux erreurs selon leur type.",

        "spell_info": "L’apparence du soulignement des erreurs orthographiques (vaguelette rouge) n’est pas modifiable",

        "restart": "Le changement ne prendra effet qu’après le redémarrage du logiciel.",

        "apply_button": "Appliquer",
        "cancel_button": "Annuler",
    },
    "en": {
        "title": "Grammalecte · Graphic options",

        "graphic_info": "Appearance of uderlines for grammar and typographical mistakes",

        "linetype_section": "Line types (for LibreOffice 6.3+)",
        "wave_line": "Thin wave (default setting of Writer)",
        "boldwave_line": "Thick wave (default setting of Grammalecte)",
        "bold_line": "Thick and straight line",

        "color_section": "Colors",
        "multicolor_line": "Use several colors",
        "multicolor_descr": "By default, Writer underlines grammar and typographical mistakes with a blue wave. If this option is activated, Grammalecte uses different colors for mistakes according to the type they belong to.",

        "spell_info": "Appearance of underlines for spelling mistakes (red and thin wave) can’t be modified",

        "restart": "The modification will be effective only after restarting the software.",

        "apply_button": "Apply",
        "cancel_button": "Cancel",
    },
}
