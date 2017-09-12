// JavaScript

let oVerb = null;

self.port.on("conjugate", function (sVerb) {
    createVerbAndConjugate(sVerb);
});

self.port.on("start", function () {
    self.port.emit("setHeight", document.getElementById("main").offsetTop + document.getElementById("main").offsetHeight + 20);
    document.getElementById("verb").focus();
});

// close
document.getElementById('close').addEventListener("click", function (event) {
    self.port.emit('closePanel');
});

// button
document.getElementById('conjugate').addEventListener("click", function (event) {
    createVerbAndConjugate(document.getElementById('verb').value);
});

// text field
document.getElementById('verb').addEventListener("change", function (event) {
    createVerbAndConjugate(document.getElementById('verb').value);
});

// options
document.getElementById('oneg').addEventListener("click", function (event) {
    _displayResults();
});
document.getElementById('opro').addEventListener("click", function (event) {
    _displayResults();
});
document.getElementById('oint').addEventListener("click", function (event) {
    _displayResults();
});
document.getElementById('ofem').addEventListener("click", function (event) {
    _displayResults();
});
document.getElementById('otco').addEventListener("click", function (event) {
    _displayResults();
});

function createVerbAndConjugate (sVerb) {
    try {
        document.getElementById('oneg').checked = false;
        document.getElementById('opro').checked = false;
        document.getElementById('oint').checked = false;
        document.getElementById('otco').checked = false;
        document.getElementById('ofem').checked = false;
        document.getElementById('smallnote').hidden = true;

        // request analyzing
        sVerb = sVerb.trim().toLowerCase().replace(/’/g, "'").replace(/  +/g, " ");
        if (sVerb) {
            if (sVerb.startsWith("ne pas ")) {
                document.getElementById('oneg').checked = true;
                sVerb = sVerb.slice(7);
            }
            if (sVerb.startsWith("se ")) {
                document.getElementById('opro').checked = true;
                sVerb = sVerb.slice(3);
            } else if (sVerb.startsWith("s'")) {
                document.getElementById('opro').checked = true;
                sVerb = sVerb.slice(2);
            }
            if (sVerb.endsWith("?")) {
                document.getElementById('oint').checked = true;
                sVerb = sVerb.slice(0,-1).trim();
            }

            if (!conj.isVerb(sVerb)) {
                document.getElementById('verb').style = "color: #BB4411;";
            } else {
                self.port.emit("show");
                document.getElementById('verb_title').textContent = sVerb;
                document.getElementById('verb').style = "color: #999999;";
                document.getElementById('verb').value = "";
                oVerb = new Verb(sVerb);
                let sRawInfo = oVerb._sRawInfo;
                document.getElementById('info').textContent = oVerb.sInfo;
                document.getElementById('opro').textContent = "pronominal";
                if (sRawInfo.endsWith("zz")) {
                    document.getElementById('opro').checked = false;
                    document.getElementById('opro').disabled = true;
                    document.getElementById('opro_lbl').style = "color: #CCC;";
                    document.getElementById('otco').checked = false;
                    document.getElementById('otco').disabled = true;
                    document.getElementById('otco_lbl').style = "color: #CCC;";
                    document.getElementById('smallnote').hidden = false;
                } else {
                    if (sRawInfo[5] == "_") {
                        document.getElementById('opro').checked = false;
                        document.getElementById('opro').disabled = true;
                        document.getElementById('opro_lbl').style = "color: #CCC;";
                    } else if (["q", "u", "v", "e"].includes(sRawInfo[5])) {
                        document.getElementById('opro').checked = false;
                        document.getElementById('opro').disabled = false;
                        document.getElementById('opro_lbl').style = "color: #000;";
                    } else if (sRawInfo[5] == "p" || sRawInfo[5] == "r") {
                        document.getElementById('opro').checked = true;
                        document.getElementById('opro').disabled = true;
                        document.getElementById('opro_lbl').style = "color: #CCC;";
                    } else if (sRawInfo[5] == "x") {
                        document.getElementById('opro').textContent = "cas particuliers";
                        document.getElementById('opro').checked = false;
                        document.getElementById('opro').disabled = true;
                        document.getElementById('opro_lbl').style = "color: #CCC;";
                    } else {
                        document.getElementById('opro').textContent = "# erreur #";
                        document.getElementById('opro').checked = false;
                        document.getElementById('opro').disabled = true;
                        document.getElementById('opro_lbl').style = "color: #CCC;";
                    }
                    document.getElementById('otco').disabled = false;
                    document.getElementById('otco_lbl').style = "color: #000;";
                }
                _displayResults();
            }
        }
    }
    catch (e) {
        console.error("\n" + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
    }
}

function _displayResults () {
    if (oVerb === null) {
        return;
    }
    try {
    	let opro = document.getElementById('opro').checked;
    	let oneg = document.getElementById('oneg').checked;
    	let otco = document.getElementById('otco').checked;
    	let oint = document.getElementById('oint').checked;
    	let ofem = document.getElementById('ofem').checked;
        // titles
        _setTitles()
        // participes passés
        document.getElementById('ppas1').textContent = oVerb.participePasse(":Q1") || " "; // something or nbsp
        document.getElementById('ppas2').textContent = oVerb.participePasse(":Q2") || " ";
        document.getElementById('ppas3').textContent = oVerb.participePasse(":Q3") || " ";
        document.getElementById('ppas4').textContent = oVerb.participePasse(":Q4") || " ";
        // infinitif
        document.getElementById('infi').textContent = oVerb.infinitif(opro, oneg, otco, oint, ofem);
        // participe présent
        document.getElementById('ppre').textContent = oVerb.participePresent(opro, oneg, otco, oint, ofem) || " ";
        // conjugaisons
        document.getElementById('ipre1').textContent = oVerb.conjugue(":Ip", ":1s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ipre2').textContent = oVerb.conjugue(":Ip", ":2s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ipre3').textContent = oVerb.conjugue(":Ip", ":3s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ipre4').textContent = oVerb.conjugue(":Ip", ":1p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ipre5').textContent = oVerb.conjugue(":Ip", ":2p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ipre6').textContent = oVerb.conjugue(":Ip", ":3p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('iimp1').textContent = oVerb.conjugue(":Iq", ":1s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('iimp2').textContent = oVerb.conjugue(":Iq", ":2s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('iimp3').textContent = oVerb.conjugue(":Iq", ":3s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('iimp4').textContent = oVerb.conjugue(":Iq", ":1p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('iimp5').textContent = oVerb.conjugue(":Iq", ":2p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('iimp6').textContent = oVerb.conjugue(":Iq", ":3p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ipsi1').textContent = oVerb.conjugue(":Is", ":1s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ipsi2').textContent = oVerb.conjugue(":Is", ":2s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ipsi3').textContent = oVerb.conjugue(":Is", ":3s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ipsi4').textContent = oVerb.conjugue(":Is", ":1p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ipsi5').textContent = oVerb.conjugue(":Is", ":2p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ipsi6').textContent = oVerb.conjugue(":Is", ":3p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ifut1').textContent = oVerb.conjugue(":If", ":1s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ifut2').textContent = oVerb.conjugue(":If", ":2s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ifut3').textContent = oVerb.conjugue(":If", ":3s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ifut4').textContent = oVerb.conjugue(":If", ":1p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ifut5').textContent = oVerb.conjugue(":If", ":2p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('ifut6').textContent = oVerb.conjugue(":If", ":3p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('conda1').textContent = oVerb.conjugue(":K", ":1s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('conda2').textContent = oVerb.conjugue(":K", ":2s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('conda3').textContent = oVerb.conjugue(":K", ":3s", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('conda4').textContent = oVerb.conjugue(":K", ":1p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('conda5').textContent = oVerb.conjugue(":K", ":2p", opro, oneg, otco, oint, ofem) || " ";
        document.getElementById('conda6').textContent = oVerb.conjugue(":K", ":3p", opro, oneg, otco, oint, ofem) || " ";
        if (!oint) {
            document.getElementById('spre1').textContent = oVerb.conjugue(":Sp", ":1s", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('spre2').textContent = oVerb.conjugue(":Sp", ":2s", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('spre3').textContent = oVerb.conjugue(":Sp", ":3s", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('spre4').textContent = oVerb.conjugue(":Sp", ":1p", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('spre5').textContent = oVerb.conjugue(":Sp", ":2p", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('spre6').textContent = oVerb.conjugue(":Sp", ":3p", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('simp1').textContent = oVerb.conjugue(":Sq", ":1s", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('simp2').textContent = oVerb.conjugue(":Sq", ":2s", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('simp3').textContent = oVerb.conjugue(":Sq", ":3s", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('simp4').textContent = oVerb.conjugue(":Sq", ":1p", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('simp5').textContent = oVerb.conjugue(":Sq", ":2p", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('simp6').textContent = oVerb.conjugue(":Sq", ":3p", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('impe1').textContent = oVerb.imperatif(":2s", opro, oneg, otco, ofem) || " ";
            document.getElementById('impe2').textContent = oVerb.imperatif(":1p", opro, oneg, otco, ofem) || " ";
            document.getElementById('impe3').textContent = oVerb.imperatif(":2p", opro, oneg, otco, ofem) || " ";
        } else {
            document.getElementById('spre_temps').textContent = " ";
            document.getElementById('spre1').textContent = " ";
            document.getElementById('spre2').textContent = " ";
            document.getElementById('spre3').textContent = " ";
            document.getElementById('spre4').textContent = " ";
            document.getElementById('spre5').textContent = " ";
            document.getElementById('spre6').textContent = " ";
            document.getElementById('simp_temps').textContent = " ";
            document.getElementById('simp1').textContent = " ";
            document.getElementById('simp2').textContent = " ";
            document.getElementById('simp3').textContent = " ";
            document.getElementById('simp4').textContent = " ";
            document.getElementById('simp5').textContent = " ";
            document.getElementById('simp6').textContent = " ";
            document.getElementById('impe_temps').textContent = " ";
            document.getElementById('impe1').textContent = " ";
            document.getElementById('impe2').textContent = " ";
            document.getElementById('impe3').textContent = " ";
        }
        if (otco) {
            document.getElementById('condb1').textContent = oVerb.conjugue(":Sq", ":1s", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('condb2').textContent = oVerb.conjugue(":Sq", ":2s", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('condb3').textContent = oVerb.conjugue(":Sq", ":3s", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('condb4').textContent = oVerb.conjugue(":Sq", ":1p", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('condb5').textContent = oVerb.conjugue(":Sq", ":2p", opro, oneg, otco, oint, ofem) || " ";
            document.getElementById('condb6').textContent = oVerb.conjugue(":Sq", ":3p", opro, oneg, otco, oint, ofem) || " ";
        } else {
            document.getElementById('condb1').textContent = " ";
            document.getElementById('condb2').textContent = " ";
            document.getElementById('condb3').textContent = " ";
            document.getElementById('condb4').textContent = " ";
            document.getElementById('condb5').textContent = " ";
            document.getElementById('condb6').textContent = " ";
        }
        document.getElementById('verb').Text = "";
    }
    catch (e) {
        console.error("\n" + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
    }
}

function _setTitles () {
    try {
        if (!document.getElementById('otco').checked) {
            document.getElementById('ipre_temps').textContent = "Présent";
            document.getElementById('ifut_temps').textContent = "Futur";
            document.getElementById('iimp_temps').textContent = "Imparfait";
            document.getElementById('ipsi_temps').textContent = "Passé simple";
            document.getElementById('spre_temps').textContent = "Présent";
            document.getElementById('simp_temps').textContent = "Imparfait";
            document.getElementById('conda_temps').textContent = "Présent";
            document.getElementById('condb_temps').textContent = " ";
            document.getElementById('impe_temps').textContent = "Présent";
        } else {
            document.getElementById('ipre_temps').textContent = "Passé composé";
            document.getElementById('ifut_temps').textContent = "Futur antérieur";
            document.getElementById('iimp_temps').textContent = "Plus-que-parfait";
            document.getElementById('ipsi_temps').textContent = "Passé antérieur";
            document.getElementById('spre_temps').textContent = "Passé";
            document.getElementById('simp_temps').textContent = "Plus-que-parfait";
            document.getElementById('conda_temps').textContent = "Passé (1ʳᵉ forme)";
            document.getElementById('condb_temps').textContent = "Passé (2ᵉ forme)";
            document.getElementById('impe_temps').textContent = "Passé";
        }
    }
    catch (e) {
        console.error("\n" + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
    }
}
