#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module functions description
#	MakeResultFolder(): 
		#create result-folder in results folder with current date_time name; 
		#return datestr, folder_name
#	Run_adb(command): 
		#command - string for adb _command_; start adb process, exit on error; 
		#return adb answer
#	Get_wifi_ip(): 
		#return usb-UP ip to use in ConCmd.py
#	Get_device_info(): 
		#return full device name, android version, major android version, device-nick
#	UpdateLuaFile(fname, resultFolder, isScreenShot): 
		#Create Current.lua where are new resultFolder and isScreenShot values
#	GetRunner(): 
		#Start adb-server; 
		#return runner name
#	GetapkFile(): 
		#Retrieve *.apk file info, placed in the current folder; exit if the file cannot be found; 
		#return appPath, appName, build, branch, cmp
#       InstallAndStart(appPath, cmp, waits): 
		#Install, start appPath, wait for _waits_ seconds after launching
#	ColdStart(appPath, cmp, waits) :
		#Clean settings, start appPath, wait for _waits_ seconds after launching
#	WaitForResults(folder_name): 
		#Wait for /sdcard/resultfolder/report.txt 
		#exit and return 1 on success; wait 500sec and exit on falure
#	GetResults(folder_name): 
		#Copy all files from /sdcard/folder_name to PC results/folder_name, check there is *.bmp; 
		#exit on falure, remove the folder from device on success 
#	run_UIAuto(ip, file): 
		#Start UI_Auto script for _file_ - lua-file in LUAscripts folder 
#	UploadResults(pageName, device, runner, andr, datestr, resultFolder):
		#Create CurrentWiKi.py wich will perform uploading text and files of _pageName_ page in MonkeyRunner-results
#	ResizeWithPIL(folder_name):
		#Resize and compress all png files from folder_name, need PIL module installed

from string import strip, split, find, replace
import subprocess
import os
import sys
from time import sleep
import traceback

#-----------------------------------------------------------------------------------

def MakeResultFolder():
	import datetime
	t = datetime.datetime.today()
	datestr = t.strftime('%d.%m.%y')
	folder_name = t.strftime('%y.%m.%d') + '-' + t.strftime('%H.%M.%S')
	print 'folder name: ' + folder_name
	if not (os.path.exists('results')): os.mkdir('results')
	if not (os.path.exists('results/'+folder_name)): os.mkdir('results/'+folder_name)
	return (datestr, folder_name)


