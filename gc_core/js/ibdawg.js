//// IBDAWG

"use strict";


if (typeof(require) !== 'undefined') {
    var str_transform = require("resource://grammalecte/str_transform.js");
    var helpers = require("resource://grammalecte/helpers.js");
}


// String
// Don’t remove. Necessary in TB.
${string}



class IBDAWG {
    // INDEXABLE BINARY DIRECT ACYCLIC WORD GRAPH

    constructor (sDicName) {
        try {
            let sURL = (typeof(browser) !== 'undefined') ? browser.extension.getURL("grammalecte/_dictionaries/"+sDicName) : "resource://grammalecte/_dictionaries/"+sDicName;
            const dict = JSON.parse(helpers.loadFile(sURL));
            Object.assign(this, dict);
        }
        catch (e) {
            throw Error("# Error. File not found or not loadable.\n" + e.message + "\n");
        }
        /*
            Properties:
            sName, nVersion, sHeader, lArcVal, nArcVal, byDic, sLang, nChar, nBytesArc, nBytesNodeAddress,
            nEntries, nNode, nArc, nAff, cStemming, nTag, dChar, _arcMask, _finalNodeMask, _lastArcMask, _addrBitMask, nBytesOffset,
        */
        if (!this.sHeader.startsWith("/pyfsa/")) {
            throw TypeError("# Error. Not a pyfsa binary dictionary. Header: " + this.sHeader);
        }
        if (!(this.nVersion == "1" || this.nVersion == "2" || this.nVersion == "3")) {
            throw RangeError("# Error. Unknown dictionary version: " + this.nVersion);
        }

        this.dChar = helpers.objectToMap(this.dChar);
        //this.byDic = new Uint8Array(this.byDic);  // not quicker, even slower

        if (this.cStemming == "S") {
            this.funcStemming = str_transform.getStemFromSuffixCode;
        } else if (this.cStemming == "A") {
            this.funcStemming = str_transform.getStemFromAffixCode;
        } else {
            this.funcStemming = str_transform.noStemming;
        }

        // Configuring DAWG functions according to nVersion
        switch (this.nVersion) {
            case 1:
                this.morph = this._morph1;
                this.stem = this._stem1;
                this._lookupArcNode = this._lookupArcNode1;
                this._writeNodes = this._writeNodes1;
                break;
            case 2:
                this.morph = this._morph2;
                this.stem = this._stem2;
                this._lookupArcNode = this._lookupArcNode2;
                this._writeNodes = this._writeNodes2;
                break;
            case 3:
                this.morph = this._morph3;
                this.stem = this._stem3;
                this._lookupArcNode = this._lookupArcNode3;
                this._writeNodes = this._writeNodes3;
                break;
            default:
                throw ValueError("# Error: unknown code: " + this.nVersion);
        }
        //console.log(this.getInfo());
        this.bOptNumSigle = true;
        this.bOptNumAtLast = false;
    };

    getInfo () {
        return  `  Language: ${this.sLang}      Version: ${this.nVersion}      Stemming: ${this.cStemming}FX\n` +
                `  Arcs values:  ${this.nArcVal} = ${this.nChar} characters,  ${this.nAff} affixes,  ${this.nTag} tags\n` +
                `  Dictionary: ${this.nEntries} entries,    ${this.nNode} nodes,   ${this.nArc} arcs\n` +
                `  Address size: ${this.nBytesNodeAddress} bytes,  Arc size: ${this.nBytesArc} bytes\n`;
    };

    isValidToken (sToken) {
        // checks if sToken is valid (if there is hyphens in sToken, sToken is split, each part is checked)
        if (this.isValid(sToken)) {
            return true;
        }
        if (sToken.includes("-")) {
            if (sToken.gl_count("-") > 4) {
                return true;
            }
            return sToken.split("-").every(sWord  =>  this.isValid(sWord)); 
        }
        return false;
    };

    isValid (sWord) {
        // checks if sWord is valid (different casing tested if the first letter is a capital)
        if (!sWord) {
            return null;
        }
        if (sWord.includes("’")) { // ugly hack
            sWord = sWord.replace("’", "'");
        }
        if (this.lookup(sWord)) {
            return true;
        }
        if (sWord.charAt(0).gl_isUpperCase()) {
            if (sWord.length > 1) {
                if (sWord.gl_isTitle()) {
                    return !!this.lookup(sWord.toLowerCase());
                }
                if (sWord.gl_isUpperCase()) {
                    if (this.bOptNumSigle) {
                        return true;
                    }
                    return !!(this.lookup(sWord.toLowerCase()) || this.lookup(sWord.gl_toCapitalize()));
                }
                return !!this.lookup(sWord.slice(0, 1).toLowerCase() + sWord.slice(1));
            } else {
                return !!this.lookup(sWord.toLowerCase());
            }
        }
        return false;
    };

    _convBytesToInteger (aBytes) {
        // Byte order = Big Endian (bigger first)
        let nVal = 0;
        let nWeight = (aBytes.length - 1) * 8;
        for (let n of aBytes) {
            nVal += n << nWeight;
            nWeight = nWeight - 8;
        }
        return nVal;
    };

