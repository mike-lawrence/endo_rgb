def writerChildFunction(
qTo
, qFrom
, windowSize = [200,200]
, windowPosition = [0,0]
):
	import sdl2
	import sdl2.ext
	import sys
	import time
	try:
		import appnope
		appnope.nope()
	except:
		pass


	byteify = lambda x, enc: x.encode(enc)

	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
	window = sdl2.ext.Window("writer",size=windowSize,position=windowPosition,flags=sdl2.SDL_WINDOW_SHOWN)
	windowID = sdl2.SDL_GetWindowID(window.window)
	windowSurf = sdl2.SDL_GetWindowSurface(window.window)
	sdl2.ext.fill(windowSurf.contents,sdl2.pixels.SDL_Color(r=0, g=0, b=0, a=255))
	window.refresh()

	files = {}

	def exitSafely():
		try:
			for index,fileObj in files.items():
				fileObj.close()
				# gpg -r "Michael Lawrence <mike.lwrnc@gmail.com>" -e mac.txt
		except:
			pass
		sys.exit()

	while True:
		sdl2.SDL_PumpEvents()
		for event in sdl2.ext.get_events():
			if event.type==sdl2.SDL_WINDOWEVENT:
				if (event.window.event==sdl2.SDL_WINDOWEVENT_CLOSE):
					exitSafely()
		if not qTo.empty():
			message = qTo.get()
			if message=='quit':
				exitSafely()
			elif message[0]=='newFile':
				files[message[1]] = open(message[2],'w')
			elif message[0]=='write':
				files[message[1]].write(message[2]+'\n')
		else:
			time.sleep(1)

writerChildFunction(qTo,qFrom,**initDict)
