// JavaScript

// FSA DICTIONARY BUILDER
//
// by Olivier R.
// License: MPL 2
//
// This tool encodes lexicon into an indexable binary dictionary 
// Input files MUST be encoded in UTF-8.

"use strict";


if (typeof(require) !== 'undefined') {
    var str_transform = require("resource://grammalecte/graphspell/str_transform.js");
}


${map}


class DAWG {
    /*  DIRECT ACYCLIC WORD GRAPH
        This code is inspired from Steve Hanov’s DAWG, 2011. (http://stevehanov.ca/blog/index.php?id=115)
        We store suffix/affix codes and tags within the graph after the “real” word.
        A word is a list of numbers [ c1, c2, c3 . . . cN, iAffix, iTags]
        Each arc is an index in this.lArcVal, where are stored characters, suffix/affix codes for stemming and tags.
        Important: As usual, the last node (after ‘iTags’) is tagged final, AND the node after ‘cN’ is ALSO tagged final.
    */

    constructor (lEntrySrc, sLangName, cStemming, xProgressBarNode=null) {
        console.log("===== Direct Acyclic Word Graph - Minimal Acyclic Finite State Automaton =====");
        let funcStemmingGen = null;
        switch (cStemming.toUpperCase()) {
            case "A":
                funcStemmingGen = str_transform.defineAffixCode; break;
            case "S":
                funcStemmingGen = str_transform.defineSuffixCode; break;
            case "N":
                funcStemmingGen = str_transform.noStemming; break;
            default:
                throw "Error. Unknown stemming code: " + cStemming;
        }
        
        let lEntry = [];
        let lChar = [''],  dChar = new Map(),  nChar = 1,  dCharOccur = new Map();
        let lAff  = [],    dAff  = new Map(),  nAff  = 0,  dAffOccur = new Map();
        let lTag  = [],    dTag  = new Map(),  nTag  = 0,  dTagOccur = new Map();
        let nErr = 0;
        
        // read lexicon
        for (let [sFlex, sStem, sTag] of lEntrySrc) {
            addWordToCharDict(sFlex);
            // chars
            for (let c of sFlex) {
                if (!dChar.get(c)) {
                    dChar.set(c, nChar);
                    lChar.push(c);
                    nChar += 1;
                }
                dCharOccur.set(c, dCharOccur.gl_get(c, 0) + 1);
            }
            // affixes to find stem from flexion
            let sAff = funcStemmingGen(sFlex, sStem);
            if (!dAff.get(sAff)) {
                dAff.set(sAff, nAff);
                lAff.push(sAff);
                nAff += 1;
            }
            dAffOccur.set(sAff, dCharOccur.gl_get(sAff, 0) + 1);
            // tags
            if (!dTag.get(sTag)) {
                dTag.set(sTag, nTag);
                lTag.push(sTag);
                nTag += 1;
            }
            dTagOccur.set(sTag, dTagOccur.gl_get(sTag, 0) + 1);
            lEntry.push([sFlex, dAff.get(sAff), dTag.get(sTag)]);
        }
        if (lEntry.length == 0) {
            throw "Error. Empty lexicon";
        }
        
        // Preparing DAWG
        console.log(" > Preparing list of words");
        let lVal = lChar.concat(lAff).concat(lTag);
        let lWord = [];
        for (let [sFlex, iAff, iTag] of lEntry) {
            let lTemp = [];
            for (let c of sFlex) {
                lTemp.push(dChar.get(c));
            }
            lTemp.push(iAff+nChar);
            lTemp.push(iTag+nChar+nAff)
            lWord.push(lTemp);
        }
        lEntry.length = 0; // clear the array
        
        // Dictionary of arc values occurrency, to sort arcs of each node
        let lKeyVal = [];
        for (let c of dChar.keys()) { lKeyVal.push([dChar.get(c), dCharOccur.get(c)]); }
        for (let sAff of dAff.keys()) { lKeyVal.push([dAff.get(sAff)+nChar, dAffOccur.get(sAff)]); }
        for (let sTag of dTag.keys()) { lKeyVal.push([dTag.get(sTag)+nChar+nAff, dTagOccur.get(sTag)]); }
        let dValOccur = new Map(lKeyVal);
        lKeyVal.length = 0; // clear the array

        this.sLang = sLangName;
        this.nEntry = lWord.length;
        this.aPreviousEntry = [];
        oNodeCounter.reset();
        this.oRoot = new DawgNode();
        this.lUncheckedNodes = [];          // list of nodes that have not been checked for duplication.
        this.dMinimizedNodes = new Map();   // list of unique nodes that have been checked for duplication.
        this.nNode = 0;
        this.nArc = 0;
        this.dChar = dChar;
        this.nChar = dChar.size;
        this.nAff = nAff;
        this.lArcVal = lVal;
        this.nArcVal = lVal.length;
        this.nTag = this.nArcVal - this.nChar - nAff;
        this.cStemming = cStemming;
        if (cStemming == "A") {
            this.funcStemming = str_transform.changeWordWithAffixCode;
        } else if (cStemming == "S") {
            this.funcStemming = str_transform.changeWordWithSuffixCode;
        } else {
            this.funcStemming = str_transform.noStemming;
        }
        
        // build
        lWord.sort();
        if (xProgressBarNode) {
            xProgressBarNode.value = 0;
            xProgressBarNode.max = lWord.length;
        }
        let i = 1;
        for (let aEntry of lWord) {
            this.insert(aEntry);
            if (xProgressBarNode) {
                xProgressBarNode.value = i;
                i += 1;
            }
        }
        this.finish();
        this.countNodes();
        this.countArcs();
        this.sortNodeArcs(dValOccur);
        this.displayInfo();
        //this.writeInfo();
        //this.oRoot.display(0, this.lArcVal, true);
    }

