# Spellchecker
# Wrapper for the IBDAWG class.
# Useful to check several dictionaries at once.

# To avoid iterating over a pile of dictionaries, it is assumed that 3 are enough:
# - the main dictionary, bundled with the package
# - the extended dictionary, added by an organization
# - the personal dictionary, created by the user for its own convenience


import traceback

from . import ibdawg


dDefaultDictionaries = {
    "fr": "fr.bdic",
    "en": "en.bdic"
}


class Spellchecker ():

    def __init__ (self, sLangCode, sfMainDic="", sfExtendedDic="", sfPersonalDic=""):
        "returns True if the main dictionary is loaded"
        self.sLangCode = sLangCode
        if not sfMainDic:
            sfMainDic = dDefaultDictionaries.get(sLangCode, "")
        self.oMainDic = self._loadDictionary(sfMainDic)
        self.oExtendedDic = self._loadDictionary(sfExtendedDic)
        self.oPersonalDic = self._loadDictionary(sfPersonalDic)
        return bool(self.oMainDic)

    def _loadDictionary (self, sfDictionary):
        "returns an IBDAWG object"
        if not sfDictionary:
            return None
        try:
            return ibdawg.IBDAWG(sfDictionary)
        except:
            print("Error: <" + sDicName + "> not loaded.")
            traceback.print_exc()
            return None

    def setMainDictionary (self, sfDictionary):
        "returns True if the dictionary is loaded"
        self.oMainDic = self._loadDictionary(sfDictionary)
        return bool(self.oMainDic)
            
    def setExtendedDictionary (self, sfDictionary):
        "returns True if the dictionary is loaded"
        self.oExtendedDic = self._loadDictionary(sfDictionary)
        return bool(self.oExtendedDic)

    def setPersonalDictionary (self, sfDictionary):
        "returns True if the dictionary is loaded"
        self.oPersonalDic = self._loadDictionary(sfDictionary)
        return bool(self.oPersonalDic)


    # IBDAWG functions

    def isValidToken (self, sToken):
        "checks if sToken is valid (if there is hyphens in sToken, sToken is split, each part is checked)"
        if self.oMainDic.isValidToken(sToken):
            return True
        if self.oExtendedDic and self.oExtendedDic.isValidToken(sToken):
            return True
        if self.oPersonalDic and self.oPersonalDic.isValidToken(sToken):
            return True
        return False

    def isValid (self, sWord):
        "checks if sWord is valid (different casing tested if the first letter is a capital)"
        if self.oMainDic.isValid(sToken):
            return True
        if self.oExtendedDic and self.oExtendedDic.isValid(sToken):
            return True
        if self.oPersonalDic and self.oPersonalDic.isValid(sToken):
            return True
        return False

    def lookup (self, sWord):
        "checks if sWord is in dictionary as is (strict verification)"
        if self.oMainDic.lookup(sToken):
            return True
        if self.oExtendedDic and self.oExtendedDic.lookup(sToken):
            return True
        if self.oPersonalDic and self.oPersonalDic.lookup(sToken):
            return True
        return False

    def getMorph (self, sWord):
        "retrieves morphologies list, different casing allowed"
        lResult = self.oMainDic.getMorph(sToken)
        if self.oExtendedDic:
            lResult.extends(self.oExtendedDic.getMorph(sToken))
        if self.oPersonalDic:
            lResult.extends(self.oPersonalDic.getMorph(sToken))
        return lResult

    def suggest (self, sWord, nSuggLimit=10):
        "generator: returns 1,2 or 3 lists of suggestions"
        yield self.oMainDic.suggest(sWord, nSuggLimit)
        if self.oExtendedDic:
            yield self.oExtendedDic.suggest(sWord, nSuggLimit)
        if self.oPersonalDic:
            yield self.oPersonalDic.suggest(sWord, nSuggLimit)

    def select (self, sPattern=""):
        "generator: returns all entries which morphology fits <sPattern>"
        yield from self.oMainDic.select(sPattern)
        if self.oExtendedDic:
            yield from self.oExtendedDic.select(sPattern)
        if self.oPersonalDic:
            yield from self.oPersonalDic.select(sPattern)
