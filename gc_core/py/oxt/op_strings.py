# -*- encoding: UTF-8 -*-

def getUI (sLang):
    if sLang in dStrings:
        return dStrings[sLang]
    return dStrings["fr"]

dStrings = {
    "fr": {
            "title": u"Grammalecte · Options du contrôle grammatical",

            "default": u"Par ~défaut",
            "apply": u"~OK",
            "cancel": u"~Annuler"
          },
    "en": {
            "title": u"Grammalecte · Grammar checking options",

            "default": u"~Default",
            "apply": u"~OK",
            "cancel": u"~Cancel"
          }
}


