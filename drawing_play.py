import OpenGL.GL as gl
import sdl2 #for input and display
import sdl2.ext #for input and display
import math
import random
import time
import numpy
import aggdraw
from PIL import Image #for image manipulation
from PIL import ImageFont
from PIL import ImageOps



class stimDisplayClass:
	def __init__(self):
		sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
	def show(self,stimDisplayRes,stimDisplayPosition):
		self.Window = sdl2.ext.Window("Experiment", size=stimDisplayRes,position=stimDisplayPosition,flags=sdl2.SDL_WINDOW_OPENGL|sdl2.SDL_WINDOW_SHOWN| sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP |sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
		self.glContext = sdl2.SDL_GL_CreateContext(stimDisplay.Window.window)
		gl.glMatrixMode(gl.GL_PROJECTION)
		gl.glLoadIdentity()
		gl.glOrtho(0, stimDisplayRes[0],stimDisplayRes[1], 0, 0, 1)
		gl.glMatrixMode(gl.GL_MODELVIEW)
		gl.glDisable(gl.GL_DEPTH_TEST)
	def refresh(self):
		sdl2.SDL_GL_SwapWindow(self.Window.window)
	def hide():
		sdl2.SDL_DestroyWindow(self.Window.window)


stimDisplayRes = (1920,1080)
stimDisplayPosition=(0-1440-1080,0)
stimDisplay = stimDisplayClass()
stimDisplay.show(stimDisplayRes=stimDisplayRes,stimDisplayPosition=stimDisplayPosition)

for i in range(10):
	sdl2.SDL_PumpEvents() #to show the windows

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


pickerSize = 50
targetSize = 50
wheelSize = 500


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

def drawPicker(xOffset,yOffset):
	underColor = numpy.fromstring(gl.glReadPixels(stimDisplayRes[0]/2+xOffset,stimDisplayRes[1]/2+yOffset,1,1,gl.GL_RGB,gl.GL_UNSIGNED_BYTE),dtype=numpy.uint8)
	pickerDraw = aggdraw.Draw('RGBA',[pickerSize*3,pickerSize*3],(0,0,0,0))
	pickerDraw.ellipse((pickerSize,pickerSize,pickerSize*2,pickerSize*2),aggdraw.Brush((127,127,127,255)))
	pickerDraw.ellipse((pickerSize+int(pickerSize/4.0),pickerSize+int(pickerSize/4.0),pickerSize*2-int(pickerSize/4.0),pickerSize*2-int(pickerSize/4.0)),aggdraw.Brush((underColor[0],underColor[1],underColor[2],255)))
	pickerDraw.flush()
	pickerString = pickerDraw.tostring()
	pickerPil = Image.fromstring('RGBA',[pickerSize*3,pickerSize*3],pickerString)
	pickerArray = numpy.array(pickerPil,dtype=numpy.uint8)
	# newAlphasFromRed = pickerArray[:,:,0]
	# pickerArray[:,:,3][newAlphasFromRed==0] = 0
	blitNumpy(pickerArray,stimDisplayRes[0]/2+xOffset,stimDisplayRes[1]/2+yOffset)
	# a = numpy.asarray(pilSurf)#,dtype=numpy.uint8)
	# b = numpy.reshape(a,(pilSurf.size[1],pilSurf.size[0]),order='C')


# def drawPicker(xOffset,yOffset):
# 	gl.glColor3ub(127,127,127)
# 	# for i in range(len(fullColorList)):
# 	# 	gl.glBegin(gl.GL_POLYGON)
# 	# 	index = i % len(fullColorList)
# 	# 	gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*(360.0/len(fullColorList))*math.pi/180)*(pickerSize-pickerSize/5.0) , stimDisplayRes[1]/2+yOffset + math.cos(i*(360.0/len(fullColorList))*math.pi/180)*(pickerSize-pickerSize/5.0))
# 	# 	gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin((i+1)*(360.0/len(fullColorList))*math.pi/180)*(pickerSize-pickerSize/5.0) , stimDisplayRes[1]/2+yOffset + math.cos((i+1)*(360.0/len(fullColorList))*math.pi/180)*(pickerSize-pickerSize/5.0))
# 	# 	gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*(360.0/len(fullColorList))*math.pi/180)*pickerSize , stimDisplayRes[1]/2+yOffset + math.cos(i*(360.0/len(fullColorList))*math.pi/180)*pickerSize)
# 	# 	gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin((i+1)*(360.0/len(fullColorList))*math.pi/180)*pickerSize , stimDisplayRes[1]/2+yOffset + math.cos((i+1)*(360.0/len(fullColorList))*math.pi/180)*pickerSize)
# 	# 	gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*(360.0/len(fullColorList))*math.pi/180)*(pickerSize-pickerSize/5.0) , stimDisplayRes[1]/2+yOffset + math.cos(i*(360.0/len(fullColorList))*math.pi/180)*(pickerSize-pickerSize/5.0))
# 	# 	gl.glEnd()
# 	for i in range(360):
# 		gl.glBegin(gl.GL_POLYGON)
# 		gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*(pickerSize-pickerSize/5.0) , stimDisplayRes[1]/2+yOffset + math.cos(i*math.pi/180)*(pickerSize-pickerSize/5.0))
# 		gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin((i+1)*math.pi/180)*(pickerSize-pickerSize/5.0) , stimDisplayRes[1]/2+yOffset + math.cos((i+1)*math.pi/180)*(pickerSize-pickerSize/5.0))
# 		gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*pickerSize , stimDisplayRes[1]/2+yOffset + math.cos(i*math.pi/180)*pickerSize)
# 		gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin((i+1)*math.pi/180)*pickerSize , stimDisplayRes[1]/2+yOffset + math.cos((i+1)*math.pi/180)*pickerSize)
# 		gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*(pickerSize-pickerSize/5.0) , stimDisplayRes[1]/2+yOffset + math.cos(i*math.pi/180)*(pickerSize-pickerSize/5.0))
# 		gl.glEnd()
# 	return None

def drawWheel():
	gl.glBegin(gl.GL_TRIANGLE_FAN)
	gl.glColor3ub(0,0,0)
	gl.glVertex2f( stimDisplayRes[0]/2 , stimDisplayRes[1]/2 ) #center vertex
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


def drawColorTarget(xOffset,targetColor):
	gl.glBegin(gl.GL_TRIANGLE_FAN)
	gl.glColor3ub(targetColor[0],targetColor[1],targetColor[2])
	gl.glVertex2f( stimDisplayRes[0]/2+xOffset , stimDisplayRes[1]/2 ) #center vertex
	for i in range(len(fullColorList)+1):
		index = i % len(fullColorList)
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*(360.0/len(fullColorList))*math.pi/180)*targetSize , stimDisplayRes[1]/2 + math.cos(i*(360.0/len(fullColorList))*math.pi/180)*targetSize)
	gl.glEnd()
	return None

