def eyelinkChildFunction(
qTo
, qFrom
, windowSize = [200,200]
, windowPosition = [0,0]
, calibrationDisplayRes = [1920,1080]
, calibrationDisplayPosition = [1920,0]
, calibrationDotSize = 10
, eyelinkIP = '100.1.1.1'
, edfFileName = 'temp.edf'
, edfPath = './_Data/temp.edf'
, saccadeSoundFile = '_Stimuli/stop.wav'
, blinkSoundFile = '_Stimuli/stop.wav'
):
	import sdl2
	import sdl2.ext
	import sdl2.sdlmixer
	import pylink
	import numpy
	import sys
	import shutil
	import subprocess
	import time
	import os
	try:
		import appnope
		appnope.nope()
	except:
		pass


	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
	window = sdl2.ext.Window("eyelink",size=windowSize,position=windowPosition,flags=sdl2.SDL_WINDOW_SHOWN)
	windowID = sdl2.SDL_GetWindowID(window.window)
	windowSurf = sdl2.SDL_GetWindowSurface(window.window)
	sdl2.ext.fill(windowSurf.contents,sdl2.pixels.SDL_Color(r=255, g=255, b=255, a=255))
	window.refresh()

	for i in range(10):
		sdl2.SDL_PumpEvents() #to show the windows


	sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO)
	sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)
	class Sound:
		def __init__(self, fileName):
			self.sample = sdl2.sdlmixer.Mix_LoadWAV(sdl2.ext.compat.byteify(fileName, "utf-8"))
			self.started = False
		def play(self):
			self.channel = sdl2.sdlmixer.Mix_PlayChannel(-1, self.sample, 0)
			self.started = True
		def stillPlaying(self):
			if self.started:
				if sdl2.sdlmixer.Mix_Playing(self.channel):
					return True
				else:
					self.started = False
					return False
			else:
				return False

	saccadeSound = Sound(saccadeSoundFile)
	blinkSound = Sound(blinkSoundFile)

	def exitSafely():
		if 'eyelink'in locals():
			if eyelink.isRecording():
				eyelink.stopRecording()
			eyelink.setOfflineMode()
			eyelink.closeDataFile()
			eyelink.receiveDataFile('temp.edf','temp.edf')
			eyelink.close()
			if os.path.isfile('temp.edf'):
				print 'temp.edf exists'
				shutil.move('temp.edf', edfPath)
				if os.path.isfile(edfPath):
					print edfPath+' exists'
					subprocess.call('./edf2asc '+edfPath)
		sys.exit()

	#define a class for a clickable text UI
	class clickableText:
		def __init__(self,x,y,text,rightJustified=False,valueText=''):
			self.x = x
			self.y = y
			self.text = text
			self.rightJustified = rightJustified
			self.valueText = valueText
			self.isActive = False
			self.clicked = False
			self.updateSurf()
		def updateSurf(self):
			if self.isActive:
				self.surf = sdl2.sdlttf.TTF_RenderText_Blended_Wrapped(font,self.text+self.valueText,sdl2.pixels.SDL_Color(r=0, g=255, b=255, a=255),previewWindow.size[0]).contents
			else:
				self.surf = sdl2.sdlttf.TTF_RenderText_Blended_Wrapped(font,self.text+self.valueText,sdl2.pixels.SDL_Color(r=0, g=0, b=255, a=255),previewWindow.size[0]).contents
		def checkIfActive(self,event):
			if self.rightJustified:
				xLeft = self.x - self.surf.w
				xRight = self.x
			else:
				xLeft = self.x
				xRight = self.x + self.surf.w
			if (event.button.x>xLeft) & (event.button.x<xRight) & (event.button.y>self.y) & (event.button.y<(self.y+fontSize)):
				self.isActive = True
			else:
				self.isActive = False
			self.updateSurf()
		def draw(self,targetWindowSurf):
			if self.rightJustified:
				sdl2.SDL_BlitSurface(self.surf, None, targetWindowSurf, sdl2.SDL_Rect(self.x-self.surf.w,self.y,self.surf.w,self.surf.h))
			else:
				sdl2.SDL_BlitSurface(self.surf, None, targetWindowSurf, sdl2.SDL_Rect(self.x,self.y,self.surf.w,self.surf.h))

	#define a class for settings
	class settingText(clickableText):
		def __init__(self,value,x,y,text,rightJustified=False):
			self.value = value
			self.valueText = str(value)
			clickableText.__init__(self,x,y,text,rightJustified,self.valueText)
		def addValue(self,toAdd):
			self.valueText = self.valueText+toAdd
			self.updateSurf()
		def delValue(self):
			if self.valueText!='':
				self.valueText = self.valueText[0:(len(self.valueText)-1)]
				self.updateSurf()
		def finalizeValue(self):
			try:
				self.value = int(self.valueText)
			except:
				print 'Non-numeric value entered!'



	edfPath = './_Data/temp.edf' #temporary default location, to be changed later when ID is established
	eyelink = pylink.EyeLink(eyelinkIP)
	eyelink.sendCommand('select_parser_configuration 0')# 0--> standard (cognitive); 1--> sensitive (psychophysical)
	eyelink.sendCommand('sample_rate 250')
	eyelink.setLinkEventFilter("SACCADE,BLINK")
	eyelink.openDataFile(edfFileName)
	eyelink.sendCommand("screen_pixel_coords =  0 0 %d %d" %(calibrationDisplayRes[0],calibrationDisplayRes[1]))
	eyelink.sendMessage("DISPLAY_COORDS  0 0 %d %d" %(calibrationDisplayRes[0],calibrationDisplayRes[1]))

	#create saccade threshold settings
	settingsDict = {}
	settingsDict['velocity'] = settingText(value=30,x=fontSize,y=fontSize,text='Velocity = ')
	settingsDict['accelleration'] = settingText(value=9500,x=fontSize,y=fontSize*2,text='Accelleration = ')
	settingsDict['distance'] = settingText(value=0.15,x=fontSize,y=fontSize*3,text='Distance = ')


	#send the initial settings
	for setting in settingsDict:
		sendCommand("saccade_"+setting+"_threshold =%d"%(settingsDict[setting].value))


	class EyeLinkCoreGraphicsPySDL2(pylink.EyeLinkCustomDisplay):
		def __init__(self,targetSize,windowSize,windowPosition):
			self.targetSize = targetSize
			self.windowPosition = windowPosition
			self.windowSize = windowSize
			self.__target_beep__ = Sound('_Stimuli/type.wav')
			self.__target_beep__done__ = Sound('qbeep.wav')
			self.__target_beep__error__ = Sound('error.wav')
		def play_beep(self,beepid):
			if beepid == pylink.DC_TARG_BEEP or beepid == pylink.CAL_TARG_BEEP:
				self.__target_beep__.play()
			elif beepid == pylink.CAL_ERR_BEEP or beepid == pylink.DC_ERR_BEEP:
				self.__target_beep__error__.play()
			else:#	CAL_GOOD_BEEP or DC_GOOD_BEEP
				self.__target_beep__done__.play()
		def clear_cal_display(self): 
			sdl2.ext.fill(self.windowSurf.contents,sdl2.pixels.SDL_Color(r=255, g=255, b=255, a=255))
			self.window.refresh()
			sdl2.ext.fill(self.windowSurf.contents,sdl2.pixels.SDL_Color(r=255, g=255, b=255, a=255))
			sdl2.SDL_PumpEvents()
		def setup_cal_display(self):
			self.window = sdl2.ext.Window("Calibration",size=self.windowSize,position=self.windowPosition,flags=sdl2.SDL_WINDOW_SHOWN)#|sdl2.SDL_WINDOW_BORDERLESS)
			self.windowID = sdl2.SDL_GetWindowID(self.window.window)
			self.windowSurf = sdl2.SDL_GetWindowSurface(self.window.window)
			self.windowArray = sdl2.ext.pixels3d(self.windowSurf.contents)
			self.clear_cal_display()
			for i in range(10):
				sdl2.SDL_PumpEvents() #to show the windows
		def exit_cal_display(self): 
			sdl2.SDL_DestroyWindow(self.window.window)
		def erase_cal_target(self):
			self.clear_cal_display()		
		def draw_cal_target(self, x, y):
			radius = self.targetSize/2
			yy, xx = numpy.ogrid[-radius: radius, -radius: radius]
			index = numpy.logical_and( (xx**2 + yy**2) <= (radius**2) , (xx**2 + yy**2) >= ((radius/4)**2) )
			self.windowArray[ (x-radius):(x+radius) , (y-radius):(y+radius) ,  ][index] = [0,0,0,255]
			self.window.refresh()
			sdl2.SDL_PumpEvents()
		def get_input_key(self):
			sdl2.SDL_PumpEvents()
			return None
		def get_input_key(self):
			tracker_mode = self.tracker.getTrackerMode()
			sdl2.SDL_PumpEvents()
			for event in sdl2.ext.get_events():
				if event.type == sdl2.SDL_KEYDOWN:
					keysym = event.key.keysym
					if keysym.sym == sdl2.SDLK_ESCAPE:  # don't allow escape to control tracker unless calibrating
						if tracker_mode in [pylink.EL_VALIDATE_MODE, pylink.EL_CALIBRATE_MODE]:
							return [pylink.KeyInput(sdl2.SDLK_ESCAPE, 0)]
						else:
							return False
					return [pylink.KeyInput(keysym.sym, keysym.mod)]
			return None

	customDisplay = EyeLinkCoreGraphicsPySDL2(targetSize=calibrationDotSize,windowSize=calibrationDisplayRes,windowPosition=calibrationDisplayPosition)
	pylink.openGraphicsEx(customDisplay)

	doSounds = False
	while True:
		sdl2.SDL_PumpEvents()
		for event in sdl2.ext.get_events():
			if event.type==sdl2.SDL_WINDOWEVENT:
				if (event.window.event==sdl2.SDL_WINDOWEVENT_CLOSE):
					exitSafely()
			elif event.type==sdl2.SDL_MOUSEMOTION:
				alreadyClicked = False
				for setting in settingsDict:
					if (settingsDict[setting].isActive) and (settingsDict[setting].clicked):
						alreadyClicked = True
				if not alreadyClicked:
					for setting in settingsDict:
						settingsDict[setting].checkIfActive(event)
			elif event.type==sdl2.SDL_MOUSEBUTTONDOWN:
				alreadyClicked = False
				for setting in settingsDict:
					if (settingsDict[setting].isActive) and (settingsDict[setting].clicked):
						alreadyClicked = True
				if not alreadyClicked:
					for setting in settingsDict:
						if settingsDict[setting].isActive:
							settingsDict[setting].clicked = True
			elif event.type==sdl2.SDL_KEYDOWN:
				key = sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()
				if key == 'backspace':
					for setting in settingsDict:
						if (settingsDict[setting].isActive) and (settingsDict[setting].clicked):
							settingsDict[setting].delValue()
				elif key=='return':
					for setting in settingsDict:
						if (settingsDict[setting].isActive) and (settingsDict[setting].clicked):
							settingsDict[setting].finalizeValue()
							sendCommand("saccade_"+setting+"_threshold =%d"%(settingsDict[setting].value))
							settingsDict[setting].clicked = False
				else:
					for setting in settingsDict:
						if (settingsDict[setting].isActive) and (settingsDict[setting].clicked):
							settingsDict[setting].addValue(key)

		if not qTo.empty():
			message = qTo.get()
			if message=='quit':
				exitSafely()
			elif message[0]=='edfPath':
				edfPath = message[1]
			elif message[0]=='doSounds':
				doSounds = message[1]
			elif message[0]=='sendMessage':
				eyelink.sendMessage(message[1])
			elif message[0]=='accept_trigger':
				eyelink.accept_trigger()
			elif message=='doCalibration':
				doSounds = False
				if eyelink.isRecording():
					eyelink.stopRecording()
				eyelink.doTrackerSetup()
				qFrom.put('calibrationComplete')
				eyelink.startRecording(1,1,1,1) #this retuns immediately takes 10-30ms to actually kick in on the tracker
		if eyelink.isRecording()==0:
			eyeData = eyelink.getNextData()
			if doSounds:
				if (eyeData==pylink.STARTSACC) or (eyeData==pylink.STARTBLINK):
					eyeEvent = eyelink.getFloatData()
					if isinstance(eyeEvent,pylink.StartSaccadeEvent):
						gaze = eyeEvent.getEndGaze()
						distFromFixation = numpy.linalg.norm(numpy.array(gaze)-numpy.array(calibrationDisplayRes)/2)
						print [gaze,distFromFixation,calibrationDotSize]
						if distFromFixation>calibrationDotSize:
							if (not saccadeSound.stillPlaying()) and (not blinkSound.stillPlaying()):
								saccadeSound.play()
					elif isinstance(eyeEvent,pylink.StartBlinkEvent):
						if (not saccadeSound.stillPlaying()) and (not blinkSound.stillPlaying()):
							blinkSound.play()

eyelinkChildFunction(qTo,qFrom,**initDict)