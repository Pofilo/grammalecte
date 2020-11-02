# Grammalecte - Lexicographe
# by Olivier R. License: MPL 2

import uno
import unohelper
import traceback

from com.sun.star.task import XJob
from com.sun.star.ui import XContextMenuInterceptor
#from com.sun.star.ui.ContextMenuInterceptorAction import IGNORED
#from com.sun.star.ui.ContextMenuInterceptorAction import EXECUTE_MODIFIED

from grammalecte.graphspell.spellchecker import SpellChecker
from grammalecte.graphspell.echo import echo
import helpers


xDesktop = None
oSpellChecker = None


class MyContextMenuInterceptor (XContextMenuInterceptor, unohelper.Base):
    def __init__ (self, ctx):
        self.ctx = ctx

    def notifyContextMenuExecute (self, xEvent):
        sWord = self._getWord()
        try:
            lWordAndMorph = oSpellChecker.analyze(sWord)
            # if not lWordAndMorph:
            #     return uno.Enum("com.sun.star.ui.ContextMenuInterceptorAction", "IGNORED") # don’t work on AOO, have to import the value
            #     #return IGNORED
            xContextMenu = xEvent.ActionTriggerContainer
            if xContextMenu:
                # entries index
                i = xContextMenu.Count
                nUnoConstantLine = uno.getConstantByName("com.sun.star.ui.ActionTriggerSeparatorType.LINE")

                if lWordAndMorph:
                    # word analysis
                    i = self._addItemToContextMenu(xContextMenu, i, "ActionTriggerSeparator", SeparatorType=nUnoConstantLine)
                    for sWord, lMorph in lWordAndMorph:
                        if len(lMorph) == 1:
                            sMorph, sReadableMorph = lMorph[0]
                            i = self._addItemToContextMenu(xContextMenu, i, "ActionTrigger", Text=sWord + " : " + sReadableMorph, CommandURL="service:net.grammalecte.AppLauncher?None")
                        elif len(lMorph) >= 1:
                            # submenu
                            xSubMenuContainer = xContextMenu.createInstance("com.sun.star.ui.ActionTriggerContainer")
                            for j, (sMorph, sReadableMorph) in enumerate(lMorph):
                                self._addItemToContextMenu(xSubMenuContainer, j, "ActionTrigger", Text=sReadableMorph, CommandURL="service:net.grammalecte.AppLauncher?None")
                            # create root menu entry
                            i = self._addItemToContextMenu(xContextMenu, i, "ActionTrigger", Text=sWord, SubContainer=xSubMenuContainer)
                        else:
                            i = self._addItemToContextMenu(xContextMenu, i, "ActionTrigger", Text=sWord + " : [erreur] aucun résultat trouvé.")

                    # Links to Conjugueur
                    aVerb = { sMorph[1:sMorph.find("/")]  for sMorph in oSpellChecker.getMorph(sWord) if ":V" in sMorph }
                    if aVerb:
                        i = self._addItemToContextMenu(xContextMenu, i, "ActionTriggerSeparator", SeparatorType=nUnoConstantLine)
                        for sVerb in aVerb:
                            i = self._addItemToContextMenu(xContextMenu, i, "ActionTrigger", Text="Conjuguer “{}”…".format(sVerb), \
                                                            CommandURL="service:net.grammalecte.AppLauncher?CJ/"+sVerb)

                    # Search
                    xDoc = xDesktop.getCurrentComponent()
                    xViewCursor = xDoc.CurrentController.ViewCursor
                    if not xViewCursor.isCollapsed():
                        sSelec = xViewCursor.getString()
                        if sSelec.count(" ") <= 2:
                            i = self._addItemToContextMenu(xContextMenu, i, "ActionTriggerSeparator", SeparatorType=nUnoConstantLine)
                            # submenu
                            xSubMenuContainer = xContextMenu.createInstance("com.sun.star.ui.ActionTriggerContainer")
                            self._addItemToContextMenu(xSubMenuContainer, 0, "ActionTrigger", Text="insensible à la casse",
                                                       CommandURL="service:net.grammalecte.AppLauncher?FA/nn/"+sSelec)
                            self._addItemToContextMenu(xSubMenuContainer, 1, "ActionTrigger", Text="casse préservée",
                                                       CommandURL="service:net.grammalecte.AppLauncher?FA/yn/"+sSelec)
                            self._addItemToContextMenu(xSubMenuContainer, 2, "ActionTrigger", Text="mot(s) entier(s)",
                                                       CommandURL="service:net.grammalecte.AppLauncher?FA/ny/"+sSelec)
                            self._addItemToContextMenu(xSubMenuContainer, 3, "ActionTrigger", Text="casse préservée + mot(s) entier(s)",
                                                       CommandURL="service:net.grammalecte.AppLauncher?FA/yy/"+sSelec)
                            # create root menu entry
                            i = self._addItemToContextMenu(xContextMenu, i, "ActionTrigger", Text="Rechercher “{}”".format(sSelec),
                                                           SubContainer=xSubMenuContainer)
                else:
                    # Link to Lexicon Editor
                    i = self._addItemToContextMenu(xContextMenu, i, "ActionTriggerSeparator", SeparatorType=nUnoConstantLine)
                    i = self._addItemToContextMenu(xContextMenu, i, "ActionTrigger", Text="Éditeur lexical…", \
                                                            CommandURL="service:net.grammalecte.AppLauncher?LE/"+sWord)

                # The controller should execute the modified context menu and stop notifying other interceptors.
                return uno.Enum("com.sun.star.ui.ContextMenuInterceptorAction", "EXECUTE_MODIFIED") # don’t work on AOO, have to import the value
                #return EXECUTE_MODIFIED # Doesn’t work since LO 5.3
        except:
            traceback.print_exc()
        return uno.Enum("com.sun.star.ui.ContextMenuInterceptorAction", "IGNORED") # don’t work on AOO, have to import the value
        #return IGNORED # Doesn’t work since LO 5.3

    def _addItemToContextMenu (self, xContextMenu, i, sType, **args):
        xMenuItem = xContextMenu.createInstance("com.sun.star.ui."+sType)
        #echo("com.sun.star.ui."+sType)
        for k, v in args.items():
            xMenuItem.setPropertyValue(k, v)
            #print("> ", k, v, xMenuItem)
        xContextMenu.insertByIndex(i, xMenuItem)
        return i + 1

    def _getWord (self):
        try:
            xDoc = xDesktop.getCurrentComponent()
            xViewCursor = xDoc.CurrentController.ViewCursor
            if xViewCursor.CharLocale.Language != "fr":
                return ""
            xText = xViewCursor.Text
            xCursor = xText.createTextCursorByRange(xViewCursor)
            xCursor.gotoStartOfWord(False)
            xCursor.gotoEndOfWord(True)
        except:
            traceback.print_exc()
        return xCursor.String.strip('.')


