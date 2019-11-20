
def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
        "title": "Grammalecte · Formateur de texte [Français]",

        "ssp": "Espaces ~surnuméraires",
        "ssp1": "En début de paragraphe",
        "ssp2": "Entre les mots",
        "ssp3": "En fin de paragraphe",
        "ssp4": "Avant les points (.), les virgules (,)",
        "ssp5": "À l’intérieur des parenthèses",
        "ssp6": "À l’intérieur des crochets",
        "ssp7": "À l’intérieur des guillemets “ et ”",

        "space": "Espaces ~manquants",
        "space1": "Après , ; : ? ! . …",
        "space2": "Autour des tirets d’incise",

        "nbsp": "Espaces ~insécables",
        "nbsp1": "Avant : ; ? et !",
        "nbsp2": "Avec les guillemets « et »",
        "nbsp3": "Avant % ‰ € $ £ ¥ ˚C",
        "nbsp4": "À l’intérieur des nombres",
        "nbsp5": "Avant les unités de mesure",
        "nbsp6": "Après les titres de civilité",
        "nnbsp": "fins",
        "nnbsp_help": "sauf avec “:”",

        "delete": "Su~ppressions",
        "delete1": "Tirets conditionnels",
        "delete2": "Puces  → tirets cadratins + style :",
        "delete2a": "Standard",
        "delete2b": "Corps de texte",
        "delete2c": "Ø",
        "delete2c_help": "Pas de changement",

        "typo": "Signes ~typographiques",
        "typo1": "Apostrophe (’)",
        "typo2": "Points de suspension (…)",
        "typo3": "Tirets d’incise :",
        "typo4": "Tirets en début de paragraphe :",
        "emdash": "cadratin (—)",
        "endash": "demi-cadratin (–)",
        "typo5": "Modifier les guillemets droits (\" et ')",
        "typo6": "Points médians des unités (N·m, Ω·m…)",
        "typo7": "Ligatures et diacritiques (cœur, ça, Étude…)",
        "typo8": "Ligatures",
        "typo8_help": "Avertissement : de nombreuses polices ne contiennent pas ces caractères.",
        "typo8a": "Faire",
        "typo8b": "Défaire",
        "typo_ff": "ff",
        "typo_fi": "fi",
        "typo_ffi": "ffi",
        "typo_fl": "fl",
        "typo_ffl": "ffl",
        "typo_ft": "ft",
        "typo_st": "st",

        "misc": "~Divers",
        "misc1": "Ordinaux (15e, XXIe…)",
        "misc1a": "e → ᵉ",
        "misc2": "Et cætera, etc.",
        "misc3": "Traits d’union manquants",
        "misc5": "Apostrophes manquantes",
        "misc5b": "lettres isolées (j’ n’ m’ t’ s’ c’ d’ l’)",
        "misc5c": "Maj.",

        "struct": "~Restructuration [!]",
        "struct_help": "Attention : la restructuration coupe ou fusionne les paragraphes.",
        "struct1": "Retour à la ligne ⇒ fin de paragraphe",
        "struct2": "Enlever césures en fin de ligne/paragraphe",
        "struct3": "Fusionner les paragraphes contigus [!]",
        "struct3_help": "Concatène tous les paragraphes non séparés par un paragraphe vide.\nAttention : LibreOffice et OpenOffice ne peuvent accepter des paragraphes de plus de 65535 caractères, ce qui fait environ 12 pages avec une police de taille 12. Un dépassement de cette limite fera planter le logiciel. À partir de LibreOffice 4.3, cette limitation n’existe plus.",

        "default": "[·]",
        "default_help": "Options par défaut",

        "bsel": "Sur la sélection active",
        "apply": "~Appliquer",
        "close": "~Fermer",

        "info": "(i)",
        "infotitle": "Informations",
        "infomsg": "Le formateur de texte est un outil qui automatise la correction d’erreurs typographiques en employant le moteur interne “Chercher & remplacer” de Writer.\n\nUtilisez l’outil avec prudence. À cause de certaines limitations, le formateur ne peut gérer tous les cas. Vérifiez votre texte après emploi."
    },
    "en": {
        "title": "Grammalecte · Text Formatter [French]",

        "ssp": "~Supernumerary spaces",
        "ssp1": "At the beginning of paragraph",
        "ssp2": "Between words",
        "ssp3": "At the end of paragraph",
        "ssp4": "Before dots (.), commas (,)",
        "ssp5": "Within parenthesis",
        "ssp6": "Within square brackets",
        "ssp7": "Within “ and ”",

        "space": "~Missing spaces",
        "space1": "After , ; : ? ! . …",
        "space2": "Surrounding dashes",

        "nbsp": "~Non-breaking spaces ",
        "nbsp1": "Before : ; ? and !",
        "nbsp2": "With quoting marks « and »",
        "nbsp3": "Before % ‰ € $ £ ¥ ˚C",
        "nbsp4": "Within numbers",
        "nbsp5": "Before units of measurement",
        "nbsp6": "After titles",
        "nnbsp": "narrow",
        "nnbsp_help": "except with “:”",

        "delete": "~Deletions",
        "delete1": "Soft hyphens",
        "delete2": "Bullets  → em-dash + style:",
        "delete2a": "Standard",
        "delete2b": "Text Body",
        "delete2c": "Ø",
        "delete2c_help": "No change",

        "typo": "~Typographical signs",
        "typo1": "Apostrophe (’)",
        "typo2": "Ellipsis (…)",
        "typo3": "Dashes:",
        "typo4": "Dashes at beginning of paragraph:",
        "emdash": "em dash (—)",
        "endash": "en dash (–)",
        "typo5": "Change quotation marks (\" and ')",
        "typo6": "Interpuncts in units (N·m, Ω·m…)",
        "typo7": "Ligatures and diacritics (cœur, ça, Étude…)",
        "typo8": "Ligatures",
        "typo8_help": "Warning: many fonts don’t contain these characters.",
        "typo8a": "Set",
        "typo8b": "Unset",
        "typo_ff": "ff",
        "typo_fi": "fi",
        "typo_ffi": "ffi",
        "typo_fl": "fl",
        "typo_ffl": "ffl",
        "typo_ft": "ft",
        "typo_st": "st",


        "misc": "M~iscellaneous",
        "misc1": "Ordinals (15e, XXIe…)",
        "misc1a": "e → ᵉ",
        "misc2": "Et cætera, etc.",
        "misc3": "Missing hyphens",
        "misc5": "Missing apostrophes",
        "misc5b": "single letters (j’ n’ m’ t’ s’ c’ d’ l’)",
        "misc5c": "Cap.",

        "struct": "~Restructuration [!]",
        "struct_help": "Caution: Restructuration cuts or merges paragraphs.",
        "struct1": "End of line ⇒ end of paragraph",
        "struct2": "Remove syllabification hyphens at EOL/EOP",
        "struct3": "Merge contiguous paragraphs [!]",
        "struct3_help": "Concatenate all paragraphs not separated by an empty paragraph.\nCaution: LibreOffice and OpenOffice can’t deal with paragraphs longer than 65,535 characters, which is about 12 pages with font size 12. Overstepping this limit will crash the software. For LibreOffice 4.3 and beyond, this limitation doesn’t exist any more.",

        "default": "[·]",
        "default_help": "Default options",

        "bsel": "On current selection",
        "apply": "~Apply",
        "close": "~Close",

        "info": "(i)",
        "infotitle": "Informations",
        "infomsg": "The text formatter is a tool which automates correction of typographical errors by using the internal engine “Search & replace” of Writer.\n\nUse this tool with caution. Due to several limitations, it cannot handle all cases. Check your text after use."
    }
}


