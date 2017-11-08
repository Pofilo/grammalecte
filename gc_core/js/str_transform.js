//// STRING TRANSFORMATION
/*jslint esversion: 6*/

// Note: 48 is the ASCII code for "0"

var str_transform = {

    distanceDamerauLevenshtein: function (s1, s2) {
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
            //console.log(s2 + ": " + matrix[nLen1][nLen2]);
            return matrix[nLen1][nLen2];
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