class JobExecutor (XJob, unohelper.Base):

    def __init__ (self, ctx):
        self.ctx = ctx
        global xDesktop
        global oSpellChecker
        try:
            if not xDesktop:
                xDesktop = self.ctx.getServiceManager().createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
            if not oSpellChecker:
                xCurCtx = uno.getComponentContext()
                oGC = self.ctx.ServiceManager.createInstanceWithContext("org.openoffice.comp.pyuno.Lightproof.grammalecte", self.ctx)
                if hasattr(oGC, "getSpellChecker"):
                    # https://bugs.documentfoundation.org/show_bug.cgi?id=97790
                    oSpellChecker = oGC.getSpellChecker()
                else:
                    oSpellChecker = SpellChecker("${lang}", "fr-allvars.bdic")
        except:
            traceback.print_exc()

    def execute (self, args):
        if not args:
            return
        try:
            sProdName, sVersion = helpers.getProductNameAndVersion()
            if (sProdName == "LibreOffice" and sVersion < "4") or sProdName == "OpenOffice.org":
                return

            # what event?
            bCorrectEvent = False
            for arg in args:
                if arg.Name == "Environment":
                    for v in arg.Value:
                        if v.Name == "EnvType" and v.Value == "DOCUMENTEVENT":
                            bCorrectEvent = True
                        elif v.Name == "EventName":
                            pass
                            # check is correct event
                            #print "Event: %s" % v.Value
                        elif v.Name == "Model":
                            model = v.Value
            if bCorrectEvent:
                if model.supportsService("com.sun.star.text.TextDocument"):
                    xController = model.getCurrentController()
                    if xController:
                        xController.registerContextMenuInterceptor(MyContextMenuInterceptor(self.ctx))
                        #print("OFF")
        except:
            traceback.print_exc()


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(JobExecutor, "grammalecte.ContextMenuHandler", ("grammalecte.ContextMenuHandler",),)
