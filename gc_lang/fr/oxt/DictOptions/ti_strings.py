def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
        "title": "Grammalecte · Informations",

        "information_section": "Informations",

        "save": "Enregistrement",
        "save_desc": "Les modifications apportées au lexique ne sont enregistrées dans le dictionnaire qu’au moment où vous cliquez sur ‹Enregistrer› dans l’onglet ‹Lexique›.",

        "duplicates": "Doublons",
        "duplicates_desc": "Il est inutile de purger votre lexique des doublons éventuels. Les doublons sont automatiquement supprimés lors de la création du dictionnaire.",

        "compilation": "Compilation du dictionnaire",
        "compilation_desc": "Le dictionnaire est compilé comme un graphe de mots sous la forme d’une chaîne binaire dans un fichier JSON. Cette opération peut prendre du temps et consommer beaucoup de mémoire si votre lexique contient plusieurs dizaines de milliers d’entrées.",

        "warning": "Avertissement",
        "warning_desc": "Il est déconseillé d’utiliser la catégorie ‹Autre› pour générer autre chose que des noms, des adjectifs, des noms propres, des verbes et des adverbes. Il n’y a aucune garantie que les étiquettes pour les autres catégories, notamment les mots grammaticaux, ne changeront pas.",

        "tags_section": "Signification des étiquettes",
        "tags": "Étiquettes",
        "meaning": "Signification",


        "close_button": "Fermer",
    },

    "en": {
        "title": "Grammalecte · Informations",
        
        "close_button": "Close",
    },
}
