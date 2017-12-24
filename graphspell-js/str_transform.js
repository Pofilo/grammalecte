//// STRING TRANSFORMATION
/*jslint esversion: 6*/

// Note: 48 is the ASCII code for "0"

var str_transform = {

    distanceDamerauLevenshtein2: function (s1, s2) {
        // distance of Damerau-Levenshtein between <s1> and <s2>
        // https://fr.wikipedia.org/wiki/Distance_de_Damerau-Levenshtein
        try {
            let nLen1 = s1.length;
            let nLen2 = s2.length;
            let matrix = [];
            for (let i = 0;  i <= nLen1;  i++) {
                matrix[i] = new Array(nLen2 + 1);
            }
            for (let i = 0;  i <= nLen1;  i++) {
                matrix[i][0] = i;
            }
            for (let j = 0;  j <= nLen2;  j++) {
                matrix[0][j] = j;
            }
            for (let i = 1;  i <= nLen1;  i++) {
                for (let j = 1;  j <= nLen2;  j++) {
                    let nCost = (s1[i] === s2[j]) ? 0 : 1;
                    matrix[i][j] = Math.min(
                        matrix[i-1][j] + 1,         // Deletion
                        matrix[i][j-1] + 1,         // Insertion
                        matrix[i-1][j-1] + nCost    // Substitution
                    );
                    if (i > 1 && j > 1 && s1[i] == s2[j-1] && s1[i-1] == s2[j]) {
                        matrix[i][j] = Math.min(matrix[i][j], matrix[i-2][j-2] + nCost);  // Transposition
                    }
                }
            }
            return matrix[nLen1][nLen2];
        }
        catch (e) {
            helpers.logerror(e);
        }
    },

    distanceDamerauLevenshtein: function (s1, s2) {
        // distance of Damerau-Levenshtein between <s1> and <s2>
        // https://fr.wikipedia.org/wiki/Distance_de_Damerau-Levenshtein
        try {
            let nLen1 = s1.length;
            let nLen2 = s2.length;
            let INF = nLen1 + nLen2;
            let matrix = [];
            let sd = {};
            for (let i = 0; i < nLen1+2; i++) {
                matrix[i] = new Array(nLen2+2);
            }
            matrix[0][0] = INF;
            for (let i = 0; i <= nLen1; i++) {
                matrix[i+1][1] = i;
                matrix[i+1][0] = INF;
                sd[s1[i]] = 0;
            }
            for (let j = 0; j <= nLen2; j++) {
                matrix[1][j+1] = j;
                matrix[0][j+1] = INF;
                sd[s2[j]] = 0;
            }

            for (let i = 1; i <= nLen1; i++) {
                let DB = 0;
                for (let j = 1; j <= nLen2; j++) {
                    let i1 = sd[s2[j-1]];
                    let j1 = DB;
                    if (s1[i-1] === s2[j-1]) {
                        matrix[i+1][j+1] = matrix[i][j];
                        DB = j;
                    }
                    else {
                        matrix[i+1][j+1] = Math.min(matrix[i][j], Math.min(matrix[i+1][j], matrix[i][j+1])) + 1;
                    }
                    matrix[i+1][j+1] = Math.min(matrix[i+1][j+1], matrix[i1] ? matrix[i1][j1] + (i-i1-1) + 1 + (j-j1-1) : Infinity);
                }
                sd[s1[i-1]] = i;
            }
            return matrix[nLen1+1][nLen2+1];
        }
        catch (e) {
            helpers.logerror(e);
        }
    },

    showDistance (s1, s2) {
        console.log(`Distance: ${s1} / ${s2} = ${this.distanceDamerauLevenshtein(s1, s2)})`);
    },

    getStemFromSuffixCode: function (sFlex, sSfxCode) {
        // Suffix only
        if (sSfxCode == "0") {
            return sFlex;
        }
        return sSfxCode[0] == '0' ? sFlex + sSfxCode.slice(1) : sFlex.slice(0, -(sSfxCode.charCodeAt(0)-48)) + sSfxCode.slice(1);
    },
    
    getStemFromAffixCode: function (sFlex, sAffCode) {
        // Prefix and suffix
        if (sAffCode == "0") {
            return sFlex;
        }
        if (!sAffCode.includes("/")) {
            return "# error #";
        }
        let [sPfxCode, sSfxCode] = sAffCode.split('/');
        sFlex = sPfxCode.slice(1) + sFlex.slice(sPfxCode.charCodeAt(0)-48);
        return sSfxCode[0] == '0' ? sFlex + sSfxCode.slice(1) : sFlex.slice(0, -(sSfxCode.charCodeAt(0)-48)) + sSfxCode.slice(1);
    }
};


if (typeof(exports) !== 'undefined') {
    exports.getStemFromSuffixCode = str_transform.getStemFromSuffixCode;
    exports.getStemFromAffixCode = str_transform.getStemFromAffixCode;
}
