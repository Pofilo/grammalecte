// JavaScript
// Text formatter

"use strict";


class GrammalecteTextFormatter extends GrammalectePanel {

    constructor (...args) {
        super(...args);
        this.xTFNode = this._createTextFormatter();
        this.xPanelContent.appendChild(this.xTFNode);
        this.xTextArea = null;
    }

    _createTextFormatter () {
        let xTFNode = document.createElement("div");
        try {
            // Options
            let xOptions = createNode("div", {id: "grammalecte_tf_options"});
            let xColumn1 = createNode("div", {className: "grammalecte_tf_column"});
            let xSSP = this._createFieldset("group_ssp", true, "Espaces surnuméraires");
            xSSP.appendChild(this._createSimpleOption("o_start_of_paragraph", true, "En début de paragraphe"));
            xSSP.appendChild(this._createSimpleOption("o_end_of_paragraph", true, "En fin de paragraphe"));
            xSSP.appendChild(this._createSimpleOption("o_between_words", true, "Entre les mots"));
            xSSP.appendChild(this._createSimpleOption("o_before_punctuation", true, "Avant les points (.), les virgules (,)"));
            xSSP.appendChild(this._createSimpleOption("o_within_parenthesis", true, "À l’intérieur des parenthèses"));
            xSSP.appendChild(this._createSimpleOption("o_within_square_brackets", true, "À l’intérieur des crochets"));
            xSSP.appendChild(this._createSimpleOption("o_within_quotation_marks", true, "À l’intérieur des guillemets “ et ”"));
            let xSpace = this._createFieldset("group_space", true, "Espaces manquants");
            xSpace.appendChild(this._createSimpleOption("o_add_space_after_punctuation", true, "Après , ; : ? ! . …"));
            xSpace.appendChild(this._createSimpleOption("o_add_space_around_hyphens", true, "Autour des tirets d’incise"));
            let xNBSP = this._createFieldset("group_nbsp", true, "Espaces insécables");
            xNBSP.appendChild(this._createSimpleOption("o_nbsp_before_punctuation", true, "Avant : ; ? et !"));
            xNBSP.appendChild(this._createSimpleOption("o_nbsp_within_quotation_marks", true, "Avec les guillemets « et »"));
            xNBSP.appendChild(this._createSimpleOption("o_nbsp_before_symbol", true, "Avant % ‰ € $ £ ¥ ˚C"));
            xNBSP.appendChild(this._createSimpleOption("o_nbsp_within_numbers", true, "À l’intérieur des nombres"));
            xNBSP.appendChild(this._createSimpleOption("o_nbsp_before_units", true, "Avant les unités de mesure"));
            let xDelete = this._createFieldset("group_delete", true, "Suppressions");
            xDelete.appendChild(this._createSimpleOption("o_erase_non_breaking_hyphens", true, "Tirets conditionnels"));
            let xColumn2 = createNode("div", {className: "grammalecte_tf_column"});
            let xTypo = this._createFieldset("group_typo", true, "Signes typographiques");
            xTypo.appendChild(this._createSimpleOption("o_ts_apostrophe", true, "Apostrophe (’)"));
            xTypo.appendChild(this._createSimpleOption("o_ts_ellipsis", true, "Points de suspension (…)"));
            xTypo.appendChild(this._createSimpleOption("o_ts_dash_middle", true, "Tirets d’incise :"));
            xTypo.appendChild(this._createRadioBoxHyphens("hyphen1", "o_ts_m_dash_middle", "o_ts_n_dash_middle", false));
            xTypo.appendChild(this._createSimpleOption("o_ts_dash_start", true, "Tirets en début de paragraphe :"));
            xTypo.appendChild(this._createRadioBoxHyphens("hyphen2", "o_ts_m_dash_start", "o_ts_n_dash_start", true));
            xTypo.appendChild(this._createSimpleOption("o_ts_quotation_marks", true, "Modifier les guillemets droits (\" et ')"));
            xTypo.appendChild(this._createSimpleOption("o_ts_units", true, "Points médians des unités (N·m, Ω·m…)"));
            xTypo.appendChild(this._createSimpleOption("o_ts_spell", true, "Ligatures (cœur…) et diacritiques (ça, État…)"));
            xTypo.appendChild(this._createRadioBoxLigatures());
            xTypo.appendChild(this._createLigaturesSelection());
            let xMisc = this._createFieldset("group_misc", true, "Divers");
            xMisc.appendChild(this._createOrdinalOptions());
            xMisc.appendChild(this._createSimpleOption("o_etc", true, "Et cætera, etc."));
            xMisc.appendChild(this._createSimpleOption("o_missing_hyphens", true, "Traits d’union manquants"));
            xMisc.appendChild(this._createSimpleOption("o_ma_word", true, "Apostrophes manquantes"));
            xMisc.appendChild(this._createSingleLetterOptions());
            let xStruct = this._createFieldset("group_struct", false, "Restructuration [!]");
            xStruct.appendChild(this._createSimpleOption("o_remove_hyphens_at_end_of_paragraphs", false, "Enlever césures en fin de ligne/paragraphe [!]"));
            xStruct.appendChild(this._createSimpleOption("o_merge_contiguous_paragraphs", false, "Fusionner les paragraphes contigus [!]"));
            xColumn1.appendChild(xSSP);
            xColumn1.appendChild(xSpace);
            xColumn1.appendChild(xNBSP);
            xColumn1.appendChild(xDelete);
            xColumn2.appendChild(xTypo);
            xColumn2.appendChild(xMisc);
            xColumn2.appendChild(xStruct);
            xOptions.appendChild(xColumn1);
            xOptions.appendChild(xColumn2);
            // Actions
            let xActions = createNode("div", {id: "grammalecte_tf_actions"});
            let xDefaultButton = createNode("div", {id: "grammalecte_tf_reset", textContent: "Par défaut", className: "grammalecte_button"});
            xDefaultButton.addEventListener("click", () => { this.reset(); });
            let xApplyButton = createNode("div", {id: "grammalecte_tf_apply", textContent: "Appliquer", className: "grammalecte_button"});
            xApplyButton.addEventListener("click", () => { this.saveOptions(); this.apply(); });
            xActions.appendChild(xDefaultButton);
            xActions.appendChild(createNode("progress", {id: "grammalecte_tf_progressbar"}));
            xActions.appendChild(createNode("span", {id: "grammalecte_tf_time_res", textContent: "…"}));
            xActions.appendChild(xApplyButton);
            //xActions.appendChild(createNode("div", {id: "grammalecte_infomsg", textContent: "blabla"}));
            // create result
            xTFNode.appendChild(xOptions);
            xTFNode.appendChild(xActions);
        }
        catch (e) {
            showError(e);
        }
        return xTFNode;
    }

