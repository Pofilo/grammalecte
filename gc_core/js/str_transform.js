//// STRING TRANSFORMATION
/*jslint esversion: 6*/

// Note: 48 is the ASCII code for "0"

var str_transform = {
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
