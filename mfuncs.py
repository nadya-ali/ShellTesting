import time
import os, sys, re
pathname = os.path.dirname(sys.argv[0])
currpath = os.path.abspath(pathname)
sys.path.append(currpath)

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

device = MonkeyRunner.waitForConnection()
if not device:
	raise Exception('Cannot connect to device')
(height, width, density) = (int(device.getProperty('display.height')), int(device.getProperty('display.width')), float(device.getProperty('display.density')))
screenshoted = 1
majorAndr, folder_name, model, isCrashExit = 1, '', '', True
statusBarHeight = int(25 * density)
print density


def SetGlobVars(majorAndr_, folder_name_, model_, isCrashExit_) :
	global majorAndr, folder_name, model, isCrashExit
	majorAndr, folder_name, model = majorAndr_, folder_name_, model_
	if isCrashExit_ == 'False' : isCrashExit = False


def intOst(a, b):
	intPart = int(a/b)
	ostPart = a - b*intPart
	return intPart, ostPart


def GetError(st):
	error_desc = "-------!!!Unexpected error! It is not possible " + st + "! :-------\n" 
	error_desc += str(sys.exc_info()[0]) +" --- " + str(sys.exc_info()[1]) + "\n"
	error_desc += "Probably, device was disconnected"
	return error_desc


def mAct(action, count):
	try:
		for county in range(count): 
			device.press('KEYCODE_'+action)
			time.sleep(0.5)
		return()
	except:
		sys.exit(GetError("to press on screen"))


def CheckShellCrash() :
	if (os.path.exists('results/'+folder_name+'/logcat-extracts.txt')) :
		if isCrashExit :
			sys.exit('-------Yandex.shell crash was detected!-------')


def screenshot(name_append):
	#makes a screenshot saved to results/[folder_name] with provided appendix
	global screenshoted
	CheckShellCrash()
	try:
		if (screenshoted!=-1):
			name = currpath + '/results/' + folder_name + '/' + GetName() + model + name_append + '.png'
			result = device.takeSnapshot()
			result.writeToFile(name, 'png')
			screenshoted += 1
		return screenshoted
	except:
		print '!!!!!!!!!!!!!!!!!! worked!'
		sys.exit(GetError("to make screenshot"))


def GetName() :
	if screenshoted < 10 :
		return '00' + str(screenshoted) + '-'
	elif screenshoted < 100 :
		return '0' + str(screenshoted) + '-'
	else :
		return str(screenshoted) + '-' 


def GetScreenshoted() :	
	return str(screenshoted - 1)


def ScaleByDensity(x) :
	return int(x*density*160/120)


def xyHomeBt() :
	return (width/2, height*9/10)


def xyCenterMenuBt() :
	return (width/2, height-10)


def xyLeftMenuBt() :
	return (10, height-10)


def xyLeft2MenuBt() :
	return (int(width*3/8), height-10)


def xyRight2MenuBt() :
	return (int(width*5/8), height-10)


def xyRightMenuBt() :
	return (width-10, height-10)


def DragSlider() :
	device.drag(xyCenterMenuBt(), (width-10, height-10))
	time.sleep(1)

def SwitchToLastPanel() :
	device.drag(xyHomeBt(), (width-10, height*9/10))
	time.sleep(1)


def SlideRight() :
	try:
		device.drag((width*8/10, height/2), (width*2/10, height/2))
		time.sleep(0.5)
	except:
		sys.exit(GetError("to perform guest"))


def SlideLeft() :
	try:
		device.drag((width*2/10, height/2), (width*8/10, height/2))
		time.sleep(0.5)
	except:
		sys.exit(GetError("to perform guest"))


def TapAndHold(x, y) :
	device.drag((x, y), (x, y), 1, 1)


def PressXY(xy) :
	device.touch(xy[0], xy[1], MonkeyDevice.DOWN_AND_UP)
	time.sleep(1)


def SelectYandexHomeByDefault() :
	mAct('HOME', 1)
	time.sleep(1)
	mAct('DPAD_RIGHT', 2)
	mAct('ENTER', 1)
	time.sleep(0.5)
	mAct('DPAD_DOWN', 1)
	mAct('DPAD_LEFT', 1)
	time.sleep(0.5)
	mAct('ENTER', 1)
	time.sleep(0.5)


