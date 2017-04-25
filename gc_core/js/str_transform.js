//// STRING TRANSFORMATION

var dSimilarChars = new Map ([
    ["a", "aàâáä"],
    ["à", "aàâáä"],
    ["â", "aàâáä"],
    ["á", "aàâáä"],
    ["ä", "aàâáä"],
    ["c", "cç"],
    ["ç", "cç"],
    ["e", "eéêèë"],
    ["é", "eéêèë"],
    ["ê", "eéêèë"],
    ["è", "eéêèë"],
    ["ë", "eéêèë"],
    ["i", "iîïíì"],
    ["î", "iîïíì"],
    ["ï", "iîïíì"],
    ["í", "iîïíì"],
    ["ì", "iîïíì"],
    ["o", "oôóòö"],
    ["ô", "oôóòö"],
    ["ó", "oôóòö"],
    ["ò", "oôóòö"],
    ["ö", "oôóòö"],
    ["u", "uûùüú"],
    ["û", "uûùüú"],
    ["ù", "uûùüú"],
    ["ü", "uûùüú"],
    ["ú", "uûùüú"]
]);

// Note: 48 is the ASCII code for "0"

// Suffix only
function getStemFromSuffixCode (sFlex, sSfxCode) {
    if (sSfxCode == "0") {
        return sFlex;
    }
    return sSfxCode[0] == '0' ? sFlex + sSfxCode.slice(1) : sFlex.slice(0, -(sSfxCode.charCodeAt(0)-48)) + sSfxCode.slice(1);
}

// Prefix and suffix
function getStemFromAffixCode (sFlex, sAffCode) {
    if (sAffCode == "0") {
        return sFlex;
    }
    if (!sAffCode.includes("/")) {
        return "# error #";
    }
    var [sPfxCode, sSfxCode] = sAffCode.split('/');
    sFlex = sPfxCode.slice(1) + sFlex.slice(sPfxCode.charCodeAt(0)-48);
    return sSfxCode[0] == '0' ? sFlex + sSfxCode.slice(1) : sFlex.slice(0, -(sSfxCode.charCodeAt(0)-48)) + sSfxCode.slice(1);
}


exports.getStemFromSuffixCode = getStemFromSuffixCode;
exports.getStemFromAffixCode = getStemFromAffixCode;
