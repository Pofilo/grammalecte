// JavaScript
// Text formatter

"use strict";

function createTextFormatter (xTextArea) {
    let xTFNode = document.createElement("div");
    try {
        // Options
        let xOptions = createDiv("tf_options", "");
        let xSSP = createFieldset("group_ssp", true, "Espaces surnuméraires");
        xSSP.appendChild(createOptionInputAndLabel("o_start_of_paragraph", true, "En début de paragraphe"));
        xSSP.appendChild(createOptionInputAndLabel("o_end_of_paragraph", true, "En fin de paragraphe"));
        xSSP.appendChild(createOptionInputAndLabel("o_between_words", true, "Entre les mots"));
        xSSP.appendChild(createOptionInputAndLabel("o_before_punctuation", true, "Avant les points (.), les virgules (,)"));
        xSSP.appendChild(createOptionInputAndLabel("o_within_parenthesis", true, "À l’intérieur des parenthèses"));
        xSSP.appendChild(createOptionInputAndLabel("o_within_square_brackets", true, "À l’intérieur des crochets"));
        xSSP.appendChild(createOptionInputAndLabel("o_within_quotation_marks", true, "À l’intérieur des guillemets “ et ”"));
        let xSpace = createFieldset("group_space", true, "Espaces manquants");
        xSpace.appendChild(createOptionInputAndLabel("o_add_space_after_punctuation", true, "Après , ; : ? ! . …"));
        xSpace.appendChild(createOptionInputAndLabel("o_add_space_around_hyphens", true, "Autour des tirets d’incise"));
        let xNBSP = createFieldset("group_nbsp", true, "Espaces insécables");
        xNBSP.appendChild(createOptionInputAndLabel("o_nbsp_before_punctuation", true, "Avant : ; ? et !"));
        xNBSP.appendChild(createOptionInputAndLabel("o_nbsp_within_quotation_marks", true, "Avec les guillemets « et »"));
        xNBSP.appendChild(createOptionInputAndLabel("o_nbsp_before_symbol", true, "Avant % ‰ € $ £ ¥ ˚C"));
        xNBSP.appendChild(createOptionInputAndLabel("o_nbsp_within_numbers", true, "À l’intérieur des nombres"));
        xNBSP.appendChild(createOptionInputAndLabel("o_nbsp_before_units", true, "Avant les unités de mesure"));
        let xDelete = createFieldset("group_delete", true, "Suppressions");
        xDelete.appendChild(createOptionInputAndLabel("o_erase_non_breaking_hyphens", true, "Tirets conditionnels"));
        let xTypo = createFieldset("group_typo", true, "Signes typographiques");
        xTypo.appendChild(createOptionInputAndLabel("o_ts_apostrophe", true, "Apostrophe (’)"));
        xTypo.appendChild(createOptionInputAndLabel("o_ts_ellipsis", true, "Points de suspension (…)"));
        xTypo.appendChild(createOptionInputAndLabel("o_ts_dash_middle", true, "Tirets d’incise :"));
        xTypo.appendChild(createOptionInputAndLabel("o_ts_dash_start", true, "Tirets en début de paragraphe :"));
        xTypo.appendChild(createOptionInputAndLabel("o_ts_quotation_marks", true, "Modifier les guillemets droits (\" et ')"));
        xTypo.appendChild(createOptionInputAndLabel("o_ts_units", true, "Points médians des unités (N·m, Ω·m…)"));
        xTypo.appendChild(createOptionInputAndLabel("o_ts_spell", true, "Ligatures (cœur…) et diacritiques (ça, État…)"));
        xTypo.appendChild(createOptionInputAndLabel("o_ts_ligature", true, "Ligatures"));
        let xMisc = createFieldset("group_misc", true, "Divers");
        xMisc.appendChild(createOptionInputAndLabel("o_ordinals_no_exponant", true, "Ordinaux (15e, XXIe…)"));
        xMisc.appendChild(createOptionInputAndLabel("o_etc", true, "Et cætera, etc."));
        xMisc.appendChild(createOptionInputAndLabel("o_missing_hyphens", true, "Traits d’union manquants"));
        xMisc.appendChild(createOptionInputAndLabel("o_ma_word", true, "Apostrophes manquantes"));
        let xStruct = createFieldset("group_struct", false, "Restructuration [!]");
        xStruct.appendChild(createOptionInputAndLabel("o_remove_hyphens_at_end_of_paragraphs", false, "Enlever césures en fin de ligne/paragraphe [!]"));
        xStruct.appendChild(createOptionInputAndLabel("o_merge_contiguous_paragraphs", false, "Fusionner les paragraphes contigus [!]"));
        xOptions.appendChild(xSSP);
        xOptions.appendChild(xSpace);
        xOptions.appendChild(xNBSP);
        xOptions.appendChild(xDelete);
        xOptions.appendChild(xTypo);
        xOptions.appendChild(xMisc);
        xOptions.appendChild(xStruct);
        // Actions
        let xActions = createDiv("tf_actions", "");
        let xPgBarBox = createDiv("tf_progressbarbox", "");
        xPgBarBox.innerHTML = '<progress id="progressbar" style="width: 400px;"></progress> <span id="time_res"></span>';
        xActions.appendChild(createDiv("tf_reset", "Par défaut", "button blue"));
        xActions.appendChild(xPgBarBox);
        xActions.appendChild(createDiv("tf_apply", "Appliquer", "button green"));
        xActions.appendChild(createDiv("infomsg", "blabla"));
        // create result
        xTFNode.appendChild(xOptions);
        xTFNode.appendChild(xActions);
    }
    catch (e) {
        //console.error(e);
        showError(e);
    }
    return xTFNode;
}

