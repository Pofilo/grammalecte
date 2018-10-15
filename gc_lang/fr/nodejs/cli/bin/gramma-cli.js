#! /usr/bin/env node
// -*- js -*-

// Gramma-Cli
// Grammalect client pour node

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global require, console */

/*
Doc :
https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment
https://stackoverflow.com/questions/41058569/what-is-the-difference-between-const-and-const-in-javascript
*/

const argCmd = require("../lib/minimist.js")(process.argv.slice(2));
const { performance } = require("perf_hooks");

var repJson = false;
var repPerf = false;

var sBufferConsole = "";
var sCmdToExec = "";

var cmdAction = {
    help: {
        short: "",
        description: "Affichie les informations que vous lisez ;)",
        execute: ""
    },
    perf: {
        short: "",
        description: "(on/off) Permet d'afficher le temps d'exécution des commandes.",
        execute: ""
    },
    json: {
        short: "",
        description: "(on/off) Réponse en format format json.",
        execute: ""
    },
    exit: {
        short: "",
        description: "Client intéractif: Permet de le quitter.",
        execute: ""
    },
    text: {
        short: "",
        description: "Client / Server: Définir un texte pour plusieurs actions.",
        execute: ""
    },
    gceoption: {
        short: "",
        description: "Défini une option a utilisé par le correcteur de grammaire.",
        execute: ""
    },
    format: {
        short: "",
        description: "Permet de mettre en forme le texte.",
        execute: "formatText"
    },
    check: {
        short: "",
        description: "Vérifie la grammaire et l'orthographe d'un texte.",
        execute: "verifParagraph"
    },
    lexique: {
        short: "",
        description: "Affiche le lexique du texte.",
        execute: "lexique"
    },
    spell: {
        short: "",
        description: "Vérifie l'existence d'un mot.",
        execute: "spell"
    },
    suggest: {
        short: "",
        description: "Suggestion des orthographes possible d'un mot.",
        execute: "suggest"
    },
    morph: {
        short: "",
        description: "Affiche les informations pour un mot.",
        execute: "morph"
    },
    lemma: {
        short: "",
        description: "Donne le lemme d'un mot.",
        execute: "lemma"
    }
};

var cmdOne = ["json", "perf", "help", "exit"];
var cmdMulti = ["text", "format", "check", "lexique", "spell", "suggest", "morph", "lemma"];

var cmdAll = [...cmdOne, ...cmdMulti];

function getArgVal(aArg, lArgOk) {
    for (let eArgOk of lArgOk) {
        if (typeof aArg[eArgOk] !== "undefined") {
            return aArg[eArgOk];
        }
    }
    return false;
}

function getArg(aArg, lArgOk) {
    for (let eArgOk of lArgOk) {
        if (typeof aArg[eArgOk] !== "undefined") {
            return true;
        }
    }
    return false;
}

function toBool(aStr) {
    return aStr === "true" || aStr === "on";
}

function isBool(aStr) {
    if (typeof aStr === "boolean" || typeof aStr === "undefined") {
        return true;
    }
    aStr = aStr.toLowerCase();
    return aStr === "true" || aStr === "on" || aStr === "false" || aStr === "off" || aStr === "";
}

function toTitle(aStr) {
    return aStr.charAt(0).toUpperCase() + aStr.slice(1);
}

