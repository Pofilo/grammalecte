# -*- encoding: UTF-8 -*-

def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
            "windowtitle": "À propos…",
            "title": "Grammalecte",
            "version": "Version : ${version}",
            "license": "Licence : GPL 3",
            "website": "Site web",

            "pythonver": "Machine virtuelle Python : v",

            "message": "Avec le soutien de",
            "sponsor": "La Mouette…",
            "link": "… et de nombreux contributeurs.",

            "close": "~OK"
          },
    "en": {
            "windowtitle": "About…",
            "title": "Grammalecte",
            "version": "Version: ${version}",
            "license": "License: GPL 3",
            "website": "Web site",

            "pythonver": "Python virtual machine: v",

            "message": "With the support of",
            "sponsor": "La Mouette…",
            "link": "… and many contributors.",

            "close": "~OK"
          }
}