function createFieldset (sId, bDefault, sLabel) {
    let xFieldset = document.createElement("fieldset");
    xFieldset.id = sId;
    xFieldset.className = "groupblock";
    let xLegend = document.createElement("legend");
    let xInput = createCheckbox("o_"+sId, bDefault, "option");
    let xLabel = createLabel(xInput.id, sLabel);
    // create result
    xLegend.appendChild(xInput);
    xLegend.appendChild(xLabel);
    xFieldset.appendChild(xLegend);
    return xFieldset;
}

function createOptionInputAndLabel (sId, bDefault, sLabel) {
    let xOption = document.createElement("div");
    xOption.className = "blockopt underline";
    let xInput = createCheckbox(sId, bDefault, "option");
    let xLabel = createLabel(sId, sLabel, "opt_lbl largew");
    let xResult = createDiv("res_"+sId, "", "result fright");
    // create result
    xOption.appendChild(xResult);
    xOption.appendChild(xInput);
    xOption.appendChild(xLabel);
    return xOption;
}

let sTFinnerHTML = ' \
<h1>FORMATEUR DE TEXTE</h1> \
<div id="tf_options"> \
 \
<!-- Supernumerary spaces --> \
<fieldset> \
  <legend><input type="checkbox" id="o_group_ssp" class="option" data-default="true" /><label for="o_group_ssp" data-l10n-en="tf_ssp">${tf_ssp}</label></legend> \
  <div id="group_ssp" class="groupblock"> \
    <div class="blockopt underline"> \
      <div id="res_o_start_of_paragraph" class="result fright"></div> \
      <input type="checkbox" id="o_start_of_paragraph" class="option" data-default="true" /> \
      <label for="o_start_of_paragraph" class="opt_lbl largew" data-l10n-en="tf_start_of_paragraph">${tf_start_of_paragraph}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_end_of_paragraph" class="result fright"></div> \
      <input type="checkbox" id="o_end_of_paragraph" class="option" data-default="true" /> \
      <label for="o_end_of_paragraph" class="opt_lbl largew" data-l10n-en="tf_end_of_paragraph">${tf_end_of_paragraph}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_between_words" class="result fright"></div> \
      <input type="checkbox" id="o_between_words" class="option" data-default="true" /> \
      <label for="o_between_words" class="opt_lbl largew" data-l10n-en="tf_between_words">${tf_between_words}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_before_punctuation" class="result fright"></div> \
      <input type="checkbox" id="o_before_punctuation" class="option" data-default="true" /> \
      <label for="o_before_punctuation" class="opt_lbl largew" data-l10n-en="tf_before_punctuation">${tf_before_punctuation}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_within_parenthesis" class="result fright"></div> \
      <input type="checkbox" id="o_within_parenthesis" class="option" data-default="true" /> \
      <label for="o_within_parenthesis" class="opt_lbl largew" data-l10n-en="tf_within_parenthesis">${tf_within_parenthesis}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_within_square_brackets" class="result fright"></div> \
      <input type="checkbox" id="o_within_square_brackets" class="option" data-default="true" /> \
      <label for="o_within_square_brackets" class="opt_lbl largew" data-l10n-en="tf_within_square_brackets">${tf_within_square_brackets}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_within_quotation_marks" class="result fright"></div> \
      <input type="checkbox" id="o_within_quotation_marks" class="option" data-default="true" /> \
      <label for="o_within_quotation_marks" class="opt_lbl largew" data-l10n-en="tf_within_quotation_marks">${tf_within_quotation_marks}</label> \
    </div> \
  </div> \
</fieldset> \
 \
<!-- Missing spaces --> \
<fieldset> \
  <legend><input type="checkbox" id="o_group_space" class="option" data-default="true" /><label for="o_group_space" data-l10n-en="tf_space">${tf_space}</label></legend> \
  <div id="group_space" class="groupblock"> \
    <div class="blockopt underline"> \
      <div id="res_o_add_space_after_punctuation" class="result fright"></div> \
      <input type="checkbox" id="o_add_space_after_punctuation" class="option" data-default="true" /> \
      <label for="o_add_space_after_punctuation" class="opt_lbl reducedw" data-l10n-en="tf_add_space_after_punctuation">${tf_add_space_after_punctuation}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_add_space_around_hyphens" class="result fright"></div> \
      <input type="checkbox" id="o_add_space_around_hyphens" class="option" data-default="true" /> \
      <label for="o_add_space_around_hyphens" class="opt_lbl largew" data-l10n-en="tf_add_space_around_hyphens">${tf_add_space_around_hyphens}</label> \
    </div> \
  </div> \
</fieldset> \
 \
<!-- Non breaking spaces --> \
<fieldset> \
  <legend><input type="checkbox" id="o_group_nbsp" class="option" data-default="true" /><label for="o_group_nbsp" data-l10n-en="tf_nbsp">${tf_nbsp}</label></legend> \
  <div id="group_nbsp" class="groupblock"> \
    <div class="blockopt underline"> \
      <div id="res_o_nbsp_before_punctuation" class="result fright"></div> \
      <input type="checkbox" id="o_nbsp_before_punctuation" class="option" data-default="true" /> \
      <label for="o_nbsp_before_punctuation" class="opt_lbl reducedw" data-l10n-en="tf_nbsp_before_punctuation">${tf_nbsp_before_punctuation}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_nbsp_within_quotation_marks" class="result fright"></div> \
      <input type="checkbox" id="o_nbsp_within_quotation_marks" class="option" data-default="true" /> \
      <label for="o_nbsp_within_quotation_marks" class="opt_lbl reducedw" data-l10n-en="tf_nbsp_within_quotation_marks">${tf_nbsp_within_quotation_marks}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_nbsp_before_symbol" class="result fright"></div> \
      <input type="checkbox" id="o_nbsp_before_symbol" class="option" data-default="true" /> \
      <label for="o_nbsp_before_symbol" class="opt_lbl largew" data-l10n-en="tf_nbsp_before_symbol">${tf_nbsp_before_symbol}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_nbsp_within_numbers" class="result fright"></div> \
      <input type="checkbox" id="o_nbsp_within_numbers" class="option" data-default="true" /> \
      <label for="o_nbsp_within_numbers" class="opt_lbl reducedw" data-l10n-en="tf_nbsp_within_numbers">${tf_nbsp_within_numbers}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_nbsp_before_units" class="result fright"></div> \
      <input type="checkbox" id="o_nbsp_before_units" class="option" data-default="true" /> \
      <label for="o_nbsp_before_units" class="opt_lbl largew" data-l10n-en="tf_nbsp_before_units">${tf_nbsp_before_units}</label> \
    </div> \
  </div> \
</fieldset> \
 \
<!-- Deletions --> \
<fieldset> \
  <legend><input type="checkbox" id="o_group_delete" class="option" data-default="true" /><label for="o_group_delete" data-l10n-en="tf_delete">${tf_delete}</label></legend> \
  <div id="group_delete" class="groupblock"> \
    <div class="blockopt underline"> \
      <div id="res_o_erase_non_breaking_hyphens" class="result fright"></div> \
      <input type="checkbox" id="o_erase_non_breaking_hyphens" class="option" data-default="true" /> \
      <label for="o_erase_non_breaking_hyphens" class="opt_lbl largew" data-l10n-en="tf_erase_non_breaking_hyphens">${tf_erase_non_breaking_hyphens}</label> \
    </div> \
  </div> \
</fieldset> \
 \
<!-- Typographical signs --> \
<fieldset> \
  <legend><input type="checkbox" id="o_group_typo" class="option" data-default="true" /><label for="o_group_typo" data-l10n-en="tf_typo">${tf_typo}</label></legend> \
  <div id="group_typo" class="groupblock"> \
    <div class="blockopt underline"> \
      <div id="res_o_ts_apostrophe" class="result fright"></div> \
      <input type="checkbox" id="o_ts_apostrophe" class="option" data-default="true" /> \
      <label for="o_ts_apostrophe" class="opt_lbl largew" data-l10n-en="tf_ts_apostrophe">${tf_ts_apostrophe}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_ts_ellipsis" class="result fright"></div> \
      <input type="checkbox" id="o_ts_ellipsis" class="option" data-default="true" /> \
      <label for="o_ts_ellipsis" class="opt_lbl largew" data-l10n-en="tf_ts_ellipsis">${tf_ts_ellipsis}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_ts_dash_middle" class="result fright"></div> \
      <input type="checkbox" id="o_ts_dash_middle" class="option" data-default="true" /> \
      <label for="o_ts_dash_middle" class="opt_lbl largew" data-l10n-en="tf_ts_dash_middle">${tf_ts_dash_middle}</label> \
    </div> \
    <div class="blockopt"> \
      <div class="inlineblock indent"> \
        <input type="radio" name="hyphen1" id="o_ts_m_dash_middle" class="option" data-default="false" /><label for="o_ts_m_dash_middle" class="opt_lbl" data-l10n-en="tf_emdash">${tf_emdash}</label> \
      </div> \
      <div class="inlineblock indent"> \
        <input type="radio" name="hyphen1" id="o_ts_n_dash_middle" class="option" data-default="true" /><label for="o_ts_n_dash_middle" class="opt_lbl" data-l10n-en="tf_endash">${tf_endash}</label> \
      </div> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_ts_dash_start" class="result fright"></div> \
      <input type="checkbox" id="o_ts_dash_start" class="option" data-default="true" /> \
      <label for="o_ts_dash_start" class="opt_lbl largew" data-l10n-en="tf_ts_dash_start">${tf_ts_dash_start}</label> \
    </div> \
    <div class="blockopt"> \
      <div class="inlineblock indent"> \
        <input type="radio" name="hyphen2" id="o_ts_m_dash_start" class="option"  data-default="true" /><label for="o_ts_m_dash_start" class="opt_lbl" data-l10n-en="tf_emdash">${tf_emdash}</label> \
      </div> \
      <div class="inlineblock indent"> \
        <input type="radio" name="hyphen2" id="o_ts_n_dash_start" class="option" data-default="false" /><label for="o_ts_n_dash_start" class="opt_lbl" data-l10n-en="tf_endash">${tf_endash}</label> \
      </div> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_ts_quotation_marks" class="result fright"></div> \
      <input type="checkbox" id="o_ts_quotation_marks" class="option" data-default="true" /> \
      <label for="o_ts_quotation_marks" class="opt_lbl largew" data-l10n-en="tf_ts_quotation_marks">${tf_ts_quotation_marks}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_ts_units" class="result fright"></div> \
      <input type="checkbox" id="o_ts_units" class="option" data-default="true" /> \
      <label for="o_ts_units" class="opt_lbl largew" data-l10n-en="tf_ts_units">${tf_ts_units}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_ts_spell" class="result fright"></div> \
      <input type="checkbox" id="o_ts_spell" class="option" data-default="true" /> \
      <label for="o_ts_spell" class="opt_lbl largew" data-l10n-en="tf_ts_spell">${tf_ts_spell}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_ts_ligature" class="result fright"></div> \
      <div class="inlineblock"> \
        <input type="checkbox" id="o_ts_ligature" class="option" data-default="false" /> \
        <label for="o_ts_ligature" class="opt_lbl" data-l10n-en="tf_ts_ligature">${tf_ts_ligature}</label> \
      </div> \
      <div class="inlineblock indent"> \
        <input type="radio" id="o_ts_ligature_do" name="liga" class="option" data-default="false" /> \
        <label for="o_ts_ligature_do" class="opt_lbl" data-l10n-en="tf_ts_ligature_do">${tf_ts_ligature_do}</label> \
      </div> \
      <div class="inlineblock indent"> \
        <input type="radio" id="o_ts_ligature_undo" name="liga" class="option" data-default="true" /> \
        <label for="o_ts_ligature_undo" class="opt_lbl" data-l10n-en="tf_ts_ligature_undo">${tf_ts_ligature_undo}</label> \
      </div> \
    </div> \
 \
    <div class="blockopt"> \
      <div class="inlineblock indent"><input type="checkbox" id="o_ts_ligature_ff" class="option" data-default="true" /><label for="o_ts_ligature_ff" class="opt_lbl">ff</label></div> \
      &nbsp; <div class="inlineblock"><input type="checkbox" id="o_ts_ligature_fi" class="option" data-default="true" /><label for="o_ts_ligature_fi" class="opt_lbl">fi</label></div> \
      &nbsp; <div class="inlineblock"><input type="checkbox" id="o_ts_ligature_ffi" class="option" data-default="true" /><label for="o_ts_ligature_ffi" class="opt_lbl">ffi</label></div> \
      &nbsp; <div class="inlineblock"><input type="checkbox" id="o_ts_ligature_fl" class="option" data-default="true" /><label for="o_ts_ligature_fl" class="opt_lbl">fl</label></div> \
      &nbsp; <div class="inlineblock"><input type="checkbox" id="o_ts_ligature_ffl" class="option" data-default="true" /><label for="o_ts_ligature_ffl" class="opt_lbl">ffl</label></div> \
      &nbsp; <div class="inlineblock"><input type="checkbox" id="o_ts_ligature_ft" class="option" data-default="true" /><label for="o_ts_ligature_ft" class="opt_lbl">ft</label></div> \
      &nbsp; <div class="inlineblock"><input type="checkbox" id="o_ts_ligature_st" class="option" data-default="false" /><label for="o_ts_ligature_st" class="opt_lbl">st</label></div> \
    </div> \
  </div> \
</fieldset> \
 \
<!-- Misc --> \
<fieldset> \
  <legend><input type="checkbox" id="o_group_misc" class="option" data-default="true" /><label for="o_group_misc" data-l10n-en="tf_misc">${tf_misc}</label></legend> \
  <div id="group_misc" class="groupblock"> \
    <div class="blockopt underline"> \
      <div id="res_o_ordinals_no_exponant" class="result fright"></div> \
      <input type="checkbox" id="o_ordinals_no_exponant" class="option" data-default="true" /> \
      <label for="o_ordinals_no_exponant" class="opt_lbl reducedw" data-l10n-en="tf_ordinals_no_exponant">${tf_ordinals_no_exponant}</label> \
      <div class="secondoption"> \
        <input type="checkbox" id="o_ordinals_exponant" class="option" data-default="true" /> \
        <label for="o_ordinals_exponant" class="opt_lbl smallw" data-l10n-en="tf_ordinals_exponant">${tf_ordinals_exponant}</label> \
      </div> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_etc" class="result fright"></div> \
      <input type="checkbox" id="o_etc" class="option" data-default="true" /> \
      <label for="o_etc" class="opt_lbl largew" data-l10n-en="tf_etc">${tf_etc}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_missing_hyphens" class="result fright"></div> \
      <input type="checkbox" id="o_missing_hyphens" class="option" data-default="true" /> \
      <label for="o_missing_hyphens" class="opt_lbl largew" data-l10n-en="tf_missing_hyphens">${tf_missing_hyphens}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_ma_word" class="result fright"></div> \
      <input type="checkbox" id="o_ma_word" class="option" data-default="true" /> \
      <label for="o_ma_word" class="opt_lbl largew" data-l10n-en="tf_ma_word">${tf_ma_word}</label> \
    </div> \
    <div class="blockopt"> \
      <div class="inlineblock indent"> \
        <input type="checkbox" id="o_ma_1letter_lowercase" class="option" /> \
        <label for="o_ma_1letter_lowercase" class="opt_lbl" data-l10n-en="tf_ma_1letter_lowercase">${tf_ma_1letter_lowercase}</label> \
      </div> \
      <div class="inlineblock indent"> \
        <input type="checkbox" id="o_ma_1letter_uppercase" class="option" /> \
        <label for="o_ma_1letter_uppercase" class="opt_lbl" data-l10n-en="tf_ma_1letter_uppercase">${tf_ma_1letter_uppercase}</label> \
      </div> \
    </div> \
  </div> \
</fieldset> \
 \
<!-- Restructuration --> \
<fieldset> \
  <legend><input type="checkbox" id="o_group_struct" class="option" data-default="false" /><label for="o_group_struct" data-l10n-en="tf_struct">${tf_struct}</label></legend> \
  <div id="group_struct" class="groupblock"> \
    <div class="blockopt underline"> \
      <div id="res_o_remove_hyphens_at_end_of_paragraphs" class="result fright"></div> \
      <input type="checkbox" id="o_remove_hyphens_at_end_of_paragraphs" class="option" data-default="false" /> \
      <label for="o_remove_hyphens_at_end_of_paragraphs" class="opt_lbl largew"  data-l10n-en="tf_remove_hyphens_at_end_of_paragraphs">${tf_remove_hyphens_at_end_of_paragraphs}</label> \
    </div> \
    <div class="blockopt underline"> \
      <div id="res_o_merge_contiguous_paragraphs" class="result fright"></div> \
      <input type="checkbox" id="o_merge_contiguous_paragraphs" class="option" data-default="false" /> \
      <label for="o_merge_contiguous_paragraphs" class="opt_lbl largew" data-l10n-en="tf_merge_contiguous_paragraphs">${tf_merge_contiguous_paragraphs}</label> \
    </div> \
  </div> \
</fieldset> \
</div> \
 \
<div id="tf_actions"> \
  <div id="tf_reset" class="button blue" data-l10n-en="Default">Par défaut</div> \
  <div id="tf_apply" class="button green fright" data-l10n-en="Apply">Appliquer</div> \
  <div id="tf_progressbarbox"><progress id="progressbar" style="width: 400px;"></progress> <span id="time_res"></span></div> \
  <!--<div class="clearer"></div> \
  <div id="infomsg" data-l10n-id="tf_infomsg"></div>--> \
</div> \
';