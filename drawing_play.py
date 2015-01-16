import OpenGL.GL as gl
import sdl2 #for input and display
import sdl2.ext #for input and display
import math
import random

class stimDisplayClass:
	def __init__(self):
		sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
	def show(self,stimDisplayRes,stimDisplayPosition):
		self.Window = sdl2.ext.Window("Experiment", size=stimDisplayRes,position=stimDisplayPosition,flags=sdl2.SDL_WINDOW_OPENGL|sdl2.SDL_WINDOW_SHOWN)
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
stimDisplay = stimDisplayClass()
stimDisplay.show(stimDisplayRes=stimDisplayRes,stimDisplayPosition=(0,0))

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

targetSize = 200
wheelSize = 500

def drawWheel():
	gl.glBegin(gl.GL_TRIANGLE_FAN)
	gl.glColor3ub(0,0,0)
	gl.glVertex2f( stimDisplayRes[0]/2 , stimDisplayRes[1]/2 ) #center vertex
	colors = fullColorList#random.sample(fullColorList,len(fullColorList))
	for i in range(len(colors)):
		gl.glColor3ub(colors[i][0],colors[i][1],colors[i][2])
		gl.glVertex2f( stimDisplayRes[0]/2 + math.sin(i*(360.0/len(colors))*math.pi/180)*wheelSize , stimDisplayRes[1]/2 + math.cos(i*(360.0/len(colors))*math.pi/180)*wheelSize)
	i=0
	gl.glColor3ub(colors[i][0],colors[i][1],colors[i][2])
	gl.glVertex2f( stimDisplayRes[0]/2 + math.sin(i*(360.0/len(colors))*math.pi/180)*wheelSize , stimDisplayRes[1]/2 + math.cos(i*(360.0/len(colors))*math.pi/180)*wheelSize)
	gl.glEnd()
	gl.glBegin(gl.GL_TRIANGLE_FAN)
	gl.glColor3ub(0,0,0)#,1)
	for i in range(len(colors)+1):
		gl.glVertex2f( stimDisplayRes[0]/2 + math.sin(i*(360.0/len(colors))*math.pi/180)*wheelSize*.9 , stimDisplayRes[1]/2 + math.cos(i*(360.0/len(colors))*math.pi/180)*wheelSize*.9)
	gl.glEnd()
	return None


def drawDot(xOffset,targetColor):
	gl.glBegin(gl.GL_TRIANGLE_FAN)
	if targetColor!=None:
		gl.glColor3ub(targetColor[0],targetColor[1],targetColor[2])
	else:
		gl.glColor3ub(0,0,0)
	gl.glVertex2f( stimDisplayRes[0]/2+xOffset , stimDisplayRes[1]/2 ) #center vertex
	colors = fullColorList#random.sample(fullColorList,len(fullColorList))
	for i in range(len(colors)):
		if targetColor==None:
			gl.glColor3ub(colors[i][0],colors[i][1],colors[i][2])
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*(360.0/len(colors))*math.pi/180)*targetSize , stimDisplayRes[1]/2 + math.cos(i*(360.0/len(colors))*math.pi/180)*targetSize)
	i=0
	if targetColor==None:
		gl.glColor3ub(colors[i][0],colors[i][1],colors[i][2])
	gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*(360.0/len(colors))*math.pi/180)*targetSize , stimDisplayRes[1]/2 + math.cos(i*(360.0/len(colors))*math.pi/180)*targetSize)
	gl.glEnd()
	return None


gl.glClearColor(0,0,0,1)
gl.glClear(gl.GL_COLOR_BUFFER_BIT)
# drawDot(0,targetColor=None)#(255,255,255))
drawWheel()
stimDisplay.refresh()



clickedColor = numpy.fromstring(gl.glReadPixels(clickX,clickY,1,1,gl.GL_RGB,gl.GL_UNSIGNED_BYTE),dtype=numpy.uint8)