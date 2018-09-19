#### GRAMMAR CHECKING ENGINE PLUGIN

#### Check date validity

_lDay = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
_dMonth = { "janvier":1, "février":2, "mars":3, "avril":4, "mai":5, "juin":6, "juillet":7, "août":8, "aout":8, "septembre":9, "octobre":10, "novembre":11, "décembre":12 }

import datetime


def checkDate (sDay, sMonth, sYear):
    "to use if <sMonth> is a number"
    try:
        return datetime.date(int(sYear), int(sMonth), int(sDay))
    except ValueError:
        return False
    except:
        return True


def checkDateWithString (sDay, sMonth, sYear):
    "to use if <sMonth> is a noun"
    try:
        return datetime.date(int(sYear), _dMonth.get(sMonth.lower(), ""), int(sDay))
    except ValueError:
        return False
    except:
        return True


def checkDay (sWeekday, sDay, sMonth, sYear):
    "to use if <sMonth> is a number"
    oDate = checkDate(sDay, sMonth, sYear)
    if oDate and _lDay[oDate.weekday()] != sWeekday.lower():
        return False
    return True


def checkDayWithString (sWeekday, sDay, sMonth, sYear):
    "to use if <sMonth> is a noun"
    oDate = checkDate(sDay, _dMonth.get(sMonth, ""), sYear)
    if oDate and _lDay[oDate.weekday()] != sWeekday.lower():
        return False
    return True


def getDay (sDay, sMonth, sYear):
    "to use if <sMonth> is a number"
    return _lDay[datetime.date(int(sYear), int(sMonth), int(sDay)).weekday()]


def getDayWithString (sDay, sMonth, sYear):
    "to use if <sMonth> is a noun"
    return _lDay[datetime.date(int(sYear), _dMonth.get(sMonth.lower(), ""), int(sDay)).weekday()]
