#! /usr/bin/env monkeyrunner

import sys, os, time
majorAndr = sys.argv[1]
model = sys.argv[2]
folder_name = sys.argv[3]
isCrashExit = sys.argv[4]
pathname = os.path.dirname(sys.argv[0])        
currpath = os.path.abspath(pathname)
# this must be imported before MonkeyRunner and MonkeyDevice,
# otherwise the import fails
sys.path.append(currpath)
import adbcom_module
import mfuncs
os.chdir(currpath)
mfuncs.SetGlobVars(int(majorAndr), folder_name, model, isCrashExit)
(appPath, appName, build, branch, cmp) = adbcom_module.GetapkFile()

def run () :
    from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
    currentCarouselPanels = defaultCarouselPanels = 7
    defaultFloorPanels = 6
    WidgetSet = (16, 9, 2, 2)
    if model=='GT-I9100' or model=='m0' or model=='GT-N7000' or model=='t03g' or 2.3 > float(andr):
        WidgetSet = (16, 8, 2, 2)
    print 'starting test'
    mfuncs.mAct('BACK', 2)
    time.sleep(1)
    mfuncs.addYandexWidgets(WidgetSet)
    mfuncs.mAct('BACK', 2)
    mfuncs.DialerContactsFavourites()
    mfuncs.DialerContacts()
    mfuncs.MessagesCheck()
    mfuncs.BrowserCheck()
    adbcom_module.ShellStart(appPath, cmp, 2)
    mfuncs.SearchCheck()

    #mfuncs.takePanelsToCarousel2(11, False)
    #mfuncs.addYandexWidgets()

    mfuncs.screenshotPanels(5)
    #widgetSettings
    #widgetWork

    currentCarouselPanels += defaultFloorPanels
    currentCarouselPanels += 4

    """
    mfuncs.addAndroidWidgets(5)

    mfuncs.screenshotCarouselPanels(currentCarouselPanels)

    """
    print ('Made ' +mfuncs.GetScreenshoted() +' screenshots')


try:
    run()

except:
    adbcom_module.trace2log(folder_name)
