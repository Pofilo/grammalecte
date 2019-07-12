# Helpers for LibreOffice extension

import os
import traceback
import subprocess

import uno

from com.sun.star.beans import PropertyValue
from com.sun.star.uno import RuntimeException as _rtex


def start_console ():
    "open console from APSO extension"
    try:
        ctx = uno.getComponentContext()
        ctx.ServiceManager.createInstance("apso.python.script.organizer.impl")
        # now we can import apso_utils library
        from apso_utils import console
        console()
    except:
        try:
            ctx = uno.getComponentContext()
            xSvMgr = ctx.getServiceManager()
            xPathSettings = xSvMgr.createInstanceWithContext("com.sun.star.util.PathSettings", ctx)
            spPyInstallion = uno.fileUrlToSystemPath(xPathSettings.Module)
            subprocess.Popen(spPyInstallion + os.sep + "python")  # Start Python interactive Shell
        except:
            traceback.print_exc()


def xray (xObject):
    "XRay - API explorer"
    try:
        sm = uno.getComponentContext().ServiceManager
        mspf = sm.createInstanceWithContext("com.sun.star.script.provider.MasterScriptProviderFactory", uno.getComponentContext())
        scriptPro = mspf.createScriptProvider("")
        xScript = scriptPro.getScript("vnd.sun.star.script:XrayTool._Main.Xray?language=Basic&location=application")
        xScript.invoke((xObject,), (), ())
        return
    except:
        raise _rtex("\nBasic library Xray is not installed", uno.getComponentContext())


def mri (ctx, xTarget):
    "MRI - API Explorer"
    try:
        xMri = ctx.ServiceManager.createInstanceWithContext("mytools.Mri", ctx)
        xMri.inspect(xTarget)
    except:
        raise _rtex("\nPython extension MRI is not installed", uno.getComponentContext())


def getConfigSetting (sNodeConfig, bUpdate=False):
    "get a configuration node"
    # example: xNode = getConfigSetting("/org.openoffice.Office.Common/Path/Current", False)
    xSvMgr = uno.getComponentContext().ServiceManager
    xConfigProvider = xSvMgr.createInstanceWithContext("com.sun.star.configuration.ConfigurationProvider", uno.getComponentContext())
    xPropertyValue = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    xPropertyValue.Name = "nodepath"
    xPropertyValue.Value = sNodeConfig
    if bUpdate:
        sService = "com.sun.star.configuration.ConfigurationUpdateAccess"
    else:
        sService = "com.sun.star.configuration.ConfigurationAccess"
    return xConfigProvider.createInstanceWithArguments(sService, (xPropertyValue,)) # return xNode


def printServices (o):
    for s in o.getAvailableServiceNames():
        print(' > '+s)


def getWindowSize ():
    "return main window size"
    xCurCtx = uno.getComponentContext()
    xDesktop = xCurCtx.getServiceManager().createInstanceWithContext('com.sun.star.frame.Desktop', xCurCtx)
    xContainerWindow = xDesktop.getCurrentComponent().CurrentController.Frame.ContainerWindow
    xWindowSize = xContainerWindow.convertSizeToLogic(xContainerWindow.Size, uno.getConstantByName("com.sun.star.util.MeasureUnit.POINT"))
    #print(xContainerWindow.Size.Width, ">", xWindowSize.Width)
    #print(xContainerWindow.Size.Height, ">", xWindowSize.Height)
    xWindowSize.Width = xWindowSize.Width * 0.666
    xWindowSize.Height = xWindowSize.Height * 0.666
    return xWindowSize


def getAbsolutePathOf (sPath=""):
    xDefaultContext = uno.getComponentContext().ServiceManager.DefaultContext
    xPackageInfoProvider = xDefaultContext.getValueByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
    sFullPath = xPackageInfoProvider.getPackageLocation("French.linguistic.resources.from.Dicollecte.by.OlivierR")
    if sPath and not sPath.startswith("/"):
        sPath = "/" + sPath
    sFullPath = sFullPath[8:] + sPath
    return os.path.abspath(sFullPath)