def OpenCarousel() :
	SwitchToLastPanel()
	PressXY(xyHomeBt())
	PressXY(xyHomeBt())


def openShellSettings(): 
	#opens Shell Settings from homescreen (launcher panel or static one - no matter). Option placement differs on Froyo and HC+ devices
	if majorAndr > 2:
		device.press('KEYCODE_MENU')
		time.sleep(3)
		mAct('DPAD_DOWN', 8)
		device.press('KEYCODE_DPAD_UP')
		device.press('KEYCODE_ENTER')
	else:
		device.press('KEYCODE_MENU')
		time.sleep(3)
		mAct('DPAD_DOWN', 5)
		device.press('KEYCODE_DPAD_LEFT')
		device.press('KEYCODE_ENTER')
	return()


def openManagePanels2():
	"""
	opens Manage Panels from homescreen for Yandex.shell 2.0
	"""
	OpenCarousel()
	PressXY(xyRightMenuBt())


def takePanelsToCarousel2(count, isDefaulted):
	"""
	moves all floor panels to default position (the most left panel is on screen) and lifts up [count] panels
	"""
	CheckShellCrash()
	try:
		openManagePanels2()
		time.sleep(1)
		screenshot('-ManagePanelsStart')
		if not isDefaulted:
			device.drag((width/5,height*3/5), (width*4/5,height*3/5))
			time.sleep(1)
		for county in range(count):
			device.drag((width/5,height*3/5), (width/5,height*1/5))
			time.sleep(1)
		screenshot('-ManagePanelsEnd')
		PressXY(xyLeftMenuBt())
		mAct('BACK', 1)
		time.sleep(1)
		return count
	except:
		sys.exit(GetError("to edit panels"))


def screenshotPanels(count):
	"""
	makes screenshots of [count] panels starting from current one and going to the right
	"""
	CheckShellCrash()
	SwitchToLastPanel()
	screenshot('-homepanels-last')
	for county in range(count):
		SlideLeft()
		screenshot('-homepanels'+str(county))
	return ()


def screenshotCarouselPanels(count):
	"""
	makes screenshots of [count] panels in carousel mode starting from current one and going to the right
	"""
	CheckShellCrash()
	PressXY(xyCenterMenuBt())
	screenshot('-carousel'+str(count))
	for county in range(3):
		panelInCarousel('-carousel', 1)
		panelInCarousel('-carousel', 0)
	for county in range(2):
		panelInCarousel('-carousel', 1)
	for county in range(4):
		panelInCarousel('-carousel', 0)
	for county in range(4):
		panelInCarousel('-carousel', 2)
		panelInCarousel('-carousel', 1)
		panelInCarousel('-carousel', 0)
	PressXY(xyCenterMenuBt())
	return ()


def panelInCarousel(name, nAnimation):
	CheckShellCrash()
	SlideRight()
	screenshot(name)
	if (nAnimation > 0) :
		for county in range(nAnimation):
			time.sleep(3)
			screenshot(name+'-animation')
			time.sleep(2.5)
	return ()


def PageUp(dy) :
	device.drag((width/2, dy), (width/2, 0), 2, 10) 	
	time.sleep(1)


def addYandexWidgets(WidgetSet):
	CheckShellCrash()
	PressXY(xyRightMenuBt())
	screenshot('-Launcher-app')
	PressXY(xyCenterMenuBt())
	screenshot('-Launcher-wid1')
	WidgetsAdded = 0
	for p in range(2):
		for cl in range(5):
			for r in range(2):
				if (WidgetsAdded < WidgetSet[0]):
					SelectYandexWidget(r, cl)
					WidgetsAdded += 1
		SlideRight()

def SelectIndicator(r) :
	y = ScaleByDensity(44) * r
	x = int(density*160) 
	PressXY([width/2 + x, y])
	time.sleep(0.2)

def SelectYandexWidget(r, cl) :
	PressXY([ScaleByDensity(118+132*r), ScaleByDensity(81+78*cl)])
	time.sleep(0.5)

def AddContact() :
	y = ScaleByDensity(44) 
	print width/2, y*7
	PressXY([width/2, y*7])
	time.sleep(0.5)
	screenshot('-contacts')
	PressXY([width/2, y])
	time.sleep(1)
	screenshot('-a-contact-is-added')


