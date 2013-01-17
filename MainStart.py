#! /usr/bin/env monkeyrunner

import subprocess
import os, sys, traceback
from time import sleep
from threading import Thread
import adbcom_module

#True - if exit after Shell Crash, False - if continue test after Shell crash
isCrashExit = False
runner = adbcom_module.GetRunner()	
pathname = os.path.dirname(sys.argv[0])        
(appPath, appName, build, branch, cmp) = adbcom_module.GetapkFile()
(device_name, andr, majorAndr, model) = adbcom_module.Get_device_info()
(datestr, folder_name) = adbcom_module.MakeResultFolder()
adbcom_module.InstallAndStart(appPath, cmp, 0)
#p1 - 1st process, which is writing logcat and should be killed
(p1, fL) = adbcom_module.StartLogcat(folder_name)

def run () :
    adbcom_module.ColdStart(appPath, cmp, 35)
    #t2 - 2d process=thread, which is checking logcat for Yandex.shell crashed and will be finished when 1st process will be killed
    t2 = Thread(target=adbcom_module.LoopOfCheckingLogcat, args=(folder_name, isCrashExit))
    t2.start()

    #3d process+thread, which is starting Monkey or MonkeyRunner test and should be stopped when 2d process is finished
    #StartMonkey(t2)
    StartMonkeyRunner(t2)


def StartMonkey(t2) :
    #continue test until Yandex.shell crash or Monkey test is finished or crashed
    testresults = device_name + ';' + andr + ';2.0;' + branch + ';' + build + ';'
    monkeyfiles = ''

    for n in ['500', '1000', '5000', '50000'] :
        adbcom_module.StartMonkey(folder_name, n, cmp)
        testresults += n + ' '
        monkeyfiles += 'file:monkey' + n + '-' + folder_name + '.txt'
        if (not t2.isAlive()) or (n == '50000') : break
        monkeyfiles += ' --- '

    monkeyfiles = 'file:logcat-' + folder_name + '.txt;' + monkeyfiles
    if not adbcom_module.CheckShellCrash(folder_name) :
        testresults += ';OK;'
    else :
        monkeyfiles = 'file:logcat-extracts-' + folder_name + '.txt --- ' + monkeyfiles
        testresults += ';!!FAILED!!;'
    testresults += datestr + ';staff:' + runner + ';' + monkeyfiles + '\n'
    adbcom_module.StopLogcat(p1, fL)
    print "Monkey test is finished!"
    t2.join()
    adbcom_module.UploadMonkeyResults('MonkeyResults', testresults, folder_name)

def StartMonkeyRunner(t2):
    print 'Starting MonkeyRunner ...'
    if pathname=='':
        script='MR_SmokeTest.py '
    else:
        script='"' + os.path.abspath(pathname+'/MR_SmokeTest.py') + '" '
    pageName = 'SmokeTest'
    testresults = device_name + ';' + andr + ';2.0;' + branch + ';' + build + ';'
    testresults += '((http://wiki.yandex-team.ru/shelltesting/Autotests/MonkeyRunner/Results/' +  pageName + ' ' + pageName + '));'
    try:
        subprocess.check_call('monkeyrunner '+script +majorAndr+' "'+model+'" '+folder_name+' '+str(isCrashExit), shell=True)
    except:
        adbcom_module.trace2log(folder_name)
        sys.exit('-------Monkeyrunner ERROR!-------\n')

    if not adbcom_module.CheckShellCrash(folder_name) :
        logcatfiles = ''
        testresults += 'OK;'
    else :
        logcatfiles = 'file:logcat-extracts.txt --- '
        testresults += '!!FAILED!!;'
    logcatfiles += 'file:logcat.txt; '
    testresults += datestr + ';staff:' + runner + ';' + logcatfiles
    if (os.path.exists('results/'+folder_name+'/traceback.txt')) :
        testresults += 'file:traceback.txt '
    adbcom_module.StopLogcat(p1, fL)
    print "Monkey test is finished!"
    adbcom_module.ResizeWithPIL(folder_name)
    adbcom_module.UploadMonkeyRunnerResults(pageName, testresults, folder_name)


try:
    run()

except:
    adbcom_module.StopLogcat(p1, fL)
    adbcom_module.trace2log(folder_name)

