def writerChildFunction(
qTo
,qFrom
):
	import sys
	import time
	try:
		import appnope
		appnope.nope()
	except:
		pass

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
