# Builder for French language

import os
import platform
import zipfile
from distutils import dir_util, file_util

import helpers


def build (sLang, dVars, spLangPack):
    "complementary build launched from make.py"
    createWebExtension(sLang, dVars)
    createThunderbirdExtension(sLang, dVars, spLangPack)
    createNodeJSPackage(sLang)


def createWebExtension (sLang, dVars):
    "create Web-extension"
    print("Building WebExtension")
    helpers.createCleanFolder("_build/webext/"+sLang)
    dir_util.copy_tree("gc_lang/"+sLang+"/webext/", "_build/webext/"+sLang)
    dir_util.copy_tree("grammalecte-js", "_build/webext/"+sLang+"/grammalecte")
    dVars['webextOptionsHTML'] = _createOptionsForWebExtension(dVars)
    helpers.copyAndFileTemplate("_build/webext/"+sLang+"/manifest.json", "_build/webext/"+sLang+"/manifest.json", dVars)
    helpers.copyAndFileTemplate("_build/webext/"+sLang+"/panel/main.html", "_build/webext/"+sLang+"/panel/main.html", dVars)
    with helpers.cd("_build/webext/"+sLang):
        os.system("web-ext build")


def _createOptionsForWebExtension (dVars):
    sHTML = ""
    sLang = dVars['sDefaultUILang']
    for sSection, lOpt in dVars['lStructOpt']:
        sHTML += f'\n<div id="subsection_{sSection}" class="opt_subsection">\n  <h2 data-l10n-id="option_{sSection}">{dVars["dOptLabel"][sLang][sSection][0]}</h2>\n'
        for lLineOpt in lOpt:
            for sOpt in lLineOpt:
                sHTML += f'  <p><input type="checkbox" id="option_{sOpt}" class="gc_option" data-option="{sOpt}"/><label id="option_label_{sOpt}" for="option_{sOpt}" data-l10n-id="option_{sOpt}">{dVars["dOptLabel"][sLang][sOpt][0]}</label></p>\n'
        sHTML += '</div>\n'
    return sHTML


def createThunderbirdExtension (sLang, dVars, spLangPack):
    "create extension for Thunderbird"
    print("Building extension for Thunderbird")
    sExtensionName = dVars['tb_identifier'] + "-v" + dVars['version'] + '.xpi'
    spfZip = "_build/" + sExtensionName
    hZip = zipfile.ZipFile(spfZip, mode='w', compression=zipfile.ZIP_DEFLATED)
    _copyGrammalecteJSPackageInZipFile(hZip, spLangPack)
    for spf in ["LICENSE.txt", "LICENSE.fr.txt"]:
        hZip.write(spf)
    dVars = _createOptionsForThunderbird(dVars)
    helpers.addFolderToZipAndFileFile(hZip, "gc_lang/"+sLang+"/tb", "", dVars, True)
    hZip.close()
    spDebugProfile = dVars['win_tb_debug_extension_path']  if platform.system() == "Windows"  else dVars['linux_tb_debug_extension_path']
    helpers.unzip(spfZip, spDebugProfile)
    spfBetaExtension = dVars['win_tb_beta_extension_filepath']  if platform.system() == "Windows"  else dVars['linux_tb_beta_extension_filepath']
    #helpers.unzip(spfZip, spBetaProfile)
    file_util.copy_file(spfZip, spfBetaExtension)


def _createOptionsForThunderbird (dVars):
    dVars['sXULTabs'] = ""
    dVars['sXULTabPanels'] = ""
    # dialog options
    for sSection, lOpt in dVars['lStructOpt']:
        dVars['sXULTabs'] += '    <tab label="&option.label.'+sSection+';"/>\n'
        dVars['sXULTabPanels'] += '    <tabpanel orient="vertical">\n      <label class="section" value="&option.label.'+sSection+';" />\n'
        for lLineOpt in lOpt:
            for sOpt in lLineOpt:
                dVars['sXULTabPanels'] += '      <checkbox id="option_'+sOpt+'" class="option" label="&option.label.'+sOpt+';" />\n'
        dVars['sXULTabPanels'] += '    </tabpanel>\n'
    # translation data
    for sLang in dVars['dOptLabel'].keys():
        dVars['gc_options_labels_'+sLang] = "\n".join( [ "<!ENTITY option.label." + sOpt + ' "' + dVars['dOptLabel'][sLang][sOpt][0] + '">'  for sOpt in dVars['dOptLabel'][sLang] ] )
    return dVars


def _copyGrammalecteJSPackageInZipFile (hZip, spLangPack, sAddPath=""):
    for sf in os.listdir("grammalecte-js"):
        if not os.path.isdir("grammalecte-js/"+sf):
            hZip.write("grammalecte-js/"+sf, sAddPath+"grammalecte-js/"+sf)
    for sf in os.listdir("grammalecte-js/graphspell"):
        if not os.path.isdir("grammalecte-js/graphspell/"+sf):
            hZip.write("grammalecte-js/graphspell/"+sf, sAddPath+"grammalecte-js/graphspell/"+sf)
    for sf in os.listdir("grammalecte-js/graphspell/_dictionaries"):
        if not os.path.isdir("grammalecte-js/graphspell/_dictionaries/"+sf):
            hZip.write("grammalecte-js/graphspell/_dictionaries/"+sf, sAddPath+"grammalecte-js/graphspell/_dictionaries/"+sf)
    for sf in os.listdir(spLangPack):
        if not os.path.isdir(spLangPack+"/"+sf):
            hZip.write(spLangPack+"/"+sf, sAddPath+spLangPack+"/"+sf)


def createNodeJSPackage (sLang):
    helpers.createCleanFolder("_build/nodejs/"+sLang)
    dir_util.copy_tree("gc_lang/"+sLang+"/nodejs/", "_build/nodejs/"+sLang)
    dir_util.copy_tree("grammalecte-js", "_build/nodejs/"+sLang+"/core/grammalecte")
