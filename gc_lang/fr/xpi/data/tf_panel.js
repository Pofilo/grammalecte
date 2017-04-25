// JavaScript


/*
    Events
*/
self.port.on("receiveTextToFormat", function (sText) {
    self.port.emit("applyFormattedText", applyOptions(sText));
});

self.port.on("start", function (sTFOptions) {
    self.port.emit("setHeight", document.getElementById("actions").offsetTop + document.getElementById("actions").offsetHeight);
    if (sTFOptions !== "") {
        setOptionsInPanel(JSON.parse(sTFOptions));
    } else {
        reset();
    }
    resetProgressBar();
    document.getElementById('apply').focus();
});

document.getElementById('close').addEventListener("click", function (event) {
    self.port.emit('closePanel');
});

document.getElementById('reset').addEventListener("click", function (event) {
    reset();
});

document.getElementById('apply').addEventListener("click", function (event) {
    saveOptions();
    self.port.emit("getTextToFormat");
});

window.addEventListener("click", function (xEvent) {
    let xElem = xEvent.target;
    if (xElem.id) {
        if (xElem.id.startsWith("resize")) {
            self.port.emit("resize", xElem.id, 10);
        } else if (xElem.id.startsWith("o_group_")) {
            switchGroup(xElem.id);
            resetProgressBar();
        }
    }
}, false);


/*
    Actions
*/
function switchGroup (sOptName) {
    if (document.getElementById(sOptName).checked) {
        document.getElementById(sOptName.slice(2)).style.opacity = 1;
    } else {
        document.getElementById(sOptName.slice(2)).style.opacity = 0.3;
    }
}

function reset () {
    resetProgressBar();
    for (let xNode of document.getElementsByClassName("option")) {
        xNode.checked = (xNode.dataset.default === "true");
        if (xNode.id.startsWith("o_group_")) {
            switchGroup(xNode.id);
        }
    }
}

function resetProgressBar () {
    document.getElementById('progressbar').value = 0;
    document.getElementById('time_res').textContent = "";
}

function setOptionsInPanel (oOptions) {
    for (let sOptName in oOptions) {
        //console.log(sOptName + ":" + oOptions[sOptName]);
        if (document.getElementById(sOptName) !== null) {
            document.getElementById(sOptName).checked = oOptions[sOptName];
            if (sOptName.startsWith("o_group_")) {
                switchGroup(sOptName);
            } 
            if (document.getElementById("res_"+sOptName) !== null) {
                document.getElementById("res_"+sOptName).textContent = "";
            }
        }
    }
}

function saveOptions () {
    let oOptions = {};
    for (let xNode of document.getElementsByClassName("option")) {
        oOptions[xNode.id] = xNode.checked;
    }
    self.port.emit("saveOptions", JSON.stringify(oOptions));
}

