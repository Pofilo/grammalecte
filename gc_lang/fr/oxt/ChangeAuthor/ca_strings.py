# strings for change author


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