function repToText(oRep) {
    //console.log(oRep);
    let repText = "";
    for (const action of ["Json", "Perf", "GceOption"]) {
        if (action in oRep) {
            repText += toTitle(action) + " " + oRep[action];
        }
    }

    for (const action of ["morph", "lemma"]) {
        if (action in oRep) {
            if (oRep[action] == "NoText") {
                repText += "\n" + toTitle(action) + ": Pas de texte à vérifier.";
            } else {
                if (oRep[action].length == 0) {
                    repText += "\nAuncun " + toTitle(action) + " existant pour: " + oRep.text;
                } else {
                    let ascii = "├";
                    let numRep = 0;
                    repText += "\n" + toTitle(action) + " possible de: " + oRep.text;
                    for (let reponse of oRep[action]) {
                        numRep++;
                        if (numRep == oRep[action].length) {
                            ascii = "└";
                        }
                        repText += "\n " + ascii + " " + reponse;
                    }
                }
            }
        }
    }

    if ("spell" in oRep) {
        if (oRep.spell == "NoText") {
            repText += "\nSpell: Pas de texte à vérifier.";
        } else {
            repText += "\nLe mot " + (oRep.spell || oRep.text) + " " + (oRep.spell ? "existe" : "innexistant");
        }
    }

    if ("format" in oRep) {
        if (oRep.spell == "NoText") {
            repText += "\nPas de texte à formatter.";
        } else {
            repText += "\nMise en forme:\n" + (oRep.format || oRep.text);
        }
    }

    if ("suggest" in oRep) {
        if (oRep.suggest == "NoText") {
            repText += "\nSuggest : Pas de texte à vérifier.";
        } else {
            //let numgroup = 0;
            if (oRep.suggest.length == 0) {
                repText += "\nAucune suggestion possible pour: " + oRep.text;
            } else {
                repText += "\nSuggestion possible de: " + oRep.text;
                let ascii = "├";
                let numRep = 0;
                for (let reponse of oRep.suggest) {
                    numRep++;
                    if (numRep == oRep.suggest.length) {
                        ascii = "└";
                    }
                    repText += "\n " + ascii + " " + reponse;
                }
            }
        }
    }

    if ("lexique" in oRep) {
        if (oRep.lexique == "NoText") {
            repText += "\nLexique: Pas de texte à vérifier.";
        } else {
            repText += "\nLexique:";
            for (let reponse of oRep.lexique) {
                repText += "\n" + reponse.sValue;
                let ascii = "├";
                let numRep = 0;
                for (let label of reponse.aLabel) {
                    numRep++;
                    if (numRep == reponse.aLabel.length) {
                        ascii = "└";
                    }
                    repText += "\n " + ascii + " " + label;
                }
            }
        }
    }

    if ("check" in oRep) {
        if (oRep.check == "NoText") {
            repText += "\nCheck: Pas de texte à vérifier.";
        } else {
            let ascii1, ascii1a, numRep1, ascii2, numRep2, replength;

            ascii1 = "├";
            ascii1a = "│";
            numRep1 = 0;
            replength = Object.keys(oRep.check.lGrammarErrors).length;
            if (replength == 0) {
                repText += "\nPas de faute de grammaire";
            } else {
                repText += "\nFaute(s) de grammaire";
                for (let gramma of oRep.check.lGrammarErrors) {
                    numRep1++;
                    if (numRep1 == replength) {
                        ascii1 = "└";
                        ascii1a = " ";
                    }
                    repText += "\n " + ascii1 + " " + gramma.nStart + "->" + gramma.nEnd + " " + gramma.sMessage;
                    ascii2 = "├";
                    numRep2 = 0;
                    for (let suggestion of gramma.aSuggestions) {
                        numRep2++;
                        if (numRep2 == gramma.aSuggestions.length) {
                            ascii2 = "└";
                        }
                        repText += "\n " + ascii1a + "  " + ascii2 + ' "' + suggestion + '"';
                    }
                }
            }

            ascii1 = "├";
            ascii1a = "│";
            numRep1 = 0;
            replength = Object.keys(oRep.check.lSpellingErrors).length;
            if (replength == 0) {
                repText += "\nPas de faute d'orthographe";
            } else {
                repText += "\nFaute(s) d'orthographe";
                for (let ortho of oRep.check.lSpellingErrors) {
                    numRep1++;
                    if (numRep1 == replength) {
                        ascii1 = "└";
                        ascii1a = " ";
                    }
                    repText += "\n " + ascii1 + " " + ortho.nStart + "->" + ortho.nEnd + " " + ortho.sValue;
                    ascii2 = "├";
                    numRep2 = 0;
                    for (let suggestion of ortho.aSuggestions) {
                        numRep2++;
                        if (numRep2 == ortho.aSuggestions.length) {
                            ascii2 = "└";
                        }
                        repText += "\n " + ascii1a + "  " + ascii2 + ' "' + suggestion + '"';
                    }
                }
            }
        }
    }


    if ("help" in oRep) {
        let colorNum = 31;
        for (const action of oRep.help) {
            //Uniquement pour le fun on met de la couleur ;)
            if(action.indexOf('===')>-1){
                console.log("\x1b["+colorNum+"m"+action+"\x1b[0m");
                colorNum = colorNum + 2;
            } else {
                console.log(action);
            }
        }
    }

    if (oRep.time) {
        repText += "\nExécuté en: " + oRep.time + " ms";
    }
    return repText.trim("\n");
}