function applyOptions (sText) {
    try {
        const t0 = Date.now();
        //window.setCursor("wait"); // change pointer
        resetProgressBar();
        document.getElementById('progressbar').max = 7;
        let n1 = 0, n2 = 0, n3 = 0, n4 = 0, n5 = 0, n6 = 0, n7 = 0;
        
        // Restructuration
        if (document.getElementById("o_group_struct").checked) {
            if (document.getElementById("o_remove_hyphens_at_end_of_paragraphs").checked) {
                [sText, n1] = removeHyphenAtEndOfParagraphs(sText);
                document.getElementById('res_o_remove_hyphens_at_end_of_paragraphs').textContent = n1;
            }
            if (document.getElementById("o_merge_contiguous_paragraphs").checked) {
                [sText, n1] = mergeContiguousParagraphs(sText);
                document.getElementById('res_o_merge_contiguous_paragraphs').textContent = n1;
            }
            document.getElementById("o_group_struct").checked = false;
            switchGroup("o_group_struct");
        }
        document.getElementById('progressbar').value = 1;

        // espaces surnuméraires
        if (document.getElementById("o_group_ssp").checked) {
            if (document.getElementById("o_end_of_paragraph").checked) {
                [sText, n1] = formatText(sText, "end_of_paragraph");
                document.getElementById('res_o_end_of_paragraph').textContent = n1;
            }
            if (document.getElementById("o_between_words").checked) {
                [sText, n1] = formatText(sText, "between_words");
                document.getElementById('res_o_between_words').textContent = n1;
            }
            if (document.getElementById("o_start_of_paragraph").checked) {
                [sText, n1] = formatText(sText, "start_of_paragraph");
                document.getElementById('res_o_start_of_paragraph').textContent = n1;
            }
            if (document.getElementById("o_before_punctuation").checked) {
                [sText, n1] = formatText(sText, "before_punctuation");
                document.getElementById('res_o_before_punctuation').textContent = n1;
            }
            if (document.getElementById("o_within_parenthesis").checked) {
                [sText, n1] = formatText(sText, "within_parenthesis");
                document.getElementById('res_o_within_parenthesis').textContent = n1;
            }
            if (document.getElementById("o_within_square_brackets").checked) {
                [sText, n1] = formatText(sText, "within_square_brackets");
                document.getElementById('res_o_within_square_brackets').textContent = n1;
            }
            if (document.getElementById("o_within_quotation_marks").checked) {
                [sText, n1] = formatText(sText, "within_quotation_marks");
                document.getElementById('res_o_within_quotation_marks').textContent = n1;
            }
            document.getElementById("o_group_ssp").checked = false;
            switchGroup("o_group_ssp");
        }
        document.getElementById('progressbar').value = 2;

        // espaces typographiques
        if (document.getElementById("o_group_nbsp").checked) {
            if (document.getElementById("o_nbsp_before_punctuation").checked) {
                [sText, n1] = formatText(sText, "nbsp_before_punctuation");
                [sText, n2] = formatText(sText, "nbsp_repair");
                document.getElementById('res_o_nbsp_before_punctuation').textContent = n1 - n2;
            }
            if (document.getElementById("o_nbsp_within_quotation_marks").checked) {
                [sText, n1] = formatText(sText, "nbsp_within_quotation_marks");
                document.getElementById('res_o_nbsp_within_quotation_marks').textContent = n1;
            }
            if (document.getElementById("o_nbsp_before_symbol").checked) {
                [sText, n1] = formatText(sText, "nbsp_before_symbol");
                document.getElementById('res_o_nbsp_before_symbol').textContent = n1;
            }
            if (document.getElementById("o_nbsp_within_numbers").checked) {
                [sText, n1] = formatText(sText, "nbsp_within_numbers");
                document.getElementById('res_o_nbsp_within_numbers').textContent = n1;
            }
            if (document.getElementById("o_nbsp_before_units").checked) {
                [sText, n1] = formatText(sText, "nbsp_before_units");
                document.getElementById('res_o_nbsp_before_units').textContent = n1;
            }
            document.getElementById("o_group_nbsp").checked = false;
            switchGroup("o_group_nbsp");
        }
        document.getElementById('progressbar').value = 3;

        // espaces manquants
        if (document.getElementById("o_group_typo").checked) {
            if (document.getElementById("o_ts_units").checked) {
                [sText, n1] = formatText(sText, "ts_units");
                document.getElementById('res_o_ts_units').textContent = n1;
            }
        }
        if (document.getElementById("o_group_space").checked) {
            if (document.getElementById("o_add_space_after_punctuation").checked) {
                [sText, n1] = formatText(sText, "add_space_after_punctuation");
                [sText, n2] = formatText(sText, "add_space_repair");
                document.getElementById('res_o_add_space_after_punctuation').textContent = n1 - n2;
            }
            if (document.getElementById("o_add_space_around_hyphens").checked) {
                [sText, n1] = formatText(sText, "add_space_around_hyphens");
                document.getElementById('res_o_add_space_around_hyphens').textContent = n1;
            }
            document.getElementById("o_group_space").checked = false;
            switchGroup("o_group_space");
        }
        document.getElementById('progressbar').value = 4;

        // suppression
        if (document.getElementById("o_group_delete").checked) {
            if (document.getElementById("o_erase_non_breaking_hyphens").checked) {
                [sText, n1] = formatText(sText, "erase_non_breaking_hyphens");
                document.getElementById('res_o_erase_non_breaking_hyphens').textContent = n1;
            }
            document.getElementById("o_group_delete").checked = false;
            switchGroup("o_group_delete");
        }
        document.getElementById('progressbar').value = 5;

        // signes typographiques
        if (document.getElementById("o_group_typo").checked) {
            if (document.getElementById("o_ts_apostrophe").checked) {
                [sText, n1] = formatText(sText, "ts_apostrophe");
                document.getElementById('res_o_ts_apostrophe').textContent = n1;
            }
            if (document.getElementById("o_ts_ellipsis").checked) {
                [sText, n1] = formatText(sText, "ts_ellipsis");
                document.getElementById('res_o_ts_ellipsis').textContent = n1;
            }
            if (document.getElementById("o_ts_dash_start").checked) {
                if (document.getElementById("o_ts_m_dash_start").checked) {
                    [sText, n1] = formatText(sText, "ts_m_dash_start");
                } else {
                    [sText, n1] = formatText(sText, "ts_n_dash_start");
                }
                document.getElementById('res_o_ts_dash_start').textContent = n1;
            }
            if (document.getElementById("o_ts_dash_middle").checked) {
                if (document.getElementById("o_ts_m_dash_middle").checked) {
                    [sText, n1] = formatText(sText, "ts_m_dash_middle");
                } else {
                    [sText, n1] = formatText(sText, "ts_n_dash_middle");
                }
                document.getElementById('res_o_ts_dash_middle').textContent = n1;
            }
            if (document.getElementById("o_ts_quotation_marks").checked) {
                [sText, n1] = formatText(sText, "ts_quotation_marks");
                document.getElementById('res_o_ts_quotation_marks').textContent = n1;
            }
            if (document.getElementById("o_ts_spell").checked) {
                [sText, n1] = formatText(sText, "ts_spell");
                document.getElementById('res_o_ts_spell').textContent = n1;
            }
            if (document.getElementById("o_ts_ligature").checked) {
                // ligatures typographiques : fi, fl, ff, ffi, ffl, ft, st
                if (document.getElementById("o_ts_ligature_do").checked) {
                    if (document.getElementById("o_ts_ligature_ffi").checked) {
                        [sText, n1] = formatText(sText, "ts_ligature_ffi_do");
                    }
                    if (document.getElementById("o_ts_ligature_ffl").checked) {
                        [sText, n2] = formatText(sText, "ts_ligature_ffl_do");
                    }
                    if (document.getElementById("o_ts_ligature_fi").checked) {
                        [sText, n3] = formatText(sText, "ts_ligature_fi_do");
                    }
                    if (document.getElementById("o_ts_ligature_fl").checked) {
                        [sText, n4] = formatText(sText, "ts_ligature_fl_do");
                    }
                    if (document.getElementById("o_ts_ligature_ff").checked) {
                        [sText, n5] = formatText(sText, "ts_ligature_ff_do");
                    }
                    if (document.getElementById("o_ts_ligature_ft").checked) {
                        [sText, n6] = formatText(sText, "ts_ligature_ft_do");
                    }
                    if (document.getElementById("o_ts_ligature_st").checked) {
                        [sText, n7] = formatText(sText, "ts_ligature_st_do");
                    }
                }
                if (document.getElementById("o_ts_ligature_undo").checked) {
                    if (document.getElementById("o_ts_ligature_ffi").checked) {
                        [sText, n1] = formatText(sText, "ts_ligature_ffi_undo");
                    }
                    if (document.getElementById("o_ts_ligature_ffl").checked) {
                        [sText, n2] = formatText(sText, "ts_ligature_ffl_undo");
                    }
                    if (document.getElementById("o_ts_ligature_fi").checked) {
                        [sText, n3] = formatText(sText, "ts_ligature_fi_undo");
                    }
                    if (document.getElementById("o_ts_ligature_fl").checked) {
                        [sText, n4] = formatText(sText, "ts_ligature_fl_undo");
                    }
                    if (document.getElementById("o_ts_ligature_ff").checked) {
                        [sText, n5] = formatText(sText, "ts_ligature_ff_undo");
                    }
                    if (document.getElementById("o_ts_ligature_ft").checked) {
                        [sText, n6] = formatText(sText, "ts_ligature_ft_undo");
                    }
                    if (document.getElementById("o_ts_ligature_st").checked) {
                        [sText, n7] = formatText(sText, "ts_ligature_st_undo");
                    }
                }
                document.getElementById('res_o_ts_ligature').textContent = n1 + n2 + n3 + n4 + n5 + n6 + n7;
            }
            document.getElementById("o_group_typo").checked = false;
            switchGroup("o_group_typo");
        }
        document.getElementById('progressbar').value = 6;

        // divers
        if (document.getElementById("o_group_misc").checked) {
            if (document.getElementById("o_ordinals_no_exponant").checked) {
                if (document.getElementById("o_ordinals_exponant").checked) {
                    [sText, n1] = formatText(sText, "ordinals_exponant");
                } else {
                    [sText, n1] = formatText(sText, "ordinals_no_exponant");
                }
                document.getElementById('res_o_ordinals_no_exponant').textContent = n1;
            }
            if (document.getElementById("o_etc").checked) {
                [sText, n1] = formatText(sText, "etc");
                document.getElementById('res_o_etc').textContent = n1;
            }
            if (document.getElementById("o_missing_hyphens").checked) {
                [sText, n1] = formatText(sText, "missing_hyphens");
                document.getElementById('res_o_missing_hyphens').textContent = n1;
            }
            if (document.getElementById("o_ma_word").checked) {
                [sText, n1] = formatText(sText, "ma_word");
                if (document.getElementById("o_ma_1letter_lowercase").checked) {
                    [sText, n1] = formatText(sText, "ma_1letter_lowercase");
                    if (document.getElementById("o_ma_1letter_uppercase").checked) {
                        [sText, n1] = formatText(sText, "ma_1letter_uppercase");
                    }
                }
                document.getElementById('res_o_ma_word').textContent = n1;
            }
            document.getElementById("o_group_misc").checked = false;
            switchGroup("o_group_misc");
        }
        document.getElementById('progressbar').value = document.getElementById('progressbar').max;
        // end of processing

        //window.setCursor("auto"); // restore pointer

        const t1 = Date.now();
        document.getElementById('time_res').textContent = this.getTimeRes((t1-t0)/1000);
    }
    catch (e) {
        console.error("\n" + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
    }
    return sText;
}

function formatText (sText, sOptName) {
    let nCount = 0;
    try {
        if (!oReplTable.hasOwnProperty(sOptName)) {
            console.log("# Error. TF: there is no option “" + sOptName+ "”.");
            return [sText, nCount];
        }
        for (let [zRgx, sRep] of oReplTable[sOptName]) {
            nCount += (sText.match(zRgx) || []).length;
            sText = sText.replace(zRgx, sRep);
        }
        document.getElementById('progressbar').value += 1;
    }
    catch (e) {
        console.error("\n" + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
    }
    return [sText, nCount];
};

function removeHyphenAtEndOfParagraphs (sText) {
    let nCount = (sText.match(/-[  ]*\n/gm) || []).length;
    sText = sText.replace(/-[  ]*\n/gm, "");
    /*
    sText = sText.replace(/-[  ]+$/gm, "-"); // remove spaces at end of paragraphs if - is the last character
    let m = null;
    let zRegExp = /([a-zA-Zà-ö0-9À-Öø-ÿØ-ßĀ-ʯ]+)-\n([a-zA-Zà-ö0-9À-Öø-ÿØ-ßĀ-ʯ]+)/g;
    while ((m = zRegExp.exec(sText)) !== null) {
        console.log("+");
        sText = sText.slice(0, m.index) + m[1] + m[2] + sText.slice(RegExp.lastIndex);
    }*/
    return [sText, nCount];
}

function mergeContiguousParagraphs (sText) {
    let nCount = 0;
    sText = sText.replace(/^[  ]+$/gm, ""); // clear empty paragraphs
    let s = "";
    for (let sParagraph of getParagraph(sText)) {
        if (sParagraph === "") {
            s += "\n";
        } else {
            s += sParagraph + " ";
            nCount += 1;
        }
    }
    s = s.replace(/  +/g, " ").replace(/ $/gm, "");
    return [s, nCount];
}

function* getParagraph (sText) {
    // generator: returns paragraphs of text
    let iStart = 0;
    let iEnd = 0;
    while ((iEnd = sText.indexOf("\n", iStart)) !== -1) {
        yield sText.slice(iStart, iEnd);
        iStart = iEnd + 1;
    }
    yield sText.slice(iStart);
}

function getTimeRes (n) {
    // returns duration in seconds as string
    if (n < 10) {
        return n.toFixed(3).toString() + " s";
    }
    if (n < 100) {
        return n.toFixed(2).toString() + " s";
    }
    if (n < 1000) {
        return n.toFixed(1).toString() + " s";
    }
    return n.toFixed().toString() + " s";
}
