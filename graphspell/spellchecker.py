# Spellchecker
# Wrapper for the IBDAWG class.
# Useful to check several dictionaries at once.

from . import ibdawg


dDictionaries = {
    "fr": "French.bdic",
    "en": "English.bdic"
}


class Spellchecker ():

    def __init__ (self, sLangCode):
        self.sLangCode = sLangCode
        self.oMainDic = None
        if sLangCode in dDictionaries:
            self.oMainDic = ibdawg.IBDAWG(dDictionaries[sLangCode])
        self.lOtherDic = []
        return bool(self.oMainDic)


    def setMainDictionary (self, sDicName):
        try:
            self.oMainDic = ibdawg.IBDAWG(sDicName)
            return True
        except:
            print("Error: <" + sDicName + "> not set as main dictionary.")
            return False

    def addDictionary (self, sDicName):
        try:
            self.lOtherDic.append(ibdawg.IBDAWG(sDicName))
            return True
        except:
            print("Error: <" + sDicName + "> not added to the list.")
            return False

    # Return codes:
    #   0: invalid
    #   1: correct in main dictionary
    #   2+: correct in foreign dictionaries


    # check in the main dictionary only

    def isValidToken (self, sToken):
        "(in main dictionary) checks if sToken is valid (if there is hyphens in sToken, sToken is split, each part is checked)"
        if self.oMainDic.isValidToken(sToken):
            return 1
        return 0

    def isValid (self, sWord):
        "(in main dictionary) checks if sWord is valid (different casing tested if the first letter is a capital)"
        if self.oMainDic.isValid(sWord):
            return 1
        return 0

    def lookup (self, sWord):
        "(in main dictionary) checks if sWord is in dictionary as is (strict verification)"
        if self.oMainDic.lookup(sWord):
            return 1
        return 0


    # check in all dictionaries

    def isValidTokenAll (self, sToken):
        "(in all dictionaries) checks if sToken is valid (if there is hyphens in sToken, sToken is split, each part is checked)"
        if self.oMainDic.isValidToken(sToken):
            return 1
        for i, oDic in enumerate(self.lOtherDic, 2):
            if oDic.isValidToken(sToken):
                return i
        return 0

    def isValidAll (self, sWord):
        "(in all dictionaries) checks if sWord is valid (different casing tested if the first letter is a capital)"
        if self.oMainDic.isValid(sToken):
            return 1
        for i, oDic in enumerate(self.lOtherDic, 2):
            if oDic.isValid(sToken):
                return i
        return 0

    def lookupAll (self, sWord):
        "(in all dictionaries) checks if sWord is in dictionary as is (strict verification)"
        if self.oMainDic.lookup(sToken):
            return 1
        for i, oDic in enumerate(self.lOtherDic, 2):
            if oDic.lookup(sToken):
                return i
        return 0


    # check in dictionaries up to level n

    def isValidTokenLevel (self, sToken, nLevel):
        "(in dictionaries up to level n) checks if sToken is valid (if there is hyphens in sToken, sToken is split, each part is checked)"
        if self.oMainDic.isValidToken(sToken):
            return 1
        if nLevel >= 2:
            for i, oDic in enumerate(self.lOtherDic, 2):
                if oDic.isValidToken(sToken):
                    return i
                if i == nLevel:
                    break
        return 0

    def isValidLevel (self, sWord, nLevel):
        "(in dictionaries up to level n) checks if sWord is valid (different casing tested if the first letter is a capital)"
        if self.oMainDic.isValid(sToken):
            return 1
        if nLevel >= 2:
            for i, oDic in enumerate(self.lOtherDic, 2):
                if oDic.isValid(sToken):
                    return i
                if i == nLevel:
                    break
        return 0

    def lookupLevel (self, sWord, nLevel):
        "(in dictionaries up to level n) checks if sWord is in dictionary as is (strict verification)"
        if self.oMainDic.lookup(sToken):
            return 1
        if nLevel >= 2:
            for i, oDic in enumerate(self.lOtherDic, 2):
                if oDic.lookup(sToken):
                    return i
                if i == nLevel:
                    break
        return 0