def drawMask(xOffset):
	randomizedColorList = random.sample(fullColorList,len(fullColorList))
	for i in range(len(randomizedColorList)):
		gl.glBegin(gl.GL_POLYGON)
		index = i % len(randomizedColorList)
		gl.glColor3ub(randomizedColorList[index][0],randomizedColorList[index][1],randomizedColorList[index][2])
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset , stimDisplayRes[1]/2 ) #center vertex
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*(360.0/len(randomizedColorList))*math.pi/180)*targetSize , stimDisplayRes[1]/2 + math.cos(i*(360.0/len(randomizedColorList))*math.pi/180)*targetSize)
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin((i+1)*(360.0/len(randomizedColorList))*math.pi/180)*targetSize , stimDisplayRes[1]/2 + math.cos((i+1)*(360.0/len(randomizedColorList))*math.pi/180)*targetSize)
		gl.glEnd()
	return None

gl.glClearColor(0,0,0,1)
gl.glClear(gl.GL_COLOR_BUFFER_BIT)
drawColorTarget(0,targetColor=[0,255,0])
drawWheel()
drawPicker(wheelSize-targetSize/2,0)
stimDisplay.refresh()
time.sleep(10)

# for i in range(10):
# 	gl.glClearColor(0,0,0,1)
# 	gl.glClear(gl.GL_COLOR_BUFFER_BIT)
# 	targetColor = random.choice(fullColorList)
# 	drawColorTarget(0,targetColor=targetColor)
# 	print [targetColor,numpy.fromstring(gl.glReadPixels(stimDisplayRes[0]/2,stimDisplayRes[1]/2,1,1,gl.GL_RGB,gl.GL_UNSIGNED_BYTE),dtype=numpy.uint8)]
# 	# drawWheel()
# 	stimDisplay.refresh()
# 	# print [ i for i in numpy.fromstring(gl.glReadPixels(0,0,stimDisplayRes[0],stimDisplayRes[1],gl.GL_RGB,gl.GL_UNSIGNED_BYTE),dtype=numpy.uint8)]
# 	time.sleep(.1)
# 	now = time.time()
# 	while (time.time()-now)<.1:
# 		gl.glClearColor(0,0,0,1)
# 		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
# 		drawMask(0)
# 		# drawWheel()
# 		stimDisplay.refresh()
# 	gl.glClearColor(0,0,0,1)
# 	gl.glClear(gl.GL_COLOR_BUFFER_BIT)
# 	stimDisplay.refresh()
# 	time.sleep(2)


