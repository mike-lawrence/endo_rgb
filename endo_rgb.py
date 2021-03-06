if __name__ == '__main__':

	########
	# Generate RGB color list
	########
	fullColorList = []
	for i in range(256):
		fullColorList.append([255-i,i,0])

	for i in range(256):
		if i>0:
			fullColorList.append([0,255-i,0+i])

	for i in range(256):
		if i>0:
			if i<255:
				fullColorList.append([0+i,0,255-i])

	########
	#Important parameters
	########

	viewingDistance = 57.0 #units can be anything so long as they match those used in stimDisplayWidth below
	stimDisplayWidth = 54.5 #units can be anything so long as they match those used in viewingDistance above
	stimDisplayRes = (1280, 1024)
	stimDisplayPosition=(0,0)

	gamepadWindowSize = (200,100)
	gamepadWindowPosition = (0,0)

	writerWindowSize = (200,100)
	writerWindowPosition = (0,200)


	doEyelink = False
	eyelinkWindowSize = (200,100)
	eyelinkWindowPosition = (0,400)
	eyelinkIp = '100.1.1.1'
	edfFileName = 'temp.edf'
	edfPath = './'
	saccadeSoundFile = '_Stimuli/stop.wav'
	blinkSoundFile = '_Stimuli/stop.wav'
	calibrationDotSizeInDegrees = 1


	#gamepad trigger criterion value
	triggerCriterionValue = 127 #min is 0, max is 255, so 127 is halfway

	cueValidityList = ['valid','valid','invalid']
	targetSideList = ['left','right']
	targetIdentityList = ['dot']#['square','diamond']

	numTargetColors = 12
	targetColorList = []
	for i in range(numTargetColors):
		index = (len(fullColorList)*1.0/numTargetColors)*i+(len(fullColorList)*1.0/numTargetColors/2.0)
		targetColorList.append(fullColorList[int(index)])


	#times are specified in seconds
	cueTargetSOA = 2.000
	targetDuration = 0.100
	responseTimeout = 1.000
	feedbackDuration = 1.000

	trialsPerBreak = 36
	numberOfBlocks = 10 #3*2*12 = 72 trials per block, 3s per trial = 72*3/60 = 7.5mins per block

	instructionSizeInDegrees = 1
	feedbackSizeInDegrees = 1

	arrowSizeInDegrees = 2
	offsetSizeInDegrees = 10
	targetSizeInDegrees = 3
	ringSizeInDegrees = 8
	ringThicknessProportion = .8
	pickerSizeInDegrees = 1
	wheelSizeInDegrees = 10

	textWidth = .9 #specify the proportion of the stimDisplay to use when drawing instructions


	########
	# Import libraries
	########
	import sdl2 #for input and display
	import sdl2.ext #for input and display
	import numpy #for image and display manipulation
	from PIL import Image #for image manipulation
	from PIL import ImageFont
	from PIL import ImageOps
	import aggdraw #for drawing
	import math #for rounding
	import sys #for quitting
	import os
	import random #for shuffling and random sampling
	import time #for timing
	import shutil #for copying files
	import hashlib #for encrypting
	import OpenGL.GL as gl
	try:
		os.nice(-20)
	except:
		pass#print('Can\'t nice')
	try:
		import appnope
		appnope.nope()
	except:
		pass
	import fileForker


	########
	# Define a custom time function using the same clock as that which generates the SDL2 event timestamps
	########

	#define a function that gets the time (unit=seconds,zero=?)
	def getTime():
		return time.time()


	########
	# Initialize the timer and random seed
	########
	sdl2.SDL_Init(sdl2.SDL_INIT_TIMER)
	seed = getTime() #grab the time of the timer initialization to use as a seed
	random.seed(seed) #use the time to set the random seed


	########
	#Perform some calculations to convert stimulus measurements in degrees to pixels
	########
	stimDisplayWidthInDegrees = math.degrees(math.atan((stimDisplayWidth/2.0)/viewingDistance)*2)
	PPD = stimDisplayRes[0]/stimDisplayWidthInDegrees #compute the pixels per degree (PPD)
	print PPD
	calibrationDotSize = int(calibrationDotSizeInDegrees*PPD)
	instructionSize = int(instructionSizeInDegrees*PPD)
	feedbackSize = int(feedbackSizeInDegrees*PPD)
	arrowSize = int(arrowSizeInDegrees*PPD)
	targetSize = int(targetSizeInDegrees*PPD)
	offsetSize = int(offsetSizeInDegrees*PPD)
	ringSize = int(ringSizeInDegrees*PPD)
	ringThickness = int(ringSizeInDegrees*PPD*ringThicknessProportion)
	pickerSize = int(pickerSizeInDegrees*PPD)
	wheelSize = int(wheelSizeInDegrees*PPD)


	########
	# Initialize fonts
	########
	feedbackFontSize = 2
	feedbackFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", feedbackFontSize)
	feedbackHeight = feedbackFont.getsize('XXX')[1]
	while feedbackHeight<feedbackSize:
		feedbackFontSize = feedbackFontSize + 1
		feedbackFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", feedbackFontSize)
		feedbackHeight = feedbackFont.getsize('XXX')[1]

	feedbackFontSize = feedbackFontSize - 1
	feedbackFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", feedbackFontSize)

	instructionFontSize = 2
	instructionFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", instructionFontSize)
	instructionHeight = instructionFont.getsize('XXX')[1]
	while instructionHeight<instructionSize:
		instructionFontSize = instructionFontSize + 1
		instructionFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", instructionFontSize)
		instructionHeight = instructionFont.getsize('XXX')[1]

	instructionFontSize = instructionFontSize - 1
	instructionFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", instructionFontSize)


	########
	# Initialize the writer
	########
	writerChild = fileForker.childClass(childFile='writerChild.py')
	writerChild.initDict['windowSize'] = writerWindowSize
	writerChild.initDict['windowPosition'] = writerWindowPosition
	writerChild.start()

	########
	# start the event timestamper
	########
	gamepadChild = fileForker.childClass(childFile='gamepadChild.py')
	gamepadChild.initDict['windowSize'] = gamepadWindowSize
	gamepadChild.initDict['windowPosition'] = gamepadWindowPosition
	gamepadChild.start()


	########
	# initialize the eyelink
	########
	if doEyelink:
		eyelinkChild = fileForker.childClass(childFile='eyelinkChild.py')
		eyelinkChild.initDict['windowSize'] = eyelinkWindowSize
		eyelinkChild.initDict['windowPosition'] = eyelinkWindowPosition
		eyelinkChild.initDict['stimDisplayRes'] = stimDisplayRes
		eyelinkChild.initDict['stimDisplayPosition'] = stimDisplayPosition
		eyelinkChild.initDict['calibrationDisplayRes'] = stimDisplayRes
		eyelinkChild.initDict['calibrationDotSize'] = calibrationDotSize
		eyelinkChild.initDict['gazeTargetCriterion'] = PPD*2
		eyelinkChild.initDict['eyelinkIp'] = eyelinkIp
		eyelinkChild.initDict['edfFileName'] = edfFileName
		eyelinkChild.initDict['edfPath'] = edfPath
		eyelinkChild.initDict['saccadeSoundFile'] = saccadeSoundFile
		eyelinkChild.initDict['blinkSoundFile'] = blinkSoundFile
		eyelinkChild.start()
		done = False
		while not done:
			while not eyelinkChild.qFrom.empty():
				message = eyelinkChild.qFrom.get()
				if message=='connected':
					done = True
	########
	# Initialize the stimDisplay
	########
	class stimDisplayClass:
		def __init__(self):
			sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
			self.lastUpdate = None #for keeping track of when the screen last updated
			self.dt = None #for keeping track of the time between updates
			return None
		def show(self,stimDisplayRes,stimDisplayPosition):
			self.Window = sdl2.ext.Window("Experiment", size=stimDisplayRes,position=stimDisplayPosition,flags=sdl2.SDL_WINDOW_SHOWN| sdl2.SDL_WINDOW_OPENGL|sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP |sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
			self.glContext = sdl2.SDL_GL_CreateContext(stimDisplay.Window.window)
			gl.glMatrixMode(gl.GL_PROJECTION)
			gl.glLoadIdentity()
			gl.glOrtho(0, stimDisplayRes[0],stimDisplayRes[1], 0, 0, 1)
			gl.glMatrixMode(gl.GL_MODELVIEW)
			gl.glDisable(gl.GL_DEPTH_TEST)
			gl.glClearColor(0,0,0,1)
			gl.glClear(gl.GL_COLOR_BUFFER_BIT)
			return None
		def refresh(self):
			sdl2.SDL_GL_SwapWindow(self.Window.window)
			now = getTime()
			if self.lastUpdate!=None:
				self.dt = now-self.lastUpdate
			self.lastUpdate = getTime()
			gl.glClearColor(0,0,0,1)
			gl.glClear(gl.GL_COLOR_BUFFER_BIT)
			return None
		def hide():
			sdl2.SDL_DestroyWindow(self.Window.window)
			return None

	time.sleep(2)
	stimDisplay = stimDisplayClass()
	stimDisplay.show(stimDisplayRes=stimDisplayRes,stimDisplayPosition=stimDisplayPosition)
	sdl2.mouse.SDL_ShowCursor(0)
	for i in range(10):
		sdl2.SDL_PumpEvents() #to show the windows



	########
	# Drawing functions
	########

	def text2numpy(myText,myFont,fg=[255,255,255,255],bg=[0,0,0,0]):
		glyph = myFont.getmask(myText,mode='L')
		a = numpy.asarray(glyph)#,dtype=numpy.uint8)
		b = numpy.reshape(a,(glyph.size[1],glyph.size[0]),order='C')
		c = numpy.zeros((glyph.size[1],glyph.size[0],4))#,dtype=numpy.uint8)
		# c[:,:,0][b>0] = b[b>0]
		# c[:,:,1][b>0] = b[b>0]
		# c[:,:,2][b>0] = b[b>0]
		# c[:,:,3][b>0] = b[b>0]
		c[:,:,0][b>0] = fg[0]*b[b>0]/255.0
		c[:,:,1][b>0] = fg[1]*b[b>0]/255.0
		c[:,:,2][b>0] = fg[2]*b[b>0]/255.0
		c[:,:,3][b>0] = fg[3]*b[b>0]/255.0
		c[:,:,0][b==0] = bg[0]
		c[:,:,1][b==0] = bg[1]
		c[:,:,2][b==0] = bg[2]
		c[:,:,3][b==0] = bg[3]
		return c.astype(dtype=numpy.uint8)


	def blitNumpy(numpyArray,xLoc,yLoc,xCentered=True,yCentered=True):
		gl.glEnable(gl.GL_BLEND)
		gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
		ID = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, ID)
		gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE);
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
		gl.glTexImage2D( gl.GL_TEXTURE_2D , 0 , gl.GL_RGBA , numpyArray.shape[1] , numpyArray.shape[0] , 0 , gl.GL_RGBA , gl.GL_UNSIGNED_BYTE , numpyArray )
		gl.glEnable(gl.GL_TEXTURE_2D)
		gl.glBindTexture(gl.GL_TEXTURE_2D, ID)
		gl.glBegin(gl.GL_QUADS)
		x1 = xLoc + 1.5 - 0.5
		x2 = xLoc + numpyArray.shape[1] - 0.0 + 0.5
		y1 = yLoc + 1.0 - 0.5
		y2 = yLoc + numpyArray.shape[0] - 0.5 + 0.5
		if xCentered:
			x1 = x1 - numpyArray.shape[1]/2.0
			x2 = x2 - numpyArray.shape[1]/2.0
		if yCentered:
			y1 = y1 - numpyArray.shape[0]/2.0
			y2 = y2 - numpyArray.shape[0]/2.0
		gl.glTexCoord2f( 0 , 0 )
		gl.glVertex2f( x1 , y1 )
		gl.glTexCoord2f( 1 , 0 )
		gl.glVertex2f( x2 , y1 )
		gl.glTexCoord2f( 1 , 1)
		gl.glVertex2f( x2 , y2 )
		gl.glTexCoord2f( 0 , 1 )
		gl.glVertex2f( x1, y2 )
		gl.glEnd()
		gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
		gl.glDeleteTextures([ID])
		del ID
		gl.glDisable(gl.GL_TEXTURE_2D)
		return None


	def drawText( myText , myFont , textWidth , xLoc , yLoc , fg=[255,255,255,255] , bg=[0,0,0,0] , xCentered=True , yCentered=True , lineSpacing=1.2):
		lineHeight = myFont.getsize('Tj')[0]*lineSpacing
		paragraphs = myText.splitlines()
		renderList = []
		for thisParagraph in paragraphs:
			words = thisParagraph.split(' ')
			if len(words)==1:
				renderList.append(words[0])
				if (thisParagraph!=paragraphs[len(paragraphs)-1]):
					renderList.append(' ')
			else:
				thisWordIndex = 0
				while thisWordIndex < (len(words)-1):
					lineStart = thisWordIndex
					lineWidth = 0
					while (thisWordIndex < (len(words)-1)) and (lineWidth <= textWidth):
						thisWordIndex = thisWordIndex + 1
						lineWidth = myFont.getsize(' '.join(words[lineStart:(thisWordIndex+1)]))[0]
					if thisWordIndex < (len(words)-1):
						#last word went over, paragraph continues
						renderList.append(' '.join(words[lineStart:(thisWordIndex-1)]))
						thisWordIndex = thisWordIndex-1
					else:
						if lineWidth <= textWidth:
							#short final line
							renderList.append(' '.join(words[lineStart:(thisWordIndex+1)]))
						else:
							#full line then 1 word final line
							renderList.append(' '.join(words[lineStart:thisWordIndex]))
							renderList.append(words[thisWordIndex])
						#at end of paragraph, check whether a inter-paragraph space should be added
						if (thisParagraph!=paragraphs[len(paragraphs)-1]):
							renderList.append(' ')
		numLines = len(renderList)
		for thisLineNum in range(numLines):
			if renderList[thisLineNum]==' ':
				pass
			else:
				thisRender = text2numpy( renderList[thisLineNum] , myFont , fg=fg , bg=bg )
				if xCentered:
					x = xLoc - thisRender.shape[1]/2.0
				else:
					x = xLoc
				if yCentered:
					y = yLoc - numLines*lineHeight/2.0 + thisLineNum*lineHeight
				else:
					y = yLoc + thisLineNum*lineHeight
				blitNumpy(numpyArray=thisRender,xLoc=x,yLoc=y,xCentered=False,yCentered=False)
		return None


	def drawFeedback(feedbackText):
		feedbackArray = text2numpy(feedbackText,feedbackFont,fg=[127,127,127,255],bg=[0,0,0,0])
		blitNumpy(feedbackArray,stimDisplayRes[0]/2,stimDisplayRes[1]/2,xCentered=True,yCentered=True)
		return None


	def drawArrow(direction):
		start = getTime()
		if direction=='left':
			directionMultiplier = 1
		else:
			directionMultiplier = -1
		gl.glColor3ub(127,127,127)
		gl.glBegin(gl.GL_POLYGON)
		gl.glVertex2f( stimDisplayRes[0]/2 - (arrowSize/3*2)*directionMultiplier , stimDisplayRes[1]/2 )
		gl.glVertex2f( stimDisplayRes[0]/2 - (arrowSize/3)*directionMultiplier , stimDisplayRes[1]/2 - arrowSize/3)
		gl.glVertex2f( stimDisplayRes[0]/2 - (arrowSize/3)*directionMultiplier , stimDisplayRes[1]/2 - arrowSize/6)
		gl.glVertex2f( stimDisplayRes[0]/2 + (arrowSize/3*2)*directionMultiplier , stimDisplayRes[1]/2 - arrowSize/6)
		gl.glVertex2f( stimDisplayRes[0]/2 + (arrowSize/3*2)*directionMultiplier , stimDisplayRes[1]/2 + arrowSize/6)
		gl.glVertex2f( stimDisplayRes[0]/2 - (arrowSize/3)*directionMultiplier , stimDisplayRes[1]/2 + arrowSize/6)
		gl.glVertex2f( stimDisplayRes[0]/2 - (arrowSize/3)*directionMultiplier , stimDisplayRes[1]/2 + arrowSize/3)
		gl.glVertex2f( stimDisplayRes[0]/2 - (arrowSize/3*2)*directionMultiplier , stimDisplayRes[1]/2 )
		gl.glEnd()
		gl.glColor3ub(0,0,0)
		gl.glBegin(gl.GL_POLYGON)
		gl.glVertex2f( stimDisplayRes[0]/2 - 1 , stimDisplayRes[1]/2 - 1)
		gl.glVertex2f( stimDisplayRes[0]/2 + 1 , stimDisplayRes[1]/2 - 1)
		gl.glVertex2f( stimDisplayRes[0]/2 + 1 , stimDisplayRes[1]/2 + 1)
		gl.glVertex2f( stimDisplayRes[0]/2 - 1 , stimDisplayRes[1]/2 + 1)
		gl.glVertex2f( stimDisplayRes[0]/2 - 1 , stimDisplayRes[1]/2 - 1)
		gl.glEnd()
		#print 'Arrow: '+str(int((getTime()-start)*1000))
		return None


	def drawPicker(xOffset,yOffset):
		underColor = numpy.fromstring(gl.glReadPixels(stimDisplayRes[0]/2+xOffset,stimDisplayRes[1]/2-yOffset,1,1,gl.GL_RGB,gl.GL_UNSIGNED_BYTE),dtype=numpy.uint8)
		pickerDraw = aggdraw.Draw('RGBA',[pickerSize*3,pickerSize*3],(0,0,0,0))
		pickerDraw.ellipse((pickerSize,pickerSize,pickerSize*2,pickerSize*2),aggdraw.Brush((0,0,0,255)))
		pickerDraw.ellipse((pickerSize+int(pickerSize/4.0),pickerSize+int(pickerSize/4.0),pickerSize*2-int(pickerSize/4.0),pickerSize*2-int(pickerSize/4.0)),aggdraw.Brush((underColor[0],underColor[1],underColor[2],255)))
		pickerDraw.flush()
		pickerString = pickerDraw.tostring()
		pickerPil = Image.frombytes('RGBA',[pickerSize*3,pickerSize*3],pickerString)
		pickerArray = numpy.array(pickerPil,dtype=numpy.uint8)
		blitNumpy(pickerArray,stimDisplayRes[0]/2+xOffset,stimDisplayRes[1]/2+yOffset)
		return None


	def drawWheel(rotation=None):
		gl.glBegin(gl.GL_TRIANGLE_FAN)
		gl.glColor3ub(0,0,0)
		gl.glVertex2f( stimDisplayRes[0]/2 , stimDisplayRes[1]/2 ) #center vertex
		if rotation==None:
			rotation = random.choice(range(len(fullColorList)))
		for i in range(len(fullColorList)+1):
			index = (i+rotation) % len(fullColorList) #serves to implement a ring array with rotation
			gl.glColor3ub(fullColorList[index][0],fullColorList[index][1],fullColorList[index][2])
			gl.glVertex2f( stimDisplayRes[0]/2 + math.sin(i*(360.0/len(fullColorList))*math.pi/180)*wheelSize , stimDisplayRes[1]/2 + math.cos(i*(360.0/len(fullColorList))*math.pi/180)*wheelSize)
		gl.glEnd()
		gl.glBegin(gl.GL_TRIANGLE_FAN) #begin center black disk
		gl.glColor3ub(0,0,0)#,1)
		for i in range(len(fullColorList)+1):
			gl.glVertex2f( stimDisplayRes[0]/2 + math.sin(i*(360.0/len(fullColorList))*math.pi/180)*wheelSize*.9 , stimDisplayRes[1]/2 + math.cos(i*(360.0/len(fullColorList))*math.pi/180)*wheelSize*.9)
		gl.glEnd() #end center black disk
		return rotation

	def drawDot(size,xOffset=0):
		gl.glColor3f(.5,.5,.5)
		gl.glBegin(gl.GL_POLYGON)
		for i in range(360):
			gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*(size/2.0) , stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*(size/2.0))
		gl.glEnd()

	def drawCalTarget(x=stimDisplayRes[0]/2,y=stimDisplayRes[1]/2):
		gl.glColor3f(.5,.5,.5)
		gl.glBegin(gl.GL_POLYGON)
		for i in range(360):
			gl.glVertex2f( x + math.sin(i*math.pi/180.0)*(calibrationDotSize/2.0) , y + math.cos(i*math.pi/180.0)*(calibrationDotSize/2.0))
		gl.glEnd()
		gl.glColor3f(0,0,0)
		gl.glBegin(gl.GL_POLYGON)
		for i in range(360):
			gl.glVertex2f( x + math.sin(i*math.pi/180.0)*(calibrationDotSize/8.0) , y + math.cos(i*math.pi/180.0)*(calibrationDotSize/8.0))
		gl.glEnd()

	def drawColorTarget(xOffset,targetColor):
		start = getTime()
		gl.glBegin(gl.GL_TRIANGLE_FAN)
		gl.glColor3ub(targetColor[0],targetColor[1],targetColor[2])
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset , stimDisplayRes[1]/2 ) #center vertex
		for i in range(len(fullColorList)+1):
			index = i % len(fullColorList)
			gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*(360.0/len(fullColorList))*math.pi/180)*targetSize , stimDisplayRes[1]/2 + math.cos(i*(360.0/len(fullColorList))*math.pi/180)*targetSize)
		gl.glEnd()
		#print 'Color: '+str(int((getTime()-start)*1000))
		return None


	def drawMask(targetSide):
		start = getTime()
		if targetSide=='left':
			xOffset = -offsetSize
		else:
			xOffset = offsetSize
		randomizedColorList = random.sample(fullColorList,len(fullColorList))
		for i in range(len(randomizedColorList)):
			gl.glBegin(gl.GL_POLYGON)
			index = i % len(randomizedColorList)
			gl.glColor3ub(randomizedColorList[index][0],randomizedColorList[index][1],randomizedColorList[index][2])
			gl.glVertex2f( stimDisplayRes[0]/2+xOffset , stimDisplayRes[1]/2 ) #center vertex
			gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*(360.0/len(randomizedColorList))*math.pi/180)*targetSize , stimDisplayRes[1]/2 + math.cos(i*(360.0/len(randomizedColorList))*math.pi/180)*targetSize)
			gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin((i+1)*(360.0/len(randomizedColorList))*math.pi/180)*targetSize , stimDisplayRes[1]/2 + math.cos((i+1)*(360.0/len(randomizedColorList))*math.pi/180)*targetSize)
			gl.glEnd()
		#print 'Mask: '+str(int((getTime()-start)*1000))
		return None

	def drawRing(xOffset):
		start = getTime()
		outer = ringSize/2
		inner = ringSize/2*ringThicknessProportion
		gl.glColor3f(.5,.5,.5)
		gl.glBegin(gl.GL_QUAD_STRIP)
		for i in range(360):
			gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*outer,stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*outer)
			gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*inner,stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*inner)
		gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(360*math.pi/180)*outer,stimDisplayRes[1]/2 + math.cos(360*math.pi/180)*outer)
		gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(360*math.pi/180)*inner,stimDisplayRes[1]/2 + math.cos(360*math.pi/180)*inner)
		gl.glEnd()
		#print 'Ring: '+str(int((getTime()-start)*1000))
		return None

	def drawSquare(xOffset):
		start = getTime()
		outer = ringSize
		inner = ringSize*ringThicknessProportion
		gl.glColor3f(.5,.5,.5)
		gl.glBegin(gl.GL_QUAD_STRIP)
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-outer/2 , stimDisplayRes[1]/2-outer/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-inner/2 , stimDisplayRes[1]/2-inner/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset+outer/2 , stimDisplayRes[1]/2-outer/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset+inner/2 , stimDisplayRes[1]/2-inner/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset+outer/2 , stimDisplayRes[1]/2+outer/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset+inner/2 , stimDisplayRes[1]/2+inner/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-outer/2 , stimDisplayRes[1]/2+outer/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-inner/2 , stimDisplayRes[1]/2+inner/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-outer/2 , stimDisplayRes[1]/2-outer/2 )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-inner/2 , stimDisplayRes[1]/2-inner/2 )
		gl.glEnd()
		#print 'Square: '+str(int((getTime()-start)*1000))
		return None


	def drawDiamond(xOffset):
		start = getTime()
		outer = ringSize
		inner = ringSize*ringThicknessProportion
		gl.glColor3f(.5,.5,.5)
		gl.glBegin(gl.GL_QUAD_STRIP)
		outer = math.sqrt((outer**2)*2)/2
		inner = math.sqrt((inner**2)*2)/2
		yOffset = stimDisplayRes[1]/2
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-outer , yOffset )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-inner , yOffset )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset , yOffset-outer )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset , yOffset-inner )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset+outer , yOffset )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset+inner , yOffset )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset , yOffset+outer )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset , yOffset+inner )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-outer , yOffset )
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset-inner , yOffset )
		gl.glEnd()
		#print 'Diamond: '+str(int((getTime()-start)*1000))
		return None


	def drawTargets(targetSide,targetIdentity,targetColor):
		if targetSide=='left':
			xOffset = -offsetSize
		else:
			xOffset = offsetSize
		drawRing(-xOffset)
		if targetIdentity=='square':
			drawSquare(xOffset)
		elif targetIdentity=='diamond':
			drawDiamond(xOffset)
		drawColorTarget(xOffset,targetColor)
		return None

	def drawFixation(arrowDirection):
		drawArrow(arrowDirection)
		drawRing(offsetSize)
		drawRing(-offsetSize)
		return None


	def doCalibration():
		eyelinkChild.qTo.put('startingCalibration')
		calibrationDone = False
		while not calibrationDone:
			#check for gamepad input
			while not gamepadChild.qFrom.empty():
				event = gamepadChild.qFrom.get()
				if event['type'] == 'buttonDown':
					#print 'main: button'
					eyelinkChild.qTo.put('go')
			sdl2.SDL_PumpEvents()
			for event in sdl2.ext.get_events():
				if event.type==sdl2.SDL_KEYDOWN:
					if sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()=='q':
						exitSafely()
					else:
						eyelinkChild.qTo.put(['keycode',event.key.keysym])
			if not eyelinkChild.qFrom.empty():
				message = eyelinkChild.qFrom.get()
				if message=='calibrationComplete':
					calibrationDone = True
				elif (message=='setupCalDisplay') or (message=='exitCalDisplay'):
					drawDot(calibrationDotSize/2)
					stimDisplay.refresh()
				elif message=='eraseCalTarget':
					pass
				elif message=='clearCalDisplay':
					stimDisplay.refresh()
				elif message[0]=='drawCalTarget':
					x = message[1]
					y = message[2]
					drawCalTarget(x,y)
					stimDisplay.refresh()
				elif message[0]=='image':
					blitNumpy(message[1],stimDisplayRes[0]/2,stimDisplayRes[1]/2,xCentered=True,yCentered=True)
					stimDisplay.refresh()

	########
	# Helper functions
	########

	#define a function that waits for a given duration to pass
	def simpleWait(duration):
		start = getTime()
		while getTime() < (start + duration):
			pass


	#define a function that will kill everything safely
	def exitSafely():
		writerChild.stop()
		gamepadChild.stop(killAfter=2)
		if doEyelink:
			eyelinkChild.stop()
		while gamepadChild.isAlive():
			time.sleep(.1)
		sdl2.ext.quit()
		sys.exit()


	#define a function that waits for a response
	def waitForResponse():
		done = False
		while not done:
			sdl2.SDL_PumpEvents()
			for event in sdl2.ext.get_events():
				if event.type==sdl2.SDL_KEYDOWN:
					if sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()=='q':
						exitSafely()
					else:
						done = True
			if not gamepadChild.qFrom.empty():
				event = gamepadChild.qFrom.get()
				if (event['type']=='buttonDown'):
					done = True
		return None

	#define a function that prints a message on the stimDisplay while looking for user input to continue. The function returns the total time it waited
	def showMessage(myText):
		messageViewingTimeStart = getTime()
		#gl.glClearColor(0,0,0,1)
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		stimDisplay.refresh()
		#gl.glClearColor(0,0,0,1)
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
		simpleWait(0.500)
		stimDisplay.refresh()
		#gl.glClearColor(0,0,0,1)
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		waitForResponse()
		stimDisplay.refresh()
		#gl.glClearColor(0,0,0,1)
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		simpleWait(0.500)
		messageViewingTime = getTime() - messageViewingTimeStart
		return messageViewingTime


	#define a function that requests user input
	def getInput(getWhat):
		getWhat = getWhat
		textInput = ''
		#gl.glClearColor(0,0,0,1)
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		stimDisplay.refresh()
		simpleWait(0.500)
		myText = getWhat+textInput
		#gl.glClearColor(0,0,0,1)
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
		stimDisplay.refresh()
		#gl.glClearColor(0,0,0,1)
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		done = False
		while not done:
			sdl2.SDL_PumpEvents()
			for event in sdl2.ext.get_events():
				if event.type==sdl2.SDL_KEYDOWN:
					response = sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()
					if response=='q':
						exitSafely()
					elif response == 'backspace':
						if textInput!='':
							textInput = textInput[0:(len(textInput)-1)]
							myText = getWhat+textInput
							#gl.glClearColor(0,0,0,1)
							#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
							drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
							stimDisplay.refresh()
					elif response == 'return':
						done = True
					else:
						textInput = textInput + response
						myText = getWhat+textInput
						#gl.glClearColor(0,0,0,1)
						#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
						drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
						stimDisplay.refresh()
		#gl.glClearColor(0,0,0,1)
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		stimDisplay.refresh()
		return textInput


	#define a function that obtains subject info via user input
	def getSubInfo():
		year = time.strftime('%Y')
		month = time.strftime('%m')
		day = time.strftime('%d')
		hour = time.strftime('%H')
		minute = time.strftime('%M')
		sid = getInput('ID (\'test\' to demo): ')
		if sid != 'test':
			sex = getInput('Sex (m or f): ')
			age = getInput('Age (2-digit number): ')
			handedness = getInput('Handedness (r or l): ')
			password = getInput('Please enter a password (ex. B00): ')
		else:
			sex = 'test'
			age = 'test'
			handedness = 'test'
			password = 'test'
		password = hashlib.sha512(password).hexdigest()
		subInfo = [ sid , year , month , day , hour , minute , sex , age , handedness , password ]
		return subInfo


	#define a function that generates a randomized list of trial-by-trial stimulus information representing a factorial combination of the independent variables.
	def getTrials():
		trials=[]
		for cueValidity in cueValidityList:
			for targetSide in targetSideList:
				for targetIdentity in targetIdentityList:
					for targetColor in targetColorList:
						trials.append([cueValidity,targetSide,targetIdentity,targetColor])
		random.shuffle(trials)
		return trials


	#define a function to quit if q is pressed
	def checkQ():
		sdl2.SDL_PumpEvents()
		for event in sdl2.ext.get_events():
			if event.type==sdl2.SDL_KEYDOWN:
				if sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()=='q':
					exitSafely()


	#define a function that runs a block of trials
	def runBlock():

		#print 'block started'

		#get trials
		trialList = getTrials()

		#run the trials
		trialNum = 0
		while trialNum<trialsPerBreak:
			#bump the trial number
			trialNum = trialNum + 1

			#get the trial info
			# trialInfo = random.choice(trialList) #random trial type (ensures true equiprobablilty of conditions for [on average] unbiased *behaviour*)
			trialInfo = trialList.pop(0) #iterates through trial types (ensures equal cell sizes for unbiased *analysis*)

			#parse the trial info
			cueValidity,targetSide,targetIdentity,targetColor = trialInfo

			trialDescriptor = '\t'.join(map(str,[subInfo[0],block,trialNum]))

			#do drift correction
			start = getTime()
			if doEyelink:
				drawCalTarget()
				stimDisplay.refresh()
				outerDone = False
				while not outerDone:
					sdl2.SDL_PumpEvents()
					drawCalTarget()
					stimDisplay.refresh()
					outerDone = True #set to False below if need to re-do drift correct after re-calibration
					eyelinkChild.qTo.put('doDriftCorrect')
					innerDone = False
					#check for gamepad input
					while not gamepadChild.qFrom.empty():
						event = gamepadChild.qFrom.get()
						if event['type'] == 'buttonDown':
							#print 'main: button'
							eyelinkChild.qTo.put('go')
					while not innerDone:
						sdl2.SDL_PumpEvents()
						while not eyelinkChild.qFrom.empty():
							message = eyelinkChild.qFrom.get()
							if message=='driftCorrectComplete':
								innerDone = True
							elif message=='doCalibration':
								doCalibration()
								innerDone = True
								outerDone = False
						for event in sdl2.ext.get_events():
							if event.type==sdl2.SDL_KEYDOWN:
								if sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()=='q':
									exitSafely()
								else:
									eyelinkChild.qTo.put(['keycode',event.key.keysym])
						#check for gamepad input
						while not gamepadChild.qFrom.empty():
							event = gamepadChild.qFrom.get()
							if event['type'] == 'buttonDown':
								#print 'main: button'
								eyelinkChild.qTo.put('go')
				eyelinkChild.qTo.put(['reportBlinks',True])
				eyelinkChild.qTo.put(['reportSaccades',True])
				eyelinkChild.qTo.put(['doSounds',True])
			trialInitiationTime = getTime() - start


			#determine the arrow direction
			if cueValidity=='valid':
				if targetSide=='left':
					arrowDirection = 'left'
				else:
					arrowDirection = 'right'
			else:
				if targetSide=='left':
					arrowDirection = 'right'
				else:
					arrowDirection = 'left'


			#prep and show the buffers
			drawFixation(arrowDirection)
			stimDisplay.refresh()
			drawFixation(arrowDirection)
			stimDisplay.refresh() #this one should block until it's actually displayed
			if doEyelink:
				eyelinkChild.qTo.put(['edfEntry','trialStart\t'+trialDescriptor])

			#get the trial start time
			trialStartTime = getTime() - 1/60.0
			targetOnTime = trialStartTime + cueTargetSOA
			targetOffTime = targetOnTime + targetDuration
			responseTimeoutTime = targetOnTime + responseTimeout

			#prepare the target screen
			drawArrow(arrowDirection)
			drawTargets(targetSide,targetIdentity,targetColor)

			targetShown = False
			targetRemoved = False

			miss = False
			anticipation = False
			feedbackResponse = False
			rt = 'NA'
			rtLeft = 'NA'
			rtRight = 'NA'
			pickerTime = 'NA'
			colorChoice = 'NA'

			biggestSmallSaccade = 0
			blink = False
			saccade = False

			rtList = {'left':[],'right':[]}
			triggerData = {'left':[],'right':[]}
			triggerData['left'].append({'time':getTime(),'value':0})
			triggerData['right'].append({'time':getTime(),'value':0})

			trialDone = False
			while not trialDone:
				#manage eyelink
				if doEyelink:
					if not eyelinkChild.qFrom.empty():
						message = eyelinkChild.qFrom.get()
						if (message=='blink') or (message=='gazeTargetLost'):
							if message=='blink':
								blink = True
								trialDone = True
							elif message=='gazeTargetLost':
								saccade = True
								trialDone = True
						elif message[0]=='smallerSaccade':
							if message[1]>biggestSmallSaccade:
								biggestSmallSaccade = message[1]
				#check for q key pressed
				checkQ()
				#check for gamepad input
				while not gamepadChild.qFrom.empty():
					event = gamepadChild.qFrom.get()
					if event['type'] == 'trigger':
						event['time'] = event['time']-targetOnTime
						triggerData[event['side']].append({'time':event['time'],'value':event['value']})
						if event['value']>=triggerCriterionValue:
							if triggerData[event['side']][-2]['value']<triggerCriterionValue:
								rtList[event['side']].append(event['time'])
								if not targetShown:
									trialDone = True
									anticipation = True
								if (len(rtList['left'])>0) & (len(rtList['right'])>0):
									trialDone = True
				#manage stimuli
				if not targetShown:
					if getTime()>=targetOnTime:
						stimDisplay.refresh() #show the target
						targetShown = True
						if doEyelink:
							eyelinkChild.qTo.put(['edfEntry','targetOn\t'+trialDescriptor])
						drawFixation(arrowDirection)
				elif not targetRemoved:
					if getTime()>=targetOffTime:
						stimDisplay.refresh() #remove the target
						targetRemoved = True
						if doEyelink:
							eyelinkChild.qTo.put(['edfEntry','targetOff\t'+trialDescriptor])
				else:
					if getTime()>=responseTimeoutTime:
						miss = True
						trialDone = True
			#trial is done
			trialDoneTime = getTime()
			#manage feedback
			if blink:
				feedbackText = 'Blinked!'
			elif saccade:
				feedbackText = 'Eyes moved!'
			elif miss:
				feedbackText = 'Miss!'
			elif anticipation:
				feedbackText = 'Too soon!'
			else:
				rt = (rtList['left'][-1]+rtList['right'][-1])/2.0
				rtLeft = rtList['left'][-1]
				rtRight = rtList['right'][-1]
				feedbackText = str(int(rt*100)) #convert from seconds to hundredths of seconds
			#show feedback
			gl.glClear(gl.GL_COLOR_BUFFER_BIT)
			drawFeedback(feedbackText)
			stimDisplay.refresh()
			if doEyelink:
				eyelinkChild.qTo.put(['edfEntry','feedbackOn\t'+trialDescriptor])
				eyelinkChild.qTo.put(['reportBlinks',False])
				eyelinkChild.qTo.put(['reportSaccades',False])
				eyelinkChild.qTo.put(['doSounds',False])
			trialDone = False
			while getTime()<(trialDoneTime+feedbackDuration):
				#check for q key pressed
				checkQ()
				#check for gamepad input
				while not gamepadChild.qFrom.empty():
					event = gamepadChild.qFrom.get()
					if event['type'] == 'trigger':
						event['time'] = event['time']-targetOnTime
						triggerData[event['side']].append({'time':event['time'],'value':event['value']})
						if event['value']>=triggerCriterionValue:
							if triggerData[event['side']][-1]['value']<triggerCriterionValue:
								feedbackResponse = True
			if (not blink) & (not saccade) & (not anticipation):
				#Do color wheel here
				wheelRotation = drawWheel()
				pickerX,pickerY = [0,0]
				pickerDrawX,pickerDrawY = [0,0]
				stimDisplay.refresh()
				pickerStart = getTime()
				doPicker = False
				done = False
				while not done:
					#check for q key pressed
					checkQ()
					#check for gamepad input
					while (not gamepadChild.qFrom.empty()) and ((getTime()-stimDisplay.lastUpdate)<.01):
						event = gamepadChild.qFrom.get()
						if event['type'] == 'stick':
							if event['side']=='right':
								pickerX,pickerY = event['value']
								pickerY = -pickerY
								magnitude = math.sqrt(pickerX**2+pickerY**2)
								if magnitude>(255/3.0):
									doPicker=True
									if pickerX==0:
										pickerDrawX = 0
										if pickerY>0:
											pickerDrawY = (wheelSize-(wheelSize-wheelSize*.9)/2.0)
										else:
											pickerDrawY = -(wheelSize-(wheelSize-wheelSize*.9)/2.0)
									elif pickerY==0:
										pickerDrawY = 0
										if pickerX>0:
											pickerDrawX = (wheelSize-(wheelSize-wheelSize*.9)/2.0)
										else:
											pickerDrawX = -(wheelSize-(wheelSize-wheelSize*.9)/2.0)
									else:
										angle = math.atan((pickerY*1.0)/pickerX)
										if pickerX>0:
											pickerDrawX = (wheelSize-(wheelSize-wheelSize*.9)/2.0)*math.cos(angle)
											pickerDrawY = (wheelSize-(wheelSize-wheelSize*.9)/2.0)*math.sin(angle)
										else:
											pickerDrawX = -(wheelSize-(wheelSize-wheelSize*.9)/2.0)*math.cos(angle)
											pickerDrawY = -(wheelSize-(wheelSize-wheelSize*.9)/2.0)*math.sin(angle)
								else:
									doPicker=False
						elif event['type'] == 'buttonDown':
							pickerTime = getTime()-pickerStart
							done = True
					drawWheel(rotation=wheelRotation)
					if doPicker:
						drawPicker(pickerDrawX,pickerDrawY)
					stimDisplay.refresh()
				colorChoice = ','.join(map(str,numpy.fromstring(gl.glReadPixels(stimDisplayRes[0]/2+pickerX,stimDisplayRes[1]/2+pickerY,1,1,gl.GL_RGB,gl.GL_UNSIGNED_BYTE),dtype=numpy.uint8)))
			#write out trial info
			triggerDataToWriteLeft = '\n'.join([trialDescriptor + '\tleft\t' + '\t'.join(map(str,i)) for i in triggerData['left']])
			triggerDataToWriteRight = '\n'.join([trialDescriptor + '\tright\t' + '\t'.join(map(str,i)) for i in triggerData['right']])
			writerChild.qTo.put(['write','trigger',triggerDataToWriteLeft])
			writerChild.qTo.put(['write','trigger',triggerDataToWriteRight])
			dataToWrite = '\t'.join(map(str,[ subInfoForFile , messageViewingTime , block , trialNum , cueValidity , targetSide , targetIdentity , targetColor , rt , rtLeft , rtRight , anticipation , feedbackResponse , wheelRotation , colorChoice , pickerX , pickerY , pickerTime , blink , saccade , biggestSmallSaccade]))
			writerChild.qTo.put(['write','data',dataToWrite])
		print 'on break'



	########
	# Initialize the data files
	########

	if doEyelink:
		doCalibration()

	#get subject info
	subInfo = getSubInfo()
	password = subInfo[-1]
	subInfo = subInfo[0:(len(subInfo)-1)]

	if not os.path.exists('_Data'):
		os.mkdir('_Data')
	if subInfo[0]=='test':
		filebase = 'test'
	else:
		filebase = '_'.join(subInfo[0:6])
	if not os.path.exists('_Data/'+filebase):
		os.mkdir('_Data/'+filebase)

	shutil.copy(sys.argv[0], '_Data/'+filebase+'/'+filebase+'_code.py')

	if doEyelink:
		eyelinkChild.qTo.put(['edfPath','_Data/'+filebase+'/'+filebase+'_eyelink.edf'])

	writerChild.qTo.put(['newFile','data','_Data/'+filebase+'/'+filebase+'_data.txt'])
	writerChild.qTo.put(['write','data',password])
	header ='\t'.join(['id' , 'year' , 'month' , 'day' , 'hour' , 'minute' , 'sex' , 'age'  , 'handedness' , 'messageViewingTime' , 'block' , 'trialNum' , 'cueValidity' , 'targetSide' , 'targetIdentity' , 'targetColor' , 'rt', 'rtLeft', 'rtRight' , 'anticipation' , 'feedbackResponse' , 'wheelRotation' , 'colorChoice' , 'pickerX' , 'pickerY' , 'pickerTime', 'blink' , 'saccade' , 'biggestSmallSaccade'])
	writerChild.qTo.put(['write','data',header])

	writerChild.qTo.put(['newFile','trigger','_Data/'+filebase+'/'+filebase+'_trigger.txt'])
	header ='\t'.join(['id' , 'block' , 'trial' , 'trigger' , 'time' , 'value' ])
	writerChild.qTo.put(['write','trigger',header])

	subInfoForFile = '\t'.join(map(str,subInfo))


	########
	# Start the experiment
	########

	messageViewingTime = showMessage('Press any button to begin practice.')
	block = 'practice'
	runBlock()
	messageViewingTime = showMessage('Practice is complete.\nPress any button to begin the experiment.')

	for i in range(numberOfBlocks):
		block = i+1
		runBlock()
		if block<(numberOfBlocks):
			messageViewingTime = showMessage('Take a break!\nYou\'re about '+str(block)+'/'+str(numberOfBlocks)+' done.\nWhen you are ready, press any button to continue the experiment.')

	messageViewingTime = showMessage('You\'re all done!\nPlease alert the person conducting this experiment that you have finished.')

	exitSafely()

