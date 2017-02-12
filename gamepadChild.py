def gamepadChildFunction(
qTo
, qFrom
):
	import usb
	import sys
	import time
	import copy
	try: #use appnope if available
		import appnope
		appnope.nope()
	except:
		pass
	#find, claim & configure the gamepad
	dev = usb.core.find(idVendor=1118, idProduct=654) #wired 360 gamepad
	usb.util.claim_interface(dev, 0)
	dev.set_configuration()
	readEP = dev[0][(0,0)][0] #endpoint to read from
	writeEP = dev[0][(0,0)][1] #endpoint to write to
	#turn the LED off
	dev.write(writeEP,"\x01\x03\x00",0)
	lastData = None
	buttonNames = {\
		'2': {\
			'1':'dpad-up'\
			, '2':'dpad-down'\
			, '4':'dpad-left'\
			, '8':'dpad-right'\
			, '16':'start'\
			, '32':'back'\
			, '64':'left-stick'\
			, '128':'right-stick'\
		}\
		, '3': {\
			'1':'LB'\
			, '2':'RB'\
			, '4':'xbox'\
			, '8':''\
			, '16':'A'\
			, '32':'B'\
			, '64':'X'\
			, '128':'Y'\
		}\
	}
	lastButtonsDown = {\
		'2': {\
			'1':False\
			, '2':False\
			, '4':False\
			, '8':False\
			, '16':False\
			, '32':False\
			, '64':False\
			, '128':False\
		}\
		, '3': {\
			'1':False\
			, '2':False\
			, '4':False\
			, '8':False\
			, '16':False\
			, '32':False\
			, '64':False\
			, '128':False\
		}\
	}
	#define a useful function for processing button input
	def processButtons(buttonSet,now,data,lastButtonsDown):
		buttonsDown = copy.deepcopy(lastButtonsDown)
		state = data[buttonSet]
		events = []
		for i in [128,64,32,16,8,4,2,1]:
			if state>=i:
				buttonsDown[str(buttonSet)][str(i)] = True
				state = state - i
			else:
				buttonsDown[str(buttonSet)][str(i)] = False
			# for i in [128,64,32,16,8,4,2,1]:
			#print [i,buttonsDown[str(buttonSet)][str(i)],lastButtonsDown[str(buttonSet)][str(i)]]
			if buttonsDown[str(buttonSet)][str(i)]!=lastButtonsDown[str(buttonSet)][str(i)]:
				message = {}
				message['time'] = now
				if buttonsDown[str(buttonSet)][str(i)]:
					message['type'] = 'buttonDown'
				else:
					message['type'] = 'buttonUp'
				message['name'] = buttonNames[str(buttonSet)][str(i)]
				events.append(message)
		return [events,buttonsDown]
	while True:
		#check if there are any messages from the parent process
		if not qTo.empty():
			message = qTo.get()
			if message=='quit':
				# usb.util.release_interface(dev, 0)
				sys.exit()
		#get the current time
		now = time.time()
		#check if there's any data from the gamepad
		try:
			data = dev.read(readEP.bEndpointAddress,readEP.wMaxPacketSize,0)
		except usb.core.USBError as e:
			data = None
			if e.args == ('Operation timed out',):
				continue
		#process the data from the gamepad
		if data is not None:
			if len(data)==20: #getting some button/axis state data
				if lastData is not None:
					events = []
					for buttonSet in [2,3]: #check both button sets
						if lastData[buttonSet]!=data[buttonSet]: #check buttons associated with state 2
							buttonEvents,lastButtonsDown = processButtons(buttonSet=buttonSet,now=now,data=data,lastButtonsDown=lastButtonsDown)
							for i in buttonEvents:
								events.append(i)
					for trigger in [4,5]:
						if lastData[trigger]!=data[trigger]:
							message = {}
							message['type'] = 'trigger'
							if trigger==4:
								message['side'] = 'left'
							else:
								message['side'] = 'right'
							message['time'] = now
							message['value'] = data[trigger]
							events.append(message)
					for axisSet in [[7,9],[11,13]]:
						if (lastData[axisSet[0]]!=data[axisSet[0]]) or (lastData[axisSet[1]]!=data[axisSet[1]]):
							xval = data[axisSet[0]]
							if xval>127:
								xval = xval-255
							yval = data[axisSet[1]]
							if yval>127:
								yval = yval-255
							message = {}
							message['type'] = 'stick'
							message['time'] = now
							if axisSet==[7,9]:
								message['side'] = 'left'
							else:
								message['side'] = 'right'
							message['value'] = [xval,yval]
							events.append(message)
					for event in events:
						#print(event)
						qFrom.put(event)
				#write/overwrite lastData with current data
				lastData = data

gamepadChildFunction(qTo,qFrom,**initDict)


"""
Results from exploring the output from the gamepad:
0: always 0
1: always 20
2: 1=up, 2=down, 4=left, 8=right, 16=start, 32=back, 64=left stick, 128 = right stick
3: 1=left shoulder, 2=right shoulder, 4 = X, 16=A, 32=B, 64=X, 128=Y
4: left trigger
5: right trigger
6: left stick x
7: left stick angle: 0/255@north, 127@east, 0/255@south, 128@west
8: at extremes, reflects left y, but weirdly non-linear between
9: left stick angle: 0/255@west, 127 @ north, 0/255 @ east, 128 @ south
10: influenced by both sticks, 255 when right stick @east
11: right stick angle: 0/255@north, 127@east, 0/255@south, 128@west
12: influenced by both sticks, 0 when right stick @south
13: right stick angle: 0/255@west, 127 @ north, 0/255 @ east, 128 @ south
14: always 0
15: always 0
16: always 0
17: always 0
18: always 0
19: always 0
"""