var sWord = "";
var actionToExec = function(aArg) {
    let repAction = {};
    let tStart, tEnd;

    if (!isBool(aArg.text)) {
        sWord = aArg.text;
    }

    repAction["text"] = sWord;

    if (getArg(aArg, ["json"])) {
        repJson = getArgVal(aArg, ["json"]);
        repAction["Json"] = repJson ? "ON" : "OFF";
    }

    if (getArg(aArg, ["perf"])) {
        repPerf = getArgVal(aArg, ["perf"]);
        repAction["Perf"] = repPerf ? "ON" : "OFF";
    }

    if (repPerf) {
        tStart = performance.now();
    }

    if (getArg(aArg, ["gceoption"])) {
        let sOpt = sWord.split(" ");
        if (sOpt[0] == "reset") {
            oGrammarChecker.resetGceOptions();
            repAction["GceOption"] = "reset";
        } else {
            let bOptVal = toBool(sOpt[1]);
            oGrammarChecker.setGceOption(sOpt[0], bOptVal);
            repAction["GceOption"] = sOpt[0] + " " + (bOptVal ? "ON" : "OFF");
        }
    }

    for (const action in aArg) {
        if (cmdAction[action] && cmdAction[action].execute !== "") {
            if (!isBool(aArg[action]) && aArg[action] !== "") {
                repAction.text = aArg[action];
                sWord = repAction.text;
            }
            if (!isBool(repAction.text)) {
                repAction[action] = oGrammarChecker[cmdAction[action].execute](repAction.text);
            } else {
                repAction[action] = "NoText";
            }
        }
    }

    if (getArg(aArg, ["help"])) {
        repAction["help"] = [];

        repAction["help"].push("================================== Aide: ==================================");
        repAction["help"].push("");
        repAction["help"].push("Il y a trois modes de fonctionnement: client / client intératif / serveur.");

        repAction["help"].push(" * le client intéractif: «gramma-cli -i».");
        repAction["help"].push(" * pour le client exemple: «gramma-cli --command \"mot/texte\"».");
        repAction["help"].push(" * le serveur se lance avec la commande «gramma-cli --server --port 8085».");

        repAction["help"].push("");
        repAction["help"].push("========================= Les commandes/arguments: ========================");
        repAction["help"].push("");
        for (const action in cmdAction) {
            repAction["help"].push(action.padEnd(15, ' ') + ': ' + cmdAction[action].description);
        }
        repAction["help"].push("");
        repAction["help"].push("================================== Note: ==================================");
        repAction["help"].push("");
        repAction["help"].push("En mode client: les arguments sont de la forme «--argument» !");
        repAction["help"].push("En mode client intéractif: pour les commandes concernant un texte, vous");
        repAction["help"].push("  pouvez taper la commande puis entrer (pour saisir le texte) pour ");
        repAction["help"].push("  terminer la saisie du texte et exécuter la commande taper /\"commande\"");
    }

    if (repPerf) {
        tEnd = performance.now();
        //On ajoute l"information au résultat
        repAction["time"] = (Math.round((tEnd - tStart) * 1000) / 1000).toString();
    }

    if (repJson) {
        return JSON.stringify(repAction);
    } else {
        return repToText(repAction);
    }
};

function argToExec(aCommand, aText, rl, resetCmd = true){
    let execAct = {};
    aCommand = aCommand.toLowerCase();

    if (!isBool(aText)) {
        execAct["text"] = aText;
        execAct[aCommand] = true;
    } else {
        execAct[aCommand] = toBool(aText);
    }

    console.log(actionToExec(execAct));
    //sBufferConsole = "";
    if (resetCmd){
        sCmdToExec = "";
    }

    if (typeof(rl) !== "undefined"){
        rl.setPrompt("\x1b[36mGrammaJS\x1b[33m>\x1b[0m ");
    }
}

function completer(line) {
    var hits = cmdAll.filter(function(c) {
        if (c.indexOf(line) == 0) {
            return c;
        }
    });
    return [hits && hits.length ? hits : cmdAll, line];
}

