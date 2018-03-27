def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
        "title": "Grammalecte · Éditeur lexical",

        # Ajout
        "add_section": "Nouveau mot (lemme)",
        "lemma": "Lemme",
        "search_button": "Recherche",
        "information_button": "<i>",

        # catégories
        "common_name": "Nom commun",
        "nom_adj": "Nom et adjectif",
        "nom": "Nom",
        "adj": "Adjectif",
        "alt_lemma": "[optionnel] Autre forme (masculine, féminine, variante, etc.)",

        "proper_name": "Nom propre",
        "M1": "Prénom",
        "M2": "Patronyme",
        "MP": "Autre",

        "gender": "Genre",
        "epi": "épicène",
        "mas": "masculin",
        "fem": "féminin",
        "plural": "Pluriel",
        "-s": "pluriel en ·s",
        "-x": "pluriel en ·x",
        "inv": "invariable",

        "verb": "Verbe",
        "v_i": "intransitif",
        "v_t": "transitif",
        "v_n": "transitif indirect",
        "v_p": "pronominal",
        "v_m": "impersonnel",
        "aux": "Auxiliaire au passé composé",
        "v_ae": "être",
        "v_aa": "avoir",
        "v_pp": "Participes passés variables",
        "v_pattern": "Verbe modèle [optionnel]",

        "adverb": "Adverbe",

        "other": "Autre",
        "flexion": "Flexion",
        "tags": "Étiquettes",

        # Lexicon
        "new_section": "Mots générés",
        "lexicon_section": "Votre lexique",
        "lex_#": "#",
        "lex_flex": "Flexions",
        "lex_lemma": "Lemmes",
        "lex_tags": "Étiquettes",

        "add_button": "Ajouter au lexique",
        "delete_button": "Supprimer la sélection",
        "save_button": "Enregistrer",

        # Dictionary
        "dictionary_section": "Dictionnaire personnel",
        "save_date_label": "Date d’enregistrement :",
        "num_of_entries_label": "Nombre d’entrées :",
        "export_button": "Exporter",
        "export_title": "Exportation du dictionnaire",
        "export_message": "Fichier exporté : ‹%s>",
        "empty_dictionary": "Le dictionnaire est vide. Aucun fichier créé.",
        "void": "[néant]",

        #
        "close_button": "Fermer",
    },
    # Traduction délibérément limitée
    "en": {
        "title": "Grammalecte · Lexicon editor",
        
        "close_button": "Close",
    },
}