def Run_adb(command):
	comm = split(command)
	p = subprocess.Popen(['adb'] + comm[:], stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
	if (p[1].find('err') != -1) or (p[1].find('failed') != -1):
		sys.exit('-------adb ERRORS:-------\n' + p[1])
	return p[0]
	
	
def StartLogcat(folder_name, filename='Logcat.txt'):
	Run_adb('logcat -c')
	f = open('results/' + folder_name + '/' + filename, 'a', 0)
	f.write(folder_name)
	p = subprocess.Popen(['adb', 'logcat', '-v', 'time'], stdout = f)
	return (p, f)
	

def CheckLogcat(f, pos, folder_name, isCrashExit):
	str = ''
	f.seek(pos)
	lines = f.readlines()
	curpos = f.tell()
	#print curpos
	for index in range(len(lines)):
		isWinDeath = (lines[index].find('WIN DEATH') != -1) and ((lines[index].find('yandex') != -1) or (lines[index].find('shell3d') != -1))
		isC = (lines[index].find('*** ***') != -1)
		isJava = (lines[index].find('FATAL EXCEPTION') != -1)
		if isWinDeath or isC or isJava:	
			str += lines[index] + lines[index+1]
	if (str  != '') :
		fn = open('results/' + folder_name + '/logcat-extracts.txt', 'a', 0)	
		fn.write(str)
		fn.close
		if isCrashExit :
			f.close
			sys.exit('-------Exiting from test...Logcat ERRORS:-------\n' + str)
		else : 
			print '-------Test will be continue...Logcat ERRORS:-------\n' + str
	return curpos
	

def LoopOfCheckingLogcat(folder_name, isCrashExit, logname='logcat.txt'):
	pos = 0
	try :
		f = open('results/' + folder_name + '/' + logname, 'r', 0)
		sleep(7)
		for i in range(300):
			posNew = CheckLogcat(f, pos, folder_name, isCrashExit)
			if (posNew != pos) :
				sleep(5)
				pos = posNew
			else :
				f.close
				print 'Logcat monitoring has been stoped.'
				break
	except :
		print 'Logcat monitoring has been stoped.'
		trace2log(folder_name)


def CheckShellCrash(folder_name) :
	if (os.path.exists('results/'+folder_name+'/logcat-extracts.txt')) :
		return True
	else:
		return False


def StopLogcat(p, f):
	if p.poll() is None: p.kill() #check if logging is not terminated by python exception.systemExit
	f.close 
	print "Logcat is ready!"
	

def trace2log(folder_name):
    error_desc = "-------!!!Unexpected error during test!!!-------:\n" 
    error_str = traceback.format_exc()
    print error_desc
    print str(sys.exc_info()[0]) +"\n" + str(sys.exc_info()[1])
    f = open('results/' + folder_name + '/traceback.txt', 'a', 0)
    f.write(error_desc)
    f.write(error_str)
    f.close


def Get_wifi_ip():   
	output = split(Run_adb('shell netcfg'), '\n')	
	for ln in output:
		if len(ln) == 0:
			continue
		columns = split(ln)
		conn_id = columns[0]
		conn_stat = columns[1]
		if ((conn_id.find('usb') != -1) and (conn_stat == 'UP')):
			return columns[2]
	print "Mobile IP is not detected! Mail to nadya-ali with device - adb shell netcfg - logs"
	return '127.0.0.1'

    
def Get_device_info():   
	manuf = dev = model = andr = ''
	output = split(Run_adb('shell getprop'), '\n')
	for ln in output:
		if len(ln) == 0:
			continue
		columns = split(ln, ':')
		if (not manuf) and (columns[0].find('product.manufacturer') != -1): 
			manuf = strip(columns[1])
			continue
		if (not dev) and (columns[0].find('product.device') != -1): 
			dev = strip(columns[1])
			continue
		if (not model) and (columns[0].find('product.model') != -1): 
			model = strip(columns[1])
			continue
		if (not andr) and (columns[0].find('build.version.release') != -1):
			andr = strip(columns[1])
	device = (manuf + ' ' + dev + ' ' + model).replace("[", "").replace("]", "")
	dev = (dev).replace("[", "").replace("]", "")
	andr = andr.replace("[", "").replace("]", "")
	majorAndr = split(andr, '.')[0]
	print 'device full name: ' + device + '\ndevice: ' + dev + '\nandroid: ' + andr + '\nmajorAndr: ' + majorAndr
	return (device, andr, majorAndr, dev)


def UpdateLuaFile(fname, resultFolder, isScreenShot):
	if os.path.exists(fname) : 
		f = open( fname, 'r' )
		fout = open('current.lua', 'wt')
		fout.write("local resultFolder = '" + resultFolder + "'\n")
		fout.write("local isScreenShot = " + isScreenShot + "\n")
		for line in f:
			if ((line.find('local resultFolder') == -1) and (line.find('local isScreenShot') == -1)): fout.write( line )
		f.close()
		fout.close()
	else :
		sys.exit('-------LUA-file script ERROR:\n-------' + fname + ' cannot be found!')

def GetRunner():
	import getpass
	subprocess.call(['adb', 'start-server'])
	if (os.path.exists('traceback.txt')): os.remove('traceback.txt')
	runner = getpass.getuser()
	print 'runner: ' + runner
	return (runner)


def GetapkFile():
	for files in os.listdir("."):
    		if files.endswith(".apk"):
			appPath = files
			appName = os.path.splitext(files)[0]
			build = split(appName, '-v')[-1].replace("v", "")
			build = split(build, '-')[0]
			build = split(build)[0]
			branch = split(appName, '-v')[0]
			if appName.find('shell3d') != -1:
				cmp = 'com.spb.shell3d'
			else:
				cmp = 'ru.yandex.shell'	
			print "appName: " + appName + "\nbuild: " + build + "\nbranch: " + branch + "\ncmp: " + cmp
        		return (appPath, appName, build, branch, cmp)
	sys.exit('------- .apk file not found!-------')


def InstallAndStart(appPath, cmp, waits) :
	print 'Installing ' + appPath + '... ' 
	print Run_adb('install -r ' + appPath)
	if (waits > 0) : ShellStart(appPath, cmp, waits)


def ShellStart(appPath, cmp, waits) :
	print 'Starting ' + appPath + '... ' 
	print Run_adb('shell am start -W -a android.intent.action.Main -n ' + cmp + '/.HomeAlias2')
	sleep(waits)


def ColdStart(appPath, cmp, waits) :
	print 'Cold start ' + appPath + '... ' 
	print Run_adb('shell pm clear ' + cmp)
	ShellStart(appPath, cmp, waits)


def WaitForResults(folder_name) :
	from time import sleep
	print 'waiting for /sdcard/' + folder_name + '/report.txt...'
	for i in range(200) :
		Run_adb('pull /sdcard/' + folder_name + '/report.txt results/' + folder_name + '/report.log')
		if os.path.exists('results/' + folder_name + '/report.log') : 
			return 1
		else :
			sleep(5)
	sys.exit('-------Results ERROR-------:\nResult folder cannot be found on mobile!')


def GetResults(folder_name) :
	print 'Copying results from /sdcard/' + folder_name + '...'
	Run_adb('pull /sdcard/' + folder_name + ' results/' + folder_name)
	for files in os.listdir('results/' + folder_name):
		if (files.endswith('.bmp')) or (files.endswith('.png')): 
			Run_adb('shell rm /sdcard/' + folder_name + '/*')
			Run_adb('shell rmdir /sdcard/' + folder_name)
			return 1
	sys.exit('-------Results ERROR-------:\nResults cannot be found on mobile!')


def push_file(path):
	import posixpath
	basename = os.path.basename(path)
	remotepath = posixpath.join("/sdcard", basename)
	p = subprocess.Popen(['adb', 'push', path, remotepath])
	p.wait()
	if p.returncode == 0:
		return remotepath
	return None


def run_UIAuto(ip, file):
	remote_path = push_file(file)
	if remote_path is None: sys.exit('-------Push failed!-------')
	concmd_path = os.path.join(os.path.dirname(sys.argv[0]), "ConCmd.py")
	ip_arg = ["-i", ip] if ip else []
	subprocess.Popen(["python", concmd_path] + ip_arg + ["uiscript", remote_path]).wait()


def ResizeWithPIL(folder_name) :
	resultPath = os.path.abspath('results/' + folder_name)
	if not (os.path.exists(resultPath)):
		print 'Result folder ' + resultPath + ' cannot be found!'
		sys.exit(1)
	if ResizeImgs(resultPath) : print 'Size of images is changed successfuly!'


def ResizeImgs(resultPath) :
	try:
		import Image
	except:
		sys.exit('PIL module cannot be found! Please, install from https://developers.google.com/appengine/docs/python/images/installingPIL')
	print 'PIL import is ok'
	basewidth = 320
	isOK = False
	for infile in os.listdir(resultPath) :
		if infile.endswith(".png") :
			im = Image.open(os.path.abspath(resultPath + '/' + infile))
			wpercent = (basewidth / float(im.size[0]))
			hsize = int((float(im.size[1]) * float(wpercent)))
			im = im.resize((basewidth, hsize))
			im.save(resultPath + '/0' + infile, "PNG", quality = 100)
			os.remove(resultPath + '/' + infile)
			isOK = True
	return isOK


#-----------------------------------------------------------------------------------

def StartMonkey(folder_name, nEvents, cmp) :
	print 'Starting Monkey test for ' + nEvents + ' events ...'
	f = open('results/' + folder_name + '/monkey' + nEvents + '.txt', 'a', 0)
	p = subprocess.Popen(['adb', 'shell', 'monkey', '-p', cmp, '-c', 'android.intent.category.HOME', '-v', '-v', '-v', nEvents], stdout = f, stderr = subprocess.PIPE).communicate()
	if (p[1].find('err') != -1) or (p[1].find('failed') != -1):
		sys.exit('-------adb ERRORS:-------\n' + p[1])
	print 'Monkey test for ' + nEvents + ' events is finished successfully!'
	
def toBase64(fpath):
	f = open(fpath, "rb")
	data = f.read()
	return data.encode("base64")

def UploadMonkeyResults(pageName, testresults, folder_name):
	import xmlrpclib
	pageName = 'MonkeyResults'
	pagePath = '/shelltesting/Autotests/Monkey/' + pageName
	print 'Uploading results to http://wiki.yandex-team.ru' + pagePath + '...'
	s = xmlrpclib.ServerProxy("https://wiki.yandex-team.ru/_api/xmlrpc/")
	auth = s.rpc.login("_rpc_mobileshell", "JkxmnM2s9A")

	src = s.pages.getSrc(auth, pagePath)
	lines = split(src, '\n')	
	head = text = ''
	for index in range(len(lines)):
		if index < 2:
			head += lines[index] + '\n'
		else :
			text += lines[index] + '\n'
	print head, testresults, text
	print 'Uploading results...'
	for file in os.listdir('results/' + folder_name):
		fname = split(file, '.')[0]
		newname = 'results/' + folder_name + '/' + fname + '-' + folder_name + '.txt'
		print s.pages.addFile(auth, pagePath, newname, toBase64('results/' + folder_name + '/' + file))	
	print s.pages.save(auth, pagePath, head+testresults+text, False, "XML-RPC test")
				
				
def UploadMonkeyRunnerResults(pageName, testresults, folder_name):
	import xmlrpclib
	pagePath = '/shelltesting/Autotests/MonkeyRunner/Results/' + pageName
	print 'Uploading results to http://wiki.yandex-team.ru' + pagePath + '...'
	s = xmlrpclib.ServerProxy("https://wiki.yandex-team.ru/_api/xmlrpc/")
	auth = s.rpc.login("_rpc_mobileshell", "JkxmnM2s9A")
	imlist = s.pages.getFiles(auth, pagePath)
	for im in imlist :
		s.pages.deleteFile(auth, pagePath, im["url"])
	text = '%%(csv delimiter=; head=1; wrapper=page wrapper_width=1600)\n' + \
	'Device;OS version;Version;Branch;Build;Screenshots;Result;Test Date;Tested by;Logcat;Comments	\n' + \
	testresults + '\n%%\n\n' + PNGTable(folder_name)
	print s.pages.save(auth, pagePath, text, False, "XML-RPC test")
	for file in os.listdir('results/' + folder_name):
		print s.pages.addFile(auth, pagePath, file, toBase64('results/' + folder_name + '/' + file))	
	
	
	
def PNGTable(folder_name) :
	i = 0
	text = "%%(csv delimiter=;)\n"
	for file in os.listdir('results/' + folder_name):
    		if file.endswith('.png'):
			fname = split(file, '.')[0]
			i += 1
			text += fname + ' --- file:' + file + ';'
			if i == 4 : 
				text += ' \n'
				i = 0
	text += "\n%%"
	return text
	
	
def UploadLoadingResults(device_name, testresults, log):
	import xmlrpclib
	pageName = device_name.replace(" ", "").lower()
	pagePath = '/shelltesting/autotests/loadingtest/' + pageName
	print 'Uploading results to http://wiki.yandex-team.ru' + pagePath + '...'
	s = xmlrpclib.ServerProxy("https://wiki.yandex-team.ru/_api/xmlrpc/")
	auth = s.rpc.login("_rpc_mobileshell", "JkxmnM2s9A")
	
	pageslist = s.pages.getChildren(auth, '/shelltesting/autotests/loadingtest')
	if pagePath in pageslist : 
		src = s.pages.getSrc(auth, pagePath)
		lines = split(src, '\n')	
		if len(lines) > 1 :
			head = text = ''
			for index in range(len(lines)):
				if index < 2:
					head += lines[index] + '\n'
				else :
					text += lines[index] + '\n'
			print head, testresults, text
			resultsrc = head+testresults+text
		else : resultsrc = CreatePage(testresults)
	else : resultsrc = CreatePage(testresults)
	print 'Uploading results...'
	print resultsrc
	if log != '' : 
		print s.pages.addFile(auth, pagePath, log, toBase64(log))	
	print s.pages.save(auth, pagePath, resultsrc, True, device_name)
				
				 
def CreatePage(testresults) :
	head = '%%(csv delimiter=; head=1; wrapper=page wrapper_width=1800)\n'
	head += 'Android;Version;Branch;Build;Test result;Type of loading;Loading time;Range;7 Longest---components;;;;;;;'
	head += 'Number---of loading;Test Date;Tested by\n'
	text = '\n%%\n* Loading time is calculated as average between all loadings for current test\n'
	text += '* For 7 longest components taken maximum time for the current component between all loadings '
	text += 'for the current test\n'
	text += '* More results and log-files you can find in results folder on your PC'
	return head+testresults+text

