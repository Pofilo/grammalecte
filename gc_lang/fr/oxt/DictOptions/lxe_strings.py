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
        "alt_lemma": "[optionnel] Autre forme (masculine, féminine, etc.)",

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
        "v_pp": "Participe passé invariable",
        "v_pattern": "Verbe modèle [optionnel]",

        "adverb": "Adverbe",

        "other": "Autre",
        "flexion": "Flexion",
        "tags": "Étiquettes",

        # Lexicon
        "new_section": "Mots générés",
        "lexicon_section": "Votre lexique",
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
        "save_title": "Enregistrement du dictionnaire",
        "save_message": "Enregistrement fait.\nCe nouveau dictionnaire ne sera pris en compte qu’au redémarrage de LibreOffice.",
        "import_button": "Importer",
        "import_title": "Importation du dictionnaire",
        "export_button": "Exporter",
        "export_title": "Exportation du dictionnaire",
        "export_message": "Fichier exporté : ‹%s›",
        "empty_dictionary": "Le dictionnaire est vide. Aucun fichier créé.",
        "file_not_found": "Importation du fichier ‹%s›.\nCe fichier ne semble pas exister.",
        "wrong_json": "Le fichier ‹%s› n’est pas un fichier JSON valide.",
        "load_title": "Chargement du dictionnaire.",
        "not_loaded": "Le fichier n’a pas pu être chargé.\n",
        "void": "[néant]",

        # Close button
        "close_button": "Fermer",

        ##
        "verb_information": ""
    },
    # Traduction délibérément limitée
    "en": {
        "title": "Grammalecte · Lexicon editor",

        # Ajout
        "add_section": "New word (lemma)",
        "lemma": "Lemma",
        "search_button": "Search",
        "information_button": "<i>",

        # catégories
        "common_name": "Nom commun",
        "nom_adj": "Nom et adjectif",
        "nom": "Nom",
        "adj": "Adjectif",
        "alt_lemma": "[optionnel] Autre forme (masculine, féminine, etc.)",

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
        "v_pp": "Participe passé invariable",
        "v_pattern": "Verbe modèle [optionnel]",

        "adverb": "Adverbe",

        "other": "Other",
        "flexion": "Flexion",
        "tags": "Tags",

        # Lexicon
        "new_section": "Generated words",
        "lexicon_section": "Your lexicon",
        "lex_flex": "Flexions",
        "lex_lemma": "Lemmas",
        "lex_tags": "Tags",

        "add_button": "Add to the lexicon",
        "delete_button": "Delete selection",
        "save_button": "Save",

        # Dictionary
        "dictionary_section": "Dictionnaire personnel",
        "save_date_label": "Save date:",
        "num_of_entries_label": "Number of entries:",
        "save_title": "Saving dictionary",
        "save_message": "Saving done.\nThis new dictionary will be loaded after LibreOffice restart.",
        "import_button": "Import",
        "import_title": "Import dictionary",
        "export_button": "Export",
        "export_title": "Export dictionary",
        "export_message": "Exported file: ‹%s›",
        "empty_dictionary": "The dictionary is empty. No file created.",
        "file_not_found": "File import: ‹%s›.\nThis file doesn’t seem to exist.",
        "wrong_json": "The file ‹%s› is not a valid JSON file.",
        "load_title": "Dictionary loading.",
        "not_loaded": "The file couln’t be loaded.\n",
        "void": "[void]",

        # Close button
        "close_button": "Close",

        ##
        "verb_information": ""
    },
}
