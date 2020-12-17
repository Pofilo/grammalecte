# Strings for Text Formatter Editor


sUI = "fr"


def selectLang (sLang):
    global sUI
    if sLang in dStrings:
        sUI = sLang


def get (sMsgCode):
    try:
        return dStrings[sUI].get(sMsgCode, sMsgCode)
    except:
        return "#error"


dStrings = {
    "fr": {
        "title": "Grammalecte · Éditeur des transformations personnalisées",

        "name": "Nom de la règle",
        "pattern": "Motif de remplacement",
        "repl": "par",
        "regex": "Regex",
        "regex_help": "Une expression régulière est une forme de syntaxe décrivant un motif de recherche de caractères",
        "casesens": "Casse rigide",
        "casesens_help": "La casse des caractères sera respectée telle quelle.",

        "new_entry": "Nouvelle entrée",
        "edit_entry": "Entrée sélectionnée",

        "add": "Ajouter",
        "delete": "Supprimer",
        "modify": "Modifier",
        "apply": "Appliquer",
        "apply_help": "Appliquer cette règle sur le texte",
        "modif": "modifications",

        "import": "Importer",
        "export": "Exporter",
        "delete_all": "Tout supprimer",
        "save_and_close": "Enregistrer et fermer",

        "name_error": "Pour le nom des règles, utilisez uniquement les lettres, les nombres et les caractères parmi ‹_-#.,;!?›.",
        "name_error_title": "Le nom de la règle n’est pas conforme.",

        "name_and_replace_error": "Ni le nom de la règle, ni ce qui doit être remplacé ne peut être vide. Veuillez remplir les champs requis.",
        "name_and_replace_error_title": "L’un des champs requis est vide",

        "add_name_error": "Une règle porte déjà ce nom. Veuillez modifier son nom.",
        "add_name_error_title": "Nom déjà utilisé",

        "delete_name_error": "Vous avez modifié le nom de la règle. Veuillez resélectionner la règle que vous voulez supprimer, et cliquez sur ‹Supprimer›.",
        "delete_name_error_title": "Nom de la règle à supprimer douteux",

        "modify_name_error": "Une autre règle porte déjà ce nom. Veuillez modifier le nom de la règle.",
        "modify_name_error_title": "Nouveau nom déjà utilisé par une autre règle",

        "import_question": "Voulez-vous que les règles importées écrasent celles existantes si elles possèdent un nom identique ?",
        "import_title": "Importation d’un fichier de règles de transformation",

        "error": "Erreur",
        "file_not_found": "Fichier introuvable : ",
    },
    "en": {
        "title": "Grammalecte · Editor for custom transformations",

        "name": "Rule name",
        "pattern": "Replacement pattern",
        "repl": "by",
        "regex": "Regex",
        "regex_help": "A regular expression is a kind of syntax describing a search pattern of characters",
        "casesens": "Case sensitivity",
        "casesens_help": "Characters case will be treated as written.",

        "new_entry": "New entry",
        "edit_entry": "Selected entry",

        "add": "Add",
        "delete": "Delete",
        "modify": "Modify",
        "apply": "Apply",
        "apply_help": "Apply this rule on the text",
        "modif": "modifications",

        "import": "Import",
        "export": "Export",
        "delete_all": "Delete all",
        "save_and_close": "Save and close",

        "name_error": "For rules names, only use letters, numbers et characters among ‹_-#.,;!?›",
        "name_error_title": "Le nom de la règle n’est pas conforme.",

        "name_and_replace_error": "Neither the rule name, neither what has to be replaced can be empty. Please, fill the required fields.",
        "name_and_replace_error_title": "One of the required fields is empty",

        "add_name_error": "There is already a rule with this name. Please, find another name.",
        "add_name_error_title": "Rule name already used",

        "delete_name_error": "You have modified the name of the rule. Please, select again the rule you want to delete and click on ‹Delete›.",
        "delete_name_error_title": "Dubious rule name to delete",

        "modify_name_error": "This rule name is already used by another rule. Please, modify the rule name.",
        "modify_name_error_title": "New rule name already used by another rule",

        "import_question": "Do you want that imported rules replace existing ones if they have the same name?",
        "import_title": "Importation of a transformation rules file",

        "error": "Error",
        "file_not_found": "File not found: ",
    }
}