    // Common options
    _createFieldset (sId, bDefault, sLabel) {
        let xFieldset = createNode("fieldset", {id: sId, className: "groupblock"});
        let xLegend = document.createElement("legend");
        let xGroupOption = createNode("input", {type: "checkbox", id: "o_"+sId, className: "option"}, {default: bDefault});
        xGroupOption.addEventListener("click", (xEvent) => { this.switchGroup(xEvent.target.id); });
        xLegend.appendChild(xGroupOption);
        xLegend.appendChild(createNode("label", {htmlFor: "o_"+sId, textContent: sLabel}));
        xFieldset.appendChild(xLegend);
        return xFieldset;
    }

    _createSimpleOption (sId, bDefault, sLabel) {
        let xLine = createNode("div", {className: "blockopt underline"});
        xLine.appendChild(createNode("input", {type: "checkbox", id: sId, className: "option"}, {default: bDefault}));
        xLine.appendChild(createNode("label", {htmlFor: sId, textContent: sLabel, className: "opt_lbl largew"}));
        xLine.appendChild(createNode("div", {id: "res_"+sId, className: "grammalecte_tf_result", textContent: "·"}));
        return xLine;
    }

    // Hyphens
    _createRadioBoxHyphens (sName, sIdEmDash, sIdEnDash, bDefaultEmDash) {
        let xLine = createNode("div", {className: "blockopt indent"});
        xLine.appendChild(this._createInlineRadioOption(sName, sIdEmDash, "cadratin (—)", bDefaultEmDash));
        xLine.appendChild(this._createInlineRadioOption(sName, sIdEnDash, "demi-cadratin (—)", !bDefaultEmDash));
        return xLine;
    }

