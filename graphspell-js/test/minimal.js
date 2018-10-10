/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global require, console */

"use strict";

/*
Reset = "\x1b[0m"
Bright = "\x1b[1m"
Dim = "\x1b[2m"
Underscore = "\x1b[4m"
Blink = "\x1b[5m"
Reverse = "\x1b[7m"
Hidden = "\x1b[8m"

FgBlack = "\x1b[30m"
FgRed = "\x1b[31m"
FgGreen = "\x1b[32m"
FgYellow = "\x1b[33m"
FgBlue = "\x1b[34m"
FgMagenta = "\x1b[35m"
FgCyan = "\x1b[36m"
FgWhite = "\x1b[37m"

BgBlack = "\x1b[40m"
BgRed = "\x1b[41m"
BgGreen = "\x1b[42m"
BgYellow = "\x1b[43m"
BgBlue = "\x1b[44m"
BgMagenta = "\x1b[45m"
BgCyan = "\x1b[46m"
BgWhite = "\x1b[47m"
*/

//console.log('\x1B[2J\x1B[0f'); //Clear the console (cmd win)

var spellCheck = require("../spellchecker.js");
var checker = new spellCheck.SpellChecker('fr', '../_dictionaries');

function perf(sWord){
    console.log('\x1b[1m\x1b[31m%s\x1b[0m', '--------------------------------');

    console.log('\x1b[36m%s \x1b[32m%s\x1b[0m', 'Vérification de:', sWord);
    console.time('Valid:'+sWord);
    console.log(sWord, checker.isValid(sWord) );
    console.timeEnd('Valid:'+sWord);

    console.log('\x1b[36m%s \x1b[32m%s\x1b[0m', 'Suggestion de:', sWord);
    console.time('Suggestion:'+sWord);
    console.log( JSON.stringify( Array.from(checker.suggest(sWord)) ) );
    console.timeEnd('Suggestion:'+sWord);
}

perf('binjour');
perf('saluté');
perf('graphspell');
perf('dicollecte');