    // BUILD DAWG
    insert (aEntry) {
        if (aEntry < this.aPreviousEntry) {
            throw "Error: Words must be inserted in alphabetical order.";
        }
        
        // find common prefix between word and previous word
        let nCommonPrefix = 0;
        for (let i = 0;  i < Math.min(aEntry.length, this.aPreviousEntry.length);  i++) {
            if (aEntry[i] != this.aPreviousEntry[i]) {
                break;
            }
            nCommonPrefix += 1;
        }
        // Check the lUncheckedNodes for redundant nodes, proceeding from last
        // one down to the common prefix size. Then truncate the list at that point.
        this._minimize(nCommonPrefix);

        // add the suffix, starting from the correct node mid-way through the graph
        let oNode = (this.lUncheckedNodes.length == 0) ? this.oRoot : this.lUncheckedNodes[this.lUncheckedNodes.length-1][2];
        let iChar = nCommonPrefix;
        for (let c of aEntry.slice(nCommonPrefix)) {
            let oNextNode = new DawgNode();
            oNode.arcs.set(c, oNextNode);
            this.lUncheckedNodes.push([oNode, c, oNextNode]);
            if (iChar == (aEntry.length - 2)) {
                oNode.final = true;
            }
            iChar += 1;
            oNode = oNextNode;
        }
        oNode.final = true;
        this.aPreviousEntry = aEntry;
    }

    finish () {
        // minimize unchecked nodes
        this._minimize(0);
    }

    _minimize (nDownTo) {
        // proceed from the leaf up to a certain point
        for (let i = this.lUncheckedNodes.length-1;  i > nDownTo-1;  i--) {
            let [oNode, char, oChildNode] = this.lUncheckedNodes[i];
            if (this.dMinimizedNodes.has(oChildNode.__hash__())) {
                // replace the child with the previously encountered one
                oNode.arcs.set(char, this.dMinimizedNodes.get(oChildNode.__hash__()));
            } else {
                // add the state to the minimized nodes.
                this.dMinimizedNodes.set(oChildNode.__hash__(), oChildNode);
            }
            this.lUncheckedNodes.pop();
        }
    }

    countNodes () {
        this.nNode = this.dMinimizedNodes.size;
    }