def AddAndroidWid(r) :
	for i in range(3):
		PressXY(xyRightMenuBt())
		PressXY(xyCenterMenuBt())
		device.drag((width/2, height/2), (width/2, 0), 0.2, 5) 	
		time.sleep(3)
		y = ScaleByDensity(44) 
		PressXY([width/2, y*r])
		time.sleep(0.5)
		if i==0 :	screenshot('-Android-wid-list')
		PressXY([width/2, y*(2+i)])
		time.sleep(0.5)
		mAct('BACK', 1)
		time.sleep(1)	
		screenshot('-Android-wid-on-panel')


def SearchCheck() :
	PressXY(xyRight2MenuBt())
	time.sleep(1)
	screenshot('-YaSearch')
	device.type('spb')
	time.sleep(3)
	screenshot('-YaSearch-results')
	xY = ScaleByDensity(18)
	yY = ScaleByDensity(22)
	PressXY([xY, statusBarHeight+yY])
	time.sleep(0.5)
	screenshot('-YaSearch-panel')
	x = ScaleByDensity(65) 
	y = ScaleByDensity(57) 
	for i in range(8) :
		if i < 4 : r = 1
		else : r = 2
		if r == 1 : c = i + 1
		else : c = i - 3
		PressXY([x*c - int(x/2), y*r + statusBarHeight - int(y/2)])
		time.sleep(1.5)
		screenshot('-YaSearch-panel')
		mAct('BACK', 1)
		time.sleep(1)	
	PressXY([xY, y*2 + statusBarHeight + yY])
	time.sleep(0.5)	
	screenshot('-YaSearch-collapsed-panel')
	PressXY([width-xY, statusBarHeight + yY])
	time.sleep(1)	
	screenshot('-YaSearch-result')
	mAct('BACK', 1)
	time.sleep(0.5)	
	PressXY([width-xY*3, statusBarHeight + yY])
	screenshot('-YaSearch-voice')
	mAct('BACK', 1)
	time.sleep(0.5)	
	mAct('BACK', 1)
	time.sleep(0.5)	
	screenshot('-YaSearch-clear')
	mAct('BACK', 1)
	time.sleep(1)	


def BrowserCheck() :
	PressXY(xyCenterMenuBt())
	time.sleep(2)
	screenshot('-Browser-button-work')
	mAct('HOME', 1)
	time.sleep(1)	


def MessagesCheck() :
	PressXY(xyLeft2MenuBt())
	time.sleep(1)
	screenshot('-Messages-button-work')
	mAct('HOME', 1)
	time.sleep(1)


def DialerContactsFavourites() :
	PressXY(xyLeftMenuBt())
	time.sleep(1)
	screenshot('-Dialer-button-work')
	x1 = ScaleByDensity(44) #1st favourite contact
	y1 = ScaleByDensity(53) + statusBarHeight
	TapAndHold(x1, y1)
	screenshot('-FavContact-contextmenu')
	dy = ScaleByDensity(37.5) #of context-menu item
	dy_m = ScaleByDensity(41) #botton menu
	y_start = int((height - dy_m - statusBarHeight - dy * 5) / 2 ) #of the top point context-menu
	y_openCard = y_start + int(dy * 1.5)
	time.sleep(2)
	PressXY([int(width/2), y_openCard])
	time.sleep(2)
	screenshot('-contact-card')
	#test contact card
	mAct('BACK', 1)

	TapAndHold(x1, y1) #1st fav. contact.
	time.sleep(1)
	PressXY([int(width/2), y_openCard + dy])
	screenshot('-contact-message')
	#test contact messaging
	mAct('HOME', 1)
	time.sleep(0.5)

	PressXY(xyLeftMenuBt())
	TapAndHold(x1, y1)
	PressXY([int(width/2), y_openCard + dy*2])
	time.sleep(1)
	screenshot('-contact-remove-from-fav')

	TapAndHold(x1, y1) #1st fav. contact.
	screenshot('-contact-empty-contextmenu')
	PressXY([int(width/2), int(height/2)])
	time.sleep(1)
	screenshot('-contact-change-fav')

	device.drag((width/2, y1), (x1, y1), 2, 10) 	
	time.sleep(1)
	mAct('BACK', 1)
	screenshot('-contact-moved-fav')

	device.drag((width/2, height - dy_m - statusBarHeight - 5), (width/2, statusBarHeight + 5), 2, 10) 	
	time.sleep(1)
	screenshot('-Favourite-contacts2')
	mAct('HOME', 1)
	time.sleep(1)