if (process.argv.length <= 2) {
    console.log(actionToExec({help:true}));
} else {
    //var GrammarChecker = require("./api.js");
    //console.log(module.paths);
    var GrammarChecker = require("grammalecte");
    var oGrammarChecker = new GrammarChecker.GrammarChecker(
        ["Grammalecte", "Graphspell", "TextFormatter", "Lexicographer", "Tokenizer"],
        "fr"
    );

    if (argCmd.server) {
        var http = require("http");
        var url = require("url");
        var querystring = require("querystring");

        var collectRequestData = function(aRequest, aResponse, callback) {
            let sBody = "";
            aRequest.on("data", chunk => {
                sBody += chunk.toString();
            });
            aRequest.on("end", () => {
                let oParams = querystring.parse(sBody);
                //console.log(oParams /*, page*/);
                callback(querystring.parse(sBody), aResponse);
            });
        };

        var reponseRequest = function(aParms, aResponse) {
            aResponse.setHeader("access-control-allow-origin", "*");
            aResponse.writeHead(200, { "Content-Type": "application/json" });
            aParms["json"] = true; //Forcage de la réponse en json
            aResponse.write(actionToExec(aParms));
            aResponse.end();
        };

        var server = http.createServer(function(aRequest, aResponse) {
            var sPage = url.parse(aRequest.url).pathname;
            if (sPage !== "/") {
                //favicon.ico
                aResponse.writeHead(404, { "Content-Type": "text/plain" });
                aResponse.write("Error 404");
                aResponse.end();
            } else {
                if (aRequest.method === "POST") {
                    collectRequestData(aRequest, aResponse, reponseRequest);
                } else {
                    let oParams = querystring.parse(url.parse(aRequest.url).query);
                    reponseRequest(oParams, aResponse);
                }
            }
        });
        server.listen(argCmd.port || 2212);
        console.log("Server started on http://127.0.0.1:" + (argCmd.port || 2212) + "/");
    } else if (getArg(argCmd, ["i", "interactive"])) {
        const readline = require("readline");
        const reg = /(.*?) (.*)/gm;

        process.stdin.setEncoding("utf8");

        const rl = readline.createInterface({
            crlfDelay: Infinity,
            input: process.stdin,
            output: process.stdout,
            completer: completer,
            prompt: "\x1b[36mGrammaJS\x1b[33m>\x1b[0m "
        });
        //console.log( process.stdin.isTTY );
        process.stdout.write("\x1b[31mBienvenu sur Grammalecte pour NodeJS!!!\x1b[0m\n");
        rl.prompt();
        rl.on("line", sBuffer => {
            //process.stdout.write
            if (sBuffer == "exit") {
                console.log("\x1b[31m\x1b[5m\x1b[5mBye bye!\x1b[0m");
                process.exit(0);
            }

            let lg = sBuffer.toLowerCase().trim();
            let bSpace = lg.indexOf(" ") > -1;
            //sBufferConsole
            //console.log("\""+sBuffer+"\"");
            if (!bSpace) {
                //console.log("=> ", lg.slice(0, lg.length-1), cmdAll.indexOf( lg.slice(-1) ));
                if (cmdOne.indexOf(lg) > -1){
                    argToExec(lg, sBuffer, rl, true);
                } else if (cmdAll.indexOf(lg) > -1) {
                    sBufferConsole = "";
                    sCmdToExec = lg;
                    //Prompt simple pour distinguer que c"est une suite d"une commande
                    rl.setPrompt("\x1b[33m>\x1b[0m ");
                } else if (lg.slice(1) == sCmdToExec) {
                    argToExec(sCmdToExec, sBufferConsole, rl, true);
                } else if (cmdAll.indexOf(lg.slice(0, lg.length - 1)) > -1) {
                    argToExec(lg.slice(0, lg.length - 1), sBufferConsole, rl, true);
                } else if (lg == "") {
                    sBufferConsole += "\n";
                }
            } else if (sCmdToExec == "") {
                let regRep = /(.*?) (.*)/gm.exec(sBuffer);
                //console.log(regRep.length,sBuffer);
                if (regRep && regRep.length == 3) {
                    argToExec(regRep[1], regRep[2]);
                }
            } else {
                sBufferConsole += sBuffer + "\n";
            }

            rl.prompt();
        }).on("close", () => {
            console.log("\n\x1b[31m\x1b[5mBye bye!\x1b[0m");
            process.exit(0);
        });
    } else {
        console.log(actionToExec(argCmd));
    }
}