    countArcs () {
        this.nArc = 0;
        for (let oNode of this.dMinimizedNodes.values()) {
            this.nArc += oNode.arcs.size;
        }
    }
    
    sortNodeArcs (dValOccur) {
        console.log(" > Sort node arcs");
        this.oRoot.sortArcs(dValOccur);
        for (let oNode of this.dMinimizedNodes.values()) {
            oNode.sortArcs(dValOccur);
        }
    }

    lookup (sWord) {
        let oNode = this.oRoot;
        for (let c of sWord) {
            if (!oNode.arcs.has(this.dChar.gl_get(c, ''))) {
                return false;
            }
            oNode = oNode.arcs.get(this.dChar.get(c));
        }
        return oNode.final;
    }

    morph (sWord) {
        let oNode = this.oRoot;
        for (let c of sWord) {
            if (!oNode.arcs.has(this.dChar.get(c, ''))) {
                return '';
            }
            oNode = oNode.arcs.get(this.dChar.get(c));
        }
        if (oNode.final) {
            let s = "* ";
            for (let arc of oNode.arcs.keys()) {
                if (arc >= this.nChar) {
                    s += " [" + this.funcStemming(sWord, this.lArcVal[arc]);
                    let oNode2 = oNode.arcs.get(arc);
                    for (let arc2 of oNode2.arcs.keys()) {
                        s += " / " + this.lArcVal[arc2];
                    }
                    s += "]";
                }
            }
            return s;
        }
        return '';
    }

    displayInfo () {
        console.log("Entries: " + this.nEntry);
        console.log("Characters: " + this.nChar);
        console.log("Affixes: " + this.nAff);
        console.log("Tags: " + this.nTag);
        console.log("Arc values: " + this.nArcVal);
        console.log("Nodes: " + this.nNode);
        console.log("Arcs: " + this.nArc);
        console.log("Stemming: " + this.cStemming + "FX");
    }

    getArcStats () {
        let d = new Map();
        for (let oNode of this.dMinimizedNodes.values()) {
            let n = oNode.arcs.size;
            d.set(n, d.gl_get(n, 0) + 1);
        }
        let s = " * Nodes:\n";
        for (let [nKey, nVal] of d.entries()) {
            s = s + " " + nVal + " nodes have " + nKey + " arcs\n";
        }
        return s;
    }

    writeInfo () {
        console.log(this.getArcStats());
        console.log("\n * Values:\n");
        let i = 0;
        for (let s of this.lArcVal) {
            console.log(i + ": " + s);
            i++;
        }
    }

    // BINARY CONVERSION
    createBinary (nMethod) {
        console.log("Write DAWG as an indexable binary dictionary [method: "+nMethod+"]");
        if (nMethod == 1) {
            this.nBytesArc = Math.floor( (this.nArcVal.toString(2).length + 2) / 8 ) + 1;     // We add 2 bits. See DawgNode.convToBytes1()
            this._calcNumBytesNodeAddress()
            this._calcNodesAddress1()
        } else {
            console.log("Error: unknown compression method");
        }
        console.log("Arc values (chars, affixes and tags): " + this.nArcVal);
        console.log("Arc size: "+this.nBytesArc+" bytes, Address size: "+this.nBytesNodeAddress+" bytes");
        console.log("-> " + this.nBytesArc+this.nBytesNodeAddress + " * " + this.nArc + " = " + (this.nBytesArc+this.nBytesNodeAddress)*this.nArc + " bytes");
        return this._createJSON(nMethod);
    }

    _calcNumBytesNodeAddress () {
        // how many bytes needed to store all nodes/arcs in the binary dictionary
        this.nBytesNodeAddress = 1;
        while (((this.nBytesArc + this.nBytesNodeAddress) * this.nArc) > (2 ** (this.nBytesNodeAddress * 8))) {
            this.nBytesNodeAddress += 1;
        }
    }

