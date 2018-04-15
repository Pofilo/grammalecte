def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
        "title": "Grammalecte · Informations",

        "information_section": "Informations",

        "save": "Enregistrement",
        "save_desc": "Les modifications apportées au lexique ne sont enregistrées dans le dictionnaire qu’au moment où vous cliquez sur ‹Enregistrer›.",

        "duplicates": "Doublons",
        "duplicates_desc": "Il est inutile de purger votre lexique des doublons éventuels. Les doublons sont automatiquement supprimés lors de la création du dictionnaire.",

        "compilation": "Compilation du dictionnaire",
        "compilation_desc": "Le dictionnaire est compilé comme un graphe de mots compressé sous la forme d’une chaîne binaire dans un fichier JSON. Cette opération peut prendre du temps et consommer beaucoup de mémoire si votre lexique contient plusieurs dizaines de milliers d’entrées.",

        "warning": "Avertissement",
        "warning_desc": "Il est déconseillé d’utiliser la catégorie ‹Autre› pour générer autre chose que des noms, des adjectifs, des noms propres, des verbes et des adverbes. Il n’y a aucune garantie que les étiquettes pour les autres catégories, notamment les mots grammaticaux, ne changeront pas.",

        "tags_section": "Signification des étiquettes",
        "tags": "Étiquettes",
        "meaning": "Signification",

        "close_button": "Fermer"
    },

    "en": {
        "title": "Grammalecte · Informations",
        
        "information_section": "Informations",

        "save": "Save",
        "save_desc": "Modifications to the lexicon are only saved in the dictionary when you click on ‹Save›.",

        "duplicates": "Duplicates",
        "duplicates_desc": "It is useless to expurgate your lexicon from duplicates. Duplicates are automatically deleted when the dictionary is created.",

        "compilation": "Dictionary compilation",
        "compilation_desc": "The dictionary is compiled as a word graph compressed as a binary string in a JSON file. This operation may be long and use a lot of memory and CPU resources if your lexicon contains several thousands of entries.",

        "warning": "Warning",
        "warning_desc": "You shouldn’t use the category ‹Other› to generate words which are not names, adjectives, proper names, verbs and adverbs. There is no garantee that tags used for other categories won’t change.",

        "tags_section": "Tags meaning",
        "tags": "Tags",
        "meaning": "Meaning",

        "close_button": "Close"
    },
}
