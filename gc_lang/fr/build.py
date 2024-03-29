# Builder for French language

import os
import platform
import zipfile
import shutil
import json
import traceback
from distutils import dir_util, file_util

import helpers


def build (sLang, dVars):
    "complementary build launched from make.py"
    dVars['webextOptionsHTML'] = _createOptionsForWebExtension(dVars)
    createWebExtension(sLang, dVars)
    convertWebExtensionForChrome(sLang, dVars)
    createMailExtension(sLang, dVars)
    createNodeJSPackage(sLang)


def createWebExtension (sLang, dVars):
    "create Web-extension"
    print("> Building WebExtension for Firefox")
    helpers.createCleanFolder("_build/webext/"+sLang)
    dir_util.copy_tree("gc_lang/"+sLang+"/webext/", "_build/webext/"+sLang)
    dir_util.copy_tree("grammalecte-js", "_build/webext/"+sLang+"/grammalecte")
    helpers.copyAndFileTemplate("_build/webext/"+sLang+"/manifest.json", "_build/webext/"+sLang+"/manifest.json", dVars)
    helpers.copyAndFileTemplate("_build/webext/"+sLang+"/panel/main.html", "_build/webext/"+sLang+"/panel/main.html", dVars)
    with helpers.CD("_build/webext/"+sLang):
        os.system("web-ext build")
    # Copy Firefox zip extension to _build
    helpers.moveFolderContent("_build/webext/"+sLang+"/web-ext-artifacts", "_build", "firefox-", True)


def convertWebExtensionForChrome (sLang, dVars):
    "Create the extension for Chrome"
    print("> Converting WebExtension for Chrome")
    try:
        with open(f"_build/webext/{sLang}/manifest.json", "r", encoding="utf-8") as hSrc:
            dManifest = json.load(hSrc)
            if "applications" in dManifest:
                del dManifest["applications"]
            if "chrome_settings_overrides" in dManifest:
                del dManifest["chrome_settings_overrides"]
        with open(f"_build/webext/{sLang}/manifest.json", "w", encoding="utf-8") as hDst:
            json.dump(dManifest, hDst, ensure_ascii=True, indent=2)
        shutil.make_archive(f"_build/chrome-grammalecte-{sLang}-v{dVars['version']}", 'zip', "_build/webext/"+sLang)
    except:
        traceback.print_exc()
        print("  Error. Converting the WebExtension for Chrome failed.")


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
    print("> Building extension for Thunderbird (MailExtension)")
    spfZip = f"_build/thunderbird-grammalecte-{sLang}-v{dVars['version']}.mailext.xpi"
    hZip = zipfile.ZipFile(spfZip, mode='w', compression=zipfile.ZIP_DEFLATED)
    _copyGrammalecteJSPackageInZipFile(hZip, sLang)
    for spf in ["LICENSE.txt", "LICENSE.fr.txt"]:
        hZip.write(spf)
    helpers.addFolderToZipAndFileFile(hZip, f"gc_lang/{sLang}/mailext", "", dVars, True)
    helpers.addFileToZipAndFileFile(hZip, f"gc_lang/{sLang}/webext/background.js", "background.js", dVars)
    helpers.addFileToZipAndFileFile(hZip, f"gc_lang/{sLang}/webext/gce_worker.js", "gce_worker.js", dVars)
    helpers.addFileToZipAndFileFile(hZip, f"gc_lang/{sLang}/webext/README.md", "README.md", dVars)
    helpers.addFileToZipAndFileFile(hZip, f"gc_lang/{sLang}/webext/NOTE_FOR_REVIEWERS.md", "NOTE_FOR_REVIEWERS.md", dVars)
    helpers.addFolderToZipAndFileFile(hZip, f"gc_lang/{sLang}/webext/3rd", "3rd", dVars, True)
    helpers.addFolderToZipAndFileFile(hZip, f"gc_lang/{sLang}/webext/_locales", "_locales", dVars, True)
    helpers.addFolderToZipAndFileFile(hZip, f"gc_lang/{sLang}/webext/content_scripts", "content_scripts", dVars, True)
    helpers.addFolderToZipAndFileFile(hZip, f"gc_lang/{sLang}/webext/fonts", "fonts", dVars, True)
    helpers.addFolderToZipAndFileFile(hZip, f"gc_lang/{sLang}/webext/img", "img", dVars, True)
    helpers.addFolderToZipAndFileFile(hZip, f"gc_lang/{sLang}/webext/panel", "panel", dVars, True)
    hZip.close()
    # Note about copying Thunderbird extension directly into the profile:
    # In Options > Configuration editor (about:config), deactivate option <xpinstall.whitelist.required>
    # If <manifest.json> is changed, you must reinstall the extension manually
    spExtension = dVars['win_tb_debug_extension_path']  if platform.system() == "Windows"  else dVars['linux_tb_debug_extension_path']
    if os.path.isdir(spExtension):
        file_util.copy_file(spfZip, f"{spExtension}/{dVars['tb_identifier']}.xpi")  # Filename for TB is just <identifier.xpi>
        print(f"Thunderbird extension copied in <{spExtension}>")
    spExtension = dVars['win_tb_beta_extension_path']  if platform.system() == "Windows"  else dVars['linux_tb_beta_extension_path']
    if os.path.isdir(spExtension):
        file_util.copy_file(spfZip, f"{spExtension}/{dVars['tb_identifier']}.xpi")  # Filename for TB is just <identifier.xpi>
        print(f"Thunderbird extension copied in <{spExtension}>")


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
