# Builder for French language

import os
import platform
import zipfile
from distutils import dir_util, file_util

import helpers


def build (sLang, dVars):
    "complementary build launched from make.py"
    createWebExtension(sLang, dVars)
    createThunderbirdExtension(sLang, dVars)
    createMailExtension(sLang, dVars)
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
    with helpers.CD("_build/webext/"+sLang):
        os.system("web-ext build")
    # Copy Firefox zip extension to _build
    helpers.moveFolderContent("_build/webext/"+sLang+"/web-ext-artifacts", "_build", "fx-"+sLang+"-", True)


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


def createMailExtension (sLang, dVars):
    "create extension for Thunderbird (as MailExtension)"
    print("Building extension for Thunderbird (MailExtension)")
    spfZip = "_build/" + dVars['tb_identifier'] + "-v" + dVars['version'] + '.mailext.xpi'
    hZip = zipfile.ZipFile(spfZip, mode='w', compression=zipfile.ZIP_DEFLATED)
    _copyGrammalecteJSPackageInZipFile(hZip, sLang)
    for spf in ["LICENSE.txt", "LICENSE.fr.txt"]:
        hZip.write(spf)
    dVars = _createOptionsForThunderbird(dVars)
    helpers.addFolderToZipAndFileFile(hZip, "gc_lang/"+sLang+"/mailext", "", dVars, True)
    hZip.close()
    spExtension = dVars['win_tb_debug_extension_path']  if platform.system() == "Windows"  else dVars['linux_tb_debug_extension_path']
    file_util.copy_file(spfZip, spExtension + "/" + dVars['tb_identifier']+ ".xpi")  # Filename for TB is just <identifier.xpi>
    spExtension = dVars['win_tb_beta_extension_path']  if platform.system() == "Windows"  else dVars['linux_tb_beta_extension_path']
    file_util.copy_file(spfZip, spExtension + "/" + dVars['tb_identifier']+ ".xpi")  # Filename for TB is just <identifier.xpi>


def createThunderbirdExtension (sLang, dVars):
    "create extension for Thunderbird (as XUL addon)"
    print("Building extension for Thunderbird")
    spfZip = "_build/" + dVars['tb_identifier'] + "-v" + dVars['version'] + '.xpi'
    hZip = zipfile.ZipFile(spfZip, mode='w', compression=zipfile.ZIP_DEFLATED)
    _copyGrammalecteJSPackageInZipFile(hZip, sLang)
    for spf in ["LICENSE.txt", "LICENSE.fr.txt"]:
        hZip.write(spf)
    dVars = _createOptionsForThunderbird(dVars)
    helpers.addFolderToZipAndFileFile(hZip, "gc_lang/"+sLang+"/tb", "", dVars, True)
    hZip.close()
    #spDebugProfile = dVars['win_tb_debug_extension_path']  if platform.system() == "Windows"  else dVars['linux_tb_debug_extension_path']
    #helpers.unzip(spfZip, spDebugProfile)


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


def _copyGrammalecteJSPackageInZipFile (hZip, sLang, sAddPath=""):
    for sf in os.listdir("grammalecte-js"):
        if not os.path.isdir("grammalecte-js/"+sf):
            hZip.write("grammalecte-js/"+sf, sAddPath+"grammalecte/"+sf)
    for sf in os.listdir("grammalecte-js/graphspell"):
        if not os.path.isdir("grammalecte-js/graphspell/"+sf):
            hZip.write("grammalecte-js/graphspell/"+sf, sAddPath+"grammalecte/graphspell/"+sf)
    for sf in os.listdir("grammalecte-js/graphspell/_dictionaries"):
        if not os.path.isdir("grammalecte-js/graphspell/_dictionaries/"+sf):
            hZip.write("grammalecte-js/graphspell/_dictionaries/"+sf, sAddPath+"grammalecte/graphspell/_dictionaries/"+sf)
    for sf in os.listdir("grammalecte-js/"+sLang):
        if not os.path.isdir("grammalecte-js/"+sLang+"/"+sf):
            hZip.write("grammalecte-js/"+sLang+"/"+sf, sAddPath+"grammalecte/"+sLang+"/"+sf)


def createNodeJSPackage (sLang):
    helpers.createCleanFolder("_build/nodejs/"+sLang)
    dir_util.copy_tree("gc_lang/"+sLang+"/nodejs/", "_build/nodejs/"+sLang)
    dir_util.copy_tree("grammalecte-js", "_build/nodejs/"+sLang+"/core/grammalecte")