    // Ligatures
    _createRadioBoxLigatures () {
        let xLine = createNode("div", {className: "blockopt underline"});
        xLine.appendChild(createNode("div", {id: "res_"+"o_ts_ligature", className: "grammalecte_tf_result", textContent: "·"}));
        xLine.appendChild(this._createInlineCheckboxOption("o_ts_ligature", "Ligatures", true));
        xLine.appendChild(this._createInlineRadioOption("liga", "o_ts_ligature_do", "faire", false));
        xLine.appendChild(this._createInlineRadioOption("liga", "o_ts_ligature_undo", "défaire", true));
        return xLine;
    }

    _createLigaturesSelection () {
        let xLine = createNode("div", {className: "blockopt indent"});
        xLine.appendChild(this._createInlineCheckboxOption("o_ts_ligature_ff", "ff", true));
        xLine.appendChild(this._createInlineCheckboxOption("o_ts_ligature_fi", "fi", true));
        xLine.appendChild(this._createInlineCheckboxOption("o_ts_ligature_ffi", "ffi", true));
        xLine.appendChild(this._createInlineCheckboxOption("o_ts_ligature_fl", "fl", true));
        xLine.appendChild(this._createInlineCheckboxOption("o_ts_ligature_ffl", "ffl", true));
        xLine.appendChild(this._createInlineCheckboxOption("o_ts_ligature_ft", "ft", true));
        xLine.appendChild(this._createInlineCheckboxOption("o_ts_ligature_st", "st", false));
        return xLine;
    }

    // Apostrophes
    _createSingleLetterOptions () {
        let xLine = createNode("div", {className: "blockopt indent"});
        xLine.appendChild(this._createInlineCheckboxOption("o_ma_1letter_lowercase", "lettres isolées (j’ n’ m’ t’ s’ c’ d’ l’)", false));
        xLine.appendChild(this._createInlineCheckboxOption("o_ma_1letter_uppercase", "Maj.", false));
        return xLine;
    }

    // Ordinals
    _createOrdinalOptions () {
        let xLine = createNode("div", {className: "blockopt underline"});
        xLine.appendChild(createNode("div", {id: "res_"+"o_ordinals_no_exponant", className: "grammalecte_tf_result", textContent: "·"}));
        xLine.appendChild(this._createInlineCheckboxOption("o_ordinals_no_exponant", "Ordinaux (15e, XXIe…)", true));
        xLine.appendChild(this._createInlineCheckboxOption("o_ordinals_exponant", "e → ᵉ", true));
        return xLine;
    }
    

    // Inline option block
    _createInlineCheckboxOption (sId, sLabel, bDefault) {
        let xInlineBlock = createNode("div", {className: "inlineblock"});
        xInlineBlock.appendChild(createNode("input", {type: "checkbox", id: sId, className: "option"}, {default: bDefault}));
        xInlineBlock.appendChild(createNode("label", {htmlFor: sId, textContent: sLabel, className: "opt_lbl"}));
        return xInlineBlock;
    }

    _createInlineRadioOption (sName, sId, sLabel, bDefault) {
        let xInlineBlock = createNode("div", {className: "inlineblock"});
        xInlineBlock.appendChild(createNode("input", {type: "radio", id: sId, name: sName, className:"option"}, {default: bDefault}));
        xInlineBlock.appendChild(createNode("label", {htmlFor: sId, className: "opt_lbl", textContent: sLabel}));
        return xInlineBlock;
    }


