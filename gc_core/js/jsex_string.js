
// String

if (String.prototype.__grammalecte__ === undefined) {
    String.prototype._count = function (sSearch, bOverlapping) {
        // http://jsperf.com/string-ocurrence-split-vs-match/8
        if (sSearch.length <= 0) {
            return this.length + 1;
        }
        let nOccur = 0;
        let iPos = 0;
        let nStep = (bOverlapping) ? 1 : sSearch.length;
        while ((iPos = this.indexOf(sSearch, iPos)) >= 0) {
            nOccur++;
            iPos += nStep;
        }
        return nOccur;
    }
    String.prototype._isDigit = function () {
        return (this.search(/^[0-9⁰¹²³⁴⁵⁶⁷⁸⁹]+$/) !== -1);
    }
    String.prototype._isLowerCase = function () {
        return (this.search(/^[a-zà-öø-ÿ0-9-]+$/) !== -1);
    }
    String.prototype._isUpperCase = function () {
        return (this.search(/^[A-ZÀ-ÖØ-ßŒ0-9-]+$/) !== -1);
    }
    String.prototype._isTitle = function () {
        return (this.search(/^[A-ZÀ-ÖØ-ßŒ][a-zà-öø-ÿ'’-]+$/) !== -1);
    }
    String.prototype._toCapitalize = function () {
        return this.slice(0,1).toUpperCase() + this.slice(1).toLowerCase();
    }
    String.prototype._expand = function (oMatch) {
        let sNew = this;
        for (let i = 0; i < oMatch.length ; i++) {
            let z = new RegExp("\\\\"+parseInt(i), "g");
            sNew = sNew.replace(z, oMatch[i]);
        }
        return sNew;
    }
    String.prototype._trimRight = function (sChars) {
        let z = new RegExp("["+sChars+"]+$");
        return this.replace(z, "");
    }
    String.prototype._trimLeft = function (sChars) {
        let z = new RegExp("^["+sChars+"]+");
        return this.replace(z, "");
    }
    String.prototype._trim = function (sChars) {
        let z1 = new RegExp("^["+sChars+"]+");
        let z2 = new RegExp("["+sChars+"]+$");
        return this.replace(z1, "").replace(z2, "");
    }

    String.prototype.__grammalecte__ = true;
}
