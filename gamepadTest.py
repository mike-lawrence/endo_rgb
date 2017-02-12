if __name__ == '__main__':
	import fileForker
	import time
	gamepadChild = fileForker.childClass(childFile='gamepadChild.py')
	gamepadChild.start()
	start = time.time()
	done = False
	while not done:
		if not gamepadChild.qFrom.empty():
			message = gamepadChild.qFrom.get()
			if message['type']=='trigger':
				print message
			# if message['type']=='stick':
			# 	print [message['time']-start,message['value'][0],message['side'],message['value'][1]]
			if message['type']=='buttonsDown':
				if message['name']=='xbox':
					done = True
	gamepadChild.stop(killAfter=1)