def DialerContacts() :
	PressXY(xyLeftMenuBt())
	time.sleep(1)
	PressXY(xyLeft2MenuBt())
	screenshot('-Dialer-Contacts')
	x1 = ScaleByDensity(25) #..., picture button
	y1 = ScaleByDensity(88/2) + statusBarHeight
	PressXY([width - x1, y1])
	time.sleep(2)
	screenshot('-Contact-Card')

	y2 = ScaleByDensity(24) + statusBarHeight #1st line
	xM = width - ScaleByDensity(11) #...
	xF = width - ScaleByDensity(40) #star
	xP = ScaleByDensity(40) #picture

	PressXY([xP, y2])
	time.sleep(0.5)
	screenshot('-Contact-Change-Picture')
	mAct('BACK', 1)
	time.sleep(0.3)

	PressXY([xF, y2])
	time.sleep(1)
	screenshot('-Contact-Changed-Favourite')

	ContactCardMenu(xM, y2)
	yS = height - ScaleByDensity(67) #serch
	PressXY([width - 20, yS])
	PressXY([int(width/2), yS])
	mAct('BACK', 1)
	time.sleep(0.5)

	#device.type('spb')
	time.sleep(2)
	screenshot('-Contact-Serch-Favourite')

	PressXY(xyRight2MenuBt())
	time.sleep(0.5)
	screenshot('-Contact-Calllog')

	PressXY(xyRightMenuBt())
	time.sleep(0.5)
	screenshot('-Contact-DialerPad')
	mAct('HOME', 1)
	time.sleep(0.3)


def ContactCardMenu(x, y) :
	time.sleep(10)
	PressXY([x, y])
	time.sleep(1)
	screenshot('-Contact-Card-menu')

	dy_m = ScaleByDensity(238)
	y_m = int((height - dy_m) / 2)
	dy_mI = ScaleByDensity(38)
	x_m = int(width / 2)
	PressXY([x_m, y_m + dy_mI]) #press Edit contact
	time.sleep(1)
	screenshot('-Contact-Edit')
	mAct('BACK', 1)
	time.sleep(1)
	"""	
	PressXY([x, y])
	time.sleep(0.5)
	PressXY([x_m, y_m + dy_mI*2]) #press Merge contact
	time.sleep(6)
	screenshot('-Contact-Merge')
	PressXY([x, y])
	time.sleep(3)
	"""

	PressXY([x, y])
	time.sleep(1)
	PressXY([x_m, y_m + dy_mI*3]) #press send contact
	time.sleep(1)
	screenshot('-Contact-Send')
	mAct('BACK', 1)
	time.sleep(0.5)

	PressXY([x, y])
	time.sleep(0.5)
	PressXY([x_m, y_m + dy_mI*4]) #press ringtones
	time.sleep(0.3)
	screenshot('-Contact-Ringtone_menu')
	mAct('BACK', 1)
	time.sleep(0.5)

	PressXY([x, y])
	time.sleep(0.5)
	PressXY([x_m, y_m + dy_mI*5]) #press delete
	time.sleep(0.3)
	screenshot('-Contact-delete')
	mAct('BACK', 1)
	time.sleep(0.3)

#-------------------------------------------------------------------------------------------------------------------------------------

def openAddDialog(): #old
	if majorAndr > 2:
		device.press('KEYCODE_MENU')
		time.sleep(1)
		mAct('DPAD_UP', 8)
		device.press('KEYCODE_ENTER')
	else:
		device.press('KEYCODE_MENU')
		time.sleep(1)
		mAct('DPAD_UP', 5)
		device.press('KEYCODE_DPAD_LEFT')
		device.press('KEYCODE_ENTER')
	return()


def addSpbWidgetDialog(): #old
	openAddDialog()
	time.sleep(1)
	device.touch(width/6, height/2+10, MonkeyDevice.DOWN_AND_UP)
	return()


def addAndroidWidgetDialog(): #old
	openAddDialog()
	time.sleep(1)
	device.touch(width/2, height/2+15, MonkeyDevice.DOWN_AND_UP)
	return()


