# Builder for French language

import os
import zipfile
from distutils import dir_util, file_util

import helpers


def build (sLang, dVars, spLangPack):
    "complementary build launched from make.py"
    createFirefoxExtension(sLang, dVars)
    createWebExtension(sLang, dVars)
    createThunderbirdExtension(sLang, dVars, spLangPack)


def createWebExtension (sLang, dVars):
    "create Web-extension"
    print("Building WebExtension")
    helpers.createCleanFolder("_build/webext/"+sLang)
    dir_util.copy_tree("gc_lang/"+sLang+"/webext/", "_build/webext/"+sLang)
    dir_util.copy_tree("grammalecte-js", "_build/webext/"+sLang+"/grammalecte")
    dVars['webextOptionsHTML'] = _createOptionsForWebExtension(dVars)
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
                sHTML += f'  <p><input type="checkbox" id="option_{sOpt}" /><label id="option_label_{sOpt}" for="option_{sOpt}" data-l10n-id="option_{sOpt}">{dVars["dOptLabel"][sLang][sOpt][0]}</label></p>\n'
        sHTML += '</div>\n'
    return sHTML


def createFirefoxExtension (sLang, dVars):
    "create extension for Firefox"
    print("Building extension for Firefox")
    helpers.createCleanFolder("_build/xpi/"+sLang)
    dir_util.copy_tree("gc_lang/"+sLang+"/xpi/", "_build/xpi/"+sLang)
    dir_util.copy_tree("grammalecte-js", "_build/xpi/"+sLang+"/grammalecte")
    sHTML, dProperties = _createOptionsForFirefox(dVars)
    dVars['optionsHTML'] = sHTML
    helpers.copyAndFileTemplate("_build/xpi/"+sLang+"/data/about_panel.html", "_build/xpi/"+sLang+"/data/about_panel.html", dVars)
    for sLocale in dProperties.keys():
        spfLocale = "_build/xpi/"+sLang+"/locale/"+sLocale+".properties"
        if os.path.exists(spfLocale):
            helpers.copyAndFileTemplate(spfLocale, spfLocale, dProperties)
        else:
            print("Locale file not found: " + spfLocale)
    with helpers.cd("_build/xpi/"+sLang):
        os.system("jpm xpi")


def _createOptionsForFirefox (dVars):
    sHTML = ""
    for sSection, lOpt in dVars['lStructOpt']:
        sHTML += '\n<div id="subsection_' + sSection + '" class="opt_subsection">\n  <h2 data-l10n-id="option_'+sSection+'"></h2>\n'
        for lLineOpt in lOpt:
            for sOpt in lLineOpt:
                sHTML += '  <p><input type="checkbox" id="option_'+sOpt+'" /><label id="option_label_'+sOpt+'" for="option_'+sOpt+'" data-l10n-id="option_'+sOpt+'"></label></p>\n'
        sHTML += '</div>\n'
    # Creating translation data
    dProperties = {}
    for sLang in dVars['dOptLabel'].keys():
        dProperties[sLang] = "\n".join( [ "option_" + sOpt + " = " + dVars['dOptLabel'][sLang][sOpt][0].replace(" [!]", " [!]")  for sOpt in dVars['dOptLabel'][sLang] ] )
    return sHTML, dProperties


def createThunderbirdExtension (sLang, dVars, spLangPack):
    "create extension for Thunderbird"
    print("Building extension for Thunderbird")
    sExtensionName = dVars['tb_identifier'] + "-v" + dVars['version'] + '.xpi'
    spfZip = "_build/" + sExtensionName
    hZip = zipfile.ZipFile(spfZip, mode='w', compression=zipfile.ZIP_DEFLATED)
    _copyGrammalecteJSPackageInZipFile(hZip, spLangPack, dVars['dic_name']+".json")
    for spf in ["LICENSE.txt", "LICENSE.fr.txt"]:
        hZip.write(spf)
    dVars = _createOptionsForThunderbird(dVars)
    helpers.addFolderToZipAndFileFile(hZip, "gc_lang/"+sLang+"/tb", "", dVars, True)
    hZip.write("gc_lang/"+sLang+"/xpi/gce_worker.js", "worker/gce_worker.js")
    spDict = "gc_lang/"+sLang+"/xpi/data/dictionaries"
    for sp in os.listdir(spDict):
        if os.path.isdir(spDict+"/"+sp):
            hZip.write(spDict+"/"+sp+"/"+sp+".dic", "content/dictionaries/"+sp+"/"+sp+".dic")
            hZip.write(spDict+"/"+sp+"/"+sp+".aff", "content/dictionaries/"+sp+"/"+sp+".aff")
    hZip.close()
    helpers.unzip(spfZip, dVars['tb_debug_extension_path'])


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


def _copyGrammalecteJSPackageInZipFile (hZip, spLangPack, sDicName, sAddPath=""):
    for sf in os.listdir("grammalecte-js"):
        if not os.path.isdir("grammalecte-js/"+sf):
            hZip.write("grammalecte-js/"+sf, sAddPath+"grammalecte-js/"+sf)
    for sf in os.listdir(spLangPack):
        if not os.path.isdir(spLangPack+"/"+sf):
            hZip.write(spLangPack+"/"+sf, sAddPath+spLangPack+"/"+sf)
    hZip.write("grammalecte-js/_dictionaries/"+sDicName, sAddPath+"grammalecte-js/_dictionaries/"+sDicName)
