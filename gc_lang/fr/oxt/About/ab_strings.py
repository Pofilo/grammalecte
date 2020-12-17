# strings for About


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
        "windowtitle": "À propos…",
        "title": "Grammalecte",
        "version": "Version : ${version}",
        "license": "Licence : GPL 3",
        "website": "Site web",

        "pythonver": "Python v",
        "console": "Console",

        "message": "Avec le soutien de",
        "sponsor": "La Mouette…",
        "sponsor2": "Algoo…",
        "link": "… et de nombreux contributeurs.",

        "close": "~OK"
    },
    "en": {
        "windowtitle": "About…",
        "title": "Grammalecte",
        "version": "Version: ${version}",
        "license": "License: GPL 3",
        "website": "Web site",

        "pythonver": "Python v",
        "console": "Console",

        "message": "With the support of",
        "sponsor": "La Mouette…",
        "sponsor2": "Algoo…",
        "link": "… and many contributors.",

        "close": "~OK"
    }
}