def addSpbWidgets(count): #old
	CheckShellCrash()
	cellHeight = ScaleByDensity(46)
	startPos = ScaleByDensity(35 + 19)
	startBottomPos = ScaleByDensity(43)
	if count<14:
		bookmarksToAdd = 0
	else:
		bookmarksToAdd = 1
	bookmarksAdded = 0
	widgetsPerScreen = (height-startPos-startBottomPos)/cellHeight
	(scrollCounts, widgetsFromBottom) = intOst(count-1, widgetsPerScreen)
	widgetsOnPreLastPanel = intOst(scrollCounts*widgetsPerScreen, 6)[1]-bookmarksToAdd
	for counter in range(scrollCounts*widgetsPerScreen-bookmarksToAdd):
		countWidget = counter - int(counter/widgetsPerScreen)*widgetsPerScreen
		SelectSPBWidget(cellHeight*widgetsPerScreen+startPos, startPos+cellHeight*(2*countWidget+1)/2, int(counter/widgetsPerScreen), startPos)
		if counter==9:
			time.sleep(3)
			device.touch(width/2, int(height*2/7), MonkeyDevice.DOWN_AND_UP)
			time.sleep(1)
		if (counter, bookmarksAdded)==(13, 0):
			SelectSPBWidget(cellHeight*widgetsPerScreen+startPos, startPos+cellHeight*(2*countWidget+1)/2, int(counter/widgetsPerScreen), startPos)
			bookmarksAdded = 1
		if float(counter+1+bookmarksAdded)/6==(counter+1+bookmarksAdded)/6:
			screenshot('-SPBPanels')
		SlideRight()
	if widgetsOnPreLastPanel+widgetsFromBottom > 5:
		screenshot('-SPBPanels')
	SlideRight()
	for counter in range(count - scrollCounts*widgetsPerScreen):
		SelectSPBWidget(cellHeight*widgetsPerScreen+startPos, startPos+cellHeight*(widgetsPerScreen-counter)-15, scrollCounts, startPos)
		screenshot('-SPBPanels')
	return ()


def SelectSPBWidget(yd, yt, count, startPos) : #old
	addSpbWidgetDialog()
	time.sleep(1)
	for dragy in range(count):
			device.drag((width/2, yd), (width/2, startPos-8), 2)
			time.sleep(1)
	device.touch(width/2, yt, MonkeyDevice.DOWN_AND_UP)
	time.sleep(1)
	return ()


def addAndroidWidgets(count): #old
	CheckShellCrash()
	for counter in range(count):
		addAndroidWidgetDialog()
		time.sleep(1.5)
		mAct('DPAD_DOWN', 2*counter+1)
		mAct('ENTER', 1)
		time.sleep(2.5)
		mAct('BACK', 1)
		time.sleep(1)
		screenshot('-SPBPanels')
	return ()

def takePanelsToCarousel(count, isDefaulted): #old
	"""
	moves all floor panels to default position (the most left panel is on screen) and lifts up [count] panels
	"""
	CheckShellCrash()
	try:
		openManagePanels()
		time.sleep(1)
		screenshot('-ManagePanelsStart')
		if not isDefaulted:
			for counter in range(5):
				device.drag((width/5,height*3/5), (width,height*3/5))
				time.sleep(1)
		for county in range(count):
			device.drag((width/5,height*3/5), (width/5,height*1/5))
			time.sleep(1)
		screenshot('-ManagePanelsEnd')
		device.touch(5, height-5, MonkeyDevice.DOWN_AND_UP)
		time.sleep(1)
		return count
	except:
		sys.exit(GetError("to edit panels"))


def openManagePanels(): #old
	"""
	opens Manage Panels from homescreen (launcher panel or static one - no matter). Option placement differs on Froyo and HC+ devices
	"""
	if majorAndr > 2:
		device.press('KEYCODE_MENU')
		time.sleep(3)
		mAct('DPAD_DOWN', 8)
		mAct('DPAD_UP', 4)
		device.press('KEYCODE_ENTER')
	else:
		device.press('KEYCODE_MENU')
		time.sleep(3)
		mAct('DPAD_UP', 5)
		device.press('KEYCODE_DPAD_RIGHT')
		device.press('KEYCODE_ENTER')
	return()


