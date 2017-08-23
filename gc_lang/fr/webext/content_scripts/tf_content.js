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

    setTextArea (xTextArea) {
        this.xTextArea = xTextArea;
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
            xMisc.appendChild(this._createSimpleOption("o_ordinals_no_exponant", true, "Ordinaux (15e, XXIe…)"));
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
            xActions.appendChild(createNode("div", {id: "grammalecte_tf_reset", textContent: "Par défaut", className: "grammalecte_button", style: "background-color: hsl(210, 50%, 50%)"}));
            xActions.appendChild(createNode("progress", {id: "grammalecte_tf_progressbar"}));
            xActions.appendChild(createNode("span", {id: "grammalecte_tf_time_res"}));
            xActions.appendChild(createNode("div", {id: "grammalecte_tf_apply", textContent: "Appliquer", className: "grammalecte_button", style: "background-color: hsl(180, 50%, 50%)"}));
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
        xLegend.appendChild(createNode("input", {type: "checkbox", id: "o_"+sId, className: "option"}, {default: bDefault}));
        xLegend.appendChild(createNode("label", {htmlFor: "o_"+sId, textContent: sLabel}));
        xFieldset.appendChild(xLegend);
        return xFieldset;
    }

    _createSimpleOption (sId, bDefault, sLabel) {
        let xLine = createNode("div", {className: "blockopt underline"});
        xLine.appendChild(createNode("input", {type: "checkbox", id: sId, className: "option"}, {default: bDefault}));
        xLine.appendChild(createNode("label", {htmlFor: sId, textContent: sLabel, className: "opt_lbl largew"}));
        xLine.appendChild(createNode("div", {id: "res_"+sId, className: "grammalecte_tf_result", textContent: "9999"}));
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
        xLine.appendChild(createNode("div", {id: "res_"+"o_ts_ligature", className: "grammalecte_tf_result", textContent: "9999"}));
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
    switchGroup (sOptName) {
        if (document.getElementById(sOptName).checked) {
            document.getElementById(sOptName.slice(2)).style.opacity = 1;
        } else {
            document.getElementById(sOptName.slice(2)).style.opacity = 0.3;
        }
    }


    reset () {
        this.resetProgressBar();
        for (let xNode of document.getElementsByClassName("option")) {
            xNode.checked = (xNode.dataset.default === "true");
            if (xNode.id.startsWith("o_group_")) {
                switchGroup(xNode.id);
            }
        }
    }

    resetProgressBar () {
        document.getElementById('progressbar').value = 0;
        document.getElementById('time_res').textContent = "";
    }

    setOptions (oOptions) {
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

    saveOptions () {
        let oOptions = {};
        for (let xNode of document.getElementsByClassName("option")) {
            oOptions[xNode.id] = xNode.checked;
        }
        self.port.emit("saveOptions", JSON.stringify(oOptions));
    }


}


let sTFinnerHTML = ' \
<!-- Misc --> \
    <div class="blockopt underline"> \
      <div id="res_o_ordinals_no_exponant" class="result fright"></div> \
      <input type="checkbox" id="o_ordinals_no_exponant" class="option" data-default="true" /> \
      <label for="o_ordinals_no_exponant" class="opt_lbl reducedw" data-l10n-en="tf_ordinals_no_exponant">${tf_ordinals_no_exponant}</label> \
      <div class="secondoption"> \
        <input type="checkbox" id="o_ordinals_exponant" class="option" data-default="true" /> \
        <label for="o_ordinals_exponant" class="opt_lbl smallw" data-l10n-en="tf_ordinals_exponant">${tf_ordinals_exponant}</label> \
      </div> \
    </div> \
';