    /*
        Actions
    */
    start (xTextArea) {
        this.xTextArea = xTextArea;
        let xPromise = browser.storage.local.get("tf_options");
        xPromise.then(this.setOptions.bind(this), this.reset.bind(this));
    }

    switchGroup (sOptName) {
        if (document.getElementById(sOptName).checked) {
            document.getElementById(sOptName.slice(2)).style.opacity = 1;
        } else {
            document.getElementById(sOptName.slice(2)).style.opacity = 0.3;
        }
        this.resetProgressBar();
    }

    reset () {
        this.resetProgressBar();
        for (let xNode of document.getElementsByClassName("option")) {
            xNode.checked = (xNode.dataset.default === "true");
            if (xNode.id.startsWith("o_group_")) {
                this.switchGroup(xNode.id);
            }
        }
    }

    resetProgressBar () {
        document.getElementById('grammalecte_tf_progressbar').value = 0;
        document.getElementById('grammalecte_tf_time_res').textContent = "";
    }

    setOptions (oOptions) {
        if (oOptions.hasOwnProperty("tf_options")) {
            oOptions = oOptions.tf_options;
        }
        for (let xNode of document.getElementsByClassName("option")) {
            //console.log(xNode.id + " > " + oOptions.hasOwnProperty(xNode.id) + ": " + oOptions[xNode.id] + " [" + xNode.dataset.default + "]");
            xNode.checked = (oOptions.hasOwnProperty(xNode.id)) ? oOptions[xNode.id] : (xNode.dataset.default === "true");
            if (document.getElementById("res_"+xNode.id) !== null) {
                document.getElementById("res_"+xNode.id).textContent = "";
            }
            if (xNode.id.startsWith("o_group_")) {
                this.switchGroup(xNode.id);
            }
        }
    }

    saveOptions () {
        let oOptions = {};
        for (let xNode of document.getElementsByClassName("option")) {
            oOptions[xNode.id] = xNode.checked;
            //console.log(xNode.id + ": " + xNode.checked);
        }
        browser.storage.local.set({"tf_options": oOptions});
    }