    lookup (sWord) {
        // returns true if sWord in dictionary (strict verification)
        let iAddr = 0;
        for (let c of sWord) {
            if (!this.dChar.has(c)) {
                return false;
            }
            iAddr = this._lookupArcNode(this.dChar.get(c), iAddr);
            if (iAddr === null) {
                return false;
            }
        }
        return Boolean(this._convBytesToInteger(this.byDic.slice(iAddr, iAddr+this.nBytesArc)) & this._finalNodeMask);
    };

    getMorph (sWord) {
        // retrieves morphologies list, different casing allowed
        let l = this.morph(sWord);
        if (sWord[0].gl_isUpperCase()) {
            l = l.concat(this.morph(sWord.toLowerCase()));
            if (sWord.gl_isUpperCase() && sWord.length > 1) {
                l = l.concat(this.morph(sWord.gl_toCapitalize()));
            }
        }
        return l;
    };

    // morph (sWord) {
    //     is defined in constructor
    // };
    
    // VERSION 1
    _morph1 (sWord) {
        // returns morphologies of sWord
        let iAddr = 0;
        for (let c of sWord) {
            if (!this.dChar.has(c)) {
                return [];
            }
            iAddr = this._lookupArcNode(this.dChar.get(c), iAddr);
            if (iAddr === null) {
                return [];
            }
        }
        if (this._convBytesToInteger(this.byDic.slice(iAddr, iAddr+this.nBytesArc)) & this._finalNodeMask) {
            let l = [];
            let nRawArc = 0;
            while (!(nRawArc & this._lastArcMask)) {
                var iEndArcAddr = iAddr + this.nBytesArc;
                nRawArc = this._convBytesToInteger(this.byDic.slice(iAddr, iEndArcAddr));
                var nArc = nRawArc & this._arcMask;
                if (nArc >= this.nChar) {
                    // This value is not a char, this is a stemming code 
                    var sStem = ">" + this.funcStemming(sWord, this.lArcVal[nArc]);
                    // Now , we go to the next node and retrieve all following arcs values, all of them are tags
                    var iAddr2 = this._convBytesToInteger(this.byDic.slice(iEndArcAddr, iEndArcAddr+this.nBytesNodeAddress));
                    var nRawArc2 = 0;
                    while (!(nRawArc2 & this._lastArcMask)) {
                        var iEndArcAddr2 = iAddr2 + this.nBytesArc;
                        nRawArc2 = this._convBytesToInteger(this.byDic.slice(iAddr2, iEndArcAddr2));
                        l.push(sStem + " " + this.lArcVal[nRawArc2 & this._arcMask]);
                        iAddr2 = iEndArcAddr2+this.nBytesNodeAddress;
                    }
                }
                iAddr = iEndArcAddr + this.nBytesNodeAddress;
            }
            return l;
        }
        return [];
    };

    _stem1 (sWord) {
        // returns stems list of sWord
        let iAddr = 0;
        for (let c of sWord) {
            if (!this.dChar.has(c)) {
                return [];
            }
            iAddr = this._lookupArcNode(this.dChar.get(c), iAddr);
            if (iAddr === null) {
                return [];
            }
        }
        if (this._convBytesToInteger(this.byDic.slice(iAddr, iAddr+this.nBytesArc)) & this._finalNodeMask) {
            let l = [];
            let nRawArc = 0;
            while (!(nRawArc & this._lastArcMask)) {
                var iEndArcAddr = iAddr + this.nBytesArc;
                nRawArc = this._convBytesToInteger(this.byDic.slice(iAddr, iEndArcAddr));
                var nArc = nRawArc & this._arcMask;
                if (nArc >= this.nChar) {
                    // This value is not a char, this is a stemming code 
                    l.push(this.funcStemming(sWord, this.lArcVal[nArc]));
                }
                iAddr = iEndArcAddr + this.nBytesNodeAddress;
            }
            return l;
        }
        return [];
    };

    _lookupArcNode1 (nVal, iAddr) {
        // looks if nVal is an arc at the node at iAddr, if yes, returns address of next node else None
        while (true) {
            let iEndArcAddr = iAddr+this.nBytesArc;
            let nRawArc = this._convBytesToInteger(this.byDic.slice(iAddr, iEndArcAddr));
            if (nVal == (nRawArc & this._arcMask)) {
                // the value we are looking for 
                // we return the address of the next node
                return this._convBytesToInteger(this.byDic.slice(iEndArcAddr, iEndArcAddr+this.nBytesNodeAddress));
            }
            else {
                // value not found
                if (nRawArc & this._lastArcMask) {
                    return null;
                }
                iAddr = iEndArcAddr + this.nBytesNodeAddress;
            }
        }
    };

    // VERSION 2
    _morph2 (sWord) {
        // to do
    };

    _stem2 (sWord) {
        // to do
    };

    _lookupArcNode2 (nVal, iAddr) {
        // to do
    };


    // VERSION 3
    _morph3 (sWord) {
        // to do
    };

    _stem3 (sWord) {
        // to do
    };

    _lookupArcNode3 (nVal, iAddr) {
        // to do
    };
}


if (typeof(exports) !== 'undefined') {
    exports.IBDAWG = IBDAWG;
}
