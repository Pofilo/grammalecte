# -*- encoding: UTF-8 -*-

def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
            "title": "Grammalecte · Édition du champ “Auteur”",

            "state": "Valeur actuelle du champ “Auteur” :",
            "empty": "[vide]",

            "newvalue": "Entrez la nouvelle valeur :",

            "modify": "Modifier",
            "cancel": "Annuler"
          },
    "en": {
            "title": "Grammalecte · Edition of field “Author”",

            "state": "Current value of field “Author”:",
            "empty": "[empty]",

            "newvalue": "Enter the new value:",

            "modify": "Modify",
            "cancel": "Cancel"
          }
}