    _calcNodesAddress1 () {
        let nBytesNode = this.nBytesArc + this.nBytesNodeAddress;
        let iAddr = this.oRoot.arcs.size * nBytesNode;
        for (let oNode of this.dMinimizedNodes.values()) {
            oNode.addr = iAddr;
            iAddr += Math.max(oNode.arcs.size, 1) * nBytesNode;
        }
    }

    _createJSON (nMethod) {
        /*
            Format of the binary indexable dictionary:
            Each section is separated with 4 bytes of \0
            
            - Section Header:
                /pyfsa/[version]
                    * version is an ASCII string
            
            - Section Informations:
                /[tag_lang]
                /[number of chars]
                /[number of bytes for each arc]
                /[number of bytes for each address node]
                /[number of entries]
                /[number of nodes]
                /[number of arcs]
                /[number of affixes]
                    * each field is a ASCII string
                /[stemming code]
                    * "S" means stems are generated by /suffix_code/, "A" means they are generated by /affix_code/
                      See defineSuffixCode() and defineAffixCode() for details.
                      "N" means no stemming
            
            - Section Values:
                    * a list of strings encoded in binary from utf-8, each value separated with a tabulation
            
            - Section Word Graph (nodes / arcs)
                    * A list of nodes which are a list of arcs with an address of the next node.
                      See DawgNode.convToBytes() for details.
        */
        let sByDic = "";
        if (nMethod == 1) {
            sByDic = this.oRoot.convToBytes1(this.nBytesArc, this.nBytesNodeAddress);
            for (let oNode of this.dMinimizedNodes.values()) {
                sByDic += oNode.convToBytes1(this.nBytesArc, this.nBytesNodeAddress);
            }
        }
        let oJSON = {
            "sName": this.sName,
            "nVersion": this.nMethod,
            "sHeader": this.sHeader,
            "lArcVal": this.lArcVal,
            "nArcVal": this.nArcVal,
            "byDic": sByDic,
            "sLang": this.sLang,
            "nChar": this.nChar,
            "nBytesArc": this.nBytesArc,
            "nBytesNodeAddress": this.nBytesNodeAddress,
            "nEntries": this.nEntry,
            "nNode": this.nNode,
            "nArc": this.nArc,
            "nAff": this.nAff,
            "cStemming": this.cStemming,
            "nTag": this.nTag,
            "dChar": this.dChar,
            "_arcMask": this._arcMask,
            "_finalNodeMask": this._finalNodeMask,
            "_lastArcMask": this._lastArcMask,
            "_addrBitMask": this._addrBitMask,
            "nBytesOffset": this.nBytesOffset
        };
        return oJSON;
    }
}


const oNodeCounter = {
    nNextId: 0,

    getId: function () {
        this.nNextId += 1;
        return this.nNextId-1;
    },

    reset: function () {
        this.nNextId = 0;
    }
}


class DawgNode {

    constructor () {
        this.i = oNodeCounter.getId();
        this.final = false;
        this.arcs = new Map();  // key: arc value; value: a node
        this.addr = 0;          // address in the binary dictionary
    }

    __str__ () {
        // Caution! this function is used for hashing and comparison!
        let sFinalChar = (self.final) ? "1" : "0";
        let l = [sFinalChar];
        for (let [key, node] of this.arcs.entries()) {
            l.push(key.toString());
            l.push(node.i.toString());
        }
        return l.join("_");
    }

    __hash__ () {
        // Used as a key in a python dictionary.
        return this.__str__();
    }

    __eq__ (other) {
        // Used as a key in a python dictionary.
        // Nodes are equivalent if they have identical arcs, and each identical arc leads to identical states.
        return this.__str__() == other.__str__();
    }

    sortArcs (dValOccur) {
        let lTemp = Array.from(this.arcs.entries());
        lTemp.sort(function (a, b) {
            if (dValOccur.get(a[0], 0) > dValOccur.get(b[0], 0))
                return -1;
            if (dValOccur.get(a[0], 0) < dValOccur.get(b[0], 0))
                return 1;
            return 0;
        });
        this.arcs = new Map(lTemp);
    }

