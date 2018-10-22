// GRAMMAR CHECKING ENGINE PLUGIN

// Check date validity
// WARNING: when creating a Date, month must be between 0 and 11

/* jshint esversion:6 */
/* jslint esversion:6 */


const _lDay = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];
const _dMonth = new Map ([
    ["janvier", 1], ["février", 2], ["mars", 3], ["avril", 4], ["mai", 5], ["juin", 6], ["juillet", 7],
    ["août", 8], ["aout", 8], ["septembre", 9], ["octobre", 10], ["novembre", 11], ["décembre", 12]
]);
const _dDaysInMonth = new Map ([
    [1, 31], [2, 28], [3, 31], [4, 30], [5, 31], [6, 30], [7, 31],
    [8, 31], [8, 31], [9, 30], [10, 31], [11, 30], [12, 31]
]);

// Dans Python, datetime.weekday() envoie le résultat comme si nous étions dans un calendrier grégorien universal.
// https://fr.wikipedia.org/wiki/Passage_du_calendrier_julien_au_calendrier_gr%C3%A9gorien
// Selon Grégoire, le jeudi 4 octobre 1582 est immédiatement suivi par le vendredi 15 octobre.
// En France, la bascule eut lieu le 9 décembre 1582 qui fut suivi par le 20 décembre 1582.
// C’est la date retenue pour la bascule dans Grammalecte, mais le calendrier grégorien fut adopté dans le monde diversement.
// Il fallut des siècles pour qu’il soit adopté par l’Occident et une grande partie du reste du monde.
const _dGregorianToJulian = new Map ([
    ["lundi",    "jeudi"],
    ["mardi",    "vendredi"],
    ["mercredi", "samedi"],
    ["jeudi",    "dimanche"],
    ["vendredi", "lundi"],
    ["samedi",   "mardi"],
    ["dimanche", "mercredi"]
]);

function _checkDate (nDay, nMonth, nYear) {
    // returns true or false
    if (nMonth > 12 || nMonth < 1 || nDay > 31 || nDay < 1) {
        return false;
    }
    if (nDay <= _dDaysInMonth.get(nMonth)) {
        return true;
    }
    if (nDay === 29) {
        // leap years, http://jsperf.com/ily/15
        return !(nYear & 3 || !(nYear % 25) && nYear & 15);
    }
    return false;
}

function checkDate (sDay, sMonth, sYear) {
    // return True if the date is valid
    if (!sMonth.gl_isDigit()) {
        sMonth = _dMonth.get(sMonth.toLowerCase());
    }
    if (_checkDate(parseInt(sDay, 10), parseInt(sMonth, 10), parseInt(sYear, 10))) {
        return new Date(parseInt(sYear, 10), parseInt(sMonth, 10)-1, parseInt(sDay, 10));
    }
    return false;
}

function checkDay (sWeekday, sDay, sMonth, sYear) {
    // return True if sWeekday is valid according to the given date
    let xDate = checkDate(sDay, sMonth, sYear);
    if (xDate  &&  _getDay(xDate) != sWeekday.toLowerCase()) {
        return false;
    }
    // if the date isn’t valid, any day is valid.
    return true;
}

function getDay (sDay, sMonth, sYear) {
    // return the day of the date (in Gregorian calendar after 1582-12-20, in Julian calendar before 1582-12-09)
    let xDate = checkDate(sDay, sMonth, sYear);
    if (xDate) {
        return _getDay(xDate);
    }
    return ""
}

function _getDay (xDate) {
    // return the day of the date (in Gregorian calendar after 1582-12-20, in Julian calendar before 1582-12-09)
    if (xDate.getFullYear() > 1582) {
        // Calendrier grégorien
        return _lDay[xDate.getDay()];
    }
    if (xDate.getFullYear() < 1582) {
        // Calendrier julien
        let sGregorianDay = _lDay[xDate.getDay()];
        return _dGregorianToJulian.get(sGregorianDay, "Erreur: jour inconnu")
    }
    // 1582
    if ((xDate.getMonth()+1) < 12  || xDate.getDate() <= 9) {
        // Calendrier julien
        let sGregorianDay = _lDay[xDate.getDay()];
        return _dGregorianToJulian.get(sGregorianDay, "Erreur: jour inconnu");
    }
    else if (xDate.getDate() >= 20) {
        // Calendrier grégorien
        return _lDay[xDate.getDay()];
    }
    else {
        // 10 - 19 décembre 1582: jours inexistants en France.
        return "";
    }
}