    apply () {
        try {
            const t0 = Date.now();
            //window.setCursor("wait"); // change pointer
            this.resetProgressBar();
            let sText = this.xTextArea.value;
            document.getElementById('grammalecte_tf_progressbar').max = 7;
            let n1 = 0, n2 = 0, n3 = 0, n4 = 0, n5 = 0, n6 = 0, n7 = 0;
            
            // Restructuration
            if (document.getElementById("o_group_struct").checked) {
                if (document.getElementById("o_remove_hyphens_at_end_of_paragraphs").checked) {
                    [sText, n1] = this.removeHyphenAtEndOfParagraphs(sText);
                    document.getElementById('res_o_remove_hyphens_at_end_of_paragraphs').textContent = n1;
                }
                if (document.getElementById("o_merge_contiguous_paragraphs").checked) {
                    [sText, n1] = this.mergeContiguousParagraphs(sText);
                    document.getElementById('res_o_merge_contiguous_paragraphs').textContent = n1;
                }
                document.getElementById("o_group_struct").checked = false;
                this.switchGroup("o_group_struct");
            }
            document.getElementById('grammalecte_tf_progressbar').value = 1;

            // espaces surnuméraires
            if (document.getElementById("o_group_ssp").checked) {
                if (document.getElementById("o_end_of_paragraph").checked) {
                    [sText, n1] = this.formatText(sText, "end_of_paragraph");
                    document.getElementById('res_o_end_of_paragraph').textContent = n1;
                }
                if (document.getElementById("o_between_words").checked) {
                    [sText, n1] = this.formatText(sText, "between_words");
                    document.getElementById('res_o_between_words').textContent = n1;
                }
                if (document.getElementById("o_start_of_paragraph").checked) {
                    [sText, n1] = this.formatText(sText, "start_of_paragraph");
                    document.getElementById('res_o_start_of_paragraph').textContent = n1;
                }
                if (document.getElementById("o_before_punctuation").checked) {
                    [sText, n1] = this.formatText(sText, "before_punctuation");
                    document.getElementById('res_o_before_punctuation').textContent = n1;
                }
                if (document.getElementById("o_within_parenthesis").checked) {
                    [sText, n1] = this.formatText(sText, "within_parenthesis");
                    document.getElementById('res_o_within_parenthesis').textContent = n1;
                }
                if (document.getElementById("o_within_square_brackets").checked) {
                    [sText, n1] = this.formatText(sText, "within_square_brackets");
                    document.getElementById('res_o_within_square_brackets').textContent = n1;
                }
                if (document.getElementById("o_within_quotation_marks").checked) {
                    [sText, n1] = this.formatText(sText, "within_quotation_marks");
                    document.getElementById('res_o_within_quotation_marks').textContent = n1;
                }
                document.getElementById("o_group_ssp").checked = false;
                this.switchGroup("o_group_ssp");
            }
            document.getElementById('grammalecte_tf_progressbar').value = 2;

            // espaces typographiques
            if (document.getElementById("o_group_nbsp").checked) {
                if (document.getElementById("o_nbsp_before_punctuation").checked) {
                    [sText, n1] = this.formatText(sText, "nbsp_before_punctuation");
                    [sText, n2] = this.formatText(sText, "nbsp_repair");
                    document.getElementById('res_o_nbsp_before_punctuation').textContent = n1 - n2;
                }
                if (document.getElementById("o_nbsp_within_quotation_marks").checked) {
                    [sText, n1] = this.formatText(sText, "nbsp_within_quotation_marks");
                    document.getElementById('res_o_nbsp_within_quotation_marks').textContent = n1;
                }
                if (document.getElementById("o_nbsp_before_symbol").checked) {
                    [sText, n1] = this.formatText(sText, "nbsp_before_symbol");
                    document.getElementById('res_o_nbsp_before_symbol').textContent = n1;
                }
                if (document.getElementById("o_nbsp_within_numbers").checked) {
                    [sText, n1] = this.formatText(sText, "nbsp_within_numbers");
                    document.getElementById('res_o_nbsp_within_numbers').textContent = n1;
                }
                if (document.getElementById("o_nbsp_before_units").checked) {
                    [sText, n1] = this.formatText(sText, "nbsp_before_units");
                    document.getElementById('res_o_nbsp_before_units').textContent = n1;
                }
                document.getElementById("o_group_nbsp").checked = false;
                this.switchGroup("o_group_nbsp");
            }
            document.getElementById('grammalecte_tf_progressbar').value = 3;

            // espaces manquants
            if (document.getElementById("o_group_typo").checked) {
                if (document.getElementById("o_ts_units").checked) {
                    [sText, n1] = this.formatText(sText, "ts_units");
                    document.getElementById('res_o_ts_units').textContent = n1;
                }
            }
            if (document.getElementById("o_group_space").checked) {
                if (document.getElementById("o_add_space_after_punctuation").checked) {
                    [sText, n1] = this.formatText(sText, "add_space_after_punctuation");
                    [sText, n2] = this.formatText(sText, "add_space_repair");
                    document.getElementById('res_o_add_space_after_punctuation').textContent = n1 - n2;
                }
                if (document.getElementById("o_add_space_around_hyphens").checked) {
                    [sText, n1] = this.formatText(sText, "add_space_around_hyphens");
                    document.getElementById('res_o_add_space_around_hyphens').textContent = n1;
                }
                document.getElementById("o_group_space").checked = false;
                this.switchGroup("o_group_space");
            }
            document.getElementById('grammalecte_tf_progressbar').value = 4;

            // suppression
            if (document.getElementById("o_group_delete").checked) {
                if (document.getElementById("o_erase_non_breaking_hyphens").checked) {
                    [sText, n1] = this.formatText(sText, "erase_non_breaking_hyphens");
                    document.getElementById('res_o_erase_non_breaking_hyphens').textContent = n1;
                }
                document.getElementById("o_group_delete").checked = false;
                this.switchGroup("o_group_delete");
            }
            document.getElementById('grammalecte_tf_progressbar').value = 5;

            // signes typographiques
            if (document.getElementById("o_group_typo").checked) {
                if (document.getElementById("o_ts_apostrophe").checked) {
                    [sText, n1] = this.formatText(sText, "ts_apostrophe");
                    document.getElementById('res_o_ts_apostrophe').textContent = n1;
                }
                if (document.getElementById("o_ts_ellipsis").checked) {
                    [sText, n1] = this.formatText(sText, "ts_ellipsis");
                    document.getElementById('res_o_ts_ellipsis').textContent = n1;
                }
                if (document.getElementById("o_ts_dash_start").checked) {
                    if (document.getElementById("o_ts_m_dash_start").checked) {
                        [sText, n1] = this.formatText(sText, "ts_m_dash_start");
                    } else {
                        [sText, n1] = this.formatText(sText, "ts_n_dash_start");
                    }
                    document.getElementById('res_o_ts_dash_start').textContent = n1;
                }
                if (document.getElementById("o_ts_dash_middle").checked) {
                    if (document.getElementById("o_ts_m_dash_middle").checked) {
                        [sText, n1] = this.formatText(sText, "ts_m_dash_middle");
                    } else {
                        [sText, n1] = this.formatText(sText, "ts_n_dash_middle");
                    }
                    document.getElementById('res_o_ts_dash_middle').textContent = n1;
                }
                if (document.getElementById("o_ts_quotation_marks").checked) {
                    [sText, n1] = this.formatText(sText, "ts_quotation_marks");
                    document.getElementById('res_o_ts_quotation_marks').textContent = n1;
                }
                if (document.getElementById("o_ts_spell").checked) {
                    [sText, n1] = this.formatText(sText, "ts_spell");
                    document.getElementById('res_o_ts_spell').textContent = n1;
                }
                if (document.getElementById("o_ts_ligature").checked) {
                    // ligatures typographiques : fi, fl, ff, ffi, ffl, ft, st
                    if (document.getElementById("o_ts_ligature_do").checked) {
                        if (document.getElementById("o_ts_ligature_ffi").checked) {
                            [sText, n1] = this.formatText(sText, "ts_ligature_ffi_do");
                        }
                        if (document.getElementById("o_ts_ligature_ffl").checked) {
                            [sText, n2] = this.formatText(sText, "ts_ligature_ffl_do");
                        }
                        if (document.getElementById("o_ts_ligature_fi").checked) {
                            [sText, n3] = this.formatText(sText, "ts_ligature_fi_do");
                        }
                        if (document.getElementById("o_ts_ligature_fl").checked) {
                            [sText, n4] = this.formatText(sText, "ts_ligature_fl_do");
                        }
                        if (document.getElementById("o_ts_ligature_ff").checked) {
                            [sText, n5] = this.formatText(sText, "ts_ligature_ff_do");
                        }
                        if (document.getElementById("o_ts_ligature_ft").checked) {
                            [sText, n6] = this.formatText(sText, "ts_ligature_ft_do");
                        }
                        if (document.getElementById("o_ts_ligature_st").checked) {
                            [sText, n7] = this.formatText(sText, "ts_ligature_st_do");
                        }
                    }
                    if (document.getElementById("o_ts_ligature_undo").checked) {
                        if (document.getElementById("o_ts_ligature_ffi").checked) {
                            [sText, n1] = this.formatText(sText, "ts_ligature_ffi_undo");
                        }
                        if (document.getElementById("o_ts_ligature_ffl").checked) {
                            [sText, n2] = this.formatText(sText, "ts_ligature_ffl_undo");
                        }
                        if (document.getElementById("o_ts_ligature_fi").checked) {
                            [sText, n3] = this.formatText(sText, "ts_ligature_fi_undo");
                        }
                        if (document.getElementById("o_ts_ligature_fl").checked) {
                            [sText, n4] = this.formatText(sText, "ts_ligature_fl_undo");
                        }
                        if (document.getElementById("o_ts_ligature_ff").checked) {
                            [sText, n5] = this.formatText(sText, "ts_ligature_ff_undo");
                        }
                        if (document.getElementById("o_ts_ligature_ft").checked) {
                            [sText, n6] = this.formatText(sText, "ts_ligature_ft_undo");
                        }
                        if (document.getElementById("o_ts_ligature_st").checked) {
                            [sText, n7] = this.formatText(sText, "ts_ligature_st_undo");
                        }
                    }
                    document.getElementById('res_o_ts_ligature').textContent = n1 + n2 + n3 + n4 + n5 + n6 + n7;
                }
                document.getElementById("o_group_typo").checked = false;
                this.switchGroup("o_group_typo");
            }
            document.getElementById('grammalecte_tf_progressbar').value = 6;

            // divers
            if (document.getElementById("o_group_misc").checked) {
                if (document.getElementById("o_ordinals_no_exponant").checked) {
                    if (document.getElementById("o_ordinals_exponant").checked) {
                        [sText, n1] = this.formatText(sText, "ordinals_exponant");
                    } else {
                        [sText, n1] = this.formatText(sText, "ordinals_no_exponant");
                    }
                    document.getElementById('res_o_ordinals_no_exponant').textContent = n1;
                }
                if (document.getElementById("o_etc").checked) {
                    [sText, n1] = this.formatText(sText, "etc");
                    document.getElementById('res_o_etc').textContent = n1;
                }
                if (document.getElementById("o_missing_hyphens").checked) {
                    [sText, n1] = this.formatText(sText, "missing_hyphens");
                    document.getElementById('res_o_missing_hyphens').textContent = n1;
                }
                if (document.getElementById("o_ma_word").checked) {
                    [sText, n1] = this.formatText(sText, "ma_word");
                    if (document.getElementById("o_ma_1letter_lowercase").checked) {
                        [sText, n1] = this.formatText(sText, "ma_1letter_lowercase");
                        if (document.getElementById("o_ma_1letter_uppercase").checked) {
                            [sText, n1] = this.formatText(sText, "ma_1letter_uppercase");
                        }
                    }
                    document.getElementById('res_o_ma_word').textContent = n1;
                }
                document.getElementById("o_group_misc").checked = false;
                this.switchGroup("o_group_misc");
            }
            document.getElementById('grammalecte_tf_progressbar').value = document.getElementById('grammalecte_tf_progressbar').max;
            // end of processing

            //window.setCursor("auto"); // restore pointer

            const t1 = Date.now();
            document.getElementById('grammalecte_tf_time_res').textContent = this.getTimeRes((t1-t0)/1000);
            this.xTextArea.value = sText;
        }
        catch (e) {
            showError(e);
        }
    }

    formatText (sText, sOptName) {
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
        }
        catch (e) {
            showError(e);
        }
        return [sText, nCount];
    }

    removeHyphenAtEndOfParagraphs (sText) {
        let nCount = (sText.match(/-[  ]*\n/gm) || []).length;
        sText = sText.replace(/-[  ]*\n/gm, "");
        return [sText, nCount];
    }

    mergeContiguousParagraphs (sText) {
        let nCount = 0;
        sText = sText.replace(/^[  ]+$/gm, ""); // clear empty paragraphs
        let s = "";
        for (let sParagraph of this.getParagraph(sText)) {
            if (sParagraph === "") {
                s += "\n";
            } else {
                s += sParagraph + " ";
                nCount += 1;
            }
        }
        s = s.replace(/  +/gm, " ").replace(/ $/gm, "");
        return [s, nCount];
    }

    * getParagraph (sText) {
        // generator: returns paragraphs of text
        let iStart = 0;
        let iEnd = 0;
        while ((iEnd = sText.indexOf("\n", iStart)) !== -1) {
            yield sText.slice(iStart, iEnd);
            iStart = iEnd + 1;
        }
        yield sText.slice(iStart);
    }

    getTimeRes (n) {
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
}