    display (nTab, lArcVal, bRecur=false) {
        let sResult = "    ".repeat(nTab) + "Node: " + this.i + " " + this.final + "\n";
        for (let arc of this.arcs.keys()) {
            sResult += "    ".repeat(nTab) + lArcVal[arc] + "\n";
        }
        console.log(sResult);
        if (bRecur) {
            for (let oNode of this.arcs.values()) {
                oNode.display(nTab+1, lArcVal, bRecur);
            }
        }
    }

    // VERSION 1 =====================================================================================================
    convToBytes1 (nBytesArc, nBytesNodeAddress) {
        /*
            Node scheme:
            - Arc length is defined by nBytesArc
            - Address length is defined by nBytesNodeAddress
                                           
            |                Arc                |                         Address of next node                          |
            |                                   |                                                                       |
             /---------------\ /---------------\ /---------------\ /---------------\ /---------------\ /---------------\
             | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |
             \---------------/ \---------------/ \---------------/ \---------------/ \---------------/ \---------------/
             [...]
             /---------------\ /---------------\ /---------------\ /---------------\ /---------------\ /---------------\
             | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |
             \---------------/ \---------------/ \---------------/ \---------------/ \---------------/ \---------------/
              ^ ^
              | |
              | |
              |  \___ if 1, last arc of this node
               \_____ if 1, this node is final (only on the first arc)
        */
        let nArc = this.arcs.size;
        let nFinalNodeMask = 1 << ((nBytesArc*8)-1);
        let nFinalArcMask = 1 << ((nBytesArc*8)-2);
        if (this.arcs.size == 0) {
            let nVal = nFinalNodeMask | nFinalArcMask;
            let sBinary = this.convValueToHexString(nVal, nBytesArc);
            sBinary += this.convValueToHexString(0, nBytesNodeAddress);
            return sBinary;
        }
        let sBinary = "";
        let i = 1;
        for (let arc of this.arcs.keys()) {
            let nVal = arc;
            if (i == 1 && this.final) {
                nVal = nVal | nFinalNodeMask;
            }
            if (i == nArc) {
                nVal = nVal | nFinalArcMask;
            }
            i++;
            sBinary += this.convValueToHexString(nVal, nBytesArc);
            sBinary += this.convValueToHexString(this.arcs.get(arc).addr, nBytesNodeAddress);
        }
        return sBinary;
    }

    convValueToHexString (nVal, nByte) {
        // nVal: value to convert, nByte: number of bytes
        let sHexVal = nVal.toString(16); // conversion to hexadecimal string
        //console.log(`value: ${nVal} in ${nByte} bytes`);
        if (sHexVal.length < (nByte*2)) {
            return "0".repeat((nByte*2) - sHexVal.length) + sHexVal;
        } else if (sHexVal.length == (nByte*2)) {
            return sHexVal
        } else {
            throw "Conversion to byte string: value bigger than allowed.";
        }
    }
}



// Another attempt to sort node arcs

const _dCharOrder = new Map([ ["", new Map()] ]);
// key: previous char, value: dictionary of chars {c: nValue}


function addWordToCharDict (sWord) {
    let cPrevious = "";
    for (let cChar of sWord) {
        if (!_dCharOrder.get(cPrevious)) {
            _dCharOrder.set(cPrevious, new Map());
        }
        _dCharOrder.get(cPrevious).set(cChar, _dCharOrder.get(cPrevious).gl_get(cChar, 0) + 1);
        cPrevious = cChar;
    }
}

function getCharOrderAfterChar (cChar) {
    return _dCharOrder.gl_get(cChar, null);
}

function displayCharOrder () {
    for (let [key, value] of _dCharOrder.entries()) {
        let s = "[" + key + "]: ";
        let lTemp = Array.from(value.entries());
        lTemp.sort(function (a, b) {
            if (a[1] > b[1])
                return -1;
            if (a[1] < b[1])
                return 1;
            return 0;
        });
        for (let [c, n] of lTemp) {
            s += c+":"+n+", ";
        }
        console.log(s);
    }
}
