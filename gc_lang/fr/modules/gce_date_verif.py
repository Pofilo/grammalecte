#### GRAMMAR CHECKING ENGINE PLUGIN

#### Check date validity

import datetime


_lDay = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
_dMonth = { "janvier":1, "février":2, "mars":3, "avril":4, "mai":5, "juin":6, "juillet":7, "août":8, "aout":8, "septembre":9, "octobre":10, "novembre":11, "décembre":12 }

# Dans Python, datetime.weekday() envoie le résultat comme si nous étions dans un calendrier grégorien universal.
# https://fr.wikipedia.org/wiki/Passage_du_calendrier_julien_au_calendrier_gr%C3%A9gorien
# Selon Grégoire, le jeudi 4 octobre 1582 est immédiatement suivi par le vendredi 15 octobre.
# En France, la bascule eut lieu le 9 décembre 1582 qui fut suivi par le 20 décembre 1582.
# C’est la date retenue pour la bascule dans Grammalecte, mais le calendrier grégorien fut adopté dans le monde diversement.
# Il fallut des siècles pour qu’il soit adopté par l’Occident et une grande partie du reste du monde.
_dGregorianToJulian = {
    "lundi":    "jeudi",
    "mardi":    "vendredi",
    "mercredi": "samedi",
    "jeudi":    "dimanche",
    "vendredi": "lundi",
    "samedi":   "mardi",
    "dimanche": "mercredi"
}


def checkDate (sDay, sMonth, sYear):
    "return True if the date is valid"
    if not sMonth.isdigit():
        sMonth = _dMonth.get(sMonth.lower(), "13")
    try:
        return datetime.date(int(sYear), int(sMonth), int(sDay))
    except ValueError:
        return False
    except:
        return True


def checkDay (sWeekday, sDay, sMonth, sYear):
    "return True if sWeekday is valid according to the given date"
    xDate = checkDate(sDay, sMonth, sYear)
    if xDate and _getDay(xDate) != sWeekday.lower():
        return False
    # if the date isn’t valid, any day is valid.
    return True


def getDay (sDay, sMonth, sYear):
    "return the day of the date (in Gregorian calendar after 1582-12-20, in Julian calendar before 1582-12-09)"
    xDate = checkDate(sDay, sMonth, sYear)
    if xDate:
        return _getDay(xDate)
    return ""


def _getDay (xDate):
    "return the day of the date (in Gregorian calendar after 1582-12-20, in Julian calendar before 1582-12-09)"
    if xDate.year > 1582:
        # Calendrier grégorien
        return _lDay[xDate.weekday()]
    if xDate.year < 1582:
        # Calendrier julien
        sGregorianDay = _lDay[xDate.weekday()]
        return _dGregorianToJulian.get(sGregorianDay, "Erreur: jour inconnu")
    # 1582
    if xDate.month < 12  or xDate.day <= 9:
        # Calendrier julien
        sGregorianDay = _lDay[xDate.weekday()]
        return _dGregorianToJulian.get(sGregorianDay, "Erreur: jour inconnu")
    elif xDate.day >= 20:
        # Calendrier grégorien
        return _lDay[xDate.weekday()]
    else:
        # 10 - 19 décembre 1582: jours inexistants en France.
        return ""
