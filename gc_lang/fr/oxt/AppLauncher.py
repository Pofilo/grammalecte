# Grammalecte AppLauncher
# by Olivier R.
# License: MPL 2

import unohelper
import uno
import traceback

import helpers

from com.sun.star.task import XJobExecutor


xDesktop = None


class AppLauncher (unohelper.Base, XJobExecutor):
    def __init__ (self, ctx):
        self.ctx = ctx
        # In this extension, French is default language.
        # It is assumed that those who need to use the French dictionaries understand French and may not understand English.
        xSettings = helpers.getConfigSetting("/org.openoffice.Setup/L10N", False)
        sLocale = xSettings.getByName("ooLocale")  # Note: look at ooSetupSystemLocale value?
        self.sLang = sLocale[0:2]

    # XJobExecutor
    def trigger (self, sCmd):
        try:
            if sCmd == "About":
                import About
                xDialog = About.AboutGrammalecte(self.ctx)
                xDialog.run(self.sLang)
            elif sCmd.startswith("CJ"):
                import Conjugueur
                xDialog = Conjugueur.Conjugueur(self.ctx)
                if sCmd[2:3] == "/":
                    xDialog.run(sCmd[3:])
                else:
                    xDialog.run()
            elif sCmd == "TF":
                import TextFormatter
                xDialog = TextFormatter.TextFormatter(self.ctx)
                xDialog.run(self.sLang)
            elif sCmd == "DI":
                import DictOptions
                xDialog = DictOptions.DictOptions(self.ctx)
                xDialog.run(self.sLang)
            elif sCmd == "LE":
                import LexiconEditor
                xDialog = LexiconEditor.LexiconEditor(self.ctx)
                xDialog.run(self.sLang)
            elif sCmd == "MA":
                import Author
                xDialog = Author.Author(self.ctx)
                xDialog.run(self.sLang)
            elif sCmd == "OP":
                import Options
                xDialog = Options.GC_Options(self.ctx)
                xDialog.run(self.sLang)
            elif sCmd == "EN":
                import Enumerator
                xDialog = Enumerator.Enumerator(self.ctx)
                xDialog.run(self.sLang)
            elif sCmd == "GO":
                import GraphicOptions
                xDialog = GraphicOptions.GraphicOptions(self.ctx)
                xDialog.run(self.sLang)
            elif sCmd.startswith("FA/"):
                findAll(sCmd[6:], (sCmd[3:4] == "y"), (sCmd[4:5] == "y"))
            # elif sCmd.startswith("URL/"):
            #     # Call from context menu to launch URL?
            #     # http://opengrok.libreoffice.org/xref/core/sw/source/ui/lingu/olmenu.cxx#785
            #     xSystemShellExecute = self.ctx.getServiceManager().createInstanceWithContext('com.sun.star.system.SystemShellExecute', self.ctx)
            #     xSystemShellExecute.execute(url, "", uno.getConstantByName("com.sun.star.system.SystemShellExecuteFlags.URIS_ONLY"))
            elif sCmd == "None":
                pass
            else:
                print("Unknown command: "+str(sCmd))
        except:
            traceback.print_exc()


def findAll (sText, bCaseSensitive, bFullWord):
    global xDesktop
    if not xDesktop:
        xCurCtx = uno.getComponentContext()
        xDesktop = xCurCtx.getServiceManager().createInstanceWithContext('com.sun.star.frame.Desktop', xCurCtx)
    if sText:
        xDoc = xDesktop.getCurrentComponent()
        xSearchDescr = xDoc.createSearchDescriptor()
        xSearchDescr.SearchString = sText
        xSearchDescr.SearchCaseSensitive = bCaseSensitive
        xSearchDescr.SearchWords = bFullWord
        xSearchDescr.SearchAll = True           # necessary ?
        xFound = xDoc.findAll(xSearchDescr)
        xDoc.CurrentController.select(xFound)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(AppLauncher, 'net.grammalecte.AppLauncher', ('com.sun.star.task.Job',))
