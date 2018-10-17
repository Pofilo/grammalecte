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

//Initialisation des messages
const msgStart = "\x1b[31mBienvenue sur Grammalecte pour NodeJS!!!\x1b[0m\n";
const msgPrompt = "\x1b[36mGrammaJS\x1b[33m>\x1b[0m ";
const msgSuite = "\x1b[33m…\x1b[0m ";
const msgEnd = "\x1b[31m\x1b[5m\x1b[5mBye bye!\x1b[0m";

var repPreference = {
    json: false,
    perf: false
};

var sBufferConsole = "";
var sCmdToExec = "";
var sText = "";

var cmdAction = {
    help: {
        short: "",
        arg: "",
        description: "Affiche les informations que vous lisez ;)",
        execute: ""
    },
    perf: {
        short: "",
        arg: "on/off",
        description: "Permet d’afficher le temps d’exécution des commandes.",
        execute: ""
    },
    json: {
        short: "",
        arg: "on/off",
        description: "Réponse en format format json.",
        execute: ""
    },
    exit: {
        short: "",
        arg: "",
        description: "Client interactif: Permet de le quitter.",
        execute: ""
    },
    text: {
        short: "",
        arg: "texte",
        description: "Client / Server: Définir un texte pour plusieurs actions.",
        execute: ""
    },
    format: {
        short: "",
        arg: "texte",
        description: "Permet de mettre en forme le texte.",
        execute: "formatText"
    },
    check: {
        short: "",
        arg: "texte",
        description: "Vérifie la grammaire et l’orthographe d'un texte.",
        execute: "verifParagraph"
    },
    lexique: {
        short: "",
        arg: "texte",
        description: "Affiche le lexique du texte.",
        execute: "lexique"
    },
    spell: {
        short: "",
        arg: "mot",
        description: "Vérifie l’existence d’un mot.",
        execute: "spell"
    },
    suggest: {
        short: "",
        arg: "mot",
        description: "Suggestion des graphies proches d’un mot.",
        execute: "suggest"
    },
    morph: {
        short: "",
        arg: "mot",
        description: "Affiche les informations pour un mot.",
        execute: "morph"
    },
    lemma: {
        short: "",
        arg: "mot",
        description: "Donne le lemme d’un mot.",
        execute: "lemma"
    },
    gceoption: {
        short: "",
        arg: "+/-name",
        description: "Définit les options à utiliser par le correcteur grammatical.",
        execute: ""
    },
    tfoption: {
        short: "",
        arg: "+/-name",
        description: "Définit les options à utiliser par le formateur de texte.",
        execute: ""
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
    for (const action of ["json", "perf", "gceoption", "tfoption"]) {
        if (action in oRep) {
            repText += toTitle(action) + " " + oRep[action];
        }
    }

    for (const action of ["morph", "lemma"]) {
        if (action in oRep) {
            for (const toAff of oRep[action]) {
                if (toAff.text == "NoText") {
                    repText += "\n" + toTitle(action) + ": Pas de texte à vérifier.";
                } else {
                    if (toAff.reponse.length == 0) {
                        repText += "\nAuncun " + toTitle(action) + " existant pour: «" + toAff.text + "»";
                    } else {
                        let ascii = "├";
                        let numRep = 0;
                        repText += "\n" + toTitle(action) + " possible de: «" + toAff.text + "»";
                        for (let reponse of toAff.reponse) {
                            numRep++;
                            if (numRep == toAff.reponse.length) {
                                ascii = "└";
                            }
                            repText += "\n " + ascii + " " + reponse;
                        }
                    }
                    repText += affPerf(toAff.time);
                }
            }
        }
    }

    if ("spell" in oRep) {
        for (const toAff of oRep.spell) {
            if (toAff.text == "NoText") {
                repText += "\nSpell: Pas de texte à vérifier.";
            } else {
                repText += "\nLe mot «" + toAff.text + "» " + (toAff.reponse ? "existe" : "innexistant");
                repText += affPerf(toAff.time);
            }
        }
    }

    if ("suggest" in oRep) {
        for (const toAff of oRep.suggest) {
            if (toAff.text == "NoText") {
                repText += "\nSuggest : Pas de texte à vérifier.";
            } else {
                //let numgroup = 0;
                if (toAff.reponse.length == 0) {
                    repText += "\nAucune suggestion possible pour: «" + toAff.text + "»";
                } else {
                    repText += "\nSuggestion possible de: «" + toAff.text + "»";
                    let ascii = "├";
                    let numRep = 0;
                    for (let reponse of toAff.reponse) {
                        numRep++;
                        if (numRep == toAff.reponse.length) {
                            ascii = "└";
                        }
                        repText += "\n " + ascii + " " + reponse;
                    }
                }
                repText += affPerf(toAff.time);
            }
        }
    }

    if ("format" in oRep) {
        for (const toAff of oRep.format) {
            if (toAff.text == "NoText") {
                repText += "\nPas de texte à formatter.";
            } else {
                repText += "\nMise en forme:\n" + toAff.reponse;
                repText += affPerf(toAff.time);
            }
        }
    }

    if ("lexique" in oRep) {
        for (const toAff of oRep.lexique) {
            if (toAff.text == "NoText") {
                repText += "\nLexique: Pas de texte à vérifier.";
            } else {
                repText += "\nLexique:";

                let ascii1, ascii1a, numRep1, ascii2, numRep2, replength;

                ascii1 = "├";
                ascii1a = "│";
                numRep1 = 0;

                replength = toAff.reponse.length;
                for (let reponse of toAff.reponse) {
                    numRep1++;
                    if (numRep1 == replength) {
                        ascii1 = "└";
                        ascii1a = " ";
                    }
                    repText += "\n  " + ascii1 + " " + reponse.sValue;
                    let ascii = "├";
                    let numRep = 0;
                    for (let label of reponse.aLabel) {
                        numRep++;
                        if (numRep == reponse.aLabel.length) {
                            ascii = "└";
                        }
                        repText += "\n  " + ascii1a + " " + ascii + " " + label.trim();
                    }
                }
                repText += affPerf(toAff.time);
            }
        }
    }

    if ("check" in oRep) {
        for (const toAff of oRep.check) {
            if (toAff.text == "NoText") {
                repText += "\nCheck: Pas de texte à vérifier.";
            } else {
                let ascii1, ascii1a, numRep1, ascii2, numRep2, replength;

                ascii1 = "├";
                ascii1a = "│";
                numRep1 = 0;
                replength = Object.keys(toAff.reponse.lGrammarErrors).length;
                if (replength == 0) {
                    repText += "\nPas de faute de grammaire";
                } else {
                    repText += "\nFaute(s) de grammaire";
                    for (let gramma of toAff.reponse.lGrammarErrors) {
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
                replength = Object.keys(toAff.reponse.lSpellingErrors).length;
                if (replength == 0) {
                    repText += "\nPas de faute d'orthographe";
                } else {
                    repText += "\nFaute(s) d'orthographe";
                    for (let ortho of toAff.reponse.lSpellingErrors) {
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
                repText += affPerf(toAff.time);
            }
        }
    }

    if ("help" in oRep) {
        let colorNum = 31;
        for (const action of oRep.help) {
            //Uniquement pour le fun on met de la couleur ;)
            if (action.indexOf("===") > -1) {
                console.log("\x1b[" + colorNum + "m" + action + "\x1b[0m");
                colorNum = colorNum + 2;
            } else {
                console.log(action);
            }
        }
    }

    return repText.trim("\n");
}

function affPerf(aTime) {
    if (aTime == "NA") {
        return "";
    }
    return "\nExécuté en: " + aTime + " ms";
}

function actionGramma(repPreference, action, aAction) {
    let tStart, tEnd;
    let tmpRep = {
        text: "",
        reponse: "",
        time: "NA"
    };

    if (!isBool(aAction) && aAction !== "") {
        tmpRep.text = aAction;
        sText = aAction;
    } else if (!isBool(sText)) {
        //Utilisation du dernier texte connu
        tmpRep.text = sText;
    } else {
        tmpRep.text = "NoText";
    }

    if (repPreference.perf) {
        tStart = performance.now();
    }

    tmpRep.reponse = oGrammarChecker[cmdAction[action].execute](tmpRep.text);

    if (repPreference.perf) {
        tEnd = performance.now();
        tmpRep["time"] = (Math.round((tEnd - tStart) * 1000) / 1000).toString();
    }

    return tmpRep;
}

function actionToExec(aArg) {
    let repAction = {};

    if (!isBool(aArg.text)) {
        sText = aArg.text;
    }

    for (const action of ["json", "perf"]) {
        if (getArg(aArg, [action])) {
            repPreference[action] = getArgVal(aArg, [action]);
            repAction[action] = repPreference[action] ? "ON" : "OFF";
        }
    }

    for (const action of ["gceoption", "tfoption"]) {
        if (getArg(aArg, [action])) {
            let sFonction = action == "gceoption" ? "GceOption" : "TfOption";
            let sOpt = sText.split(" ");
            if (sOpt[0] == "reset") {
                oGrammarChecker["reset" + sFonction + "s"]();
                repAction[action] = "reset";
            } else {
                for (const optAction of sOpt) {
                    let bOptVal = optAction[0] == "+" ? true : false;
                    let sOptName = optAction.slice(1, optAction.length);
                    oGrammarChecker["set" + sFonction](sOptName, bOptVal);
                    repAction[action] = sText;
                }
            }
        }
    }

    for (const action in aArg) {
        if (cmdAction[action] && cmdAction[action].execute !== "") {
            //console.log(aArg, aArg[action], !isBool(aArg[action]), !isBool(repAction.text));
            if (!repAction[action]) {
                repAction[action] = [];
            }

            if (typeof aArg[action] === "object") {
                for (const valAction of aArg[action]) {
                    tmpRep = actionGramma(repPreference, action, valAction);
                    repAction[action].push(tmpRep);
                }
            } else {
                tmpRep = actionGramma(repPreference, action, aArg[action]);
                repAction[action].push(tmpRep);
            }
        }
    }

    if (getArg(aArg, ["help"])) {
        repAction["help"] = [];

        repAction["help"].push("================================== Aide: ==================================");
        repAction["help"].push("");
        repAction["help"].push("Il y a trois modes de fonctionnement: client / client intératif / serveur.");

        repAction["help"].push(" * le client intéractif: «gramma-cli -i».");
        repAction["help"].push(' * pour le client exemple: «gramma-cli --command "mot/texte"».');
        repAction["help"].push(" * le serveur se lance avec la commande «gramma-cli --server --port 8085».");

        repAction["help"].push("");
        repAction["help"].push("========================= Les commandes/arguments: ========================");
        repAction["help"].push("");
        for (const action in cmdAction) {
            repAction["help"].push(action.padEnd(10, " ") + ": " + cmdAction[action].arg.padEnd(8, " ") + ": " + cmdAction[action].description);
        }
        repAction["help"].push("");
        repAction["help"].push("================================== Note: ==================================");
        repAction["help"].push("");
        repAction["help"].push("En mode client: les arguments sont de la forme «--argument» !");
        repAction["help"].push("En mode client intéractif: pour les commandes concernant un texte, vous");
        repAction["help"].push("  pouvez taper la commande puis Entrée (pour saisir le texte) pour ");
        repAction["help"].push('  terminer la saisie du texte et exécuter la commande taper /"commande"');
    }

    if (repPreference.json) {
        return JSON.stringify(repAction);
    } else {
        return repToText(repAction);
    }
}

function argToExec(aCommand, aText, rl, resetCmd = true) {
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
    if (resetCmd) {
        sCmdToExec = "";
    }

    if (typeof rl !== "undefined") {
        rl.setPrompt(msgPrompt);
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
    console.log(actionToExec({ help: true }));
} else {
    //var GrammarChecker = require("./api.js");
    //console.log(module.paths);
    var GrammarChecker = require("grammalecte");
    var oGrammarChecker = new GrammarChecker.GrammarChecker(["Grammalecte", "Graphspell", "TextFormatter", "Lexicographer", "Tokenizer"], "fr");

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
        process.stdin.setEncoding("utf8");

        const readline = require("readline");
        const rl = readline.createInterface({
            crlfDelay: Infinity,
            input: process.stdin,
            output: process.stdout,
            completer: completer,
            prompt: msgPrompt
        });

        //console.log( process.stdin.isTTY );
        console.log(msgStart);
        rl.prompt();
        rl.on("line", sBuffer => {
            //process.stdout.write
            if (sBuffer == "exit") {
                console.log(msgEnd);
                process.exit(0);
            }

            let lg = sBuffer.toLowerCase().trim();
            let bSpace = lg.indexOf(" ") > -1;
            if (!bSpace) {
                if (cmdOne.indexOf(lg) > -1) {
                    argToExec(lg, sBuffer, rl, true);
                } else if (cmdAll.indexOf(lg) > -1) {
                    sBufferConsole = "";
                    sCmdToExec = lg;
                    //Prompt simple pour distinguer que c"est une suite d"une commande
                    rl.setPrompt(msgSuite);
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
            console.log(msgEnd);
            process.exit(0);
        });
    } else {
        if (
            typeof argCmd.text !== "object" &&
            typeof argCmd.json !== "object" &&
            typeof argCmd.perf !== "object" &&
            typeof argCmd.gceoption !== "object" &&
            typeof argCmd.tfoption !== "object"
        ) {
            console.log(actionToExec(argCmd));
        } else {
            console.log("Votre demmande est confuse.");
        }
    }
}
